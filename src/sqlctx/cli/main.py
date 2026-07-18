"""Owner-local control and deterministic bundle transfer CLI."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Annotated

import httpx
import typer

from sqlctx.core.errors import SqlCtxError
from sqlctx.core.models import ExportStatus
from sqlctx.exporting.assembly import assemble_bundles
from sqlctx.exporting.validation import inventory_output, validate_bundle
from sqlctx.exporting.writer import sha256_bytes
from sqlctx.formatting.manager import SqlFluffManager
from sqlctx.security.approvals import ApprovalService
from sqlctx.security.profiles import YamlConnectionProfileRepository
from sqlctx.security.runtime import CredentialMetadataStore, JsonRuntimeStateStore

app = typer.Typer(help="Build and validate sanitized SQL context packages.", no_args_is_help=True)
approvals_app = typer.Typer(help="Grant request-bound privileged operation approvals.")
export_app = typer.Typer(help="Fetch integrity-protected export bundles.")
validate_app = typer.Typer(help="Validate locally assembled managed output.")
sqlfluff_app = typer.Typer(help="Verify and owner-manage SQLFluff on this exact host Python.")
harness_app = typer.Typer(
    help="Launch a supported harness with protected agent connection metadata."
)
app.add_typer(approvals_app, name="approvals")
app.add_typer(export_app, name="export")
app.add_typer(validate_app, name="validate")
app.add_typer(sqlfluff_app, name="sqlfluff")
app.add_typer(harness_app, name="harness")


@app.command("doctor")
def doctor() -> None:
    """Verify host Python, pinned SQLFluff, protected server metadata, and safe profiles."""
    state = JsonRuntimeStateStore()
    tooling = SqlFluffManager(state).status()
    metadata_ready = state._safe("connection-metadata.json").is_file()
    profiles = YamlConnectionProfileRepository().list_descriptors()
    result = {
        "python": {
            "version": tooling.python_version,
            "executable_fingerprint": tooling.python_executable_fingerprint,
            "supported": True,
        },
        "sqlfluff": {
            "version": tooling.sqlfluff_version,
            "ready": tooling.ready,
            "tooling_fingerprint": tooling.tooling_fingerprint,
        },
        "server_metadata_ready": metadata_ready,
        "profiles": {"configured": len(profiles), "ready": sum(item.ready for item in profiles)},
        "creates_python_environment": False,
    }
    typer.echo(json.dumps(result, sort_keys=True))
    if not tooling.ready:
        raise typer.Exit(code=1)


@sqlfluff_app.command("status")
def sqlfluff_status() -> None:
    """Verify the selected host interpreter and pinned SQLFluff without mutation."""
    descriptor = SqlFluffManager(JsonRuntimeStateStore()).status()
    typer.echo(json.dumps(descriptor.model_dump(mode="json"), sort_keys=True))


@sqlfluff_app.command("ensure")
def sqlfluff_ensure() -> None:
    """Install pinned SQLFluff to the selected base host Python user site after confirmation."""
    manager = SqlFluffManager(JsonRuntimeStateStore())
    current = manager.status()
    if current.ready:
        typer.echo(json.dumps(current.model_dump(mode="json"), sort_keys=True))
        return
    if not sys.stdin.isatty() or not typer.confirm(
        f"Install sqlfluff=={manager.pinned_version} with this exact host Python using --user?",
        default=False,
    ):
        raise typer.Abort()
    descriptor = manager.ensure(approved=True)
    typer.echo(json.dumps(descriptor.model_dump(mode="json"), sort_keys=True))


@sqlfluff_app.command("update")
def sqlfluff_update(version: Annotated[str, typer.Option("--version")]) -> None:
    """Update/rollback SQLFluff through this same idle host interpreter after confirmation."""
    if not sys.stdin.isatty() or not typer.confirm(
        f"Update SQLFluff to {version!r} through this exact host Python?", default=False
    ):
        raise typer.Abort()
    descriptor = SqlFluffManager(JsonRuntimeStateStore()).update(version, approved=True)
    typer.echo(json.dumps(descriptor.model_dump(mode="json"), sort_keys=True))


@harness_app.command(
    "run", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def harness_run(
    context: typer.Context,
    harness: Annotated[str, typer.Option("--harness", help="codex, claude, or gemini")],
) -> None:
    """Launch an installed harness with agent metadata injected only into its child process."""
    if harness not in {"codex", "claude", "gemini"}:
        raise typer.BadParameter("Supported harnesses are codex, claude, and gemini.")
    executable = shutil.which(harness)
    if executable is None:
        raise SqlCtxError(
            "HARNESS_NOT_INSTALLED",
            f"{harness} is not installed; sqlctx never installs harness CLIs.",
        )
    base_url, token = _connection()
    child_environment = os.environ.copy()
    child_environment["SQLCTX_MCP_URL"] = base_url + "/mcp"
    child_environment["SQLCTX_API_TOKEN"] = token
    result = subprocess.run(  # noqa: S603 - executable comes from a closed harness allowlist.
        [executable, *context.args], env=child_environment, check=False
    )
    raise typer.Exit(code=result.returncode)


def _connection() -> tuple[str, str]:
    state = JsonRuntimeStateStore()
    value = state.read_json("connection-metadata.json")
    if not value:
        raise SqlCtxError(
            "SERVER_METADATA_MISSING", "Start sqlctx-server before using transfer commands."
        )
    return str(value["mcp_url"]).removesuffix("/mcp"), str(value["agent_token"])


def _http_error(response: httpx.Response) -> SqlCtxError:
    try:
        error = response.json()["error"]
        return SqlCtxError(
            str(error["code"]), str(error["message"]), status_code=response.status_code
        )
    except (ValueError, KeyError, TypeError):
        return SqlCtxError(
            "HTTP_TRANSFER_FAILED",
            "The local service returned an invalid transfer response.",
            status_code=response.status_code,
        )


@approvals_app.command("grant")
def grant(
    challenge: Annotated[
        str,
        typer.Option(
            "--challenge", help="Challenge ID printed in the sanitized approval response."
        ),
    ],
) -> None:
    """Grant one exact request from an interactive owner terminal."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise typer.BadParameter("Owner approval requires an interactive local terminal.")
    state = JsonRuntimeStateStore()
    CredentialMetadataStore(state).ensure("http://127.0.0.1:8765/mcp")
    if not typer.confirm(f"Grant the exact operation bound to {challenge}?", default=False):
        raise typer.Abort()
    ApprovalService(state=state).grant(challenge, interactive=True)
    typer.echo("Approval granted for one matching retry.")


