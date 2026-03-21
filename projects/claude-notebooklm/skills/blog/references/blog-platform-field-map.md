# Blog Platform Field Mapping — GHL vs ShopWired

## Create Blog Post

| Blog Skill Concept | GHL Field | ShopWired Field | Notes |
|---|---|---|---|
| Title | `title` | `title` | Same |
| URL slug | `urlSlug` | `slug` | Different field name |
| Body content | `rawHTML` (HTML string) | `content` (HTML string) | Same format, different field |
| Meta description | `description` | `metaDescription` | Different field name |
| SEO title | Part of `title` | `metaTitle` | ShopWired has dedicated SEO title |
| SEO keywords | Not supported | `metaKeywords` | ShopWired only |
| Featured image | `imageUrl` (URL) | `image` (URL or base64) | ShopWired also accepts base64 |
| Image alt text | `imageAltText` | Not in create API | GHL only |
| Excerpt | Not native | `excerpt` | ShopWired only |
| Categories | `categories` (array of IDs) | `categoryId` (single integer) | GHL=multi, SW=single |
| Category by name | Not supported | `categoryTitle` (string) | ShopWired can auto-match |
| Tags | `tags` (array of strings) | `tags` (comma-separated string) | Different format |
| Author | `author` (author ID) | Auto-set by store | GHL requires explicit |
| Status / Draft | `status`: `"DRAFT"` | `active`: `false` | Different mechanisms |
| Status / Published | `status`: `"PUBLISHED"` | `active`: `true` | Different mechanisms |
| Status / Scheduled | `status`: `"SCHEDULED"` + `publishedAt` | `active`: `false` + `releaseDate` | Both need date |
| Blog site ID | `blogId` (required) | Not needed | ShopWired = single blog |
| Location ID | `locationId` (required) | Not needed | GHL multi-tenant |
| Canonical URL | `canonicalLink` | `customUrl` | Optional on both |
| Publish date | `publishedAt` (ISO datetime) | `releaseDate` (string) | Format may differ |

## Update Blog Post

| Operation | GHL | ShopWired |
|---|---|---|
| Endpoint | `PUT /blogs/posts/{postId}` | `PUT /blog-posts/{id}` |
| ID format | Alphanumeric string | Integer |
| Partial update | Full payload required | Only changed fields needed |
| Fetch existing | Not available via API | `GET /blog-posts/{id}?embed=content` |

## Fetch Metadata

| Data | GHL | ShopWired |
|---|---|---|
| Blog sites | `GET /blogs/site/all` | Not needed (single blog) |
| Categories | `GET /blogs/categories?locationId=...` | `GET /blog-categories` |
| Authors | `GET /blogs/authors?locationId=...` | Not available |
| Tags | Inline in create payload | `GET /blog-tags` |
| Posts list | `GET /blogs/posts/all?locationId=...` | `GET /blog-posts` |
| Slug check | `GET /blogs/posts/url-slug-exists?...` | Check via `GET /blog-posts` list |
| Post count | Not available | `GET /blog-posts/count` |

## Category Sync (for --destination both)

When publishing to both platforms, categories may not match by ID. Strategy:
1. Fetch categories from both GHL and ShopWired.
2. Match by `title`/`name` (case-insensitive).
3. If match found: use each platform's category ID.
4. If no match: create category in the missing platform, or ask user.

## Script Reference

| Script | Platform | Purpose |
|---|---|---|
| `ghl_create_blog_post.sh` | GHL | Create post |
| `ghl_update_blog_post.sh` | GHL | Update post |
| `ghl_get_blogs.sh` | GHL | Fetch sites/categories/authors/slug check |
| `sw_create_blog_post.sh` | ShopWired | Create post |
| `sw_update_blog_post.sh` | ShopWired | Update post |
| `sw_get_blog_meta.sh` | ShopWired | Fetch categories/tags/posts/count |
| `md_to_blog_html.py` | Both | Convert markdown to semantic HTML |
