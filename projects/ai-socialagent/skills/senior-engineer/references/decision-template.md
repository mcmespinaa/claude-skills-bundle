# Decision Template

Use this format when logging architectural or engineering decisions. Every non-obvious choice should be recorded — the cost of writing it is 2 minutes, the cost of re-litigating it later is hours.

---

## When to Log a Decision

- Choosing between two or more viable approaches
- Rejecting a "standard" approach for a project-specific reason
- Adopting a dependency, framework, or service
- Defining a convention that others will follow
- Making a tradeoff (speed vs. correctness, simplicity vs. flexibility)
- Deferring something intentionally (not forgetting — choosing to wait)

## When NOT to Log

- Following the framework's default/recommended approach
- Using standard library functions as intended
- Obvious choices with no viable alternative

---

## Format

### Inline (for small decisions near the code)

```
// Decision: Using JSONB instead of separate columns for translations.
// Reason: Scales to 3+ languages without schema changes.
// Rejected: Separate columns (doesn't scale), translation table (overkill for 2 languages).
```

### Registry Entry (for architectural decisions)

```markdown
### DEC-NNN — [short title]
- **status:** accepted | proposed | deferred
- **date:** YYYY-MM-DD
- **context:** What situation prompted this decision? What problem are we solving?
- **decision:** What did we decide? Be specific enough to act on.
- **rationale:** Why this approach? What's the key tradeoff?
- **alternatives rejected:** What else did we consider and why didn't we pick it?
```

---

## Decision Quality Checklist

A good decision entry answers these questions:

1. **What did we choose?** (Specific enough that someone could implement it)
2. **Why?** (The actual reason, not a post-hoc justification)
3. **What didn't we choose?** (Shows you considered alternatives)
4. **Why not?** (The actual tradeoff that made you reject it)

A bad decision entry is:
- "We chose X because it's best practice" (doesn't explain why it's best for *this* project)
- "We chose X" without alternatives (no evidence of deliberation)
- "We chose X because Y said so" (defers reasoning to authority)

---

## Examples

**Good:**
> DEC-009 — Meta Conversions API (server-side) per organization
> - **context:** Each org page needs its own ad tracking. Meta deprecated client-side pixels.
> - **decision:** Server-side CAPI via Next.js API route. Each initiative stores `meta_pixel_id` in Supabase. Dual-send to org pixel + master pixel.
> - **rationale:** Server-side avoids ad blockers. Per-org pixel IDs in database = scalable. Dual-send ensures master account sees all traffic.
> - **alternatives rejected:** Client-side pixel (blocked by ad blockers, deprecated by Meta), single pixel for all orgs (can't optimize ad spend per organization)

**Bad:**
> We're using Meta CAPI because it's the recommended approach.

The good version tells you *what*, *why*, *how*, and *why not the alternatives*. The bad version tells you nothing useful.
