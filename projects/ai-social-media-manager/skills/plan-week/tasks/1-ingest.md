# Task 1 -- Ingest & Understand Input

Read all user-provided input and classify intent.

## Steps

1. For each URL, use `WebFetch` to extract content:
   - Articles / blogs: title, key points, quotes, data.
   - YouTube: title, description, key takeaways.
   - TikTok: caption, context, trend angle.
   - PDFs: main arguments, data points, quotes.
2. For topics without URLs, use `WebSearch` to gather current trends, data points, angles, and recent developments.
3. Classify intent:
   - **Mostly finished captions** -> "schedule these drafts." Polish with brand voice and schedule.
   - **URLs** -> "extract and repurpose." Research the source, create original posts.
   - **Topic / theme** -> "create original content." Research and write from scratch.
   - **Mixed** -> combine approaches to fill a 7-day plan.
4. Read `ghl_post_log.md` to understand what has already been scheduled.
5. Read `locations.json`. If multiple locations exist, ask: "Which client/location is this plan for?" Use that location's accounts from `ghl_accounts_map.json` and pass `--location <shorthand>` to all scripts.
6. Read `ghl_accounts_map.json` to know available platforms for the selected location.

## Accepted Input Types

| Input Type | Examples | How to Process |
|------------|----------|----------------|
| Topic / theme | "AI tools for PMs", "burnout recovery" | WebSearch to research. Generate original posts. |
| Draft posts | Pasted text, partial captions | Polish using brand voice. Adapt per platform. |
| URLs (article / blog) | Medium links, Substack, news sites | WebFetch the URL. Extract key points. Create posts from content. |
| URLs (YouTube) | YouTube links | WebFetch the URL. Extract title, description, key takeaways. |
| URLs (TikTok) | TikTok links | WebFetch the URL. Extract caption, context. |
| URLs (PDF) | PDF links, local PDF paths | WebFetch or Read tool. Extract key content. |
| Image / photo URLs | Direct image links | Use as visual assets. Assign to appropriate days. |
| Mixed | "Plan around this article [URL] and also do 2 posts about AI tools" | Combine all approaches. |

## Output

A structured understanding of:
- What content sources are available
- What the user wants (schedule drafts, repurpose, create original, or mixed)
- Which location and platforms to target
- What has already been scheduled (from post log)

Proceed to Task 2 when input is fully understood.
