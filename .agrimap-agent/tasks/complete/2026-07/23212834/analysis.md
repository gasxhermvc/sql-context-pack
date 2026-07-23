# Analysis

## Current State

- Requirement v1.22 and the existing operator documents correctly describe Query Data, ETL scope,
  LUT synchronization, and MCP/CLI limits, but the workflow is distributed across README,
  getting-started, command reference, server operations, use cases, and the canonical Skill.
- A user must currently infer whether to create/export context, run `sync-data`, or use Query Data by
  combining several documents.
- The implemented runtime and generated contracts are already verified and require no behavior or
  public-schema change for this request.

## Findings

- The smallest complete solution is one consolidated Thai guide plus navigation links, rather than
  duplicating another set of product commands across every document.
- The guide must preserve three boundaries that are easy to confuse: sync keeps old retained scope,
  Query Data never creates/caches context, and unlimited-row output is CLI-only.
- ETL schema/prefix/category ambiguity and LUT 10-to-15 replacement need explicit examples because
  both previously caused incomplete expectations.
- Requirement versioning is mandatory under repository governance even though the change is
  documentation-only; v1.23 must preserve v1.22 byte-for-byte after its revision marker.
- Test decision: documentation/spec integrity tests are required; no new runtime behavior test is
  needed because product code and contracts do not change.

## Proposed Approach

- Add Requirement v1.23/hash preserving v1.22 and extend frozen-spec integrity coverage.
- Add `docs/working-guide.md` in Thai with a three-workflow decision table, exact commands,
  complete ETL/LUT rules, JOIN examples, flags, safety, troubleshooting, and update/new-room steps.
- Link the guide from README, getting-started, command reference, and canonical Skill; update
  requirements, acceptance, versioning, security/output normative references, implementation state,
  and changelog.
- Add a focused contract test proving the guide exists and contains the authoritative boundaries,
  then run `scripts/dev-check.ps1 -Task all` and regulated QA.

## Pre-write gate

1. Objective/non-goals: owner-approved Prompt V6 authorizes a documentation-only consolidated guide;
   product code, runtime actions, database access, deployment, and publication are excluded.
2. Write boundary: Requirement v1.23/hash, guide/navigation/Skill documents, focused documentation
   tests, implementation state, changelog, and workflow artifacts.
3. Allowed behavior: documentation routing and clarity only; all v1.22 runtime/public contracts stay
   unchanged.
4. Simplest complete approach: one primary guide with links avoids contradictory duplicated manuals.
5. Acceptance: exact spec preservation/hash, guide content/link tests, full dev-check/build, zero
   residue, and independent regulated QA.

## Writer verification

- `scripts/dev-check.ps1 -Task all` passed formatting, Ruff, strict mypy over 63 source files,
  176 tests, sdist/wheel builds, and repository-local residue cleanup.
- No product code/public schema, live database, runtime/service/MCP session, deployment, commit,
  publish, or release action was performed.
