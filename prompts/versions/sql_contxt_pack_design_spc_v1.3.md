# SQL Context Pack — Architecture, Security, Skill, and Implementation Prompt Specification

**Status:** Proposed v1.3  
**Specification version:** `1.3`  
**Recommended GitHub repository:** `sql-context-pack`  
**CLI command:** `sqlctx`  
**Service process:** `sqlctx-server`  
**MCP server name:** `SQL Context Pack`  
**Agent Skill name:** `sql-context-pack`  
**Export bundle extension:** `.sqlctx.zip`

### Revision v1.3

This revision retains every accepted v1.2 behavior, incorporates the appended raw requirements without altering the original raw text, and closes the verified contract gaps:

- one GitHub monorepo and one canonical Agent Skill shared by Codex, Claude Code, and Gemini CLI,
- vendor-specific plugin/extension manifests and connection examples without duplicating workflow logic,
- an explicit owner-started service default and an opt-in client-managed STDIO trade-off,
- a deterministic-server versus model-harness classification boundary,
- complete MCP tool input/output contract mapping and examples,
- normative interpretation of the ten-row sample requirement,
- required operator, harness, command, case-by-case, troubleshooting, and security documentation,
- SemVer, changelog, manifest-version, and release-consistency rules,
- cross-harness conformance tests and requirement traceability,
- a pinned SQLFluff materialization stage with internally consistent manifest counters,
- symmetric report access, paginated classification responses, job list/cancel/delete operations, and explicit idempotency,
- one canonical `output_format_version` field name across manifests, validation, cache keys, and prose,
- deterministic HMAC alias encoding with collision handling and resumable per-snapshot registries,
- bounded runtime retention, authenticated token handoff, and a canonical large-bundle download path,
- Python 3.11 minimum, checked-in CI, development-versus-release version rules, and fresh-session chunk execution,
- removal of optional relationship-aware sampling and dependency-closure materialization because they are outside the raw v1 requirement.

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

### 1.3 GitHub repository count and authoritative development layout

Create **one GitHub repository**, `sql-context-pack`, as a Python monorepo. Do not create separate repositories for the server, CLI, Skill, or individual harnesses in v1.

Reasons:

- HTTP, MCP, CLI, and all harness packages share one application core and one release version.
- One canonical `SKILL.md` prevents Codex, Claude Code, and Gemini CLI workflows from drifting.
- Contract tests, fixtures, security rules, and changelog updates can be atomic in one pull request.
- A split repository would add cross-repository version coordination without providing a v1 requirement benefit.

Use this structure:

```text
sql-context-pack/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .codex-plugin/
│   └── plugin.json
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json.example
├── gemini-extension.json
├── skills/
│   └── sql-context-pack/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── examples/
├── harnesses/
│   ├── codex/
│   │   ├── config.toml.example
│   │   └── README.md
│   ├── claude/
│   │   └── README.md
│   └── gemini/
│       ├── settings.json.example
│       └── README.md
├── src/
│   └── sqlctx/
│       ├── core/
│       ├── application/
│       ├── adapters/
│       │   ├── sqlserver/
│       │   ├── mysql/
│       │   ├── mariadb/
│       │   ├── oracle/
│       │   └── postgres/
│       ├── security/
│       ├── formatting/
│       ├── classification/
│       ├── indexing/
│       ├── exporting/
│       ├── server/
│       │   ├── http/
│       │   └── mcp/
│       └── cli/
├── docs/
│   ├── spec/
│   │   ├── design-spec-v1.3.md
│   │   └── design-spec-v1.3.sha256
│   ├── implementation-state.md
│   ├── getting-started.md
│   ├── server-operations.md
│   ├── command-reference.md
│   ├── use-cases.md
│   ├── api-and-mcp-examples.md
│   ├── security.md
│   ├── troubleshooting.md
│   └── harnesses/
│       ├── codex.md
│       ├── claude-code.md
│       └── gemini-cli.md
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   ├── e2e/
│   └── harness/
├── fixtures/
├── examples/
├── scripts/
├── config/
│   └── examples/
│       └── profiles.yaml
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
└── README.md
```

The root-level `skills/sql-context-pack/SKILL.md` is canonical. Vendor directories may contain only manifests, connection templates, installation notes, and thin compatibility shims. They must not copy or fork the workflow instructions.

A separate repository may be considered only after v1 when a component has an independent release cadence, ownership boundary, or security boundary. Graph/ER rendering remains a later phase and is not a reason to split the v1 repository.

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
23. One canonical open-format Agent Skill with tested packaging for Codex, Claude Code, and Gemini CLI.
24. A complete operator and user documentation set with case-by-case command examples.
25. SemVer version bumping, `CHANGELOG.md` maintenance, and cross-file release-version validation for every change.
26. Complete HTTP/MCP contract schemas, behavior mapping, and representative request/response examples.
27. A provider-neutral classification boundary in which the server supplies sanitized evidence and the active harness/model may submit non-authoritative proposals.

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
- Direct calls from `sqlctx-server` to Codex, Claude, Gemini, or other model-provider APIs.
- Installation or management of the Codex, Claude Code, or Gemini CLI executables themselves.
- Separate provider-specific copies of the core classification/export workflow.

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

### 3.4 One canonical Skill, three harness packages

The harness architecture is:

```text
                         skills/sql-context-pack/SKILL.md
                                      │
                  canonical workflow, inputs, outputs, safety rules
                                      │
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
   Codex plugin/config       Claude plugin/config     Gemini extension/config
             │                        │                        │
             └────────────────────────┼────────────────────────┘
                                      ▼
                     owner-started SQL Context Pack MCP
                                      ▼
                         shared Python application core
```

Harness packages must differ only where the host requires a different manifest, discovery path, MCP configuration shape, or invocation syntax. The following behavior must remain byte-for-byte equivalent where practical and semantically equivalent otherwise:

- selection intent parsing,
- pagination loops,
- model-proposal handling,
- owner clarification,
- batching and resumability,
- bundle validation and assembly,
- final completeness checks,
- prohibited behaviors.

### 3.5 Deterministic server and model-harness responsibility boundary

The Python server must not embed a model-provider SDK or model API credential.

Responsibilities:

```text
Server/core:
  - catalog discovery and extraction
  - masking before serialization
  - deterministic Pass 1 rules
  - relationship/dependency evidence construction
  - deterministic Pass 2 rules
  - proposal validation and provenance recording
  - owner override persistence
  - materialization, export, and validation

Active Agent Skill/model:
  - interpret the user's output intent
  - review only sanitized classification evidence
  - submit optional semantic classification proposals
  - present unresolved trade-offs to the owner
  - never mark its own proposal as an owner decision

Owner:
  - configure credentials and start the service
  - approve sensitive lifecycle operations
  - decide genuinely ambiguous business categories
```

This separation makes the same server work with Codex, Claude, Gemini, or no model at all. Model proposals may improve classification recall, but their absence must not prevent deterministic extraction, indexing, or export.

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
HTTP API: owner-started
MCP transport: owner-started Streamable HTTP on the same loopback service
```

The owner must start `sqlctx-server` before an agent uses it. Harness configuration may connect to the already-running loopback MCP endpoint, but the model must not construct a database credential-bearing launch command.

Local bearer-token handoff is normative:

1. On first start, generate a cryptographically random bearer token and write it with the MCP URL and non-secret connection metadata into the user runtime directory.
2. Protect the metadata file as owner-only: mode `0600` on POSIX; an ACL limited to the current user and `SYSTEM` on Windows.
3. Server stdout may show only the MCP URL and metadata-file path. It must never print the bearer token.
4. Harness configuration and the `sqlctx` CLI may consume the token only through an owner-approved bootstrap/configuration command that reads the protected file inside the process.
5. The Skill/model must never read, display, request, log, or pass the token as a tool argument or command-line argument.
6. Connection examples may contain environment-variable or metadata-path references, never a literal token.

For remote HTTP mode:

- TLS is mandatory.
- Authentication/authorization is mandatory.
- Apply least-privilege scopes.
- Add per-client rate limiting.
- Record audit metadata without recording sample values.
- Do not enable remote mode by default.

For optional local MCP STDIO mode:

- obtain database credentials from the environment of the server process,
- never pass credentials as MCP tool parameters,
- keep STDIO disabled in the default package,
- require the owner to opt in to client-managed process lifecycle,
- document that the harness may automatically start the configured process at session startup,
- treat a harness-spawned process as owner-authorized only when the owner created or approved its configuration,
- never let the model print, inspect, or rewrite credential-bearing environment entries.

Trade-off decision: owner-started Streamable HTTP is the v1 default because it satisfies the requirement that the owner configure credentials and run the service in advance. STDIO is retained only as an explicit convenience mode because Codex, Claude Code, and Gemini CLI can manage STDIO child processes differently.

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
| username | deterministic synthetic alias | `user_k7m2q9x4p1` |
| password | full replacement; never partial | `[REDACTED:PASSWORD]` |
| password_hash | full replacement with algorithm hint only | `[REDACTED:HASH:bcrypt]` |
| secret_key | full replacement | `[REDACTED:SECRET_KEY]` |
| api_key | full replacement | `[REDACTED:API_KEY]` |
| access_token | full replacement | `[REDACTED:ACCESS_TOKEN]` |
| refresh_token | full replacement | `[REDACTED:REFRESH_TOKEN]` |
| jwt | full replacement | `[REDACTED:JWT]` |
| email | deterministic synthetic alias | `user_k7m2q9x4p1@example.invalid` |
| phone | format-preserving mask | `08xxxx1234` |
| personal_name | deterministic synthetic alias | `PERSON_0007` |
| address | generalized replacement | `[REDACTED:ADDRESS]` |
| credit_card | keep last four only | `xxxxxxxxxxxx4242` |
| binary/blob | omit content and report length | `<BINARY length=2048>` |

A fake password-like value such as `dPtv2oGEZLFvC3G1yiftC...` may be generated only when the policy explicitly requests **synthetic format preservation**. The default is a clear redaction marker, because fake secrets that look valid can be mistaken for real credentials.

### 5.5 Referential consistency

When a value is used as a business key or relation key, masking must remain stable within the snapshot.

Use deterministic pseudonymization and explicit alias encoding:

```text
digest = HMAC-SHA256(snapshot_masking_key, normalized_value)
token  = lowercase(CrockfordBase32(digest))[0:N]
```

Map the result to the target format, for example:

```text
username -> user_k7m2q9x4p1
email    -> user_k7m2q9x4p1@example.invalid
```

Requirements:

- The masking key must never be included in the export.
- The same raw value within one snapshot must map to the same alias.
- Different snapshots should use different keys by default.
- Owner-configured stable keys may be supported, but must remain outside the model context.
- Foreign-key values must retain join consistency after transformation.
- Sequence numbers based on query order are forbidden because they drift across pagination, retry, and process restart.
- Use the Crockford Base32 alphabet so examples containing decimal digits such as `user_k7m2q9x4p1` are valid and unambiguous; do not silently switch alphabets between processes.
- Maintain a protected per-snapshot alias registry in the runtime store so resume produces the same alias and collisions can be detected.
- Registry entries contain the full keyed digest, alias namespace, and chosen alias—not the normalized raw value.
- On collision, extend `N` deterministically for all colliding entries until the aliases are unique; do not assign a sequence suffix.
- Never export raw values, the masking key, or the secret alias registry. Only the resulting aliases may enter output artifacts.

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
minimum requested sample target per eligible table = 10
default requested sample target per eligible table = 10
```

