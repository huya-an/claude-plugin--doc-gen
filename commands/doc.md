# /doc — Discovery & Planning

Scan the codebase and create a documentation plan.

## Instructions

You are running the `/doc` command — the first step in documentation generation.

**This command does NOT generate documentation — it only creates the plan.**

### Step 1: Check for Existing Plan

Check if `docs/.doc-plan.json` already exists.
- If it does, ask the user: "An existing documentation plan was found. Re-scan (overwrites) or view current plan?"
- If they want to view, read and display the current plan, then stop
- If they want to re-scan, continue below

### Step 2: Locate Plugin Skills

Find the doc-discover skill file. Try these in order:

1. Use Glob tool to search locally:
   `**/plugins/doc-gen/skills/doc-discover/SKILL.md`

2. If Glob returns no results, run this command with the Bash tool:
   `find ~/.claude/plugins/cache -name "SKILL.md" -path "*/doc-discover/*" 2>/dev/null | head -1`

3. Use the Read tool to read the SKILL.md file at the path found. It contains additional discovery context.

### Step 3: Execute Discovery

Read and follow the instructions in the `doc-discover/SKILL.md` file you located in Step 2. Execute them directly in your current session — do NOT try to invoke a separate skill.

The skill file contains the complete, authoritative instructions for:
- Detecting the project type
- Inventorying files by category
- Building the documentation plan (with correct 6-wave structure)
- Presenting the plan to the user for approval
- Writing `docs/.doc-plan.json` and `docs/.doc-manifest.json`
- Validating the plan JSON (mandatory — must pass before proceeding)

**Do NOT use any inline wave tables, section lists, or example plans from this command file.** The skill file is the single source of truth for discovery logic.

### Step 4: Display Next Steps

```
Documentation plan saved!

Files created:
  - docs/.doc-plan.json (documentation plan)
  - docs/.doc-manifest.json (file-to-section mapping)

Next steps:
  1. Run /doc-generate to generate markdown documentation
  2. Run /doc-site to build the static HTML site
  3. Open docs/site/index.html in your browser
```

### Important Rules
- Never read full source files — only Glob for discovery and Grep for patterns
- Be conservative — include a section if in doubt
- Respect user choices when they disable sections
- Handle monorepos — if multiple projects detected, ask which to document
- Exclude plugin directories, node_modules, vendor, .git, and docs/ from scanning
- **The plan JSON MUST include `"wave"` on every section and a top-level `"waves"` object** — required for `/doc-generate` wave execution
