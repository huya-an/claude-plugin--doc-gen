# /doc-all — Full Documentation Pipeline

Run the complete documentation pipeline: discover, generate markdown (wave-based), build site (`mkdocs build`), and optionally publish to S3.

## Instructions

You are running the `/doc-all` command — the full documentation pipeline in one go.

### Step 1: Discovery (/doc)

Execute the `/doc` command logic directly:

1. Check if `docs/.doc-plan.json` exists. If it does, ask user: "Existing plan found. Re-scan or use existing?"
2. If re-scanning or no plan exists, perform discovery:
   - Detect project type via Glob (pom.xml, package.json, go.mod, etc.)
   - Inventory files by category (controllers, services, entities, events, security, tests, CI/CD, ADRs, quality configs)
   - Exclude: node_modules/, vendor/, .git/, docs/, claude-doc-gen/
   - Build plan with sections, wave assignments, and file counts
   - Present plan table to user via AskUserQuestion for approval
   - Save `docs/.doc-plan.json` and `docs/.doc-manifest.json`

### Step 2: Generate Markdown (/doc-generate) — Wave-Based

1. Read `docs/.doc-plan.json` and `docs/.doc-manifest.json`
2. Validate the plan has a `waves` object
3. Run `mkdir -p docs/md`
4. Locate skills: Glob `**/doc-gen/skills/doc-c4/SKILL.md` — if not found locally, check the plugin cache: Glob `~/.claude/plugins/cache/**/doc-gen/**/doc-c4/SKILL.md`
5. Extract `SKILLS_DIR` base path

Execute waves sequentially: Wave 1 → Wave 2 → Wave 3 → Wave 4. Within each wave, spawn enabled sections in parallel (up to 3 concurrent agents).

**CRITICAL: Each wave MUST fully complete before the next wave starts.** Later waves depend on earlier wave markdown output for context compression.

#### Wave 1: C4 Architecture

Read `{SKILLS_DIR}/doc-c4/SKILL.md` and spawn a single Task agent:

```
You are a documentation agent generating C4 architecture documentation.

CONTEXT:
- Read docs/.doc-plan.json and docs/.doc-manifest.json for your file assignments
- Write output to docs/md/
- If instructions reference "references/", read from: {SKILLS_DIR}/doc-c4/references/
- Read source files in batches of 5-8. Keep output concise, no stubs.

INSTRUCTIONS:
{contents of doc-c4/SKILL.md}
```

Wait for completion. Report status.

#### Wave 2: API, Data, Events (parallel)

For each enabled section in Wave 2, read its SKILL.md and spawn agents **in parallel**:

```
You are a documentation agent generating {section_title} documentation.

CONTEXT:
- Read docs/.doc-plan.json and docs/.doc-manifest.json for your file assignments
- Write output to docs/md/
- If instructions reference "references/", read from: {SKILLS_DIR}/{section_id}/references/
- Read source files in batches of 5-8. Keep output concise, no stubs.

PRIOR WAVE CONTEXT (read these for system context, do not regenerate):
- docs/md/arch-overview.md — system overview from C4 analysis
- docs/md/arch-c4-level1.md — system context diagram
- docs/md/arch-c4-level2.md — container diagram

INSTRUCTIONS:
{contents of SKILL.md}
```

Wait for all Wave 2 agents. Report each status.

#### Wave 3: Security, DevOps, Testing (parallel)

For each enabled section in Wave 3, read its SKILL.md and spawn agents **in parallel**:

```
PRIOR WAVE CONTEXT (read these for cross-domain context, do not regenerate):
Wave 1: docs/md/arch-overview.md, docs/md/arch-c4-level2.md
Wave 2 (read whichever exist): docs/md/api-index.md, docs/md/data-overview.md, docs/md/events-overview.md
```

Wait for all Wave 3 agents. Report each status.

#### Wave 4: ADR, Quality (parallel)

For each enabled section in Wave 4, read its SKILL.md and spawn agents **in parallel**:

