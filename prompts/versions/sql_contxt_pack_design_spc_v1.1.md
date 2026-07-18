# SQL Context Pack — Architecture, Security, Skill, and Implementation Prompt Specification

**Status:** Proposed v1.1  
**Recommended GitHub repository:** `sql-context-pack`  
**CLI command:** `sqlctx`  
**Service process:** `sqlctx-server`  
**MCP server name:** `SQL Context Pack`  
**Agent Skill name:** `sql-context-pack`  
**Export bundle extension:** `.sqlctx.zip`

### Revision v1.1

This revision adds:

- user-selectable category materialization modes,
- a default ask-before-materialization workflow,
- two-pass classification,
- full-database analysis before category filtering,
- final relationship-aware reclassification,
- separate analysis and materialization counts,
- boundary relationship metadata for excluded objects,
- validation rules for selective outputs.

The central invariant is:

```text
User category selection controls what is materialized into the project.
It must never reduce the database objects analyzed by the server.
```

---

## 1. Naming Decision

### 1.1 Recommended name: SQL Context Pack

Use **SQL Context Pack** as the product name and `sql-context-pack` as the GitHub repository name.

The name describes the real responsibility of the system:

- Extract SQL schema definitions.
- Extract stored routine definitions.
- Attach sanitized representative sample data.
- Classify database objects into business categories.
- Build indexes and relationship metadata.
- Package the result as AI-ready context.
- Expose the capability through HTTP and MCP.
- Prepare metadata for later ER diagram and graph rendering.

Do **not** use `db-dump-skills` as the primary name. “Dump” describes only extraction and does not communicate masking, classification, indexing, relationship analysis, or AI context packaging.

### 1.2 Names to avoid

- `sql-context-forge`: avoid brand confusion with IBM ContextForge.
- `sql-dump-skill`: too narrow.
- `database-rag`: implies a retrieval system that is not required in v1.
- `schema-seed`: could be confused with database seed-data generation.
- Names containing `agrimap`: the project must remain vendor- and organization-neutral.

### 1.3 Repository/component naming

```text
sql-context-pack/
├── packages/
│   ├── sqlctx-core/
│   ├── sqlctx-server/
│   ├── sqlctx-cli/
│   └── sqlctx-skill/
├── adapters/
│   ├── sqlserver/
│   ├── mysql/
│   ├── mariadb/
│   ├── oracle/
│   └── postgres/
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

A single Python distribution may be used for v1, but the internal modules must retain these boundaries.

---

## 2. Product Boundary

### 2.1 Required scope

Version 1 must provide:

1. Database connection profiles configured and started by the owner.
2. Schema discovery for supported relational databases.
3. Preliminary name-based category discovery.
4. User-selectable materialization mode: ask, all categories, or selected categories.
5. Full extraction and analysis of every permitted object regardless of the selected output categories.
6. Final relationship-aware category classification after full extraction.
7. Table DDL extraction.
8. Stored procedure extraction.
9. Masked representative sample rows for tables.
10. SQLFluff formatting.
11. Unknown-category escalation to the owner.
12. Object, dependency, relationship, tag, and graph-ready indexes.
13. Boundary metadata for analyzed objects intentionally excluded from selective output.
14. HTTP API.
15. MCP tools and resources over the same application core.
16. Paginated sitemap and resumable batch extraction/export.
17. Configurable client-side output directory.
18. Separate analysis-completeness and materialization-completeness validation.
19. No database username or password exposed to the agent/model.
20. No persistent temporary directories created inside the target project.
21. SQLFluff install, status, and explicit update lifecycle.
22. Detailed reports for partial failures without stopping the whole export.

### 2.2 Explicitly out of scope for v1

Do not add these features unless separately requested:

- Natural-language querying of production data.
- Arbitrary SQL execution.
- INSERT, UPDATE, DELETE, DDL mutation, or migration execution.
- Automatic database schema changes.
- Vector database or embedding generation.
- Full text-to-SQL.
- Web administration UI.
- Cloud-hosted credential vault.
- Automatic business-category invention without owner confirmation.
- ER diagram rendering itself; v1 only produces graph-ready metadata.
- Continuous database change-data capture.
- Background scheduling.
- Database backup/restore.

---

## 3. Core Architectural Decision

### 3.1 Choose Python, not Node.js

Use Python as the primary implementation language.

#### Reasons

1. SQLFluff is a Python package and can be called through its Python module or CLI without introducing a second runtime.
2. The system requires database adapters, masking, structured export, filesystem packaging, FastAPI, and MCP integration; all are available in one Python runtime.
3. A Node.js implementation would still require Python or an external SQLFluff executable, creating:
   - runtime coordination,
   - subprocess error handling,
   - duplicated dependency management,
   - cross-platform PATH issues,
   - more complex installation and update behavior.
4. Python provides mature database drivers for SQL Server, MySQL, MariaDB, Oracle, and PostgreSQL.
5. The official MCP Python SDK supports tools, resources, and common transports.

### 3.2 High-level component diagram

```text
Owner
  │
  ├─ creates connection profile
  ├─ provides credentials through environment/secret mechanism
  └─ starts sqlctx-server
          │
          ▼
Agent Skill / CLI / MCP Client
          │
          ├─ HTTP API
          └─ MCP tools/resources
                  │
                  ▼
          SQL Context Application Core
          ├─ Connection Profile Resolver
          ├─ Database Adapter Registry
          ├─ Name Inventory and Category Preview
          ├─ Materialization Selection Manager
          ├─ Full DDL/Routine Extractor
          ├─ Sample Extractor
          ├─ Sensitive Data Classifier
          ├─ Masking/Pseudonymization Engine
          ├─ SQLFluff Manager
          ├─ Two-pass Category Classifier
          ├─ Dependency and Relationship Analyzer
          ├─ Materialization Planner
          ├─ Graph Metadata Builder
          ├─ Export Job Manager
          └─ Bundle/Manifest Writer
                  │
                  ▼
             Read-only Database
```

### 3.3 One core, two interfaces

HTTP and MCP must call the same application services. Business rules must not be duplicated in route handlers or MCP tool functions.

```text
HTTP Router ─┐
             ├─> Application Services ─> Domain/Core ─> Adapters
MCP Server ──┘
```

---

## 4. Security Model

### 4.1 Credential ownership

The owner must configure credentials and start the server before an agent uses it.

The model/agent may know only:

- connection profile name,
- database engine,
- permitted schema names,
- server capability metadata,
- export job identifiers.

The model/agent must never receive:

- database hostname when hidden by policy,
- database username,
- database password,
- connection string,
- client secret,
- private key,
- credential-bearing environment variables.

### 4.2 Connection profiles

Default profile location:

```text
Linux/macOS: ~/.config/sql-context-pack/profiles.yaml
Windows:     %APPDATA%\sql-context-pack\profiles.yaml
```

A profile must reference environment-variable names rather than storing a password directly.

```yaml
profiles:
  agrimap-readonly:
    engine: sqlserver
    host_env: SQLCTX_AGRIMAP_DB_HOST
    port: 1433
    database_env: SQLCTX_AGRIMAP_DB_NAME
    username_env: SQLCTX_AGRIMAP_DB_USER
    password_env: SQLCTX_AGRIMAP_DB_PASSWORD
    allowed_schemas:
      - agrimap_app
    allowed_object_types:
      - table
      - procedure
    sample_rows_per_table: 10
    max_sample_rows_per_table: 20
    masking_policy: strict
```

Rules:

- Never return resolved environment values through an API.
- Never log resolved environment values.
- Never serialize a complete connection string.
- Error responses must reference the profile name, not the credentials.
- A profile file containing a raw password must be rejected by default.
- Optional OS keychain integration may be added later but is not required in v1.

### 4.3 Database account

Require a dedicated read-only database account.

The account should have only:

- metadata/catalog read permission,
- object-definition read permission,
- SELECT permission on explicitly allowed schemas/tables.

It must not have:

- INSERT,
- UPDATE,
- DELETE,
- ALTER,
- CREATE,
- DROP,
- EXECUTE unless metadata extraction genuinely requires it,
- server administration permission.

### 4.4 No arbitrary SQL

Do not expose a generic endpoint such as:

```text
POST /query
POST /execute
tool: run_sql
```

All SQL must be generated from reviewed adapter templates.

Identifiers must be:

- discovered from the database catalog, or
- validated against the discovered catalog,
- quoted by the database adapter,
- never concatenated directly from untrusted input.

### 4.5 Server network boundary

Default behavior:

```text
Host: 127.0.0.1
Remote access: disabled
Authentication: random local bearer token
```

For remote HTTP mode:

- TLS is mandatory.
- Authentication/authorization is mandatory.
- Apply least-privilege scopes.
- Add per-client rate limiting.
- Record audit metadata without recording sample values.
- Do not enable remote mode by default.

For local MCP STDIO mode:

- obtain database credentials from the environment of the server process,
- never pass credentials as MCP tool parameters.

### 4.6 Audit log

The audit log may include:

- timestamp,
- profile name,
- caller identity or local session identifier,
- requested schemas,
- object count,
- exported object IDs,
- row counts,
- masking rule IDs,
- result status,
- durations,
- content hashes.

The audit log must not include:

- raw DDL literals identified as secrets,
- raw sample values,
- passwords,
- tokens,
- connection strings.

---

## 5. Sensitive Data Cleansing

### 5.1 Cleansing must happen before serialization

Raw values must be classified and transformed inside the server process before they are:

- returned by HTTP,
- returned by MCP,
- written to an export file,
- placed in a bundle,
- written to a log,
- included in an exception message.

### 5.2 Detection layers

Apply detection in this order:

1. **Owner policy override**
2. **Database-native classification metadata**, where available
3. **Exact column-name rule**
4. **Column-name token rule**
5. **Data type and length heuristic**
6. **Value-pattern detector**
7. **Routine/DDL secret scanner**
8. **Conservative fallback**

Do not let an LLM inspect raw values to decide whether they are sensitive.

### 5.3 Required sensitive classes

At minimum:

```text
national_id
passport
username
password
password_hash
secret
secret_key
private_key
api_key
client_secret
access_token
refresh_token
jwt
session_token
cookie
email
phone
address
personal_name
financial_account
credit_card
date_of_birth
precise_location
biometric
```

### 5.4 Default transformations

| Class | Default transformation | Example output |
|---|---|---|
| national_id | format-preserving partial mask or synthetic alias | `1102001xxxxxx` |
| username | deterministic synthetic alias | `user_0007` |
| password | full replacement; never partial | `[REDACTED:PASSWORD]` |
| password_hash | full replacement with algorithm hint only | `[REDACTED:HASH:bcrypt]` |
| secret_key | full replacement | `[REDACTED:SECRET_KEY]` |
| api_key | full replacement | `[REDACTED:API_KEY]` |
| access_token | full replacement | `[REDACTED:ACCESS_TOKEN]` |
| refresh_token | full replacement | `[REDACTED:REFRESH_TOKEN]` |
| jwt | full replacement | `[REDACTED:JWT]` |
| email | deterministic synthetic alias | `user0007@example.invalid` |
| phone | format-preserving mask | `08xxxx1234` |
| personal_name | deterministic synthetic alias | `PERSON_0007` |
| address | generalized replacement | `[REDACTED:ADDRESS]` |
| credit_card | keep last four only | `xxxxxxxxxxxx4242` |
| binary/blob | omit content and report length | `<BINARY length=2048>` |

A fake password-like value such as `dPtv2oGEZLFvC3G1yiftC...` may be generated only when the policy explicitly requests **synthetic format preservation**. The default is a clear redaction marker, because fake secrets that look valid can be mistaken for real credentials.

### 5.5 Referential consistency

When a value is used as a business key or relation key, masking must remain stable within the snapshot.

Use deterministic pseudonymization:

```text
alias = HMAC-SHA256(snapshot_masking_key, normalized_value)
```

Map the result to the target format, for example:

```text
username -> user_0007
email    -> user0007@example.invalid
```

Requirements:

- The masking key must never be included in the export.
- The same raw value within one snapshot must map to the same alias.
- Different snapshots should use different keys by default.
- Owner-configured stable keys may be supported, but must remain outside the model context.
- Foreign-key values must retain join consistency after transformation.

### 5.6 Fail-closed behavior

If a value is probably sensitive but cannot be classified confidently:

- do not emit the raw value,
- replace it with `[REDACTED:UNCLASSIFIED]`,
- add a warning to the masking report,
- allow the owner to add a policy override and rerun.

### 5.7 Stored procedure and DDL source scanning

Sensitive values can be hardcoded inside routines, comments, default constraints, or dynamic SQL.

Before writing routine/DDL text:

- scan quoted string literals,
- scan comments,
- detect JWTs, API keys, connection strings, passwords, and private keys,
- replace only the literal content while preserving valid SQL quoting,
- record the transformation location and detector rule in metadata,
- never write the original literal to the report.

Example:

```sql
SET @API_KEY = '[REDACTED:API_KEY]';
```

---

## 6. Database and SQLFluff Dialect Mapping

| Database engine key | SQLFluff dialect | Initial Python driver | Notes |
|---|---|---|---|
| `sqlserver` | `tsql` | `pyodbc` | SQL Server / T-SQL |
| `mysql` | `mysql` | `pymysql` or `mysql-connector-python` | Keep separate from MariaDB adapter |
| `mariadb` | `mariadb` | MariaDB Connector/Python or compatible reviewed driver | SQLFluff dialect inherits from MySQL but must remain a distinct adapter |
| `oracle` | `oracle` | `oracledb` | SQLFluff Oracle dialect includes PL/SQL |
| `postgres` | `postgres` | `psycopg` | `psql` is a client command, not the SQLFluff dialect name |

At runtime, expose the installed canonical dialect list from:

```bash
sqlfluff dialects
```

Do not hardcode a claim that a dialect is supported without verifying it against the installed SQLFluff version.

---

## 7. Database Adapter Contract

Each adapter must implement this interface conceptually:

```python
class DatabaseAdapter(Protocol):
    engine: str
    sqlfluff_dialect: str

    async def test_connection(self, profile: ResolvedProfile) -> ConnectionTestResult: ...
    async def get_server_info(self, profile: ResolvedProfile) -> ServerInfo: ...
    async def list_schemas(self, profile: ResolvedProfile) -> list[SchemaInfo]: ...
    async def discover_objects(
        self,
        profile: ResolvedProfile,
        request: DiscoveryRequest,
    ) -> AsyncIterator[DatabaseObject]: ...
    async def get_table_definition(
        self,
        profile: ResolvedProfile,
        object_ref: ObjectRef,
    ) -> SqlDefinition: ...
    async def get_procedure_definition(
        self,
        profile: ResolvedProfile,
        object_ref: ObjectRef,
    ) -> SqlDefinition: ...
    async def get_table_columns(
        self,
        profile: ResolvedProfile,
        object_ref: ObjectRef,
    ) -> list[ColumnMetadata]: ...
    async def get_constraints(
        self,
        profile: ResolvedProfile,
        object_ref: ObjectRef,
    ) -> list[ConstraintMetadata]: ...
    async def get_foreign_keys(
        self,
        profile: ResolvedProfile,
        object_ref: ObjectRef,
    ) -> list[ForeignKeyMetadata]: ...
    async def get_sample_rows(
        self,
        profile: ResolvedProfile,
        request: SampleRequest,
    ) -> SamplePage: ...
    async def get_routine_dependencies(
        self,
        profile: ResolvedProfile,
        object_ref: ObjectRef,
    ) -> list[DependencyEdge]: ...