Normative interpretation of the raw phrase “at least 10 rows per table”:

- A normal export request must not set `rows_per_table` below 10.
- If at least 10 eligible source rows exist, the export must contain at least 10; the v1 default contains exactly 10.
- The owner may request more than 10 up to `max_sample_rows_per_table`.
- Fewer than 10 is valid only when the table contains fewer eligible rows, access/policy removes rows, or extraction fails; the shortage must be explicit.
- The system must never duplicate or fabricate rows to satisfy the target.

Behavior:

- If the table contains at least the requested target, export exactly the requested target.
- If the table contains fewer rows than the requested target, export the actual available count.
- Never duplicate or fabricate production rows merely to reach 10.
- Record `requested_count`, `actual_count`, and `shortage_reason`.
- If policy removes every eligible row, emit zero rows and a masking/policy warning.
- Reject a user or profile request below 10 with `400 INVALID_SAMPLE_TARGET`; policy-driven shortages are reported results, not invalid requests.

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

### 8.4 Sample representation inside table SQL

The table `.sql` file must remain valid SQL and self-contained for an AI model.

Processing order:

1. Extract DDL.
2. Clean sensitive literals in DDL.
3. During final materialization only, format the SQL definition with SQLFluff.
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
-- {"ID":1,"USERNAME":"user_k7m2q9x4p1","PASSWORD":"[REDACTED:PASSWORD]"}
-- {"ID":2,"USERNAME":"user_r4v8c2n6d0","PASSWORD":"[REDACTED:PASSWORD]"}
-- @sqlctx-samples-end
```

Additional metadata belongs in the object index, not in arbitrary prose inside the SQL body.

---

## 9. SQLFluff Lifecycle

### 9.1 Installation guarantee

A Skill Markdown file alone cannot guarantee installation. The repository must include executable bootstrap logic.

Cross-harness guarantee boundary:

- Installing a plugin/extension manifest alone must not be claimed to execute Python package installation; Codex, Claude Code, and Gemini CLI have different lifecycle and consent behavior.
- Installing the Python package installs the pinned SQLFluff dependency in the managed runtime.
- On the first Skill invocation, every harness must call `sqlctx_sqlfluff_status` and then `sqlctx_sqlfluff_ensure` before formatting.
- If installation needs network/process consent, the Skill asks once and resumes after approval.
- A successful `ensure` is cached and later runs must not reinstall the same pinned version.
- Therefore the product guarantees “available before first formatting,” not “silently installed merely by copying a plugin.”

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
SQLFluff runs only after Pass 2 and owner resolution, and only for SQL files included in final materialization. Full extraction and relationship analysis use sanitized, unformatted definitions. Analysis-failed objects never enter the formatting scope.

For every materialized SQL object:

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
  "selected_categories": []
}
```

Allowed `mode` values:

| Mode | Behavior |
|---|---|
| `ask` | Pause after Pass 1 and ask the owner to choose all or selected categories |
| `all` | Analyze all objects and materialize all final categories |
| `selected` | Analyze all objects and materialize only objects assigned to selected final categories |

Version 1 has one fixed dependency behavior: excluded related objects appear only as boundary nodes/edges in indexes; their SQL and samples are not written. This `index_only` behavior is an invariant, not a request field or user-selectable mode. Direct dependency or reachable-closure materialization is outside v1 scope.

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
Idempotency-Key: <required-owner-generated-key>
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
    "selected_categories": []
  },
  "sample": {
    "rows_per_table": 10,
    "strategy": "deterministic"
  },
  "masking_policy": "strict"
}
```

`Idempotency-Key` is required. It is scoped by authenticated caller and operation. Reusing a key with the same normalized request returns the original catalog job; reusing it with a different normalized request returns `409 IDEMPOTENCY_CONFLICT`. The application core stores the record for the catalog retention period, and HTTP and MCP use the same idempotency model.

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

### 11.5a Rediscover catalog jobs

```http
GET /api/v1/catalogs?status=ready&limit=100&cursor=...
```

Response:

```json
{
  "items": [
    {"catalog_id":"cat_01J...","profile":"agrimap-readonly","status":"ready","created_at":"2026-07-18T12:00:00+07:00","expires_at":"2026-07-19T12:00:00+07:00"}
  ],
  "page": {"limit":100,"returned":1,"next_cursor":null}
}
```

Return safe descriptors only. Never return connection details, raw SQL, samples, or secret metadata.

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

### 11.6a Cancel or delete a catalog job

```http
POST   /api/v1/catalogs/{catalog_id}/cancel
DELETE /api/v1/catalogs/{catalog_id}
```

Cancellation is cooperative and idempotent. The application stops scheduling new work, propagates cancellation to an active adapter query when supported, reaches `cancelled`, and retains an honest partial report. Repeated cancellation returns the same terminal state. Delete is owner-authorized, returns `200 DeleteResult`, and is allowed only when the catalog and dependent exports are not active; otherwise return `409 JOB_ACTIVE`.

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
  "selected_categories": []
}
```

Input for selected categories:

```json
{
  "mode": "selected",
  "selected_categories": ["um", "content"]
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
    "selected_categories": ["um", "content"]
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
  "catalog_id": "cat_01J...",
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
  ],
  "page": {"limit":100,"returned":1,"next_cursor":null}
}
```

The Skill must request pages until `page.next_cursor` is `null`.

### 11.12 Submit model proposals and resolve classifications

Before owner resolution, an active harness/model may submit optional non-authoritative Pass 2 proposals:

```http
POST /api/v1/catalogs/{catalog_id}/classification-proposals
Content-Type: application/json
```

Input:

```json
{
  "proposer": {
    "harness": "codex",
    "skill_version": "1.0.0"
  },
  "proposals": [
    {
      "object_id": "table:agrimap_app.APP_AUDIT_LOG",
      "category": "audit",
      "confidence": 0.78,
      "evidence_ids": ["ev_name_audit", "ev_fk_um_user"],
      "rationale": "Name and sanitized relationship evidence indicate an audit domain."
    }
  ]
}
```

Response `200`:

```json
{
  "accepted_as_suggestion": 1,
  "rejected": 0,
  "requires_owner_resolution": 1
}
```

Rules:

- `harness` is one of `codex`, `claude`, `gemini`, or `other` and is provenance, not authority.
- Every `evidence_id` must reference sanitized evidence already present in the catalog.
- The server rejects invented object IDs, category IDs, or evidence IDs.
- A model proposal may produce only `final_suggested` or `final_unresolved`; it must never produce `final_confirmed`.
- The endpoint must not accept raw SQL, sample values, credentials, or an `owner=true` assertion.

Owner resolution remains authoritative:

#### Resolve classifications

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
Idempotency-Key: <required-owner-generated-key>
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

The export uses the same required idempotency semantics as catalog creation. A repeated key plus identical normalized request returns the existing export; a different request returns `409 IDEMPOTENCY_CONFLICT`.

Response `202`:

```json
{
  "export_id": "exp_01J...",
  "status": "queued",
  "status_url": "/api/v1/exports/exp_01J..."
}
```

### 11.13a Rediscover export jobs

```http
GET /api/v1/exports?catalog_id=cat_01J...&status=completed_with_warnings&limit=100&cursor=...
```

Response:

```json
{
  "items": [
    {"export_id":"exp_01J...","catalog_id":"cat_01J...","status":"completed_with_warnings","size_bytes":481002,"sha256":"sha256:...","expires_at":"2026-07-19T12:30:00+07:00"}
  ],
  "page": {"limit":100,"returned":1,"next_cursor":null}
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
    "manifest_url": "/api/v1/exports/exp_01J.../manifest",
    "report_url": "/api/v1/exports/exp_01J.../report"
  }
}
```

### 11.14a Cancel or delete an export job

```http
POST   /api/v1/exports/{export_id}/cancel
DELETE /api/v1/exports/{export_id}
```

Cancellation and deletion follow the catalog rules: cooperative/idempotent cancel, owner-authorized delete, no silent removal of active or unexpired artifacts, and `409 JOB_ACTIVE` when immediate deletion is unsafe.

### 11.15 Download batch bundle

```http
GET /api/v1/exports/{export_id}/bundle
```

Response:

```text
200 application/zip
```

This binary endpoint is consumed by the deterministic helper only:

```bash
sqlctx export fetch --export-id exp_01J... --destination <os-temp-path>
```

The CLI reads authentication from protected owner-approved connection metadata inside its process; the token is never present in the prompt or command line. Before assembly, it verifies declared size, bundle hash, manifest hashes, and path safety in an OS temporary directory. MCP must not return ZIP/base64 content or an unrestricted local runtime path.

Bundle filename:

```text
exp_01J....sqlctx.zip
```

### 11.16 Get manifest

```http
GET /api/v1/exports/{export_id}/manifest
```

Response `200 application/json`.

### 11.16a Get structured export report

```http
GET /api/v1/exports/{export_id}/report
```

Response `200 application/json` using the same `ExportReport` model as `sqlctx://export/{export_id}/report`.

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
  "expected_output_format_version": "1"
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
| `507` | Runtime storage quota exhausted after expired-artifact cleanup |

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

### 11.20 Contract completeness and generated API reference

The implementation must use one typed request/response model for HTTP and MCP. OpenAPI and MCP JSON Schemas must be generated from these shared models and checked for semantic equivalence in contract tests.

Every operation must document:

- function/operation name,
- HTTP method and complete relative URL when applicable,
- authentication/authorization requirement,
- path, query, and body input schema,
- success output schema and example,
- all expected error codes,
- synchronous/job behavior,
- idempotency and safe-retry behavior,
- pagination termination rule where applicable.

Minimum HTTP contract map:

