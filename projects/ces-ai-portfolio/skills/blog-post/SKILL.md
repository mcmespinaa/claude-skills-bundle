---
name: blog-post
description: >-
  Create a new blog post for the portfolio site. Use when user says /blog-post,
  write a blog post, create a new post, or wants to publish an article.
allowed-tools: "Read Write Edit Grep Glob Bash"
---

# /blog-post — Blog Post Creation Skill

## Steps

1. **Gather requirements**
   - Topic and key points from the user
   - Target audience (technical, general, hiring managers)
   - Check existing posts for voice consistency

2. **Research** (if needed)
   - Check `Ces Portfolio/research/` for existing findings
   - Review relevant code in `src/` for technical posts

3. **Draft the post**
   - Write in the portfolio's established voice
   - Include code examples for technical posts
   - Structure: hook → context → meat → takeaway
   - Add metadata: title, slug, description, tags, status

4. **Create the database entry**
   - Insert via Supabase client or provide the SQL
   - Set status to `draft` initially

5. **Verify**
   - Check the post renders correctly on the blog page
   - Verify SEO metadata and JSON-LD schema

## Writing rules
- Clear, simple language. Short sentences.
- Active voice. No buzzwords.
- Show specific results and examples.
- Every post needs a clear takeaway.
- AVOID: em dashes, delve, embark, realm, tapestry, groundbreaking, game-changer
