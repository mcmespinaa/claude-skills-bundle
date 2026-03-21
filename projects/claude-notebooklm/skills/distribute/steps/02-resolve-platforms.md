# Step 2: Resolve Platforms & Accounts

Using the `LOCATION` resolved in Step 0:

1. Read `ghl_accounts_map.json[<LOCATION>]["accounts"]` to get all available platforms and their account IDs for this location.
2. If user specified platforms (e.g., "IG FB"), filter to those. Otherwise use defaults from the routing table.
3. If a requested platform is not available for this location, warn the user and skip it.
4. If the content type maps to "Upload to Media Library" only (no default platforms), inform the user and upload without creating a post. Offer to create a text announcement post instead.

**Account ID lookup:** Do NOT hardcode account IDs. Always read them dynamically from `ghl_accounts_map.json` for the resolved location. Each location has its own unique account IDs.

Example structure in `ghl_accounts_map.json`:
```json
{
  "ces": {
    "accounts": {
      "FB": { "id": "...", "platform": "facebook" },
      "IG": { "id": "...", "platform": "instagram" },
      "TH": { "id": "...", "platform": "threads" },
      "LI": { "id": "...", "platform": "linkedin" }
    }
  }
}
```
