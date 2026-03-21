# Blog SEO Guide

On-page SEO checklist for blog posts. Read this before finalizing any blog post for publication.

---

## Table of Contents

1. [Title Tag](#1-title-tag)
2. [Meta Description](#2-meta-description)
3. [URL Slug](#3-url-slug)
4. [Heading Structure](#4-heading-structure)
5. [Keyword Placement](#5-keyword-placement)
6. [Image Optimization](#6-image-optimization)
7. [Internal & External Links](#7-internal--external-links)
8. [Content Quality Signals](#8-content-quality-signals)

---

## 1. Title Tag

- **50-60 characters** — anything longer gets truncated in search results
- Include primary keyword within the first 40 characters when natural
- Make it compelling for humans first, search engines second
- No keyword stuffing ("Best AI Tools | AI Tools Guide | Top AI Tools")

## 2. Meta Description

- **150-160 characters** — the description field in the GHL blog API
- Include the primary keyword once
- Write it as a pitch: what will the reader gain?
- End with a soft CTA: "Learn how", "Discover", "Find out"
- No duplicate descriptions across posts

**Example:**
```
Learn 5 proven strategies to reduce customer churn by 40%. Practical tips you can implement this week without discounting.
```

## 3. URL Slug

- **3-5 words**, lowercase, hyphen-separated
- Include primary keyword
- No stop words unless needed for clarity ("a", "the", "and", "of")
- No dates in slugs (content stays evergreen)
- No special characters or numbers unless essential

**Good:** `reduce-customer-churn-strategies`
**Bad:** `5-ways-to-reduce-your-customer-churn-in-2026-and-beyond`

## 4. Heading Structure

- **H1:** Blog title (GHL handles this automatically)
- **H2:** Main section headings (3-5 per post)
- **H3:** Subsections within H2s
- Never skip levels (H2 → H4 without H3)
- Include keyword variations in 1-2 H2s naturally

## 5. Keyword Placement

Place the primary keyword in these locations (naturally, not forced):

1. Title (H1)
2. First paragraph (within the first 100 words)
3. At least one H2
4. Meta description
5. URL slug
6. Image alt text
7. Conclusion paragraph

Use semantic variations and related terms throughout. Search engines understand context — repeating the exact keyword is less important than covering the topic thoroughly.

## 6. Image Optimization

- **Alt text:** Descriptive, includes keyword when natural. "Customer churn dashboard showing retention metrics" not "image1.png"
- **File names:** Use descriptive names before uploading (GHL stores by URL, but alt text matters)
- **Featured image:** Landscape orientation (16:9 or 3:2), relevant to the topic
- **Size:** Keep images under 500KB for fast loading

## 7. Internal & External Links

- **Internal links:** Link to 2-3 related blog posts or pages on the same site. This helps search engines understand site structure and keeps readers engaged.
- **External links:** Link to 1-2 authoritative sources when citing data or referencing research. Use `rel="noopener noreferrer"` and `target="_blank"`.
- **Anchor text:** Use descriptive text, not "click here" or "read more."

## 8. Content Quality Signals

These factors influence search ranking indirectly through user engagement:

- **Answer the search intent.** If someone searches "how to reduce churn", they want actionable steps, not a history of churn.
- **Comprehensive coverage.** Cover the topic thoroughly enough that the reader doesn't need to search again.
- **Fresh content.** Update posts periodically with new data or examples.
- **Readability.** Short paragraphs, clear language, logical flow.
- **Original insight.** Add perspectives, data, or examples that aren't in every other post on the topic.
