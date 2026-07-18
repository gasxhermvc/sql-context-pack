# Gemini CLI

## Configure

Use `gemini-extension.json`, `harnesses/gemini/settings.json.example`, and the same canonical Skill:

```powershell
gemini extensions validate .
sqlctx harness run --harness gemini
sqlctx harness run --harness gemini -- -p "Resume the exact SQL context request and validate output"
```

The wrapper sets the loopback URL and agent bearer only for the child. The extension must not
start the server, manage Python, or use STDIO by default. Expected important output is Skill/MCP
discovery; next, traverse every cursor and use HTTP fetch through the deterministic CLI.
