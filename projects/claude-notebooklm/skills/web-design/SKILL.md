---
name: web-design
description: >-
  Design high-converting web pages: sales pages, landing pages, ecommerce
  product pages, SaaS pages, and funnels. Generates complete page specs with
  section-by-section layout, copy, and visual design using proven conversion
  frameworks (PAS, AIDA, StoryBrand, Hook-Story-Offer). Use when user says
  'design a sales page', 'landing page for...', 'product page layout', 'funnel
  for...', 'web page spec', or invokes /web-design. Outputs structured page
  blueprints ready for development. Do NOT use for building/coding pages -- this
  skill produces design specs and copy, not code.
argument-hint: '"product or offer" [SalesPage|Landing|ProductPage|SaaS|Funnel] [--location ces|...]'
disable-model-invocation: true
---

# /web-design -- High-Converting Page Designer

> **Trigger:** User says `/web-design`, "design a sales page", "landing page for...", "product page layout", "funnel for...", "web page spec", or similar.

## Role

You are a Nordic-minimalist web designer and conversion copywriter. You design high-converting pages by combining Scandinavian design principles (generous white space, clean typography, warm neutrals) with proven conversion frameworks (PAS, AIDA, StoryBrand, Hook-Story-Offer). You produce complete page specifications: section-by-section layouts, copy, visual design tokens, and mobile behavior -- ready for a developer to build.

---

## Constants

```
WEB_DESIGN_SCRIPTS_DIR: ${CLAUDE_PLUGIN_ROOT}/skills/web-design/scripts
WEB_DESIGN_REFS_DIR:    ${CLAUDE_PLUGIN_ROOT}/skills/web-design/references
BRAND_DOCS_DIR:         Resolved in Step 0 -- $PWD/brands/<LOCATION>/ if it exists,
                        else ${CLAUDE_PLUGIN_ROOT}/skills/distribute/references (fallback)
BRAND_VOICE_PATH:       <BRAND_DOCS_DIR>/brand-voice.md
BRAND_WEB_DESIGN_PATH:  <BRAND_DOCS_DIR>/brand-web-design.md
BRAND_COLORS_PATH:      <BRAND_DOCS_DIR>/brand-colors.md
BRAND_TYPOGRAPHY_PATH:  <BRAND_DOCS_DIR>/brand-typography.md
```

---

## Page Types

| Type | When to Use | Sections | Output |
|------|------------|----------|--------|
| **Sales Page** | Info-products, courses, coaching, digital offers | 10-section long-form | Full spec + copy |
| **Landing Page** | Lead magnets, webinar signups, single-offer pages | 5-7 sections | Focused spec + copy |
| **Product Page** | Physical products, B2B/B2C ecommerce | Product hero + specs + reviews | Product spec + copy |
| **SaaS Landing** | Software, apps, tools | Story-driven hero + features + pricing | SaaS spec + copy |
| **Funnel** | Multi-page sequences (lead magnet → tripwire → core → upsell) | Multiple page specs | Full funnel architecture + per-page specs |

If the user doesn't specify a type, infer from context:
- Digital product, course, coaching → **Sales Page**
- "Get my free [thing]", email capture → **Landing Page**
- Physical product, ecommerce store → **Product Page**
- Software, app, tool → **SaaS Landing**
- "Build a funnel", multi-step → **Funnel**

---

## Workflow

### Step 0: Resolve Location & Brand

1. If `--location <shorthand>` is provided, use that location.
2. If no flag, read `locations.json` in `$PWD`:
   - **Single location:** Use it automatically.
   - **Multiple locations:** Ask the user which brand/location.
3. Resolve brand directory: `$PWD/brands/<location>/` if it exists, else fall back to `${CLAUDE_PLUGIN_ROOT}/skills/distribute/references`.

### Step 1: Read Brand Design System

**Read these files before designing anything:**

1. `BRAND_WEB_DESIGN_PATH` -- page blueprints, design tokens, conversion frameworks, layout specs
2. `BRAND_VOICE_PATH` -- tone, banned words, writing rules
3. `BRAND_COLORS_PATH` -- color palette and accessibility rules
4. `BRAND_TYPOGRAPHY_PATH` -- font stack, sizes, weights

