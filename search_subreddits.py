#!/usr/bin/env python3

import argparse
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Generator

import praw


def get_reddit_client() -> praw.Reddit:
    """Initialize Reddit client using environment variables."""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'Subreddit Search Bot 1.0 (by /u/bot)')
    
    if not client_id or not client_secret:
        print("Error: Missing required environment variables.", file=sys.stderr)
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET", file=sys.stderr)
        sys.exit(1)
    
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )


def format_subreddit_data(subreddit) -> Dict[str, Any]:
    """Extract relevant data from a Reddit subreddit."""
    try:
        return {
            'name': subreddit.display_name,
            'title': getattr(subreddit, 'title', ''),
            'description': getattr(subreddit, 'public_description', ''),
            'subscribers': getattr(subreddit, 'subscribers', 0),
            'active_users': getattr(subreddit, 'active_user_count', 0),
            'created_utc': getattr(subreddit, 'created_utc', 0),
            'created_date': datetime.fromtimestamp(getattr(subreddit, 'created_utc', 0)).strftime('%Y-%m-%d') if getattr(subreddit, 'created_utc', 0) else 'Unknown',
            'over_18': getattr(subreddit, 'over18', False),
            'url': f"https://reddit.com/r/{subreddit.display_name}",
            'quarantined': getattr(subreddit, 'quarantine', False)
        }
    except Exception as e:
        print(f"Warning: Error formatting subreddit data for r/{subreddit.display_name}: {e}", file=sys.stderr)
        return {
            'name': subreddit.display_name,
            'title': '',
            'description': '',
            'subscribers': 0,
            'active_users': 0,
            'created_utc': 0,
            'created_date': 'Unknown',
            'over_18': False,
            'url': f"https://reddit.com/r/{subreddit.display_name}",
            'quarantined': False
        }


def search_subreddits(reddit: praw.Reddit, query: str, limit: int) -> Generator:
    """Search for subreddits by query."""
    try:
        return reddit.subreddits.search(query, limit=limit)
    except Exception as e:
        print(f"Error searching subreddits: {str(e)}", file=sys.stderr)
        sys.exit(1)


def get_popular_subreddits(reddit: praw.Reddit, limit: int) -> Generator:
    """Get popular subreddits."""
    try:
        return reddit.subreddits.popular(limit=limit)
    except Exception as e:
        print(f"Error fetching popular subreddits: {str(e)}", file=sys.stderr)
        sys.exit(1)


def get_new_subreddits(reddit: praw.Reddit, limit: int) -> Generator:
    """Get newly created subreddits."""
    try:
        return reddit.subreddits.new(limit=limit)
    except Exception as e:
        print(f"Error fetching new subreddits: {str(e)}", file=sys.stderr)
        sys.exit(1)


def get_recommended_subreddits(reddit: praw.Reddit, subreddit_names: List[str]) -> Generator:
    """Get recommended subreddits based on input subreddits."""
    try:
        return reddit.subreddits.recommended(subreddit_names)
    except Exception as e:
        print(f"Error fetching recommendations: {str(e)}", file=sys.stderr)
        sys.exit(1)


def apply_filters(subreddits_data: List[Dict[str, Any]], 
                 min_subscribers: Optional[int] = None,
                 max_subscribers: Optional[int] = None,
                 exclude_nsfw: bool = False,
                 min_activity: Optional[int] = None) -> List[Dict[str, Any]]:
    """Apply filtering criteria to subreddit data."""
    filtered = []
    
    for sub in subreddits_data:
        # Filter by subscribers
        if min_subscribers is not None and sub['subscribers'] < min_subscribers:
            continue
        if max_subscribers is not None and sub['subscribers'] > max_subscribers:
            continue
            
        # Filter NSFW
        if exclude_nsfw and sub['over_18']:
            continue
            
        # Filter by activity
        if min_activity is not None and sub['active_users'] < min_activity:
            continue
            
        filtered.append(sub)
    
    return filtered


