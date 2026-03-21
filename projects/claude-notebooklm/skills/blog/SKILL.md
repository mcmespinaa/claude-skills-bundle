---
name: blog
description: Create and publish blog posts to GoHighLevel (GHL) and/or ShopWired blog sites from any content source — NotebookLM artifacts, Obsidian notes, markdown files, URLs, or raw topics. Use when user says "write a blog post", "publish to blog", "create a blog about...", "blog this", "turn this into a blog post", or invokes /blog. Converts content to SEO-optimized HTML, uploads featured images, and publishes via GHL Blog API and/or ShopWired Blog API. Do NOT use for social media posts — use /distribute or /linkedin instead. Do NOT use for email newsletters — use /newsletter instead.
argument-hint: '"source" [--location ces|...] [--destination ghl|shopwired|both] [--status DRAFT|PUBLISHED] [--blog-id "..."] [--schedule "ISO datetime"]'
disable-model-invocation: true
---

# /blog — Blog Post Creator & Publisher

> **Trigger:** User says `/blog`, "write a blog post", "publish to blog", "blog this", "create a blog about...", "turn this into a blog post", or similar.

## Role

You create SEO-optimized blog posts from any content source and publish them to GHL blog sites, ShopWired stores, or both. You write in the brand's voice, optimize for search engines, generate structured HTML, and handle the full lifecycle: draft, preview, publish, or schedule.

---

## Destination Routing

The `--destination` flag controls where the blog post is published:

| Flag | Behavior |
|------|----------|
| `--destination ghl` | Publish to GHL blog only (default) |
| `--destination shopwired` | Publish to ShopWired blog only |
| `--destination both` | Publish to both GHL and ShopWired |

If no `--destination` is provided, default to `ghl` (backward compatible).

When `--destination shopwired` or `both`: the location must have `shopwiredApiKeyVar` and `shopwiredApiSecretVar` in `locations.json`. If missing, stop and tell the user.

---

## Constants

```
BLOG_SCRIPTS_DIR: ${CLAUDE_PLUGIN_ROOT}/skills/blog/scripts
BRAND_DOCS_DIR: Resolved in Step 0 — $PWD/brands/<LOCATION>/ if it exists,
                else ${CLAUDE_PLUGIN_ROOT}/skills/distribute/references (fallback)
BRAND_VOICE_PATH: <BRAND_DOCS_DIR>/brand-voice.md
BLOG_WRITING_GUIDE: ${CLAUDE_PLUGIN_ROOT}/skills/blog/references/blog-writing-guide.md
BLOG_SEO_GUIDE: ${CLAUDE_PLUGIN_ROOT}/skills/blog/references/blog-seo.md
```

---

## Content Sources

| Source | How It Arrives | Action |
|--------|---------------|--------|
| NotebookLM report/summary | `.md` file | Convert to blog HTML |
| Obsidian note | File path or vault note | Read and adapt into blog format |
| Markdown file | `.md` path | Convert to blog HTML |
| URL | Web link | Fetch, extract key points, write original blog post |
| Raw topic | "blog about AI agents" | Research and write from scratch |
| Existing blog post | `--update <postId>` | Fetch, edit, and update |

---

## Workflow

### Step 0: Resolve Location, Destination & Blog Site

1. If `--location <shorthand>` is provided, use that location.
2. If no `--location`, read `locations.json`:
   - **Single location:** Use it automatically.
   - **Multiple locations:** Ask: "Which location?"
3. Resolve API key and brand directory via init.sh.
4. Parse `--destination` flag: `ghl` (default), `shopwired`, or `both`.

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve_location.sh" \
  --export --location <LOCATION>
```

**If destination includes `ghl`:**

5a. Discover GHL blog sites:
```bash
bash "${BLOG_SCRIPTS_DIR}/ghl_get_blogs.sh" \
  --action sites \
  --location <LOCATION>
