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
| `build.zig` | Zig |

Also check for framework-specific markers:

**Java/JVM:**
- `application.yml` / `application.properties` → Spring Boot
- `quarkus.properties` / `application.properties` + `io.quarkus` → Quarkus

**JavaScript/TypeScript:**
- `angular.json` → Angular
- `next.config.*` → Next.js
- `nuxt.config.*` → Nuxt.js
- `vite.config.*` → Vite
- `remix.config.*` → Remix

**Rust:**
- Grep `Cargo.toml` for `actix-web` → Actix-web
- Grep `Cargo.toml` for `axum` → Axum
- Grep `Cargo.toml` for `rocket` → Rocket
- Grep `Cargo.toml` for `warp` → Warp
- Grep `Cargo.toml` for `tokio` → Async runtime (Tokio)
- Grep `Cargo.toml` for `diesel` or `sqlx` or `sea-orm` → ORM/DB layer

**Python:**
- Grep `requirements.txt` or `pyproject.toml` for `django` → Django
- Grep for `fastapi` → FastAPI
- Grep for `flask` → Flask

**Go:**
- Grep `go.mod` for `gin-gonic` → Gin
- Grep for `gorilla/mux` → Gorilla
- Grep for `echo` → Echo

**Infrastructure:**
- `serverless.yml` / `serverless.ts` → Serverless Framework
- `cdk.json` → AWS CDK
- `terraform/` or `*.tf` → Terraform
- `pulumi.*` → Pulumi

### Step 2: Inventory by Category

Use Glob patterns to find files. Grep for key patterns if needed, but DO NOT read file contents.

**Exclude from all searches:** `node_modules/`, `vendor/`, `.git/`, `target/`, `dist/`, `build/`, `docs/`, `claude-doc-gen/`, `__pycache__/`

#### Controllers / Routes → feeds `doc-api`
```
Glob: **/*Controller*, **/*Resource*, **/routes/*, **/router/*, **/*Handler*, **/*Endpoint*
Grep patterns:
  Java: @RestController, @RequestMapping, @GetMapping, @PostMapping, @PutMapping, @DeleteMapping
  JS/TS: app.get(, app.post(, router.get(, router.post(, @Controller, @Get(, @Post(
  Python: @app.route, @router.get, @router.post, @api_view
  Rust: #[get(, #[post(, .route(, .resource(, web::get, web::post, HttpResponse
  Go: http.HandleFunc, r.HandleFunc, e.GET, e.POST, gin.Context
```

#### Services / Business Logic → feeds `doc-c4`
```
Glob: **/*Service*, **/*UseCase*, **/*Interactor*, **/*Manager*, **/*Facade*, **/*Orchestrator*
Also: src/main/**/*, src/**/lib.rs, src/**/main.rs (entry points for C4 system boundary)
```

#### Entities / Models / Migrations → feeds `doc-data`
```
Glob: **/*Entity*, **/*Model*, **/*Schema*, **/*Migration*, **/*migration*, **/entities/*, **/models/*, **/domain/*
Grep patterns:
  Java: @Entity, @Table, @Column, @Id, @ManyToOne, @OneToMany
  Rust: #[derive(.*Queryable.*)]  , diesel::table!, #[derive(.*FromRow.*)]
  JS/TS: Schema.define, @Entity(), @Column(), model.define
  Python: class.*Model, db.Column, models.Model
  SQL: CREATE TABLE, ALTER TABLE
Also: **/migrations/*, **/flyway/*, **/alembic/*, **/prisma/schema.prisma
```

#### Event Handlers / Async Triggers → feeds `doc-events`
```
Message-driven:
  Glob: **/*Event*, **/*Listener*, **/*Consumer*, **/*Producer*, **/*Publisher*, **/*Subscriber*, **/*Handler*
  Grep patterns:
    Java: @EventListener, @KafkaListener, @SqsListener, @RabbitListener
    Rust: rdkafka, lapin, async-nats, Redpanda
    JS/TS: EventEmitter, on(', subscribe(, @EventPattern, @MessagePattern
    Go: sarama, confluent-kafka, amqp

Schedule-driven:
  Grep patterns: @Scheduled, cron(, schedule(, setInterval, rate(, CloudWatch Events, EventBridge

Cloud-event-driven:
  Grep patterns: S3Event, S3Handler, s3:ObjectCreated, DynamoDBStreamHandler, SNSEvent, SESEvent

Webhook receivers:
  Grep patterns: /webhook, /hook, /callback, hmac, signature, x-hub-signature
```

