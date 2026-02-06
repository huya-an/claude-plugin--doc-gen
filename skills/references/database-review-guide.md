# Database Review Guide

Shared reference for the `doc-data` skill. The agent uses this guide to grade tables and queries across all data store types. This is a **review** reference (evaluating existing schemas from source code), not a **generation** reference (designing new schemas from scratch).

---

## Grading Rubric (A-F)

| Grade | Score | Meaning | Action Required |
|---|---|---|---|
| **A** | 95-100 | Best practice, production-hardened | None |
| **B** | 80-94 | Solid, minor improvements possible | Backlog |
| **C** | 65-79 | Meaningful gaps, functional but fragile | Next sprint |
| **D** | 50-64 | Significant problems, data risk | Priority fix |
| **F** | 0-49 | Critical — security hole, data loss risk, or correctness bug | Stop-ship |
| **N/D** | — | Cannot determine from source code | Note what is missing and where to look |

**Critical rule:** An F in Security caps the overall grade at D regardless of other scores.

---

## Table Scorecard — 6 Categories

### 1. Modeling (20%)

*Is the structure right for the data and its relationships?*

| Store | Best Practice | Common Smells |
|---|---|---|
| **PostgreSQL** | 3NF compliance, single-responsibility tables, appropriate PK strategy (surrogate for entities, natural for lookups), intentional denormalization documented | Wide tables (>20 columns) carrying multiple concerns, accidental denormalization (storing both `make_id` and `make_value`), varchar PKs where integer/UUID would perform better, composite PKs on non-join tables |
| **DynamoDB** | High-cardinality partition keys, sort keys that enable range queries on access patterns, single-table design where beneficial, item size < 400KB | Low-cardinality partition key (hot partitions), sort key unused or not aligned to queries, storing large blobs in items, overloaded GSIs |
| **S3** | Key hierarchy matches access patterns, object granularity appropriate, prefix design enables parallel reads | Flat key namespace, oversized objects requiring partial reads, PII in key names |
| **Redis** | Data structure matches access pattern (hash for objects, sorted set for ranked data, set for membership), key namespace design with `:` separators | String for everything, large keys, no namespace separation, storing relational data in a key-value store |

### 2. Types & Precision (15%)

*Are data types correct, specific, and appropriately sized?*

**PostgreSQL type rules:**

| Use case | Correct type | Wrong type | Why |
|---|---|---|---|
| Money/currency | `numeric(p,s)` | `float8`, `real`, `money` | Floating-point causes rounding errors in financial calculations. The `money` type is locale-dependent. |
| Timestamps | `timestamptz` | `timestamp` | Bare `timestamp` stores no timezone — causes silent offset bugs across environments. |
| Year | `smallint` + CHECK | `varchar(20)` | Allows invalid values, wastes space, breaks range queries. |
| Boolean flags | `boolean` | `varchar`, `char(1)` | `varchar` allows arbitrary values; boolean enforces true/false at the type level. |
| IDs (auto-increment) | `bigint GENERATED ALWAYS AS IDENTITY` | `serial` | `serial` is legacy; identity columns are SQL-standard and prevent accidental manual inserts. |
| IDs (globally unique) | `uuid` | `varchar(160)`, `varchar(255)` | UUID is fixed 16 bytes; varchar PKs waste index space and slow joins. |
| Short strings with known max | `varchar(n)` or `text` + `CHECK(length(col) <= n)` | `varchar(255)` everywhere | Oversized varchar wastes query planner estimates. |
| Freeform text | `text` | `varchar(255)`, `varchar(4000)` | `text` has no artificial limit; if you need a limit, use CHECK. |
| Enums with fixed values | `text` + `CHECK(col IN (...))` | bare `varchar` | No enforcement of valid values without CHECK. |

**DynamoDB type rules:** Use Number type for numeric values (not String). Use Set types (`SS`, `NS`, `BS`) for collections of unique values. Use Binary for hashes/tokens. Prefer flat attributes over deeply nested Maps for queryable fields.

**S3 type rules:** Set accurate Content-Type headers. Use appropriate serialization format (Parquet for analytics, JSON for interchange, binary for media).

**Redis type rules:** Use appropriate serialization (MessagePack or Protobuf for high-throughput, JSON for debuggability). Store numeric values as numbers, not strings.

### 3. Integrity (20%)

*Are rules enforced at the data layer, not just the application?*

**PostgreSQL integrity checklist:**

