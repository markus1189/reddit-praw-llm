# Claude AI Assistant Guide for Reddit PRAW Toolkit

This document provides guidance for AI assistants working with this Reddit data extraction toolkit.

## Project Overview

This toolkit contains three complementary Python scripts for Reddit data extraction:

1. **`search_subreddits.py`** - Discovers and searches subreddits by topic, popularity, or recommendations
2. **`list_top_posts.py`** - Discovers and filters top posts from subreddits with advanced pagination
3. **`fetch_comments.py`** - Extracts detailed post content and top-level comments from specific Reddit posts

**Key Capabilities:**
- Discover subreddits by topic, popularity, or get personalized recommendations
- Extract up to 1000 posts from any subreddit with time filtering
- Real-time streaming output with progress tracking  
- Regex-based title filtering for targeted data collection
- Multiple output formats (streaming, text, JSON)
- Memory-efficient processing for large datasets
- Post content extraction including text posts and metadata

## Environment Setup

**Prerequisites Check:**
- Nix with flakes enabled
- direnv (optional but recommended)
- Reddit API credentials (client_id, client_secret, user_agent)

**Quick Setup Commands:**
```bash
# Initial setup
cp .env.example .env
# User must edit .env with their Reddit API credentials
direnv allow  # or `nix develop`
```

## Common Use Cases & Workflows

### 1. Research & Discovery
**Goal:** Find interesting posts on a topic
```bash
# Step 1: Discover relevant subreddits
python search_subreddits.py --search "python tutorial" --limit 10

# Step 2: Browse top posts in discovered subreddits
python list_top_posts.py learnpython --filter-title "tutorial" --time month

# Find AI/ML discussions
python list_top_posts.py MachineLearning --filter-title "(AI|ML|machine.*learning)" --time week
```

### 2. Content Analysis
**Goal:** Deep dive into specific posts
```bash
# Step 1: Find relevant subreddits
python search_subreddits.py --search "programming" --min-subscribers 10000

# Step 2: Find posts (note the post IDs in brackets)
python list_top_posts.py programming --filter-title "python"

# Step 3: Get detailed content for interesting posts
python fetch_comments.py abc123def  # Use post ID from step 2
```

### 3. Data Collection
**Goal:** Build datasets for analysis
```bash
# Export subreddit data
python list_top_posts.py datascience --time month --format json > dataset.json

# Get structured comment data
python fetch_comments.py xyz789 --format json > post_analysis.json
```

### 4. Monitoring & Tracking
**Goal:** Track discussions on specific topics
```bash
# Daily check for new discussions
python list_top_posts.py python --time day --filter-title "(release|update|new)"
```

## Command Patterns & Examples

### search_subreddits.py

**Basic Patterns:**
```bash
# Search by topic/keyword
python search_subreddits.py --search "machine learning"

# Get popular subreddits
python search_subreddits.py --popular --limit 50

# Find newly created subreddits
python search_subreddits.py --new --limit 25

# Get recommendations based on existing subreddits
python search_subreddits.py --recommend "python,datascience,MachineLearning"
```

**Advanced Filtering:**
```bash
# Filter by subscriber count
python search_subreddits.py --search "programming" --min-subscribers 10000 --max-subscribers 100000

# Exclude NSFW content (shows all by default)
python search_subreddits.py --popular --exclude-nsfw

# Filter by activity level
python search_subreddits.py --search "gamedev" --min-activity 50

# Sort results
python search_subreddits.py --search "python" --sort subscribers-desc
```

### list_top_posts.py

**Basic Patterns:**
```bash
# Default: stream last week's top posts
python list_top_posts.py SUBREDDIT

# Time filtering
python list_top_posts.py SUBREDDIT --time {hour|day|week|month|year|all}

# Limit posts (max 1000)
python list_top_posts.py SUBREDDIT --limit 500

# Title filtering (regex)
python list_top_posts.py SUBREDDIT --filter-title "PATTERN"

# Output formats
python list_top_posts.py SUBREDDIT --format {stream|text|json}
```

**Useful Regex Patterns:**
```bash
# Multiple keywords (OR)
--filter-title "(tutorial|guide|beginner)"

# Case-insensitive partial match
--filter-title "machine.*learning"

# Question posts
--filter-title "\?"

# Exclude certain terms
--filter-title "(?!.*deprecated).*python"
```

### fetch_comments.py