```

### 7.1 SQL Server metadata sources

Use reviewed queries against:

```text
sys.schemas
sys.tables
sys.columns
sys.types
sys.indexes
sys.index_columns
sys.key_constraints
sys.foreign_keys
sys.foreign_key_columns
sys.procedures
sys.sql_modules
sys.parameters
sys.extended_properties
sys.sql_expression_dependencies
```

Use `OBJECT_DEFINITION()` or `sys.sql_modules.definition` for routines where permitted.

### 7.2 MySQL metadata sources

Use reviewed queries against:

```text
information_schema.SCHEMATA
information_schema.TABLES
information_schema.COLUMNS
information_schema.TABLE_CONSTRAINTS
information_schema.KEY_COLUMN_USAGE
information_schema.ROUTINES
information_schema.PARAMETERS
```

Use engine-supported `SHOW CREATE TABLE` and reviewed routine-definition retrieval where privileges permit.

### 7.3 MariaDB metadata sources

Use a distinct MariaDB adapter even where catalog structures resemble MySQL.

Reasons:

- syntax and metadata behavior can diverge,
- SQLFluff exposes a distinct `mariadb` dialect,
- future MariaDB-specific behavior must not be hidden in a MySQL conditional.

### 7.4 Oracle metadata sources

Use owner-permitted views and APIs such as:

```text
ALL_USERS or USER_USERS
ALL_TABLES
ALL_TAB_COLUMNS
ALL_CONSTRAINTS
ALL_CONS_COLUMNS
ALL_PROCEDURES
ALL_ARGUMENTS
ALL_SOURCE
ALL_DEPENDENCIES
DBMS_METADATA.GET_DDL
```

Capabilities must be discovered at runtime because access to `DBMS_METADATA` and `ALL_*` views varies by account privileges.

### 7.5 PostgreSQL metadata sources

Use reviewed queries against:

```text
pg_catalog.pg_namespace
pg_catalog.pg_class
pg_catalog.pg_attribute
pg_catalog.pg_constraint
pg_catalog.pg_index
pg_catalog.pg_proc
pg_catalog.pg_depend
information_schema.columns
information_schema.routines
```

Use functions such as:

```text
pg_get_functiondef
pg_get_viewdef
pg_get_constraintdef
pg_get_indexdef
```

### 7.6 Capability negotiation

Each adapter must return:

```json
{
  "engine": "sqlserver",
  "server_version": "masked-or-policy-allowed",
  "sqlfluff_dialect": "tsql",
  "supports": {
    "tables": true,
    "procedures": true,
    "functions": false,
    "packages": false,
    "routine_dependencies": true,
    "native_comments": true,
    "native_classification": false,
    "deterministic_sampling": true
  },
  "limits": {
    "max_batch_objects": 25,
    "recommended_batch_objects": 10,
    "max_sample_rows_per_table": 20
  }
}
```

The skill must use capabilities instead of assuming every engine supports the same object types.

---

## 8. Sample Data Strategy

### 8.1 Required row count

Default:

```text
target sample rows per table = 10
```

Behavior:

- If the table contains at least 10 eligible rows, export exactly 10.
- If the table contains fewer than 10 rows, export the actual available count.
- Never duplicate or fabricate production rows merely to reach 10.
- Record `requested_count`, `actual_count`, and `shortage_reason`.
- If policy removes every eligible row, emit zero rows and a masking/policy warning.

### 8.2 Deterministic selection

Default strategy:

1. Use the primary key ordered ascending.
2. Otherwise use the first unique non-null index.
3. Otherwise use a deterministic engine-supported physical or hash strategy where safe.
4. Otherwise return a non-deterministic sample and mark it explicitly.

Do not use expensive full-table random sorting by default.

### 8.3 Query limits

- Select only required columns.
- Limit text values by configured maximum length.
- Do not read large binary/LOB values by default.
- Apply database statement timeout.
- Cancel the query if the client cancels the job.
- Use a small connection pool.
- Use a configurable concurrency limit.
- Do not issue `COUNT(*)` on every large table merely to know whether ten rows exist.
- Fetch `target + 1` only when needed to detect continuation.

### 8.4 Relationship-aware samples

Version 1 may support an optional mode:

```yaml
sample_strategy: relationship_aware
```

It may select rows that preserve a useful subset of foreign-key relationships. This mode is optional and must not replace the deterministic default.

### 8.5 Sample representation inside table SQL

The table `.sql` file must remain valid SQL and self-contained for an AI model.

Processing order:

1. Extract DDL.
2. Clean sensitive literals in DDL.
3. Format only the SQL definition with SQLFluff.
4. Append masked sample rows as SQL line comments.
5. Do not run SQLFluff over the appended sample block.

Example:

```sql
CREATE TABLE [agrimap_app].[UM_USER] (
    [ID] NUMERIC(38, 0) NOT NULL,
    [USERNAME] NVARCHAR(100) NOT NULL,
    [PASSWORD] NVARCHAR(255) NOT NULL
);

-- @sqlctx-samples-begin requested=10 actual=10 masked=true
-- {"ID":1,"USERNAME":"user_0001","PASSWORD":"[REDACTED:PASSWORD]"}
-- {"ID":2,"USERNAME":"user_0002","PASSWORD":"[REDACTED:PASSWORD]"}
-- @sqlctx-samples-end
```

Additional metadata belongs in the object index, not in arbitrary prose inside the SQL body.

---

## 9. SQLFluff Lifecycle

### 9.1 Installation guarantee

A Skill Markdown file alone cannot guarantee installation. The repository must include executable bootstrap logic.

Use both layers:

1. Declare SQLFluff as a pinned Python dependency in `pyproject.toml`.
2. Add a runtime `ensure` command that verifies the package and CLI before formatting.

Required commands:

```bash
sqlctx doctor
sqlctx sqlfluff status
sqlctx sqlfluff ensure
sqlctx sqlfluff update
sqlctx sqlfluff update --version X.Y.Z
```

### 9.2 Managed runtime location

Do not install tools into the target project.

Preferred managed locations:

```text
Linux/macOS: ~/.local/share/sql-context-pack/runtime/
Windows:     %LOCALAPPDATA%\sql-context-pack\runtime\
```

Store installation state outside the project:

```json
{
  "python_version": "3.x",
  "sqlfluff_version": "X.Y.Z",
  "installed_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "install_source": "locked-dependency"
}
```

### 9.3 Ensure algorithm

```text
1. Check importlib.metadata.version("sqlfluff").
2. Check `python -m sqlfluff version`.
3. Compare with the project lock/allowed version range.
4. If valid, reuse it and do not install.
5. If missing:
   a. acquire a cross-process installation lock;
   b. recheck after lock acquisition;
   c. install the pinned version once;
   d. verify import and CLI;
   e. write runtime state atomically.
6. If installation fails, stop formatting and return a clear TOOLING_UNAVAILABLE error.
7. Never silently install `latest` during a normal export.
```

### 9.4 Update algorithm

An update must occur only after an explicit owner/user request.

```text
1. Resolve requested version or latest stable version.
2. Validate it against supported Python versions.
3. Install into a new managed runtime directory.
4. Run self-tests and dialect checks.
5. Switch the active runtime pointer atomically.
6. Keep one previous version for rollback.
7. Remove older inactive versions.
8. Do not modify the target project.
```

### 9.5 Required formatting command semantics

Equivalent configuration:

```bash
python -m sqlfluff format \
  --exclude-rules "CP02,LT01,RF06" \
  --dialect tsql \
  --templater raw \
  XXXXX.sql
