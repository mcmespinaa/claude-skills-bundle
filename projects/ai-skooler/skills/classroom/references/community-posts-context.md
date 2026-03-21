# Community Posts CONTEXT.md Template

Create this file at `<Community>/Community Posts/CONTEXT.md` for every new community.

## Template

```markdown
# Community Posts

Member-shared implementations, workflows, and case studies from the <Community Name> community feed. These are not classroom content — they're real-world applications of the methodology.

## What Belongs Here

- Show Your Work posts with actual builds or workflows
- Use case analyses and pattern extraction
- High-value discussion threads with actionable insights

## What Doesn't Belong Here

- Intro posts, milestone celebrations, general chat
- Lesson check-in polls (those reference the lessons directly)
- Duplicate or low-signal content

## File Format

## \`\`\`yaml

type: community-post
community: "<Community Name>"
author: "Author Name"
source: "full-url"
date_scraped: "YYYY-MM-DD" # for analysis files

---

\`\`\`

## Process

1. Scrape the post content and comments
2. Expand all "See more" and "View more replies" before extraction
3. Structure comments as blockquotes with author attribution
4. Extract actionable ideas into a separate section
5. Add wiki-links to related lessons
6. Update Course Index.md with new entry under Community Posts
```