| HTTP operation | Input model | Success output | Behavior |
|---|---|---|---|
| `GET /health` | none | `HealthResponse` | synchronous; no database probe |
| `GET /capabilities` | none | `CapabilitiesResponse` | synchronous; safe to retry |
| `GET /profiles` | none | `ProfileDescriptorList` | synchronous; never returns secrets |
| `POST /profiles/{profile}/test` | `profile` path | `ConnectionTestResult` | bounded read-only test |
| `GET /catalogs` | cursor/filter query | `CatalogJobPage` | safe rediscovery; paginated |
| `POST /catalogs` | `CreateCatalogRequest` + required `Idempotency-Key` header | `CatalogAccepted` | asynchronous `202`; same key/request returns same job |
| `GET /catalogs/{catalog_id}` | `catalog_id` path | `CatalogStatus` | pollable; safe to retry |
| `POST /catalogs/{catalog_id}/cancel` | path only | `CatalogStatus` | cooperative and idempotent |
| `DELETE /catalogs/{catalog_id}` | path only | `DeleteResult` | owner-authorized; rejects active dependent work |
| `GET /catalogs/{catalog_id}/category-preview` | cursor/limit query | `CategoryPreviewPage` | preliminary, paginated |
| `POST /catalogs/{catalog_id}/selection` | `MaterializationSelection` | `CatalogStatus` | state transition; idempotent for identical input |
| `GET /catalogs/{catalog_id}/sitemap` | view/cursor/limit | `SitemapPage` | paginated until `next_cursor=null` |
| `GET /catalogs/{catalog_id}/materialization-plan` | path only | `MaterializationPlan` | final-category view |
| `GET /catalogs/{catalog_id}/classification-requests` | cursor/limit query | `ClassificationRequestPage` | sanitized evidence only |
| `POST /catalogs/{catalog_id}/classification-proposals` | `ClassificationProposalBatch` | `ProposalBatchResult` | non-authoritative suggestions |
| `POST /catalogs/{catalog_id}/classification-resolutions` | `ClassificationResolutionBatch` | `ResolutionBatchResult` | owner-authorized state change |
| `GET /exports` | cursor/filter query | `ExportJobPage` | safe rediscovery; paginated |
| `POST /exports` | `ExportBatchRequest` + required `Idempotency-Key` header | `ExportAccepted` | asynchronous `202`; same key/request returns same job |
| `GET /exports/{export_id}` | path only | `ExportStatus` | pollable; safe to retry |
| `POST /exports/{export_id}/cancel` | path only | `ExportStatus` | cooperative and idempotent |
| `DELETE /exports/{export_id}` | path only | `DeleteResult` | owner-authorized immediate cleanup |
| `GET /exports/{export_id}/bundle` | path only | ZIP bytes | consumed only by `sqlctx export fetch`; validate size/hash/manifest/path safety |
| `GET /exports/{export_id}/manifest` | path only | `ExportManifest` | structured manifest |
| `GET /exports/{export_id}/report` | path only | `ExportReport` | same structured report as MCP resource |
| `POST /validations` | `ValidationRequest` | `ValidationResult` | blocks completion on mismatch |
| `GET /tooling/sqlfluff` | none | `SqlFluffStatus` | synchronous |
| `POST /tooling/sqlfluff/ensure` | `SqlFluffEnsureRequest` | `SqlFluffStatus` | install once; owner consent if needed |
| `POST /tooling/sqlfluff/update` | `SqlFluffUpdateRequest` | `SqlFluffUpdateResult` | explicit owner-authorized update only |

The generated `docs/api-and-mcp-examples.md` must include at least one success and one error example for every operation family. Do not hand-maintain a second schema that can drift from runtime models.

---

## 12. MCP Specification

MCP tools must mirror application commands, not raw HTTP mechanics.

### 12.1 Tools

```text
sqlctx_get_capabilities
sqlctx_list_profiles
sqlctx_test_profile
sqlctx_list_catalogs
sqlctx_create_catalog
sqlctx_get_catalog_status
sqlctx_cancel_catalog
sqlctx_delete_catalog
sqlctx_get_category_preview
sqlctx_set_materialization_selection
sqlctx_list_sitemap
sqlctx_get_materialization_plan
sqlctx_get_classification_requests
sqlctx_submit_classification_proposals
sqlctx_resolve_classifications
sqlctx_list_exports
sqlctx_export_batch
sqlctx_get_export_status
sqlctx_cancel_export
sqlctx_delete_export
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
sqlctx://export/{export_id}/report
```

Large bundle bytes are intentionally not an MCP resource. The sole v1 transfer path is the HTTP binary endpoint through `sqlctx export fetch`; MCP exposes only safe status, size, hash, manifest, and report metadata.

Resource parity tests are mandatory:

- `GET /api/v1/exports/{export_id}/manifest` and `sqlctx://export/{export_id}/manifest` return the same normalized `ExportManifest`.
- `GET /api/v1/exports/{export_id}/report` and `sqlctx://export/{export_id}/report` return the same normalized `ExportReport`.
- HTTP health and HTTP binary download are transport-specific exceptions; neither creates a fake MCP large-content operation.

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

### 12.5 MCP transport and complete tool contracts

Default MCP endpoint:

```text
Transport: Streamable HTTP
URL: http://127.0.0.1:<owner-selected-port>/mcp
Lifecycle: owner starts sqlctx-server before the harness connects
Authentication: bearer token supplied by harness configuration, never as a tool argument
```

MCP tools reuse the shared models from Section 11.20:

| MCP tool | Input model | Structured output | Important behavior |
|---|---|---|---|
| `sqlctx_get_capabilities` | empty object | `CapabilitiesResponse` | no database probe |
| `sqlctx_list_profiles` | empty object | `ProfileDescriptorList` | safe descriptors only |
| `sqlctx_test_profile` | `TestProfileRequest` | `ConnectionTestResult` | bounded read-only test |
| `sqlctx_list_catalogs` | `JobCursorRequest` | `CatalogJobPage` | rediscovery; cursor pagination |
| `sqlctx_create_catalog` | `CreateCatalogRequest` with required `idempotency_key` | `CatalogAccepted` | asynchronous; shared application idempotency semantics |
| `sqlctx_get_catalog_status` | `CatalogIdRequest` | `CatalogStatus` | pollable |
| `sqlctx_cancel_catalog` | `CatalogIdRequest` | `CatalogStatus` | cooperative and idempotent |
| `sqlctx_delete_catalog` | `CatalogIdRequest` | `DeleteResult` | owner-authorized; rejects active dependent work |
| `sqlctx_get_category_preview` | `CatalogCursorRequest` | `CategoryPreviewPage` | preliminary; cursor pagination |
| `sqlctx_set_materialization_selection` | `CatalogSelectionRequest` | `CatalogStatus` | selection never narrows analysis |
| `sqlctx_list_sitemap` | `SitemapRequest` | `SitemapPage` | stop only at null cursor |
| `sqlctx_get_materialization_plan` | `CatalogIdRequest` | `MaterializationPlan` | final categories only |
| `sqlctx_get_classification_requests` | `CatalogCursorRequest` | `ClassificationRequestPage` | sanitized evidence only |
| `sqlctx_submit_classification_proposals` | `ClassificationProposalBatch` | `ProposalBatchResult` | model suggestion, never owner confirmation |
| `sqlctx_resolve_classifications` | `ClassificationResolutionBatch` | `ResolutionBatchResult` | owner-authorized resolution |
| `sqlctx_list_exports` | `ExportJobCursorRequest` | `ExportJobPage` | rediscovery; cursor pagination |
| `sqlctx_export_batch` | `ExportBatchRequest` with required `idempotency_key` | `ExportAccepted` | bounded, resumable, idempotent batch |
| `sqlctx_get_export_status` | `ExportIdRequest` | `ExportStatus` | returns resource links, not large content |
| `sqlctx_cancel_export` | `ExportIdRequest` | `ExportStatus` | cooperative and idempotent |
| `sqlctx_delete_export` | `ExportIdRequest` | `DeleteResult` | owner-authorized immediate cleanup |
| `sqlctx_validate_exports` | `ValidationRequest` | `ValidationResult` | blocks false completion |
| `sqlctx_sqlfluff_status` | empty object | `SqlFluffStatus` | no install side effect |
| `sqlctx_sqlfluff_ensure` | `SqlFluffEnsureRequest` | `SqlFluffStatus` | install once when missing |
| `sqlctx_sqlfluff_update` | `SqlFluffUpdateRequest` | `SqlFluffUpdateResult` | explicit update only |

Representative paginated input and output:

```json
{
  "tool": "sqlctx_get_category_preview",
  "arguments": {
    "catalog_id": "cat_01J...",
    "cursor": null,
    "limit": 100
  }
}
```

```json
{
  "catalog_id": "cat_01J...",
  "classification_pass": "preliminary",
  "items": [
    {"category": "um", "preliminary_count": 64, "examples": ["UM_USER", "UM_ROLE"]}
  ],
  "page": {"limit": 100, "returned": 1, "next_cursor": null}
}
```

Representative model proposal input and output:

```json
{
  "tool": "sqlctx_submit_classification_proposals",
  "arguments": {
    "catalog_id": "cat_01J...",
    "proposer": {"harness": "gemini", "skill_version": "1.0.0"},
    "proposals": [
      {
        "object_id": "table:agrimap_app.APP_OBJECT",
        "category": "content",
        "confidence": 0.84,
        "evidence_ids": ["ev_fk_content", "ev_written_by_content_i"]
      }
    ]
  }
}
```

```json
{
  "accepted_as_suggestion": 1,
  "rejected": 0,
  "requires_owner_resolution": 1
}
```

For every tool, generate and publish an example for success, validation failure, state conflict, and dependency failure when those cases apply. Contract tests must call the same scenario through HTTP and MCP and compare normalized structured results.

For create operations, the HTTP `Idempotency-Key` header and MCP `idempotency_key` field map to the same application command property. A key is scoped to caller plus operation; the same normalized request returns the original job, while a different request returns `409 IDEMPOTENCY_CONFLICT` (or the equivalent structured MCP error).

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
11. Sanitized semantic proposal submitted by the active harness/model, when available

A semantic or model-generated suggestion alone must never become `final_confirmed`. The server must not call a provider API to obtain it.

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
- would materially change selected-output dependency interpretation,
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

Under the fixed v1 `index_only` boundary behavior, write boundary nodes such as:

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

SQL definitions and sample rows for boundary nodes must not be written in v1. Their sanitized descriptors and edges exist only in boundary/index metadata.

### 13.10 Harness/model proposal stage

After the server has built deterministic Pass 2 evidence and before the owner is asked to resolve ambiguity:

1. The Skill fetches all paginated classification requests.
2. The active model reviews only sanitized names, metadata, evidence IDs, relationship summaries, and masked sample shapes.
3. The Skill submits zero or more proposals through `sqlctx_submit_classification_proposals`.
4. The server validates object IDs, category IDs, evidence IDs, confidence range, and proposer provenance.
5. The server recalculates suggestions without elevating a model proposal to owner authority.
6. The Skill fetches the remaining unresolved decisions and asks one consolidated owner question.

If the harness cannot or does not provide a semantic proposal, skip steps 2–4 and continue with deterministic evidence. Cross-harness support must not depend on a particular provider model name or model version.

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
output_format_version: "1"
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
  excluded_dependencies: index_only_boundary_metadata

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
  format_scope: final_materialization
  version: "PINNED_VERSION"
  dialect: tsql
  exclude_rules:
    - CP02
    - LT01
    - RF06
  format_requested: 214
  formatted: 210
  parse_failed_preserved: 4
  format_failed_preserved: 0
```

Manifest accounting is normative:

```text
format_requested
  = formatted
  + parse_failed_preserved
  + format_failed_preserved
  = materialized_object_count
```

The four analysis-failed objects in this example are outside materialization and therefore outside SQLFluff scope. SQLFluff must not run during full extraction/analysis.

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

Per-profile overrides may lower operational limits, but must not lower `sample_rows_per_table` below 10. Only actual source availability, access policy, masking policy, or extraction failure may produce fewer than 10 exported rows, and every shortage must be reported.

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
- `output_format_version`.

Never cache raw unmasked sample values on disk by default.

### 17.6 Runtime retention and quota

Default runtime-store policy:

```yaml
runtime_store:
  completed_catalog_ttl_hours: 24
  completed_export_artifact_ttl_hours: 24
  max_total_bytes: 5368709120  # 5 GiB
```

- The owner may configure these values, but defaults must be explicit and observable through safe capabilities/operations output.
- Active jobs are never removed automatically.
- Before accepting a new catalog or export, remove expired completed artifacts using an atomic, auditable cleanup process.
- Never silently remove an active job or an unexpired artifact to make space.
- If cleanup cannot provide sufficient capacity, reject the new job with `507 RUNTIME_STORAGE_FULL` and a sanitized capacity summary.
- Owner-authorized catalog/export delete operations provide immediate cleanup subject to active-job and dependency checks.
- Catalog snapshots, checkpoints, bundles, reports, alias registries, and idempotency records follow the applicable job retention period.

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
5. List safe connection profiles and page through recent catalog/export jobs so an interrupted matching job can be rediscovered.
6. Select only the profile explicitly named or unambiguously configured.
7. Ensure SQLFluff is available.
8. Test profile connectivity.
9. Resume the matching catalog when safe; otherwise create it with a new idempotency key and the two-pass category policy.
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
21. Fetch every classification-request page until next_cursor is null.
22. Let the active harness/model optionally propose categories from sanitized evidence and submit proposals with provenance.
23. Refresh every classification-request page after proposal validation.
24. If owner decisions are required:
    a. present all final categories;
    b. present suggested categories and evidence;
    c. prioritize unresolved objects affecting selected output;
    d. ask one consolidated owner question;
    e. submit resolutions;
    f. refresh final classification and materialization plan.
25. Fetch every materialization sitemap page until next_cursor is null.
26. Collect only final included object IDs for export.
27. Record every intentionally excluded object and reason.
28. Partition included object IDs by recommended batch size and weight.
29. Export every materialization batch with a stable per-batch idempotency key.
30. Poll every export.
31. Fetch every completed bundle through `sqlctx export fetch`; never transfer ZIP/base64 through MCP.
32. Validate declared size, bundle/manifest hashes, and path safety in OS temp.
33. Assemble into the selected output root.
34. Call final validation with:
    a. expected discovered count;
    b. expected analyzed count;
    c. expected materialized count;
    d. `expected_output_format_version`;
    e. all export IDs.
35. Verify:
    discovered = analyzed + failed_analysis
    analyzed = materialized + intentionally_excluded
36. Write reports and manifest.
37. Remove all OS temporary files.
38. Report exact analysis, materialization, exclusion, warning, unresolved, and failure counts.
```

At every polling or extraction step, honor an owner/client cancellation by invoking the corresponding cooperative catalog/export cancel operation. If work is no longer needed, owner-authorized delete operations may clean retained jobs explicitly.

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
- send raw SQL or unmasked sample values to a model provider,
- represent a model proposal as an owner decision,
- silently include a newly discovered category,
- silently exclude an object moved into a selected category,
- export more sample rows than policy permits,
- request fewer than 10 sample rows per eligible table,
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

- `pyproject.toml` declares `requires-python = ">=3.11"` and unsupported versions fail with a clear bootstrap error.
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

### 19.3a Sample-row target

- A request for 9 rows per eligible table is rejected.
- A default request against a table with at least 10 eligible rows emits exactly 10 real sanitized rows.
- An owner request for 15 within the configured maximum emits exactly 15 when available.
- A table with only 7 eligible rows emits 7 with `requested_count=10`, `actual_count=7`, and a shortage reason.
- A policy that excludes every eligible row emits zero with an explicit warning.
- No test fixture or production path duplicates or fabricates rows.

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
- A harness/model proposal using valid sanitized evidence remains `final_suggested` or `final_unresolved`, never `final_confirmed`.
- A proposal with an unknown object/category/evidence ID is rejected.
- The server has no provider model API dependency or provider credential.
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

### 19.8 Documentation and case-study acceptance

The repository must ship all of the following; a README section alone is not sufficient:

| Document | Required content |
|---|---|
| `README.md` | purpose, supported databases/harnesses, five-minute path, links to detailed guides |
| `docs/getting-started.md` | Python install, profile setup, SQLFluff bootstrap, first validated export |
| `docs/server-operations.md` | owner-started HTTP/MCP service, bind/auth modes, start/stop/health/doctor |
| `docs/command-reference.md` | every CLI command with syntax, inputs, outputs, exit codes, and examples |
| `docs/use-cases.md` | ask/all/selected flows, custom output path, ambiguity resolution, resume/retry |
| `docs/api-and-mcp-examples.md` | HTTP and MCP request/response examples tied to generated schemas |
| `docs/security.md` | credential boundary, read-only grants, masking, local/remote threat assumptions |
| `docs/troubleshooting.md` | connection, privilege, SQLFluff, parse, paging, hash, and cleanup failures |
| `docs/harnesses/codex.md` | install/discover Skill, connect MCP, invoke, verify tools |
| `docs/harnesses/claude-code.md` | install/discover Skill, connect MCP, invoke, verify tools |
| `docs/harnesses/gemini-cli.md` | install/discover Skill, connect MCP, invoke, verify tools |

Command and case documentation must use tables and provide **two or three examples for each applicable topic**. Minimum topics:

| Topic | Minimum example cases |
|---|---|
| installation/bootstrap | clean machine; already installed; offline/tooling unavailable |
| profiles | SQL Server env profile; PostgreSQL env profile; invalid raw-password profile |
| server startup | loopback HTTP+MCP; custom port; rejected remote bind without TLS/auth |
| SQLFluff | status/ensure; one bad file isolated; explicit version update and rollback |
| materialization | ask then select; explicit all; explicit selected categories |
| output path | default root; explicit nested relative path; rejected traversal |
| classification | ambiguous object proposed; owner override; leave unresolved |
| batching/resume | multi-page catalog; interrupted export resume; partial object failure |
| harness use | Codex; Claude Code; Gemini CLI |

Examples must show the command or prompt, preconditions, expected important output, and what the user should do next. Provide PowerShell and POSIX shell variants where syntax differs. Secrets must use placeholders and must never resemble production credentials.

### 19.9 Codex, Claude Code, and Gemini CLI compatibility

Use the open Agent Skills `SKILL.md` format as the canonical workflow. Package it for each harness without forking the instructions:

| Harness | Distribution metadata | Skill source | Default MCP connection | Required verification |
|---|---|---|---|---|
| Codex | `.codex-plugin/plugin.json` and `harnesses/codex/config.toml.example` | root `skills/sql-context-pack/SKILL.md`; repo authoring may link through `.agents/skills/` | owner-started loopback Streamable HTTP | Skill is discoverable; tools list; selected-category E2E passes |
| Claude Code | `.claude-plugin/plugin.json` and `.mcp.json.example` | root `skills/sql-context-pack/SKILL.md`; project authoring may link through `.claude/skills/` | owner-started loopback Streamable HTTP | plugin validates; Skill is discoverable; tools list; same E2E passes |
| Gemini CLI | root `gemini-extension.json` and `harnesses/gemini/settings.json.example` | root `skills/sql-context-pack/SKILL.md`; workspace authoring may link through `.gemini/skills/` or `.agents/skills/` | owner-started loopback Streamable HTTP | extension validates; Skill is discoverable; tools list; same E2E passes |

Compatibility rules:

- Do not pin the workflow to a proprietary model name. Test supported current models through their harnesses, but keep tool schemas and business behavior provider-neutral.
- Do not rely on vendor-only frontmatter in the canonical `SKILL.md`. Vendor-only metadata belongs in the vendor manifest or a thin wrapper that references the canonical Skill.
- Keep the canonical `SKILL.md` focused and below 500 lines; place detailed contracts/examples in one-level `references/` files and deterministic helpers in `scripts/`.
- Do not expose database credentials in plugin manifests, MCP tool arguments, prompts, or checked-in config.
- Connection examples may reference `SQLCTX_MCP_URL` and `SQLCTX_API_TOKEN`; actual values are owner-managed and ignored by version control.
- A harness package must not auto-enable remote access or weaken masking.
- A harness package must not claim plugin installation itself installed SQLFluff; it must run the shared status/ensure workflow before the first format.
- The same catalog fixture, expected calls, pagination behavior, clarification behavior, and validation result must be used for all three harness conformance tests.

### 19.10 Versioning and changelog acceptance

Keep these version domains separate:

| Version | Format | Meaning |
|---|---|---|
| specification version | `1.3` | version of this design/prompt document |
| product/package/Skill version | SemVer, for example `1.0.0` | server, CLI, canonical Skill, and three harness packages released together |
| `output_format_version` | monotonic schema version, for example `"1"` | canonical bundle/index compatibility field; bump only for incompatible format change |
| SQLFluff version | exact dependency version | managed formatter runtime; updated only by explicit tooling lifecycle |

During implementation chunks:

