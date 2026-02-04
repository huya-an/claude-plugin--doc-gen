# /doc-update — Incremental Documentation Update

Update documentation for only the sections affected by recent code changes.

## Instructions

You are running the `/doc-update` command — incremental documentation updates.

### Prerequisites

Check all of these exist:
- `docs/.doc-plan.json` (run `/doc` first)
- `docs/.doc-manifest.json` (run `/doc` first)
- `docs/md/*.md` files (run `/doc-generate` first)

Also verify this is a git repository (`git rev-parse --is-inside-work-tree`).

If any prerequisite fails, tell the user what to run first and stop.

### Step 1: Determine Change Scope

Use AskUserQuestion to ask what changes to consider:
1. "Uncommitted changes" — `git diff --name-only` + `git diff --name-only --cached`
2. "Last commit" — `git diff --name-only HEAD~1`
3. "Last N commits" — ask for N, then `git diff --name-only HEAD~N`
4. "Custom range" — ask for commit range

Run the appropriate git command to get the list of changed files.

If no files changed, tell the user "No changes found" and stop.

### Step 2: Map Changes to Sections

Read `docs/.doc-manifest.json` for the current file-to-section mapping.

Use these patterns to map changed files to documentation sections:

| Changed File Pattern | Affected Sections |
|---|---|
| `*Controller*`, `*Resource*`, `*Route*`, route handlers | `doc-api`, `doc-c4` |
| `*Service*`, `*UseCase*`, `*Interactor*` | `doc-c4`, `doc-api` |
| `*Entity*`, `*Model*`, `*Schema*`, `*Migration*` | `doc-data`, `doc-c4` |
| `*Repository*`, `*DAO*`, `*Store*` | `doc-data`, `doc-c4` |
| `*Event*`, `*Listener*`, `*Consumer*`, `*Producer*` | `doc-events` |
| `*Security*`, `*Auth*`, `*Filter*`, `*Guard*` | `doc-security` |
| `*Test*`, `*Spec*`, `*test*`, `*spec*` | `doc-testing` |
| `Dockerfile*`, `.github/workflows/*`, `*.tf`, CI configs | `doc-devops` |
| `pom.xml`, `build.gradle*`, `package.json`, deps | `doc-quality`, `doc-c4` |
| `**/adr/*`, `**/decisions/*`, `*ADR*` | `doc-adr` |
| `.eslintrc*`, `.prettierrc*`, quality configs | `doc-quality` |

Also check: if a changed file appears in any section's file list in the manifest, that section is affected.

Only include sections that are `enabled: true` in the plan.

### Step 3: Present Update Plan

```
Incremental Update Plan
========================
Changed files: {count}
{list each changed file}

Affected sections:
  [checkmark] Architecture (C4) — {reason}
  [checkmark] API Plane — {reason}
  [dash] Security — no changes
  [dash] DevOps — no changes
  ...

Pages to rebuild: ~{count} of {total}
```

If more than 50% of sections are affected, suggest: "Most sections are affected. Consider running /doc-generate + /doc-site for a full rebuild instead."

Use AskUserQuestion to get approval.

### Step 4: Locate Plugin Skills

Use Glob to find the plugin skills directory (same as doc-generate):
```
Glob: **/doc-gen/skills/doc-c4/SKILL.md
```
If not found locally, check the plugin cache:
```
Glob: ~/.claude/plugins/cache/**/doc-gen/**/doc-c4/SKILL.md
```
Extract the base `SKILLS_DIR` path (the parent of `doc-c4/`).

### Step 5: Regenerate Affected Sections (Wave-Ordered)

Group affected sections by their wave assignment from the plan's `waves` object. Execute waves sequentially, parallel within each wave — same as `/doc-generate` but only for affected waves.

For each affected wave (in order 1 → 2 → 3 → 4):
1. For each affected section in this wave, read `{SKILLS_DIR}/{section_id}/SKILL.md`
2. Spawn Task agents (subagent_type: "general-purpose") **in parallel within the wave** with:

   ```
   You are a documentation agent regenerating {section_title} documentation.

   CONTEXT:
   - Read docs/.doc-plan.json and docs/.doc-manifest.json for your file assignments
   - Write output to docs/md/
   - If instructions reference "references/", read from: {SKILLS_DIR}/{section_id}/references/
   - Read source files in batches of 5-8. Keep output concise, no stubs.

   PRIOR WAVE CONTEXT (read these for system context, do not regenerate):
   {prior wave files — same as /doc-generate for this wave number}

   INSTRUCTIONS:
   {SKILL.md contents}
   ```

3. Wait for all agents in this wave to complete before starting the next wave

**Only execute waves that contain affected sections.** If only Wave 2 and Wave 3 sections are affected, skip Wave 1 and Wave 4. But if Wave 1 (doc-c4) is affected, it MUST complete before Wave 2+ agents start — they depend on its markdown output for context.

### Step 6: Rebuild HTML Site

Check if `docs/site/` exists. If it does:

1. Verify `mkdocs.yml` exists and mkdocs-drawio-plugin is installed
2. If navigation changed (sections added/removed), update `nav:` in `mkdocs.yml`
3. Run `mkdocs build` to rebuild the entire site
4. Verify output: count HTML pages, count `class="mxgraph"` embeds, check for unconverted Mermaid blocks

If `docs/site/` doesn't exist, skip HTML rebuild and suggest running `/doc-site`.

### Step 7: Run Validation

If HTML was rebuilt:
1. Read `{SKILLS_DIR}/doc-validate-site/SKILL.md`
2. Spawn a validation Task agent
3. Display results

### Step 8: Summary

```
Incremental Update Complete
=============================
Sections updated: {count}
Markdown files regenerated: {md_count}
HTML pages rebuilt: {html_count}
Validation: {PASS/FAIL}

Site location: docs/site/index.html
```

### Error Handling

- If git is not available, tell user and stop
- If no changes detected, tell user and stop
- If a domain agent fails, report error and continue with remaining sections
- If skills directory not found, tell user to verify plugin installation
