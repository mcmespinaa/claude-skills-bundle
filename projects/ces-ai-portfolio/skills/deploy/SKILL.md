---
name: deploy
description: Build and deploy the portfolio site to Cloudflare. Use when user says /deploy, deploy this, push to production, or ship it.
allowed-tools: "Bash Read Grep Glob"
---

# /deploy — Build & Deploy Skill

## Steps

1. **Pre-flight checks**
   - Run `yarn lint` — fix any errors before proceeding
   - Run `yarn build` — verify production build passes
   - Check `git status` — warn if uncommitted changes exist

2. **Build for Cloudflare**
   - Run `yarn build:cf` (OpenNext + Wrangler build)
   - Verify output in `.open-next/` or equivalent

3. **Deploy**
   - Run `yarn deploy` (wrangler deploy)
   - Report the deployment URL

4. **Post-deploy**
   - Confirm deployment is live
   - Report any errors or warnings from the build

## Rules
- Always build before deploying — never deploy without a successful build
- Warn the user if there are uncommitted changes
- If build fails, diagnose and report — do not deploy broken code
