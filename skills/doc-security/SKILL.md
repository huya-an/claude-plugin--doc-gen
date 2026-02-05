# doc-security

## Description
Generates security analysis documentation: authentication flows, authorization models, threat modeling, and security configuration review. Runs as Wave 3 — cross-cutting analysis that reads Wave 1-2 output for system context. Produces Mermaid diagrams (sequence diagrams for auth flows, flowcharts for threat model with trust boundaries).

## Context
fork

## References
- ../references/mermaid-diagram-guide.md

## Instructions

### Inputs
1. Read `docs/.doc-plan.json` — verify `doc-security` is enabled
2. Read `docs/.doc-manifest.json` — get files under `doc-security.files`
3. Read assigned source files in batches of 5-8 to stay within context limits
4. Read prior wave output for cross-domain context (do not regenerate):
   - Wave 1: `docs/md/arch-overview.md` (system overview), `docs/md/arch-c4-level2.md` (container diagram and boundaries)
   - Wave 2: `docs/md/api-index.md` (API endpoints for auth matrix), `docs/md/data-overview.md` (data stores for encryption assessment), `docs/md/events-overview.md` (event flows for message-level auth)
   Reference component names, endpoints, data stores, and event flows as established in prior waves.
5. Read `mermaid-diagram-guide.md` from the shared references directory for Mermaid syntax

### Analysis Steps
1. **Authentication** — identify mechanism (JWT, OAuth2/OIDC, session-based, API keys, mTLS). Document: auth flow (login -> token -> validation -> refresh), token/session lifecycle, storage mechanism.
2. **Authorization** — identify model (RBAC, ABAC, ACL, custom). Document: role hierarchy, permission model, enforcement points (filters/guards/middleware/annotations), protected vs public endpoints.
3. **Security configuration** — analyze: CORS, CSRF protection, rate limiting, input validation, password hashing/encryption, secret management, security headers (CSP, HSTS, X-Frame-Options), TLS/SSL config.
4. **Threat model** — identify: trust boundaries (external/internal, user/admin, service/service), data flows across boundaries, relevant OWASP Top 10 vectors, existing mitigations in code, gaps where mitigations may be missing.

### Output Files
All files go to `docs/md/`.

**`security-overview.md`** — Frontmatter: title "Security Overview", section "Security", order 1, generated "{{DATE}}". Content: security architecture summary, auth mechanism overview, authorization model overview, key security features table, links to detail pages.

**`security-auth.md`** — Frontmatter: title "Authentication & Authorization", section "Security", order 2, generated "{{DATE}}". Content: auth flow with Mermaid sequence diagram, token/session lifecycle, role & permission model, authorization enforcement points, protected endpoint summary table.

**`security-threats.md`** — Frontmatter: title "Threat Model", section "Security", order 3, generated "{{DATE}}". Content: threat model Mermaid flowchart diagram, trust boundary descriptions, data flow analysis, OWASP Top 10 relevance table (which apply, mitigations, gaps), security recommendations.

### Diagram Format — Mermaid

#### Auth Flow Sequence Diagram (security-auth.md)

```mermaid
sequenceDiagram
    participant C as Client
    participant G as API Gateway
    participant A as Auth Service
    participant T as Token Store

    rect rgb(232, 245, 233)
        Note over C,T: Happy Path — Successful Authentication
        C->>G: POST /login (credentials)
        G->>A: forward credentials
        A->>A: Validate credentials
        A->>T: Store token
        T-->>A: tokenId
        A-->>G: 200 (access_token, refresh_token)
        G-->>C: 200 OK
    end

    rect rgb(227, 242, 253)
        Note over C,T: Token Refresh
        C->>G: POST /refresh (refresh_token)
        G->>A: forward token
        A->>T: Lookup token
        T-->>A: valid
        A->>A: Issue new pair
        A-->>G: 200 (new access_token, refresh_token)
        G-->>C: 200 OK
    end

    rect rgb(255, 235, 238)
        Note over C,T: Failure Paths
        C->>G: POST /login (bad credentials)
        G->>A: forward
        A->>A: Validate fail
        A-->>G: 401 Unauthorized
        G-->>C: 401

        C->>G: GET /resource (expired token)
        G->>A: validate token
        A-->>G: 403 Forbidden
        G-->>C: 403
    end
```

Use `sequenceDiagram` with `rect` blocks to group happy path, token refresh, and failure paths.

#### Threat Model Diagram (security-threats.md)

```mermaid
flowchart TD
    subgraph Public["Public Internet (untrusted)"]
        client["Client"]
    end

    subgraph DMZ["DMZ / Edge (semi-trusted)"]
        gw["API Gateway<br/>TLS 1.2+, Rate Limit"]
    end

    subgraph Internal["Internal Network (trusted)"]
        auth["Auth Service<br/>JWT, bcrypt"]
        app["App Service"]
        db[("Token Store<br/>AES-256, TLS")]
    end

    client -->|"T1: Credential stuffing<br/>(Spoofing)"| gw
    client -->|"T2: Session hijacking<br/>(Spoofing)"| gw
    gw -->|"T3: Token forgery<br/>(Tampering)"| auth
    client -->|"T4: DDoS<br/>(Denial of Service)"| gw
    gw --> auth
    auth --> db
    auth --> app
```

Use `flowchart TD` with nested `subgraph` blocks for trust boundaries (Public, DMZ, Internal). Label attack vector edges with threat ID, name, and STRIDE category.

### Rules
- Auth flow diagram must show COMPLETE flow (login through token refresh)
- Threat model must use real trust boundaries from the architecture
- Recommendations must be specific and actionable (not generic "use HTTPS")
- NEVER expose actual secrets, keys, or passwords -- redact them
- If security config is minimal, note it as a finding rather than skipping
- Every claim must reference specific code/config files

## Tools
- Read
- Glob
- Grep
- Write

## Output
Markdown files in `docs/md/`:
- `security-overview.md`
- `security-auth.md`
- `security-threats.md`