```
   - **Single blog site:** Use it automatically.
   - **Multiple sites:** Ask: "Which blog site? Available: [names]"
   - **No blog sites:** Stop. "No GHL blog sites found. Create one in GHL first."
   - Store the resolved `BLOG_ID`.

**If destination includes `shopwired`:**

5b. Verify ShopWired credentials exist in `locations.json` (`shopwiredApiKeyVar`, `shopwiredApiSecretVar`). Fetch ShopWired blog metadata:
```bash
bash "${BLOG_SCRIPTS_DIR}/sw_get_blog_meta.sh" \
  --action categories \
  --location <LOCATION>
```
ShopWired has a single blog per store (no blog site selection needed).

### Step 1: Gather Input & Source Material

Collect from the user:

| Input | How |
|-------|-----|
| **Source** | File path, URL, topic, or "use latest NotebookLM report" |
| **Target audience** | Optional. Default: infer from brand voice |
| **Status** | Optional. Default: `DRAFT` (safe — user publishes when ready) |
| **Schedule** | Optional. ISO datetime for scheduled publishing |

**Source resolution:**
- **File path:** Read the file directly.
- **URL:** Fetch with `WebFetch` to extract content. Write an original blog post (not a copy).
- **Topic string:** Research the topic, then write from scratch.
- **NotebookLM artifact:** Run `notebooklm artifact list --json`, find the latest report/summary, download it.
- **Obsidian note:** Read from vault path.

### Step 2: Fetch Blog Metadata

Fetch categories and authors in parallel — needed for the blog post payload.

**For GHL destination:**
```bash
bash "${BLOG_SCRIPTS_DIR}/ghl_get_blogs.sh" \
  --action categories \
  --location <LOCATION>
```
```bash
bash "${BLOG_SCRIPTS_DIR}/ghl_get_blogs.sh" \
  --action authors \
  --location <LOCATION>
```

**For ShopWired destination:**
```bash
bash "${BLOG_SCRIPTS_DIR}/sw_get_blog_meta.sh" \
  --action categories \
  --location <LOCATION>
```
```bash
bash "${BLOG_SCRIPTS_DIR}/sw_get_blog_meta.sh" \
  --action tags \
  --location <LOCATION>
```

ShopWired does not have an authors API — the `author` field is set automatically by the store.

- **Categories:** Present the list to the user if the source doesn't map to an obvious category. Otherwise, pick the best match automatically.
- **Authors (GHL only):** If only one author, use it. If multiple, ask or use the default.
- **For `--destination both`:** Fetch from both APIs. Categories may differ between platforms — map by name when possible, ask user if ambiguous.

### Step 3: Write the Blog Post

**Before writing, read these reference files:**
1. `BRAND_VOICE_PATH` — tone, banned words, writing rules
2. `BLOG_WRITING_GUIDE` — blog-specific structure, formatting, and patterns
3. `BLOG_SEO_GUIDE` — on-page SEO checklist (title tags, meta description, headings, internal links)

Write the blog post with these elements:

| Element | Requirement |
|---------|-------------|
| **Title** | 50-60 chars, includes primary keyword, compelling |
| **Meta description** | 150-160 chars, includes keyword, has CTA |
| **URL slug** | Lowercase, hyphenated, 3-5 words, keyword-rich |
| **Featured image alt text** | Descriptive, includes keyword naturally |
| **Body** | 800-2000 words (adjustable), structured with H2/H3 headings |
| **Tags** | 3-8 relevant tags |

**Blog body structure:**
1. **Hook intro** — 2-3 sentences that establish the problem or opportunity
2. **Context** — why this matters now
3. **Main sections** — 3-5 H2 sections, each with a clear subtopic
4. **Actionable takeaways** — bullet points or numbered list
5. **Conclusion** — summary + CTA (subscribe, contact, read next)

Write in the brand's voice. No em dashes, no banned words, no fluff. Every paragraph should earn its place.

### Step 4: Convert to HTML

Convert the markdown blog content to clean, semantic HTML:

```bash
python3 "${BLOG_SCRIPTS_DIR}/md_to_blog_html.py" \
  "<content_file.md>" > /tmp/blog_post.html
```

The script produces semantic HTML (not email-style table layout). It outputs:
- Clean `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>` tags
- No inline styles (the GHL blog theme handles styling)
- Proper `<a>` tags with `rel="noopener"` for external links
- `<img>` tags with alt text for any embedded images

### Step 5: Fetch Featured Image

If the user hasn't provided a featured image:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/unsplash_fetch.py" \
  --query "<blog topic keywords>" \
  --orientation landscape \
  --output-dir /tmp
```

