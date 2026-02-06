# /doc-generate — Generate Markdown Documentation

Generate markdown documentation for all approved sections using forked agents in wave-based execution order.

## Instructions

You are running the `/doc-generate` command — Phase 1 of documentation generation.

**This command spawns forked agents in 6 sequential waves. Each wave waits for the previous wave to fully complete before starting. Domains within a wave run in parallel.**

### Prerequisites

Read `docs/.doc-plan.json` and `docs/.doc-manifest.json`. If either file doesn't exist, tell the user to run `/doc` first and stop.

Validate the plan has a `waves` object. If missing, **fix it yourself** — do NOT tell the user to re-run `/doc`. Instead:
1. Add the `"waves"` object using the wave assignments from Step 1 below (only include enabled section IDs)
2. If sections have `"priority"` instead of `"wave"`, rename the field and set the correct wave number
3. Write the fixed plan back to `docs/.doc-plan.json`

### Step 1: Display Plan

Read `docs/.doc-plan.json`. Show enabled sections grouped by wave:

```
Documentation Generation Plan
==============================

Wave 1 (Foundation):
  - doc-c4: Architecture (C4) — {n} files → {n} pages

Wave 2 (Horizontal):
  - doc-api: API Plane — {n} files → {n} pages
  - doc-data-discover: Data Discovery — {n} files → manifest
  - doc-events: Events & Async — {n} files → {n} pages

Wave 3 (Data Tables):
  - doc-data-tables: Data Tables — reads manifest → 1 page per table

Wave 4 (Data Queries):
  - doc-data-queries: Data Queries — reads manifest → 1 page per query

Wave 5 (Cross-Cutting):
  - doc-security: Security — {n} files → {n} pages
  - doc-devops: DevOps — {n} files → {n} pages
  - doc-testing: Testing — {n} files → {n} pages
  - doc-data-overview: Data Overviews — reads table/query pages → rollup pages

Wave 6 (Assessment):
  - doc-adr: ADRs — {n} files → {n} pages
  - doc-quality: Quality — {n} files → {n} pages

Starting generation...
```

Skip any section with `"enabled": false`.

### Step 2: Create Output Directory

Run: `mkdir -p docs/md`

### Step 3: Locate Plugin Skills

Use Glob to find the skills directory:
```
Glob: **/doc-gen/skills/doc-c4/SKILL.md
```
If not found locally, check the plugin cache:
```
Glob: ~/.claude/plugins/cache/**/doc-gen/**/doc-c4/SKILL.md
```

Extract the base path (everything before `doc-c4/SKILL.md`) — this is `SKILLS_DIR`.

### Step 4: Execute Waves

Execute waves sequentially: Wave 1 → Wave 2 → Wave 3 → Wave 4 → Wave 5 → Wave 6. Within each wave, spawn all enabled sections in parallel (up to 3 concurrent agents).

**CRITICAL: Each wave MUST fully complete before the next wave starts.** Later waves depend on earlier wave output.

For each wave, read the SKILL.md for every enabled section in that wave and spawn Task agents with this template:

```
You are a documentation agent generating {section_title} documentation.

CONTEXT:
- Read docs/.doc-plan.json and docs/.doc-manifest.json to find your assigned files
- Write all output markdown to docs/md/
- If your instructions reference files in a "references/" directory, read them from: {SKILLS_DIR}/{section_id}/references/
- If your instructions reference shared references (e.g., ../references/), read them from: {SKILLS_DIR}/references/
- Read source files in batches of 5-8 at a time to stay within context limits
- Keep output concise. Do not generate placeholder or stub content.

{PRIOR_WAVE_CONTEXT}

INSTRUCTIONS:
{contents of SKILL.md}
```

Use `subagent_type: "general-purpose"` for all spawned agents.

#### Prior Wave Context by Wave

**Wave 1** — No prior context. Omit the PRIOR_WAVE_CONTEXT block.

**Wave 2** — C4 architecture establishes the system map:
```
PRIOR WAVE CONTEXT (read these for system context, do not regenerate them):
- docs/md/arch-overview.md — system overview from C4 analysis
- docs/md/arch-c4-level1.md — system context diagram
- docs/md/arch-c4-level2.md — container diagram
Reading these gives you the system map established in Wave 1. Reference it for component names, boundaries, and relationships.
```

**Wave 3** — Data manifest is now available from Wave 2:
```
PRIOR WAVE CONTEXT (read these for system context, do not regenerate them):
- docs/md/arch-overview.md — system overview
- docs/md/arch-c4-level2.md — container diagram
- docs/.data-manifest.json — data inventory from doc-data-discover (your primary input)
```