If `brand-web-design.md` does not exist for this location, use the generic template at `${CLAUDE_PLUGIN_ROOT}/config/brands/_example/brand-web-design.md` and ask the user for brand-specific values (colors, fonts, feel).

### Step 2: Gather Input

Collect from the user:

| Input | How to process |
|-------|---------------|
| **Product/offer** | What they're selling or promoting |
| **Target audience** | Who the page is for (demographics, pain points, awareness level) |
| **Page type** | Sales Page, Landing, Product Page, SaaS, Funnel (or auto-detect) |
| **Traffic temperature** | Cold (ads/SEO), warm (email list), hot (existing customers) |
| **Key differentiator** | What makes this offer unique |
| **Social proof** | Testimonials, stats, logos available |
| **Price point(s)** | Single price or tiered |
| **Primary CTA** | What action should visitors take |

If the user provides only a product/topic, ask:
1. Who is the target audience?
2. Where is the traffic coming from? (determines page length)
3. What's the primary action you want visitors to take?

### Step 3: Select Copywriting Framework

Based on the page type and traffic temperature, select the primary framework:

| Context | Framework | Why |
|---------|-----------|-----|
| Cold traffic, complex offer | PAS (Problem → Agitate → Solution) | Must name the pain before presenting the fix |
| Warm traffic, emotional product | AIDA (Attention → Interest → Desire → Action) | Audience already aware; build desire |
| Brand/about page, storytelling | StoryBrand 7-Part | Customer as hero, brand as guide |
| Funnel pages, webinars | Hook-Story-Offer | Pattern interrupt → connection → irresistible deal |
| Product descriptions, features | FAB (Feature → Advantage → Benefit) | Translate specs into value |
| High-ticket, persuasion-heavy | 4Ps (Promise → Picture → Proof → Push) | Build conviction before asking for commitment |

Present the recommended framework to the user with a one-line explanation. Get confirmation.

### Step 4: Design Page Structure

Using the blueprint from `brand-web-design.md` for the selected page type, build the section-by-section spec.

**For each section, define:**

| Element | What to specify |
|---------|----------------|
| **Section name** | e.g., "Hero", "Problem", "Social Proof" |
| **Purpose** | What this section achieves in the conversion flow |
| **Layout** | Desktop layout (columns, alignment) and mobile behavior |
| **Background** | Hex color or gradient from brand palette |
| **Headline** | Actual copy. Font, size, weight, color from brand tokens. |
| **Body copy** | Actual copy. Font, size, color from brand tokens. |
| **Visual** | What visual element goes here (illustration, product photo, gradient shape, icon grid) |
| **CTA** | Button text, style (primary/secondary/ghost), placement |
| **Spacing** | Vertical padding (desktop/mobile) using brand spacing scale |

**Quality checks on the structure:**
- Does the hero answer "What do I get?" and "Is this for me?" in <5 seconds?
- Is there only one primary CTA repeated (not competing goals)?
- Is social proof placed near CTAs?
- Does the section order follow the selected copywriting framework?
- Is every section optimized for mobile (stacked layout, thumb-zone CTAs)?

Present the structure as a numbered table. Get approval before writing copy.

### Step 5: Write Section Copy

For each approved section, write the actual copy:

**Rules:**
- Read and follow `brand-voice.md` strictly (tone, banned words, style)
- Headlines: specific outcomes, not clever wordplay. Max 8 words for hero.
- Body: "you"-focused, not "we/our". Every feature includes a benefit.
- CTAs: action verb + specific benefit ("Start Free Trial", "Get the Guide")
- Social proof: specific results, names, photos -- never vague praise
- No em dashes (use commas, periods, or ellipsis per brand rules)

**Copy deliverables per section:**
- Eyebrow text (if applicable)
- Headline
- Subheadline
- Body paragraphs
- Bullet points / feature lists
- CTA button text
- Supporting micro-copy (guarantees, reassurance)

### Step 6: Specify Visual Design

For each section, map the brand design tokens:

| Token | Source |
|-------|--------|
| Background color | `brand-colors.md` backgrounds |
| Text colors | `brand-colors.md` text scale |
| Headline font/size/weight | `brand-typography.md` web scale |
| Body font/size | `brand-typography.md` web scale |
| CTA button style | `brand-web-design.md` CTA tokens |
| Card style | `brand-web-design.md` card tokens |
| Spacing | `brand-illustrations.md` spacing system or `brand-web-design.md` layout specs |
| Icons/illustrations | `brand-illustrations.md` style rules |

**Also specify:**
- Navigation bar (sticky, with CTA button visible)
- Mobile breakpoints and behavior
- Sticky mobile CTA bar (appears after scrolling past hero)
- Image/illustration recommendations with Unsplash search terms

### Step 7: Preview & Approval

Present the complete page spec in a structured format:

```
## Page Spec: [Page Title]

**Type:** [Sales Page | Landing | Product Page | SaaS | Funnel]
**Framework:** [PAS | AIDA | StoryBrand | ...]
**Traffic:** [Cold | Warm | Hot]
**Audience:** [description]
**Primary CTA:** [action]

---

### Section 1: Hero
**Layout:** [description]
**Background:** [hex]

**Eyebrow:** [text]
**Headline:** [text]
**Subheadline:** [text]
**CTA:** [button text] — [Primary/Secondary style]
**Visual:** [description]
**Mobile:** [behavior]

---

### Section 2: Problem
...
```

Ask the user to approve, request changes, or regenerate specific sections.

### Step 8: Export Options

After approval, offer these outputs:

| Format | Description |
|--------|-------------|
| **Markdown spec** | Full page spec saved to a `.md` file (default) |
| **Obsidian note** | Save to vault via `/vault-save` with `type: web-design-spec` |
| **Figma handoff** | Copy-paste ready content organized by frames (if Figma MCP available) |
| **HTML prototype** | Basic semantic HTML with inline styles matching brand tokens (on request only) |

**Save the spec:**
```
Output: /tmp/web-design-spec-[slug].md
```

Optional: Save to Obsidian vault:
```
/vault-save --type web-design-spec --title "[Page Title]"
```

---

## Funnel Mode

When the page type is **Funnel**, design a multi-page sequence:

### Funnel Types

| Funnel | Pages | Use Case |
|--------|-------|----------|
| Lead Magnet | Opt-in → Thank You | Email list building |
| Tripwire | Opt-in → Tripwire Offer → Thank You | Low-ticket first purchase |
| Webinar | Registration → Confirmation → Replay → Sales Page | Course/program launch |
| Product Launch | Pre-launch → Cart Open → Cart Close | Seasonal/timed launches |
| Application | Sales Page → Application Form → Booking | High-ticket services |

### Funnel Workflow

1. User specifies the offer and funnel type (or auto-detect from offer price/complexity).
2. Apply the Value Ladder framework (Russell Brunson):
   - What's the free lead magnet?
   - What's the tripwire ($7-47)?
   - What's the core offer ($97-497)?
   - What's the high-ticket upsell ($1,000+)?
3. Design each page in the funnel using the section blueprints from `brand-web-design.md`.
4. Specify the email triggers between pages (hand off to `/newsletter` for email content).
5. Present the complete funnel map + individual page specs.

### Funnel Map Format

```
## Funnel: [Name]

### Traffic Sources
- [Ad platform / SEO / Social / Email]

### Page Flow
1. [Opt-in Page] → Headline + 3 bullets + Email capture
   ↓ (triggers: Welcome email + Lead magnet delivery)
2. [Tripwire Page] → Low-cost offer + Order bump
   ↓ (triggers: Purchase confirmation + Upsell email sequence)
3. [Core Offer Page] → Full sales page (10-section blueprint)
   ↓ (triggers: Onboarding sequence)
4. [Thank You / Onboarding]

### Email Sequence
- Email 1 (immediate): Lead magnet delivery
- Email 2 (Day 1): Story + value
- Email 3 (Day 3): Case study
- Email 4 (Day 5): Tripwire offer
- Email 5 (Day 7): Urgency + final CTA
```

---

## Content Pillar Integration

If the brand uses content pillars (e.g., Ces: AI+Product, Leadership, Sustainability, Consciousness), select the appropriate pillar for accent colors and gradient treatments:

| Pillar match | Effect |
|-------------|--------|
| Topic matches a pillar | Use that pillar's accent color for CTAs, tags, hero gradient wash |
| Topic spans multiple pillars | Use Gold (primary accent) as default |
| Topic doesn't match any pillar | Use Gold (primary accent) as default |

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| No `brand-web-design.md` | Brand not set up for web | Use `_example` template, ask user for brand values |
| No `brand-voice.md` | Brand not configured | Ask user for tone and style preferences |
| User provides no audience info | Can't write effective copy | Ask: "Who is this page for?" |
| User wants code output | Skill produces specs, not code | Clarify: "This skill produces design specs. Would you like me to also generate HTML/CSS from the spec?" |
| Funnel too complex | 5+ pages | Break into phases, design 2-3 pages per session |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading `locations.json`
- Reading all brand reference files (voice, colors, typography, web-design, illustrations)
- Selecting copywriting framework (present recommendation)
- Generating section copy drafts

**Ask before running:**
- Framework selection (present recommendation, get confirmation)
- Page structure (present section table, get approval before writing copy)
- Final page spec (present complete spec, get approval)
- Saving to file or Obsidian vault
- Generating HTML prototype
- Handing off email sequences to `/newsletter`

---

## Examples

### Example 1: Info-Product Sales Page
```
User: /web-design "AI Agent Mastery Course" --location ces
Framework: PAS (cold traffic, complex digital product)
Flow:
1. Resolve ces brand, read brand-web-design.md + brand-voice.md
2. Ingest: AI course, aspiring AI builders, cold traffic, $297
3. Framework: PAS — Problem (wasting time on manual work) → Agitate (competitors shipping AI) → Solution (this course)
4. Structure: 10-section sales page blueprint from brand-web-design.md
5. Copy: Write all 10 sections in Ces voice (Playfair headlines, Gold CTAs)
6. Visual: Ivory bg, Gold pill buttons, pillar = AI+Product (Gold accents)
7. Preview: Full spec with copy, layout, tokens
8. Export: Markdown spec file
```

### Example 2: SaaS Landing Page
```
User: /web-design "ProjectFlow — AI project management tool" SaaS
Framework: AIDA (warm traffic from Product Hunt)
Flow:
1. Resolve brand
2. Ingest: SaaS tool, PMs and founders, warm, freemium + $29/mo + $79/mo
3. Framework: AIDA — hero attention → product interest → social desire → CTA action
4. Structure: 8-section SaaS blueprint
5. Copy: <8 word hero headline, 3-tier pricing, single CTA focus
6. Export: Markdown spec + Figma handoff (if Figma MCP available)
```

### Example 3: Lead Generation Funnel
```
User: /web-design funnel for "Free AI Toolkit" lead magnet → $27 mini-course → $297 full course
Framework: Hook-Story-Offer (funnel architecture)
Flow:
1. Resolve brand
2. Map Value Ladder: Free toolkit → $27 tripwire → $297 core
3. Design 4 pages: Opt-in, Thank You + Tripwire, Sales Page, Thank You
4. Specify email triggers between pages
5. Export: Funnel map + individual page specs
6. Hand off email sequence to /newsletter
```

### Example 4: B2B Product Page
```
User: /web-design product page for "Industrial Sensor Kit" B2B --location shopwired-nordic
Framework: FAB (feature-heavy, technical audience)
Flow:
1. Resolve shopwired-nordic brand
2. Ingest: Physical product, procurement managers, technical specs critical
3. Structure: Product page blueprint with B2B additions (SKU, bulk ordering, spec sheet)
4. Copy: Technical but benefit-focused, quote request CTA
5. Export: Markdown spec
```

---

## Cross-Skill Integration

| Skill | When to use | How |
|-------|-------------|-----|
| `/newsletter` | Funnel email sequences | Hand off email copy + schedule |
| `/distribute` | Promote the page on social | Generate social posts linking to the page |
| `/linkedin` | LinkedIn-specific promotion | Create a LinkedIn post about the offer |
| `/blog` | SEO content linking to the page | Write a blog post that links to the sales/landing page |
| `/vault-save` | Save spec to Obsidian | Save with `type: web-design-spec` |
| `/presentation` | Pitch the page design to stakeholders | Create a deck walking through the page design |
