---
name: seo-aio
description: "SEO, AIO, and GEO optimization for the Sweden Ecosystem Directory. Activates on: schema markup, meta tags, sitemap, robots.txt, programmatic SEO, keyword strategy, AI citation optimization, search ranking, structured data, traffic strategy — even without the word 'SEO'."
---

# SEO/AIO Agent — Sweden Ecosystem Directory

Optimize every page for three surfaces: Google organic, Google AI Overviews, and generative AI citation (ChatGPT, Perplexity, Claude). This skill contains the project-specific architecture, code patterns, and decision logic. General SEO knowledge is assumed.

---

## Architecture — What Exists

All SEO infrastructure is built and compiled. Tracking is dormant until env vars are set (DEC-010).

| File | Purpose |
|------|---------|
| `lib/schema.ts` | JSON-LD `@graph` builder — WebPage + Organization + BreadcrumbList + FAQPage per listing |
| `lib/seo.ts` | Next.js `Metadata` builder — title, description, OG, Twitter, geo, robots, Google Ads labels |
| `lib/pixels.ts` | Meta Conversions API (server-side) — dual-send to org pixel + master pixel |
| `lib/use-meta-tracking.ts` | Client hook — fires PageView/ViewContent on mount, returns `trackLead()` |
| `app/api/meta-event/route.ts` | Server endpoint — receives client events, looks up org's `meta_pixel_id`, sends to CAPI |
| `app/robots.ts` | Allows all AI crawlers (GPTBot, PerplexityBot, Claude-Web, etc.) |
| `app/sitemap.ts` | Dynamic from Supabase — homepage, map, all listings, category filter URLs |
| `app/layout.tsx` | GA4 + GTM injection (gated behind env vars), site-wide WebSite schema |

---

## Decision Logic — Category → Schema Type

When building or modifying schema, use this mapping from `lib/schema.ts`:

```
ecovillage    → ["Organization", "Place"]
coliving      → "LodgingBusiness"
permaculture  → "Farm"
ecological    → "NGO"
transition    → "NGO"
rewilding     → "NGO"
funding       → "GovernmentOrganization"
research      → "ResearchOrganization"
social_ent    → "Organization"
cooperative   → "Organization"
network       → "Organization"
circular      → "Organization"
```

Always use the most specific type. If adding a new category, find the closest Schema.org type — never default to plain `Organization` when a subtype exists.

---

## Schema Pattern — Listing Page `@graph`

Every listing page gets a single JSON-LD `@graph` combining four schemas:

1. **WebPage** — `@id` is the page URL, links to `#organization` and `#website`
2. **Organization** (category-specific type) — `@id` is `{pageUrl}#organization`, includes geo, address, founding date, keywords
3. **BreadcrumbList** — Home → Category → Listing (3 levels)
4. **FAQPage** — 5 auto-generated Q&As from initiative data fields:
   - "What is {name}?" — uses `long_description` approach section when available
   - "Where is {name} located?" — includes lat/lng
   - "When was {name} founded?" — conditional on `founded` field
   - "What does {name} focus on?" — from `focus_areas` array
   - "How can I visit {name}?" — conditional on `website` field

**Why FAQPage matters:** 3.2x more likely to appear in AI Overviews. Question queries trigger AI Overviews 57.9% of the time.

Use `buildListingPageSchema(initiative)` — never construct schema manually.

---

## Meta Tags — Constraints

`buildInitiativeMetadata(initiative)` handles all metadata. Key constraints:

- **Title:** `{name} — {category} in {location} | Sweden Ecosystem Directory` — keep under 60 chars
- **Description:** truncated to 155 chars with `...` — Google cuts at 160
- **OG description:** truncated to 200 chars — social platforms allow more
- **Keywords:** `[name, category, location, region, "Sweden", "sustainability", ...focus_areas]`
- **Geo meta:** `geo.region`, `geo.position`, `ICBM` from initiative lat/lng
- **Google Ads labels:** `google-ads-category`, `google-ads-region`, `google-ads-location` in `other`
- **Canonical:** always set to prevent duplicate content

When creating new page types (category hubs, region pages), follow the same pattern: title under 60, description under 155, canonical set, OG populated.

---

## Per-Organization Tracking — Meta CAPI

Architecture: 1 organization = 1 ad account. Each org stores `meta_pixel_id` in Supabase.

**Flow:**
1. Client hook (`useMetaTracking`) fires `fetch("/api/meta-event")` with `{ slug, event, url, fbc, fbp }`
2. API route looks up initiative by slug → gets `meta_pixel_id`
3. `sendEventToOrgAndDefault()` sends to BOTH org's pixel AND master pixel via `Promise.allSettled`
4. Three events: `PageView` (on load), `ViewContent` (on load), `Lead` (on "Visit Website" click)

**Env vars (dormant):**
- `META_CAPI_ACCESS_TOKEN` — system user token
- `NEXT_PUBLIC_META_PIXEL_DEFAULT` — fallback/master pixel

When adding new trackable actions, use `buildEvent()` from `lib/pixels.ts` — it standardizes `custom_data` with initiative name, category, type, and ID.

---

## Programmatic SEO — Page Matrix

Current: L listing pages. Planned expansion:

| Page Type | Route | When to Build |
|-----------|-------|---------------|
| Listing | `/initiative/[slug]` | ✅ Built |
| Category hub | `/[category]` | When L > 50 per category |
| Region hub | `/regions/[region]` | When 3+ listings per region |
| Category × Region | `/[category]/[region]` | Only if combo has ≥ 3 listings — redirect thin pages to parent |
| Pillar guide | `/guides/[topic]` | Content engine phase (Month 2-4) |

**Thin page rule:** If a programmatic page would have < 3 listings or < 300 words unique content, do not create it. Redirect to parent.

**Internal linking:** Every listing links to its category and region. Every hub links to its listings. Cross-link related initiatives by category or geography.

---

## AIO/GEO Content Rules

These are the project-specific content rules that make pages citable:

1. **First 100 words** answer "What is {org name}?" — Google AI Overview extracts from here
2. **Lists over paragraphs** — 78% of AI Overview responses use list format
3. **Self-contained FAQ answers** — each answer must be extractable independently, no pronouns referring to other answers
4. **Statistics every 150-200 words** — founding year, member count, hectares, focus area count
5. **Bilingual keywords** — Swedish primary (`ekobyar Sverige`), English secondary (`ecovillages Sweden`). English-only misses 70%+ of local search volume

---

## When to Use This Skill

- **New page type:** Build `generateMetadata()` using `lib/seo.ts` patterns, add schema via `lib/schema.ts` patterns, add to `sitemap.ts`
- **New category added:** Update `SCHEMA_TYPE_MAP` in `lib/schema.ts`, update `CATEGORIES` in `types/database.ts`
- **Content optimization:** Restructure for AI extraction — answer-first, lists, self-contained sections
- **New tracking event:** Add builder in `lib/pixels.ts`, handle in `api/meta-event/route.ts`
- **Going live:** Activate env vars per playbooks — see `~/Obsidian/SocialAgent/playbooks/`

---

## References

Read `references/keyword-research.md` for the bilingual keyword database (4 tiers).
Read `references/schema-templates.md` for copy-paste JSON-LD patterns.
Read `references/content-calendar.md` for the 12-month publishing roadmap.
