# Mermaid Diagram Syntax Guide

Shared reference for all diagram-producing skills. Every diagram in Phase 1 markdown output MUST be a fenced Mermaid code block. No ASCII art, no `<!-- diagram-meta -->` YAML, no `<!-- diagram:type:name -->` markers.

---

## General Rules

1. Every diagram is a fenced code block starting with `` ```mermaid `` and ending with `` ``` ``
2. The first line inside the fence declares the diagram type
3. Use **real names** from the codebase — never placeholders like "ServiceA" or "ExampleController"
4. No color metadata, no style directives — the MkDocs plugin handles all styling
5. Keep labels concise but specific (include technology where relevant)
6. One diagram per fenced block — never combine multiple diagram types in one block

---

## C4 Diagrams

### C4 Context (Level 1)

```mermaid
C4Context
    title System Context Diagram — {System Name}

    Person(user, "User", "Description of user role")
    Person(admin, "Admin", "Administrative user")

    System(sys, "System Name", "Brief description")

    System_Ext(email, "Email Service", "Transactional email delivery")
    System_Ext(payment, "Payment Gateway", "Payment processing via Stripe")

    Rel(user, sys, "Uses", "HTTPS")
    Rel(admin, sys, "Manages", "HTTPS")
    Rel(sys, email, "Sends email via", "SMTP")
    Rel(sys, payment, "Processes payments via", "REST API")
```

**Elements:** `Person(id, label, description)`, `System(id, label, desc)`, `System_Ext(id, label, desc)`
**Relationships:** `Rel(from, to, label)` or `Rel(from, to, label, technology)`

### C4 Container (Level 2)

```mermaid
C4Container
    title Container Diagram — {System Name}

    Person(user, "User", "End user")

    Container_Boundary(sys, "System Name") {
        Container(web, "Web App", "React", "Single-page application")
        Container(api, "API Server", "Spring Boot", "REST API backend")
        Container(worker, "Worker", "Python", "Background job processor")
        ContainerDb(db, "Database", "PostgreSQL", "Primary data store")
        ContainerDb(cache, "Cache", "Redis", "Session and query cache")
        ContainerQueue(queue, "Message Queue", "RabbitMQ", "Async task queue")
    }

    System_Ext(email, "Email Service", "SendGrid")

    Rel(user, web, "Uses", "HTTPS")
    Rel(web, api, "Calls", "HTTPS/JSON")
    Rel(api, db, "Reads/writes", "JDBC")
    Rel(api, cache, "Caches", "TCP")
    Rel(api, queue, "Publishes", "AMQP")
    Rel(worker, queue, "Consumes", "AMQP")
    Rel(worker, email, "Sends via", "REST API")
```

**Elements:** `Container(id, label, technology, desc)`, `ContainerDb(...)`, `ContainerQueue(...)`
**Boundaries:** `Container_Boundary(id, label) { ... }`

### C4 Component (Level 3)

```mermaid
C4Component
    title Component Diagram — {Container Name}

    Container_Boundary(api, "API Server") {
        Component(ctrl, "PaymentController", "Spring MVC", "Handles payment REST endpoints")
        Component(svc, "PaymentService", "Spring Bean", "Payment business logic")
        Component(repo, "PaymentRepository", "Spring Data JPA", "Payment data access")
        Component(client, "StripeClient", "HTTP Client", "Stripe API integration")
    }

    ContainerDb(db, "PostgreSQL", "Primary data store")
    System_Ext(stripe, "Stripe API", "Payment processor")

    Rel(ctrl, svc, "Calls")
    Rel(svc, repo, "Reads/writes")
    Rel(svc, client, "Charges via")
    Rel(repo, db, "SQL queries", "JDBC")
    Rel(client, stripe, "REST calls", "HTTPS")
```

**Elements:** `Component(id, label, technology, desc)`

### C4 Code (Level 4) — Use flowchart

For code-level detail, use `flowchart TD` since Mermaid has no C4 code diagram type:

```mermaid
flowchart TD
    subgraph PaymentService
        process["process(payment: Payment)"]
        validate["validate(payment)"]
        charge["charge(amount, token)"]
        persist["persist(record)"]
    end

    process --> validate
    validate -->|valid| charge
    validate -->|invalid| error["Return ValidationError"]
    charge -->|success| persist
    charge -->|failure| retry["Retry with backoff"]
    persist --> ok["Return PaymentResult"]
```

---

## Sequence Diagrams

