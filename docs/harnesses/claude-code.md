# Claude Code

## Configure

Validate the root plugin, use `.mcp.json.example`, and keep the canonical Skill at its repository
path:

```powershell
claude plugin validate .
sqlctx harness run --harness claude
sqlctx harness run --harness claude -- "Create only final um/content context under ./docs/db"
```

The owner-started service remains independent of Claude lifecycle. The child receives only the
agent connection values; it never receives the owner credential. Expected discovery and next
action match Codex: one Skill, 24 tools, capabilities, then profiles. Model classification output
is a suggestion only.
