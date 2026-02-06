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

#### Generate Index Page with Codebase Grade

After all 4 waves complete, create `docs/md/index.md` — the documentation home page. **The codebase grade MUST be the very first content after the title.** It comes before section links.

Read these overview files (whichever exist) to synthesize grades:
- `docs/md/arch-overview.md` — architecture quality
- `docs/md/testing-overview.md` — testing maturity
- `docs/md/security-overview.md` — security posture
- `docs/md/devops-overview.md` — CI/CD and infrastructure
- `docs/md/quality-overview.md` — code quality and dependency health
- `docs/md/data-overview.md` — data layer design
- `docs/md/events-overview.md` — event architecture
- `docs/md/api-index.md` — API design

Also read `docs/.doc-plan.json` for the project name, language, and framework.

Write `docs/md/index.md` with this exact structure:

```markdown
---
title: "Home"
section: "Home"
order: 0
generated: "YYYY-MM-DD"
---

# {project_name} Documentation

Auto-generated technical documentation for the {project_name} project.

## Codebase Quality Grade: {OVERALL_GRADE}

### Overall Assessment

{1-2 paragraph synthesis of the codebase's overall quality based on all overview files. Be specific — reference actual patterns, tools, and metrics found in the generated documentation.}

### Scorecard

| Dimension | Grade | Rationale |
|---|---|---|
| **Architecture** | {grade} | {1-2 sentences based on arch-overview.md findings} |
| **Testing** | {grade} | {1-2 sentences based on testing-overview.md findings} |
| **Security** | {grade} | {1-2 sentences based on security-overview.md findings} |
| **CI/CD & DevOps** | {grade} | {1-2 sentences based on devops-overview.md findings} |
| **Code Quality** | {grade} | {1-2 sentences based on quality-overview.md findings} |
| **Dependency Health** | {grade} | {1-2 sentences based on quality-overview.md dependency analysis} |
| **Maintainability** | {grade} | {1-2 sentences — cross-domain synthesis} |

### Strengths

- {bullet points — specific, evidence-based strengths found across all domains}

### Areas for Improvement

1. {numbered list — specific, actionable improvements with file/metric references}

---

## Sections

### {Section Name}

{Brief description}

- [Page Title](page-file.md)
- ...

{repeat for each enabled section from the plan, grouped by domain}

---

*Generated on YYYY-MM-DD*
```

**Grading rules:**
- Use letter grades: A, A-, B+, B, B-, C+, C, C-, D, F
- The **overall grade** is a weighted synthesis, not a simple average. Architecture and Security weigh more heavily than Maintainability.
- Only include scorecard rows for dimensions that have corresponding generated documentation. If a domain was skipped (e.g., no events found), omit that row.
- Every grade must have a rationale grounded in evidence from the overview files. Never assign a grade without justification.
- Strengths and areas for improvement must reference specific findings — tool names, file counts, patterns, metrics, version numbers.
- Keep the overall assessment to 1-2 paragraphs max.

#### Markdown Validation

Read `{SKILLS_DIR}/doc-validate-md/SKILL.md`, spawn Task agent, display results.

### Step 3: Build Site — MkDocs Build

**CRITICAL: Always use `mkdocs build`. Never manually convert markdown to HTML.**

1. Verify `mkdocs.yml` exists and mkdocs is installed (`which mkdocs`)
2. Read frontmatter from all markdown files, generate `nav:` section for `mkdocs.yml`
3. Verify `docs/md/index.md` exists (should have been created with the codebase grade in the previous step). If missing, create it using the grade structure above.
4. Run `mkdocs build`
5. Verify output:
   - Count HTML pages
   - Count Mermaid blocks (`class="mermaid"`)
   - Check for legacy `<!-- diagram-meta` markers (CRITICAL if found)
6. Run site validation: read `{SKILLS_DIR}/doc-validate-site/SKILL.md`, spawn Task agent, display results

### Step 4: Ask About Publishing

Use AskUserQuestion:
- "Publish to S3?" with options:
  - "Yes — publish to S3"
  - "No — just local site"

If yes:
1. Check environment variables `$SITE_S3_BUCKET` and `$SITE_PROFILE`
2. If either is not set, use AskUserQuestion to prompt for them:
   - For bucket: "S3 bucket not configured. Please provide the bucket name:"
   - For profile: "AWS profile not configured. Which profile? (default, or enter name)"
3. Determine directory name from git repo name or current directory basename
4. Verify AWS CLI: `aws sts get-caller-identity --profile $SITE_PROFILE`
5. Upload: `aws s3 sync docs/site/ s3://$SITE_S3_BUCKET/{directory-name}/ --delete --profile $SITE_PROFILE`
6. Fix content types for .html, .css, .js files

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
{If published: S3: https://$SITE_S3_BUCKET.s3.amazonaws.com/{directory-name}/index.html}
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