**Basic Patterns:**
```bash
# Single post: human-readable output
python fetch_comments.py POST_ID

# Multiple posts: compare discussions
python fetch_comments.py POST_ID1 POST_ID2 POST_ID3

# JSON for analysis (single or multiple)
python fetch_comments.py POST_ID --format json
python fetch_comments.py POST_ID1 POST_ID2 --format json

# Combine with list_top_posts.py
python list_top_posts.py SUBREDDIT | grep "\[.*\]" | # extract post IDs
python fetch_comments.py ID1 ID2 ID3  # analyze multiple posts
```

## Performance & Limitations

### Reddit API Constraints
- **Maximum posts per listing:** ~1000 (hard Reddit limit)
- **Rate limiting:** 60 requests/minute (auto-handled by PRAW)  
- **Pagination delays:** 2-second delays between 100-post batches
- **Large dataset timing:** 1000 posts ≈ 20 minutes

### Memory Usage
- `list_top_posts.py` uses generators (memory-efficient)
- Regex filtering happens during iteration (not post-processing)
- Safe to interrupt with Ctrl+C (preserves partial results)

### Practical Limits
- For analysis of 1000+ posts, consider breaking into smaller time periods
- Use streaming format for real-time feedback on large datasets
- JSON format is best for programmatic analysis

## Troubleshooting Guidance

### Common Issues & Solutions

**"Missing environment variables"**
- Guide user to check `.env` file exists with valid credentials
- Remind about Reddit app setup at reddit.com/prefs/apps

**"Error accessing subreddit"**
- Check subreddit name (no 'r/' prefix needed)
- Verify subreddit exists and is public
- Some subreddits may be private/quarantined

**"Invalid regex pattern"**
- Help user test regex patterns
- Remind about escaping special characters
- Suggest using quotes around complex patterns

**Slow performance**
- Explain Reddit's rate limiting (normal behavior)
- Suggest reducing `--limit` for faster results
- Recommend streaming format for progress visibility

### Post ID Extraction
Reddit URLs: `https://reddit.com/r/SUBREDDIT/comments/POST_ID/title/`
Post ID is the part between `/comments/` and the next `/`

## Reddit Analysis Protocol

When analyzing Reddit content for any topic:

### Source Reference Requirements
- **Always include clickable source links**: `[Post Title](permalink)` format
- **Credit authors**: Use `u/username` format  
- **Show community validation**: Include `(X upvotes)` scores
- **Use direct quotes**: With proper attribution when impactful
- **Organize insights**: By relevance to user's topic
- **Enable verification**: Link to original discussions for follow-up

### Standard Reference Format
```markdown
**Source**: [Post Title](https://reddit.com/r/SUBREDDIT/comments/POST_ID) by u/author (score upvotes)
```

### Analysis Template for Any Topic
```markdown
Analyze these Reddit posts about [TOPIC] from r/[SUBREDDIT]. For each key insight:

1. **Include source reference**: [Post Title](permalink) by u/username (Score upvotes)
2. **Extract key insights** relevant to [TOPIC]
3. **Use direct quotes** with attribution when impactful
4. **Organize by themes** or importance
5. **Note community consensus** via upvote patterns

Format each insight as:
### Insight Title (Score upvotes)
**Source**: [Post Title](link) by u/author
**Key Point**: Summary...
> "Relevant quote from post or comments"
> — u/author

Make sources clickable so readers can verify claims and engage with original authors.
```

## Topic-Agnostic Discovery Patterns

### Universal Search Patterns
```bash
# Find tutorials/guides in any field
python list_top_posts.py SUBREDDIT --filter-title "(tutorial|guide|how.*to)" 

# Find best practices
python list_top_posts.py SUBREDDIT --filter-title "(best.*practice|tip|trick|hack)"

# Find tools/resources  
python list_top_posts.py SUBREDDIT --filter-title "(tool|resource|library|framework)"

# Find problem-solving discussions
python list_top_posts.py SUBREDDIT --filter-title "(problem|issue|solution|fix)"

# Find experience sharing
python list_top_posts.py SUBREDDIT --filter-title "(experience|lesson|mistake|learn)"
```

### Flexible Analysis Workflow
```bash
# Step 1: Broad discovery
python list_top_posts.py SUBREDDIT --time month --limit 50

# Step 2: Focused filtering  
python list_top_posts.py SUBREDDIT --filter-title "RELEVANT_TERMS" --time week

# Step 3: Deep analysis with source references
python fetch_comments.py INTERESTING_POST_IDS

# Step 4: Synthesize with proper attribution
```

### Example Use Cases

