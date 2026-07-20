# Getting Started

Follow this guide from top to bottom. Normal marketplace users do not clone the repository, provide
`--source`, start MCP manually, or install Python repeatedly.

For the consolidated marketplace path containing only native harness commands and Agent Skill
actions, use [Agent and Harness Lifecycle](agent-harness-lifecycle.md).

## 1. Requirements

- Windows with owner-approved CPython 3.11 or newer.
- A read-only database account.
- Codex, Claude Code, or Gemini CLI.
- The managed service remains on `127.0.0.1`; it creates no firewall rule.

SQL Context Pack uses the selected machine Python directly. It never creates or manages `venv`,
virtualenv, conda, pipx, or a bundled Python environment.

If Python is unavailable, install it once and verify it:

```powershell
winget install -e --id Python.Python.3.13
py -3 --version
```

Repository developers may run `scripts\python-preflight.ps1` on Windows or
`./scripts/python-preflight.sh` on Linux/macOS. SQL Context Pack never installs Python silently.

## 2. Install the Skill or extension

Choose one provider. These are the normal installation commands.

### Codex

```powershell
codex plugin marketplace add gasxhermvc/sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

### Claude Code

```powershell
claude plugin marketplace add gasxhermvc/sql-context-pack
claude plugin install sql-context-pack@sql-context-pack
```

### Gemini CLI

```powershell
gemini extensions install https://github.com/gasxhermvc/sql-context-pack
```

The native manager downloads the plugin/extension and makes the Skill available. It does not run a
silent privileged post-install hook.

## 3. Complete first-time setup

1. Open a new Codex/Claude/Gemini room or session.
2. Run:

   ```text
   $sql-context-pack setup
   ```

3. Read the terminal explanation and approve UAC once. Setup installs the owner Python package,
   registers the automatic `SQLContextPack` Windows Service, applies protected ProgramData ACLs,
   and verifies authenticated loopback health. It does not open a firewall port.
4. Open one final new room/session so MCP starts from the installed runtime.

If no profile exists, setup starts the secure profile wizard. Password input is hidden. Profile YAML
stores only a safe credential reference; connection values and credentials remain encrypted in the
owner runtime directory.

## 4. Select a database connection

Each new room begins disconnected. List profiles and connect explicitly:

```text
$sql-context-pack profiles
$sql-context-pack connect agrimap-dev
```

The bridge tests the database before activation. The selected profile exists only for that room;
changing it does not restart the shared Windows Service.

Additional interactive commands:

```text
$sql-context-pack help
$sql-context-pack change-profile
$sql-context-pack disconnect
```

For owner-side profile administration, use:

```powershell
sqlctx profile list
sqlctx profile test agrimap-dev
sqlctx profile schemas agrimap-dev
sqlctx profile scope agrimap-dev --schema agrimap_app --schema agrimap_etl --schema agrimapadm --exclude 'i[0-9]*'
```

Allowed schemas are an explicit allowlist. Database visibility never expands the profile scope.
SQL Server system objects and configured exclusion patterns are removed before classification.

## 5. Create the first context

After connecting, ask the Skill to build sanitized context from the active profile. It will discover
the allowed schemas, exclude system/owner-filtered objects, show business categories, request your
selection, and run the validated export workflow.

```text
Create all SQL context from the active profile under ./sql-context
```

Use `$sql-context-pack help` whenever you want an interactive list of supported actions.

The default output is the lean `ai` profile: SQL, masked Markdown samples, YAML metadata, and
concise Markdown indexes/reports. JSON, JSONL, graph, and machine indexes are skipped completely.
Request `output profile full`, `sample format csv`, or `sample format json` explicitly only when
those artifacts are needed. Final `lut` objects are always included as lookup metadata.
When no sample-row count is supplied, the catalog uses the connected profile's
`sample_rows_per_table` value rather than a hidden Agent default.

## 6. Update

The native manager downloads updated plugin source first.

### Codex

```powershell
codex plugin marketplace upgrade sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

### Claude Code

```powershell
claude plugin marketplace update sql-context-pack
claude plugin install sql-context-pack@sql-context-pack
```

### Gemini CLI

```powershell
gemini extensions update sql-context-pack
```

After the native update, open a new room/session and run `$sql-context-pack setup`, then open one
final room when Skill/MCP content changed. Setup reads the exact installed plugin cache and updates
only changed layers:

- identical fingerprints: no wheel, pip, UAC, PATH rewrite, or service restart;
- application-only change: one OS-temp wheel, `--no-deps`, then health-checked restart;
- dependency, database-extra, or Python ABI change: rebuild the dependency layer;
- plugin-only change: new room required, service restart not required;
- service-host-only change: restart only the service host.

Python itself is never reinstalled. `sqlctx update --source <checkout>` is an explicit development
override, not a normal marketplace instruction.

## 7. Uninstall

Run uninstall while the Skill is still installed:

```text
$sql-context-pack uninstall
```

The bundled lifecycle removes items in this order:

1. stop and unregister `SQLContextPack` Windows Service;
2. remove replaceable ProgramData application/service files;
3. stop SQL Context Pack bridge processes;
4. uninstall the owner `sql-context-pack` Python package;
5. remove this native plugin/extension and its dedicated marketplace.

Service removal must succeed before native plugin removal begins. Encrypted profiles, config, and
retained runtime data are preserved by default. Do not use only `codex plugin remove`, because that
cannot remove the privileged Windows Service.

## 8. SQL Server named instances and development certificates

Enter endpoint values without surrounding quotes:

- named instance: `10.20.30.40\DB2019`;
- named instance with static port: `10.20.30.40\DB2019,1544`;
- explicit TCP endpoint: `10.20.30.40,1544`;
- plain host/IP: `10.20.30.40` plus the separate port prompt.

Named-instance discovery requires SQL Server Browser/UDP 1434. Prefer a known static TCP port when
Browser is unavailable.

Certificate verification defaults on. For an explicitly approved development profile only:

```powershell
sqlctx profile trust-certificate agrimap-dev --enable
sqlctx profile test agrimap-dev
```

Encryption remains enabled. Restore certificate-chain verification with `--disable`. Production
profiles should use a trusted issuing CA/server certificate.

## 9. Diagnostics and development installation

Safe diagnostics:

```powershell
sqlctx doctor
sqlctx runtime status
sqlctx approvals list
sqlctx audit tail --limit 50
```

Foreground `sqlctx-server` and `scripts\start-server.ps1` remain development-only fallbacks. For an
intentional development checkout, package-only installation remains available:

```powershell
py -3 -m pip install --user -e ".[all-databases]"
py -3 -m sqlctx.cli doctor
```

See [Marketplace Lifecycle](codex-marketplace.md),
[Global Installation](global-installation.md), [Command Reference](command-reference.md),
[Troubleshooting](troubleshooting.md), and the provider-specific guides under
[Harnesses](harnesses/).
