# Step 0: Resolve Location, Credentials & Brand

Determine which GHL subaccount, API key, and brand identity to use.

1. If `--location <shorthand>` is provided in the command, use that location.
2. If no `--location` flag, read `locations.json` in `$PWD`:
   - **Single location:** Use it automatically (no prompt needed).
   - **Multiple locations:** Read `.user.json` `allowedLocations` (if exists) to filter the list. Ask the user: "Which GHL location? Available: <filtered list>"
3. Resolve API key via `apiKeyVar` in `locations.json` (falls back to `$GHL_API_KEY` if not set).
4. Resolve brand directory: `$PWD/brands/<location>/` if it exists, else fall back to `${CLAUDE_PLUGIN_ROOT}/skills/distribute/references`.
5. Read `ghl_accounts_map.json[<location>]` to get that location's available platforms and account IDs.
6. Store the resolved `LOCATION` shorthand. Pass `--location <LOCATION>` to ALL downstream scripts.

**Brand files:** Read brand voice and visual identity from the resolved brand directory (BRAND_DOCS_DIR). Each location can have its own brand personality, writing rules, visual style, and banned words.

**Multi-location distribution:** If the user says "both" or "all locations", upload the media once, then create separate posts for each location's accounts (each location gets its own scheduling slot via `next_slot.sh --location <loc>` and its own brand voice for captions).