```

For other engines, replace only the dialect:

```text
sqlserver -> tsql
mysql     -> mysql
mariadb   -> mariadb
oracle    -> oracle
postgres  -> postgres
```

### 9.6 Do not format a directory in production orchestration

Although SQLFluff accepts a directory, the exporter must invoke SQLFluff **one file at a time**.

Reason:

- one unparsable file must not prevent other files from being formatted,
- each file needs its own result, timing, error, and fallback,
- the original file must remain available when formatting fails.

### 9.7 Per-file fail-isolated algorithm

```text
For every extracted SQL object:

1. Keep the cleaned, unformatted SQL in memory.
2. Create a temporary file in the operating-system temp directory.
3. Run:
   python -m sqlfluff parse --dialect <dialect> --templater raw <temp-file>
4. If parse fails:
   a. do not format;
   b. preserve the cleaned original SQL;
   c. mark format_status=parse_failed;
   d. capture sanitized diagnostics;
   e. continue to the next file.
5. If parse succeeds:
   a. run sqlfluff format on the temporary file;
   b. run parse again on the formatted temporary file;
   c. if post-format parse succeeds, use formatted content;
   d. otherwise use the cleaned original content and mark rollback.
6. Append the masked sample comment block after formatting.
7. Write the final target file atomically.
8. Delete the OS temporary file in a finally block.
9. Continue regardless of a single-object failure.
```

Never enable:

```text
fix_even_unparsable
--FIX-EVEN-UNPARSABLE
```

### 9.8 Exit-code handling

Interpret SQLFluff subprocess results explicitly:

```text
0 = success
1 = operation completed with violations or parse issue
2 = operational/configuration/internal error
```

Do not treat every non-zero result as the same failure type.

### 9.9 No project temporary directories

The system must not create these inside the output project:

```text
.tmp-sql-finalizer/
.tmp-sqlfluff-format/
.tmp-*/
```

Temporary work must use:

```python
tempfile.TemporaryDirectory()
```

or the platform-specific user cache/runtime directory.

Cleanup requirements:

- use `try/finally`,
- close file handles before cleanup on Windows,
- retry deletion for transient file locks,
- run stale-runtime cleanup on startup,
- never leave a partially extracted target directory.

Optional defensive `.gitignore` entry:

```gitignore
# Defensive only; sqlctx must not create these in the project.
.tmp-*/
.sqlctx-staging/
```

The `.gitignore` entry is a final defense, not a substitute for correct cleanup.

---

## 10. Catalog, Category Selection, Full Analysis, Pagination, and Batch Export

### 10.1 Analysis scope and materialization scope are different

The system must maintain two independent scopes:

```text
analysis_scope:
  Every permitted table and stored procedure in the selected schemas.

materialization_scope:
  The objects whose SQL files are written into the user-selected project output.
```

Mandatory invariant:

```text
A category selection may reduce materialization_scope.
It must never reduce analysis_scope.
```

This prevents false exclusions caused by ambiguous names such as:

- an object whose prefix appears unrelated but is connected to the selected domain,
- a generic object such as `CONTENT`, `CONFIG`, `MASTER`, or `TRANSACTION`,
- a procedure whose name does not identify every table it reads or writes,
- a shared table used by more than one business category.

The full sanitized snapshot used for analysis stays in the server runtime store. It is not automatically written into the target project.

### 10.2 Two-pass classification lifecycle

The catalog lifecycle must run in this order.

#### Pass 1 — Preliminary classification

Use only inexpensive catalog information:

- schema,
- object type,
- object name,
- configured exact-name rules,
- configured prefix/token rules,
- database-native comments that are available without full object extraction.

Do not use:

- table samples,
- complete DDL,
- procedure bodies,
- foreign-key graph,
- procedure read/write dependencies.

Pass 1 exists only to create a category preview for the user. It must be labeled `preliminary`, not final.

#### User materialization selection

After Pass 1, the user may choose:

```text
all:
  Materialize every final category.

selected:
  Materialize only the categories selected by the user after Pass 2.

ask:
  Pause after category preview and ask whether to materialize all
  categories or selected categories.
```

`ask` is the default when the user has not explicitly requested all categories or named selected categories.

The selection records intent only. The server must still continue with full extraction of every permitted object.

#### Full extraction

After selection is recorded, extract and sanitize all permitted objects:

- table DDL,
- columns and data types,
- keys and constraints,
- foreign keys,
- stored procedure definitions,
- routine parameters,
- routine dependencies,
- up to the permitted sample-row count,
- database comments and extended metadata.

The extraction must be paginated, batched, resumable, and fail-isolated.

#### Pass 2 — Final contextual classification

Reclassify every object using the complete sanitized context:

- Pass 1 evidence,
- column names and data types,
- primary and foreign keys,
- incoming and outgoing relationships,
- stored procedure read/write/call edges,
- table and routine descriptions,
- sanitized sample shape and representative values,
- owner overrides.

An object may move to a different category between Pass 1 and Pass 2.

Examples:

```text
Pass 1:
  APP_OBJECT -> unresolved

Pass 2:
  APP_OBJECT has FK to CONTENT and is written by CONTENT_I
  -> final category: content
```

```text
Pass 1:
  CONTENT_CONFIG -> content

Pass 2:
  used only by global platform configuration procedures
  -> final category: platform_config
```

#### Materialization planning

Apply the user's selected category names to the **final Pass 2 categories**, not to the preliminary object list.

This guarantees:

- an initially ambiguous object that becomes `content` is included when `content` was selected,
- an initially `content`-looking object that becomes another category is excluded from strict `content` output,
- category selection remains semantically meaningful after relationship analysis.

### 10.3 Materialization modes

Request model:

```json
{
  "mode": "ask",
  "selected_categories": [],
  "dependency_materialization": "index_only"
}
```

Allowed `mode` values:

| Mode | Behavior |
|---|---|
| `ask` | Pause after Pass 1 and ask the owner to choose all or selected categories |
| `all` | Analyze all objects and materialize all final categories |
| `selected` | Analyze all objects and materialize only objects assigned to selected final categories |

Allowed `dependency_materialization` values:

| Value | Behavior |
|---|---|
| `index_only` | Default. Excluded related objects appear as boundary nodes/edges in indexes, but their SQL and samples are not written |
| `direct` | Also materialize directly referenced tables/procedures required to understand selected objects |
| `closure` | Materialize the complete reachable dependency closure, subject to configured depth and safety limits |

`closure` must not be the default because it can make a selective export nearly as large as an all-category export.

### 10.4 Category preview

The category preview must contain only safe object descriptors and preliminary category evidence.

```json
{
  "catalog_id": "cat_01J...",
  "classification_pass": "preliminary",
  "analysis_scope": {
    "discovered_objects": 842
  },
  "categories": [
    {
      "category": "um",
      "preliminary_count": 64,
      "examples": [
        "UM_USER",
        "UM_ROLE",
        "UM_USER_ROLE"
      ],
      "confidence_summary": {
        "confirmed_by_rule": 58,
        "suggested": 6
      }
    },
    {
      "category": "content",
      "preliminary_count": 103,
      "examples": [
        "CONTENT",
        "CONTENT_SHARE",
        "CONTENT_PERMISSION"
      ],
      "confidence_summary": {
        "confirmed_by_rule": 91,
        "suggested": 12
      }
    }
  ],
  "unresolved_count": 37,
  "warning": "Preliminary categories may change after full relationship analysis."
}
```

The preview must support cursor pagination when category members or examples exceed response limits.

### 10.5 Sitemap contents

A database may contain 100–1000 or more objects. The agent must not receive one huge response.

The sitemap must contain:

- object ID,
- engine,
- database/schema,
- object type,
- object name,
- preliminary category,
- final category when available,
- classification pass/status,
- materialization decision,
- inclusion/exclusion reason,
- dependency counts,
- extraction status,
- content fingerprint,
- estimated cost,
- recommended extraction/export batch.

Example final item:

```json
{
  "object_id": "table:agrimap_app.APP_OBJECT",
  "object_type": "table",
  "schema": "agrimap_app",
  "name": "APP_OBJECT",
  "preliminary_category": null,
  "final_category": "content",
  "classification_status": "suggested",
  "materialization": {
    "included": true,
    "reason": "final_category_selected"
  },
  "estimated_weight": 3
}
```

### 10.6 Cursor pagination

Use opaque cursors, not page numbers.

```json
{
  "items": [],
  "page": {
    "limit": 100,
    "returned": 100,
    "next_cursor": "opaque-cursor-or-null"
  },
  "batching": {
    "recommended_objects": 10,
    "maximum_objects": 25,
    "recommended_weight": 30
  }
}
```

Never stop merely because a page returned fewer items than requested. Stop only when `next_cursor` is null.

### 10.7 Skill pagination and completeness rule

The skill must maintain separate sets:

```text
all_discovered_object_ids
all_analyzed_object_ids
final_materialization_object_ids
intentionally_excluded_object_ids
failed_analysis_object_ids
```

Workflow:

```text
cursor = null
all_discovered_object_ids = []

repeat:
    call list_sitemap(cursor, limit, view="analysis")
    append returned object IDs
    cursor = next_cursor
until cursor is null

wait for full analysis to finish

cursor = null
final_materialization_object_ids = []

repeat:
    call list_sitemap(cursor, limit, view="materialization")
    append included object IDs
    record excluded object IDs and reasons
    cursor = next_cursor
until cursor is null

export only final_materialization_object_ids
verify:
    discovered = analyzed + failed_analysis
    analyzed = materialized + intentionally_excluded