Parse the JSON output. The featured image URL will be passed to the blog post payload as `imageUrl`. For GHL blogs, use the Unsplash source URL directly (GHL stores images by URL reference).

Use the sidecar `.json` for attribution — add "Photo by {Name} on Unsplash" at the bottom of the blog post body.

### Step 6: Validate URL Slug

Before publishing, check that the slug is unique:

```bash
bash "${BLOG_SCRIPTS_DIR}/ghl_get_blogs.sh" \
  --action check-slug \
  --slug "<proposed-slug>" \
  --location <LOCATION>
```

If the slug exists, append a counter: `my-blog-post-2`.

### Step 7: Preview & Approval

Present the complete blog post for review:

```
## Blog Post Preview

**Title:** [title]
**Slug:** /post/[url-slug]
**Status:** [DRAFT|PUBLISHED|SCHEDULED]
**Category:** [category name]
**Author:** [author name]
**Tags:** [tag1, tag2, tag3]
**Meta description:** [description]
**Featured image:** [image URL or "none"]

---

[Full blog post content in markdown for readability]

---

Approve, edit, or regenerate?
```

Do NOT proceed until the user approves.

### Step 8: Publish

Route to the correct API(s) based on `--destination`.

**GHL** (`--destination ghl` or `both`):

```bash
bash "${BLOG_SCRIPTS_DIR}/ghl_create_blog_post.sh" \
  --title "<title>" \
  --blog-id "<BLOG_ID>" \
  --description "<meta_description>" \
  --html-file "/tmp/blog_post.html" \
  --status "<DRAFT|PUBLISHED|SCHEDULED>" \
  --image-url "<featured_image_url>" \
  --image-alt "<alt_text>" \
  --slug "<url-slug>" \
  --author "<author_id>" \
  --categories "<cat_id1,cat_id2>" \
  --tags "<tag1,tag2,tag3>" \
  --published-at "<ISO_datetime>" \
  --location <LOCATION>
```

**ShopWired** (`--destination shopwired` or `both`):

```bash
bash "${BLOG_SCRIPTS_DIR}/sw_create_blog_post.sh" \
  --title "<title>" \
  --slug "<url-slug>" \
  --html-file "/tmp/blog_post.html" \
  --meta-title "<seo_title>" \
  --meta-description "<meta_description>" \
  --meta-keywords "<keyword1, keyword2>" \
  --image-url "<featured_image_url>" \
  --excerpt "<excerpt_150_chars>" \
  --category-id <shopwired_category_id> \
  --tags "<tag1,tag2,tag3>" \
  --active <true|false> \
  --release-date "<ISO_datetime>" \
  --location <LOCATION>
```

**Status mapping for ShopWired:**
| Blog Skill Status | ShopWired `--active` |
|---|---|
| `DRAFT` | `false` |
| `PUBLISHED` | `true` |
| `SCHEDULED` | `false` + `--release-date` |

**For `--destination both`:** Run both scripts. Report results from each. If one fails, still attempt the other and report partial success.

Parse the JSON responses to get post IDs and confirmations from each platform.

### Step 9: Log & Confirm

Append to `blog_post_log.md` at project root:

```
| <LOCATION> | <destination> | <title> | <status> | <datetime> | <post_id> | <url_slug> |
```

For `--destination both`, log one row per platform (two rows).

Confirm to user:

**GHL:** "Blog post created on GHL. Title: '[title]'. Status: [status]. Slug: /post/[slug]. Post ID: [id]."

**ShopWired:** "Blog post created on ShopWired. Title: '[title]'. Active: [true/false]. URL: [url]. Post ID: [id]."

If status is `PUBLISHED` / active is `true`, provide the live URL.

---

## Updating Existing Posts

When the user says "update the blog post" or passes `--update <postId>`:

1. Determine destination: GHL post IDs are alphanumeric strings, ShopWired post IDs are integers.
2. Fetch the existing post content:
   - **ShopWired:** `sw_get "/blog-posts/<id>?embed=content"` returns full content.
   - **GHL:** Not yet available via API — ask the user to provide the current content or URL.
3. Apply edits as instructed.
4. Convert to HTML.
5. Update via the appropriate script:

**GHL:**
```bash
bash "${BLOG_SCRIPTS_DIR}/ghl_update_blog_post.sh" \
  --post-id "<postId>" \
  --title "<title>" \
  --blog-id "<BLOG_ID>" \
  --description "<meta_description>" \
  --html-file "/tmp/blog_post.html" \
  --status "<status>" \
  --image-url "<featured_image_url>" \
  --image-alt "<alt_text>" \
  --slug "<url-slug>" \
  --author "<author_id>" \
  --categories "<cat_id1,cat_id2>" \
  --tags "<tag1,tag2>" \
  --published-at "<ISO_datetime>" \
  --location <LOCATION>
```

**ShopWired:**
```bash
bash "${BLOG_SCRIPTS_DIR}/sw_update_blog_post.sh" \
  --post-id <postId> \
  --title "<title>" \
  --slug "<url-slug>" \
  --html-file "/tmp/blog_post.html" \
  --meta-title "<seo_title>" \
  --meta-description "<meta_description>" \
  --tags "<tag1,tag2>" \
  --active <true|false> \
  --location <LOCATION>
```

---

## Quick Examples

**Blog to GHL (default):**
```
/blog "5 ways AI agents are changing customer service" --location ces
```

**Blog to ShopWired only:**
```
/blog ./report.md --destination shopwired --location ces
```

**Blog to both GHL and ShopWired:**
```
/blog ./summary.md --destination both --status PUBLISHED --location ces
```

**Blog from a NotebookLM report:**
```
/blog ./report.md --status PUBLISHED --location ces
```

**Blog from a URL (repurpose):**
```
/blog "https://example.com/article" --location ces
→ Fetches article, writes original blog post inspired by it, publishes as draft
```

**Blog from Obsidian note:**
```
/blog ~/Obsidian/Claude-Brain/01-Projects/ai-agents-research.md
```

**Schedule a blog post:**
```
/blog ./summary.md --schedule "2026-03-10T09:00:00Z" --location ces
```

**Update GHL post:**
```
/blog --update "66c381b38be80858b9af62b6" --location ces
```

**Update ShopWired post:**
```
/blog --update 12345 --destination shopwired --location ces
```

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| 401 from GHL | GHL token expired | "GHL token expired. Update `GHL_API_KEY` in .env." |
| 401 from ShopWired | Bad API key/secret | "ShopWired auth failed. Check credentials in .env." |
| 400/422 Bad Request | Invalid payload | Show raw response, check required fields |
| No blog sites found (GHL) | Location has no blogs | "No GHL blog sites. Create one in GHL first." |
| No categories found | Blog has no categories | Create post without categories |
| No authors found (GHL) | Blog has no authors | "No authors found. Add an author in GHL blog settings." |
| Missing ShopWired creds | `shopwiredApiKeyVar` not in locations.json | Show setup instructions |
| Slug already exists | Duplicate URL slug | Auto-append counter (`-2`, `-3`) and retry |
| Featured image fetch fails | Unsplash rate limit or error | Proceed without image, warn user |
| HTML conversion fails | Malformed markdown | Show error, offer to publish raw HTML |
| File not found | Invalid source path | "File not found at `<path>`. Check the path." |
| Partial failure (`both`) | One platform fails | Report which succeeded, which failed, continue |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading `locations.json`
- Fetching blog sites, categories, and authors (GHL and/or ShopWired)
- Checking URL slug uniqueness
- Converting markdown to HTML (`md_to_blog_html.py`)
- Fetching featured images from Unsplash
- Reading brand voice and blog writing guides

**Ask before running:**
- Creating or updating blog posts on any platform — always show preview first
- Publishing (status `PUBLISHED` / active `true`) — explicit confirmation required
- Downloading artifacts from NotebookLM
- Writing to `blog_post_log.md`
- Publishing to both platforms when `--destination both` — confirm each platform