**Wave 4** — Table pages are now available from Wave 3:
```
PRIOR WAVE CONTEXT (read these for system context, do not regenerate them):
- docs/md/arch-overview.md — system overview
- docs/md/arch-c4-level2.md — container diagram
- docs/.data-manifest.json — data inventory from doc-data-discover (your primary input)
- docs/md/data--*--tables--*.md — table pages from doc-data-tables (for cross-referencing)
- docs/md/api-index.md — API endpoint summary (for query-to-API cross-references)
```

**Wave 5** — All domain content is available for cross-cutting analysis:
```
PRIOR WAVE CONTEXT (read these for cross-domain context, do not regenerate them):
Wave 1 output:
- docs/md/arch-overview.md — system overview
- docs/md/arch-c4-level2.md — container diagram (component names and boundaries)
Wave 2 output (read whichever exist):
- docs/md/api-index.md — API endpoint summary
- docs/.data-manifest.json — data inventory
- docs/md/events-overview.md — async trigger summary
Wave 3-4 output (read whichever exist):
- docs/md/data--*--tables--*.md — all table pages (for doc-data-overview rollup)
- docs/md/data--*--queries--*.md — all query pages (for doc-data-overview rollup)
These give you the full system picture from Waves 1-4. Reference component names, endpoints, data stores, and event flows as established in prior waves.
```

**Wave 6** — Everything is available for synthesis:
```
PRIOR WAVE CONTEXT (read these for full system context, do not regenerate them):
Wave 1 output:
- docs/md/arch-overview.md — system overview and design principles
- docs/md/arch-c4-level2.md — container diagram
Wave 2 output (read whichever exist):
- docs/md/api-index.md — API endpoint summary
- docs/md/data--overview.md — data layer summary
- docs/md/events-overview.md — async trigger summary
Wave 5 output (read whichever exist):
- docs/md/security-overview.md — security posture summary
- docs/md/devops-overview.md — deployment and infrastructure summary
- docs/md/testing-overview.md — testing strategy and coverage summary
These give you the complete system picture from all prior waves. Use this for synthesis and cross-domain analysis.
```

Report progress after each wave completes so the user can monitor execution.

### Step 5: Generate Index Page with Codebase Grade

After all 6 waves complete, create `docs/md/index.md` — the documentation home page. **The codebase grade MUST be the very first content after the title.** It comes before section links.

Read these overview files (whichever exist) to synthesize grades:
- `docs/md/arch-overview.md` — architecture quality
- `docs/md/testing-overview.md` — testing maturity
- `docs/md/security-overview.md` — security posture
- `docs/md/devops-overview.md` — CI/CD and infrastructure
- `docs/md/quality-overview.md` — code quality and dependency health
- `docs/md/data--overview.md` — data layer design
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

### Step 6: Run Validation

After index and all wave files are complete:
1. Read `{SKILLS_DIR}/doc-validate-md/SKILL.md`
2. Spawn a Task agent with those instructions to validate all files in `docs/md/*.md`
3. Display validation results

### Step 7: Summary

Count files in `docs/md/` with Glob. Display:

```
Markdown Generation Complete
==============================

Wave 1 (C4 Architecture): ✓ {n} files
Wave 2 (API / Data Discovery / Events): ✓ {n} files
Wave 3 (Data Tables): ✓ {n} files
Wave 4 (Data Queries): ✓ {n} files
Wave 5 (Security / DevOps / Testing / Data Overviews): ✓ {n} files
Wave 6 (ADR / Quality): ✓ {n} files
Index (Codebase Grade): ✓ index.md

Total: {total} markdown files in docs/md/
Validation: {pass/fail with details}

Next step: Run /doc-site to build the static HTML site
```

### Error Handling

- If an agent fails within a wave, report the error and continue with remaining agents in that wave
- **A failed agent does NOT block the next wave.** Later-wave agents simply have less context from the failed domain — they still function.
- If the skills directory is not found, tell user to verify plugin installation
- If `.doc-plan.json` has no `waves` object, tell user to re-run `/doc` to regenerate with wave assignments

### Important Rules

- **Wave ordering is mandatory**: Never spawn Wave N+1 agents before Wave N fully completes
- **Do NOT read reference files into the prompt** — agents read their own references from disk as needed. Only include the SKILL.md contents.
- **Prior wave context is read, not generated** — agents read existing markdown from `docs/md/` for cross-domain context. They never regenerate content from prior waves.
- Use `subagent_type: "general-purpose"` for all spawned agents
- Report progress after each wave completes so the user can monitor execution
