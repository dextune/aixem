#!/usr/bin/env python3
"""Run the AIXEM 0.5.6 prepare -> check -> close authoring contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.change_scope import (  # noqa: E402
    UnsafeWorkspaceError,
    build_change_set,
    scope_summary,
    snapshot_workspace,
)
from agent.diagnostics import (  # noqa: E402
    assign_diagnostic_ids,
    diagnostic_state_digest,
    make_diagnostic,
    normalize_issue,
)
from agent.run_record import (  # noqa: E402
    FIXED_TIME,
    build_run_record,
    canonical_json,
    detect_loop_state,
    make_iteration_record,
)
from agent.validator_adapter import render_workspace, validate_workspace  # noqa: E402

VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RELEASE_ID = f"AIXEM-SRP-{VERSION}-2026-08-12"
PACKET_DIR = ROOT / "docs" / "_meta" / "generated" / "task-packets"
STATE_SCHEMA = "https://schemas.aixem.org/agent/execution-state/1"


class AuthoringCommandError(RuntimeError):
    """The execution contract cannot proceed safely."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value), encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def _safe_relative(path: Path, root: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(root.resolve()).as_posix()


def _state_dir(workspace: Path, task_id: str, explicit: Path | None) -> Path:
    if explicit is None:
        return workspace / ".aixem-agent" / task_id
    return explicit.resolve()


def _packet(route: str) -> tuple[Path, dict[str, Any]]:
    path = PACKET_DIR / f"{route}.json"
    if not path.is_file():
        raise AuthoringCommandError(f"task packet is missing for route {route!r}; run tools/docs/build_routes.py")
    return path, read_json(path)


def _resolve_packets(entry_route: str, stage_route: str | None) -> tuple[dict[str, Any], dict[str, Any], str, list[str], str]:
    entry_path, entry = _packet(entry_route)
    if entry.get("kind") == "composite":
        stage_ids = [str(item["route"]) for item in entry.get("stages", [])]
        if not stage_route:
            raise AuthoringCommandError(
                f"composite route {entry_route!r} requires --stage-route; allowed stages: {', '.join(stage_ids)}"
            )
        if stage_route not in stage_ids:
            raise AuthoringCommandError(f"stage route {stage_route!r} is not a child of {entry_route!r}")
        active_path, active = _packet(stage_route)
        chain = [entry_route, stage_route]
        active_route = stage_route
        digest = sha256_file(active_path)
    else:
        if stage_route and stage_route != entry_route:
            raise AuthoringCommandError("--stage-route is only valid for a composite entry route")
        active = entry
        chain = [entry_route]
        active_route = entry_route
        digest = sha256_file(entry_path)
    if "writes" not in active:
        raise AuthoringCommandError(f"task packet {active_route!r} has no current write-scope metadata")
    return entry, active, active_route, chain, digest


def _project_arg(workspace: Path, value: str | None) -> Path | None:
    if not value:
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        raise AuthoringCommandError(f"unsafe project path: {value!r}")
    path = (workspace / pure).resolve()
    path.relative_to(workspace.resolve())
    return path


def _load_state(path: Path) -> dict[str, Any]:
    state_file = path / "state.json"
    if not state_file.is_file():
        raise AuthoringCommandError(f"authoring state does not exist: {state_file}")
    state = read_json(state_file)
    if state.get("schema") != STATE_SCHEMA:
        raise AuthoringCommandError("unsupported authoring state schema")
    return state


def _save_state(path: Path, state: Mapping[str, Any]) -> None:
    write_json(path / "state.json", state)


