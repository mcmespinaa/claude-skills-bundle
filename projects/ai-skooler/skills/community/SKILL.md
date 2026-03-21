---
name: community
description: Scrape and analyze community feed posts from a Skool community. Extracts high-value posts, comments, and emerging use cases. Use when user says /community followed by a Skool URL, or asks to scrape community posts, analyze a feed, or extract use cases from Skool.
---

# Community Feed Scraper & Analyzer

Scrapes community posts from a Skool feed, extracts high-value content, and creates analysis documents in the Obsidian vault.

## Prerequisites

- Playwright MCP must be available
- Chrome must be fully quit before Playwright can launch
- Authenticated Skool session (cookies persist in Playwright user-data-dir)

## Input

The user provides either:

- A Skool community URL: `https://www.skool.com/<slug>` → scrape full feed
- A specific post URL: `https://www.skool.com/<slug>/<post-slug>?p=<post-id>` → scrape single post

Determine mode from the URL format.

## Mode 1: Single Post Scrape

When user provides a specific post URL.

### Step 1: Navigate to the post

Do NOT navigate directly to the post URL — Skool's `?p=` parameter redirects unreliably.

Instead:

1. Navigate to the community feed: `https://www.skool.com/<slug>`
2. Find the post by title in the feed
3. Click the post title to open it as a modal overlay

### Step 2: Expand all content

Before extracting, expand everything:

1. Click all "See more" buttons (post body truncation)
2. Click all "View N more replies" buttons (threaded comments)
3. Wait for content to fully load after each expansion

### Step 3: Extract post content

Use `browser_run_code` with the DOM-to-markdown extractor from [references/dom-extractor.md](references/dom-extractor.md).

Extract:

- Post title and author
- Post body content
- All comments with author attribution
- Threaded replies (indicate reply targets with `@username`)
- Any attached links or resources

### Step 4: Create vault file

Create the file at `Obsidian/ai-skooler/<Community>/Community Posts/<Descriptive Title>.md`

Structure:

```yaml
---
type: community-post
community: "<Community Name>"
author: "<Author Name>"
source: "<full-url>"
---
```

Sections:

1. Post content (preserve author's structure)
2. Community Discussion (comments as blockquotes with author names as H3)
3. Actionable Ideas from Comments (extract 3-5 implementation insights)
4. Related Lessons (wiki-links to relevant classroom content)

### Step 5: Update Course Index

Add the post to the Community Posts section in `Course Index.md`:

```markdown
- [[<Post Title>]] — <one-line description>
```

### Important: Wiki-links in tables

NEVER use wiki-link display syntax (`[[note|display]]`) inside markdown tables — the `|` breaks column parsing. Either use the full wiki-link without display text, or place the link outside the table.

---

## Mode 2: Full Feed Analysis

When user provides a community feed URL.

### Step 1: Navigate to feed

Navigate to `https://www.skool.com/<slug>`.

### Step 2: Paginate through all pages

Skool uses JS-only pagination. URL parameters do NOT work.

Use the "Next" button to paginate:

```javascript
const nextButton = page.getByText("Next");
await nextButton.scrollIntoViewIfNeeded();
await nextButton.click();
await page.waitForTimeout(2000);
```

Do NOT click page number buttons — they match SVG text in member avatar elements and a modal overlay intercepts the clicks.

### Step 3: Extract post metadata from each page

For each page, use `browser_run_code` to extract:

- Post title
- Author name
- Like count
- Comment count
- Preview text (first ~200 chars)
- Post URL

Save each page's data to `/tmp/skool_feed_page_<N>.json`.

### Step 4: Parse results

Results from `browser_run_code` come as JSON inside markdown. May require extraction:

````javascript
const raw = result.split("### Result\n")[1];
const json = raw.replace(/```json\n|\n```/g, "");
const data = JSON.parse(json);
````

### Step 5: Filter for high-value posts

From the collected metadata, identify high-value posts:

- Posts showing real builds or implementations (not intros/celebrations)
- Posts with high engagement (likes + comments)
- Posts sharing resources (GitHub repos, tools, frameworks)
- Posts with technical depth or novel applications

Exclude:

- Introduction posts
- Milestone celebrations
- General chat or questions with no substance
- Lesson check-in polls

### Step 6: Synthesize into analysis document

Create `Obsidian/ai-skooler/<Community>/Community Posts/Emerging Use Cases - Community Feed Analysis.md`

```yaml
---
type: community-post
community: "<Community Name>"
author: analysis
source: "https://www.skool.com/<slug>"
date_scraped: "YYYY-MM-DD"
posts_analyzed: <total-count>
---
```

Organize findings by theme:

- Group related posts into themes (e.g., Knowledge Architecture, Production Systems, Agent Infrastructure)
- For each theme: describe the pattern, name specific members and what they built, list tools/resources shared
- Include a "Key Resources Shared" section with URLs
- Include a "Community Intelligence" section with demographics and meta-patterns
- End with Related section linking to Course Index and notable individual posts

### Step 7: Update Course Index

Add the analysis to the Community Posts section in `Course Index.md`.

### Step 8: Report results

Report:

- Total posts analyzed
- Number of high-value posts identified
- Themes discovered
- Any notable resources or repos found

## Error Handling

### Playwright won't launch

Chrome is running. Ask user to confirm, then `pkill -f "Google Chrome"`.

### Pagination breaks

If "Next" button click fails, try scrolling to bottom first. The button may be below the viewport.

### Token limits on large feeds

Save each page to `/tmp/` and process with Python after collection.

### Post modal won't open

Click the post title text directly, not the surrounding card element. Use `getByText()` with the exact title.

### Prettier reformats tables

Re-read the file after writing before attempting to edit it — prettier runs as a PostToolUse hook and reformats table alignment.
