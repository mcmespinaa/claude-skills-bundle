# Step 1: Identify Content

Three invocation patterns:

1. **File path given:** `/distribute ./infographic.png IG FB TH` — use the file directly.
2. **After download:** User just ran `notebooklm download infographic ./file.png` — use that file.
3. **No file given:** User says "distribute the latest infographic" — run `notebooklm artifact list --json`, find the latest artifact of that type, download it to a temp path, then proceed.

Detect content type from file extension. Look up the Content-Type Routing Table in the parent SKILL.md.