1. Initialize the shared product version as `0.1.0-dev.0`.
2. After each completed chunk or declared sub-chunk, increment the prerelease sequence exactly once (`0.1.0-dev.1`, `0.1.0-dev.2`, and so on) and update `CHANGELOG.md`.
3. Aggregate fixes made within the same chunk into that chunk's changelog entry; do not create a release-style patch/minor bump for every file edit.
4. Keep `pyproject.toml`, health output, canonical `SKILL.md`, and all three harness manifests on the same development version.
5. Bump `output_format_version` only for an incompatible bundle/index schema change.
6. At the final release gate, after all mandatory tests pass, replace the development version with `1.0.0` exactly once and create the release changelog entry.

After v1 release, classify a release unit as breaking, feature, fix, security, documentation, or dependency and apply normal SemVer once per release unit. A version-consistency test must fail whenever any product surface differs.

Do not use `latest` as a released package/Skill version. Do not let each harness acquire an independent version in v1.

### 19.11 Cross-harness conformance acceptance

For Codex, Claude Code, and Gemini CLI, verify the same fixture scenario:

1. discover the canonical Skill,
2. connect to the owner-started MCP endpoint without exposing credentials,
3. list safe profiles and capabilities,
4. run ask mode and select `um` and `content`,
5. consume every preview and sitemap cursor,
6. analyze all objects despite selective materialization,
7. submit a non-authoritative semantic proposal with evidence references,
8. ask the owner once for unresolved categories,
9. export all batches and validate the assembled output,
10. produce equivalent normalized counts, files, indexes, and reports.

CI may use deterministic harness simulators for every commit. Before release, run opt-in smoke tests against the currently supported Codex, Claude Code, and Gemini CLI versions and record the tested harness versions. Exact natural-language wording may differ; schemas, safety invariants, call ordering, completeness, and artifacts must not.

The repository must create `.github/workflows/ci.yml` during the skeleton phase. It must run formatting, linting, type checking, unit, contract, integration, E2E, and harness-simulator jobs as those phases become available; a required phase may not remain absent merely because acceptance text mentions it.

### 19.12 Authoritative implementation context

- Commit this specification byte-for-byte as `docs/spec/design-spec-v1.3.md` and record its SHA-256 in `docs/spec/design-spec-v1.3.sha256`.
- Treat v1.3 as the only implementation source of truth; raw, v1.1, and v1.2 remain archive/traceability inputs only.
- Every fresh implementation session reads `docs/implementation-state.md`, the immutable invariants, and only the routed v1.3 sections needed for its chunk.
- Do not rewrite the immutable contract from memory and do not load the full specification when the routed sections suffice.
- Token counts are tokenizer/model dependent; measure with the target harness tokenizer when needed and never present a hard-coded estimate as fact.
- Do not attribute authorship to a model unless verifiable metadata exists.

---

# 20. Chunked Implementation Prompts

Use the following prompts sequentially in the same repository, but run **one chunk per fresh agent session**. Do not skip a chunk. Every session must first read `docs/implementation-state.md`, `CHANGELOG.md`, the immutable invariants, the routed sections named by its chunk, and only the relevant code. It must update implementation state before stopping. v1.3 is the sole source of truth; do not use raw, v1.1, or v1.2 as implementation context.

Section-routing index:

| Chunk | Required v1.3 sections |
|---|---|
| 0 | 1–4, 19.10–19.12, 20 |
| 1 | 1.3, 3, 6, 11.20, 12, 19.1, 19.10–19.12 |
| 2 | 4–5, 8–9, 17.5–17.6 |
| 3 | 6–8, 10, 17 |
| 4 | 10, 13–16, 19.3–19.6 |
| 5 | 4.5, 11–12, 17.3–17.6 |
| 6 | 13, 15, 17–18, 21 |
| 7 | 1.3, 3.4–3.5, 19, 21–23 |

---

## Prompt Chunk 0 — Immutable Contract

```text
You are implementing a repository named `sql-context-pack`.

This is a fresh Chunk 0 session. Read `docs/spec/design-spec-v1.3.md` Sections 1–4, 19.10–19.12, and 20 before changing implementation files. If the file is not present yet, copy the supplied v1.3 artifact byte-for-byte into that path, record its SHA-256, and then read those routed sections. Do not summarize or regenerate the authoritative specification.

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
- Use one GitHub monorepo named `sql-context-pack`; do not split server, CLI, Skill, or harness packages into separate repositories in v1.
- One shared application core must serve both HTTP and MCP interfaces.
- The owner configures credentials and starts the server before an agent connects.
- Default MCP transport is owner-started Streamable HTTP on loopback; client-managed STDIO is explicit opt-in only.
- Agents/models must never receive database credentials or connection strings.
- Use connection profile names in all public interfaces.
- No arbitrary SQL endpoint or MCP tool is allowed.
- Database access is read-only.
- Cleansing/masking must happen before any value is serialized, logged, returned, or written.
- SQLFluff formatting must run one SQL file at a time and only for final-materialization SQL after Pass 2 and owner resolution.
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
- The server must not call provider model APIs; the active harness/model may submit only sanitized, non-authoritative classification proposals.
- Selective output must preserve excluded connected objects as boundary metadata.
- Output business category folders must be directly under the selected output root.
- The skill must use cursor pagination until next_cursor is null.
- The skill must separately validate discovered, analyzed, failed-analysis, materialized, and intentionally-excluded counts before claiming completion.
- SQLFluff must be a pinned dependency and must also have an executable ensure/status/update lifecycle.
- Normal export must never silently update SQLFluff.
- Version 1 supports tables and stored procedures as required object types.
- Graph-ready metadata is required; graph rendering itself is a later phase.
- Maintain one canonical `skills/sql-context-pack/SKILL.md` and package it for Codex, Claude Code, and Gemini CLI without copied workflow logic.
- Start at `0.1.0-dev.0`, increment the prerelease sequence once per completed chunk/sub-chunk, and bump to `1.0.0` once at the final release gate; update `CHANGELOG.md` and pass version-consistency tests.
- Ship case-by-case operator, command, API/MCP, troubleshooting, security, and per-harness guides with two or three examples per applicable topic.
- Version 1 uses deterministic sampling only and fixed index-only boundary metadata; no relationship-aware sampling or direct/closure dependency materialization.
- Catalog/export jobs have paginated rediscovery, cooperative cancel, owner-authorized delete, 24-hour completed retention defaults, and a configurable 5 GiB runtime quota.
- HTTP create calls require `Idempotency-Key`; MCP create tools require `idempotency_key`; both map to the same application contract.
- Bundle transfer uses only `sqlctx export fetch` over authenticated loopback HTTP; never ZIP/base64 through MCP.

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
1. `docs/spec/design-spec-v1.3.md` as the byte-for-byte authoritative artifact plus `docs/spec/design-spec-v1.3.sha256`,
2. `docs/implementation-state.md`,
3. `docs/requirements.md`,
4. `docs/architecture.md`,
5. `docs/security.md`,
6. `docs/output-format.md`,
7. `docs/acceptance-criteria.md`,
8. `docs/versioning.md`,
9. `docs/harness-compatibility.md`,
10. `CHANGELOG.md`,
11. a central version source initialized at `0.1.0-dev.0`.

Derived documents must link to exact authoritative sections and add implementation decisions only where necessary. They must not become rewritten substitute contracts. Before stopping, increment the shared version once for completed Chunk 0 and record the result in `CHANGELOG.md` and `docs/implementation-state.md`.

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

This is a fresh Chunk 1 session. Read `docs/implementation-state.md`, `CHANGELOG.md`, and `docs/spec/design-spec-v1.3.md` Sections 1.3, 3, 6, 11.20, 12, 19.1, and 19.10–19.12. Do not reinterpret or weaken the immutable contract.

Implement only the repository skeleton and shared core/domain contracts.

REQUIRED MODULES
- src/sqlctx/core
- src/sqlctx/application
- src/sqlctx/adapters
- src/sqlctx/security
- src/sqlctx/formatting
- src/sqlctx/classification
- src/sqlctx/indexing
- src/sqlctx/exporting
- src/sqlctx/server/http
- src/sqlctx/server/mcp
- src/sqlctx/cli

REQUIRED SHARED SKILL/PACKAGING SKELETON
- skills/sql-context-pack/SKILL.md
- .codex-plugin/plugin.json
- .claude-plugin/plugin.json
- gemini-extension.json
- harnesses/codex
- harnesses/claude
- harnesses/gemini

Create only minimal valid manifests in this chunk. Do not duplicate SKILL.md into vendor directories.

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
- ClassificationProposal
- ClassificationProposalBatch
- ProposalBatchResult
- ClassificationRequest
- ClassificationResolution
- SampleRequest
- SamplePage
- MaskingDecision
- SqlFormatResult
- ExportBatchRequest
- ExportJob
- ExportArtifact
- CatalogJobPage
- ExportJobPage
- DeleteResult
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
- Use explicit enums for engine, object type, job status, edge type, sensitivity class, classification status, classification pass, materialization mode, and inclusion reason. Dependency handling is fixed index-only behavior, not a public mode enum.
- Add JSON-schema-compatible validation models for HTTP/MCP boundaries.
- Do not implement database queries yet.
- Do not implement HTTP routes or MCP tools yet.
- Add tests proving sensitive fields cannot be serialized from internal profile objects.

Add `pyproject.toml` with `requires-python = ">=3.11"` and a pinned/locked dependency strategy. Include SQLFluff as a required dependency but keep the actual version in one central dependency definition.

Create `.github/workflows/ci.yml` now. It must run formatting, linting, type checking, and current unit/contract tests; add integration, E2E, and harness-simulator jobs as their code appears rather than leaving CI creation until release.

Add one central product version and tests proving the same value is exposed by Python package metadata and all three harness manifests. Initialize `CHANGELOG.md` with the current version.

Before stopping, increment the development prerelease exactly once for completed Chunk 1 and update `CHANGELOG.md` and `docs/implementation-state.md`.

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

This is a fresh Chunk 2 session. Read `docs/implementation-state.md`, `CHANGELOG.md`, and `docs/spec/design-spec-v1.3.md` Sections 4–5, 8–9, and 17.5–17.6. Do not modify the immutable product scope.

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
- Implement owner-only connection metadata/token bootstrap: mode `0600` on POSIX, current-user/`SYSTEM` ACL on Windows, token never on stdout or a command line.

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
Encode a Crockford Base32 HMAC digest prefix into aliases such as `user_k7m2q9x4p1`; do not use query-order sequence numbers.
Persist the collision-checked per-snapshot alias registry in the protected runtime store so retry/resume is stable; extend the digest prefix deterministically on collision.
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
Run the formatter only for final-materialization SQL after Pass 2 and owner resolution. Do not format the full analysis snapshot. For each materialized file independently:
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

Before stopping, increment the development prerelease exactly once for completed Chunk 2 and update `CHANGELOG.md` and `docs/implementation-state.md`. Stop after tests pass.
```

