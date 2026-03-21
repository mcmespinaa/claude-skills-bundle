---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces for the Organic Forward B2B marketplace. Combines conversion-optimized ecommerce patterns, Rigby marketplace UX principles, and the project's design system (Next.js 15 + React + Tailwind + shadcn/ui + @medusajs/ui). Use when building storefront pages, components, or dashboard interfaces.
---

You are building frontend for **Organic Forward** — a B2B marketplace connecting organic food SMEs (farmers/producers) with EU procurement buyers. Built on MercurJS/Medusa.js 2.0, Next.js 15, React, Tailwind CSS, shadcn/ui, and @medusajs/ui.

The user provides frontend requirements: a component, page, section, or interface to build. They may include Figma links, wireframes, or verbal descriptions.

---

## Step 1: Understand Context

Before writing code, determine:
- **What entity?** Product, category, collection, vendor, cart, checkout, dashboard, landing page
- **Who uses it?** Buyer (procurement officer), vendor (farmer/producer), admin (marketplace operator)
- **What phase?** MVP (keep simple) or polish (go bold)
- **Stack constraints?** Read the sub-project CLAUDE.md: `b2b-storefront/CLAUDE.md`, `mercur-admin/CLAUDE.md`, or `mercur-vendor/CLAUDE.md`

---

## Step 2: Apply Conversion Principles

### Above-the-Fold Rules (50ms judgment window)
- Product/hero image LEFT, value proposition text RIGHT
- Star ratings + review count visible ("4.5 from 847 reviews")
- Price clearly visible with bulk pricing tiers for B2B
- Primary CTA high-contrast, action-oriented ("Request Quote", "Add to Cart")
- Trust bar: organic certification badges + shipping + returns

### CTA Design
- Optimal placement zone: 600-1000px from top
- High-contrast button color against background
- Action text: "Get Quote for 500kg" beats "Submit"
- Sticky mobile CTAs on scroll-heavy pages
- B2B dual CTAs: "Add to Cart" + "Request Quote"

### Trust Signals (our competitive moat)
1. **Header bar**: BioC/KRAV/EU organic badges, free shipping threshold, return policy
2. **Near product title**: star ratings, review count, certification icons
3. **Near CTA**: payment security, verified vendor badge
4. **Near forms**: privacy assurance, SSL indicators
5. **Below fold**: detailed certifications, traceability info, vendor story

### Key Metrics to Design For
- Products with 5+ reviews convert 270% better
- 70% cart abandonment — streamline checkout ruthlessly
- 32% of B2B buyers say easy checkout is #1 feature
- 67% of customers visit returns page before purchasing
- Page must load in ≤3 seconds (53% expectation)

---

## Step 3: Apply Marketplace UX Patterns (from Rigby/MercurJS)

### Six Foundational Principles
1. **Clarity over creativity** — straightforward labeling beats clever design
2. **Consistency across touchpoints** — repeating patterns reduce cognitive load
3. **Performance matters** — skeleton states, not spinners
4. **Keep users informed** — real-time feedback on all interactions
5. **Mobile-first baseline** — design for smaller screens first
6. **Trust by design** — verification badges and transparent policies

### Search & Discovery
- Autosuggestions, spelling corrections, long-tail query support
- Dynamic filters: price, certification type, delivery zone, vendor rating, allergen-free
- Mega menus for task-based ("I need organic olive oil") AND explorational browsing
- "Recent searches" and "recently viewed" to reduce effort
- Empty states: suggest alternatives, offer "notify when available"

### Multi-Vendor Cart
- Split items by vendor with clear attribution
- Per-vendor subtotals + shipping estimates
- Consolidated total with tax breakdown
- Post-purchase: unified tracking across vendors

### B2B Checkout
- Guest checkout by default; soft registration post-purchase
- Progress indicator (breadcrumb or step bar)
- Form autofill + validate-on-change (not on-submit)
- Payment options: PO, invoice/NET-30, wire transfer, card
- Delivery time + total cost transparency per vendor

---

## Step 4: Design System Rules

### Color Palette
Use CSS variables. Three custom scales (proposed, apply when building):
- `organic` — green (certification badges, sustainability, primary brand)
- `earth` — warm gold/brown (harvest, natural feel)
- `trust` — blue (EU compliance, verified badges)

