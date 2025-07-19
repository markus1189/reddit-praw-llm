#!/usr/bin/env python3

import argparse
import json
import os
import sys
from typing import Dict, List, Any

import praw
from praw.models import MoreComments


def get_reddit_client() -> praw.Reddit:
    """Initialize Reddit client using environment variables."""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'Comment Fetcher Bot 1.0 (by /u/bot)')
    
    if not client_id or not client_secret:
        print("Error: Missing required environment variables.", file=sys.stderr)
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET", file=sys.stderr)
        sys.exit(1)
    
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )


def fetch_top_level_comments(reddit: praw.Reddit, post_id: str) -> Dict[str, Any]:
    """Fetch top-level comments for a Reddit post."""
    try:
        submission = reddit.submission(id=post_id)
        
        # Basic post information
        post_data = {
            'post_id': post_id,
            'post_title': submission.title,
            'post_content': submission.selftext if submission.is_self else None,
            'post_type': 'text' if submission.is_self else 'link',
            'post_score': submission.score,
            'post_url': submission.url,
            'total_comments': submission.num_comments,
            'top_level_comments': []
        }
        
        # Collect top-level comments only
        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                continue
                
            comment_data = {
                'id': comment.id,
                'author': str(comment.author) if comment.author else '[deleted]',
                'score': comment.score,
                'body': comment.body,
                'created_utc': comment.created_utc
            }
            post_data['top_level_comments'].append(comment_data)
        
        return post_data
        
    except Exception as e:
        print(f"Error fetching post {post_id}: {str(e)}", file=sys.stderr)
        sys.exit(1)


def format_as_text(data: Dict[str, Any]) -> str:
    """Format comment data as human-readable text suitable for LLM consumption."""
    output = []
    
    # Post header
    output.append(f"Post: {data['post_title']}")
    output.append(f"Type: {data['post_type']} | Score: {data['post_score']} | Total Comments: {data['total_comments']}")
    output.append(f"URL: {data['post_url']}")
    
    # Post content (if it's a text post)
    if data['post_content']:
        output.append("")
        output.append("Post Content:")
        output.append("-" * 20)
        output.append(data['post_content'])
    
    output.append("")
    
    # Comments
    if not data['top_level_comments']:
        output.append("No top-level comments found.")
    else:
        output.append(f"Top-level Comments ({len(data['top_level_comments'])}):")
        output.append("=" * 50)
        
        for i, comment in enumerate(data['top_level_comments'], 1):
            output.append(f"\nComment {i} by {comment['author']} (Score: {comment['score']}):")
            output.append("-" * 40)
            output.append(comment['body'])
            
    return '\n'.join(output)


def format_as_json(data: Dict[str, Any]) -> str:
    """Format comment data as JSON."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_multiple_posts_text(posts_data: List[Dict[str, Any]]) -> str:
    """Format multiple posts as human-readable text with separators."""
    output = []
    
    for i, data in enumerate(posts_data):
        if i > 0:
            # Add separator between posts
            output.append("\n" + "=" * 80)
            output.append(f"POST {i + 1} OF {len(posts_data)}")
            output.append("=" * 80 + "\n")
        
        output.append(format_as_text(data))
    
    return '\n'.join(output)


def format_multiple_posts_json(posts_data: List[Dict[str, Any]]) -> str:
    """Format multiple posts as JSON array."""
    return json.dumps(posts_data, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Fetch top-level comments from Reddit post(s)')
    parser.add_argument('post_ids', nargs='+', help='Reddit post ID(s)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    
    args = parser.parse_args()
    
    # Initialize Reddit client
    reddit = get_reddit_client()
    
    # Fetch comments for all posts
    posts_data = []
    for i, post_id in enumerate(args.post_ids):
        if len(args.post_ids) > 1:
            print(f"Fetching post {i + 1}/{len(args.post_ids)}: {post_id}...", file=sys.stderr)
        
        try:
            data = fetch_top_level_comments(reddit, post_id)
            posts_data.append(data)
        except Exception as e:
            print(f"Error fetching post {post_id}: {str(e)}", file=sys.stderr)
            # Continue with other posts instead of exiting
            continue
    
    if not posts_data:
        print("Error: No posts could be fetched successfully.", file=sys.stderr)
        sys.exit(1)
    
    # Format and output
    if args.format == 'json':
        if len(posts_data) == 1:
            print(format_as_json(posts_data[0]))
        else:
            print(format_multiple_posts_json(posts_data))
    else:
        if len(posts_data) == 1:
            print(format_as_text(posts_data[0]))
        else:
            print(format_multiple_posts_text(posts_data))


if __name__ == '__main__':
    main()