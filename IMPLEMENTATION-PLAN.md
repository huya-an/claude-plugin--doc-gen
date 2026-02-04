# Implementation Plan: Documentation Generation Pipeline

## Overview

A multi-phase pipeline that documents any codebase using specialized AI agents organized like an engineering team. Deterministic work (HTML templating, encoding) is handled by code. AI agents focus on analysis, understanding, and writing.

The pipeline has 5 major phases:

```
Phase 0: Discovery (Lead Engineer scans the repo)
Phase 1: Markdown Generation (Specialized team writes docs in waves)
Phase 2: Site Skeleton (Python script generates HTML shells)
Phase 3: Site Content (Per-page agent pipelines fill in HTML)
Phase 4: Validation (Cross-page checks + visual smoke test)
```

---

## Phase 0: Discovery (Lead Engineer)

### Goal
Scan the repo structure, identify what exists, determine which documentation domains are needed, and produce a documentation plan.

### 0.1 — What the Discovery Agent Does

Reads (broad, shallow — Glob/Grep only, never reads full files):
- Project root files: README, package manifests (Cargo.toml, pom.xml, package.json, go.mod)
- File/directory structure
- Entry points, handler registrations, route definitions
- Config files, deployment configs, IaC

Identifies:
| Signal | Domain Area | Conditional? |
|---|---|---|
| Package structure, module boundaries | C4 Architecture | Always |
| Controllers, routes, handlers | API | Always (if web service) |
| ORM entities, migrations, schema files, DB configs | Data/DBA | Conditional |
| Dockerfiles, CI configs, IaC (CDK/Terraform) | DevOps | Conditional |
| Event handlers, listeners, message configs | Events | Conditional |
| Auth configs, security filters, secrets handling | Security | Always |
| Test suites, coverage configs | Testing | Always |
| Static analysis configs, dependency files | Quality | Always |
| Existing ADR docs | ADR | Always |

### 0.2 — Outputs

- `docs/.doc-plan.json` — approved documentation plan (sections, enabled/disabled, file counts)
- `docs/.doc-manifest.json` — file-to-section mapping (which source files each domain agent needs)
- User approval via AskUserQuestion before proceeding

---

## Phase 1: Markdown Generation (Specialized Engineering Team)

### Goal
Produce thorough, accurate markdown documentation with ASCII diagrams. This is where the real intelligence lives. Each domain area has a pipeline of specialized agents.

### 1.0 — Execution Waves

Domains run in waves based on dependencies. Each wave can read markdown output from previous waves.

```
Wave 1: C4 Architecture Pipeline
         L1 → L2 → L3 (per container, parallel) → L4 (per component, parallel)
         At L4, component-level analysis agents spawn (parallel per component)
         Establishes the system map + deep code understanding

Wave 2: API, Data/DBA, Events (parallel pipelines)
         Trace horizontal concerns across the system map

Wave 3: Security, DevOps, Testing (parallel)
         Analyze cross-cutting concerns with full context from Waves 1-2

Wave 4: ADR, Quality (parallel)
         Assess and recommend with the complete picture from Waves 1-3
```

### 1.1 — C4 Architecture Pipeline

Sequential levels, each feeding the next. Parallel within levels where possible.

**C4 Level 1 Agent (Context)**
- Reads: project root, README, deployment configs
- Produces: `arch-overview.md`, `arch-c4-level1.md`
- ASCII diagram: system context (system + external actors)
- Identifies: system boundary, external actors, protocols

**C4 Level 2 Agent (Containers)**
- Reads: module boundaries, deployment configs, infra code
- Produces: `arch-c4-level2.md`
- ASCII diagram: all containers and connections
- Identifies: **list of containers worth Level 3 decomposition** with associated source files
- Outputs manifest for Level 3 agent spawning

**C4 Level 3 Agents (Components) — one per container, parallel**
- Each reads: only source files for its container
- Each produces: `arch-c4-level3-{container-slug}.md`
- ASCII diagram: components within the container
- Component table: name, type, responsibility
- Identifies: **components worth Level 4 detail** with associated source files
- Outputs manifest for Level 4 agent spawning

**C4 Level 4 Agents (Code) — one per component, parallel**
- Each reads: the specific functions/classes for its component
- Each produces: `arch-c4-level4-{component-slug}.md`
- Uses judgment: if component has multiple complex flows, recommends sub-pages
- Identifies: **which component-level analysis lenses apply** (see 1.2)
- Outputs manifest for component analysis agent spawning

**C4 Level 4 Flow Agents (if needed) — one per flow, parallel**
- Only spawned for complex components with multiple distinct flows
- Each produces: `arch-c4-level4-{component}-{flow}.md`
- Data flow diagram for that specific flow

### 1.2 — Component-Level Analysis Agents

At the C4 Level 4 stage, each significant component can spawn up to 9 specialized analysis agents. The L4 agent decides which lenses apply based on the component's nature. These run **in parallel** for each component.

**1. Code Analysis Agent**
- What the function/class does in plain language
- Call chain: what it calls, what calls it
- Input/output types and shapes
- Branching logic and decision points
- Edge cases and boundary conditions
- Pure vs side-effecting code
- Dependencies (imports, injected services)