```
PRIOR WAVE CONTEXT (read these for full system context, do not regenerate):
Wave 1: docs/md/arch-overview.md, docs/md/arch-c4-level2.md
Wave 2 (read whichever exist): docs/md/api-index.md, docs/md/data-overview.md, docs/md/events-overview.md
Wave 3 (read whichever exist): docs/md/security-overview.md, docs/md/devops-overview.md, docs/md/testing-overview.md
```

Wait for all Wave 4 agents. Report each status.

#### Markdown Validation

Read `{SKILLS_DIR}/doc-validate-md/SKILL.md`, spawn Task agent, display results.

### Step 3: Build Site — MkDocs Build

**CRITICAL: Always use `mkdocs build`. Never manually convert markdown to HTML.**

1. Verify `mkdocs.yml` exists and mkdocs is installed (`which mkdocs`)
2. Read frontmatter from all markdown files, generate `nav:` section for `mkdocs.yml`
3. Create `docs/md/index.md` if missing (project name, section links, generation date)
4. Run `mkdocs build`
5. Verify output:
   - Count HTML pages
   - Count Mermaid blocks (`class="mermaid"`)
   - Check for legacy `<!-- diagram-meta` markers (CRITICAL if found)
6. Run site validation: read `{SKILLS_DIR}/doc-validate-site/SKILL.md`, spawn Task agent, display results

### Step 4: Ask About Publishing

Use AskUserQuestion:
- "Publish to S3?" with options:
  - "Yes — publish to s3://repo-documentation-918308113460/{directory-name}/"
  - "No — just local site"

If yes:
1. Determine directory name from git repo name or current directory basename
2. Verify AWS CLI: `aws sts get-caller-identity`
3. Upload: `aws s3 sync docs/site/ s3://repo-documentation-918308113460/{directory-name}/ --delete`
4. Fix content types for .html, .css, .js files

### Step 5: Final Summary

Display the inventory table using box-drawing characters:

```
┌──────┬───────────────────┬──────┬──────────────────┬──────────────┬─────────────────────────────────┐
│ Wave │      Section      │  #   │ Files to Analyze │ Output Pages │             Status              │
├──────┼───────────────────┼──────┼──────────────────┼──────────────┼─────────────────────────────────┤
│  1   │ Architecture (C4) │  1   │ 45               │ 6            │ ✓ Complete                      │
│  2   │ API Plane         │  2   │ 23               │ 12           │ ✓ Complete                      │
│  2   │ Data / DBA        │  3   │ 15               │ 3            │ ✓ Complete                      │
│  2   │ Events & Async    │  4   │ 0                │ 0            │ ○ Skipped (no files)            │
│  3   │ Security          │  5   │ 8                │ 3            │ ✓ Complete                      │
│  3   │ DevOps            │  6   │ 12               │ 3            │ ✓ Complete                      │
│  3   │ Testing           │  7   │ 34               │ 2            │ ✓ Complete                      │
│  4   │ ADRs              │  8   │ 5                │ 6            │ ✓ Complete                      │
│  4   │ Quality           │  9   │ 6                │ 2            │ ✓ Complete                      │
└──────┴───────────────────┴──────┴──────────────────┴──────────────┴─────────────────────────────────┘
```

Then display:

```
Documentation Complete
=======================
Markdown: docs/md/ ({md_count} files)
Site: docs/site/ ({html_count} pages, {diagram_count} Mermaid diagrams)
Pipeline: 4 waves → mkdocs build
Validation: {PASS/FAIL}

Local: file://{absolute_path}/docs/site/index.html
{If published: S3: https://repo-documentation-918308113460.s3.amazonaws.com/{directory-name}/index.html}
```

### Error Handling

- If discovery fails, stop and report
- If an agent fails during generation, report and continue with remaining agents in that wave
- **A failed agent does NOT block the next wave.** Later-wave agents have less context but still function.
- If `mkdocs build` fails, still show what was generated in markdown
- If S3 publish fails, still show local site path
- If skills directory not found, tell user to verify plugin installation

### Important Rules

- **Wave ordering is mandatory**: Never spawn Wave N+1 agents before Wave N fully completes
- **Do NOT read reference files into the prompt** — agents read their own references from disk
- **Prior wave context is read, not generated** — agents read existing markdown for cross-domain context
- Use `subagent_type: "general-purpose"` for all spawned agents
- Report progress after each wave completes
