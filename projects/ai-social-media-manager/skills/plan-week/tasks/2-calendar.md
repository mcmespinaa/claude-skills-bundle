# Task 2 -- Build the Content Calendar

Map content to a 7-day schedule with varied themes and post types.

## Steps

1. Run `bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/next_slot.sh --location <shorthand> --log ghl_post_log.md` to get the first available slot.
2. Space posts across 7 days from that start date, one slot per day at the same time (default 09:00 UTC).
3. Assign content to days:
   - Distribute topics so the week feels varied, not repetitive.
   - Alternate between content types: personal story, educational, AI/tech insight, encouragement, actionable tip.
   - Map to Key Recurring Themes from `/post` SKILL.md: discernment over hustle, relationships over achievements, build things, take care of your body, you are enough, AI is a skill, sustainability over intensity, share hard lessons.
4. Determine post types per day:
   - Default: mix of single-image posts with 1-2 carousel days (ideally mid-week for higher engagement).
   - If user provided enough content for more carousels, adjust accordingly.
5. Assign platforms per post:
   - Default: every post goes to all platforms in `ghl_accounts_map.json`.
   - Write a separate caption per platform (same message, different format/length/tone).

## Planning Parameters

Confirm or infer these. **Minimize questions.** If the user gives enough context, infer the rest and present the plan. Only ask when truly ambiguous.

| Parameter | Default | Ask if unclear |
|-----------|---------|----------------|
| Number of days | 7 | Only if user says "3 days" or similar |
| Posts per day | 1 per platform in `ghl_accounts_map.json` | Only if user wants more or fewer |
| Platforms | All from `ghl_accounts_map.json` | Only if user wants a subset |
| Start date | Next free slot from `ghl_post_log.md` | Only if user specifies a date |
| Post types | Mix of single image + 1-2 carousels | Only if user wants all one type |
| Scheduling mode | `scheduled` (future date) | Ask only if user mentions "publish now" or "queue" |
| Posting time | Same as last logged post (default 09:00 UTC) | Only if user specifies a time |

## Output

A day-by-day calendar structure ready for draft writing:
- Day number, date, weekday
- Theme/topic for each day
- Content pillar (AI, Leadership, Health, Consciousness, General)
- Post type (single image, carousel, text-only)
- Target platforms

Proceed to Task 3 when the calendar structure is set.
