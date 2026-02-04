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

Follow the instructions from the `doc-discover/SKILL.md` file you just read. Execute them directly in your current session — do NOT try to invoke a separate skill. Specifically:

#### 3a: Detect Project Type

Use Glob to check for these markers (skip the `claude-doc-gen/` plugin directory itself and any `docs/` output directory):

| Marker File | Language/Framework |
|---|---|
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Java (Maven/Gradle) |
| `package.json` | JavaScript/TypeScript (Node.js) |
| `requirements.txt`, `setup.py`, `pyproject.toml`, `Pipfile` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `*.csproj`, `*.sln` | C# / .NET |
| `Gemfile` | Ruby |
| `mix.exs` | Elixir |
| `composer.json` | PHP |

Also check for framework-specific markers:
- `application.yml` / `application.properties` → Spring Boot
- `angular.json` → Angular
- `next.config.*` → Next.js
- `nuxt.config.*` → Nuxt.js
- `serverless.yml` / `serverless.ts` → Serverless Framework
- `cdk.json` → AWS CDK
- `terraform/` or `*.tf` → Terraform

#### 3b: Inventory by Category

Use Glob patterns to find files. Grep for key patterns if needed. DO NOT read full file contents — only use Glob and Grep. Exclude `node_modules/`, `vendor/`, `.git/`, `docs/`, `claude-doc-gen/` from all searches.

**Controllers / Routes → feeds `doc-api`**
```
Glob: **/*Controller*, **/*Resource*, **/routes/*, **/router/*, **/*Endpoint*
Grep patterns: @RestController, @RequestMapping, @GetMapping, @PostMapping, app.get(, app.post(, router.get(, @app.route
```

**Services / Business Logic → feeds `doc-c4`**
```
Glob: **/*Service*, **/*UseCase*, **/*Interactor*, **/*Manager*, **/*Facade*
```

**Entities / Models / Migrations → feeds `doc-data`**
```
Glob: **/*Entity*, **/*Model*, **/*Schema*, **/*Migration*, **/*migration*, **/entities/*, **/models/*, **/domain/*
Grep patterns: @Entity, @Table, @Column, Schema.define, class.*Model, CREATE TABLE
```

**Event Handlers / Async Triggers → feeds `doc-events`**
```
Message-driven:
  Glob: **/*Event*, **/*Listener*, **/*Consumer*, **/*Producer*, **/*Publisher*, **/*Subscriber*
  Grep patterns: @EventListener, @KafkaListener, @SqsListener, @RabbitListener, EventEmitter, on(', subscribe(, Redpanda, rdkafka
Schedule-driven:
  Grep patterns: @Scheduled, cron(, schedule(, setInterval, rate(, CloudWatch Events, EventBridge Schedule
Cloud-event-driven:
  Grep patterns: S3Event, S3Handler, s3:ObjectCreated, DynamoDBStreamHandler, dynamodb:stream, SNSEvent
Webhook receivers:
  Grep patterns: /webhook, /hook, /callback, hmac, signature, x-hub-signature
```

**Security Configs → feeds `doc-security`**
```
Glob: **/*Security*, **/*Auth*, **/*Filter*, **/*Guard*, **/*Middleware*, **/*Permission*, **/*Role*
Grep patterns: @EnableWebSecurity, SecurityFilterChain, passport, jwt, bcrypt, OAuth, CORS
```

**Test Suites → feeds `doc-testing`**
```
Glob: **/*Test*, **/*Spec*, **/*test*, **/*spec*, **/__tests__/*, **/test/*
Also: jest.config*, pytest.ini, .nycrc, karma.conf*, codecov.yml
```

**CI/CD + Docker + IaC → feeds `doc-devops`**
```
Glob: Dockerfile*, docker-compose*, .github/workflows/*, .gitlab-ci.yml, Jenkinsfile, .circleci/*, buildspec.yml
Glob: **/terraform/*, **/cdk/*, **/cloudformation/*, **/ansible/*, **/helm/*, k8s/*, kubernetes/*, *.tf
```

**ADR Documents → feeds `doc-adr`**
```
Glob: **/adr/*, **/decisions/*, **/ADR*, **/*adr*
Grep: "## Status", "## Decision", "## Context" (in markdown files)
```

**Quality / Config → feeds `doc-quality`**
```
Glob: .eslintrc*, .prettierrc*, sonar-project.properties, .editorconfig, tslint.json, .rubocop.yml
Glob: pom.xml, build.gradle*, package.json (for dependency analysis)
```

#### 3c: Build Documentation Plan

For each category, count the files found. Create a plan with sections:
- `id`: section identifier (e.g., "doc-c4", "doc-api")
- `title`: human-readable title
- `enabled`: true if relevant files found, false if zero files
- `wave`: execution wave (1-4) — determines when this section runs relative to others
- `file_count`: number of source files
- `output_files`: list of markdown files to generate

**Wave assignments (fixed):**
- Wave 1: `doc-c4` (system map — everything else depends on this)
- Wave 2: `doc-api`, `doc-data`, `doc-events` (horizontal concerns, parallel)
- Wave 3: `doc-security`, `doc-devops`, `doc-testing` (cross-cutting, reads Wave 1-2 output)
- Wave 4: `doc-adr`, `doc-quality` (assessment, reads all prior waves)

Output files per section:
- **doc-c4**: `arch-overview.md`, `arch-c4-level1.md`, `arch-c4-level2.md`, `arch-c4-level3-{name}.md` (one per major container), `arch-c4-level4.md`
- **doc-api**: `api-index.md` + one `api-{method}-{path-slug}.md` per endpoint
- **doc-adr**: `adr-index.md` + one `adr-NNN.md` per ADR
- **doc-security**: `security-overview.md`, `security-auth.md`, `security-threats.md`
- **doc-devops**: `devops-overview.md`, `devops-cicd.md`, `devops-infra.md`
- **doc-data**: `data-overview.md`, `data-schema.md`, `data-pipelines.md`
- **doc-events**: `events-overview.md`, `events-catalog.md`, `events-flows.md`
- **doc-testing**: `testing-overview.md`, `testing-strategy.md`
- **doc-quality**: `quality-overview.md`, `quality-recommendations.md`

#### 3d: Present Plan to User

Display the plan as a formatted table grouped by wave:

```
Documentation Plan for: {project_name}
Detected: {language} / {framework}

| Wave | Section | Files | Pages | Status |
|------|---------|-------|-------|--------|
| 1 | Architecture (C4) | 45 | 6 | Enabled |
| 2 | API Plane | 23 | 12 | Enabled |
| 2 | Data / DBA | 15 | 3 | Enabled |
| 2 | Events & Async | 0 | 0 | Skipped (no async triggers found) |
| 3 | Security | 8 | 3 | Enabled |
| 3 | DevOps | 12 | 3 | Enabled |
| 3 | Testing | 34 | 2 | Enabled |
| 4 | ADRs | 5 | 6 | Enabled |
| 4 | Quality | 6 | 2 | Enabled |

Total: ~8 sections, ~37 pages (4 execution waves)
```

Use AskUserQuestion to get approval. Allow the user to disable/enable sections.

#### 3e: Save Plan Files

After approval, create `docs/` directory if needed (`mkdir -p docs`).

**Locate the references directory**: Use the same path where you found `doc-discover/SKILL.md`:
- `{SKILLS_DIR}/doc-discover/references/`

If not found, use Glob: `**/doc-discover/references/plan-template.json`

**Write `docs/.doc-plan.json`**:

Read `{SKILLS_DIR}/doc-discover/references/plan-template.json` — this contains the required JSON structure with all 9 sections, correct `"wave"` values, and the `"waves"` object. Use it as the basis for your output. Fill in:
- `project_name`, `language`, `framework`, `generated` (today's date)
- For each section: `enabled`, `file_count`, `output_files`
- Update the `"waves"` object to only include enabled section IDs

**Write `docs/.doc-manifest.json`**:

For each enabled section, list the source files and batch size. Disabled sections can have empty arrays. Group files so no section gets more than ~30 files.

#### 3f: Validate Plan JSON (MANDATORY)

Run the schema validator script. This is a **blocking requirement** — you must not proceed until the validator passes.

```bash
python3 {SKILLS_DIR}/doc-discover/references/validate-plan.py docs/.doc-plan.json
```

If you can't find the script, use Glob: `**/doc-discover/references/validate-plan.py`

**If the validator outputs `FAIL`:**
1. Read the error messages — they tell you exactly what's wrong
2. Use Edit to fix each error in `docs/.doc-plan.json`
3. Run the validator again
4. Repeat until the output is `PASS`

**You MUST NOT proceed to the next step until the validator prints `PASS`.** This is not optional. Do not skip this step.

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