def prepare(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    workspace = args.workspace.resolve()
    state_dir = _state_dir(workspace, args.task_id, args.state_dir)
    entry, active, active_route, route_chain, packet_digest = _resolve_packets(args.route, args.stage_route)
    project = _project_arg(workspace, args.project)
    try:
        baseline = snapshot_workspace(workspace)
    except UnsafeWorkspaceError as exc:
        diagnostic = make_diagnostic(
            "AIXEM-DIAG-AGENT-PATH-UNSAFE", str(exc), artifact=".", evidence={"phase": "prepare"}
        ).to_dict()
        return 2, {"valid": False, "status": "BLOCKED", "diagnostics": [{**diagnostic, "id": "diag-0001"}]}
    validation = validate_workspace(workspace, active_route, project=project, validators=active.get("validators", []))
    execution_packet = {
        "schema": "https://schemas.aixem.org/agent/execution-packet/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "taskId": args.task_id,
        "entryRoute": args.route,
        "activeRoute": active_route,
        "routeChain": route_chain,
        "taskPacket": f"docs/_meta/generated/task-packets/{active_route}.json",
        "taskPacketDigest": packet_digest,
        "allowedWrites": scope_summary(active["writes"]),
        "requiredValidators": active.get("validators", []),
        "stageExitConditions": active.get("completion", []),
        "prohibitedGeneratedOutputEdits": active["writes"].get("prohibited", []),
        "baseline": {
            "snapshotDigest": baseline["digest"],
            "authoritativeDigest": baseline["authoritativeDigest"],
            "fileCount": baseline["fileCount"],
            "authoritativeFileCount": baseline["authoritativeFileCount"],
        },
        "initialDiagnostics": validation["diagnostics"],
        "authority": "derived-execution-only",
    }
    state = {
        "schema": STATE_SCHEMA,
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "taskId": args.task_id,
        "workspace": str(workspace),
        "project": _safe_relative(project, workspace) if project else None,
        "entryRoute": args.route,
        "activeRoute": active_route,
        "routeChain": route_chain,
        "taskPacketDigest": packet_digest,
        "writeScope": scope_summary(active["writes"]),
        "validators": active.get("validators", []),
        "baselineSnapshot": baseline,
        "lastSnapshot": baseline,
        "lastDiagnostics": validation["diagnostics"],
        "iterations": [],
        "status": "PREPARED",
    }
    state_dir.mkdir(parents=True, exist_ok=True)
    _save_state(state_dir, state)
    write_json(state_dir / "prepare.json", execution_packet)
    result = {
        "valid": True,
        "status": "PREPARED",
        "stateDirectory": str(state_dir),
        "executionPacket": execution_packet,
        "initialValidation": validation,
    }
    return 0, result


def _scope_diagnostics(change_set: Mapping[str, Any]) -> list[Any]:
    diagnostics = []
    generated_paths = {item["path"] for item in change_set.get("generatedOutputEdits", [])}
    for violation in change_set.get("scopeViolations", []):
        code = (
            "AIXEM-DIAG-AGENT-GENERATED-OUTPUT-EDIT"
            if violation.get("path") in generated_paths or violation.get("kind") == "generated-output-edit"
            else "AIXEM-DIAG-AGENT-SCOPE-VIOLATION"
        )
        diagnostics.append(make_diagnostic(
            code,
            str(violation.get("message", "route scope violation")),
            artifact=str(violation.get("path", ".")),
            evidence={"violationKind": violation.get("kind"), "route": change_set.get("route")},
        ))
    return diagnostics


def _perform_check(state_dir: Path, state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    workspace = Path(state["workspace"]).resolve()
    project = _project_arg(workspace, state.get("project"))
    current = snapshot_workspace(workspace)
    iteration_number = len(state.get("iterations", [])) + 1
    change_set = build_change_set(
        state["lastSnapshot"],
        current,
        route=state["activeRoute"],
        scope=state["writeScope"],
        iteration=iteration_number,
        required_validators=state.get("validators", []),
    )
    validation = validate_workspace(
        workspace,
        state["activeRoute"],
        project=project,
        validators=state.get("validators", []),
    )
    diagnostics = [
        normalize_issue(item, artifact=item.get("artifact"), workspace_root=workspace)
        for item in validation["diagnostics"]
    ]
    diagnostics.extend(_scope_diagnostics(change_set))
    normalized = assign_diagnostic_ids(diagnostics)
    diagnostic_dicts = [item.to_dict() for item in normalized]
    iteration = make_iteration_record(
        iteration=iteration_number,
        route=state["activeRoute"],
        stage="VALIDATED" if not any(item["severity"] == "error" for item in diagnostic_dicts) else "DIAGNOSED",
        diagnostics_before=state.get("lastDiagnostics", []),
        change_set=change_set,
        diagnostics_after=diagnostic_dicts,
        validators=state.get("validators", []),
    )
    iterations = [*state.get("iterations", []), iteration]
    loop = detect_loop_state(iterations)
    if loop["stalled"] or loop["oscillating"]:
        loop_code = "AIXEM-DIAG-AGENT-OSCILLATING-LOOP" if loop["oscillating"] else "AIXEM-DIAG-AGENT-STALLED-LOOP"
        loop_diag = make_diagnostic(
            loop_code,
            "The authoring repair loop did not improve the blocking state.",
            artifact=".",
            evidence={"iteration": iteration_number, "stateDigest": loop.get("stateDigest")},
        )
        normalized = assign_diagnostic_ids([*normalized, loop_diag])
        diagnostic_dicts = [item.to_dict() for item in normalized]
        iteration["diagnosticsAfter"] = diagnostic_dicts
        iteration["diagnosticStateAfter"] = diagnostic_state_digest(diagnostic_dicts)
        iteration["blockingAfter"] = sum(item.get("severity") == "error" for item in diagnostic_dicts)
        iterations[-1] = iteration
    blocked = any(item.get("severity") == "error" for item in diagnostic_dicts)
    check_result = {
        "schema": "https://schemas.aixem.org/agent/check-result/1",
        "formatVersion": "1.0",
        "release": state["release"],
        "generatedAt": FIXED_TIME,
        "taskId": state["taskId"],
        "entryRoute": state["entryRoute"],
        "activeRoute": state["activeRoute"],
        "iteration": iteration_number,
        "changeSet": change_set,
        "diagnostics": diagnostic_dicts,
        "nextRemediationRoutes": sorted({item["remediationRoute"] for item in diagnostic_dicts if item["severity"] == "error"}),
        "loopState": detect_loop_state(iterations),
        "valid": not blocked,
        "status": "VALIDATED" if not blocked else "BLOCKED",
    }
    state.update({
        "lastSnapshot": current,
        "lastDiagnostics": diagnostic_dicts,
        "iterations": iterations,
        "status": check_result["status"],
    })
    write_json(state_dir / f"change-set-{iteration_number:04d}.json", change_set)
    write_json(state_dir / f"check-{iteration_number:04d}.json", check_result)
    _save_state(state_dir, state)
    return check_result, state


def check(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    state = _load_state(args.state_dir.resolve())
    try:
        result, _state = _perform_check(args.state_dir.resolve(), state)
    except UnsafeWorkspaceError as exc:
        diagnostic = make_diagnostic(
            "AIXEM-DIAG-AGENT-PATH-UNSAFE", str(exc), artifact=".", evidence={"phase": "check"}
        ).to_dict()
        result = {"valid": False, "status": "BLOCKED", "diagnostics": [{**diagnostic, "id": "diag-0001"}]}
    return (0 if result.get("valid") else 2), result


def close(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    state_dir = args.state_dir.resolve()
    state = _load_state(state_dir)
    workspace = Path(state["workspace"]).resolve()
    project = _project_arg(workspace, state.get("project"))
    current = snapshot_workspace(workspace)
    if current["digest"] != state["lastSnapshot"]["digest"]:
        check_result, state = _perform_check(state_dir, state)
        if not check_result["valid"]:
            return 2, {"valid": False, "status": "BLOCKED", "check": check_result}

    full_validation = validate_workspace(workspace, "validate-project", project=project)
    final_diagnostics = list(full_validation["diagnostics"])
    if any(item.get("severity") == "error" for item in final_diagnostics):
        determinism = {"valid": False, "repeatCount": 0, "projectRuns": 0, "changed": []}
        render_artifacts: dict[str, str] = {}
    else:
        rendered = render_workspace(workspace, project=project, repeat_count=3)
        final_diagnostics = assign_diagnostic_ids([
            *[normalize_issue(item, artifact=item.get("artifact"), workspace_root=workspace) for item in final_diagnostics],
            *[normalize_issue(item, artifact=item.get("artifact"), workspace_root=workspace) for item in rendered["diagnostics"]],
        ])
        final_diagnostics = [item.to_dict() for item in final_diagnostics]
        determinism = rendered["determinism"]
        render_artifacts = rendered["artifacts"]

    final_snapshot = snapshot_workspace(workspace)
    record = build_run_record(
        release=state["release"],
        task_id=state["taskId"],
        entry_route=state["entryRoute"],
        active_route=state["activeRoute"],
        task_packet_digest=state["taskPacketDigest"],
        baseline_snapshot=state["baselineSnapshot"],
        final_snapshot=final_snapshot,
        route_chain=state["routeChain"],
        iterations=state.get("iterations", []),
        final_diagnostics=final_diagnostics,
        render_artifacts=render_artifacts,
        determinism=determinism,
    )
    write_json(state_dir / "authoring-run-record.json", record)
    state.update({"status": record["final"]["status"], "finalRecordDigest": record["recordDigest"]})
    _save_state(state_dir, state)
    result = {
        "valid": bool(record["final"]["conformant"]),
        "status": record["final"]["status"],
        "runRecord": str(state_dir / "authoring-run-record.json"),
        "recordDigest": record["recordDigest"],
        "summary": {
            "iterations": len(record["iterations"]),
            "blockingDiagnostics": record["final"]["blockingDiagnosticCount"],
            "scopeViolations": record["final"]["scopeViolationCount"],
            "generatedOutputEdits": record["final"]["generatedOutputEditCount"],
            "determinism": record["final"]["determinism"],
        },
    }
    return (0 if result["valid"] else 2), result


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)

    prepare_parser = sub.add_parser("prepare", help="resolve route scope and snapshot the staged workspace")
    prepare_parser.add_argument("--workspace", type=Path, required=True)
    prepare_parser.add_argument("--route", required=True)
    prepare_parser.add_argument("--stage-route")
    prepare_parser.add_argument("--task-id", required=True)
    prepare_parser.add_argument("--project", help="workspace-relative project manifest")
    prepare_parser.add_argument("--state-dir", type=Path)
    prepare_parser.set_defaults(handler=prepare)

    check_parser = sub.add_parser("check", help="diff the agent edit and return normalized diagnostics")
    check_parser.add_argument("--state-dir", type=Path, required=True)
    check_parser.set_defaults(handler=check)

    close_parser = sub.add_parser("close", help="run full validation, three renders, and emit the run record")
    close_parser.add_argument("--state-dir", type=Path, required=True)
    close_parser.set_defaults(handler=close)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        code, payload = args.handler(args)
    except (AuthoringCommandError, UnsafeWorkspaceError, FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        payload = {"valid": False, "status": "ERROR", "error": str(exc)}
        code = 2
    print(canonical_json(payload), end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