```

In `all` mode, `intentionally_excluded` should normally be zero except for explicit security/policy exclusions.

In `selected` mode, discovered count and materialized count are expected to differ.

### 10.8 Weighted batching

Internal full extraction and final materialization exports must respect both:

- maximum object count,
- maximum estimated weight.

Suggested weights:

```text
simple table         = 1
wide table            = 2
table with samples    = 3
simple procedure      = 2
large procedure       = 5
Oracle package        = 8 (future)
```

A selected-category output must not cause the server to skip extraction of non-selected objects. It only reduces the final bundle content.

## 11. HTTP API Specification

Base path:

```text
/api/v1
```

### 11.1 Health

```http
GET /api/v1/health
```

Response `200`:

```json
{
  "status": "ok",
  "service": "sql-context-pack",
  "version": "1.0.0"
}
```

Must not test or expose every database profile.

### 11.2 Capabilities

```http
GET /api/v1/capabilities
```

Response `200`:

```json
{
  "engines": [
    {"engine":"sqlserver","sqlfluff_dialect":"tsql"},
    {"engine":"mysql","sqlfluff_dialect":"mysql"},
    {"engine":"mariadb","sqlfluff_dialect":"mariadb"},
    {"engine":"oracle","sqlfluff_dialect":"oracle"},
    {"engine":"postgres","sqlfluff_dialect":"postgres"}
  ],
  "object_types": ["table","procedure"],
  "interfaces": ["http","mcp"],
  "limits": {
    "sitemap_page_max": 250,
    "export_batch_max_objects": 25
  }
}
```

### 11.3 List safe profile descriptors

```http
GET /api/v1/profiles
```

Response:

```json
{
  "items": [
    {
      "profile": "agrimap-readonly",
      "engine": "sqlserver",
      "allowed_schemas": ["agrimap_app"],
      "ready": true
    }
  ]
}
```

Never return host, username, password, or connection string.

### 11.4 Test profile

```http
POST /api/v1/profiles/{profile}/test
```

Response `200`:

```json
{
  "profile": "agrimap-readonly",
  "reachable": true,
  "engine": "sqlserver",
  "capabilities": {
    "tables": true,
    "procedures": true
  }
}
```

### 11.5 Create catalog snapshot

```http
POST /api/v1/catalogs
Content-Type: application/json
```

Input:

```json
{
  "profile": "agrimap-readonly",
  "schemas": ["agrimap_app"],
  "object_types": ["table", "procedure"],
  "include_patterns": [],
  "exclude_patterns": [],
  "category_policy": "two_pass",
  "selection": {
    "mode": "ask",
    "selected_categories": [],
    "dependency_materialization": "index_only"
  },
  "sample": {
    "rows_per_table": 10,
    "strategy": "deterministic"
  },
  "masking_policy": "strict"
}
```

Behavior:

- `ask`: perform name inventory and Pass 1, then pause at `awaiting_selection`.
- `all`: record all-category intent and continue to full extraction.
- `selected`: require at least one selected category and continue to full extraction.
- All modes use the same full `analysis_scope`.

Response `202`:

```json
{
  "catalog_id": "cat_01J...",
  "status": "queued",
  "status_url": "/api/v1/catalogs/cat_01J..."
}
```

### 11.6 Get catalog status

```http
GET /api/v1/catalogs/{catalog_id}
```

Response while waiting for the user:

```json
{
  "catalog_id": "cat_01J...",
  "status": "awaiting_selection",
  "progress": {
    "phase": "preliminary_classification",
    "discovered": 842,
    "preliminary_classified": 805,
    "preliminary_unresolved": 37,
    "fully_analyzed": 0
  },
  "category_preview_url": "/api/v1/catalogs/cat_01J.../category-preview"
}
```

Response after final classification:

```json
{
  "catalog_id": "cat_01J...",
  "status": "ready",
  "progress": {
    "phase": "final_classification",
    "discovered": 842,
    "fully_analyzed": 838,
    "analysis_failed": 4,
    "final_classified": 826,
    "final_unresolved": 12,
    "materialization_included": 214,
    "materialization_excluded": 624
  },
  "sitemap_url": "/api/v1/catalogs/cat_01J.../sitemap",
  "materialization_plan_url": "/api/v1/catalogs/cat_01J.../materialization-plan"
}
```

Statuses:

```text
queued
discovering_names
preliminary_classifying
awaiting_selection
extracting_all_objects
analyzing_relationships
final_classifying
awaiting_resolution
ready
partial
failed
cancelled
```

### 11.7 Get preliminary category preview

```http
GET /api/v1/catalogs/{catalog_id}/category-preview?limit=100&cursor=...
```

The response uses the category-preview shape defined in Section 10.4.

The endpoint must clearly state that results are preliminary.

### 11.8 Set materialization selection

```http
POST /api/v1/catalogs/{catalog_id}/selection
```

Input for all categories:

```json
{
  "mode": "all",
  "selected_categories": [],
  "dependency_materialization": "index_only"
}
```

Input for selected categories:

```json
{
  "mode": "selected",
  "selected_categories": ["um", "content"],
  "dependency_materialization": "index_only"
}
```

Response `202`:

```json
{
  "catalog_id": "cat_01J...",
  "status": "extracting_all_objects",
  "analysis_scope": {
    "object_count": 842,
    "restricted_by_selection": false
  },
  "selection_intent": {
    "mode": "selected",
    "selected_categories": ["um", "content"]
  }
}
```

The selected categories must not be converted into database include/exclude filters.

### 11.9 Get paginated sitemap

```http
GET /api/v1/catalogs/{catalog_id}/sitemap?view=analysis&limit=100&cursor=...
GET /api/v1/catalogs/{catalog_id}/sitemap?view=materialization&limit=100&cursor=...
```

Use the response rules defined in Section 10.

### 11.10 Get materialization plan

```http
GET /api/v1/catalogs/{catalog_id}/materialization-plan
```

Response:

```json
{
  "selection": {
    "mode": "selected",
    "selected_categories": ["um", "content"],
    "dependency_materialization": "index_only"
  },
  "counts": {
    "discovered": 842,
    "fully_analyzed": 838,
    "analysis_failed": 4,
    "included": 214,
    "intentionally_excluded": 624
  },
  "classification_changes": {
    "moved_into_selected_categories": 11,
    "moved_out_of_selected_categories": 7
  },
  "boundary_relationships": 93,
  "unresolved_affecting_selection": 3
}
```

### 11.11 Get unresolved classifications

```http
GET /api/v1/catalogs/{catalog_id}/classification-requests
```

Response:

```json
{
  "existing_categories": ["um", "content"],
  "suggested_new_categories": ["audit"],
  "items": [
    {
      "object_id": "table:agrimap_app.APP_AUDIT_LOG",
      "evidence": [
        "name token AUDIT",
        "foreign key to UM_USER"
      ],
      "candidates": [
        {"category":"audit","confidence":0.78},
        {"category":"um","confidence":0.42}
      ]
    }
  ]
}
```

### 11.12 Resolve classifications

```http
POST /api/v1/catalogs/{catalog_id}/classification-resolutions
```

Input:

```json
{
  "resolutions": [
    {
      "object_id": "table:agrimap_app.APP_AUDIT_LOG",
      "category": "audit"
    }
  ],
  "persist_as_owner_override": true
}
```

Response `200`:

```json
{
  "resolved": 1,
  "remaining": 0
}
```

### 11.13 Create export batch

```http
POST /api/v1/exports
```

Input:

```json
{
  "catalog_id": "cat_01J...",
  "object_ids": [
    "table:agrimap_app.UM_USER",
    "procedure:agrimap_app.UM_USER_I"
  ],
  "format": {
    "sqlfluff": true,
    "exclude_rules": ["CP02","LT01","RF06"],
    "append_samples": true
  }
}
```

Response `202`:

```json
{
  "export_id": "exp_01J...",
  "status": "queued",
  "status_url": "/api/v1/exports/exp_01J..."
}
```

### 11.14 Get export status

```http
GET /api/v1/exports/{export_id}
```

Response:

```json
{
  "export_id": "exp_01J...",
  "status": "completed_with_warnings",
  "objects": {
    "requested": 2,
    "succeeded": 2,
    "parse_failed": 1,
    "failed": 0
  },
  "artifacts": {
    "bundle_url": "/api/v1/exports/exp_01J.../bundle",
    "manifest_url": "/api/v1/exports/exp_01J.../manifest"
  }
}
```

### 11.15 Download batch bundle

```http
GET /api/v1/exports/{export_id}/bundle
```

Response:

```text
200 application/zip
```

Bundle filename:

```text
exp_01J....sqlctx.zip
```

### 11.16 Get manifest

```http
GET /api/v1/exports/{export_id}/manifest
```

Response `200 application/json`.

### 11.17 Validate assembled output

```http
POST /api/v1/validations
```

Input:

```json
{
  "catalog_id": "cat_01J...",
  "export_ids": ["exp_1","exp_2"],
  "expected_discovered_count": 842,
  "expected_analyzed_count": 838,
  "expected_materialized_count": 214,
  "expected_output_layout_version": "1"
}
```

Response:

```json
{
  "valid": true,
  "checks": {
    "analysis_scope_accounted_for": true,
    "all_materialization_objects_exported": true,
    "intentional_exclusions_accounted_for": true,
    "no_duplicate_paths": true,
    "no_raw_secrets_detected": true,
    "boundary_relationships_recorded": true,
    "manifest_hashes_valid": true
  }
}
```

### 11.18 SQLFluff endpoints

```http
GET  /api/v1/tooling/sqlfluff
POST /api/v1/tooling/sqlfluff/ensure
POST /api/v1/tooling/sqlfluff/update
```

Update input:

```json
{
  "version": "latest-stable"
}
```

The update endpoint must require an explicit owner-authorized request.

### 11.19 HTTP status behavior

| Status | Meaning |
|---|---|
| `200` | Synchronous success |
| `202` | Job accepted |
| `400` | Invalid input |
| `401` | Missing/invalid API authentication |
| `403` | Profile or policy denies access |
| `404` | Unknown profile/catalog/export/object |
| `409` | Invalid job state or conflicting resolution |
| `413` | Batch or response exceeds configured limit |
| `422` | Unsupported engine/object/dialect/capability |
| `429` | Rate limit or concurrency limit |
| `500` | Sanitized internal error |
| `503` | Database/tooling temporarily unavailable |

Error shape:

```json
{
  "error": {
    "code": "SQLFLUFF_PARSE_FAILED",
    "message": "One SQL object could not be parsed; original cleaned SQL was preserved.",
    "retryable": false,
    "correlation_id": "corr_01J..."
  }
}
```

Never include raw database errors if they contain SQL text or values.

---

## 12. MCP Specification

MCP tools must mirror application commands, not raw HTTP mechanics.

### 12.1 Tools

```text
sqlctx_get_capabilities
sqlctx_list_profiles
sqlctx_test_profile
sqlctx_create_catalog
sqlctx_get_catalog_status
sqlctx_get_category_preview
sqlctx_set_materialization_selection
sqlctx_list_sitemap
sqlctx_get_materialization_plan
sqlctx_get_classification_requests
sqlctx_resolve_classifications
sqlctx_export_batch
sqlctx_get_export_status
sqlctx_validate_exports
sqlctx_sqlfluff_status
sqlctx_sqlfluff_ensure
sqlctx_sqlfluff_update
```

### 12.2 Resources

```text
sqlctx://catalog/{catalog_id}/category-preview
sqlctx://catalog/{catalog_id}/sitemap
sqlctx://catalog/{catalog_id}/materialization-plan
sqlctx://catalog/{catalog_id}/classification-requests
sqlctx://export/{export_id}/manifest
sqlctx://export/{export_id}/bundle
sqlctx://export/{export_id}/report
```

### 12.3 MCP tool behavior

Each tool must:

- define strict JSON Schema input,
- define structured output,
- return sanitized errors,
- be idempotent where possible,
- support cursor pagination where a list can grow,
- expose a human-readable summary and structured content,
- never accept credentials,
- never accept arbitrary SQL,
- never accept an unrestricted filesystem path.

### 12.4 Human control

Require explicit user confirmation for:

- installing SQLFluff when it requires network access,
- updating SQLFluff,
- creating a new persistent category override,
- enabling remote server access,
- changing masking policy from strict to a weaker policy.

Normal read-only catalog and export calls may be automated after the owner has started and authorized the server.

---

## 13. Two-pass Category Classification and User Selection

### 13.1 Mandatory two-pass invariant

Classification must run in two distinct passes.

```text
Pass 1:
  Preliminary category discovery from safe names and lightweight metadata.

Pass 2:
  Final classification from the complete sanitized object and relationship context.
```

The system must not collapse both passes into one model prompt or one opaque score.

The owner selects categories after seeing Pass 1, but that selection controls only final materialization.

```text
selected categories != database extraction filter
```

Every permitted object must still be extracted and analyzed before final output filtering.

### 13.2 Pass 1 — Preliminary category discovery

Allowed evidence:

1. Owner category rules
2. Exact object-name match
3. Prefix/token match
4. Schema name
5. Object type
6. Lightweight database comment/description

Pass 1 output:

```text
preliminary_confirmed:
  deterministic owner/config rule matched

preliminary_suggested:
  name/schema evidence suggests a category

preliminary_unresolved:
  no category or conflicting name evidence
