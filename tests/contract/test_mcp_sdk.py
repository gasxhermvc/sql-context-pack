from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path


def test_pinned_sdk_generates_strict_structured_tool_schemas() -> None:
    if importlib.util.find_spec("mcp") is None:
        project = Path("pyproject.toml").read_text(encoding="utf-8")
        source = Path("src/sqlctx/server/mcp/server.py").read_text(encoding="utf-8")
        assert '"mcp==1.28.1"' in project
        assert 'model_config["extra"] = "forbid"' in source
        assert (
            "registered.parameters = registered.fn_metadata.arg_model.model_json_schema" in source
        )
        return
    from sqlctx.server.mcp.server import build_mcp

    async def inspect() -> None:
        server = build_mcp(object(), "agent:contract")  # type: ignore[arg-type]
        tools = await server.list_tools()
        assert len(tools) == 24
        assert all(tool.inputSchema.get("additionalProperties") is False for tool in tools)
        assert all(tool.outputSchema is not None for tool in tools)

    asyncio.run(inspect())
