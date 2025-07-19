# Reddit PRAW Toolkit

Python scripts for Reddit data extraction using the PRAW (Python Reddit API Wrapper) library. Built with Nix flakes for reproducible development environments.

## Features

### fetch_comments.py
- Fetch top-level comments from any public Reddit post using just the post ID
- Includes post content text for text posts
- Two output formats: human-readable text (LLM-friendly) and structured JSON

### list_top_posts.py
- List top posts from any subreddit with advanced time filtering (hour/day/week/month/year/all)
- Fetch up to 1000 posts (Reddit's maximum) with automatic pagination
- Real-time streaming output with progress tracking
- Regex-based title filtering for targeted data collection
- Three output formats: streaming, text summary, and structured JSON

### Shared Features
- Secure credential management via environment variables
- Automatic development environment setup with Nix flakes and direnv
- Respects Reddit's API rate limits via PRAW

## Quick Start

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your Reddit API credentials from reddit.com/prefs/apps
direnv allow

# 2. Discover interesting posts  
python list_top_posts.py python --filter-title "tutorial" --time week

# 3. Get detailed content for a specific post
python fetch_comments.py abc123def  # Use post ID from step 2
```

## Prerequisites

- [Nix](https://nixos.org/download.html) with flakes enabled
- [direnv](https://direnv.net/) (optional but recommended)
- Reddit API credentials (see setup below)

## Setup

### 1. Clone and Enter Directory

```bash
git clone <repo-url>
cd reddit-praw-llm
```

### 2. Reddit API Credentials

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Set redirect URI to `http://localhost:8080` (required but not used)
5. Note your Client ID (under the app name) and Client Secret

### 3. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Reddit API credentials
# REDDIT_CLIENT_ID=your_14_char_client_id
# REDDIT_CLIENT_SECRET=your_27_char_client_secret
# REDDIT_USER_AGENT="Your App Name 1.0 (by /u/yourusername)"
```

### 4. Development Environment

#### With direnv (Recommended)
```bash
# Allow direnv to activate the environment
direnv allow

# Environment is now automatically activated when you cd into the directory
```

#### Without direnv
```bash
# Manually enter the Nix development shell
nix develop
```

## Usage

### fetch_comments.py - Get Post Comments

Fetch detailed post content and top-level comments from one or more Reddit posts.

```bash
# Single post - get post and comments in text format (LLM-friendly)
python fetch_comments.py <reddit_post_id>

# Multiple posts - compare posts with clear separators
python fetch_comments.py <post_id1> <post_id2> <post_id3>

# Get structured JSON output (single or multiple posts)
python fetch_comments.py <reddit_post_id> --format json
```

**Examples:**
```bash
# Single post analysis
python fetch_comments.py abc123def

# Compare multiple related posts
python fetch_comments.py abc123def xyz789ghi

# Multiple posts in JSON format for analysis
python fetch_comments.py abc123def xyz789ghi --format json

# Analyze book recommendations from multiple discussion threads
python fetch_comments.py 1m1unvq 1m2j64r 1lzctf3
```

### list_top_posts.py - Browse Subreddit Posts

List and filter top posts from any subreddit with advanced pagination and filtering.

```bash
# Basic usage - stream top posts from last week
python list_top_posts.py <subreddit>

# Get top posts from different time periods
python list_top_posts.py python --time day
python list_top_posts.py MachineLearning --time month --limit 500

# Filter posts by title (regex patterns)
python list_top_posts.py programming --filter-title "python"
python list_top_posts.py python --filter-title "(tutorial|guide)" --time year

# Different output formats
python list_top_posts.py python --format json > python_posts.json
python list_top_posts.py python --format text > readable_summary.txt
```

**Advanced Examples:**
```bash
# Find all tutorial posts from the past year
python list_top_posts.py learnpython --time year --filter-title "tutorial"

# Get top 100 AI posts with streaming output
python list_top_posts.py artificial --limit 100 --filter-title "(AI|ML|machine.*learning)"

# Export subreddit data for analysis
python list_top_posts.py datascience --time month --format json > data.json
```

### Finding the Post ID

Reddit post URLs look like:
```
https://www.reddit.com/r/subreddit/comments/abc123def/post_title/
```

The post ID is `abc123def` (the part between `/comments/` and the next `/`).

## Common Use Cases

### Research & Content Discovery
```bash
# Find trending Python tutorials
python list_top_posts.py learnpython --filter-title "tutorial" --time month

# Discover AI/ML discussions
python list_top_posts.py MachineLearning --filter-title "(AI|ML|neural)" --time week

# Track new releases and updates
python list_top_posts.py programming --filter-title "(release|v\d+|update)" --time day
```

### Data Collection & Analysis
```bash
# Build a dataset of programming discussions
python list_top_posts.py programming --time year --format json > programming_2024.json

# Analyze specific high-engagement posts
python list_top_posts.py datascience --limit 50 | # Find top posts
python fetch_comments.py POST_ID --format json   # Get detailed analysis
```

### Content Monitoring
```bash
# Daily check for questions in your area of expertise
python list_top_posts.py python --time day --filter-title "\?"

# Monitor product/library mentions
python list_top_posts.py programming --filter-title "react" --time week
```

### Academic Research
```bash
# Collect posts about specific technologies for sentiment analysis
python list_top_posts.py programming --filter-title "javascript" --time year --format json

# Study comment patterns on controversial topics
python fetch_comments.py POST_ID --format json | jq '.top_level_comments'
```

## Regex Pattern Examples

Common patterns for `--filter-title`:

```bash
# Questions (posts ending with ?)
--filter-title "\?"

# Multiple keywords (OR logic)
--filter-title "(python|javascript|golang)"

# Version numbers or releases
--filter-title "(v\d+|\d+\.\d+|release)"

# Tutorials and guides
--filter-title "(tutorial|guide|how.*to|beginner)"

# Exclude certain terms
--filter-title "(?!.*(deprecated|old)).*python"

# Case-insensitive partial matching
--filter-title "machine.*learning"
```

## Output Formats

### fetch_comments.py Output

**Text Format (Default)** - Human-readable format optimized for LLM consumption:
```
Post: Example Post Title
Type: text | Score: 1234 | Total Comments: 56
URL: https://reddit.com/r/python/comments/abc123/

Post Content:
--------------------
This is the post text content...

Top-level Comments (12):
==================================================

Comment 1 by username (Score: 42):
----------------------------------------
This is the comment text...
```

**JSON Format** - Structured data for programmatic use:
```json
{
  "post_id": "abc123def",
  "post_title": "Example Post Title",
  "post_content": "Post text...",
  "post_type": "text",
  "post_score": 1234,
  "post_url": "https://example.com",
  "total_comments": 56,
  "top_level_comments": [...]
}
```

### list_top_posts.py Output

**Stream Format (Default)** - Real-time output as posts are fetched:
```
Fetching top 1000 posts from r/python (week)...

[1/1000] 2024-01-15 | Score: 1234 | Comments: 56 | u/author
         [abc123] Cool Python Feature (text)
         https://reddit.com/r/python/comments/abc123/

[2/1000] 2024-01-14 | Score: 987 | Comments: 23 | u/other_user
         [def456] Awesome Library [NSFW] (link)
         https://example.com

Completed: Found 25 matching posts out of 100 total fetched.
```

**Text Format** - Formatted summary after completion:
```
Subreddit: r/python (Top 1000 posts from week)
Title filter: "tutorial" (showing 12 of 100 posts)

1. 2024-01-15 | Score: 1234 | Comments: 56 | u/author
   [abc123] Python Tutorial for Beginners
   Type: text | https://reddit.com/r/python/comments/abc123/

2. 2024-01-14 | Score: 987 | Comments: 23 | u/other_user
   [def456] Advanced Tutorial Guide [SPOILER]
   Type: link | https://example.com
```

**JSON Format** - Complete structured dataset:
```json
{
  "subreddit": "python",
  "time_filter": "week",
  "limit": 1000,
  "title_filter": "tutorial",
  "total_fetched": 100,
  "total_matched": 12,
  "posts": [
    {
      "id": "abc123",
      "title": "Python Tutorial for Beginners",
      "author": "username",
      "score": 1234,
      "num_comments": 56,
      "created_date": "2024-01-15",
      "post_type": "text",
      "over_18": false,
      "spoiler": false,
      "url": "https://example.com"
    }
  ]
}
```

## Environment Variables

- `REDDIT_CLIENT_ID`: Your Reddit app's client ID (required)
- `REDDIT_CLIENT_SECRET`: Your Reddit app's client secret (required)  
- `REDDIT_USER_AGENT`: User agent string (optional, defaults to "Comment Fetcher Bot 1.0")

## Performance & Timing

Understanding Reddit API performance helps set proper expectations:

### Typical Operation Times

| Operation | Posts/Comments | Estimated Time | Notes |
|-----------|---------------|----------------|-------|
| `list_top_posts.py` (100 posts) | 100 | ~2-3 minutes | 1 API call batch |
| `list_top_posts.py` (1000 posts) | 1000 | ~20 minutes | 10 API call batches |
| `fetch_comments.py` (single post) | 1 post + comments | ~5-10 seconds | Depends on comment count |
| Large subreddit (1000 posts) | 1000 | ~20 minutes | Reddit enforces 2s delays |

### Optimization Tips

```bash
# Start small for exploration
python list_top_posts.py python --limit 50 --time day

# Use streaming format for immediate feedback
python list_top_posts.py python --format stream --limit 1000

# Break large requests into smaller time windows
python list_top_posts.py python --time day    # Fast
python list_top_posts.py python --time week   # Medium  
python list_top_posts.py python --time month  # Slow
```

### Progress Tracking

- **Stream format**: Real-time progress with post-by-post output
- **Text/JSON formats**: Progress updates every 10 posts on stderr
- **Interruption**: Ctrl+C preserves partial results in all formats

## Workflow Integration

The two scripts work perfectly together for comprehensive Reddit analysis:

1. **Discovery**: Use `list_top_posts.py` to find interesting posts by browsing subreddits with filters
2. **Deep Dive**: Use `fetch_comments.py` with post IDs from step 1 to get detailed content and comments

**Example workflow:**
```bash
# Step 1: Find interesting posts about Python tutorials
python list_top_posts.py learnpython --filter-title "tutorial" --time month

# Step 2: Get detailed content for specific posts
python fetch_comments.py abc123def  # Use post IDs from step 1
python fetch_comments.py xyz789ghi --format json
```

## Important Notes

### Reddit API Limitations
- **Maximum posts per subreddit**: Reddit API limits any listing to ~1000 posts maximum
- **Rate limiting**: 60 requests per minute, automatically handled by PRAW
- **Pagination delays**: 2-second delays between batches of 100 posts for large requests

### fetch_comments.py
- Only fetches top-level comments (no replies to comments)
- Works with public posts without requiring user authentication
- Handles deleted comments gracefully

### list_top_posts.py
- Real-time streaming shows progress for large datasets (up to 1000 posts)
- Memory-efficient generator-based processing
- Regex filtering happens during iteration to save memory
- Can be interrupted with Ctrl+C while preserving partial results

## Command Reference

### fetch_comments.py
```bash
python fetch_comments.py POST_ID [POST_ID ...] [--format {text,json}]

# Arguments:
#   POST_ID              One or more Reddit post IDs (required)
#   --format             Output format: text (default) or json
#
# Notes:
#   - Multiple posts are separated by clear dividers in text format
#   - JSON format returns array for multiple posts, single object for one post
#   - Progress shown on stderr when fetching multiple posts
```

### list_top_posts.py  
```bash
python list_top_posts.py SUBREDDIT [OPTIONS]

# Arguments:
#   SUBREDDIT            Subreddit name without r/ prefix (required)
#
# Options:
#   --time {hour,day,week,month,year,all}  Time filter (default: week)
#   --limit N                              Number of posts (default: 1000, max: 1000)  
#   --format {stream,text,json}            Output format (default: stream)
#   --filter-title REGEX                   Filter by title using regex pattern
```

### Environment Variables
```bash
# Required
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Optional  
REDDIT_USER_AGENT="Your App Name 1.0 (by /u/username)"
```

## Troubleshooting

### "Missing required environment variables"
Make sure your `.env` file exists and contains valid `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` values.

### "Error fetching post" (fetch_comments.py)
- Verify the post ID is correct
- Check that the post is public (not deleted or private)
- Ensure your Reddit API credentials are valid

### "Error accessing subreddit" (list_top_posts.py)
- Verify the subreddit name is correct (don't include 'r/' prefix)
- Check that the subreddit exists and is public
- Some subreddits may be private or quarantined

### "Invalid regex pattern"
- Test your regex pattern with a simple tool first
- Common regex characters need escaping: `\.`, `\?`, `\+`, etc.
- Use quotes around complex patterns: `--filter-title "pattern.*here"`

### Slow performance (list_top_posts.py)
- This is normal for large datasets due to Reddit's rate limiting
- Fetching 1000 posts takes ~20 minutes (2-second delays between batches)
- Use `--limit` to reduce the number of posts fetched
- Use streaming format (`--format stream`) to see progress in real-time

### direnv not working
- Install direnv: `nix profile install nixpkgs#direnv`
- Add to your shell config: `eval "$(direnv hook bash)"` (or zsh/fish)
- Run `direnv allow` in the project directory