```

Even `preliminary_confirmed` may be challenged by Pass 2 relationship evidence. The final report must record any change.

Pass 1 must return enough information for a user to choose categories:

- category name,
- description,
- object count,
- representative object names,
- preliminary confidence summary,
- unresolved count,
- explicit warning that classification may change.

### 13.3 User selection behavior

When the current user request does not explicitly say “all” or name selected categories, use `ask` mode.

Ask one concise question:

```text
ต้องการสร้างทุกหมวด หรือเลือกเฉพาะบางหมวด?
```

Present:

- `ทั้งหมด`
- every preliminary category,
- an option to select multiple categories,
- the unresolved object count,
- a warning that the server will still analyze all database objects.

Do not ask the user to choose individual objects at this stage.

Selection rules:

- `all` means materialize every final category.
- `selected` stores category names, not Pass 1 object IDs.
- If a selected category disappears or is renamed after Pass 2, stop materialization and ask the owner.
- If Pass 2 creates a new category closely connected to selected categories, include it in the materialization-plan warning but do not silently select it.

### 13.4 Full analysis before final classification

After selection is recorded, extract every permitted object and build:

- complete table metadata,
- masked sample rows,
- primary/unique/foreign-key relationships,
- procedure definitions,
- procedure read/write/call relationships,
- object descriptions,
- incoming and outgoing dependency neighborhoods.

Full analysis must not be skipped for objects outside preliminary selected categories.

This is necessary because:

- names can be ambiguous,
- shared tables can belong to multiple domains,
- procedures can reveal hidden table ownership,
- foreign-key neighborhoods can place generic names into the correct business context.

### 13.5 Pass 2 — Final evidence order

Use evidence in this priority:

1. Owner override
2. Exact configured object match
3. Configured prefix
4. Database schema ownership
5. Database comments/extended properties
6. Column names, types, and key roles
7. Foreign-key neighborhood
8. Routine read/write/call dependencies
9. Sanitized sample shape and representative values
10. Name-token similarity
11. Semantic/model suggestion

A semantic or model-generated suggestion alone must never become `final_confirmed`.

Final statuses:

```text
final_confirmed:
  owner override or deterministic rule supported by contextual evidence

final_suggested:
  strong contextual evidence but no owner confirmation

final_unresolved:
  conflicting evidence, no suitable category, or low confidence
```

### 13.6 Category movement rules

The system must compare Pass 1 and Pass 2.

For every object, record:

```json
{
  "object_id": "table:agrimap_app.APP_OBJECT",
  "preliminary_category": null,
  "final_category": "content",
  "changed": true,
  "change_reason": [
    "foreign key to CONTENT",
    "written by CONTENT_I"
  ]
}
```

Materialization uses `final_category`.

Therefore:

- objects moved into a selected category are included,
- objects moved out of a selected category are excluded in strict selected mode,
- excluded related objects remain visible as boundary nodes and edges,
- materialization decisions must be explainable.

### 13.7 Unknown handling after Pass 2

The skill must not guess.

In `all` mode, ask for every unresolved object.

In `selected` mode, prioritize unresolved objects that:

- may belong to a selected category,
- are direct dependencies of selected objects,
- bridge two selected categories,
- would change dependency closure,
- have conflicting high-confidence evidence.

Other unresolved objects may remain excluded under `unresolved`, but must still appear in analysis reports.

The consolidated owner question must contain:

- every current final category,
- suggested new categories,
- unresolved objects,
- preliminary and final candidates,
- confidence,
- relationship evidence,
- whether the object affects selected output,
- the option to leave it unresolved.

Example:

```text
เลือก Output: um, content

พบ 3 objects ที่อาจกระทบ Output:
- APP_OBJECT
  - preliminary: unresolved
  - final candidate: content
  - evidence: FK -> CONTENT, written by CONTENT_I
- USER_CONTENT_MAP
  - preliminary: um
  - final candidates: um / content
  - evidence: bridge table between UM_USER and CONTENT
- GLOBAL_SETTING
  - preliminary: content
  - final candidate: platform_config
  - evidence: used only by platform configuration procedures

กรุณากำหนด category หรือเลือก unresolved
```

Do not ask one question per table when a consolidated decision is possible.

### 13.8 Persisted decisions

Owner resolutions must be stored separately from generated artifacts:

```text
config/category-overrides.yaml
```

A classification rerun must not require a new database dump when:

- the catalog snapshot is still valid,
- the masking policy is unchanged,
- relationship metadata is complete,
- the source fingerprints have not changed.

### 13.9 Boundary relationship metadata

Selective output must not pretend excluded related objects do not exist.

When `dependency_materialization=index_only`, write boundary nodes such as:

```json
{
  "node_id": "table:agrimap_app.GLOBAL_SETTING",
  "materialized": false,
  "boundary": true,
  "final_category": "platform_config",
  "exclusion_reason": "category_not_selected"
}
```

Edges from selected objects to boundary nodes must remain in graph indexes.

SQL definitions and sample rows for boundary nodes must not be written unless dependency materialization is `direct` or `closure`.

## 14. Relationship and Graph-ready Metadata

### 14.1 Node types

Version 1:

```text
database
schema
category
table
procedure
column
```

Future-compatible:

```text
view
function
trigger
sequence
package
materialized_view
```

### 14.2 Edge types

```text
CONTAINS
BELONGS_TO_CATEGORY
HAS_COLUMN
PRIMARY_KEY
FOREIGN_KEY
READS_FROM
WRITES_TO
CALLS
REFERENCES
DERIVED_FROM
```

### 14.3 Cardinality truth rules

Use explicit database constraints first.

Infer:

- `1:1` only when the foreign-key columns are unique on the child side.
- `1:N` when the child foreign key is not unique.
- optionality from nullability where possible.
- `M:N` only when an associative table has suitable foreign keys and a unique/composite key supporting that interpretation.

If constraints do not prove cardinality:

```json
{
  "cardinality": "unknown",
  "confidence": "inferred",
  "evidence": ["name similarity only"]
}
```

Never present an inferred relationship as a confirmed database fact.

### 14.4 Routine dependency analysis

Use this order:

1. Native database dependency catalog.
2. Parsed SQL references.
3. Conservative lexical fallback.
4. Unresolved dynamic-SQL marker.

Differentiate:

```text
READS_FROM
WRITES_TO
CALLS
UNKNOWN_DYNAMIC_REFERENCE
```

### 14.5 Graph output

Version 1 must emit:

```text
indexes/nodes.jsonl
indexes/edges.jsonl
indexes/relationships.json
indexes/routine-dependencies.json
indexes/graph.json
```

Phase 2 may render:

```text
graph/erd.mmd
graph/dependencies.mmd
graph/relationships.graphml
graph/tree.json
```

Graph rendering in Phase 2 must use the exported indexes and must not reconnect to the database.

---

## 15. Output Directory Resolution

### 15.1 User intent

The skill must detect explicit output intent such as:

```text
เขียนไปที่ docs/db-context
output ./knowledge/sql
สร้างที่ .agent/context/database
```

Resolution order:

1. Explicit path in the current user request.
2. Skill configuration `default_output`.
3. Project convention discovered from existing configuration.
4. Repository root + `sql-context/`.

Do not invent an absolute path.

### 15.2 Path safety

The skill, not the server, writes into the user-selected project path.

Rules:

- normalize path,
- reject traversal outside the permitted workspace,
- do not overwrite unrelated files,
- use a manifest to identify managed files,
- update only managed files,
- obtain owner confirmation before deleting stale managed files,
- extract downloaded bundles in an OS temp directory,
- validate hashes and paths,
- atomically move final files into place,
- clean the OS temp directory in `finally`.

### 15.3 Required output layout

Example:

```text
<output-root>/
├── manifest.yaml
├── catalog.json
├── categories.yaml
├── um/
│   ├── category.yaml
│   ├── tables/
│   │   ├── UM_USER.sql
│   │   └── UM_ROLE.sql
│   └── store_procedures/
│       ├── UM_USER_I.sql
│       └── UM_USER_U.sql
├── content/
│   ├── category.yaml
│   ├── tables/
│   │   ├── CONTENT.sql
│   │   └── CONTENT_SHARE.sql
│   └── store_procedures/
│       └── CONTENT_I.sql
├── unresolved/
│   └── classification-requests.yaml
├── indexes/
│   ├── objects.jsonl
│   ├── nodes.jsonl
│   ├── edges.jsonl
│   ├── relationships.json
│   ├── routine-dependencies.json
│   ├── tags.json
│   └── graph.json
└── reports/
    ├── export-summary.md
    ├── category-preview.json
    ├── classification-report.json
    ├── materialization-plan.json
    ├── masking-report.json
    ├── sqlfluff-report.json
    └── integrity-report.json
```

Do not add an extra `categories/` parent directory; business categories must appear directly under the selected output root as requested.

### 15.4 Object file naming

```text
<table-name>.sql
<procedure-name>.sql
```

Collision handling:

- Include schema only if two objects would map to the same relative path.
- Use a deterministic suffix, not a random value.
- Record the original fully qualified name in the object index.

### 15.5 Manifest example

```yaml
format_version: "1"
generator:
  name: sql-context-pack
  version: "1.0.0"

source:
  profile: agrimap-readonly
  engine: sqlserver
  database_name: "[POLICY_HIDDEN]"
  schemas:
    - agrimap_app

export:
  created_at: "2026-07-18T12:00:00+07:00"
  discovered_object_count: 842
  fully_analyzed_object_count: 838
  analysis_failed_object_count: 4
  materialized_object_count: 214
  intentionally_excluded_object_count: 624
  table_count_in_materialization: 130
  procedure_count_in_materialization: 84
  requested_samples_per_table: 10

selection:
  mode: selected
  selected_categories:
    - um
    - content
  dependency_materialization: index_only

classification:
  strategy: two_pass
  moved_into_selected_categories: 11
  moved_out_of_selected_categories: 7
  unresolved_affecting_selection: 0

security:
  masking_policy: strict
  raw_credentials_exported: false
  raw_secrets_detected_after_export: false

sqlfluff:
  version: "PINNED_VERSION"
  dialect: tsql
  exclude_rules:
    - CP02
    - LT01
    - RF06
  files_formatted: 820
  files_parse_failed: 22
```

---

## 16. Tags and Search Index

Each object index record must include:

```json
{
  "object_id": "table:agrimap_app.UM_USER",
  "qualified_name": "agrimap_app.UM_USER",
  "object_type": "table",
  "category": "um",
  "classification_status": "confirmed",
  "tags": [
    "user-management",
    "identity",
    "has-primary-key",
    "referenced-by-procedure"
  ],
  "columns": 24,
  "sample_rows": 10,
  "relationships": {
    "incoming": 4,
    "outgoing": 2
  },
  "routine_usage": {
    "read_by": 8,
    "written_by": 3
  },
  "path": "um/tables/UM_USER.sql",
  "content_hash": "sha256:..."
}
```

Tag sources must be recorded:

```json
{
  "tag": "identity",
  "source": "owner-config",
  "confidence": 1.0
}
```

Do not let generated tags overwrite owner-defined tags.

---

## 17. Performance and Resilience

### 17.1 Default limits

Suggested safe defaults:

```yaml
runtime:
  catalog_page_size: 100
  catalog_page_max: 250
  export_batch_objects: 10
  export_batch_max_objects: 25
  extraction_concurrency: 4
  sample_rows_per_table: 10
  max_sample_rows_per_table: 20
  max_text_value_chars: 512
  max_definition_bytes: 2000000
  statement_timeout_seconds: 30
  object_timeout_seconds: 60