---

## Prompt Chunk 3 — Database Adapters and Catalog Discovery

```text
Continue the existing `sql-context-pack` repository.

This work is deliberately split into fresh sessions. Each sub-chunk reads `docs/implementation-state.md`, `CHANGELOG.md`, and `docs/spec/design-spec-v1.3.md` Sections 6–8, 10, and 17:

- Chunk 3A: shared adapter contract/fixtures plus PostgreSQL and MySQL.
- Chunk 3B: MariaDB as a distinct adapter plus SQL Server.
- Chunk 3C: Oracle, catalog orchestration, paging, cancellation, retention/quota integration, and cross-adapter contract tests.

Complete, test, document, and increment the development prerelease once per sub-chunk before starting the next fresh session.

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
- Propagate cooperative job cancellation to an active database statement when the driver supports it; otherwise stop scheduling and close/rollback safely at the next boundary.

SAMPLING
- Minimum and default requested target is 10 rows per eligible table.
- Reject a configured/requested target below 10.
- If at least the requested number of eligible rows exists, return exactly the requested number.
- If fewer exist or policy removes rows, return actual count and shortage metadata.
- Never fabricate duplicate rows.
- Support deterministic sampling only; do not implement `relationship_aware` sampling.
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
Implement paginated safe catalog-job rediscovery plus the 24-hour completed-catalog retention and shared 5 GiB runtime quota. Never delete active or unexpired work silently.

MARIADB
Keep MariaDB as a distinct adapter even where implementation shares reusable MySQL helpers.

ORACLE
Discover privileges/capabilities at runtime. Do not assume DBMS_METADATA or all catalog views are always available.

TESTS
- adapter contract tests,
- identifier safety,
- allowed schema enforcement,
- sample limit,
- below-10 request rejection,
- fewer-than-10 behavior,
- deterministic ordering,
- capability negotiation,
- sanitized database errors.

Use containerized integration tests where practical and fixture/mocked adapter tests where a proprietary database cannot run in CI.

Stop after all three sub-chunks' adapter and catalog tests pass and `docs/implementation-state.md` records the next routed chunk.
```

---

## Prompt Chunk 4 — Classification, Indexes, Output Packaging, and Validation

```text
Continue the existing `sql-context-pack` repository.

This is a fresh Chunk 4 session. Read `docs/implementation-state.md`, `CHANGELOG.md`, and `docs/spec/design-spec-v1.3.md` Sections 10, 13–16, and 19.3–19.6.

Implement:
1. category rule configuration,
2. Pass 1 preliminary name-based classification,
3. user materialization selection,
4. Pass 2 relationship-aware final classification,
5. classification-change tracking,
6. sanitized non-authoritative model proposal intake,
7. unresolved owner-decision workflow,
8. materialization planning,
9. relationship/dependency indexes,
10. graph-ready indexes,
11. output package writer,
12. integrity validation.

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
11. validated sanitized semantic proposal from the active harness/model, if any

The server must not import a Codex, Anthropic, or Gemini model SDK and must not call a provider model API.

Materialization must apply selected category names to Pass 2 categories.
Track objects moved into and out of selected categories.

Only owner override or deterministic configured rules supported by context may produce final `confirmed`.
Ambiguous objects must be `unresolved`.
Do not guess.

Model proposals:
- accept only known object/category/evidence IDs,
- record harness and Skill-version provenance,
- may produce suggested/unresolved only,
- never impersonate an owner resolution,
- remain optional so deterministic export still works without a model proposal.

Classification request must include:
- all current categories,
- suggested new categories,
- all unresolved objects,
- candidates,
- confidence,
- evidence,
- unresolved option.

Every classification-request response is cursor-paginated with `items` and `page: {limit, returned, next_cursor}`.

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
- After Pass 2 and owner resolution, format cleaned DDL only for final-materialization files.
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
- canonical manifest `output_format_version` and validation `expected_output_format_version`.

The SQLFluff coverage invariant is `format_requested = formatted + parse_failed_preserved + format_failed_preserved = materialized_object_count`. Analysis-failed and intentionally excluded objects are outside formatting scope. Selective dependency behavior is fixed index-only boundary metadata; do not implement direct or closure modes.

Stop after unit tests pass and provide one realistic fixture output containing:
- um/tables/UM_USER.sql
- um/tables/UM_ROLE.sql
- content/tables/CONTENT.sql
- content/tables/CONTENT_SHARE.sql
- at least one stored procedure per category
- one unresolved object
- relationship and graph indexes.

Before stopping, increment the development prerelease exactly once for completed Chunk 4 and update `CHANGELOG.md` and `docs/implementation-state.md`.
```

---

## Prompt Chunk 5 — HTTP and MCP Interfaces

```text
Continue the existing `sql-context-pack` repository.

This is a fresh Chunk 5 session. Read `docs/implementation-state.md`, `CHANGELOG.md`, and `docs/spec/design-spec-v1.3.md` Sections 4.5, 11–12, and 17.3–17.6. The endpoint/tool lists below are only an index; implement exact request, response, pagination, idempotency, error, and example contracts from Sections 11–12. Do not invent schemas from this abbreviated list.

Implement thin HTTP and MCP interfaces over the existing application core.

HTTP BASE
/api/v1

HTTP ENDPOINTS
- GET  /health
- GET  /capabilities
- GET  /profiles
- POST /profiles/{profile}/test
- GET  /catalogs
- POST /catalogs
- GET  /catalogs/{catalog_id}
- POST /catalogs/{catalog_id}/cancel
- DELETE /catalogs/{catalog_id}
- GET  /catalogs/{catalog_id}/category-preview
- POST /catalogs/{catalog_id}/selection
- GET  /catalogs/{catalog_id}/sitemap
- GET  /catalogs/{catalog_id}/materialization-plan
- GET  /catalogs/{catalog_id}/classification-requests
- POST /catalogs/{catalog_id}/classification-proposals
- POST /catalogs/{catalog_id}/classification-resolutions
- GET  /exports
- POST /exports
- GET  /exports/{export_id}
- POST /exports/{export_id}/cancel
- DELETE /exports/{export_id}
- GET  /exports/{export_id}/bundle
- GET  /exports/{export_id}/manifest
- GET  /exports/{export_id}/report
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
- 507 runtime storage full

Default HTTP bind:
- 127.0.0.1
- random local bearer token
- remote mode disabled
- write URL/token connection metadata owner-only in the user runtime directory
- stdout may print only the MCP URL and metadata path, never the token

Default MCP transport:
- owner-started Streamable HTTP at `/mcp` on the same loopback service
- bearer token comes from harness configuration, never a tool argument
- STDIO is disabled unless the owner explicitly opts into client-managed lifecycle

MCP TOOLS
- sqlctx_get_capabilities
- sqlctx_list_profiles
- sqlctx_test_profile
- sqlctx_list_catalogs
- sqlctx_create_catalog
- sqlctx_get_catalog_status
- sqlctx_cancel_catalog
- sqlctx_delete_catalog
- sqlctx_get_category_preview
- sqlctx_set_materialization_selection
- sqlctx_list_sitemap
- sqlctx_get_materialization_plan
- sqlctx_get_classification_requests
- sqlctx_submit_classification_proposals
- sqlctx_resolve_classifications
- sqlctx_list_exports
- sqlctx_export_batch
- sqlctx_get_export_status
- sqlctx_cancel_export
- sqlctx_delete_export
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

IDEMPOTENCY AND BUNDLE TRANSFER
- HTTP catalog/export creation requires `Idempotency-Key`; MCP creation requires `idempotency_key`; normalize both into the same application property.
- Same scoped key plus same normalized request returns the original job; a changed request returns `IDEMPOTENCY_CONFLICT`.
- Implement `sqlctx export fetch --export-id ...` as the only Skill-facing bundle path. It consumes HTTP binary internally from protected connection metadata and validates size/hash/manifest/path safety in OS temp.
- Never return ZIP/base64 or an unrestricted local runtime path through MCP.

Generate HTTP OpenAPI and MCP input/output schemas from shared typed models. Add a contract table and request/response/error examples to `docs/api-and-mcp-examples.md`. Contract tests must compare normalized HTTP and MCP results for the same scenarios.

Use the current stable official MCP Python SDK and pin an exact compatible version.
Do not use a pre-release SDK in production unless the repository explicitly opts into it and tests it.

Add API contract tests and MCP Inspector-compatible tests.
Before stopping, increment the development prerelease exactly once for completed Chunk 5 and update `CHANGELOG.md` and `docs/implementation-state.md`. Stop after all interface tests pass.
```

---

## Prompt Chunk 6 — Agent Skill and End-to-End Acceptance

