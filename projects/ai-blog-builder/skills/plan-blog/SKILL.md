# /plan-blog — Batch Blog Content Planning

> **Trigger:** User says `/plan-blog`, "plan a month of blog posts", "create a blog content calendar", or similar.

## Role

You are a content strategist. You plan a series of blog posts, write full drafts, get user approval, then batch-publish all posts to GHL.

---

## Before You Start

Read these files every time:
1. `/blog` SKILL.md — Writing rules, tone, blog workflow
2. `blog-voice.md` — Voice guide, SEO rules, article structures
3. `locations.json` — Available client locations

## Multi-Location Support

Same as `/blog` skill:
1. Check locations.json for available locations
2. Single location: use automatically
3. Multiple locations: ask user which one
4. Pass `--location` to all scripts

---

## Accepts

- Topic list (e.g., "5 posts about AI for small businesses")
- URLs to repurpose (YouTube, TikTok, articles, PDFs)
- Content brief or editorial calendar
- Social media posts to expand into articles
- Mix of any of the above

---

## Workflow (7 Steps)

### Step 1: Understand Input

Parse what the user provides:
- How many posts? (default: 4 for a month, 1 per week)
- What topics or sources?
- Any scheduling preferences? (weekly, biweekly)
- Target audience or pillar focus?

If the user gives broad direction ("plan blog content for this month"), use WebSearch to identify 4 trending angles within their content pillars.

### Step 2: Discover Blog Setup

Fetch the blog ID, authors, and categories:

```bash
bash .claude/skills/blog/scripts/ghl_get_blogs.sh [--location "LOCATION_KEY"]
bash .claude/skills/blog/scripts/ghl_get_authors.sh [--location "LOCATION_KEY"]
bash .claude/skills/blog/scripts/ghl_get_categories.sh [--location "LOCATION_KEY"]
```

### Step 3: Build Content Calendar

Create a calendar with one post per slot:

For each post, plan:
- **Date** — Publishing date
- **Title** — Working title (under 80 chars)
- **Type** — How-to, listicle, thought piece, case study, or repurpose
- **Pillar** — AI, Leadership, Sustainability, or Consciousness
- **Slug** — URL-friendly version
- **Key angle** — One-sentence summary of the unique perspective
- **Source** — What input it's based on (URL, topic, social post, etc.)

### Step 4: Write Full Drafts

For each post in the calendar, write:
- Title + meta title + meta description
- Full HTML body content
- URL slug
- Tags (3-5)
- Featured image description (for Gemini generation or stock selection)

Follow ALL writing rules from `/blog` SKILL.md and `blog-voice.md`.

Save each draft to `blog-drafts/[slug].html`

### Step 5: Write blog-plan.md

Output the full plan to `blog-plan.md`:

```markdown
# Blog Content Plan

Generated: YYYY-MM-DD
Location: [LOCATION_KEY]
Blog ID: [BLOG_ID]
Posts: [N]

## Post 1: [Title]
- **Date:** YYYY-MM-DD
- **Type:** How-to
- **Pillar:** AI
- **Slug:** ai-tools-small-business
- **Meta title:** [under 70 chars]
- **Meta description:** [140-160 chars]
- **Tags:** tag1, tag2, tag3
- **Status:** Ready
- **Draft:** blog-drafts/ai-tools-small-business.html

## Post 2: [Title]
...
```

### Step 6: User Review

Present the plan summary to the user:
- List all posts with titles, dates, and types
- Ask for approval: "Ready to publish these [N] posts? (All will be created as DRAFT unless you say otherwise)"
- Wait for explicit confirmation
- Accept modifications ("change post 3 title", "swap posts 2 and 4", "remove post 5")

### Step 7: Batch Publish

After approval, create all posts sequentially (to avoid rate limits):

For each post:

1. **Validate slug:**
```bash
bash .claude/skills/blog/scripts/ghl_check_slug.sh \
  --blog-id "BLOG_ID" --slug "post-slug" --location "LOCATION_KEY"
```

2. **Upload featured image** (if generated/provided):
```bash
bash .claude/skills/blog/scripts/ghl_upload_media.sh \
  --file "path/to/image.png" --name "blog-hero-slug"
```

3. **Create post:**
```bash
bash .claude/skills/blog/scripts/ghl_create_blog_post.sh \
  --blog-id "BLOG_ID" \
  --title "Post Title" \
  --content-file "blog-drafts/slug.html" \
  --status "DRAFT" \
  --slug "post-slug" \
  --meta-title "SEO Title" \
  --meta-description "Meta description" \
  --tags "tag1,tag2,tag3" \
  --location "LOCATION_KEY"
```

4. **Log result** — Append to `ghl_blog_log.md`

5. **Error isolation** — If one post fails, log the error, continue with the next post. Report all failures at the end.

**Pacing:** Wait 2 seconds between API calls to stay within rate limits.

---

## Error Handling

- **No blog found:** Tell user to create a blog in GHL website builder first
- **Slug collision:** Auto-append `-2`, `-3`, etc. and re-validate
- **API failure on one post:** Log it, continue with remaining posts, report at end
- **Rate limit (429):** Wait 10s, retry once, then skip and report
- **Hook blocks a post:** Fix the flagged issues for that post, retry it after the batch

---

## Output

After batch publish, show summary:

```
Blog Content Plan — Published
Location: ces
Blog: [BLOG_ID]

1. "Post Title" — DRAFT — post-id-123 — /slug
2. "Post Title" — DRAFT — post-id-456 — /slug
3. "Post Title" — FAILED — [error reason]
4. "Post Title" — DRAFT — post-id-789 — /slug

3/4 posts created successfully.
1 failed — see error above.

All posts created as DRAFT. Review and publish them in GHL when ready.
```
