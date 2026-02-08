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

#### Entities / Models / Migrations / Repositories / Data Clients → feeds `doc-data-discover`
```
Entities and Models:
  Glob: **/*Entity*, **/*Model*, **/*Schema*, **/*Migration*, **/*migration*, **/entities/*, **/models/*, **/domain/*
  Grep patterns:
    Java: @Entity, @Table, @Column, @Id, @ManyToOne, @OneToMany
    Rust: #[derive(.*Queryable.*)]  , diesel::table!, #[derive(.*FromRow.*)]
    JS/TS: Schema.define, @Entity(), @Column(), model.define
    Python: class.*Model, db.Column, models.Model
    SQL: CREATE TABLE, ALTER TABLE
  Also: **/migrations/*, **/flyway/*, **/alembic/*, **/prisma/schema.prisma

Repositories and Data Access (for query discovery):
  Glob: **/*Repository*, **/*Repo.*, **/repository/*, **/repositories/*
  Grep patterns:
    Java: JpaRepository, CrudRepository, @Query, nativeQuery
    Rust: diesel::query_dsl, sqlx::query, sea_orm::EntityTrait
    JS/TS: Repository, getRepository, createQueryBuilder
    Python: session.query, db.session

DynamoDB / NoSQL Clients:
  Glob: **/*DynamoDBClient*, **/*DynamoClient*, **/*MongoClient*, **/*DocumentClient*
  Grep patterns:
    Java: DynamoDbEnhancedClient, DynamoDbTable, @DynamoDbBean
    JS/TS: DocumentClient, DynamoDB.DocumentClient
    Python: boto3.resource('dynamodb')

S3 / Object Store Clients:
  Glob: **/*FileStore*, **/*S3Client*, **/*StorageService*, **/*BlobClient*
  Grep patterns:
    Java: AmazonS3, S3Client, putObject, getObject
    JS/TS: S3Client, PutObjectCommand
    Python: boto3.client('s3')

Redis / Cache Clients:
  Glob: **/*RedisClient*, **/*CacheService*, **/*RedisTemplate*
  Grep patterns:
    Java: RedisTemplate, @Cacheable, @CacheEvict, StringRedisTemplate
    JS/TS: redis.createClient, ioredis
    Python: redis.Redis, aioredis

Stored Procedures:
  Grep patterns in migration files:
    SQL: CREATE FUNCTION, CREATE PROCEDURE, CREATE OR REPLACE FUNCTION
```

**Note on data sub-skills:** Data documentation is split into 4 focused sub-skills that run in separate waves:
- `doc-data-discover` (Wave 2) — lightweight scanner, uses only Glob/Grep, produces `docs/.data-manifest.json`
- `doc-data-tables` (Wave 3) — one page per table with DBA scorecard
- `doc-data-queries` (Wave 4) — one page per query with DBA scorecard
- `doc-data-overview` (Wave 5) — rollup overviews, ERDs, pipelines

When data files are found, create all 4 sections. Assign ALL data-related files to `doc-data-discover` in the manifest (it discovers the rest via Glob/Grep). The downstream skills (`doc-data-tables`, `doc-data-queries`, `doc-data-overview`) get empty file lists — they read `docs/.data-manifest.json` for their file inventory.

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
- `wave`: execution wave (1-6) — determines when this section runs
- `file_count`: number of source files to analyze
- `output_files`: list of markdown files to generate

**Wave assignments (fixed — do not change these):**

| Wave | Sections | Why |
|------|----------|-----|
| 1 | `doc-c4` | Establishes the system map. All other domains reference this. |
| 2 | `doc-api`, `doc-data-discover`, `doc-events` | Horizontal concerns. Data discovery produces `.data-manifest.json` for downstream data skills. |
| 3 | `doc-data-tables` | One page per table with DBA scorecard. Reads `.data-manifest.json` from Wave 2. |
| 4 | `doc-data-queries` | One page per query with DBA scorecard. Reads table pages from Wave 3 for cross-referencing. |
| 5 | `doc-security`, `doc-devops`, `doc-testing`, `doc-data-overview` | Cross-cutting analysis + data rollup overviews. Reads all prior wave output. |
| 6 | `doc-adr`, `doc-quality` | Assessment and synthesis. Reads complete system picture. |

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
| 2 | Data Discovery | 35 | manifest | Enabled |
| 2 | Events & Async | 0 | 0 | Skipped (no async triggers found) |
| 3 | Data Tables | — | 25 | Enabled (1 page per table) |
| 4 | Data Queries | — | 50 | Enabled (1 page per query) |
| 5 | Security | 8 | 3 | Enabled |
| 5 | DevOps | 12 | 3 | Enabled |
| 5 | Testing | 34 | 2 | Enabled |
| 5 | Data Overviews | — | 5 | Enabled (rollup pages) |
| 6 | ADRs | 5 | 8-12 | Enabled (inferred from code) |
| 6 | Quality | 6 | 2 | Enabled |