```text
Continue the existing `sql-context-pack` repository.

This is a fresh Chunk 6 session. Read `docs/implementation-state.md`, `CHANGELOG.md`, and `docs/spec/design-spec-v1.3.md` Sections 13, 15, 17–18, and 21.

Implement the `sql-context-pack` Agent Skill.

The skill must execute this exact workflow:

1. Parse the user request.
2. Resolve output directory: explicit path, configured default, or repository-root/sql-context.
3. Resolve initial materialization mode: ask, all, or selected.
4. Discover server capabilities.
5. List safe profiles and page through recent catalog/export jobs so an interrupted matching job can be rediscovered.
6. Select only an explicit or unambiguous profile.
7. Ensure SQLFluff is available.
8. Test profile connectivity.
9. Resume the matching catalog when safe; otherwise create it with a new idempotency key and the two-pass category policy.
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
20. Inspect moved-into/moved-out categories, connected new categories, and boundary relationships.
21. Fetch every classification-request page until next_cursor is null.
22. Optionally submit sanitized model proposals with harness/Skill provenance; never submit them as owner decisions.
23. Refresh every classification-request page after proposal validation.
24. If owner decisions are required, ask one consolidated question, submit resolutions, and refresh final classification and the materialization plan.
25. Fetch every materialization sitemap page until next_cursor is null.
26. Collect only final included object IDs for export.
27. Record every intentionally excluded object and reason.
28. Partition included object IDs by recommended batch size and weight.
29. Export every materialization batch with a stable per-batch idempotency key.
30. Poll every export.
31. Fetch every completed bundle through `sqlctx export fetch`; never transfer ZIP/base64 through MCP.
32. Validate declared size, bundle/manifest hashes, and path safety in OS temp.
33. Assemble only managed files into the selected output root.
34. Call final validation with expected discovered, analyzed, materialized, `expected_output_format_version`, and all export IDs.
35. Verify:
    discovered = analyzed + failed_analysis
    analyzed = materialized + intentionally_excluded
36. Write reports and manifest.
37. Remove all OS temporary files in finally.
38. Report exact analysis, materialization, exclusion, warning, unresolved, and failure counts.

At every polling or extraction step, honor owner/client cancellation through the catalog/export cancel operations. Use paginated list operations for rediscovery after interruption and owner-authorized delete only for deliberate cleanup.

The skill must never:
- ask for a database password,
- print credentials or environment variables,
- call arbitrary SQL,
- stop after the first category-preview or sitemap page,
- use selected categories to restrict database extraction,
- finalize categories from Pass 1 names alone,
- apply selection to preliminary object IDs,
- guess categories,
- send raw SQL or unmasked sample values to a model provider,
- mark a model proposal as an owner resolution,
- fabricate rows,
- request fewer than 10 sample rows per eligible table,
- weaken masking,
- format a whole directory,
- enable fix-even-unparsable,
- silently update SQLFluff,
- write `.tmp-*` in the project,
- overwrite unmanaged files,
- hide failures,
- claim completion before validation.
- read or print the bearer token,
- pass a bearer token as a tool or command-line argument,
- download a bundle through an MCP resource,
- implement direct/closure dependency materialization or relationship-aware sampling.

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
18. A model proposal with valid sanitized evidence remains suggested until owner resolution.
19. A proposal with invented evidence or an attempted owner assertion is rejected.
20. Catalog/export cancellation is cooperative and idempotent.
21. Expired-artifact cleanup and `507 RUNTIME_STORAGE_FULL` behavior respect active/unexpired jobs.
22. The SQLFluff manifest equation covers exactly the materialized files.

Create:
- skills/sql-context-pack/SKILL.md as the single canonical Skill
- skills/sql-context-pack/examples/
- skills/sql-context-pack/references/
- skills/sql-context-pack/scripts/ only when deterministic code is necessary
- fixtures/
- end-to-end tests
- README usage section that links to the required detailed documentation

Run:
- formatting
- linting
- type checking
- unit tests
- integration tests
- end-to-end tests

Do not mark the project complete if any mandatory acceptance test is skipped.
Before stopping, increment the development prerelease exactly once for completed Chunk 6 and update `CHANGELOG.md` and `docs/implementation-state.md`.
At the end, report:
- implemented requirements,
- test evidence,
- known limitations,
- exact commands to install, start the server, run doctor, and invoke the skill.
```

---

## Prompt Chunk 7 — Cross-harness Packaging, Documentation, Versioning, and Release Gate

```text
Continue the existing `sql-context-pack` monorepo.

Split this work across fresh sessions, each reading `docs/implementation-state.md`, `CHANGELOG.md`, and `docs/spec/design-spec-v1.3.md` Sections 1.3, 3.4–3.5, 19, and 21–23:

- Chunk 7A: three-harness packaging, documentation, generated examples, and deterministic conformance simulators.
- Chunk 7B: supported installed-harness smoke tests, final audit, and release gate.

Complete, test, document, and increment the development prerelease once for 7A. Chunk 7B performs the single final `1.0.0` release transition only after every mandatory gate passes.

Do not create another repository and do not copy the canonical Skill workflow.

PACKAGE THE SAME CANONICAL SKILL FOR:
- Codex using `.codex-plugin/plugin.json` plus a checked-in config example,
- Claude Code using `.claude-plugin/plugin.json` plus `.mcp.json.example`,
- Gemini CLI using `gemini-extension.json` plus a checked-in settings example.

All packages must reference `skills/sql-context-pack/SKILL.md` at the repository root. Vendor directories may contain only manifests, installation/configuration guidance, and thin compatibility metadata.

DEFAULT CONNECTION
- Owner starts `sqlctx-server` before an agent connects.
- Use owner-started loopback Streamable HTTP MCP at `/mcp`.
- Use the owner-approved bootstrap/configuration command to read protected connection metadata. Examples may reference `SQLCTX_MCP_URL`, `SQLCTX_API_TOKEN`, or the metadata path, but never commit or print actual values.
- Keep client-managed STDIO disabled unless the owner explicitly opts in.
- Do not install or manage the harness CLI executables.

CREATE AND COMPLETE:
- README.md
- docs/getting-started.md
- docs/server-operations.md
- docs/command-reference.md
- docs/use-cases.md
- docs/api-and-mcp-examples.md
- docs/security.md
- docs/troubleshooting.md
- docs/harnesses/codex.md
- docs/harnesses/claude-code.md
- docs/harnesses/gemini-cli.md
- CHANGELOG.md

DOCUMENTATION RULES
- Provide exact install, profile, start, health, doctor, MCP-connect, export, validation, update, and invocation commands.
- Use tables for command/use-case studies.
- Provide two or three examples for each applicable topic: bootstrap, profiles, startup, SQLFluff, materialization, output paths, classification, paging/resume, and harness use.
- Include preconditions, expected important output, and next action.
- Use placeholders only; never include realistic secrets.
- Generate API/MCP schemas and examples from shared runtime models where possible.

VERSIONING
- Use one SemVer product version for package, server, CLI, canonical Skill, Codex plugin, Claude plugin, and Gemini extension.
- Keep incrementing `0.1.0-dev.N` exactly once per completed chunk/sub-chunk and update `CHANGELOG.md` in that transition.
- Aggregate changes within a chunk; do not create a release bump for every edit.
- Keep canonical `output_format_version` independent and bump it only for incompatible bundle/index changes.
- Change the product version to `1.0.0` exactly once in Chunk 7B after all release gates pass.
- Add a version-consistency test covering pyproject metadata, health output, `SKILL.md` `metadata.version`, and all three manifests.

CONFORMANCE TESTS
Run the same deterministic fixture through Codex, Claude, and Gemini harness adapters/simulators. Verify:
- Skill discovery,
- MCP tool discovery,
- no credential exposure,
- ask/select behavior,
- complete cursor traversal,
- full analysis despite selective output,
- optional model proposal remains non-authoritative,
- consolidated owner resolution,
- identical normalized counts and artifacts,
- final validation.

Before release, run opt-in smoke tests against installed supported versions of Codex, Claude Code, and Gemini CLI. Record exact harness versions and results. A missing required harness smoke test blocks a release unless the release report explicitly marks the build non-releaseable.

FINAL RELEASE GATE
- formatting passes,
- linting passes,
- type checking passes,
- unit, contract, integration, E2E, and harness tests pass,
- documentation links and examples validate,
- every HTTP/MCP public operation has schema and examples,
- no duplicate Skill workflow exists,
- version consistency passes,
- `.github/workflows/ci.yml` exercises every mandatory implemented phase,
- CHANGELOG includes the release,
- working tree contains no project-local temporary residue.

Only after every line above passes, set every product surface to `1.0.0`, add the release changelog entry, rerun version consistency and the mandatory release test suite, and update `docs/implementation-state.md` to released.

Report:
- why one repository is used,
- final repository tree,
- released version and changelog entry,
- commands for each harness,
- test and smoke-test evidence,
- known limitations.
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
10. Every normal request asks for at least ten real sanitized rows per eligible table; exactly the requested count is emitted when available, and every unavoidable shortage is reported without fabrication.
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
22. One GitHub monorepo contains the Python core, server, CLI, canonical Skill, tests, documentation, and all three harness packages.
23. Codex, Claude Code, and Gemini CLI use the same canonical `SKILL.md` and pass the same normalized conformance scenario.
24. The default MCP connection targets an owner-started loopback Streamable HTTP service; opt-in STDIO never exposes database credentials to the model.
25. The server never calls a provider model API; harness/model proposals use sanitized evidence and remain non-authoritative until owner resolution.
26. Every public HTTP operation and MCP tool has generated input/output schemas, behavior/error documentation, and representative examples.
27. Operator, command, case-by-case, troubleshooting, security, and per-harness guides exist with two or three examples for each applicable topic.
28. Development chunks use synchronized `0.1.0-dev.N` transitions; the final gate creates `1.0.0` once, updates `CHANGELOG.md`, and passes cross-manifest version consistency.
29. SQLFluff formats only final-materialization files and manifest formatting counters satisfy `format_requested = formatted + parse_failed_preserved + format_failed_preserved = materialized_object_count`.
30. `output_format_version` is the only output-format field name, with `expected_output_format_version` used by validation.
31. Catalog/export list operations rediscover jobs and cooperative cancel operations can reach `cancelled`.
32. Completed catalogs and export artifacts default to 24-hour retention under a configurable 5 GiB runtime quota; active and unexpired work is not silently deleted.
33. Owner-authorized delete operations clean catalog/export jobs explicitly.
34. Bearer-token connection metadata is owner-only and the token never appears on stdout, in prompts, or in tool/command-line arguments.
35. HTTP and MCP create operations pass the same idempotency contract tests.
36. Large bundles travel only through `sqlctx export fetch` over HTTP; MCP never returns ZIP/base64 or unrestricted local paths.
37. HTTP and MCP expose the same structured export report.
38. Python 3.11 or newer is enforced and checked-in CI covers the required phases.
39. `docs/spec/design-spec-v1.3.md` matches the authoritative artifact hash and fresh sessions use routed sections plus implementation state.

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

Precise cross-harness answer:

```text
Plugin/extension file copied only: no install-time guarantee.
Python package installed or first Skill run approved: yes, ensure the pinned SQLFluff once before formatting.
Normal later run: reuse; do not reinstall.
Update: explicit owner command only.
```

---

# 23. Direct Answer: How Many GitHub Repositories?

Create **one GitHub repository**:

```text
sql-context-pack
```

Keep the Python server, HTTP/MCP interfaces, CLI, canonical Skill, Codex plugin manifest, Claude Code plugin manifest, Gemini CLI extension manifest, tests, fixtures, examples, documentation, and changelog in that monorepo.

Do not create these as separate repositories in v1:

```text
sqlctx-server
sqlctx-skill
sqlctx-codex
sqlctx-claude
sqlctx-gemini
```

They share one security boundary, one protocol contract, one canonical workflow, and one release version. Split later only when a component obtains a genuinely independent owner, security boundary, or release cadence.

---

# 24. Final Classification Decision

The recommended default behavior is:

```yaml
classification:
  strategy: two_pass

selection:
  mode: ask

selective_output:
  excluded_dependencies: index_only_boundary_metadata