**2. Security Agent**
- Authentication: how is the caller verified?
- Authorization: what permissions are checked?
- Input validation: what's sanitized, what's trusted?
- Secrets handling: how are credentials fetched, stored, cached?
- Cryptographic operations: algorithms, key management, timing safety
- Attack surface: what can malicious input do?
- OWASP relevance: injection, broken auth, sensitive data exposure

**3a. Data Flow Agent**
- Data transformations step by step: raw input → parsed → validated → transformed → output
- Schema at each stage: what shape is the data?
- Serialization/deserialization: JSON, protobuf, XML, etc.
- Data loss or enrichment: what's added, what's dropped?
- Cross-boundary data: what crosses a network, queue, or database boundary?

**3b. Query/Database Analysis Agent**
- Identify every SQL query, ORM call, or database operation
- For each query:
  - The raw SQL or ORM expression
  - What tables/indexes it hits
  - Is there an appropriate index? Does it need a primary key?
  - N+1 query detection
  - Full table scan risk
  - Join efficiency
  - Suggestions: rewrite, break up, different access pattern?
- DynamoDB specific: partition key design, GSI usage, scan vs query, hot partition risk
- Connection handling: connections reused or opened per call?
- Transaction boundaries: what's atomic, what's not?

**4. Sequence Diagram Agent**
- Full request lifecycle across system boundaries
- Synchronous vs asynchronous interactions
- Which external services called and in what order
- Response path: success and error
- Timeout and retry behavior
- Produces sequence diagram ASCII art

**5. Error & Resilience Agent**
- Every failure mode: what can go wrong?
- Error responses: what does the caller see for each failure?
- Retry logic: how many attempts, backoff strategy?
- Dead letter queues: where do failed messages go?
- Circuit breakers, fallbacks, graceful degradation
- Logging and observability: what's logged on failure?

**6. Testing Agent**
- How is this component tested? Unit, integration, both?
- Test file locations and test function names
- What's covered: happy path, edge cases, error cases
- What's NOT covered: gaps in test coverage
- Mocking strategy: what's mocked, what's real?
- Test data: fixtures, factories, hardcoded values

**7. Performance & Scaling Agent**
- Time complexity of key operations
- Memory allocation patterns
- Cold start behavior (Lambda, serverless)
- Caching: what's cached, TTL, invalidation
- Concurrency: thread safety, async patterns, connection pooling
- Bottlenecks: I/O bound vs CPU bound
- Scaling limits: what breaks at 10x, 100x load?

**8. Dependencies & Integration Agent**
- External service dependencies: what, why, failure impact
- SDK versions and configuration
- Connection management: pools, keepalive, timeouts
- Service contracts: expected request/response formats
- Versioning and backwards compatibility
- Infrastructure coupling: environment variables, AWS resources

Not every component gets all 9 agents. The L4 agent decides based on:
- Handles auth/secrets → Security
- Has database operations → Query/Database Analysis
- Transforms data across boundaries → Data Flow
- Calls external services → Sequence Diagram
- Complex with multiple paths → Code Analysis (detailed)
- Trivial helper → Just the L4 overview, no sub-pages

### 1.3 — API Pipeline (Wave 2)

**Step 1: Endpoint Discovery Agent**
- Reads: controller/handler/route files (signatures, annotations), middleware configs, DTO definitions, OpenAPI specs if present
- Produces: `api-index.md` — table of every endpoint (method, path, auth, handler, request/response types)
- Outputs manifest: each endpoint with its source files for Step 2

**Step 2: Per-Endpoint Agent (one per endpoint, parallel)**
- Reads (narrow, deep): handler function, every service/function it calls, every downstream call (DB queries, queue writes, external HTTP), error handling at each layer
- Traces the **full horizontal flow**: request in → through every layer → response out. Every hop, every database touched, every queue written to, every external call.
- Produces: `api-{method}-{path-slug}.md`
  - Request: method, path, headers, query params, body schema with field descriptions
  - Auth requirements
  - Full call chain trace with what happens at each step
  - Databases impacted, queries executed
  - Sequence diagram (ASCII) showing full request lifecycle across all boundaries
  - Response: success schema, error responses with status codes and conditions
  - Example request/response if inferable

This is the **horizontal view** — follow one request end to end. Engineers use this to debug: "where in this chain did things break?"

### 1.4 — ADR Pipeline (Wave 4)

**Step 1: ADR Discovery Agent**
- Reads: existing ADR documents, git log for major architectural commits, config files revealing architectural choices, README architecture sections
- Produces: `adr-index.md` — table of all ADRs (existing + inferred)
- Identifies:
  - Existing ADRs that need compliance review
  - **Inferred ADRs**: decisions visible in code but not formally documented (e.g., "chose Rust for Lambda runtime", "chose DynamoDB over Postgres", "chose FIFO queues for ordering guarantees")
- Outputs manifest for Step 2

**Step 2: Per-ADR Agent (one per ADR, parallel)**

For **existing ADRs**:
- Reads: the ADR document + relevant source code
- Produces: `adr-NNN.md` with:
  - Original decision (preserved)
  - **Compliance analysis**: was it followed, partially followed, or deviated from? Evidence from code showing adherence or drift. Specific files/patterns that confirm or contradict.
  - **Retrospective assessment**: was it a good call? What evidence supports that? What concerns have emerged? Technical debt, scaling issues, operational pain? Would the team make the same decision today? Recommendation: maintain / revisit / supersede.