Total: ~12 sections, ~100-150 pages (6 execution waves)
Note: Data sections generate 1 page per table + 1 page per query — page count varies by codebase size

Proceed with this plan? (You can disable sections or adjust)
```

Use AskUserQuestion to get approval. Allow the user to disable/enable sections.

### Step 6: Save Plan Files

After approval, create `docs/` directory if needed (`mkdir -p docs`).

#### 6a: Copy the template verbatim

1. Read `{SKILLS_DIR}/doc-discover/references/plan-template.json` (where `SKILLS_DIR` is the path where you found this SKILL.md)
2. Write its contents **verbatim** to `docs/.doc-plan.json` using the Write tool — do not modify it yet

This two-step approach ensures the JSON skeleton is always correct before you start editing.

**Fallback — if you cannot read the template**, use this exact JSON skeleton instead:

```json
{
  "project_name": "REPLACE_PROJECT_NAME",
  "language": "REPLACE_LANGUAGE",
  "framework": "REPLACE_FRAMEWORK",
  "generated": "REPLACE_DATE",
  "waves": {
    "1": ["doc-c4"],
    "2": ["doc-api", "doc-data-discover", "doc-events"],
    "3": ["doc-data-tables"],
    "4": ["doc-data-queries"],
    "5": ["doc-security", "doc-devops", "doc-testing", "doc-data-overview"],
    "6": ["doc-adr", "doc-quality"]
  },
  "sections": [
    { "id": "doc-c4",             "title": "Architecture (C4)", "enabled": false, "wave": 1, "file_count": 0, "output_files": [] },
    { "id": "doc-api",            "title": "API Plane",         "enabled": false, "wave": 2, "file_count": 0, "output_files": [] },
    { "id": "doc-data-discover",  "title": "Data Discovery",    "enabled": false, "wave": 2, "file_count": 0, "output_files": [] },
    { "id": "doc-events",         "title": "Events & Async",    "enabled": false, "wave": 2, "file_count": 0, "output_files": [] },
    { "id": "doc-data-tables",    "title": "Data Tables",       "enabled": false, "wave": 3, "file_count": 0, "output_files": [] },
    { "id": "doc-data-queries",   "title": "Data Queries",      "enabled": false, "wave": 4, "file_count": 0, "output_files": [] },
    { "id": "doc-security",       "title": "Security",          "enabled": false, "wave": 5, "file_count": 0, "output_files": [] },
    { "id": "doc-devops",         "title": "DevOps",            "enabled": false, "wave": 5, "file_count": 0, "output_files": [] },
    { "id": "doc-testing",        "title": "Testing",           "enabled": false, "wave": 5, "file_count": 0, "output_files": [] },
    { "id": "doc-data-overview",  "title": "Data Overviews",    "enabled": false, "wave": 5, "file_count": 0, "output_files": [] },
    { "id": "doc-adr",            "title": "ADRs",              "enabled": false, "wave": 6, "file_count": 0, "output_files": [] },
    { "id": "doc-quality",        "title": "Quality",           "enabled": false, "wave": 6, "file_count": 0, "output_files": [] }
  ]
}
```

#### 6b: Fill in project-specific fields

Use the **Edit** tool to update `docs/.doc-plan.json` (do NOT rewrite the entire file):

1. Replace `REPLACE_PROJECT_NAME`, `REPLACE_LANGUAGE`, `REPLACE_FRAMEWORK`, `REPLACE_DATE` with actual values
2. For each section: set `enabled` to `true`/`false`, fill in `file_count`, fill in `output_files`
3. Update the `"waves"` object: remove disabled section IDs from each wave's array

**Critical rules:**
- Every section must have a `"wave"` field (integer 1-6) — do NOT change wave values from the template
- The top level must have a `"waves"` object with keys `"1"` through `"6"`
- `"sections"` must be an **array** (not an object)
- Do NOT add keys like `"priority"`, `"order"`, or `"rank"` — use `"wave"` only

#### 6c: Write `docs/.doc-manifest.json`

1. Read `{SKILLS_DIR}/doc-discover/references/manifest-template.json` (where `SKILLS_DIR` is the path where you found this SKILL.md)
2. Write its contents **verbatim** to `docs/.doc-manifest.json` using the Write tool — do not modify it yet

**Fallback — if you cannot read the template**, use this exact JSON skeleton instead:

```json
{
  "generated": "REPLACE_DATE",
  "sections": {
    "doc-c4":            { "files": [], "batch_size": 0 },
    "doc-api":           { "files": [], "batch_size": 0 },
    "doc-data-discover": { "files": [], "batch_size": 0 },
    "doc-events":        { "files": [], "batch_size": 0 },
    "doc-data-tables":   { "files": [], "batch_size": 0 },
    "doc-data-queries":  { "files": [], "batch_size": 0 },
    "doc-security":      { "files": [], "batch_size": 0 },
    "doc-devops":        { "files": [], "batch_size": 0 },
    "doc-testing":       { "files": [], "batch_size": 0 },
    "doc-data-overview": { "files": [], "batch_size": 0 },
    "doc-adr":           { "files": [], "batch_size": 0 },
    "doc-quality":       { "files": [], "batch_size": 0 }
  }
}
```

3. Use the **Edit** tool to fill in project-specific values:
   - Replace `REPLACE_DATE` with the current date
   - For each enabled section, populate the `"files"` array with source file paths and set `"batch_size"`
   - Disabled sections keep empty arrays

**Critical rules:**
- Section keys must match the `"id"` values in `docs/.doc-plan.json` exactly (e.g., `doc-data-discover`, NOT `doc-data`)
- Group files so no section gets more than ~30 files
- `doc-data-tables`, `doc-data-queries`, and `doc-data-overview` get empty file arrays — they read `docs/.data-manifest.json` produced by `doc-data-discover`

### Step 7: Validate Plan JSON — EXIT GATE (MANDATORY)

**Your task is NOT complete until the validator prints PASS.**
**Do NOT display next steps, do NOT report success, do NOT stop until PASS.**

This is the absolute final step. Nothing comes after this except reporting the result.

#### 7a: Run the validator

```
python3 {SKILLS_DIR}/doc-discover/references/validate-plan.py docs/.doc-plan.json
```

If you can't find the script, use Glob: `**/doc-discover/references/validate-plan.py`

#### 7b: If PASS — you are done

Report success and display the next steps to the user.

#### 7c: If FAIL — fix and retry (up to 3 attempts)

1. Read the error messages — they tell you exactly what's wrong
2. Use Edit to fix each error in `docs/.doc-plan.json`
3. Run the validator again
4. If it still fails, repeat (attempt 2 of 3)
5. If it still fails, repeat one final time (attempt 3 of 3)

**If still FAIL after 3 fix attempts:** STOP and report the remaining errors to the user. Do NOT silently succeed. Do NOT display "next steps" as if the plan were valid. Say:

```
Plan validation failed after 3 fix attempts. Remaining errors:
  - [list errors from validator output]

Please review docs/.doc-plan.json manually or re-run /doc to regenerate.
```

### Important Rules

1. **Never read full source files** — only use Glob for file discovery and Grep for pattern matching
2. **Be conservative with estimates** — it's better to include a section and find nothing than to skip it
3. **Respect user choices** — if they disable a section, mark it `enabled: false`
4. **Handle monorepos** — if multiple projects detected (multiple pom.xml, Cargo.toml at different paths), ask user which to document
5. **Files should appear in at most 2-3 sections** — a Service file might feed both doc-c4 and doc-api, but not every section
6. **The plan JSON MUST include `"wave"` (integer 1-6) on every section and a top-level `"waves"` object** — downstream commands depend on these exact field names
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