```

Runtime behavior:

```text
1. Discover every permitted object name.
2. Build a preliminary category preview.
3. Ask: all categories or selected categories?
4. Record selected category names.
5. Dump and sanitize every permitted object.
6. Analyze all relationships and routine dependencies.
7. Run deterministic Pass 2 classification.
8. Let the active harness/model optionally submit sanitized non-authoritative proposals.
9. Ask the owner once for remaining ambiguous business decisions.
10. Apply selected category names to final categories.
11. Materialize only included objects.
12. Preserve excluded connected objects as boundary metadata.
```

This design is intentionally more expensive than filtering from names alone, but it prevents the more serious failure mode: silently omitting SQL objects whose names do not reveal their real business context.

---

# 25. Official Sources of Trust

- SQLFluff dialect reference: https://docs.sqlfluff.com/en/stable/reference/dialects.html
- SQLFluff installation/getting started: https://docs.sqlfluff.com/en/stable/gettingstarted.html
- SQLFluff CLI production behavior and exit codes: https://docs.sqlfluff.com/en/latest/production/cli_use.html
- SQLFluff troubleshooting/parsing errors: https://docs.sqlfluff.com/en/stable/guides/troubleshooting/how_to.html
- SQLFluff default configuration and `fix_even_unparsable`: https://docs.sqlfluff.com/en/stable/configuration/default_configuration.html
- MCP specification — tools: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- MCP specification — resources: https://modelcontextprotocol.io/specification/2025-11-25/server/resources
- MCP authorization: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- Official MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Open Agent Skills specification: https://agentskills.io/specification
- Codex Agent Skills: https://learn.chatgpt.com/docs/build-skills
- Codex MCP configuration: https://learn.chatgpt.com/docs/extend/mcp
- Claude Code Agent Skills: https://code.claude.com/docs/en/slash-commands
- Claude Code plugin reference: https://code.claude.com/docs/en/plugins-reference
- Claude Code MCP: https://code.claude.com/docs/en/mcp
- Gemini CLI Agent Skills: https://geminicli.com/docs/cli/using-agent-skills/
- Gemini CLI extension reference: https://geminicli.com/docs/extensions/reference/

At implementation/release time, re-verify the current stable harness, MCP specification, MCP Python SDK, and SQLFluff versions. Pin tested stable versions; do not adopt an alpha, beta, draft, or release candidate merely because it is newer.

---

# 26. Raw Requirement Traceability and v1.2 Gap Closure

| Original raw requirement | Historical assessment through v1.2 | v1.3 authoritative coverage |
|---|---|---|
| Detailed but non-drifting implementation prompt; chunk when large | covered, but release/harness work was not chunked | Section 20, including new Chunk 7 |
| Secure owner-managed DB user/password; owner starts service | mostly covered; default MCP process lifecycle was ambiguous | Sections 4.1–4.5 and 12.5 |
| Universal repository/product name | covered | Sections 1.1–1.3 |
| Dump table DDL and stored procedures, format, classify | covered | Sections 2, 7, 9, 10, and 13 |
| `um`/`content` direct folder structure | covered | Section 15.3 |
| Output path inferred from user language | covered | Sections 15.1 and 18.2–18.3 |
| At least 10 representative rows per table | ambiguous conflict: v1.1 used “up to 10” and allowed lower profile limits | Sections 8.1, 17.1, Chunk 3, and Definition of Done item 10 |
| Python/Node trade-off and Web/MCP service design | covered; Python selected | Sections 3, 11, and 12 |
| Function/API name, URL, HTTP behavior, input/output, examples | HTTP mostly covered; MCP per-tool contracts and examples were incomplete | Sections 11.20 and 12.5 |
| Sensitive cleansing before model input/output | covered | Section 5 |
| 100–1000+ objects, paging, sitemap, batching, resumability | covered | Sections 10 and 17 |
| Skill uses service intelligently and never guesses categories | covered | Sections 13 and 18 |
| Tags/indexes, ER cardinality, graph/tree-ready future phase | covered | Sections 14 and 16 |
| SQLFluff auto-ensure once and explicit update | covered, but plugin-install timing needed precision | Sections 9 and 22 |
| SQL Server/MySQL/MariaDB/Oracle/PostgreSQL dialect mapping | covered and corrects `psql` to SQLFluff `postgres` | Sections 6, 7, and 19.7 |
| One broken file must not stop directory-wide formatting | covered | Section 9.6–9.8 |
| No project-local temporary residue | covered | Sections 9.9 and 15.2 |
| Ask/all/selected and two-pass full analysis | covered | Sections 10 and 13 |
| Model updates changelog and increases version | v1.2 required a release bump for every repository edit, which caused build-version drift | Sections 19.10, Chunk 0–7, and Definition of Done item 28 define `0.1.0-dev.N` chunk transitions and one final `1.0.0` bump |
| MCP and Skill usage guides case by case | only a README usage mention; incomplete | Sections 19.8 and Chunk 7 |
| Command studies/examples in tables, two or three cases when applicable | missing | Section 19.8 and Chunk 7 |
| Codex, Claude, and Gemini harness/model support | missing | Sections 1.3, 3.4–3.5, 19.9–19.11, and Chunk 7 |

Appended raw requirements 6–23 close these verified v1.2 gaps:

| Appended raw requirement | v1.2 finding | v1.3 closure |
|---|---|---|
| 6 SQLFluff stage/accounting | stage undefined; `820 + 22` did not equal 214 materialized files | Sections 8.4, 9.7, 15.5; format only final materialization and require `210 + 4 + 0 = 214` in the example |
| 7 report symmetry | MCP report resource had no HTTP peer | Sections 11.16a, 11.20, 12.2, 12.5 |
| 8 canonical output version | three names could become separate fields | Sections 11.17, 15.5, 17.5, 19.10 use only `output_format_version` / `expected_output_format_version` |
| 9 HMAC alias mapping | sequence-looking examples did not define encoding/collision/resume | Section 5.4–5.5 defines Base32 digest aliases and protected per-snapshot registry |
| 10 pagination/workflow parity | classification example lacked page envelope; Chunk 6 omitted manifest step | Sections 11.11, 18.3, and Chunk 6 use paginated envelopes and matching 38-step flows |
| 11 list/cancel | cancelled state existed without callable operations; jobs could not be rediscovered | Sections 11, 12, 17, 18 and Chunk 5 add paginated list and cooperative cancel operations |
| 12 retention/quota/delete | runtime snapshot/artifact lifetime was unbounded | Sections 11.19 and 17.6 define 24-hour defaults, 5 GiB quota, 507, and owner delete |
| 13 token handoff | random token transport to harness/CLI was unspecified | Sections 4.5, 12.5 and Chunks 2/5 define owner-only metadata and no token stdout/arguments |
| 14 idempotency | mentioned but no field/header semantics | Sections 11.5, 11.13, 11.20, 12.5 define required HTTP header/MCP field and conflict behavior |
| 15 bundle transfer | MCP binary/base64 versus HTTP use was ambiguous | Sections 11.15 and 12.2 select `sqlctx export fetch` over HTTP and remove MCP bundle bytes |
| 16 Python/CI | no minimum Python and no chunk created CI | Sections 1.3, 19.1, 19.11 and Chunk 1 require Python >=3.11 and `.github/workflows/ci.yml` |
| 17 build/release versions | every-edit release bump could drift before release | Section 19.10 and Chunks 0–7 define development prereleases and one release bump |
| 18 authoritative spec routing | Chunk 0 paraphrase could drift from the design contract | Sections 1.3, 19.12, 20 require byte-for-byte v1.3, hash, section routes, and implementation state |
| 19 fresh sessions/sub-chunks | same long session risked context overflow | Section 20 uses fresh sessions and splits adapters/harness release work |
| 20 source precedence | old versions could conflict during implementation | Sections 19.12 and 20 make v1.3 the only implementation source of truth |
| 21 cut optional scope | relationship-aware sampling and dependency direct/closure were not in raw v1 | Sections 8 and 10.3 plus Chunks 3/4/6 remove them from v1 |
| 22 model attribution | no verifiable author metadata exists | Section 19.12 forbids authorship guesses without metadata |
| 23 token estimate | token count is tokenizer-dependent | Sections 19.12 and 20 use spec-in-repo/routing and require measurement with target tokenizer |

The statement that all four analysis failures were necessarily extraction failures was not provable from v1.2 because the failure type was not specified. v1.3 therefore fixes the demonstrable defect—undefined SQLFluff scope and inconsistent counters—without inventing a cause for those failures.

All raw requirements now have a normative section, implementation-chunk instruction, or acceptance criterion. The original raw text is preserved, and its additions narrow v1 scope where stated.

---

# 27. Resolved Trade-offs for v1.3

| Decision | Selected v1.3 behavior | Rejected alternative and reason |
|---|---|---|
| GitHub repositories | one `sql-context-pack` monorepo | multiple repos create version/contract drift without a v1 ownership boundary |
| implementation language | Python | Node.js still needs Python/SQLFluff and adds runtime coordination |
| default MCP lifecycle | owner-started loopback Streamable HTTP | default client-spawned STDIO conflicts with the owner-runs-first requirement; STDIO remains opt-in |
| provider integration | deterministic provider-neutral server plus optional harness/model proposals | server-side Codex/Claude/Gemini API integrations add provider credentials and duplicate harness capability |
| three-harness Skill packaging | one canonical open-format `SKILL.md` plus three manifests/configs | three copied Skills would drift |
| ten-row wording | request at least 10; export the requested real rows when available; explicitly report unavoidable shortage | duplicating/fabricating rows damages truth; silently allowing requests below 10 violates the stated target |
| SQLFluff bootstrap | pinned dependency plus first-use `ensure`, cached after success | claiming that copying any vendor plugin silently runs `pip install` is not portable or secure |
| SQLFluff stage | format only final-materialization SQL after Pass 2/owner resolution | formatting every analyzed object adds cost without helping relationship analysis |
| dependency materialization | fixed index-only boundary metadata | direct/closure modes are outside the raw v1 scope and can erase selective-output savings |
| bundle transport | deterministic CLI fetch over authenticated loopback HTTP | MCP ZIP/base64 inflates payloads and risks message limits; unrestricted runtime paths violate the boundary |
| runtime lifecycle | 24-hour completed retention, 5 GiB quota, explicit delete | unbounded storage and silent eviction are unsafe |
| implementation context | byte-for-byte v1.3 in repo, routed fresh sessions | a single long context or agent-written contract summary invites drift |
| dependency/spec freshness | re-verify and pin tested stable versions at release | automatically adopting prerelease or `latest` can break reproducibility |

These defaults are implementation-ready. Changing any of them is a product trade-off that must update this specification, acceptance tests, version, and changelog before implementation continues.
