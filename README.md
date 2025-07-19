# Reddit Comment Fetcher

A Python script that fetches top-level comments from Reddit posts using the PRAW (Python Reddit API Wrapper) library. Built with Nix flakes for reproducible development environments.

## Features

- Fetch top-level comments from any public Reddit post using just the post ID
- Two output formats: human-readable text (LLM-friendly) and structured JSON
- Secure credential management via environment variables
- Automatic development environment setup with Nix flakes and direnv

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

### Basic Usage

```bash
# Fetch comments in text format (default, LLM-friendly)
python fetch_comments.py <reddit_post_id>

# Fetch comments in JSON format
python fetch_comments.py <reddit_post_id> --format json
```

### Examples

```bash
# Using a Reddit post ID (the part after /comments/ in the URL)
python fetch_comments.py abc123def

# JSON output for programmatic use
python fetch_comments.py abc123def --format json

# Text output (default) - optimized for LLM consumption
python fetch_comments.py abc123def --format text
```

### Finding the Post ID

Reddit post URLs look like:
```
https://www.reddit.com/r/subreddit/comments/abc123def/post_title/
```

The post ID is `abc123def` (the part between `/comments/` and the next `/`).

## Output Formats

### Text Format (Default)
Human-readable format optimized for LLM consumption:
```
Post: Example Post Title
Score: 1234 | Total Comments: 56
URL: https://example.com

Top-level Comments (12):
==================================================

Comment 1 by username (Score: 42):
----------------------------------------
This is the comment text...

Comment 2 by another_user (Score: 15):
----------------------------------------
Another comment...
```

### JSON Format
Structured data for programmatic use:
```json
{
  "post_id": "abc123def",
  "post_title": "Example Post Title",
  "post_score": 1234,
  "post_url": "https://example.com",
  "total_comments": 56,
  "top_level_comments": [
    {
      "id": "comment_id",
      "author": "username",
      "score": 42,
      "body": "Comment text...",
      "created_utc": 1234567890
    }
  ]
}
```

## Environment Variables

- `REDDIT_CLIENT_ID`: Your Reddit app's client ID (required)
- `REDDIT_CLIENT_SECRET`: Your Reddit app's client secret (required)  
- `REDDIT_USER_AGENT`: User agent string (optional, defaults to "Comment Fetcher Bot 1.0")

## Notes

- Only fetches top-level comments (no replies to comments)
- Works with public posts without requiring user authentication
- Handles deleted comments gracefully
- Respects Reddit's API rate limits via PRAW

## Troubleshooting

### "Missing required environment variables"
Make sure your `.env` file exists and contains valid `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` values.

### "Error fetching post"
- Verify the post ID is correct
- Check that the post is public (not deleted or private)
- Ensure your Reddit API credentials are valid

### direnv not working
- Install direnv: `nix profile install nixpkgs#direnv`
- Add to your shell config: `eval "$(direnv hook bash)"` (or zsh/fish)
- Run `direnv allow` in the project directory