For **inferred ADRs**:
- Reads: the source files evidencing the decision
- Produces: `adr-NNN.md` reconstructing the likely reasoning:
  - What was decided (inferred from code)
  - Probable context and rationale
  - Alternatives that were likely considered
  - Current consequences visible in the codebase

ADR runs in Wave 4 because:
- Inferred ADRs are easier after code analysis, data analysis, and security analysis from earlier waves
- Compliance checking requires understanding the full system state
- Retrospective assessment benefits from knowing performance, security, and testing posture

### 1.5 — Data/DBA Pipeline (Wave 2)

Data is a horizontal concern that cuts across all containers. The C4 map from Wave 1 identifies which containers touch which data stores. The Data pipeline traces the data itself — schemas, relationships, access patterns, query quality.

**Step 1: Data Discovery Agent**
- Reads: ORM entities/models, migration files, schema definitions, database configs, connection strings, table definitions (DDL), seed files
- Identifies every data store: relational DBs, DynamoDB tables, Redis caches, S3 buckets, Elasticsearch indices, etc.
- For each store: what type, what tables/collections, how it's accessed (ORM, raw SQL, SDK)
- Produces: `data-overview.md`
  - Inventory of all data stores with connection patterns
  - High-level ERD (ASCII) showing all entities and their relationships
  - Data store technology choices and their tradeoffs
  - Storage patterns: normalized vs denormalized, event sourcing, CQRS
- Outputs manifest for Steps 2-4

**Step 2: Schema Agent**
- Produces: `data-schema.md` — the detailed ERD and full schema reference
  - Every entity with all fields, types, constraints (NOT NULL, UNIQUE, FK, CHECK)
  - Every relationship with cardinality (1:1, 1:N, M:N) and join tables
  - Indexes: what's indexed, index type (B-tree, hash, GIN, GSI), covering indexes
  - Partitioning strategy if applicable (DynamoDB partition keys, PostgreSQL partitions)
  - Schema evolution: migration history summary — major schema changes over time
  - **ERD diagram (ASCII)** — detailed version with field names, types, and relationship cardinality
  - Per-store schema diagrams if the system has multiple databases (one ERD per store + one cross-store relationship diagram)

**Step 3: Query Analysis Agent (the DBA)**
- Produces: `data-queries.md` — every significant query in the codebase, analyzed
  - For each query:
    - The raw SQL or ORM expression (as written in code)
    - Which tables/indexes it hits
    - Index coverage: does an appropriate index exist? Would a composite index help?
    - Full table scan risk: queries without WHERE clause on indexed columns
    - N+1 detection: loops that execute queries inside them
    - Join efficiency: are joins on indexed columns? Nested loop vs hash join implications
    - Suggestions: rewrite, add index, break up, use a different access pattern
  - DynamoDB-specific (if applicable):
    - Partition key design: hot partition risk, key distribution
    - GSI usage: over-projection, GSI fan-out
    - Scan vs Query: any table scans that should be queries
    - Capacity mode: on-demand vs provisioned, burst behavior
  - Connection handling: pools, per-request connections, connection leaks
  - Transaction boundaries: what's atomic, what's eventually consistent
  - Query performance summary table: each query rated (Good / Needs Index / Needs Rewrite / Critical)

**Step 4: Data Pipelines Agent** (conditional — skipped if no ETL/streaming)
- Produces: `data-pipelines.md`
  - ETL flows: source → transform → destination
  - Event sourcing patterns: event store → projections → read models
  - CQRS: command side vs query side, sync mechanism
  - Data synchronization between stores (cache invalidation, denormalization updates)
  - Data flow diagram (ASCII)