| Check | What to look for | Grade impact |
|---|---|---|
| NOT NULL coverage | Every column that is semantically required should be NOT NULL | Missing NOT NULL on required columns = D |
| FK constraints | Every FK relationship should be enforced at the DB level, not just application | Application-only FKs = D (orphan rows possible) |
| CHECK constraints | Enum-like columns, range-bounded values, format patterns | No CHECKs on enum columns = C |
| UNIQUE constraints | Business keys, natural keys, email addresses | Missing UNIQUE on business keys = C |
| DEFAULT values | Created timestamps, status columns, boolean flags | Missing DEFAULT on obvious candidates = B |
| Cascading rules | FK ON DELETE / ON UPDATE behavior defined | Missing cascade rules = C |

**DynamoDB:** Grade on condition expressions for writes, TTL configuration for temporal data, idempotency key patterns.

**S3:** Grade on lifecycle rules, versioning, object lock policies, bucket policies.

**Redis:** Grade on TTL enforcement (no immortal cache entries without justification), atomic operations for multi-step updates, Lua scripts for complex invariants.

### 4. Performance (20%)

*Is the store optimized for actual access patterns?*

**PostgreSQL indexing rules:**

| Rule | Details |
|---|---|
| Every FK column needs an index | PostgreSQL does NOT auto-index FK columns. Missing FK index = sequential scan on JOINs. |
| Covering indexes for frequent queries | If a query always filters on (A, B) and orders by C, a composite index on (A, B, C) avoids a sort step. |
| Partial indexes for filtered queries | `WHERE status = 'ACTIVE'` on a table where 90% of rows are ACTIVE benefits from a partial index on the other 10%. |
| HASH index for equality-only lookups | VIN lookups, token lookups — HASH is smaller and faster than B-tree for `=` only. |
| No index on low-selectivity columns alone | A boolean column with 50/50 distribution gains nothing from an index. Combine with other columns. |
| Check for missing indexes | Cross-reference repository query methods with existing indexes. Every WHERE/JOIN column should have index coverage. |

**DynamoDB performance rules:** Query (not Scan) for all read paths. Minimize GSI projections (KEYS_ONLY or INCLUDE, not ALL). Watch for hot partitions on time-based sort keys with uneven traffic. Item size should be < 4KB for frequent reads (1 RCU per read).

**S3 performance rules:** Prefix design for parallel reads (avoid single-prefix bottleneck). Use multipart upload for files > 100MB. Lifecycle transition to IA/Glacier for cold data.

**Redis performance rules:** Avoid O(n) commands (KEYS, SMEMBERS on large sets). Use SCAN for iteration. Pipeline batch operations. Use appropriate encoding (ziplist for small hashes/lists).

### 5. Security (20%)

*Is sensitive data protected at the storage layer?*

**Critical findings (automatic F):**

| Finding | Why it's critical |
|---|---|
| OAuth/API tokens stored plaintext in entity tables | Any query, backup, or log that touches the table exposes credentials |
| Passwords stored without hashing | Compromised DB = compromised accounts |
| PII columns without encryption | Regulatory risk (GDPR, CCPA, HIPAA) |
| S3 bucket with public access enabled | Data exposure to the internet |

**Serious findings (D):**

| Finding | Impact |
|---|---|
| Sensitive columns (tokens, PII) fetched via SELECT * in queries | Every query over-exposes data; any log/serialization leak is a breach |
| No row-level security on multi-tenant tables | Tenant data leakage possible via query bugs |
| Redis AUTH not configured | Unauthenticated access to cached data |
| DynamoDB with no IAM scoping | Any AWS principal can read/write |

**Grade on:** Token/secret storage location, PII column identification, encryption at rest configuration (from code — N/D if in infra repo), query-level data exposure (SELECT * fetching sensitive columns unnecessarily).

### 6. Naming (5%)

*Is naming consistent, clear, and predictable?*

| Rule | Good | Bad |
|---|---|---|
| snake_case for PostgreSQL | `user_vehicle`, `created_date` | `reminderId`, `vehicleId` (camelCase in DB) |
| Singular or plural — pick one | All singular OR all plural | `users` table + `vehicle` table (mixed) |
| FK columns match target PK name | `user_vehicle.user_id` → `users.user_id` | `user_vehicle.uid` → `users.user_id` |
| No reserved words | `status_code`, `user_type` | `type`, `status`, `order` |
| Consistent prefixes | `sc_access_token`, `sc_refresh_token` | `smartcar_token`, `sc_refresh` (inconsistent) |
| DynamoDB: pick one convention | All camelCase or all PascalCase | `vehicleTelematics` + `VehicleClumping` (mixed) |