#### Security Configs → feeds `doc-security`
```
Glob: **/*Security*, **/*Auth*, **/*Filter*, **/*Guard*, **/*Middleware*, **/*Permission*, **/*Role*, **/*Policy*
Grep patterns:
  Java: @EnableWebSecurity, SecurityFilterChain, OncePerRequestFilter, @PreAuthorize
  Rust: actix-web-httpauth, jsonwebtoken, argon2, tower-http::cors
  JS/TS: passport, jwt, bcrypt, OAuth, CORS, helmet
  Go: middleware, jwt-go, casbin
  Python: django.contrib.auth, flask-login, fastapi.security
```

#### Test Suites → feeds `doc-testing`
```
Glob: **/*Test*, **/*Spec*, **/*test*, **/*spec*, **/__tests__/*, **/test/*, **/tests/*
Also: jest.config*, pytest.ini, .nycrc, karma.conf*, codecov.yml, .coveragerc, tarpaulin.toml
Exclude: node_modules/*, vendor/*
```

#### CI/CD + Docker + IaC → feeds `doc-devops`
```
Glob: Dockerfile*, docker-compose*, .github/workflows/*, .gitlab-ci.yml, Jenkinsfile, .circleci/*, buildspec.yml
Glob: **/terraform/*, **/cdk/*, **/cloudformation/*, **/ansible/*, **/helm/*
Glob: k8s/*, kubernetes/*, *.tf, azure-pipelines.yml, .azure-pipelines/*
Glob: task-definition*.json, appspec.yml, ecs-params.yml
```

#### ADR Documents → feeds `doc-adr`
```
Glob: **/adr/*, **/decisions/*, **/ADR*, **/*adr*, **/doc/architecture/*
Grep: "## Status", "## Decision", "## Context" (in markdown files)
```

**Note:** `doc-adr` should almost always be enabled, even when zero ADR files are found. The agent infers architectural decisions from prior wave output (tech stack choices, data store selections, architecture patterns). Only skip if the project is trivially small (e.g., a single-file utility).

#### Quality / Config → feeds `doc-quality`
```
Glob: .eslintrc*, .prettierrc*, sonar-project.properties, .editorconfig, tslint.json, .rubocop.yml, rustfmt.toml, clippy.toml
Glob: pom.xml, build.gradle*, package.json, Cargo.toml (for dependency analysis)
```

### Step 3: Build File Manifest

Create a mapping of which source files each documentation agent needs to read. Group files so no single agent gets more than ~30 files. If a category has too many files, prioritize:
1. Entry points and configuration files first
2. Core domain files (most-imported, most-referenced)
3. Drop utility/helper files if over the limit

Files can appear in at most 2-3 sections — a Service file might feed both doc-c4 and doc-api, but not every section.

### Step 4: Build Documentation Plan

Create a plan with sections to generate. Each section has:
- `id`: skill name (e.g., "doc-c4", "doc-api")
- `title`: human-readable title
- `enabled`: boolean (true if relevant files found, or always true for doc-adr)
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

Skip sections that have zero relevant files (except `doc-adr` — see note above).

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
| 4 | ADRs | 5 | 8-12 | Enabled (inferred from code) |
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
4. **Handle monorepos** — if multiple projects detected (multiple pom.xml, Cargo.toml at different paths), ask user which to document
5. **Files should appear in at most 2-3 sections** — a Service file might feed both doc-c4 and doc-api, but not every section
6. **The plan JSON MUST include `"wave"` on every section and a top-level `"waves"` object** — downstream commands depend on these exact field names
7. **Always enable doc-adr** unless the project is trivially small — it infers decisions from prior wave output even when no ADR files exist

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