**Component-level integration**: The Query/Database Analysis agent (#3b in section 1.2) does per-component query analysis. The Wave 2 Data pipeline provides the complete picture — all queries across all components, with schema-level analysis that a single component agent can't do (e.g., "these 3 components query the same table differently, and one prevents the others from using an efficient index").

### 1.6 — Events & Async Pipeline (Wave 2)

Events and async triggers are the connective tissue of distributed systems. Where the API pipeline traces synchronous request/response flows, this pipeline traces everything that happens **without a direct caller waiting** — message consumers, cron jobs, S3 event triggers, scheduled tasks, webhook receivers, file watchers, etc.

**Step 1: Async Discovery Agent**
- Reads: event handler registrations, message broker configs (SQS, SNS, EventBridge, Kafka/Redpanda, RabbitMQ), cron/scheduler configs (CloudWatch Events, crontab, Quartz, Celery Beat), S3 event notifications, Lambda triggers, webhook handler registrations, file watcher configs
- Identifies every async trigger type:
  - **Message-driven**: Kafka/Redpanda topics, SQS queues, SNS topics, EventBridge rules — producer, consumer(s), schema
  - **Schedule-driven**: cron jobs, scheduled tasks, periodic lambdas — schedule expression, what it does, what it touches
  - **Event-driven (cloud)**: S3 object notifications, DynamoDB streams, CloudWatch alarms triggering Lambdas — trigger source, handler, filter rules
  - **Webhook receivers**: inbound webhooks from external systems — endpoint, validation, processing
  - For each: DLQ/dead letter configuration, retry policies, alerting
- Produces: `events-overview.md`
  - Inventory of all async triggers by type (message, schedule, cloud event, webhook)
  - Async topology diagram (ASCII): all producers → queues/topics/triggers → consumers
  - Messaging patterns: pub/sub, point-to-point, fan-out, request/reply, competing consumers
  - Technology choices: why Kafka/Redpanda vs SQS vs EventBridge for each use case
- Produces: `events-catalog.md`
  - Table per event/trigger type: name, schema/payload, producer/trigger source, consumer(s), queue/topic, ordering guarantee, idempotency mechanism
  - Cron schedule table: job name, schedule expression (with human-readable description), handler, what data it touches, timeout, overlap protection
  - S3 trigger table: bucket, prefix/suffix filter, event type (PUT, DELETE), handler
  - This is the reference page engineers check: "what async things exist and who owns them?"
- Outputs manifest for Step 2

**Step 2: Per-Flow Agents (one per significant flow, parallel)**

Each traces an async flow end to end:
- Produces: `events-flow-{name}.md`
  - **Trigger**: what initiates this flow — message published, cron fires, file lands in S3, DynamoDB stream record, external webhook
  - **Publisher/Source**: how the event is constructed (or how the file arrives, or what the cron reads), what data is included, serialization format
  - **Transport**: queue/topic config — FIFO ordering, deduplication ID, message group, visibility timeout, retry policy, partition key (Kafka/Redpanda: partition strategy, consumer group, offset management)
  - **Consumer processing**: what the consumer does step by step — DB writes, further events published, external calls, file writes
  - **Error handling**: what happens on failure? Retry count, backoff strategy, DLQ path, poison pill handling
  - **Idempotency**: how duplicate processing is prevented — idempotency key, upsert, dedup table, exactly-once semantics
  - **Ordering**: does order matter? What guarantees exist (FIFO, partition-level, none)? What happens on out-of-order delivery?
  - **Timing**: for scheduled jobs — what happens if a run overlaps with the previous? Locking strategy? What if it misses a scheduled window?
  - **Observability**: monitoring, metrics, alarms, dashboards — how do you know this flow is healthy or failing silently?
  - Flow diagram (ASCII): full path including retry/DLQ branches, fan-out paths, error paths

**What makes this valuable**: Async flows have "invisible" failure modes. The event was published but the consumer silently dropped it. The DLQ is filling up but nobody's watching. Messages are processed out of order and the final state is wrong. A cron job failed at 3am and nobody noticed until Monday. An S3 trigger fired but the Lambda timed out on a large file. This pipeline makes all of those paths visible on paper.

**Conditional**: If the discovery agent finds zero async infrastructure (no queues, no topics, no event handlers, no crons, no S3 triggers), this entire pipeline is skipped.

### 1.7 — Security Pipeline (Wave 3)

Runs after Waves 1-2 so it can reference API endpoints, data stores, event flows. The security agents can cross-reference:
- C4 architecture → trust boundaries between containers
- API endpoints → authentication/authorization per route
- Data stores → encryption at rest, access control per table
- Event flows → message-level auth gaps

**Step 1: Security Overview Agent**
- Reads: auth configs, security filters, IAM policies, secrets management, encryption configs
- Also reads: Wave 1-2 markdown output for context (C4, API, Data, Events)
- Analyzes:
  - Authentication mechanisms: Cognito, JWT, API keys, mTLS, OAuth flows — every auth path
  - Authorization model: RBAC, ABAC, resource-based policies, IAM roles — how "who can do what" is enforced
  - Trust boundaries: maps onto C4 context/container diagrams — what's trusted, what's untrusted
  - Secrets management: how credentials are stored, rotated, injected; hardcoded secrets detection
  - Network security: VPC boundaries, security groups, public vs private subnets (if infra code exists)
- Produces: `security-overview.md` with trust boundary diagram (ASCII)
- Outputs manifest for Step 2

**Step 2: Detail Agents (3 pages, parallel)**

**`security-auth.md`** — Authentication & Authorization Deep Dive
- Per-endpoint auth matrix: which endpoints require what auth, which are public
- Credential handling: token lifetimes, refresh flows, revocation
- Session management: stateless vs stateful, storage, timeout
- Cross-references API index from Wave 2

**`security-threats.md`** — Threat Model
- STRIDE analysis (Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege) per trust boundary
- Attack vectors specific to this system's architecture
- Data sensitivity classification: which fields are PII, PHI, financial?
- Existing mitigations found in code (rate limiting, input validation, WAF rules)
- Gaps: attack vectors with no visible mitigation
- Threat model diagram (ASCII)

**`security-compliance.md`** — Compliance & Best Practices
- OWASP Top 10 checklist against the codebase: injection, broken auth, sensitive data exposure, XXE, broken access control, misconfiguration, XSS, insecure deserialization, known vulnerabilities, insufficient logging
- Dependency vulnerability scan: outdated packages with known CVEs (reads dependency lockfiles)
- Encryption audit: at-rest, in-transit, algorithm choices
- Logging & audit trail: are security events logged? Is there enough for forensics?
- Recommendations prioritized by severity (Critical / High / Medium / Low)

**System-level vs component-level**: The component-level Security agent (section 1.2, agent #2) handles per-component security deep dives. The Wave 3 Security pipeline aggregates those findings and adds system-level analysis — e.g., whether the combination of components creates an unintended bypass path, or whether trust boundaries are consistently enforced across all containers.

### 1.8 — DevOps Pipeline (Wave 3)

DevOps analysis benefits from knowing the full system shape (Wave 1 C4), the API surface (Wave 2), and the data stores and async infrastructure (Wave 2). The DevOps agent can then answer: "does the deployment model actually match the architecture?"

**Step 1: DevOps Discovery Agent**
- Reads: CI/CD configs (GitHub Actions, Jenkins, GitLab CI, CircleCI, CodePipeline), Dockerfiles, docker-compose, IaC (CDK, Terraform, CloudFormation, Pulumi), deploy scripts, monitoring configs (DataDog, CloudWatch, Grafana), alerting rules, Makefiles/task runners
- Also reads: Wave 1-2 markdown for context
- Produces: `devops-overview.md`
  - Infrastructure topology diagram (ASCII): VPCs, subnets, load balancers, compute (ECS, EKS, Lambda, EC2), data stores, queues — all connected
  - Deployment model: how code gets from commit to production
  - Environment inventory: dev, staging, prod — how they differ, config management
  - Infrastructure-as-Code coverage: what's managed by IaC vs manually provisioned
- Outputs manifest for Steps 2-3

**Step 2: CI/CD Agent**
- Produces: `devops-cicd.md`
  - Pipeline stages visualized: commit → lint → test → build → deploy-staging → integration-test → deploy-prod
  - Pipeline diagram (ASCII)
  - Trigger conditions: push to main, PR merge, tag, manual
  - Quality gates: what blocks a deploy? Test coverage thresholds, security scans, approval steps
  - Artifact management: what's built (Docker images, JARs, Lambda zips), where it's stored, versioning
  - Rollback strategy: how to undo a bad deploy
  - Environment promotion: how artifacts move staging → prod
  - Build times and bottlenecks (if config reveals caching, parallelism, or known slow steps)

**Step 3: Infrastructure Agent**
- Produces: `devops-infra.md`
  - Compute: what runs where (Lambda functions, ECS tasks, EC2 instances, K8s pods), sizing, scaling policies
  - Networking: VPC layout, subnets, security groups, NAT, VPN/peering, public vs private
  - Storage & data: RDS, DynamoDB, S3, ElastiCache — provisioning, backup, replication
  - Scaling: auto-scaling policies, Lambda concurrency limits, queue-based scaling
  - Monitoring & alerting: what's monitored (CPU, memory, latency, error rate, queue depth), alert thresholds, on-call routing
  - Cost considerations: biggest cost drivers visible in config (instance types, reserved capacity, storage volumes)
  - Disaster recovery: backup frequency, cross-region replication, RTO/RPO if documented
  - Infrastructure topology diagram (ASCII) — detailed version with CIDR blocks, instance counts, scaling ranges

### 1.9 — Testing Pipeline (Wave 3)

Testing analysis is most valuable after understanding what the system does (Waves 1-2). The testing agent can assess: "given the complexity of this API endpoint and the data flows it touches, is the test coverage adequate?"

**Step 1: Testing Discovery Agent**
- Reads: test directories, test framework configs (Jest, pytest, JUnit, Go test, Mocha), coverage configs (Istanbul, JaCoCo, coverage.py), test infrastructure (testcontainers, localstack, mocks), CI test steps
- Also reads: Wave 1-2 markdown — especially API index and C4 component list
- Produces: `testing-overview.md`
  - Test framework and tooling inventory
  - Test pyramid analysis: how many unit vs integration vs e2e tests? Is the pyramid healthy or inverted?
  - Test pyramid diagram (ASCII)
  - Coverage summary: overall coverage %, coverage by module/package
  - Test infrastructure: what's mocked, what uses real services (testcontainers, localstack), test databases
  - Test execution: how tests run in CI, parallelization, flakiness handling
- Outputs manifest for Step 2

**Step 2: Testing Strategy Agent**
- Produces: `testing-strategy.md`
  - **Coverage gap analysis**: cross-references the C4 component list and API endpoint list against test files
    - Which components have tests? Which don't?
    - Which endpoints have integration tests? Which are untested?
    - Which critical paths (identified from C4/API analysis) lack coverage?
  - **Test quality assessment** per category:
    - Unit tests: testing behavior or implementation? Brittle coupling to internals?
    - Integration tests: real interactions or mocked boundaries?
    - E2E tests: coverage of critical user journeys?
  - **What's tested well**: specific components/flows with strong coverage — acknowledge what's good
  - **What's NOT tested**: gaps ranked by risk (missing test on a payment endpoint > missing test on a health check)
  - **Test patterns**: fixtures vs factories, test data management, setup/teardown, shared test utilities
  - **Recommendations**: prioritized list of tests to add, ranked by risk-reduction value
  - Coverage heatmap table: component/module × test type (unit/integration/e2e) → covered/partial/missing

**Component-level integration**: The Testing agent (#6 in section 1.2) examines per-component test coverage. The Wave 3 pipeline aggregates into a system-wide view and identifies patterns — e.g., "all database components have unit tests but none have integration tests with a real database."

### 1.10 — Quality Pipeline (Wave 4)

Quality assessment is the capstone. It reads everything from all prior waves and produces the "state of the codebase" report with prioritized recommendations. This is the executive summary that ties together findings from security, testing, data, DevOps — all of it.

**Step 1: Quality Overview Agent**
- Reads: linter configs (ESLint, Pylint, Checkstyle, Clippy), static analysis configs (SonarQube, CodeClimate), dependency files (package-lock.json, Cargo.lock, pom.xml, go.sum), complexity metrics if available, code formatting configs (Prettier, Black, gofmt)
- Also reads: **ALL Wave 1-3 markdown output** — the one agent that gets the full picture
- Produces: `quality-overview.md`
  - Code health dashboard: language breakdown, file counts, LOC distribution
  - Dependency health: total dependencies, outdated count, known vulnerabilities (from lockfile analysis), dependency age distribution
  - Static analysis posture: what's configured, what rules are active/suppressed, severity distribution
  - Code style consistency: formatting configs, linter coverage, suppression patterns (`// eslint-disable`, `# noqa`, `@SuppressWarnings`)
  - Complexity hotspots: largest files, deepest nesting, most-modified files (if git history available)
  - Tech debt indicators: TODO/FIXME/HACK comment inventory with context
- Outputs manifest for Step 2

**Step 2: Recommendations Agent**
- Produces: `quality-recommendations.md` — the actionable report
  - **Cross-domain findings**: synthesizes issues surfaced by all prior waves
    - Security gaps found in Wave 3 security analysis
    - Untested critical paths found in Wave 3 testing analysis
    - Query inefficiencies found in Wave 2 data/DBA analysis
    - Missing monitoring for async flows found in Wave 2 events analysis
    - Infrastructure gaps found in Wave 3 DevOps analysis
  - **Prioritized recommendations**: each item has:
    - Severity: Critical / High / Medium / Low
    - Category: Security, Performance, Reliability, Maintainability, Operability
    - Finding: what the issue is, with specific file/component references
    - Recommendation: what to do about it
    - Effort estimate: Small (< 1 day) / Medium (1-3 days) / Large (1+ week)
    - References: which documentation pages contain the detailed analysis
  - **Top 5 "fix first"**: the 5 highest-impact items to address immediately
  - **Tech debt roadmap**: grouped by quarter — what to tackle now, next quarter, and long-term
  - Summary table: all recommendations sortable by severity × effort

This is the page leadership reads. Engineers read the domain-specific pages for details, but this page answers: "what are the most important things to fix, in what order?"

### 1.11 — Orchestration: How `/doc-generate` Manages Everything

**Design principle**: Slow processing with premium accuracy and value is better than speed. Every agent gets exactly what it needs in its context, nothing more, and enough room to think deeply.

#### The Orchestrator

The `/doc-generate` command is the orchestrator. It runs in the **parent context** and never reads source code directly. Its job is purely coordination:

```
Orchestrator (parent context)
├── Reads: docs/.doc-plan.json, docs/.doc-manifest.json
├── Manages: wave execution, agent spawning, manifest passing, result collection
├── Never reads: source code, generated markdown (except frontmatter at the end)
└── Writes: docs/.generation-log.json (progress tracking)
```

#### Wave Execution — Sequential Between Waves, Parallel Within

```
Wave 1: C4 Pipeline (sequential levels, parallel within levels)
  ↓ wait for ALL Wave 1 to complete
  ↓ collect manifests from L2 (containers), L3 (components), L4 (analysis lenses)
Wave 2: API + Data/DBA + Events & Async (3 parallel pipelines)
  ↓ wait for ALL Wave 2 to complete
Wave 3: Security + DevOps + Testing (3 parallel pipelines)
  ↓ wait for ALL Wave 3 to complete
Wave 4: ADR + Quality (2 parallel pipelines)
  ↓ wait for ALL Wave 4 to complete
Post: Site config generation
```

Each wave **waits** for the previous wave to fully complete before starting. This guarantees that Wave 3 agents can read Wave 1-2 output. No race conditions on markdown files.

#### Context Window Strategy Per Agent Type

This is where quality comes from. Each agent gets a **minimal, focused context**:

| Agent | Reads Into Context | Approx Context Budget |
|---|---|---|
| C4 L1 | README, project root files, deployment configs | ~20k tokens source |
| C4 L2 | L1 output + module boundary files | ~30k tokens |
| C4 L3 (per container) | L2 output + only this container's source files | ~30k tokens |
| C4 L4 (per component) | L3 output + only this component's files | ~20k tokens |
| Component analysis (per lens) | L4 output + component files + lens-specific reference | ~25k tokens |
| API discovery | Controllers/routes/handlers (signatures only) | ~20k tokens |
| API per-endpoint | Handler + full call chain for this one endpoint | ~30k tokens |
| Data discovery | ORM entities, migrations, schema files | ~25k tokens |
| Data query analysis | All files containing queries (Grep results) | ~30k tokens |
| Events discovery | Event handlers, broker configs, cron configs, trigger configs | ~25k tokens |
| Security overview | Auth configs + ALL Wave 1-2 markdown | ~40k tokens |
| DevOps discovery | CI/CD configs, IaC files + Wave 1-2 markdown | ~35k tokens |
| Testing strategy | Test configs + Wave 1-2 markdown (API index, C4 components) | ~35k tokens |
| ADR per-ADR | ADR doc + relevant source code + Wave 1-3 markdown | ~40k tokens |
| Quality recommendations | Linter configs + ALL Wave 1-3 markdown | ~50k tokens |

**Key insight: context compression across waves.** Later-wave agents read markdown from earlier waves, not raw source code. A 500-line controller file becomes a 50-line API endpoint description. A 300-line IaC file becomes a 20-line infrastructure summary. This compression is what makes the pipeline work. Wave 3 agents can "see" the full system because they're reading distilled summaries, not raw source.

#### Agent Prompt Structure

Every agent is spawned via `Task` tool with `subagent_type: "general-purpose"` and `model: "opus"`. Each prompt follows the same structure:

```
1. Role statement — who you are, what you're doing, quality bar
2. Reference material — skill-specific (drawio patterns, ADR template, C4 guide, etc.)
3. Input data — source files OR markdown from prior waves (file paths, not inline)
4. Manifest context — what you need to produce, output filenames, required sections
5. Acceptance criteria — specific checklist items, not vague "be thorough"
```

No agent gets a vague instruction like "document the security." Every agent gets:
- Exactly which files to read (file paths from manifest)
- Exactly what to produce (output filename, required sections, required diagrams)
- Exactly what quality means for its output (specific checklist items)

#### Concurrency Model — Conservative, Debuggable

**Wave 1 (C4)**: Sequential by level. L1 → L2 → L3 → L4 → component analysis. Within each level:
- L3: 2 container agents at a time
- L4: 2 component agents at a time
- Component analysis: all lens agents for one component in parallel (up to 9), but only 1 component at a time

**Waves 2-4**: Domain pipelines within a wave run in parallel (up to 3 at a time). Within each domain pipeline:
- Discovery step runs first (single agent)
- Detail/per-item agents run with concurrency of 2

**Why 2?** Conservative concurrency prevents resource contention and makes debugging tractable. If an agent fails, you know exactly which one and why. Each agent gets full resources. The system processes slower but every page comes out right.

#### Manifest Chain — How Agents Communicate Without Sharing Context

Agents never share context windows. They communicate through manifest files on disk:

```
docs/.doc-plan.json (Phase 0 output)
  │
  ├── C4 L1 → writes arch-overview.md, arch-c4-level1.md
  ├── C4 L2 → writes arch-c4-level2.md + .c4-l3-manifest.json
  │            (lists containers with associated source files)
  ├── C4 L3 → writes arch-c4-level3-{slug}.md + .c4-l4-manifest-{slug}.json
  │            (lists components with associated source files)
  ├── C4 L4 → writes arch-c4-level4-{slug}.md + .analysis-manifest-{slug}.json
  │            (lists which analysis lenses apply per component)
  ├── Component analysis → writes findings into L4 markdown sections
  │
  ├── API discovery → writes api-index.md + .api-manifest.json
  │                    (lists endpoints with source files)
  ├── API per-endpoint → writes api-{method}-{path}.md
  │
  ├── Data discovery → writes data-overview.md + .data-manifest.json
  ├── Data schema → writes data-schema.md
  ├── Data queries → writes data-queries.md
  │
  ├── Events discovery → writes events-overview.md, events-catalog.md + .events-manifest.json
  ├── Events per-flow → writes events-flow-{name}.md
  │
  ├── Security overview → writes security-overview.md + .security-manifest.json
  ├── Security detail → writes security-auth.md, security-threats.md, security-compliance.md
  │
  ├── DevOps discovery → writes devops-overview.md + .devops-manifest.json
  ├── DevOps detail → writes devops-cicd.md, devops-infra.md
  │
  ├── Testing discovery → writes testing-overview.md + .testing-manifest.json
  ├── Testing strategy → writes testing-strategy.md
  │
  ├── ADR discovery → writes adr-index.md + .adr-manifest.json
  ├── ADR per-ADR → writes adr-NNN.md
  │
  ├── Quality overview → writes quality-overview.md + .quality-manifest.json
  └── Quality recommendations → writes quality-recommendations.md
```

The orchestrator reads only manifest files to know what to spawn next. Its context stays clean.

#### Error Handling & Recovery

When an agent fails (timeout, error, produces empty output):
1. Orchestrator logs the failure to `docs/.generation-log.json`
2. Retries the agent once with the same inputs
3. If retry fails, marks that page/component as failed and continues
4. No cascade failures — if one L3 container agent fails, the other containers still process; if one API endpoint agent fails, the other endpoints still get documented
5. At the end, reports all failures to the user with specific details
6. User can re-run just the failed items (the manifest tells the orchestrator exactly what to retry)

#### Progress Reporting

The orchestrator maintains `docs/.generation-log.json`:

```json
{
  "started": "2026-02-01T10:00:00Z",
  "wave": 2,
  "phase": "api-per-endpoint",
  "waves": {
    "1": { "status": "completed", "agents": 14, "failed": 0 },
    "2": { "status": "in_progress", "agents": 8, "completed": 5, "failed": 0 },
    "3": { "status": "pending" },
    "4": { "status": "pending" }
  },
  "current_agents": [
    { "id": "api-post-payments", "status": "in_progress" },
    { "id": "api-get-payments-id", "status": "in_progress" }
  ],
  "failures": []
}
```

The user sees progress updates as each agent completes.

#### Why This Produces Premium Quality

1. **Clean context per agent**: no context rot. The 50th agent runs with the same quality as the 1st.
2. **Specialized knowledge**: each agent loads only the reference material it needs. The diagram agent gets drawio patterns. The security agent gets OWASP criteria. No wasted tokens on irrelevant instructions.
3. **Compressed context from prior waves**: Wave 3 agents read ~50 lines of distilled markdown instead of ~500 lines of raw source per component. They see the full system at a readable density.
4. **Depth over breadth**: each agent goes deep on one thing. A per-endpoint API agent reads the full call chain — every service, every DB query, every external call — for that one endpoint. It has room to trace, think, and produce thorough output.
5. **Quality gates at every level**: component-level analysis in C4, per-page QA in site generation, cross-page validation at the end. Issues are caught close to where they're introduced.
6. **No rushing**: conservative concurrency (2 at a time) means each agent gets full resources. The system processes slower but every page comes out right.
7. **Deterministic where possible**: HTML templating, sidebar generation, encoding — all handled by code. Agents focus only on the analysis and writing that requires intelligence.

### 1.12 — Post-Generation: Site Config

After ALL waves complete and all markdown files are written:

1. Scan `docs/md/*.md` — read frontmatter from every file (title, section, order)
2. Grep for `<!-- diagram:` markers — extract diagram names per file
3. Write `docs/.site-config.json` — the complete config for the Python skeleton generator
4. Write `docs/.task-manifest-md.json` — summary of what was generated, for user review

This is the handoff point between Phase 1 (markdown) and Phase 2 (site generation).

---

## Phase 2: Site Skeleton Generation (Deterministic)

### Goal
Generate the complete HTML site skeleton deterministically from the site config. No AI involved in HTML generation. (See ADR-0007)

### 2.1 — Jinja2 Templates

**Directory:** `doc-site/templates/`

| Template | Purpose |
|---|---|
| `base-page.html.j2` | Full page shell: sidebar, breadcrumbs, `<!-- CONTENT -->` placeholder, footer, script tags |
| `index.html.j2` | Dashboard: hero, stats grid, section feature cards |
| `sidebar.html.j2` | Sidebar fragment with section groups and nav links |

Source-controlled, reviewable, diffable. Hello-world sample config for standalone preview.

### 2.2 — `generate-skeleton.py`

**Inputs:**
- `docs/.site-config.json` (from Phase 1 post-generation)
- `doc-site/templates/*.j2` (source-controlled)
- `doc-site/references/styles.css` (source-controlled)

**Outputs:**
- `docs/site/index.html` — complete dashboard
- `docs/site/{slug}.html` — one shell per page
- `docs/site/styles.css` — copied from reference
- `docs/site/js/viewer-static.min.js` — downloaded if not cached
- `docs/site/.task-manifest.json` — Phase 3 work list

Zero AI. Same input = same output byte-for-byte.

---

## Phase 3: Site Content Conversion (Per-Page Agent Pipelines)

### Goal
Convert every markdown page into final HTML with embedded draw.io diagrams. Each page gets a sequential 3-agent pipeline. (See ADR-0008)

### 3.1 — Per-Page Pipeline

```
Agent A (MD → HTML) → Agent B (Diagrams) → Agent C (QA, 3 retries)
```

**Agent A: Markdown-to-HTML Converter**
- Reads: source `.md` file + target `.html` shell
- Converts markdown body to HTML. Leaves diagram markers as-is.
- Writes: updated `.html` with `<!-- CONTENT -->` replaced

**Agent B: ASCII-to-Draw.io Diagram Specialist**
- Reads: `.html` page + drawio-patterns reference
- Converts diagram markers to draw.io XML embeds. Writes `.drawio` files.
- Skipped if page has no diagrams.

**Agent C: Per-Page QA**
- Validates content, encoding, edges, HTML well-formedness
- On failure: re-invokes Agent A or B with error details
- Up to 3 retries per failing agent

### 3.2 — Concurrency

2 page pipelines run concurrently. 14 rounds for 28 pages.

### 3.3 — Skill Files

| Skill | Purpose |
|---|---|
| `doc-site-convert-md/SKILL.md` | Agent A instructions |
| `doc-site-convert-diagrams/SKILL.md` | Agent B instructions |
| `doc-site-qa-page/SKILL.md` | Agent C instructions |

---

## Phase 4: Final Validation (Cross-Page + Smoke Test)

### Goal
Verify cross-page consistency and perform visual smoke test. (See ADR-0009)

### 4.1 — Mechanical Cross-Page Checks (Grep/Glob)

- Sidebar links match actual HTML files
- Cross-page link resolution
- Diagram embed count matches `.drawio` file count
- Every task manifest page has a QA result
- `index.html` section cards link to existing pages

### 4.2 — Visual Smoke Test

Read 2-3 pages with the most diagrams. Check:
- Content reads like real documentation
- Diagrams are contextually relevant with meaningful connections
- No placeholder text
- Section flow is coherent

### 4.3 — Final Report

Aggregate all results. Display summary to user. Write `docs/.validation-site-report.json`.

```
Overall: PASS/FAIL
Local: file://{absolute_path}/docs/site/index.html
```
