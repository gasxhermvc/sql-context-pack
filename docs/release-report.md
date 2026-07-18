# Release Report — 1.0.3

Release date: 2026-07-18  
Authoritative specification: [v1.5](spec/design-spec-v1.5.md)  
Specification SHA-256: `c627afd2a0659de96f56780dd12a10664e2447becc0652b6321e6bcd3bc5b4d8`  
Product version: `1.0.3`  
Output format version: `1`

## Repository decision

The product uses one Git repository. The Python application core, HTTP and MCP interfaces,
canonical Skill, all three harness manifests, fixtures, tests, generated contracts, documentation,
and release gate change together. This prevents interface and workflow drift and requires only one
version-consistency gate. No second repository is required.

## Final repository tree

```text
.
├── .claude-plugin/          # Claude Code manifest
├── .codex-plugin/           # Codex plugin manifest
├── .github/workflows/       # mandatory CI phases
├── config/                  # profile/category owner examples
├── dist/                    # wheel, sdist, SHA256SUMS
├── docs/
│   ├── generated/           # OpenAPI and MCP schemas/examples
│   ├── harnesses/           # Codex, Claude Code, Gemini guides
│   └── spec/                # immutable v1.5 contract and hash
├── fixtures/                # conformance and realistic output
├── harnesses/               # thin adapters and conformance simulator
├── prompts/                 # source requirement/spec history
├── scripts/                 # preflight, schema, validator, smoke helpers
├── skills/sql-context-pack/ # the only canonical SKILL.md and references
├── src/sqlctx/              # typed application package
├── tests/                   # unit, contract, integration, E2E, harness
├── CHANGELOG.md
├── pyproject.toml
└── README.md
```

## Verification evidence

| Gate | Result |
|---|---|
| Authoritative source/preserved/declared SHA-256 | identical |
| Ruff formatting and lint | passed; 75 files |
| Strict mypy | passed; 53 source files |
| Pytest unit/contract/integration/E2E/harness | passed; 52 tests, 0 skipped |
| HTTP contracts | 28 operations with typed schemas and deterministic examples |
| MCP contracts | 24 strict tools with structured outputs/examples; 2 resources |
| Canonical Skill and Codex plugin validators | passed |
| Claude plugin validator | passed |
| Gemini extension validator | passed |
| Cross-harness conformance simulator | identical safe result for all three harnesses |
| Installed harness smoke | Codex `0.144.5`; Claude Code `2.1.212`; Gemini CLI `0.50.0` |
| Wheel install smoke | package `1.0.3`, HTTP health 200, 24 MCP tools |
| Project-local environment/temp residue | none before packaging; project creates no Python environment |

Release commands used the selected host CPython `3.11.10`. Product commands always invoke
SQLFluff through the selected interpreter's absolute path. No Skill, project, or runtime virtual
environment was created.

## Artifacts

| File | Bytes | SHA-256 |
|---|---:|---|
| `sql_context_pack-1.0.3-py3-none-any.whl` | 83,292 | `2174fdc0912f5fc9d6dfe90312ef166843baaed07f18dc2b2319701d3a5a87cb` |
| `sql_context_pack-1.0.3.tar.gz` | 64,470 | `d3b8bffd90d787a81523646d39a26b2b5e176b7d6d10bbe393479789451e935e` |

The same values are recorded in `dist/SHA256SUMS` and were re-read after the build.

## Harness invocation

The owner starts `sqlctx-server` first, then launches one of:

```powershell
sqlctx harness run --harness codex
sqlctx harness run --harness claude
sqlctx harness run --harness gemini
```

The wrapper reads protected agent connection metadata and passes it only to the child process. It
does not print the bearer, pass the owner-control credential, start a client-managed STDIO server,
or install a harness executable.

## Known limitations

- Live database verification requires an owner-provided read-only database and the matching
  optional engine driver; deterministic adapter contracts were used for this release gate.
- v1 is loopback-only and owner-started. Remote service mode and client-managed STDIO remain out
  of scope.
- Installed-harness smoke verifies the installed CLI versions and each vendor's native manifest
  validation. The deterministic conformance simulator exercises the complete normalized workflow
  without spending model tokens or contacting an owner database.
- SQLFluff installation/update is available only for an owner-approved base host Python user site.
  An owner-selected existing conda/virtual environment is verify/execute-only and must be managed
  manually by its owner.
