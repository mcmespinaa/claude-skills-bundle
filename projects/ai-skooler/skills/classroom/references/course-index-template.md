# Course Index Template

Use this template when generating the Course Index.md for a scraped community.

## Template

```markdown
---
source: "https://www.skool.com/<slug>/classroom"
community: "<Community Name>"
platform: "Skool"
---

# <Community Name> - Classroom Index

## <Course Name 1>

<Course description from the classroom page, if available>

### <Module Name>

- [[<Lesson 1 Title>]]
- [[<Lesson 2 Title>]]

### <Module Name>

- [[<Lesson 3 Title>]]

---

## <Course Name 2>

### <Module Name>

- [[<Lesson Title>]]

---

## Community Posts

Member implementations, workflows, and case studies shared in the community feed.

---
```

## Rules

- Course names are H2 (`##`)
- Module names are H3 (`###`)
- Lessons are wiki-linked list items
- Courses are separated by `---`
- Community Posts section always exists (even if empty initially)
- Description text comes from the classroom page intro text if available
- Lesson titles must match filenames exactly (minus the .md extension)