```

Per-profile overrides may lower these values.

### 17.2 Bounded concurrency

- Use an async semaphore.
- Do not open one connection per table.
- Keep the database pool small.
- Allow adapter-specific concurrency limits.
- Oracle and production SQL Server profiles should default conservatively.
- Back off on transient errors.
- Never retry authentication or policy-denied errors repeatedly.

### 17.3 Resumability

Persist job checkpoints in the server runtime store, not the target project.

Checkpoint fields:

```text
catalog ID
object ID
phase
attempt count
status
sanitized error code
content hash
export ID
```

A resumed export must skip objects already completed with the same content fingerprint and policy version.

### 17.4 Partial failure

One failed object must not fail the entire database export.

Final statuses:

```text
completed
completed_with_warnings
partial
failed
cancelled
```

The final report must list:

- succeeded objects,
- parse-failed objects preserved unformatted,
- extraction failures,
- masking failures,
- unresolved categories,
- retryable failures.

### 17.5 Cache behavior

Server cache belongs in the user runtime directory, not the repository.

Cache keys must include:

- profile identifier,
- object qualified name,
- source fingerprint,
- masking policy version,
- SQLFluff version,
- formatter configuration,
- output format version.

Never cache raw unmasked sample values on disk by default.

---

## 18. Agent Skill Workflow

### 18.1 Skill objective

The skill converts a permitted database catalog into a complete, sanitized, categorized, AI-ready SQL context package in the user-selected project location.

It must distinguish:

```text
what the server analyzes
from
what the skill materializes
```

### 18.2 Selection intent detection

Before creating the catalog, parse the user request.

Examples:

```text
สร้างทั้งหมด
dump ทุกหมวด
all categories
```

Resolve to:

```json
{"mode":"all"}
```

Examples:

```text
เอาเฉพาะ um กับ content
สร้างหมวด user management
only content
```

Resolve to:

```json
{
  "mode":"selected",
  "selected_categories":["um","content"]
}
```

When no choice is explicit, resolve to:

```json
{"mode":"ask"}
```

Do not infer selected categories merely from the project name.

### 18.3 Mandatory workflow

```text
1. Parse the user request.
2. Resolve output directory.
3. Resolve initial materialization mode: ask, all, or selected.
4. Discover server capabilities.
5. List safe connection profiles.
6. Select only the profile explicitly named or unambiguously configured.
7. Ensure SQLFluff is available.
8. Test profile connectivity.
9. Create catalog snapshot with two-pass category policy.
10. Poll until preliminary classification is available.
11. Fetch all category-preview pages using next_cursor.
12. If mode=ask:
    a. present all preliminary categories and counts;
    b. present representative names;
    c. present unresolved count;
    d. ask whether to create all categories or selected categories;
    e. store the selected category names.
13. Submit materialization selection.
14. Confirm from the response that analysis_scope.restricted_by_selection=false.
15. Poll while the server extracts every permitted object.
16. Poll through relationship analysis and final classification.
17. Fetch every analysis sitemap page until next_cursor is null.
18. Record all discovered, analyzed, failed-analysis, and unresolved object IDs.
19. Fetch the final materialization plan.
20. Inspect classification changes:
    a. moved into selected categories;
    b. moved out of selected categories;
    c. new categories connected to selected categories;
    d. boundary relationships.
21. Fetch unresolved classification requests.
22. If owner decisions are required:
    a. present all final categories;
    b. present suggested categories and evidence;
    c. prioritize unresolved objects affecting selected output;
    d. ask one consolidated owner question;
    e. submit resolutions;
    f. refresh final classification and materialization plan.
23. Fetch every materialization sitemap page until next_cursor is null.
24. Collect only final included object IDs for export.
25. Record every intentionally excluded object and reason.
26. Partition included object IDs by recommended batch size and weight.
27. Export every materialization batch.
28. Poll every export.
29. Download every completed bundle.
30. Validate bundle paths and hashes.
31. Assemble into the selected output root.
32. Call final validation with:
    a. expected discovered count;
    b. expected analyzed count;
    c. expected materialized count;
    d. all export IDs.
33. Verify:
    discovered = analyzed + failed_analysis
    analyzed = materialized + intentionally_excluded
34. Write reports and manifest.
35. Remove all OS temporary files.
36. Report exact analysis, materialization, exclusion, warning, unresolved, and failure counts.
```

### 18.4 Prohibited skill behavior

The skill must not:

- request database credentials from the user in chat,
- place credentials in a command line,
- print environment variables,
- call arbitrary SQL,
- use selected categories as database extraction filters,
- skip non-selected objects during full analysis,
- finalize category assignment from names alone,
- apply selection to Pass 1 object IDs instead of Pass 2 categories,
- silently include a newly discovered category,
- silently exclude an object moved into a selected category,
- export more sample rows than policy permits,
- weaken masking to make an export succeed,
- guess a business category,
- claim completion before analysis and materialization validation,
- stop after the first sitemap page,
- use directory-wide SQLFluff formatting,
- enable format/fix on unparsable SQL,
- create `.tmp-*` directories in the project,
- delete unmanaged project files,
- invent sample rows when a table has fewer than ten,
- silently update SQLFluff,
- hide partial failures.

### 18.5 Owner clarification format

Ask only when a real owner decision is required.

For initial selection, ask one question covering:

- all categories,
- selected categories,
- preliminary category counts,
- unresolved count.

For final classification, use one consolidated question containing only decisions that are unresolved or materially affect the selected output.

Do not ask technical questions already answerable from capabilities, manifests, the catalog, or relationship indexes.

## 19. Acceptance Criteria

### 19.1 Installation

- On a clean supported machine with Python but without SQLFluff, `sqlctx sqlfluff ensure` installs the pinned SQLFluff version.
- A second call does not reinstall it.
- Two concurrent ensure calls result in one installation.
- `sqlctx doctor` reports the installed version and dialect availability.
- `sqlctx sqlfluff update` changes versions only after explicit invocation.
- Failed update retains the previous working runtime.

### 19.2 SQLFluff isolation

Given 100 SQL files where 3 are unparsable:

- 97 files are formatted.
- 3 cleaned original files are preserved.
- The process completes with warnings.
- The report identifies each failed file.
- No `fix_even_unparsable` behavior is used.
- No project-local temp directory remains.

### 19.3 Sensitive data

Test fixtures must contain:

- national ID,
- username,
- password,
- password hash,
- JWT,
- access token,
- refresh token,
- API key,
- email,
- phone,
- hardcoded routine secret.

Acceptance:

- none of the original sensitive values appears in any API response, MCP result, bundle, report, exception, or log,
- deterministic aliases preserve required joins,
- high-risk secret classes are fully redacted,
- final post-export secret scan passes.

### 19.4 Pagination, full analysis, and selective completeness

Given 842 objects, page size 100, and selected categories `um` and `content`:

- the skill requests every category-preview page until `next_cursor=null`,
- all 842 unique object IDs enter `analysis_scope`,
- selected categories do not reduce extraction scope,
- every analysis sitemap page is requested,
- no object is duplicated,
- `discovered = analyzed + failed_analysis`,
- every materialization sitemap page is requested,
- `analyzed = materialized + intentionally_excluded`,
- export batches contain only final included objects,
- every excluded object has an explicit reason,
- boundary relationships are preserved,
- count mismatch causes validation failure.

In `all` mode:

- every successfully analyzed object is materialized unless security policy explicitly excludes it.

In `selected` mode:

- materialized count may be lower than discovered count,
- the difference must be intentional and fully accounted for.

### 19.5 Two-pass category handling

Given configured categories `um` and `content`:

- Pass 1 returns preliminary category counts and representative names.
- When no selection is explicit, the skill asks all versus selected categories.
- `UM_USER` preliminarily and finally resolves to `um`.
- `CONTENT_SHARE_USER` preliminarily and finally resolves to `content`.
- `APP_OBJECT` may be unresolved in Pass 1 and move to `content` after FK/procedure analysis.
- `CONTENT_CONFIG` may move out of `content` after full contextual analysis.
- Selecting `content` includes objects moved into `content`.
- Selecting `content` excludes false-positive objects moved out of `content`.
- An ambiguous `APP_AUDIT_LOG` remains unresolved.
- The skill lists current categories and candidate categories.
- No category is silently guessed.
- Owner resolution persists as an override.
- Reclassification does not require another database extraction while the snapshot remains valid.

### 19.6 Output safety

- Explicit output path is honored.
- Traversal outside the workspace is rejected.
- Managed files are written atomically.
- Existing unmanaged files remain untouched.
- Bundle extraction rejects absolute paths and `../`.
- No `.tmp-sql-finalizer`, `.tmp-sqlfluff-format`, `.tmp-*`, or partial directory remains in the project.

### 19.7 Multi-engine mapping

Integration tests verify:

```text
sqlserver -> tsql
mysql     -> mysql
mariadb   -> mariadb
oracle    -> oracle
postgres  -> postgres
```

Each adapter must use its own catalog queries and capability declaration.

---

# 20. Chunked Implementation Prompts

Use the following prompts sequentially in the **same agent session and repository**. Do not skip a chunk. Each chunk is intentionally bounded to prevent scope drift.

---

## Prompt Chunk 0 — Immutable Contract

```text
You are implementing a repository named `sql-context-pack`.

Read this entire instruction before changing files.

IMMUTABLE PRODUCT PURPOSE
Build a universal, Python-first system that extracts database table DDL and stored procedure definitions, retrieves sanitized representative table samples, formats SQL using SQLFluff, classifies objects into business categories, creates dependency/relationship/tag indexes, and packages the result as AI-ready SQL context.

SUPPORTED DATABASE ENGINES AND SQLFLUFF DIALECTS
- sqlserver -> tsql
- mysql -> mysql
- mariadb -> mariadb
- oracle -> oracle
- postgres -> postgres

MANDATORY ARCHITECTURE
- Python is the primary implementation language.
- One shared application core must serve both HTTP and MCP interfaces.
- The owner configures credentials and starts the server.
- Agents/models must never receive database credentials or connection strings.
- Use connection profile names in all public interfaces.
- No arbitrary SQL endpoint or MCP tool is allowed.
- Database access is read-only.
- Cleansing/masking must happen before any value is serialized, logged, returned, or written.
- SQLFluff formatting must run one SQL file at a time.
- A parse failure in one file must not stop other files.
- Never enable fix_even_unparsable or --FIX-EVEN-UNPARSABLE.
- Temporary files must use the operating-system temp/runtime directory.
- Do not create `.tmp-*` or staging folders inside the target project.
- Classification must use two passes: preliminary name-based discovery, then final relationship-aware classification.
- If the user has not selected all or named categories, the skill must ask whether to materialize all categories or selected categories.
- User category selection controls final materialization only.
- Every permitted object must still be fully extracted and analyzed regardless of selected categories.
- Final materialization must use Pass 2 categories, never Pass 1 object membership.
- Unknown business categories must not be guessed; they must be returned as consolidated owner decisions.
- Selective output must preserve excluded connected objects as boundary metadata.
- Output business category folders must be directly under the selected output root.
- The skill must use cursor pagination until next_cursor is null.
- The skill must separately validate discovered, analyzed, failed-analysis, materialized, and intentionally-excluded counts before claiming completion.
- SQLFluff must be a pinned dependency and must also have an executable ensure/status/update lifecycle.
- Normal export must never silently update SQLFluff.
- Version 1 supports tables and stored procedures as required object types.
- Graph-ready metadata is required; graph rendering itself is a later phase.

STRICT SCOPE
Do not add:
- arbitrary database querying,
- data mutation,
- schema migration,
- text-to-SQL,
- vector databases,
- web admin UI,
- cloud credential vault,
- continuous scheduling,
- database backup/restore,
- unrelated framework abstractions.

IMPLEMENTATION QUALITY
- Use typed Python.
- Validate inputs.
- Sanitize errors.
- Add unit and integration tests.
- Keep interface handlers thin.
- Put database-specific logic only in adapters.
- Use atomic writes.
- Be cross-platform for Windows, Linux, and macOS.

