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


def extract_comment_data(comment, depth: int = 0, max_depth: int = None, max_comments: int = None) -> Dict[str, Any]:
    """Extract comment data including replies recursively."""
    comment_data = {
        'id': comment.id,
        'author': str(comment.author) if comment.author else '[deleted]',
        'score': comment.score,
        'body': comment.body,
        'created_utc': comment.created_utc,
        'depth': depth,
        'replies': []
    }
    
    # Recursively fetch replies if within depth limit
    if max_depth is None or depth < max_depth:
        reply_count = 0
        for reply in comment.replies:
            if isinstance(reply, MoreComments):
                # Handle "load more comments" by expanding them
                if max_comments is None or reply_count < max_comments:
                    try:
                        more_comments = reply.comments()
                        for more_comment in more_comments:
                            if max_comments is not None and reply_count >= max_comments:
                                break
                            reply_data = extract_comment_data(more_comment, depth + 1, max_depth, max_comments)
                            comment_data['replies'].append(reply_data)
                            reply_count += 1
                    except Exception as e:
                        print(f"Warning: Could not expand more comments: {str(e)}", file=sys.stderr)
                continue
            
            if max_comments is not None and reply_count >= max_comments:
                break
                
            reply_data = extract_comment_data(reply, depth + 1, max_depth, max_comments)
            comment_data['replies'].append(reply_data)
            reply_count += 1
    
    return comment_data


def fetch_comments(reddit: praw.Reddit, post_id: str, max_depth: int = None, max_comments: int = None) -> Dict[str, Any]:
    """Fetch comments for a Reddit post with configurable depth and limits."""
    try:
        submission = reddit.submission(id=post_id)
        
        # Enhanced post information with source references
        post_data = {
            'post_id': post_id,
            'post_title': submission.title,
            'post_content': submission.selftext if submission.is_self else None,
            'post_type': 'text' if submission.is_self else 'link',
            'post_score': submission.score,
            'post_url': submission.url,
            'post_author': str(submission.author) if submission.author else '[deleted]',
            'post_permalink': f"https://reddit.com{submission.permalink}",
            'post_subreddit': str(submission.subreddit),
            'post_created_utc': submission.created_utc,
            'total_comments': submission.num_comments,
            'max_depth': max_depth,
            'max_comments_per_level': max_comments,
            'comments': []
        }
        
        # Collect all comments with hierarchy
        comment_count = 0
        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                # Handle top-level "load more comments"
                if max_comments is None or comment_count < max_comments:
                    try:
                        more_comments = comment.comments()
                        for more_comment in more_comments:
                            if max_comments is not None and comment_count >= max_comments:
                                break
                            comment_data = extract_comment_data(more_comment, 0, max_depth, max_comments)
                            post_data['comments'].append(comment_data)
                            comment_count += 1
                    except Exception as e:
                        print(f"Warning: Could not expand more comments: {str(e)}", file=sys.stderr)
                continue
                
            if max_comments is not None and comment_count >= max_comments:
                break
                
            comment_data = extract_comment_data(comment, 0, max_depth, max_comments)
            post_data['comments'].append(comment_data)
            comment_count += 1
        
        return post_data
        
    except Exception as e:
        print(f"Error fetching post {post_id}: {str(e)}", file=sys.stderr)
        sys.exit(1)


def format_comment_tree(comment: Dict[str, Any], comment_num: int = None, prefix: str = "") -> List[str]:
    """Format a single comment and its replies recursively."""
    output = []
    
    # Comment header with indentation
    indent = "  " * comment['depth']
    if comment_num is not None and comment['depth'] == 0:
        header = f"\n{indent}Comment {comment_num} by {comment['author']} (Score: {comment['score']}, Depth: {comment['depth']}):"
    else:
        header = f"\n{indent}Reply by {comment['author']} (Score: {comment['score']}, Depth: {comment['depth']}):"
    
    output.append(header)
    output.append(f"{indent}{'-' * 40}")
    
    # Comment body with indentation
    body_lines = comment['body'].split('\n')
    for line in body_lines:
        output.append(f"{indent}{line}")
    
    # Recursively format replies
    if comment['replies']:
        for reply in comment['replies']:
            output.extend(format_comment_tree(reply, prefix=prefix))
    
    return output


def format_as_text(data: Dict[str, Any]) -> str:
    """Format comment data as human-readable text suitable for LLM consumption."""
    output = []
    
    # Enhanced post header with source reference
    output.append(f"Post: {data['post_title']}")
    output.append(f"Source: [{data['post_title']}]({data['post_permalink']}) by u/{data['post_author']} ({data['post_score']} upvotes)")
    output.append(f"Subreddit: r/{data['post_subreddit']} | Type: {data['post_type']} | Total Comments: {data['total_comments']}")
    output.append(f"Original URL: {data['post_url']}")
    
    # Fetch parameters
    if data.get('max_depth') is not None:
        output.append(f"Max Depth: {data['max_depth']}")
    if data.get('max_comments_per_level') is not None:
        output.append(f"Max Comments per Level: {data['max_comments_per_level']}")
    
    # Post content (if it's a text post)
    if data['post_content']:
        output.append("")
        output.append("Post Content:")
        output.append("-" * 20)
        output.append(data['post_content'])
    
    output.append("")
    
    # Comments
    if not data['comments']:
        output.append("No comments found.")
    else:
        # Count total comments including replies
        def count_comments(comments):
            total = len(comments)
            for comment in comments:
                total += count_comments(comment['replies'])
            return total
        
        total_fetched = count_comments(data['comments'])
        output.append(f"Comments ({len(data['comments'])} top-level, {total_fetched} total fetched):")
        output.append("=" * 50)
        
        for i, comment in enumerate(data['comments'], 1):
            output.extend(format_comment_tree(comment, i))
            
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
    parser = argparse.ArgumentParser(description='Fetch comments (including nested replies) from Reddit post(s)')
    parser.add_argument('post_ids', nargs='+', help='Reddit post ID(s)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--max-depth', type=int, default=None,
                       help='Maximum comment depth to fetch (default: unlimited)')
    parser.add_argument('--max-comments', type=int, default=None,
                       help='Maximum comments per level to fetch (default: unlimited)')
    parser.add_argument('--top-level-only', action='store_true',
                       help='Fetch only top-level comments (equivalent to --max-depth 0)')
    
    args = parser.parse_args()
    
    # Initialize Reddit client
    reddit = get_reddit_client()
    
    # Process arguments
    max_depth = args.max_depth
    if args.top_level_only:
        max_depth = 0
    
    # Fetch comments for all posts
    posts_data = []
    for i, post_id in enumerate(args.post_ids):
        if len(args.post_ids) > 1:
            depth_str = f"depth {max_depth}" if max_depth is not None else "unlimited depth"
            comments_str = f"max {args.max_comments}" if args.max_comments else "unlimited"
            print(f"Fetching post {i + 1}/{len(args.post_ids)}: {post_id} ({depth_str}, {comments_str} comments)...", file=sys.stderr)
        
        try:
            data = fetch_comments(reddit, post_id, max_depth, args.max_comments)
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