---

## Query Scorecard — 5 Categories

### 1. Correctness (25%)

*Does the query return the right data in all cases?*

**Static analysis checks the agent performs:**

| Check | How agent detects it | Confidence |
|---|---|---|
| NULL exclusion in WHERE != | Column allows NULL (no NOT NULL constraint) + query uses `!= value` | **Confirmed** — SQL standard: `NULL != x` is NULL, not TRUE |
| Wrong JOIN type | Entity annotation has `optional = true` but query uses INNER JOIN | **Confirmed** |
| Missing JOIN condition | JOIN without matching ON clause → cartesian product | **Confirmed** |
| N+1 lazy loading | `@OneToMany(fetch = LAZY)` + caller iterates and accesses each child | **Confirmed** |
| Pagination gaps | OFFSET-based pagination + concurrent inserts possible | **Potential** — known pattern |
| Missing GROUP BY | Aggregate function without GROUP BY on non-aggregated columns | **Confirmed** |
| Type mismatch on parameter | Java type doesn't match column type (String vs UUID) | **Confirmed** |

**Confidence prefixes:** Every correctness finding must be labeled **Confirmed** (provable from code), **Potential** (known pattern, can't verify impact), or **N/D** (not determinable).

### 2. Performance (30%)

*Is the query efficient under load?*

| Check | What to look for |
|---|---|
| Index utilization | Does an index exist that covers the WHERE + JOIN + ORDER BY columns? |
| SELECT * over-fetch | Query returns all columns when caller uses only a subset |
| N+1 queries | Lazy-loaded relationship accessed in a loop |
| Unnecessary JOINs | Table joined but no column from it used in SELECT or WHERE |
| Scan vs Query (DynamoDB) | DynamoDB scan operation = always flag as Performance F |
| Sort in application | Results sorted in Java/code when ORDER BY in the query would use an index |

### 3. Security (20%)

*Is the query safe from injection and data exposure?*

| Check | What to look for |
|---|---|
| Parameterized queries | String concatenation in SQL = F. Spring Data derived methods and `@Query` with `:param` = safe. |
| Authorization scoping | Does the query filter by user_id / tenant_id? Or does it return all data? |
| Sensitive column exposure | SELECT * returning token/PII columns to callers that don't need them |
| Native query injection risk | `nativeQuery = true` with string interpolation |

### 4. Resilience (15%)

*Does the query handle failure gracefully?*

| Check | What to look for |
|---|---|
| Timeout configuration | Is there a query timeout? Long-running queries block connection pool. |
| Transaction scope | Is the transaction wider than necessary? (e.g., wrapping reads + external API calls) |
| Connection pool pressure | Query holds connection during external calls or sleep |
| Retry logic | Write queries that should be idempotent — is retry safe? |
| Empty result handling | Does the caller handle empty Optional / null / empty list? |

### 5. Maintainability (10%)

*Can the next developer understand and safely modify this?*

| Check | What to look for |
|---|---|
| Method naming | Does the name describe the intent? (`findActiveVehiclesForUser` > `findByUserVehicles_UserIdAndVehicleStatusNot`) |
| Single responsibility | One query does one thing — not a multi-purpose method with flag parameters |
| Query complexity | > 3 JOINs or > 5 WHERE conditions = add a comment explaining intent |
| Derived name readability | Spring Data derived names > 40 chars = consider `@Query` instead |

---

## Recommendation Priorities

| Priority | Meaning | ADO Equivalent | Examples |
|---|---|---|---|
| **P1** | Security hole, data loss risk, correctness bug | Critical | Plaintext tokens, SQL injection, missing cascades causing orphans |
| **P2** | Data integrity gap, performance degradation | High | Missing FK constraints, unindexed JOINs, float8 for money |
| **P3** | Tech debt with real cost, should fix | Medium | Mixed naming, timestamp without timezone, oversized varchar |
| **P4** | Cleanup, improves hygiene | Low | Rename for consistency, add comments, minor type tightening |

## Effort Estimates

| Effort | Meaning |
|---|---|
| **XS** | Single migration or config change, < 1 hour |
| **S** | 1-2 files, < half day |
| **M** | Multiple files + migration + testing, 1-2 days |
| **L** | Cross-service coordination or data backfill, 3-5 days |
| **XL** | Major refactor or schema redesign, > 1 week |
