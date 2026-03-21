You are starting a fresh session or switching context to the SEOS vault. Load full context from the Obsidian SEOS vault before any work begins.

## What is SEOS

SEOS (Swedish Business Knowledge Base) is an Obsidian vault at `~/Obsidian/SEOS/` containing structured knowledge about starting and running a business in Sweden. Sourced from verksamt.se and skatteverket.se. It has 91 pages across 16+ sections.

## Steps

1. **Read vault index**
   - Read `~/Obsidian/SEOS/Welcome.md` for the full vault overview and structure
   - Read `~/Obsidian/SEOS/00-Index/URL Registry.md` to understand all source URLs

2. **Read section indexes** — read every section's main index page:
   - `~/Obsidian/SEOS/01-Starting a Business/Starting a Business.md`
   - `~/Obsidian/SEOS/02-Running a Business/Running a Business.md`
   - `~/Obsidian/SEOS/03-Taxes & Contributions/Taxes & Contributions.md`
   - `~/Obsidian/SEOS/04-Accounting & Bookkeeping/Accounting & Bookkeeping.md`
   - `~/Obsidian/SEOS/05-Employees & Recruitment/Employees & Recruitment.md`
   - `~/Obsidian/SEOS/06-Agreements & Invoicing/Agreements & Invoicing.md`
   - `~/Obsidian/SEOS/07-Financial Security/Financial Security.md`
   - `~/Obsidian/SEOS/08-Import & Export/Import & Export.md`
   - `~/Obsidian/SEOS/09-Trademarks & Patents/Trademarks & Patents.md`
   - `~/Obsidian/SEOS/10-Sustainable Business/Sustainable Business.md`
   - `~/Obsidian/SEOS/11-Closing Down/Closing Down.md`
   - `~/Obsidian/SEOS/12-Financing & Advice/Financing & Advice.md`
   - `~/Obsidian/SEOS/13-Protect Your Company/Protect Your Company.md`
   - `~/Obsidian/SEOS/14-Industry/Industry.md`
   - `~/Obsidian/SEOS/15-Legal/Legal Overview.md`
   - `~/Obsidian/SEOS/16-Agency Operations/Agency Operations Overview.md`

3. **Read supplementary files**
   - `~/Obsidian/SEOS/Business Model.md`
   - `~/Obsidian/SEOS/Competitors/Competitor Analysis.md`
   - `~/Obsidian/SEOS/Regulations/Swedish Accounting Requirements.md`
   - `~/Obsidian/SEOS/Regulations/Employment Law Summary.md`
   - `~/Obsidian/SEOS/Research/Needs Assessment.md`
   - `~/Obsidian/SEOS/Skatteverket/00 - Skatteverket Index.md`

4. **Scan for deep content** — list all files in each section folder to know what detail pages exist:
   ```
   find ~/Obsidian/SEOS -name "*.md" -type f | sort
   ```

5. **Check research directory** for any companion knowledge bases:
   - Read `~/ai-skatteverket/research/CONTEXT.md`
   - List files in `~/ai-skatteverket/research/`

6. **Output a session briefing** in this format:

```
## SEOS Vault Briefing — [date]

### Vault Stats
- Total pages: [count]
- Sections: [list of 16+ sections with page counts]

### Content Coverage
[For each section: brief summary of what's documented and any gaps noted]

### Companion Research Files
[List any knowledge bases in ai-skatteverket/research/ that supplement the vault]

### Key Sources
- verksamt.se: [coverage status]
- skatteverket.se: [coverage status]

### Ready For
[What types of tasks this vault supports: business setup guidance, tax questions, legal lookups, etc.]
```

7. **Ask the user**: "What area of the SEOS vault are you focusing on?"

## Rules
- Do NOT start any implementation work — this is orientation only
- Do NOT summarize files you haven't actually read
- Read section index pages in parallel (batch of 4-5 at a time) for speed
- If the user specified a section in their message, read ALL files in that section folder deeply
- All output must be in English; translate Swedish sources, keep Swedish terms in parentheses on first use
