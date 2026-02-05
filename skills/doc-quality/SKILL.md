# doc-quality

## Description
Generates code quality documentation: static analysis configuration, dependency analysis, complexity metrics, tech debt assessment, and improvement recommendations. Runs as Wave 4 — assessment phase that synthesizes findings from all prior waves into prioritized recommendations. Reads all prior wave output to ground recommendations in the actual documented architecture, APIs, data flows, security posture, and testing strategy.

## Context
fork

## Instructions

### Inputs
1. Read `docs/.doc-plan.json` — verify `doc-quality` is enabled
2. Read `docs/.doc-manifest.json` — get files under `doc-quality.files`
3. Read assigned source files in batches of 5-8 to stay within context limits
4. Read prior wave output for complete system context (do not regenerate):
   - Wave 1: `docs/md/arch-overview.md` (system overview and design principles), `docs/md/arch-c4-level2.md` (container diagram)
   - Wave 2: `docs/md/api-index.md`, `docs/md/data-overview.md`, `docs/md/events-overview.md` (read whichever exist)
   - Wave 3: `docs/md/security-overview.md` (security posture), `docs/md/devops-overview.md` (deployment and infra), `docs/md/testing-overview.md` (testing strategy and coverage)
   Use these to synthesize cross-domain recommendations. For example: 'add integration tests for the payment endpoint's DynamoDB writes' requires knowing the API surface (Wave 2), data access patterns (Wave 2), and testing gaps (Wave 3).

### Analysis Steps
1. **Static analysis tools** — identify configured tools: linters (ESLint, Pylint, Flake8, RuboCop, Checkstyle, PMD, SpotBugs), formatters (Prettier, Black, gofmt), type checkers (TypeScript strict, mypy, Sorbet), security scanners (Snyk, OWASP Dep Check, Trivy, Bandit), quality platforms (SonarQube, CodeClimate). Document config: rules enabled/disabled, severity levels, custom rules.
2. **Dependency analysis** — from build/package files: count direct vs transitive deps, flag outdated/deprecated packages, check for duplicates/conflicts, note management strategy (pinned, ranges, lockfiles).
3. **Code pattern assessment** — assess: style/pattern consistency, error handling patterns, logging practices, config management approach, dead code indicators (unused imports, commented-out code).
4. **Tech debt indicators** — search for: TODO/FIXME/HACK/XXX comments (count via Grep), suppressed warnings (@SuppressWarnings, eslint-disable, # type: ignore), deprecated API usage, large files (god classes), deep nesting.

### Output Files
All files go to `docs/md/`.

**`quality-overview.md`** — Frontmatter: title "Code Quality Overview", section "Quality", order 1, generated "{{DATE}}". Content: quality toolchain summary table, dependency summary (total, direct vs transitive), tech debt indicators summary, quality score/assessment, links to detail pages.

**`quality-recommendations.md`** — Frontmatter: title "Quality Recommendations", section "Quality", order 2, generated "{{DATE}}". Content: prioritized improvements, dependency update recommendations, tool config suggestions, tech debt items by severity (critical/high/medium/low), code pattern improvements. Format each as: severity tag, description, impact, current state, recommendation, relevant files.

### Rules
- TODO/FIXME counts must come from actual Grep results, not estimates
- Dependency counts must be from actual build/package files
- Recommendations must be specific and actionable
- Reference specific files and line patterns for every finding
- Be objective -- document what IS, not what you think SHOULD be
- Clearly distinguish facts (configs found) from assessments (quality judgment)

## Tools
- Read
- Glob
- Grep
- Write

## Output
Markdown files in `docs/md/`:
- `quality-overview.md`
- `quality-recommendations.md`