Before implementation, create:
1. `docs/requirements.md`
2. `docs/architecture.md`
3. `docs/security.md`
4. `docs/output-format.md`
5. `docs/acceptance-criteria.md`

These documents must restate the immutable contract without adding scope.

After creating the documents, stop and report:
- files created,
- architecture boundaries,
- unresolved implementation risks only.
Do not implement runtime code in this chunk.
```

---

## Prompt Chunk 1 — Repository Skeleton and Core Domain

```text
Continue the existing `sql-context-pack` repository.

Do not reinterpret or weaken the immutable contract from Prompt Chunk 0.

Implement only the repository skeleton and shared core/domain contracts.

REQUIRED MODULES
- sqlctx/core
- sqlctx/application
- sqlctx/adapters
- sqlctx/security
- sqlctx/formatting
- sqlctx/classification
- sqlctx/indexing
- sqlctx/exporting
- sqlctx/server/http
- sqlctx/server/mcp
- sqlctx/cli
- sqlctx/skill

REQUIRED DOMAIN MODELS
- ConnectionProfileDescriptor
- ResolvedConnectionProfile (internal only; never serializable publicly)
- DatabaseCapabilities
- DatabaseObject
- ObjectRef
- ColumnMetadata
- ConstraintMetadata
- ForeignKeyMetadata
- DependencyEdge
- CatalogSnapshot
- CatalogStatus
- SitemapPage
- CategoryPreview
- CategoryPreviewGroup
- MaterializationSelection
- MaterializationPlan
- ClassificationPassResult
- ClassificationCandidate
- ClassificationRequest
- ClassificationResolution
- SampleRequest
- SamplePage
- MaskingDecision
- SqlFormatResult
- ExportBatchRequest
- ExportJob
- ExportArtifact
- ValidationResult

REQUIRED PORTS/INTERFACES
- ConnectionProfileRepository
- DatabaseAdapter
- MaskingEngine
- SqlFormatter
- CategoryClassifier
- DependencyAnalyzer
- ExportStore
- RuntimeStateStore
- AuditSink

RULES
- Public models must not contain raw credentials or a connection string.
- Internal resolved profiles must have redacted repr/string behavior.
- Use explicit enums for engine, object type, job status, edge type, sensitivity class, classification status, classification pass, materialization mode, dependency materialization, and inclusion reason.
- Add JSON-schema-compatible validation models for HTTP/MCP boundaries.
- Do not implement database queries yet.
- Do not implement HTTP routes or MCP tools yet.
- Add tests proving sensitive fields cannot be serialized from internal profile objects.

Add `pyproject.toml` with pinned/locked dependency strategy. Include SQLFluff as a required dependency but keep the actual version in one central dependency definition.

Stop after:
- core modules compile,
- type checks pass,
- unit tests pass.

Report only:
- module tree,
- key contracts,
- test results,
- remaining risks.
```

---

## Prompt Chunk 2 — Profiles, Security, Masking, and SQLFluff Manager

```text
Continue the existing `sql-context-pack` repository.

Do not modify the immutable product scope.

Implement:
1. connection profile loading,
2. secret resolution from environment,
3. masking/classification engine,
4. routine/DDL secret scanning,
5. SQLFluff lifecycle manager,
6. fail-isolated per-file formatter.

CONNECTION PROFILE REQUIREMENTS
- Load profile metadata from the platform config directory.
- Profile files must reference environment variable names.
- Reject raw password fields by default.
- Public profile listing returns only profile name, engine, allowed schemas, allowed object types, and readiness.
- Never log resolved secrets.
- Internal resolved profile repr must redact all secret values.
- Validate allowed schemas and sample limits.

MASKING REQUIREMENTS
Implement at minimum:
- national_id
- username
- password
- password_hash
- secret
- secret_key
- private_key
- api_key
- client_secret
- access_token
- refresh_token
- jwt
- session_token
- cookie
- email
- phone
- address
- personal_name
- financial_account
- credit_card
- date_of_birth
- precise_location
- biometric

Apply:
1. owner override,
2. database classification metadata,
3. exact column-name rule,
4. tokenized column-name rule,
5. type/length heuristic,
6. value-pattern detector,
7. routine/DDL literal scanner,
8. fail-closed fallback.

High-risk secrets must be fully redacted.
Keys that must preserve relationships must use deterministic HMAC-based aliases within one snapshot.
Never store the HMAC key in an export.

SQLFLUFF LIFECYCLE
Required CLI/application commands:
- doctor
- sqlfluff status
- sqlfluff ensure
- sqlfluff update
- sqlfluff update --version X.Y.Z

Ensure behavior:
- check importlib metadata,
- check `python -m sqlfluff version`,
- reuse a valid install,
- use a cross-process lock,
- install the pinned version once when missing,
- verify after install,
- store runtime state outside the project,
- never install latest during a normal export.

Update behavior:
- explicit invocation only,
- install into a new runtime,
- self-test,
- atomically switch,
- keep one rollback version.

FORMATTER
For each file independently:
1. keep cleaned original SQL,
2. create OS temp file,
3. parse with `python -m sqlfluff parse`,
4. if parse fails, preserve cleaned original and continue,
5. if parse succeeds, format with:
   `python -m sqlfluff format --exclude-rules "CP02,LT01,RF06" --dialect <dialect> --templater raw <file>`
6. parse formatted result again,
7. rollback to cleaned original if post-format parse fails,
8. return structured SqlFormatResult,
9. delete temp files in finally.

Never format a directory from the production orchestrator.
Never enable fix_even_unparsable.

TESTS
- clean/missing SQLFluff simulation,
- repeated ensure does not reinstall,
- concurrent ensure installs once,
- failed update rolls back,
- one bad SQL file does not stop good files,
- no project-local temp directory,
- raw secrets absent from output/logs/errors,
- stable alias preserves joins.

Stop after tests pass.
```

---

## Prompt Chunk 3 — Database Adapters and Catalog Discovery

```text
Continue the existing `sql-context-pack` repository.

Implement database adapters for:
- SQL Server
- MySQL
- MariaDB
- Oracle
- PostgreSQL

Do not expose arbitrary SQL.

Every adapter must implement:
- test_connection
- get_server_info
- list_schemas
- discover_objects
- get_table_definition
- get_procedure_definition
- get_table_columns
- get_constraints
- get_foreign_keys
- get_sample_rows
- get_routine_dependencies
- capability declaration

DIALECT MAPPING
- sqlserver -> tsql
- mysql -> mysql
- mariadb -> mariadb
- oracle -> oracle
- postgres -> postgres

SECURITY
- Use reviewed adapter-owned query templates.
- Validate identifiers against discovered catalog objects.
- Quote identifiers through adapter functions.
- Enforce allowed schemas and object types.
- Apply statement timeouts.
- Use bounded connection pools.
- Use read-only transaction behavior where supported.
- Do not put raw SQL values in logs or errors.

SAMPLING
- Default target is 10 rows per table.
- If at least 10 eligible rows exist, return exactly 10.
- If fewer exist, return actual count and shortage metadata.
- Never fabricate duplicate rows.
- Prefer primary-key deterministic ordering.
- Fall back to unique index, then safe adapter strategy.
- Mark non-deterministic samples.
- Do not perform expensive random full-table sorts.
- Exclude/placeholder large binary values.
- Limit long text.

CATALOG PHASES
Implement two catalog phases:

Phase 1:
- discover every permitted object name,
- return preliminary category preview,
- support `awaiting_selection`,
- do not treat preliminary categories as final.

Phase 2:
- after selection is recorded, extract every permitted object,
- selection must not modify database include/exclude filters,
- build complete relationships and dependencies,
- support final contextual classification.

CATALOG
Implement a stable CatalogSnapshot containing:
- objects,
- columns,
- constraints,
- foreign keys,
- routine dependencies,
- native comments/descriptions,
- content/source fingerprints,
- capability metadata.

Use cursor pagination for the sitemap.
Response must include recommended and maximum batch sizes.

MARIADB
Keep MariaDB as a distinct adapter even where implementation shares reusable MySQL helpers.

ORACLE
Discover privileges/capabilities at runtime. Do not assume DBMS_METADATA or all catalog views are always available.

TESTS
- adapter contract tests,
- identifier safety,
- allowed schema enforcement,
- sample limit,
- fewer-than-10 behavior,
- deterministic ordering,
- capability negotiation,
- sanitized database errors.

Use containerized integration tests where practical and fixture/mocked adapter tests where a proprietary database cannot run in CI.

Stop after adapter and catalog tests pass.
```

---

## Prompt Chunk 4 — Classification, Indexes, Output Packaging, and Validation

```text
Continue the existing `sql-context-pack` repository.

Implement:
1. category rule configuration,
2. Pass 1 preliminary name-based classification,
3. user materialization selection,
4. Pass 2 relationship-aware final classification,
5. classification-change tracking,
6. unresolved owner-decision workflow,
7. materialization planning,
8. relationship/dependency indexes,
9. graph-ready indexes,
10. output package writer,
11. integrity validation.

TWO-PASS RULE
Pass 1 may use only names, schema, type, configured rules, and lightweight comments.
It exists to show a category preview.

After the user selects all or selected categories, the system must still analyze every permitted object.

Pass 2 must use:
1. owner override
2. exact configured match
3. configured prefix
4. schema ownership
5. database comment/extended property
6. columns, types, and key roles
7. foreign-key neighborhood
8. routine read/write/call dependencies
9. sanitized sample shape/representative values
10. name-token similarity
11. semantic suggestion

Materialization must apply selected category names to Pass 2 categories.
Track objects moved into and out of selected categories.

Only owner override or deterministic configured rules supported by context may produce final `confirmed`.
Ambiguous objects must be `unresolved`.
Do not guess.

Classification request must include:
- all current categories,
- suggested new categories,
- all unresolved objects,
- candidates,
- confidence,
- evidence,
- unresolved option.

Persist owner decisions in `config/category-overrides.yaml`.
Allow reclassification without a new database extraction.

RELATIONSHIPS
Emit nodes and edges for:
- database
- schema
- category
- table
- procedure
- column

Edge types:
- CONTAINS
- BELONGS_TO_CATEGORY
- HAS_COLUMN
- PRIMARY_KEY
- FOREIGN_KEY
- READS_FROM
- WRITES_TO
- CALLS
- REFERENCES
- DERIVED_FROM

Cardinality:
- prove 1:1 using child uniqueness,
- use 1:N otherwise for a confirmed FK,
- infer M:N only from a valid associative-table structure,
- mark unproven relationships as inferred/unknown.

OUTPUT LAYOUT
Business categories must be directly under output root:

<output-root>/
  manifest.yaml
  catalog.json
  categories.yaml
  <category>/
    category.yaml
    tables/
    store_procedures/
  unresolved/
  indexes/
  reports/

TABLE SQL
- Format cleaned DDL first.
- Append sanitized sample JSON rows as SQL line comments.
- Include requested and actual sample counts.
- Do not run SQLFluff over the sample comment block.

INDEXES
- objects.jsonl
- nodes.jsonl
- edges.jsonl
- relationships.json
- routine-dependencies.json
- tags.json
- graph.json

REPORTS
- export-summary.md
- category-preview.json
- classification-report.json
- materialization-plan.json
- masking-report.json
- sqlfluff-report.json
- integrity-report.json

PATH SAFETY
- Reject absolute/traversal paths inside bundles.
- Do not overwrite unmanaged files.
- Use a managed-file manifest.
- Write atomically.
- Use OS temp extraction.
- Never create project-local `.tmp-*`.

