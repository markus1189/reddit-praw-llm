#!/usr/bin/env python3

import argparse
import json
import os
import sys
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Generator

import praw


def get_reddit_client() -> praw.Reddit:
    """Initialize Reddit client using environment variables."""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'Top Posts Fetcher Bot 1.0 (by /u/bot)')
    
    if not client_id or not client_secret:
        print("Error: Missing required environment variables.", file=sys.stderr)
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET", file=sys.stderr)
        sys.exit(1)
    
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )


def format_post_data(submission) -> Dict[str, Any]:
    """Extract relevant data from a Reddit submission."""
    return {
        'id': submission.id,
        'title': submission.title,
        'author': str(submission.author) if submission.author else '[deleted]',
        'score': submission.score,
        'num_comments': submission.num_comments,
        'created_utc': submission.created_utc,
        'created_date': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
        'url': submission.url,
        'permalink': f"https://reddit.com{submission.permalink}",
        'is_self': submission.is_self,
        'post_type': 'text' if submission.is_self else 'link',
        'over_18': submission.over_18,
        'spoiler': submission.spoiler,
        'selftext': submission.selftext if submission.is_self else None
    }


def matches_title_filter(title: str, pattern: Optional[str]) -> bool:
    """Check if title matches the regex pattern (case-insensitive)."""
    if not pattern:
        return True
    try:
        return bool(re.search(pattern, title, re.IGNORECASE))
    except re.error as e:
        print(f"Error: Invalid regex pattern '{pattern}': {e}", file=sys.stderr)
        sys.exit(1)


def fetch_top_posts_generator(reddit: praw.Reddit, subreddit_name: str, 
                            time_filter: str, limit: int) -> Generator:
    """Fetch top posts from a subreddit using generator for memory efficiency."""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        return subreddit.top(time_filter=time_filter, limit=limit)
    except Exception as e:
        print(f"Error accessing subreddit r/{subreddit_name}: {str(e)}", file=sys.stderr)
        sys.exit(1)


def output_stream_format(post_data: Dict[str, Any], count: int, limit: int):
    """Output post in streaming format as it's fetched."""
    flags = []
    if post_data['over_18']:
        flags.append('NSFW')
    if post_data['spoiler']:
        flags.append('SPOILER')
    flag_str = f" [{', '.join(flags)}]" if flags else ""
    
    print(f"[{count}/{limit}] {post_data['created_date']} | Score: {post_data['score']} | "
          f"Comments: {post_data['num_comments']} | u/{post_data['author']}")
    print(f"         [{post_data['id']}] {post_data['title']}{flag_str} ({post_data['post_type']})")
    
    if post_data['is_self'] and post_data['url'] != post_data['permalink']:
        print(f"         {post_data['url']}")
    elif not post_data['is_self']:
        print(f"         {post_data['url']}")
    print()


def output_text_format(posts: List[Dict[str, Any]], subreddit_name: str, 
                      time_filter: str, title_filter: Optional[str], 
                      total_fetched: int, limit: int) -> str:
    """Format all posts as human-readable text."""
    output = []
    
    # Header
    output.append(f"Subreddit: r/{subreddit_name} (Top {limit} posts from {time_filter})")
    if title_filter:
        output.append(f"Title filter: \"{title_filter}\" (showing {len(posts)} of {total_fetched} posts)")
    else:
        output.append(f"Total posts: {len(posts)}")
    output.append("")
    
    # Posts
    if not posts:
        output.append("No posts found matching criteria.")
    else:
        for i, post in enumerate(posts, 1):
            flags = []
            if post['over_18']:
                flags.append('NSFW')
            if post['spoiler']:
                flags.append('SPOILER')
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            
            output.append(f"{i}. {post['created_date']} | Score: {post['score']} | "
                         f"Comments: {post['num_comments']} | u/{post['author']}")
            output.append(f"   [{post['id']}] {post['title']}{flag_str}")
            output.append(f"   Type: {post['post_type']} | {post['url']}")
            output.append("")
    
    return '\n'.join(output)


def output_json_format(posts: List[Dict[str, Any]], subreddit_name: str, 
                      time_filter: str, title_filter: Optional[str], 
                      total_fetched: int, limit: int) -> str:
    """Format all posts as JSON."""
    data = {
        'subreddit': subreddit_name,
        'time_filter': time_filter,
        'limit': limit,
        'title_filter': title_filter,
        'total_fetched': total_fetched,
        'total_matched': len(posts),
        'posts': posts
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='List top posts from a Reddit subreddit with pagination')
    parser.add_argument('subreddit', help='Subreddit name (without r/ prefix)')
    parser.add_argument('--time', choices=['hour', 'day', 'week', 'month', 'year', 'all'], 
                       default='week', help='Time filter (default: week)')
    parser.add_argument('--limit', type=int, default=1000, 
                       help='Number of posts to fetch (default: 1000, max: 1000)')
    parser.add_argument('--format', choices=['stream', 'text', 'json'], default='stream',
                       help='Output format (default: stream)')
    parser.add_argument('--filter-title', type=str, metavar='REGEX',
                       help='Filter posts by title using regex pattern (case-insensitive)')
    
    args = parser.parse_args()
    
    # Validate limit
    if args.limit > 1000:
        print("Warning: Reddit API limits results to ~1000 posts. Setting limit to 1000.", file=sys.stderr)
        args.limit = 1000
    elif args.limit <= 0:
        print("Error: Limit must be positive", file=sys.stderr)
        sys.exit(1)
    
    # Initialize Reddit client
    reddit = get_reddit_client()
    
    # Show initial status
    filter_msg = f" with title filter: \"{args.filter_title}\"" if args.filter_title else ""
    print(f"Fetching top {args.limit} posts from r/{args.subreddit} ({args.time}){filter_msg}...", 
          file=sys.stderr)
    
    if args.format == 'stream':
        print(f"Streaming results (progress on stderr):", file=sys.stderr)
        print()  # Start with blank line for clean output
    
    # Fetch posts using generator
    posts_generator = fetch_top_posts_generator(reddit, args.subreddit, args.time, args.limit)
    
    matched_posts = []
    total_fetched = 0
    start_time = time.time()
    
    try:
        for submission in posts_generator:
            total_fetched += 1
            
            # Show progress on stderr (not for stream format since it's noisy)
            if args.format != 'stream' and total_fetched % 10 == 0:
                elapsed = time.time() - start_time
                posts_per_sec = total_fetched / elapsed if elapsed > 0 else 0
                eta_secs = (args.limit - total_fetched) / posts_per_sec if posts_per_sec > 0 else 0
                eta_mins = int(eta_secs / 60)
                print(f"Progress: {total_fetched}/{args.limit} posts fetched "
                      f"(~{eta_mins}m remaining)...", file=sys.stderr)
            
            # Extract post data
            post_data = format_post_data(submission)
            
            # Apply title filter
            if matches_title_filter(post_data['title'], args.filter_title):
                matched_posts.append(post_data)
                
                # For streaming format, output immediately
                if args.format == 'stream':
                    output_stream_format(post_data, len(matched_posts), args.limit)
    
    except KeyboardInterrupt:
        print(f"\nInterrupted! Fetched {total_fetched} posts, {len(matched_posts)} matched.", 
              file=sys.stderr)
    
    # Final output for non-streaming formats
    if args.format == 'text':
        print(output_text_format(matched_posts, args.subreddit, args.time, 
                                args.filter_title, total_fetched, args.limit))
    elif args.format == 'json':
        print(output_json_format(matched_posts, args.subreddit, args.time,
                                args.filter_title, total_fetched, args.limit))
    elif args.format == 'stream':
        # Summary for stream format
        print(f"Completed: Found {len(matched_posts)} matching posts out of {total_fetched} total fetched.", 
              file=sys.stderr)


if __name__ == '__main__':
    main()