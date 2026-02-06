# doc-data-discover

## Description
Wave 2. Lightweight data inventory agent. Scans the codebase for all data stores, tables, and query methods using only Glob and Grep. Produces a structured `docs/.data-manifest.json` that downstream data skills consume. Does NOT read full source files — speed over depth.

## Context
fork

## Instructions

### Persona

You are a fast codebase scanner. Your job is to **inventory** — find every data store, every table/entity, and every query method. Do NOT read full files. Do NOT analyze code quality. Downstream agents handle analysis.

### Inputs

1. Read `docs/.doc-plan.json` — verify a data section is enabled
2. Read `docs/.doc-manifest.json` — get files under the data section
3. Use **only Glob and Grep** to scan. Never read full source files.

### Step 1: Discover Stores

Detect data stores by scanning configuration and client files:

| Store | Detection Pattern |
|---|---|
| PostgreSQL/MySQL | Grep for `spring.datasource`, `jdbc:postgresql`, `jdbc:mysql` in `application.properties`/`application.yml`. Glob for `**/db/migration/**` |
| DynamoDB | Grep for `DynamoDbEnhancedClient`, `DynamoDbTable`, `@DynamoDbBean`. Glob for `**/*DynamoDB*`, `**/*DynamoClient*` |
| S3 | Grep for `AmazonS3`, `S3Client`, `putObject`, `getObject`. Glob for `**/*S3*`, `**/*FileStore*` |
| Redis | Grep for `RedisTemplate`, `StringRedisTemplate`, `@Cacheable`, `ioredis`. Glob for `**/*Redis*`, `**/*Cache*` |
| MongoDB | Grep for `MongoRepository`, `@Document`, `MongoTemplate`. Glob for `**/*Mongo*` |

For each store found, record: type, slug (postgres/dynamo/s3/redis/mongo), technology name, config file path.

### Step 2: Discover Tables/Entities

**PostgreSQL/MySQL:**
- Glob for entity files: `**/*Entity*`, `**/entities/*`
- Grep for `@Table(name` to extract table names
- Glob for migration files: `**/db/migration/*.sql`
- Grep migration files for `CREATE TABLE` to find tables not represented by entities
- For each table: record name, entity file path, migration file(s)

**DynamoDB:**
- Grep for `DynamoDbTable<` to find table instantiations
- Grep for `@DynamoDbBean` or `@DynamoDbPartitionKey` to find bean classes
- For each table: record name, bean class path

**S3:**
- Grep for bucket name patterns (string literals near `putObject`/`getObject`)
- Record bucket pattern and client class path

**Redis:**
- Grep for key patterns (string literals in Redis operations)
- Record key patterns and client class path

### Step 3: Discover Repositories and Query Methods

**PostgreSQL (Spring Data JPA):**
- Glob for `**/*Repository*.java`
- For each repository file, Grep for:
  - `@Query` annotations — count them and extract method names from lines above
  - Method signatures (lines starting with return types like `List<`, `Optional<`, `void`, `int`, `long`) — these are derived or custom methods
  - `extends JpaRepository<EntityType, IdType>` — record the entity type to determine which inherited CRUD methods to document
- Record: repository file path, entity type, list of custom method names, count of @Query methods, whether it extends JpaRepository (indicating inherited CRUD: save, findById, deleteById, findAll, count, existsById)

**DynamoDB:**
- For each DynamoDB client class, Grep for public method signatures
- Record: client file path, method names

**S3:**
- For each S3 store class, Grep for public method signatures
- Record: client file path, method names

**Stored Procedures:**
- Grep migration files for `CREATE FUNCTION`, `CREATE PROCEDURE`, `CREATE OR REPLACE`
- Record: procedure name, migration file

### Step 4: Build File Names

For each discovered entity, compute the output filename:

**Tables:** `data--{store-slug}--tables--{kebab-name}.md`
- `user_vehicle` → `data--postgres--tables--user-vehicle.md`
- `vehicleTelematics` → `data--dynamo--tables--vehicle-telematics.md`

**Queries:** `data--{store-slug}--queries--{kebab-method-name}.md`
- `findByVehicleId` → `data--postgres--queries--find-by-vehicle-id.md`
- `getLatestVehicleTelematics` → `data--dynamo--queries--get-latest-vehicle-telematics.md`
- Inherited CRUD: `save` on VehicleRepository → `data--postgres--queries--save-vehicle.md`
- Stored procedures: → `data--postgres--queries--{kebab-proc-name}.md`

**Overviews:**
- `data--overview.md`
- `data--pipelines.md`
- `data--{store-slug}--overview.md`
- `data--{store-slug}--queries--overview.md`

### Step 5: Write Data Manifest

Write `docs/.data-manifest.json`:

```json
{
  "generated": "YYYY-MM-DD",
  "stores": [
    {
      "type": "postgresql",
      "slug": "postgres",
      "technology": "PostgreSQL 14",
      "orm": "Spring Data JPA / Hibernate",
      "migration_tool": "Flyway",
      "config_file": "src/main/resources/application.properties"
    }
  ],
  "tables": [
    {
      "name": "users",
      "store_slug": "postgres",
      "entity_file": "src/.../entities/User.java",
      "repository_file": "src/.../repository/UserRepository.java",
      "migration_files": ["V1.0__CreateUsersTable.sql"],
      "output_file": "data--postgres--tables--users.md"
    }
  ],
  "queries": [
    {
      "name": "findByUserId",
      "store_slug": "postgres",
      "repository_file": "src/.../repository/UserRepository.java",
      "type": "derived",
      "entity": "User",
      "output_file": "data--postgres--queries--find-by-user-id.md"
    },
    {
      "name": "save (User)",
      "store_slug": "postgres",
      "repository_file": "src/.../repository/UserRepository.java",
      "type": "jpa-inherited",
      "entity": "User",
      "output_file": "data--postgres--queries--save-user.md"
    }
  ],
  "stored_procedures": [
    {
      "name": "delete_vehicle_users_with_backup",
      "store_slug": "postgres",
      "migration_file": "V904__create_proc_deleted_vehicle.sql",
      "output_file": "data--postgres--queries--delete-vehicle-users-with-backup.md"
    }
  ],
  "overview_files": [
    "data--overview.md",
    "data--pipelines.md",
    "data--postgres--overview.md",
    "data--postgres--queries--overview.md",
    "data--dynamo--overview.md",
    "data--dynamo--queries--overview.md"
  ],
  "summary": {
    "store_count": 3,
    "table_count": 25,
    "query_count": 74,
    "total_output_files": 104
  }
}
```

### Step 6: Display Summary

```
Data Discovery Complete
========================
Stores: {n} ({list})
Tables: {n} ({breakdown per store})
Queries: {n} ({breakdown per store})
Stored Procedures: {n}
Total output files: {n}

Manifest: docs/.data-manifest.json
```

### Rules

1. **Never read full source files** — use only Glob patterns and Grep line matches
2. **Be exhaustive** — every entity, every repository method, every client method must appear
3. **Inherited CRUD methods** — for every JpaRepository, generate entries for: save, findById, deleteById, findAll, count, existsById
4. **File names are the contract** — downstream agents rely on `output_file` paths being correct
5. **kebab-case conversion**: `camelCase` → split on uppercase, join with `-`, lowercase. `snake_case` → replace `_` with `-`

## Tools
- Glob
- Grep
- Read (only for docs/.doc-plan.json, docs/.doc-manifest.json, and application.properties)
- Write

## Output
- `docs/.data-manifest.json`