VALIDATION
Check:
- discovered/analyzed/failed-analysis accounting,
- materialized/intentionally-excluded accounting,
- Pass 1 to Pass 2 category changes,
- selected-category materialization decisions,
- boundary relationships for excluded connected objects,
- duplicate paths,
- hashes,
- path traversal,
- unresolved relationship targets,
- raw-secret scan,
- SQLFluff result coverage,
- sample metadata,
- manifest/output-format version.

Stop after unit tests pass and provide one realistic fixture output containing:
- um/tables/UM_USER.sql
- um/tables/UM_ROLE.sql
- content/tables/CONTENT.sql
- content/tables/CONTENT_SHARE.sql
- at least one stored procedure per category
- one unresolved object
- relationship and graph indexes.
```

---

## Prompt Chunk 5 — HTTP and MCP Interfaces

```text
Continue the existing `sql-context-pack` repository.

Implement thin HTTP and MCP interfaces over the existing application core.

HTTP BASE
/api/v1

HTTP ENDPOINTS
- GET  /health
- GET  /capabilities
- GET  /profiles
- POST /profiles/{profile}/test
- POST /catalogs
- GET  /catalogs/{catalog_id}
- GET  /catalogs/{catalog_id}/category-preview
- POST /catalogs/{catalog_id}/selection
- GET  /catalogs/{catalog_id}/sitemap
- GET  /catalogs/{catalog_id}/materialization-plan
- GET  /catalogs/{catalog_id}/classification-requests
- POST /catalogs/{catalog_id}/classification-resolutions
- POST /exports
- GET  /exports/{export_id}
- GET  /exports/{export_id}/bundle
- GET  /exports/{export_id}/manifest
- POST /validations
- GET  /tooling/sqlfluff
- POST /tooling/sqlfluff/ensure
- POST /tooling/sqlfluff/update

Use:
- 200 synchronous success
- 202 accepted job
- 400 invalid input
- 401 unauthenticated
- 403 policy denial
- 404 not found
- 409 state conflict
- 413 too large
- 422 unsupported capability
- 429 throttled
- 500 sanitized internal error
- 503 dependency unavailable

Default HTTP bind:
- 127.0.0.1
- random local bearer token
- remote mode disabled

MCP TOOLS
- sqlctx_get_capabilities
- sqlctx_list_profiles
- sqlctx_test_profile
- sqlctx_create_catalog
- sqlctx_get_catalog_status
- sqlctx_get_category_preview
- sqlctx_set_materialization_selection
- sqlctx_list_sitemap
- sqlctx_get_materialization_plan
- sqlctx_get_classification_requests
- sqlctx_resolve_classifications
- sqlctx_export_batch
- sqlctx_get_export_status
- sqlctx_validate_exports
- sqlctx_sqlfluff_status
- sqlctx_sqlfluff_ensure
- sqlctx_sqlfluff_update

MCP RESOURCES
- sqlctx://catalog/{catalog_id}/category-preview
- sqlctx://catalog/{catalog_id}/sitemap
- sqlctx://catalog/{catalog_id}/materialization-plan
- sqlctx://catalog/{catalog_id}/classification-requests
- sqlctx://export/{export_id}/manifest
- sqlctx://export/{export_id}/bundle
- sqlctx://export/{export_id}/report

MCP RULES
- strict JSON schemas,
- structured output,
- cursor pagination,
- no credentials,
- no arbitrary SQL,
- no unrestricted filesystem path,
- sanitized errors,
- meaningful text plus structured content.

Use the current stable official MCP Python SDK and pin an exact compatible version.
Do not use a pre-release SDK in production unless the repository explicitly opts into it and tests it.

Add API contract tests and MCP Inspector-compatible tests.
Stop after all interface tests pass.
```

---

## Prompt Chunk 6 — Agent Skill and End-to-End Acceptance

```text
Continue the existing `sql-context-pack` repository.

Implement the `sql-context-pack` Agent Skill.

The skill must execute this exact workflow:

1. Parse the user request.
2. Resolve explicit output path; otherwise configured default; otherwise repository-root/sql-context.
3. Resolve initial mode:
   - explicit all -> all
   - explicit category names -> selected
   - otherwise -> ask
4. Get server capabilities.
5. List safe profiles.
6. Select only an explicit or unambiguous profile.
7. Call SQLFluff status and ensure.
8. Test the profile.
9. Create a two-pass catalog snapshot.
10. Poll until preliminary category preview is available.
11. Fetch every category-preview page until next_cursor is null.
12. If mode=ask:
    - show all preliminary categories, counts, representative names, and unresolved count,
    - ask all versus selected categories,
    - allow multiple selected categories.
13. Submit materialization selection.
14. Verify analysis_scope.restricted_by_selection=false.
15. Poll until every permitted object has been extracted and relationship analysis completes.
16. Fetch every analysis sitemap page until next_cursor is null.
17. Record discovered, analyzed, failed-analysis, and unresolved IDs.
18. Fetch the final materialization plan.
19. Review objects moved into/out of selected categories and boundary relationships.
20. Fetch final classification requests.
21. If owner decisions are required:
    - list all final categories,
    - prioritize unresolved objects affecting selected output,
    - include candidates, confidence, and relationship evidence,
    - ask one consolidated owner question,
    - submit resolutions,
    - refresh the materialization plan.
22. Fetch every materialization sitemap page until next_cursor is null.
23. Collect final included IDs and intentional exclusion reasons.
24. Partition included IDs by server-recommended object count and weight.
25. Export every materialization batch.
26. Poll every export.
27. Download each bundle.
28. Validate bundle paths and hashes before extraction.
29. Assemble only managed files into the output root.
30. Call final validation with expected discovered, analyzed, and materialized counts.
31. Verify:
    discovered = analyzed + failed_analysis
    analyzed = materialized + intentionally_excluded
32. Remove all OS temporary files in finally.
33. Report exact analysis, materialization, exclusion, warning, unresolved, and failure counts.

The skill must never:
- ask for a database password,
- print credentials or environment variables,
- call arbitrary SQL,
- stop after the first category-preview or sitemap page,
- use selected categories to restrict database extraction,
- finalize categories from Pass 1 names alone,
- apply selection to preliminary object IDs,
- guess categories,
- fabricate rows,
- weaken masking,
- format a whole directory,
- enable fix-even-unparsable,
- silently update SQLFluff,
- write `.tmp-*` in the project,
- overwrite unmanaged files,
- hide failures,
- claim completion before validation.

OUTPUT PATH LANGUAGE
Recognize user intent such as:
- “เขียนไปที่ …”
- “output …”
- “สร้างที่ …”
- “write to …”
- “generate under …”

TEST SCENARIOS
1. Clean machine without SQLFluff.
2. 842 objects across multiple sitemap pages.
3. One database connection transient failure.
4. Three unparsable procedures while other files succeed.
5. Sensitive values in rows and stored procedure source.
6. Categories um/content plus ambiguous audit objects.
7. Ask mode where the user selects only um/content.
8. A name-ambiguous object moves into content after FK analysis.
9. A false-positive content object moves out after procedure analysis.
10. All 842 objects are analyzed while only selected final categories are materialized.
11. Boundary relationships are retained for excluded objects.
12. User-specified nested output path.
13. Malicious bundle path traversal.
14. Interrupted export resumed from checkpoints.
15. No project-local temporary residue.
16. Repeated run updates only managed changed files.
17. Analysis/materialization count or hash mismatch blocks completion.

Create:
- SKILL.md
- examples/
- fixtures/
- end-to-end tests
- README usage section
- troubleshooting section
- security assumptions section

Run:
- formatting
- linting
- type checking
- unit tests
- integration tests
- end-to-end tests

Do not mark the project complete if any mandatory acceptance test is skipped.
At the end, report:
- implemented requirements,
- test evidence,
- known limitations,
- exact commands to install, start the server, run doctor, and invoke the skill.
```

---

# 21. Definition of Done

The project is complete only when:

1. The owner can configure a read-only profile without exposing credentials to the agent.
2. The owner can start one Python server that provides HTTP and MCP.
3. The skill can discover all objects through paginated category-preview and sitemap calls.
4. The skill asks all versus selected categories when the request does not specify a mode.
5. Category selection never reduces full database analysis scope.
6. Pass 1 provides only preliminary category discovery.
7. Pass 2 reclassifies every object using full sanitized relationships and dependencies.
8. Selected output uses final categories and correctly includes/excludes objects that changed category.
9. Selective output preserves boundary nodes and edges for excluded related objects.
10. Every eligible table contains up to ten real, sanitized sample rows, with exactly ten when at least ten exist.
11. SQLFluff is installed once when missing and can be explicitly updated.
12. One broken SQL file does not stop the rest.
13. No formatting is applied to unparsable SQL.
14. No project-local temporary directory remains.
15. Categories `um` and `content` produce the requested direct-folder structure.
16. Unknown categories are escalated with all available category choices and evidence.
17. Relationship, dependency, tag, boundary, and graph-ready indexes are generated.
18. The final validator separately proves analysis completeness and materialization completeness.
19. The final validator proves path safety, content hashes, intentional exclusions, and absence of detected raw secrets.
20. The implementation works with SQL Server, MySQL, MariaDB, Oracle, and PostgreSQL through separate adapters and correct SQLFluff dialect mappings.
21. Reports are honest about partial failures and never claim unsupported certainty.

---

# 22. Direct Answer: Will the Plugin Install SQLFluff Automatically?

**It can be guaranteed only when executable bootstrap logic is implemented.**

Installing or copying an Agent Skill file by itself does not inherently run `pip install`. Therefore the repository must provide:

```text
- SQLFluff as a pinned package dependency
- sqlctx sqlfluff ensure
- automatic ensure before the first formatting operation
- cross-process install lock
- post-install verification
- clean-machine integration test
```

With those requirements implemented and process execution/network access permitted:

- SQLFluff is installed when missing.
- It is installed only once for the active pinned version.
- Later exports reuse it.
- Updates happen only through an explicit update command.
- The target project is not polluted by the managed runtime.

If the host blocks package installation or has no network/package source, the system must return `TOOLING_UNAVAILABLE`; it must not pretend that SQLFluff was installed.

---

# 23. Final Classification Decision

The recommended default behavior is:

```yaml
classification:
  strategy: two_pass

selection:
  mode: ask
  dependency_materialization: index_only
```

Runtime behavior:

```text
1. Discover every permitted object name.
2. Build a preliminary category preview.
3. Ask: all categories or selected categories?
4. Record selected category names.
5. Dump and sanitize every permitted object.
6. Analyze all relationships and routine dependencies.
7. Run final classification.
8. Apply selected category names to final categories.
9. Materialize only included objects.
10. Preserve excluded connected objects as boundary metadata.
```

This design is intentionally more expensive than filtering from names alone, but it prevents the more serious failure mode: silently omitting SQL objects whose names do not reveal their real business context.

---

# 24. Official Sources of Trust

- SQLFluff dialect reference: https://docs.sqlfluff.com/en/stable/reference/dialects.html
- SQLFluff installation/getting started: https://docs.sqlfluff.com/en/stable/gettingstarted.html
- SQLFluff CLI production behavior and exit codes: https://docs.sqlfluff.com/en/latest/production/cli_use.html
- SQLFluff troubleshooting/parsing errors: https://docs.sqlfluff.com/en/stable/guides/troubleshooting/how_to.html
- SQLFluff default configuration and `fix_even_unparsable`: https://docs.sqlfluff.com/en/stable/configuration/default_configuration.html
- MCP specification — tools: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- MCP specification — resources: https://modelcontextprotocol.io/specification/2025-11-25/server/resources
- MCP authorization: https://modelcontextprotocol.io/specification/draft/basic/authorization
- Official MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk