# doc-discover

## Description
Scans a codebase and builds a documentation plan. This is the first step in documentation generation — it inventories the project structure, detects languages/frameworks, categorizes source files by documentation domain, and produces a plan for user approval.

## Context
fork

## Instructions

You are the **Discovery Agent** for the documentation generator. Your job is to scan the codebase structure and produce a documentation plan. You must be fast and lightweight — use only Glob and Grep, never read entire source files.

### Step 1: Detect Project Type

Use Glob to check for these markers:

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

### Step 2: Inventory by Category

Use Glob patterns to find files. Grep for key patterns if needed, but DO NOT read file contents.

#### Controllers / Routes → feeds `doc-api`
```
Glob: **/*Controller*, **/*Resource*, **/routes/*, **/router/*, **/*Handler*, **/*Endpoint*
Grep patterns: @RestController, @RequestMapping, @GetMapping, @PostMapping, app.get(, app.post(, router.get(, @app.route
```

#### Services / Business Logic → feeds `doc-c4`
```
Glob: **/*Service*, **/*UseCase*, **/*Interactor*, **/*Manager*, **/*Facade*
```

#### Entities / Models / Migrations → feeds `doc-data`
```
Glob: **/*Entity*, **/*Model*, **/*Schema*, **/*Migration*, **/*migration*, **/entities/*, **/models/*, **/domain/*
Grep patterns: @Entity, @Table, @Column, Schema.define, class.*Model, CREATE TABLE
```

#### Event Handlers / Async Triggers → feeds `doc-events`
```
Message-driven:
  Glob: **/*Event*, **/*Listener*, **/*Consumer*, **/*Producer*, **/*Publisher*, **/*Subscriber*, **/*Handler*
  Grep patterns: @EventListener, @KafkaListener, @SqsListener, @RabbitListener, EventEmitter, on(', subscribe(, Redpanda, rdkafka

Schedule-driven:
  Grep patterns: @Scheduled, cron(, schedule(, setInterval, rate(, CloudWatch Events, EventBridge Schedule

Cloud-event-driven:
  Grep patterns: S3Event, S3Handler, s3:ObjectCreated, DynamoDBStreamHandler, dynamodb:stream, SNSEvent, SESEvent

Webhook receivers:
  Grep patterns: /webhook, /hook, /callback, hmac, signature, x-hub-signature
```

#### Security Configs → feeds `doc-security`
```
Glob: **/*Security*, **/*Auth*, **/*Filter*, **/*Guard*, **/*Middleware*, **/*Permission*, **/*Role*
Grep patterns: @EnableWebSecurity, SecurityFilterChain, passport, jwt, bcrypt, OAuth, CORS
```

#### Test Suites → feeds `doc-testing`
```
Glob: **/*Test*, **/*Spec*, **/*test*, **/*spec*, **/__tests__/*, **/test/*
Also: jest.config*, pytest.ini, .nycrc, karma.conf*, codecov.yml
```

#### CI/CD + Docker + IaC → feeds `doc-devops`
```
Glob: Dockerfile*, docker-compose*, .github/workflows/*, .gitlab-ci.yml, Jenkinsfile, .circleci/*, buildspec.yml
Glob: **/terraform/*, **/cdk/*, **/cloudformation/*, **/ansible/*, **/helm/*
Glob: k8s/*, kubernetes/*, *.tf
```

#### ADR Documents → feeds `doc-adr`
```
Glob: **/adr/*, **/decisions/*, **/ADR*, **/*adr*
Grep: "## Status", "## Decision", "## Context" (in markdown files)
```

#### Quality / Config → feeds `doc-quality`
```
Glob: .eslintrc*, .prettierrc*, sonar-project.properties, .editorconfig, tslint.json, .rubocop.yml
Glob: pom.xml, build.gradle*, package.json (for dependency analysis)
```

### Step 3: Build File Manifest

Create a mapping of which source files each documentation agent needs to read. Group files so no single agent gets more than ~30 files. If a category has too many files, split into sub-batches.

### Step 4: Build Documentation Plan

Create a plan with sections to generate. Each section has:
- `id`: skill name (e.g., "doc-c4", "doc-api")
- `title`: human-readable title
- `enabled`: boolean (true if relevant files found)
- `wave`: execution wave (1-4) — determines when this section runs
- `file_count`: number of source files to analyze
- `output_files`: list of markdown files to generate

**Wave assignments (fixed — do not change these):**

| Wave | Sections | Why |
|------|----------|-----|
| 1 | `doc-c4` | Establishes the system map. All other domains reference this. |
| 2 | `doc-api`, `doc-data`, `doc-events` | Horizontal concerns traced across the system map. Independent of each other. |
| 3 | `doc-security`, `doc-devops`, `doc-testing` | Cross-cutting analysis. Reads Wave 1-2 markdown for context. |
| 4 | `doc-adr`, `doc-quality` | Assessment and synthesis. Reads all prior wave output. |

Skip sections that have zero relevant files.

### Step 5: Present Plan to User

Display the plan as a formatted table grouped by wave:

```
Documentation Plan for: {project_name}
Detected: {language} / {framework}

| Wave | Section | Files | Pages | Status |
|------|---------|-------|-------|--------|
| 1 | Architecture (C4) | 45 | 6 | Enabled |
| 2 | API Plane | 23 | 12 | Enabled |
| 2 | Data / DBA | 15 | 4 | Enabled |
| 2 | Events & Async | 0 | 0 | Skipped (no async triggers found) |
| 3 | Security | 8 | 3 | Enabled |
| 3 | DevOps | 12 | 3 | Enabled |
| 3 | Testing | 34 | 2 | Enabled |
| 4 | ADRs | 5 | 6 | Enabled |
| 4 | Quality | 6 | 2 | Enabled |

Total: ~8 sections, ~38 pages (4 execution waves)

Proceed with this plan? (You can disable sections or adjust)
```

Use AskUserQuestion to get approval. Allow the user to disable/enable sections.

### Step 6: Save Plan Files

After approval, create `docs/` directory if needed (`mkdir -p docs`).

#### 6a: Read the template

Read `{SKILLS_DIR}/doc-discover/references/plan-template.json` (where `SKILLS_DIR` is the path where you found this SKILL.md). This template contains the required JSON structure with all 9 sections, correct `"wave"` values, and the `"waves"` object. Use it as the basis for your output.

#### 6b: Write `docs/.doc-plan.json`

Write the plan JSON to `docs/.doc-plan.json`. Fill in:
- `project_name`, `language`, `framework`, `generated` (today's date)
- For each section: `enabled`, `file_count`, `output_files`
- Update the `"waves"` object to only include enabled section IDs

Keep the structure from the template: every section must have a `"wave"` field (integer 1-4), and the top level must have a `"waves"` object.

#### 6c: Write `docs/.doc-manifest.json`

Write the manifest JSON. For each enabled section, list the source files and batch size. Disabled sections can have empty arrays. Group files so no section gets more than ~30 files.

### Step 7: Validate Plan JSON (MANDATORY)

Run the schema validator. This is a **blocking requirement** — you must not proceed until the validator passes.

```
python3 {SKILLS_DIR}/doc-discover/references/validate-plan.py docs/.doc-plan.json
```

If you can't find the script, use Glob: `**/doc-discover/references/validate-plan.py`

**If the validator outputs `FAIL`:**
1. Read the error messages — they tell you exactly what's wrong
2. Use Edit to fix each error in `docs/.doc-plan.json`
3. Run the validator again
4. Repeat until the output is `PASS`

**You MUST NOT proceed to the next step until the validator prints `PASS`.** This is not optional. Do not skip this step.

### Important Rules

1. **Never read full source files** — only use Glob for file discovery and Grep for pattern matching
2. **Be conservative with estimates** — it's better to include a section and find nothing than to skip it
3. **Respect user choices** — if they disable a section, mark it `enabled: false`
4. **Handle monorepos** — if multiple projects detected, ask user which to document
5. **Files should appear in at most 2-3 sections** — a Service file might feed both doc-c4 and doc-api, but not every section
6. **The plan JSON MUST include `"wave"` on every section and a top-level `"waves"` object** — downstream commands depend on these exact field names

## Tools
- Glob
- Grep
- Read
- Write
- Edit
- Bash
- AskUserQuestion

## Output
Two JSON files in `docs/` directory:
- `.doc-plan.json` — the approved documentation plan
- `.doc-manifest.json` — file-to-section mapping
