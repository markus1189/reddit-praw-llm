# Claude AI Assistant Guide for Reddit PRAW Toolkit

This document provides guidance for AI assistants working with this Reddit data extraction toolkit.

## Project Overview

This toolkit contains three complementary Python scripts for Reddit data extraction:

1. **`search_subreddits.py`** - Discovers and searches subreddits by topic, popularity, or recommendations
2. **`list_top_posts.py`** - Discovers and filters top posts from subreddits with advanced pagination
3. **`fetch_comments.py`** - Extracts detailed post content and complete comment trees (including nested replies) from specific Reddit posts

**Key Capabilities:**
- Discover subreddits by topic, popularity, or get personalized recommendations
- Extract up to 1000 posts from any subreddit with time filtering
- Real-time streaming output with progress tracking  
- Regex-based title filtering for targeted data collection
- Multiple output formats (streaming, text, JSON)
- Memory-efficient processing for large datasets
- Post content extraction including text posts and metadata
- Complete comment tree extraction with configurable depth and limits
- Nested reply analysis for deep discussion insights

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
# Single post: human-readable output with full comment trees
python fetch_comments.py POST_ID

# Multiple posts: compare discussions
python fetch_comments.py POST_ID1 POST_ID2 POST_ID3

# JSON for analysis (single or multiple)
python fetch_comments.py POST_ID --format json
python fetch_comments.py POST_ID1 POST_ID2 --format json

# Control comment depth and volume
python fetch_comments.py POST_ID --max-depth 2 --max-comments 10

# Backward compatibility: top-level comments only
python fetch_comments.py POST_ID --top-level-only

# Combine with list_top_posts.py
python list_top_posts.py SUBREDDIT | grep "\[.*\]" | # extract post IDs
python fetch_comments.py ID1 ID2 ID3  # analyze multiple posts
```

**Advanced Comment Fetching:**
```bash
# Deep discussion analysis (unlimited depth)
python fetch_comments.py POST_ID --format json

# Controlled depth for large threads
python fetch_comments.py POST_ID --max-depth 3 --max-comments 20

# Focus on top-level discussions only
python fetch_comments.py POST_ID --top-level-only

# Batch analysis with depth control
python fetch_comments.py ID1 ID2 ID3 --max-depth 2 --format json

# Large thread management (avoid API limits)
python fetch_comments.py VIRAL_POST_ID --max-depth 1 --max-comments 50
```

## Performance & Limitations

### Reddit API Constraints
- **Maximum posts per listing:** ~1000 (hard Reddit limit)
- **Rate limiting:** 60 requests/minute (auto-handled by PRAW)  
- **Pagination delays:** 2-second delays between 100-post batches
- **Large dataset timing:** 1000 posts ≈ 20 minutes
- **Comment tree depth:** Unlimited by default, but deep threads may hit API limits
- **"More comments" expansion:** Automatically handled but may increase fetch time

### Memory Usage
- `list_top_posts.py` uses generators (memory-efficient)
- `fetch_comments.py` builds comment trees in memory (use limits for large threads)
- Regex filtering happens during iteration (not post-processing)
- Safe to interrupt with Ctrl+C (preserves partial results)

### Practical Limits
- For analysis of 1000+ posts, consider breaking into smaller time periods
- Use streaming format for real-time feedback on large datasets
- JSON format is best for programmatic analysis
- For viral posts with 1000+ comments, use `--max-depth` and `--max-comments` limits
- Deep comment trees (depth > 5) may significantly increase processing time

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

5. **Subagent Integration** (Recommended)
   - **Prefer subagents** over manual script chaining for complex research
   - **Start with orchestrator** for comprehensive research initiatives
   - **Use individual agents** for specific sub-tasks (discovery, curation, synthesis)
   - **Maintain Analysis Protocol** standards through automated attribution

### Common User Scenarios

**"I want to analyze discussions about X"**
1. Use `list_top_posts.py` with title filter to find relevant posts
2. Review results and identify interesting post IDs
3. Use `fetch_comments.py` to get detailed content including nested discussions
4. For large threads, use `--max-depth 2 --max-comments 20` to focus on quality content

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

# 3. Detailed analysis with comment tree control
cat high_score_ids.txt | xargs -I {} python fetch_comments.py {} --max-depth 2 --format json
```