def sort_subreddits(subreddits_data: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
    """Sort subreddit data by specified criteria."""
    if sort_by == 'subscribers-desc':
        return sorted(subreddits_data, key=lambda x: x['subscribers'], reverse=True)
    elif sort_by == 'subscribers-asc':
        return sorted(subreddits_data, key=lambda x: x['subscribers'])
    elif sort_by == 'activity-desc':
        return sorted(subreddits_data, key=lambda x: x['active_users'], reverse=True)
    elif sort_by == 'activity-asc':
        return sorted(subreddits_data, key=lambda x: x['active_users'])
    elif sort_by == 'created-desc':
        return sorted(subreddits_data, key=lambda x: x['created_utc'], reverse=True)
    elif sort_by == 'created-asc':
        return sorted(subreddits_data, key=lambda x: x['created_utc'])
    elif sort_by == 'name':
        return sorted(subreddits_data, key=lambda x: x['name'].lower())
    else:
        return subreddits_data  # No sorting or 'relevance'


def format_output(subreddits_data: List[Dict[str, Any]], 
                 method: str, query: Optional[str] = None, 
                 total_fetched: int = 0) -> str:
    """Format subreddit data as human-readable text."""
    output = []
    
    # Header
    if method == 'search' and query:
        output.append(f"Subreddit Search Results for: \"{query}\"")
    elif method == 'popular':
        output.append("Popular Subreddits")
    elif method == 'new':
        output.append("Newly Created Subreddits")
    elif method == 'recommendations':
        output.append("Recommended Subreddits")
    
    output.append(f"Found {len(subreddits_data)} subreddits")
    if total_fetched != len(subreddits_data):
        output.append(f"(showing {len(subreddits_data)} of {total_fetched} after filtering)")
    output.append("")
    
    # Subreddits
    if not subreddits_data:
        output.append("No subreddits found matching criteria.")
    else:
        for i, sub in enumerate(subreddits_data, 1):
            flags = []
            if sub['over_18']:
                flags.append('NSFW')
            if sub['quarantined']:
                flags.append('QUARANTINED')
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            
            # Format subscriber count
            subs = sub['subscribers']
            if subs >= 1000000:
                sub_str = f"{subs/1000000:.1f}M"
            elif subs >= 1000:
                sub_str = f"{subs/1000:.1f}k"
            else:
                sub_str = str(subs)
            
            # Format active users
            active = sub['active_users']
            if active and active > 0:
                if active >= 1000:
                    active_str = f" | Active: {active/1000:.1f}k"
                else:
                    active_str = f" | Active: {active}"
            else:
                active_str = ""
            
            output.append(f"{i}. r/{sub['name']}{flag_str}")
            output.append(f"   Subscribers: {sub_str}{active_str} | Created: {sub['created_date']}")
            
            if sub['title']:
                output.append(f"   Title: {sub['title']}")
            
            if sub['description']:
                # Truncate long descriptions
                desc = sub['description'].replace('\n', ' ').strip()
                if len(desc) > 150:
                    desc = desc[:147] + "..."
                output.append(f"   Description: {desc}")
            
            output.append(f"   URL: {sub['url']}")
            output.append("")
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Discover and search Reddit subreddits')
    
    # Method selection (mutually exclusive)
    method_group = parser.add_mutually_exclusive_group(required=True)
    method_group.add_argument('--search', type=str, metavar='QUERY',
                            help='Search subreddits by keyword/topic')
    method_group.add_argument('--popular', action='store_true',
                            help='List popular subreddits by subscriber count')
    method_group.add_argument('--new', action='store_true',
                            help='List newly created subreddits')
    method_group.add_argument('--recommend', type=str, metavar='SUBREDDITS',
                            help='Get recommendations based on comma-separated subreddit names')
    
    # Options
    parser.add_argument('--limit', type=int, default=25,
                       help='Number of subreddits to fetch (default: 25)')
    parser.add_argument('--min-subscribers', type=int, metavar='N',
                       help='Minimum subscriber count filter')
    parser.add_argument('--max-subscribers', type=int, metavar='N',
                       help='Maximum subscriber count filter')
    parser.add_argument('--min-activity', type=int, metavar='N',
                       help='Minimum active user count filter')
    parser.add_argument('--exclude-nsfw', action='store_true',
                       help='Exclude NSFW subreddits (shows all by default)')
    parser.add_argument('--sort', choices=['relevance', 'subscribers-desc', 'subscribers-asc', 
                                         'activity-desc', 'activity-asc', 'created-desc', 
                                         'created-asc', 'name'], default='relevance',
                       help='Sort results by criteria (default: relevance)')
    
    args = parser.parse_args()
    
    # Validate limit
    if args.limit <= 0:
        print("Error: Limit must be positive", file=sys.stderr)
        sys.exit(1)
    
    # Initialize Reddit client
    reddit = get_reddit_client()
    
    # Determine method and show initial status
    if args.search:
        method = 'search'
        query = args.search
        print(f"Searching for subreddits matching: \"{query}\"...", file=sys.stderr)
        subreddits_generator = search_subreddits(reddit, query, args.limit)
    elif args.popular:
        method = 'popular'
        query = None
        print(f"Fetching {args.limit} popular subreddits...", file=sys.stderr)
        subreddits_generator = get_popular_subreddits(reddit, args.limit)
    elif args.new:
        method = 'new'
        query = None
        print(f"Fetching {args.limit} newly created subreddits...", file=sys.stderr)
        subreddits_generator = get_new_subreddits(reddit, args.limit)
    elif args.recommend:
        method = 'recommendations'
        query = None
        subreddit_names = [name.strip() for name in args.recommend.split(',')]
        print(f"Getting recommendations based on: {', '.join(subreddit_names)}...", file=sys.stderr)
        subreddits_generator = get_recommended_subreddits(reddit, subreddit_names)
    
    # Fetch and process subreddits
    subreddits_data = []
    total_fetched = 0
    start_time = time.time()
    
    try:
        for subreddit in subreddits_generator:
            total_fetched += 1
            
            # Show progress
            if total_fetched % 5 == 0:
                elapsed = time.time() - start_time
                print(f"Progress: {total_fetched} subreddits fetched...", file=sys.stderr)
            
            # Extract subreddit data
            sub_data = format_subreddit_data(subreddit)
            subreddits_data.append(sub_data)
    
    except KeyboardInterrupt:
        print(f"\nInterrupted! Fetched {total_fetched} subreddits.", file=sys.stderr)
    except Exception as e:
        print(f"Error during fetching: {str(e)}", file=sys.stderr)
    
    if not subreddits_data:
        print("No subreddits found.", file=sys.stderr)
        sys.exit(1)
    
    # Apply filters
    original_count = len(subreddits_data)
    subreddits_data = apply_filters(
        subreddits_data,
        min_subscribers=args.min_subscribers,
        max_subscribers=args.max_subscribers,
        exclude_nsfw=args.exclude_nsfw,
        min_activity=args.min_activity
    )
    
    # Sort results
    subreddits_data = sort_subreddits(subreddits_data, args.sort)
    
    # Output results
    print(format_output(subreddits_data, method, query, original_count))


if __name__ == '__main__':
    main()