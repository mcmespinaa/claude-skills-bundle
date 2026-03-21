---
name: vault-save
description: Save content to the Obsidian documentation vault. Use when user says /vault-save, save this to the vault, document this, or log this decision.
allowed-tools: "Read Write Edit Grep Glob"
---

# /vault-save — Vault Save Skill

## Steps

1. **Determine content type** from user input:
   - Research findings → `Ces Portfolio/research/research-{slug}.md`
   - Product spec → `Ces Portfolio/product/product-{slug}.md`
   - Build documentation → `Ces Portfolio/build/build-{slug}.md`
   - Decision → `Ces Portfolio/decisions/decision-registry.md`
   - Journal/reflection → `Ces Portfolio/journal/journal-{slug}-{date}.md`
   - Playbook → `Ces Portfolio/playbooks/playbook-{slug}.md`
   - Competitive analysis → `Ces Portfolio/competitive/competitive-{slug}.md`

2. **Check for duplicates**
   - Search existing files in the target folder
   - If similar content exists, update rather than create new

3. **Write the file**
   - Use kebab-case naming: `{type}-{descriptive-slug}.md`
   - Add YAML frontmatter with `aliases`
   - Follow the format of existing files in the same folder

4. **Update _index.md**
   - Add the new file to the relevant table in `Ces Portfolio/_index.md`

## Rules
- Follow existing naming conventions exactly
- Never overwrite without checking first
- Keep file names descriptive but concise
- Always update the vault index after creating a new file
