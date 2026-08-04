---
name: classroom
description: >-
  Scrape all courses and lessons from a Skool community classroom into the
  Obsidian vault. Use when user says /classroom followed by a Skool community
  URL, or asks to scrape a classroom, courses, or lessons from Skool.
---

# Classroom Scraper

Scrapes all courses and lessons from a Skool community's classroom and creates an organized Obsidian vault structure with proper frontmatter, wiki-links, and a Course Index.

## Prerequisites

- Playwright MCP must be available
- Chrome must be fully quit before Playwright can launch
- Authenticated Skool session (cookies persist in Playwright user-data-dir)
- Direct HTTP requests (curl, WebFetch) get 403 — Skool requires login

## Input

The user provides a Skool community URL. Extract the slug from it:

- `https://www.skool.com/<slug>` → use `<slug>`
- `https://www.skool.com/<slug>/classroom` → use `<slug>`

## Instructions

### Step 1: Kill Chrome and navigate to the classroom

Chrome must be fully quit before Playwright launches. Run `pkill -f "Google Chrome"` if needed (confirm with user first).

Navigate to `https://www.skool.com/<slug>/classroom` using Playwright.

### Step 2: Discover courses and modules

Take a snapshot of the classroom page. The sidebar shows all courses and their modules. Extract:

- Course names
- Module names within each course
- Lesson titles and their URLs within each module

The classroom URL pattern is: `https://www.skool.com/<slug>/classroom/<course-id>?md=<lesson-id>`

Use `browser_run_code` to extract the full course structure from the sidebar navigation. Save to `/tmp/skool_classroom_structure.json`.

### Step 3: Create vault folder structure

Before scraping content, create the folder structure in the Obsidian vault:

```
Obsidian/ai-skooler/<Community Name>/
├── CONTEXT.md
├── Course Index.md
├── <Course Name>/
│   └── <Module Name>/
│       └── <Lesson Title>.md
└── Community Posts/
    └── CONTEXT.md
```

Determine the community name from the Skool page (the community display name, not the slug).

If a community folder already exists, do NOT overwrite existing files — only add new ones.

### Step 4: Scrape each lesson

For each lesson URL discovered in Step 2:

1. Navigate to the lesson URL
2. Wait for content to load (`.tiptap.ProseMirror` selector)
3. Extract content using `browser_run_code` with a recursive DOM-to-markdown converter

The content extractor must handle:

- H1-H6 headings
- Bold, italic, code (inline)
- Links (convert to wiki-links where they reference other lessons)
- Blockquotes
- Ordered and unordered lists
- Code blocks (preserve language)
- Horizontal rules
- Images: SKIP (Skool hosts externally, URLs break)

See [references/dom-extractor.md](references/dom-extractor.md) for the full extraction script.

### Step 5: Create lesson files

Each lesson file gets YAML frontmatter:

```yaml
---
module: "Module N: Module Name"
course: "Course Name"
source: "full-lesson-url"
---
```

File naming: `<number> <Lesson Title>.md` — match the classroom ordering exactly.

### Step 6: Create Course Index.md

Generate a `Course Index.md` with:

- YAML frontmatter (source, community, platform)
- Each course as an H2 section
- Each module as an H3 section
- Each lesson as a wiki-link: `- [[<Lesson Title>]]`

See [references/course-index-template.md](references/course-index-template.md) for format.

### Step 7: Create CONTEXT.md files

Create a community-level CONTEXT.md:

```markdown
# <Community Name>

<brief description from the community page>

## Community Details

- **Slug:** <slug>
- **URL:** https://www.skool.com/<slug>

## Courses

| Course | Status   | Lessons                        |
| ------ | -------- | ------------------------------ |
| <name> | Complete | <N> lessons across <M> modules |

## What's Here

- `/<Course>/` — description
- `/Community Posts/` — member implementations
```

Create a `Community Posts/CONTEXT.md` using the template from [references/community-posts-context.md](references/community-posts-context.md).

### Step 8: Update CLAUDE.md

Append the new community to the Communities table in `ai-skooler/CLAUDE.md`:

```markdown
| <Community Name> | <slug> | <status description> |
```

### Step 9: Report results

Report to the user:

- How many courses, modules, and lessons were scraped
- Any lessons that failed (with URLs for retry)
- The vault path where files were created

## Error Handling

### Playwright won't launch

Chrome is running. Ask user to confirm, then `pkill -f "Google Chrome"`.

### Lesson page shows no content

Wait longer — some lessons load slowly. Retry with `waitForSelector('.tiptap.ProseMirror', { timeout: 10000 })`.

### Token limits exceeded

Save lesson content to `/tmp/skool_lesson_<n>.md` via `browser_run_code`, then read the file.

### Locked/premium content

Some lessons may be behind a paywall. Log these as "Locked" in the Course Index and create a stub file noting the lesson exists but content is unavailable.

## Batch Processing Tips

- Use `browser_run_code` for extraction — it's faster than snapshot-based extraction
- Process one course at a time to avoid losing progress
- Save progress to `/tmp/` between courses
- Results from `browser_run_code` may need double `JSON.parse`