Dominant color + sharp accent outperforms evenly-distributed palettes. Define semantic tokens: primary, secondary, error, success, surface, warning.

### Typography
- Base body: 16px minimum, line-height 1.5-1.75
- 60-75 characters per line on desktop
- Choose distinctive fonts — NEVER default to Inter/Roboto/Arial
- Pair a display font (headings) with a refined body font

### Icons
- **@medusajs/icons** — primary for commerce UI (cart, checkout, orders, account, navigation)
- **lucide-react** — supplementary for domain-specific (organic certs, agriculture, allergens, delivery, compliance)
- Never mix both in the same component row

### Spacing & Layout
- 8px base unit grid
- Generous negative space for premium organic feel
- Card-based layouts for product grids
- Table view toggle for bulk buyers (B2B buyers scan specs, not browse)

---

## Step 5: Component Gap Reference

When building, check what exists vs what's needed:

| area | current state | target |
|------|---------------|--------|
| hero | generic electronics banner | organic B2B hero with trust signals + cert badges |
| nav | medusa-branded, search disabled | OF-branded, search-first, procurement mega menu |
| product cards | basic preview + price | bulk pricing, cert badges, min order qty, vendor name |
| product detail | image gallery + tabs | cert strip, allergen info, bulk tiers, RFQ button |
| cart/checkout | CSV export, approval banner | order templates, PO numbers, NET terms display |
| dashboard | profile/orders/quotes | spending analytics, approval queue, reorder |
| footer | medusa links | cert logos, trust signals, supplier CTA |
| catalog | grid only | table view toggle for bulk buyers |

---

## Step 6: Accessibility & Performance (Non-Negotiable)

### WCAG AA Compliance
- Text contrast: 4.5:1 minimum
- Touch targets: 44×44px minimum with 8px spacing
- All images need alt text (including product photos)
- Keyboard navigation on all interactive elements
- ARIA labels on custom components
- Visible focus states
- Respect `prefers-reduced-motion`
- Never convey meaning by color alone

### Performance Targets
- LCP ≤ 2.5 seconds
- CLS < 0.1
- Input latency < 100ms
- Images: WebP/AVIF with fallbacks, lazy load below-fold
- Skeleton states shown immediately while loading

---

## Step 7: Aesthetic Execution

### DO
- Commit to a BOLD aesthetic direction — intentionality matters more than intensity
- Backgrounds with atmosphere: gradient meshes, subtle textures, layered transparencies
- Motion: CSS-only where possible, staggered reveals on page load, purposeful hover states
- Asymmetric layouts, overlap, diagonal flow, grid-breaking elements when appropriate
- Match implementation complexity to aesthetic vision

### DON'T (Anti-"AI Slop" Rules)
- Never use Inter/Roboto/Arial/system fonts
- Never use purple gradients on white backgrounds
- Never use Space Grotesk (overused in AI output)
- Never create cookie-cutter hero sections
- Never use evenly-spaced, evenly-colored grids without visual hierarchy
- Never converge on common choices across generations — each design should be unique

---

## Step 8: Pre-Delivery Checklist

Before presenting any frontend work, verify:

- [ ] Visual hierarchy established through size, spacing, contrast
- [ ] All text meets WCAG AA contrast (4.5:1)
- [ ] Touch targets ≥ 44×44px with adequate spacing
- [ ] Images optimized (WebP/AVIF), dimensioned to prevent layout shift
- [ ] Focus states visible on all interactive elements
- [ ] Animations respect `prefers-reduced-motion`
- [ ] Mobile layout tested, no horizontal scroll
- [ ] Forms have visible labels and clear error messaging
- [ ] Navigation patterns consistent throughout
- [ ] Certification badges prominently displayed
- [ ] B2B CTAs present: "Request Quote" alongside "Add to Cart"
- [ ] Multi-vendor cart clearly attributes items to sellers
- [ ] Delivery zone/time visible before checkout

---

## Reference Resources

When you need deeper patterns:
- **Rigby marketplace UX**: https://www.rigbyjs.com/blog/marketplace-ux
- **Rigby B2B features**: https://www.rigbyjs.com/blog/b2b-marketplace-features
- **Mobbin** (mobbin.com): 604K real screens for pattern research
- **Unsection** (unsection.com): 2,000+ curated website sections
- **Full research**: `~/Obsidian/OrganicForward/research/research-ecommerce-design-conversion-guide.md`