### Batch Processing
```bash
# Process multiple subreddits
for sub in python javascript golang; do
    python list_top_posts.py $sub --time week --format json > ${sub}_posts.json
done
```

## Advanced Analysis Techniques

### Reddit Research Subagents (Recommended Approach)

This project includes specialized Claude Code subagents designed for efficient Reddit research workflows. These agents are located in `.claude/agents/` and provide context-efficient, orchestrated research capabilities.

#### Available Subagents:

**1. reddit-discovery-specialist**
- **Purpose**: Find relevant subreddits and optimize search strategies  
- **Use When**: Starting research on new topics
- **Capabilities**: Topic analysis, subreddit discovery, parameter optimization

**2. reddit-content-curator**  
- **Purpose**: Filter and prioritize posts based on research goals
- **Use When**: Dealing with large post volumes
- **Capabilities**: Regex pattern crafting, quality assessment, batch processing

**3. reddit-analysis-synthesizer**
- **Purpose**: Process large volumes of Reddit content with proper source attribution
- **Use When**: Analyzing 10+ posts or complex discussions  
- **Capabilities**: Theme extraction, source attribution, content organization

**4. reddit-research-orchestrator**
- **Purpose**: Coordinate complex Reddit research workflows
- **Use When**: Comprehensive research initiatives
- **Capabilities**: Workflow planning, agent coordination, quality control

#### Subagent Workflow Patterns:

**Simple Research** (Single topic):
```bash
# Deploy orchestrator with research topic
# Example: "Research ultrarunning nutrition tips from Reddit"
# Orchestrator automatically coordinates other agents
```

**Exploratory Research** (New topic):
```
1. Discovery Agent → Find relevant subreddits
2. Curator Agent → Filter high-value posts per subreddit  
3. Synthesizer Agent → Batch analyze top posts
4. Orchestrator → Compile comprehensive report
```

**Focused Investigation** (Known area):
```
1. Curator Agent → Deep dive specific subreddits
2. Synthesizer Agent → Detailed comment analysis
3. Orchestrator → Generate focused insight report
```

**Comparative Analysis** (Multiple perspectives):
```
1. Discovery Agent → Map ecosystem of related communities
2. Curator Agent → Parallel content collection
3. Synthesizer Agent → Compare/contrast insights
4. Orchestrator → Generate comparative analysis
```

#### Benefits of Subagent Approach:
- **Context Efficiency**: Each agent has its own context window
- **Specialized Expertise**: Purpose-built for specific research tasks
- **Automated Source Attribution**: Built-in Reddit Analysis Protocol compliance
- **Scalable Workflows**: Handle large research projects without token limits
- **Quality Assurance**: Consistent research methodology and output formatting

#### Usage Recommendations:
- **Always start with reddit-research-orchestrator** for complex research
- **Use individual agents** for specific sub-tasks when needed
- **Leverage existing Analysis Protocol** for source attribution standards
- **Combine with manual scripts** for specialized data collection needs

### Legacy Sub-Agent Batching for Large-Scale Analysis

For advanced users preferring manual control, the traditional batching approach remains available:

```bash
# 1. Discover relevant subreddits
python search_subreddits.py --search "topic" --limit 20

# 2. Discover posts and extract IDs
python list_top_posts.py SUBREDDIT --time week --limit 100 --format json

# 3. Extract post IDs and batch them
echo 'POST_ID1 POST_ID2 POST_ID3...' | tr ' ' '\n' | split -l 10 - post_batch_

# 4. Use Task tool with summarizing prompts for each batch
# 5. Compile final analysis from batch summaries
```

**Note**: The specialized Reddit subagents provide a more streamlined and reliable approach for most research use cases.

## Notes for Development

- Scripts use PRAW generators for memory efficiency
- Error handling includes graceful degradation
- Progress tracking uses stderr (preserves stdout for data)
- All scripts share authentication pattern
- Regex compilation happens once per run
- CTRL+C handling preserves partial results

This toolkit is designed for researchers, content creators, and analysts who need structured Reddit data extraction with filtering capabilities. The three-script pipeline enables complete workflow from topic discovery to detailed content analysis.