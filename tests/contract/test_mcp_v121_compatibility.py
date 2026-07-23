from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

V121_TOOL_HASHES = {
    "sqlctx_cancel_catalog": "f501bfb50c92d19289090378ea43895b0ff7e2972ac1d431436a2f24c70ba866",
    "sqlctx_cancel_export": "a79c195ffe22543011a779b5280f3a9db1a462e3bd931bc6ff8293ea1b8d74a1",
    "sqlctx_create_catalog": "1173d763124b1372f977662f26f886605d9a8739a3251d3717ef9fc18a6a761a",
    "sqlctx_delete_catalog": "4b0cec47bff0ef32470b7eff61c34afb60aca787be38d73faa7d095da1a5bf51",
    "sqlctx_delete_export": "6079921ef3183bfd15022c02938b65bc28d5d7cf60e8fbf26627a295862d8f54",
    "sqlctx_export_batch": "4579beb6e0a393cc8367c334e498536144da97d6db8e4ddc394ddbe4fe210be9",
    "sqlctx_get_capabilities": "ba1a9a7ee77e501eb924a66ca664c35a88db90a1a970333ec3e9e0ee7c994ed6",
    "sqlctx_get_catalog_status": "fb46bbcebb3a04c7954fdab763f8da8a9121e537141e8a19a5b9634ddcadec0d",
    "sqlctx_get_category_preview": "bfbae25e825d80e089028a5cc5f4fa08e9e4a18ee039e752e4a8d2663d9bc5c2",
    "sqlctx_get_classification_requests": "06bc3d2e7a3e089c850b0d57a23ccff85a8e0c960c8609d5b7b7f99677cc81a0",
    "sqlctx_get_export_status": "ee503092e97ec9501701f79c04eff96c9c52282a49e1a40720afbc0b5f798d40",
    "sqlctx_get_materialization_plan": "f8696941ff121064c9a100883931f3f6cbe9e892012d2e85d89e54b21c953c02",
    "sqlctx_list_catalogs": "77e26dc49a03d45a142730e48df5030f93a603dc35ae21c2e43e8043e57e4b83",
    "sqlctx_list_exports": "ba4a2b12bb26b3a5745a4cd2a53acd71b674fa59de95334f9717151ea2c3a859",
    "sqlctx_list_profiles": "f06a06727d3fd995cfd2120dc2e5ea6e7ca3cca1c33c93323272008b42c02c29",
    "sqlctx_list_sitemap": "2540bc5c16cce4cfa21e0da61788c8d7a3aceac4ef89bfd168ad7ab7ab33ee19",
    "sqlctx_resolve_classifications": "b1888d4e871406431027fb93ebb9f253d0adc2f0d19921dbcf41090cb62cf1a1",
    "sqlctx_set_materialization_selection": "de4f8cc94683c84e847a830df41bd4a31fc94385ac3d8ccfd91878bccab51cca",
    "sqlctx_sqlfluff_ensure": "620a28b6447bb5bc48cf499e8f271df287464144afa2633ec4b88a08ae8f3b98",
    "sqlctx_sqlfluff_status": "de57802f93abe837f102d2d9d6db9f0b461f2fc6752cf3186e8a18ad02488864",
    "sqlctx_sqlfluff_update": "809b51d73242a3fd3ab1ce61c5ccbe874a24c6914e68c1e89dd28365000ee5e5",
    "sqlctx_submit_classification_proposals": "6dcac10be4bd886cb7565adb3a381a7ce8a47358535fcc234908a2eea9566831",
    "sqlctx_test_profile": "2ed2fb023137c5f4c3148acc3ea1c595085717f3db4a9c8302ca9f8abe03e847",
    "sqlctx_validate_exports": "95cbf3522165264b008292da3a0c5bbae94a21801c34191d7234841eabbd9e96",
}

V121_RESOURCE_HASHES = {
    "sqlctx://export/{export_id}/manifest": "a399620b5e19700b7a4f01a5e12567176d97ebb87b3fce4d8a9f377ac6e7446e",
    "sqlctx://export/{export_id}/report": "6d4bf441cf5bf97e5016158ff2e680f4694830e651463ed438cb05dafb3dd990",
}


def digest(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_v122_is_exactly_one_additive_mcp_tool_without_old_contract_drift() -> None:
    generated = json.loads((ROOT / "docs/generated/mcp-tools.json").read_text(encoding="utf-8"))
    tools = {item["name"]: item for item in generated["tools"]}
    assert set(tools) - set(V121_TOOL_HASHES) == {"sqlctx_query_data"}
    for name, expected in V121_TOOL_HASHES.items():
        item = tools[name]
        contract = {
            key: item.get(key) for key in ("name", "description", "inputSchema", "outputSchema")
        }
        assert digest(contract) == expected


def test_v122_preserves_both_mcp_resources_exactly() -> None:
    generated = json.loads((ROOT / "docs/generated/mcp-tools.json").read_text(encoding="utf-8"))
    resources = {item["uriTemplate"]: item for item in generated["resource_templates"]}
    assert set(resources) == set(V121_RESOURCE_HASHES)
    for uri, expected in V121_RESOURCE_HASHES.items():
        assert digest(resources[uri]) == expected
