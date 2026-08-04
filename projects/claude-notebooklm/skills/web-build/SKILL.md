---
name: web-build
description: >-
  Build and deploy websites from /web-design specs or from scratch. Orchestrates
  Google Stitch (AI UI generation via MCP), Nano Banana 2 (AI image generation),
  and /render (branded templates) to produce deployable sites. Deploys to
  Firebase Hosting (static) or Cloud Run (SSR). Use when user says 'build this
  site', 'deploy to firebase', 'turn this spec into a website', 'make this
  live', or invokes /web-build. Do NOT use for design specs only -- use
  /web-design instead.
argument-hint: '"site description or spec file" [--stack astro|nextjs|html-tailwind] [--deploy firebase|cloudrun|none] [--location ces]'
disable-model-invocation: true
---

# /web-build -- Spec to Deployed Website

> **Trigger:** User says `/web-build`, "build this site", "deploy to firebase", "turn this spec into a website", "make this live", or similar.

## Role

You are a full-stack web builder. You take design specs (from `/web-design`) or natural language descriptions and produce deployable websites using AI-generated UI screens (Google Stitch), AI-generated images (Nano Banana 2), and branded HTML templates (/render). You handle the entire pipeline: design generation, code assembly, and deployment.

---

## Constants

```
WEB_BUILD_SCRIPTS: ${CLAUDE_PLUGIN_ROOT}/skills/web-build/scripts
RENDER_SCRIPTS:    ${CLAUDE_PLUGIN_ROOT}/skills/render/scripts
BRAND_DOCS_DIR:    Resolved in Step 0 -- $PWD/brands/<LOCATION>/ or fallback
GCP_PROJECT:       gen-lang-client-0715587042
BUILD_OUTPUT:      /tmp/web-build/<slug>/
```

---

## Tools Available

### Google Stitch (MCP) -- Interactive UI Generation
| Tool | Purpose |
|------|---------|
| `generate_screen_from_text` | Create a UI screen from a text prompt |
| `extract_design_context` | Extract "Design DNA" (fonts, colors, layouts) from a screen |
| `build_site` | Map screens to routes, get HTML per page |
| `get_screen_code` | Download raw HTML/CSS of a screen |
| `get_screen_image` | Download screenshot of a screen |
| `list_projects` | Browse existing Stitch projects |
| `list_screens` | List screens in a project |
| `create_project` | Create a new Stitch project |

### Nano Banana 2 -- AI Image Generation
```bash
python3 "${RENDER_SCRIPTS}/nano_banana.py" \
  --prompt "description" --brand ces --aspect-ratio 16:9 --size 1K \
  --output /tmp/hero.png
```

### /render -- Branded Template Rendering
```bash
python3 "${RENDER_SCRIPTS}/render.py" \
  --template social-card --data '{"headline":"..."}' \
  --brand ces --size 1080x1080 --output /tmp/card.png
```

### Deploy Scripts
```bash
# Firebase Hosting (static sites)
bash "${WEB_BUILD_SCRIPTS}/firebase_deploy.sh" \
  --project-dir /tmp/web-build/my-site --channel preview

# Cloud Run (SSR apps)
bash "${WEB_BUILD_SCRIPTS}/cloudrun_deploy.sh" \
  --project-dir /tmp/web-build/my-app --service my-app
```

---

## Stacks

| Stack | Deploy Target | When to Use |
|-------|--------------|-------------|
| `html-tailwind` | Firebase Hosting | Simple landing/sales pages, no build step |
| `astro` | Firebase Hosting | Multi-page static sites (Stitch default output) |
| `nextjs` | Cloud Run | SSR apps, dashboards, sites with API routes |
| `nuxtjs` | Cloud Run | Vue-based SSR apps |
| `sveltekit` | Cloud Run | Svelte SSR apps |

Default: `astro` (matches Stitch's `site` command output).

---

## Workflow

### Step 0: Resolve Location & Brand

1. If `--location <shorthand>` is provided, use that location.
2. If no flag, read `locations.json`:
   - **Single location:** Use it automatically.
   - **Multiple locations:** Ask the user which brand/location.
3. Resolve brand directory: `$PWD/brands/<location>/`.

### Step 1: Gather Input

Determine the source:

| Source | How to Detect | Action |
|--------|--------------|--------|
| `/web-design` spec file | User passes a `.md` file path or says "build from spec" | Read the spec, extract sections, copy, tokens |
| Natural language | User describes what they want ("build a landing page for X") | Gather requirements, then generate design inline |
| Existing Stitch project | User provides a Stitch project ID | Use `list_screens` to see what's there |

**If starting from scratch (no spec), collect:**
- What the site is for (product, service, portfolio)
- Target audience
- Number of pages and their purpose
- Tech stack preference (or auto-select)
- Deploy target (Firebase or Cloud Run)

### Step 2: Create Stitch Project

```
Use MCP: create_project with name "<site-slug>"
```

Store the `projectId` for subsequent calls.

### Step 3: Generate Screens with Stitch

For each page in the spec (or each page the user described):

**3a. Generate the first screen with brand context:**
```
Use MCP: generate_screen_from_text
Prompt: "Design a [page type] page for [product/service].
  Brand colors: Ivory background (#f7f4ef), Warm Charcoal text (#3a352e), Gold accent (#b8a06a).
  Fonts: Playfair Display for headings, DM Sans for body.
  Style: Nordic minimalist, generous white space, clean typography.

  Content:
  [Paste section copy from spec — headline, subheadline, body, CTA text]

  Layout:
  [Paste layout instructions from spec]"
```

**3b. Extract Design DNA from the first screen:**
```
Use MCP: extract_design_context with the first screen's ID
```
This returns the design system Stitch inferred. Use it as context for subsequent screens to maintain visual consistency.

**3c. Generate remaining screens:**
For each additional page, include the Design DNA from 3b in the prompt:
```
Use MCP: generate_screen_from_text
Prompt: "Design a [page type] page. Use this design system: [Design DNA from 3b].
  Content: [section copy]
  Layout: [layout instructions]"
```

**3d. Preview and iterate:**
After each screen generation, use `get_screen_image` to show the user a preview.
Ask: "Does this look right? Any changes?"
If changes needed, regenerate with updated prompt.

### Step 4: Generate Images with Nano Banana 2

For hero images, product visuals, illustrations, or any creative imagery the spec calls for:

```bash
python3 "${RENDER_SCRIPTS}/nano_banana.py" \
  --prompt "Hero image: [description from spec]. Professional, high-quality." \
  --brand "$LOCATION_KEY" \
  --aspect-ratio 16:9 \
  --size 2K \
  --output "/tmp/web-build/${SLUG}/assets/hero.png"
```

**When to use Nano Banana vs Unsplash:**
| Need | Tool |
|------|------|
| Custom, brand-specific imagery | Nano Banana 2 |
| Generic stock photography | Unsplash (`unsplash_fetch.py`) |
| Product mockups, illustrations | Nano Banana 2 |
| Real-world photos of specific things | Unsplash |

### Step 5: Assemble the Site

**Option A: Stitch Site Export (Astro)**
```
Use MCP: build_site with projectId and routes mapping
  routes: [
    { screenId: "abc", route: "/" },
    { screenId: "def", route: "/about" },
    { screenId: "ghi", route: "/pricing" }
  ]
```

Then from CLI (if customization needed):
```bash
npx @_davideast/stitch-mcp site -p <projectId>
```

This generates a complete Astro project.

**Option B: Manual Assembly (html-tailwind or other stacks)**

1. Use `get_screen_code` for each screen to get the HTML/CSS.
2. Create the project structure manually:
```
/tmp/web-build/<slug>/
├── index.html
├── about.html
├── pricing.html
├── assets/
│   ├── hero.png (from Nano Banana)
│   ├── logo.png (from brand dir)
│   └── styles.css
└── firebase.json (auto-generated by deploy script)
```
3. Inject brand assets (logo, favicon, fonts) from `$BRAND_DIR`.
4. Replace Stitch's generic fonts/colors with exact brand tokens.

### Step 6: Brand Refinement

After assembly, verify brand consistency:

1. **Colors:** Search the HTML for any hex codes that don't match the brand palette. Replace with brand tokens.
2. **Fonts:** Ensure Google Fonts `<link>` tags load the correct brand fonts.
3. **Logo:** Inject brand logo from `$BRAND_DIR/` if not already present.
4. **Favicon:** Generate or copy from brand assets.
5. **Meta tags:** Add OG image, title, description for SEO.
6. **Brand handle:** Add footer credit if applicable.

### Step 7: Preview

Before deploying, offer a local preview:

```bash
# For Astro projects
cd "/tmp/web-build/${SLUG}" && npm install && npm run dev

# For static HTML
python3 -m http.server 8000 --directory "/tmp/web-build/${SLUG}"
```

Ask: "Preview is running at http://localhost:8000. Check it and let me know if you want changes."

### Step 8: Deploy

Based on user preference or auto-detection:

**Firebase Hosting (static sites, Astro):**
```bash
# Build Astro first if needed
cd "/tmp/web-build/${SLUG}" && npm run build

# Deploy preview
bash "${WEB_BUILD_SCRIPTS}/firebase_deploy.sh" \
  --project-dir "/tmp/web-build/${SLUG}" \
  --channel preview \
  --location "$LOCATION_KEY"
```

Present the preview URL. Ask: "Preview is live at [URL]. Ready to go live?"

**Promote to production:**
```bash
bash "${WEB_BUILD_SCRIPTS}/firebase_deploy.sh" \
  --project-dir "/tmp/web-build/${SLUG}" \
  --channel live \
  --location "$LOCATION_KEY"
```

**Cloud Run (SSR frameworks):**
```bash
bash "${WEB_BUILD_SCRIPTS}/cloudrun_deploy.sh" \
  --project-dir "/tmp/web-build/${SLUG}" \
  --service "${SLUG}" \
  --location "$LOCATION_KEY"
```

### Step 9: Post-Deploy

After successful deployment:

1. **Screenshot the live site** for social sharing:
```bash
python3 "${RENDER_SCRIPTS}/render.py" \
  --url "$DEPLOYED_URL" \
  --size 1200x630 \
  --output "/tmp/web-build/${SLUG}/screenshot.png"
```

2. **Generate OG image** if not already done:
```bash
python3 "${RENDER_SCRIPTS}/render.py" \
  --template og-image \
  --data '{"headline":"$SITE_TITLE","pillar":"$PILLAR"}' \
  --brand "$LOCATION_KEY" \
  --size 1200x630 \
  --output "/tmp/web-build/${SLUG}/og-image.png"
```

3. **Offer cross-skill actions:**
   - `/distribute` — announce the site on social media
   - `/linkedin` — write a LinkedIn post about the launch
   - `/newsletter` — send a launch email to subscribers
   - `/blog` — write a blog post about the new site
   - `/vault-save` — save the build details to Obsidian

---

## Deploy Target Selection

| Indicator | Target | Why |
|-----------|--------|-----|
| Static HTML, no API routes | Firebase Hosting | Free, fast CDN, preview channels |
| Astro (static mode) | Firebase Hosting | Builds to `dist/`, perfect for static hosting |
| Next.js with SSR/API routes | Cloud Run | Needs Node.js runtime |
| Nuxt with SSR | Cloud Run | Needs Node.js runtime |
| User says "firebase" | Firebase Hosting | Explicit preference |
| User says "cloud run" | Cloud Run | Explicit preference |
| `--deploy none` | Skip deployment | Just generate the code |

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| Stitch MCP not available | Server not configured or auth expired | Fall back to manual HTML generation using Nano Banana for visuals |
| Nano Banana API key missing | `GOOGLE_API_KEY` not in `.env` | Warn and fall back to Unsplash for images |
| Firebase not installed | `firebase-tools` missing | Print install command, offer to install |
| gcloud not installed | gcloud CLI missing | Print install link |
| Stitch rate limit | Too many API calls | Wait and retry, or fall back to manual |
| Build fails | Framework-specific error | Show error, suggest fixes |
| Deploy fails | Auth or config issue | Show error, suggest `firebase login` or `gcloud auth login` |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading locations.json and brand files
- Creating Stitch project
- Generating screens (show previews as they're created)
- Generating images with Nano Banana
- Assembling project files
- Building (npm run build)

**Ask before running:**
- Deploying to preview channel (show what will be deployed)
- Promoting preview to live (confirm the preview URL looks good)
- Installing dependencies (npm install, firebase-tools)
- Any destructive action (overwriting existing deployment)

---

## Examples

### Example 1: Build from /web-design Spec
```
User: /web-build "/tmp/web-design-spec-ai-course.md" --deploy firebase
Flow:
1. Read spec → extract 10 sections with copy and layout
2. Create Stitch project "ai-course-landing"
3. Generate hero screen with Ces brand context
4. Extract Design DNA → feed to remaining 9 sections
5. Generate Nano Banana hero image: "AI neural network, gold tones, premium"
6. build_site → map to single-page routes
7. Brand refinement: swap fonts, inject logo
8. Deploy preview → present URL
9. User approves → deploy live
10. Screenshot → offer /distribute
```

### Example 2: Quick Landing Page from Scratch
```
User: /web-build "landing page for a free AI toolkit lead magnet" --stack html-tailwind
Flow:
1. No spec → gather: audience (marketers), CTA (download), offer (free toolkit)
2. Generate single Stitch screen with brand context
3. Get screen code → save as index.html
4. Generate Nano Banana hero: "AI toolkit floating elements, minimalist"
5. Inject brand tokens, logo, meta tags
6. Deploy to Firebase preview
```

### Example 3: Multi-page SaaS Site
```
User: /web-build "ProjectFlow SaaS — 4 pages: home, features, pricing, contact" --stack nextjs --deploy cloudrun
Flow:
1. Create Stitch project "projectflow"
2. Generate 4 screens, extract DNA after first
3. Generate product mockups with Nano Banana
4. build_site with 4 routes
5. Convert to Next.js structure (pages/, components/)
6. Deploy to Cloud Run
```

---

## Cross-Skill Integration

| Skill | Direction | How |
|-------|-----------|-----|
| `/web-design` | Input | Read its spec as the blueprint for this skill |
| `/render` | Utility | Screenshots, OG images, social cards for the built site |
| `/distribute` | Output | Announce the deployed site on social media |
| `/linkedin` | Output | Write a launch post |
| `/newsletter` | Output | Send a launch email |
| `/blog` | Output | Write a blog post about the new site |
| `/vault-save` | Output | Save build details and URLs to Obsidian |