@export_app.command("fetch")
def fetch(
    export_id: Annotated[str, typer.Option("--export-id")],
    destination: Annotated[Path, typer.Option("--destination", resolve_path=True)],
) -> None:
    """Fetch through HTTP internally and validate size, bundle hash, manifest hash, and paths."""
    base_url, token = _connection()
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(base_url=base_url, headers=headers, timeout=120.0) as client:
        response = client.get(f"/api/v1/exports/{export_id}")
        if response.status_code != 200:
            raise _http_error(response)
        status = ExportStatus.model_validate(response.json())
        if status.size_bytes is None or status.sha256 is None or status.manifest_sha256 is None:
            raise SqlCtxError(
                "EXPORT_NOT_COMPLETE",
                "Completed integrity metadata is required before bundle transfer.",
            )
        destination.mkdir(parents=True, exist_ok=True)
        target = destination / f"{export_id}.sqlctx.zip"
        with tempfile.NamedTemporaryFile(
            prefix="sqlctx-fetch-", suffix=".zip", dir=destination, delete=False
        ) as handle:
            temporary = Path(handle.name)
            received = 0
            with client.stream("GET", f"/api/v1/exports/{export_id}/bundle") as stream:
                if stream.status_code != 200:
                    raise _http_error(stream)
                for chunk in stream.iter_bytes():
                    received += len(chunk)
                    if received > status.size_bytes:
                        raise SqlCtxError(
                            "BUNDLE_INTEGRITY_FAILED",
                            "Bundle exceeded its declared size while streaming.",
                        )
                    handle.write(chunk)
        try:
            validate_bundle(
                temporary, expected_size=status.size_bytes, expected_sha256=status.sha256
            )
            with zipfile.ZipFile(temporary) as archive:
                manifest = archive.read("manifest.yaml")
            if sha256_bytes(manifest) != status.manifest_sha256:
                raise SqlCtxError(
                    "BUNDLE_INTEGRITY_FAILED", "Bundle manifest hash did not match export status."
                )
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
    typer.echo(str(target))


@export_app.command("assemble")
def assemble(
    bundle: Annotated[
        list[Path], typer.Option("--bundle", exists=True, dir_okay=False, resolve_path=True)
    ],
    output_root: Annotated[Path, typer.Option("--output-root", resolve_path=True)],
    allow_delete_stale: Annotated[
        bool,
        typer.Option(
            "--allow-delete-stale",
            help="Owner-confirmed removal of files managed by the previous manifest.",
        ),
    ] = False,
) -> None:
    """Merge fetched batches and atomically update managed files only."""
    inventory = assemble_bundles(bundle, output_root, allow_delete_stale=allow_delete_stale)
    typer.echo(json.dumps(inventory.model_dump(mode="json", by_alias=True), sort_keys=True))


@validate_app.command("output")
def validate_output(
    root: Annotated[Path, typer.Option("--root", exists=True, file_okay=False, resolve_path=True)],
) -> None:
    """Reopen and hash every managed file without sending the local root path to the server."""
    inventory = inventory_output(root)
    typer.echo(json.dumps(inventory.model_dump(mode="json", by_alias=True), sort_keys=True))


if __name__ == "__main__":
    app()