**Learning a Programming Language:**
```bash
python list_top_posts.py learnpython --filter-title "(beginner|tutorial|resource)" --time month
# → Analyze for learning paths, common mistakes, best resources
```

**Market Research:**
```bash
python list_top_posts.py startups --filter-title "(market|customer|product.*fit)" --time year  
# → Analyze for market insights, validation strategies, customer research
```

**Tool Evaluation:**
```bash
python list_top_posts.py MachineLearning --filter-title "(tool|library|framework)" --time month
# → Analyze for tool comparisons, use cases, community preferences
```

## Best Practices for AI Assistants

### Guiding Users Effectively

1. **Start with Discovery**
   - Always suggest `list_top_posts.py` first for exploration
   - Help users craft effective regex patterns for filtering
   - Explain time filter options based on their needs

2. **Progressive Refinement**
   - Start with broad searches, then narrow down
   - Use shorter time periods for active subreddits
   - Adjust limits based on user patience/needs

3. **Output Format Selection**
   - Stream: Real-time exploration and discovery
   - Text: Human review and summary reports with source references
   - JSON: Data analysis and programmatic processing

4. **Workflow Integration**
   - Show how to chain the two scripts together
   - Demonstrate extracting post IDs from list output
   - Explain when to use each tool
   - Always emphasize source attribution in final analysis

### Common User Scenarios

**"I want to analyze discussions about X"**
1. Use `list_top_posts.py` with title filter to find relevant posts
2. Review results and identify interesting post IDs
3. Use `fetch_comments.py` to get detailed content for specific posts

**"I need data for research"**
1. Use JSON output format for structured data
2. Consider multiple subreddits and time periods
3. Plan for Reddit's rate limiting in timeline

**"I want to monitor a topic"**
1. Use shorter time periods (day/week)
2. Set up regex patterns for topic keywords
3. Use streaming format for immediate feedback

## Integration Patterns

### Chaining Commands
```bash
# Find posts, then analyze top ones
python list_top_posts.py python --filter-title "tutorial" --limit 50 --format json | \
jq '.posts[0:5].id' | \
xargs -I {} python fetch_comments.py {}
```

### Data Pipeline
```bash
# 1. Discovery
python list_top_posts.py datascience --time month --format json > posts.json

# 2. Filter and extract IDs
jq '.posts[] | select(.score > 100) | .id' posts.json > high_score_ids.txt

# 3. Detailed analysis
cat high_score_ids.txt | xargs -I {} python fetch_comments.py {} --format json
```

### Batch Processing
```bash
# Process multiple subreddits
for sub in python javascript golang; do
    python list_top_posts.py $sub --time week --format json > ${sub}_posts.json
done
```

## Advanced Analysis Techniques

### Sub-Agent Batching for Large-Scale Analysis

When analyzing large datasets that might exceed context limits, use this sub-agent batching approach:

```bash
# 1. Discover relevant subreddits
python search_subreddits.py --search "topic" --limit 20

# 2. Discover posts and extract IDs
python list_top_posts.py SUBREDDIT --time week --limit 100 --format json

# 3. Extract post IDs and batch them
echo 'POST_ID1 POST_ID2 POST_ID3...' | tr ' ' '\n' | split -l 10 - post_batch_

# 4. Use Task tool with summarizing prompts for each batch
# Task tool prompt example:
# "Analyze Reddit posts from r/SUBREDDIT. Read post IDs from post_batch_aa, 
# use fetch_comments.py to get detailed content, then provide a 2-3 paragraph 
# summary focusing on: common themes, popular genres, reading situations, 
# notable book recommendations, and engagement patterns."

# 5. Compile final analysis from batch summaries
```

**Benefits:**
- Manages context size effectively for large datasets
- Enables parallel processing of post batches
- Provides focused analysis on specific subsets
- Allows for comprehensive final synthesis

**Use Cases:**
- Discovering communities around emerging topics
- Analyzing 50+ posts from active subreddits
- Conducting deep content analysis requiring detailed comment examination
- Research projects needing systematic approach to large communities
- Comparative analysis across multiple time periods or subreddits

## Notes for Development

- Scripts use PRAW generators for memory efficiency
- Error handling includes graceful degradation
- Progress tracking uses stderr (preserves stdout for data)
- All scripts share authentication pattern
- Regex compilation happens once per run
- CTRL+C handling preserves partial results

This toolkit is designed for researchers, content creators, and analysts who need structured Reddit data extraction with filtering capabilities. The three-script pipeline enables complete workflow from topic discovery to detailed content analysis.