```mermaid
sequenceDiagram
    participant C as Client
    participant G as API Gateway
    participant S as PaymentService
    participant R as PaymentRepository
    participant DB as PostgreSQL
    participant E as Stripe API

    C->>G: POST /api/payments
    G->>S: forward request
    S->>S: Validate request fields
    S->>R: save(paymentRecord)
    R->>DB: INSERT INTO payments
    DB-->>R: OK
    S->>E: charge(amount, token)
    E-->>S: chargeResult
    S-->>G: PaymentDTO
    G-->>C: 201 Created

    alt Payment declined
        E-->>S: DeclinedError
        S-->>G: 402 Payment Required
        G-->>C: 402
    end

    opt Idempotent retry
        C->>G: POST /api/payments (same idempotency key)
        G->>S: forward request
        S->>R: findByIdempotencyKey(key)
        R-->>S: existing record
        S-->>G: existing PaymentDTO
        G-->>C: 200 OK
    end
```

**Participants:** `participant ALIAS as "Display Name"`
**Arrows:**
- `->>` solid arrow (synchronous request)
- `-->>` dashed arrow (response / return)
- `-x` solid with X (failed/rejected)
- `--x` dashed with X

**Blocks:** `alt`/`else`, `opt`, `loop`, `rect`, `Note over A,B: text`

---

## Entity Relationship Diagrams

```mermaid
erDiagram
    USER {
        bigint id PK
        varchar email "NOT NULL, UNIQUE"
        varchar password_hash "NOT NULL"
        bigint org_id FK
        timestamp created_at
    }

    ORGANIZATION {
        bigint id PK
        varchar name "NOT NULL"
        varchar slug "UNIQUE"
    }

    ROLE {
        bigint id PK
        varchar name "NOT NULL"
    }

    USER_ROLE {
        bigint user_id FK
        bigint role_id FK
    }

    USER ||--o{ USER_ROLE : "has"
    ROLE ||--o{ USER_ROLE : "assigned to"
    ORGANIZATION ||--o{ USER : "employs"
```

**Entities:** Declare with `ENTITY_NAME { type field_name constraint "description" }`
**Relationships:**
- `||--||` one-to-one
- `||--o{` one-to-many
- `o{--o{` many-to-many (use join table)
- `||--o|` one-to-zero-or-one

---

## Flowcharts

### Top-to-bottom (TD) — for hierarchical flows, infrastructure topology

```mermaid
flowchart TD
    subgraph Public Internet
        client["Client Browser"]
    end

    subgraph DMZ
        gw["API Gateway<br/>Rate limiting, TLS"]
    end

    subgraph Internal Network
        svc["App Service<br/>Spring Boot"]
        db[("PostgreSQL<br/>Primary DB")]
        cache[("Redis<br/>Cache")]
    end

    client -->|HTTPS| gw
    gw -->|HTTP| svc
    svc -->|JDBC| db
    svc -->|TCP| cache
```

### Left-to-right (LR) — for pipelines, data flows, CI/CD, event flows

```mermaid
flowchart LR
    subgraph Producers
        svc["OrderService"]
    end

    subgraph Broker
        topic["orders.created<br/>Kafka Topic"]
        dlq["orders.created.dlq"]
    end

    subgraph Consumers
        notify["NotificationService"]
        analytics["AnalyticsService"]
    end

    svc -->|publish| topic
    topic -->|consume| notify
    topic -->|consume| analytics
    notify -->|max retries exceeded| dlq
```

**Node shapes:**
- `["text"]` rectangle (default)
- `("text")` rounded rectangle / stadium
- `[("text")]` cylinder (database)
- `{"text"}` diamond (decision)
- `{{"text"}}` hexagon
- `(["text"])` stadium
- `(("text"))` circle

**Subgraphs:** `subgraph Title ... end` — nest for boundaries (region > VPC > subnet)

**Edge labels:** `-->|label text|` or `-- label text -->`

---

## Diagram Type Mapping

| Documentation context | Mermaid diagram type |
|---|---|
| C4 Level 1 — System Context | `C4Context` |
| C4 Level 2 — Containers | `C4Container` |
| C4 Level 3 — Components | `C4Component` |
| C4 Level 4 — Code structure | `flowchart TD` |
| API request lifecycle | `sequenceDiagram` |
| Auth flow | `sequenceDiagram` with `rect` blocks |
| Database schema / ERD | `erDiagram` |
| Data pipeline / flow | `flowchart LR` |
| Event flow (pub/sub) | `flowchart LR` with subgraphs |
| Saga / choreography | `sequenceDiagram` with `rect` blocks |
| CI/CD pipeline | `flowchart LR` with decision diamonds |
| Infrastructure topology | `flowchart TD` with nested subgraphs |
| Threat model | `flowchart TD` with subgraphs for trust boundaries |
