# Agent and Harness Lifecycle

This is the normal marketplace workflow for owners who want the Agent and native harness to manage
SQL Context Pack. It does not require a repository checkout or manual product-CLI, Python-package,
platform-service, or MCP-launcher installation.

This managed runtime workflow is cross-platform in the current release. Windows uses the local
`SQLContextPack` Windows Service. Linux uses a systemd user service when available. macOS uses a
launchd user agent. Other Unix hosts use an owner background process with pid/state files. Native
Codex, Claude Code, and Gemini CLI download commands remain platform-dependent according to each
harness.

There are only two command locations:

- **Harness terminal:** use the provider's native plugin/extension manager.
- **Agent chat:** send a `$sql-context-pack ...` action after opening a new room/session.

Native plugin managers cannot silently run a privileged Windows installer. The explicit Agent
`setup`, `repair`, and `uninstall` actions explain the operation. UAC is requested only on Windows
when the Windows Service must change.

## 1. Install

Choose one harness and run only its native terminal commands. These commands install the
plugin/extension into the selected harness; the later Agent-managed runtime setup is cross-platform.

### Codex

```shell
codex plugin marketplace add gasxhermvc/sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

### Claude Code

```shell
claude plugin marketplace add gasxhermvc/sql-context-pack
claude plugin install sql-context-pack@sql-context-pack
```

### Gemini CLI

```shell
gemini extensions install https://github.com/gasxhermvc/sql-context-pack
```

Then complete the managed runtime installation:

1. Open a new room/session in the selected harness.
2. Send this command to the Agent:

   ```text
   $sql-context-pack setup
   ```

3. Review the explanation and approve UAC when requested on Windows. The installed Skill deploys
   the owner package and loopback-only platform runtime from its own plugin cache.
4. Open one final new room/session so the MCP bridge loads the installed runtime.
5. Confirm discovery and connect:

   ```text
   $sql-context-pack profiles
   $sql-context-pack connect <profile-name>
   ```

Do not start MCP manually. The platform runtime is persistent and each room/session receives its
own STDIO bridge automatically.

## 2. Repair and Update

### Repair

When the Skill is visible but the package, platform runtime, or MCP runtime is missing or unhealthy,
send this command to the Agent:

```text
$sql-context-pack repair
```

The Skill reuses its installed plugin cache, explains the affected layers, preserves owner data,
and health-checks the repaired service. Open a new room/session afterward when MCP or Skill content
changed.

If the Skill itself is missing, repeat the native **Install** commands for the selected harness,
open a new room/session, and run `$sql-context-pack setup`.

### Update

First refresh the plugin/extension through the native harness manager.

#### Codex

```shell
codex plugin marketplace upgrade sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

#### Claude Code

```shell
claude plugin marketplace update sql-context-pack
claude plugin install sql-context-pack@sql-context-pack
```

#### Gemini CLI

```shell
gemini extensions update sql-context-pack
```

After the native update:

1. Open a new room/session.
2. Send `$sql-context-pack setup` to deploy the exact refreshed plugin cache. Unchanged layers are
   skipped automatically.
3. Open one final room/session when Skill or MCP content changed.

Do not use repair as a substitute for the native marketplace update: repair redeploys the currently
installed cache; update fetches a newer cache first.

## 3. Uninstall

Run uninstall while the Skill is still installed. In Agent chat, send:

```text
$sql-context-pack uninstall
```

Review the explanation and approve UAC if requested. The managed lifecycle performs this order:

1. stop and unregister the platform runtime;
2. remove replaceable managed application/runtime files;
3. stop SQL Context Pack room bridges;
4. uninstall the owner Python package;
5. remove the dedicated native plugin/extension and repository marketplace.

Do not remove only the native plugin first; doing so can leave the managed runtime and owner
package behind. Encrypted profiles, configuration, and retained runtime data are preserved by
default. Data purge is a separate explicit owner decision.

To reinstall later, repeat **Install** for one harness only. Do not install both the public and
personal SQL Context Pack plugins at the same time.

## 4. Agent Command List

Send these commands in Agent chat, not in PowerShell.

| Agent command | Result |
|---|---|
| `$sql-context-pack setup` | Installs or updates the managed owner package and platform runtime from the installed plugin cache. |
| `$sql-context-pack repair` | Repairs missing or unhealthy managed runtime layers and verifies health. |
| `$sql-context-pack help` | Shows available profile, context, diagnostics, update, and lifecycle actions. |
| `$sql-context-pack profiles` | Lists configured safe profile names and readiness without exposing credentials. |
| `$sql-context-pack connect <profile-name>` | Tests and activates one profile for the current room/session. |
| `$sql-context-pack change-profile [profile-name]` | Lists choices when omitted or safely changes the active room profile. |
| `$sql-context-pack disconnect` | Disconnects only the current room without cancelling retained jobs. |
| `$sql-context-pack remove-profile <profile-name>` | Routes the owner to `sqlctx profile remove <profile-name> --yes`; profile removal is not an MCP tool. |
| `Create all SQL context under ./sql-context` | Exports every profile-allowed table and stored procedure after full analysis. |
| `Resume the interrupted SQL context run` | Rediscovers matching retained catalog/export jobs and resumes validation. |
| `$sql-context-pack doctor` | Runs safe package, service, MCP, SQLFluff, and profile readiness diagnostics. |
| `$sql-context-pack runtime status` | Reports protected runtime counts, sizes, retention, and cleanup guidance. |
| `$sql-context-pack approvals list` | Lists safe pending owner approvals and their expiry. |
| `$sql-context-pack trust-certificate <profile> --enable\|--disable` | Routes an explicit development-certificate decision without disabling encryption. |
| `$sql-context-pack update` | Shows and follows the selected harness's native update flow, then deploys via setup. |
| `$sql-context-pack uninstall` | Removes the service and owner package before removing the dedicated native plugin/extension. |

Each new room/session starts disconnected. Use `profiles` and `connect` before creating database
context. Normal context requests never require database credentials in Agent chat.
