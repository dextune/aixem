"""Deterministic Cold-Start Stage Contract 1 builder and validator."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from .change_scope import canonical_json_bytes, sha256_bytes, snapshot_workspace
from .task_contract import TaskContractError, load_and_resolve_task, resolve_task_route

STAGE_SCHEMA = "https://schemas.aixem.org/agent/stage-manifest/1"
STAGE_FORMAT_VERSION = "1.0"
FIXED_TIME = "2026-08-12T00:00:00Z"
EXCLUDED_NAMES = {"render", "evidence", ".aixem-agent", "__pycache__", ".pytest_cache", ".git"}
LEAKAGE_NAMES = {"evaluator", "invariants.json", "oracle", "solution", "golden-answer", "prior-attempts"}


class StageContractError(RuntimeError):
    """The stage cannot prove freshness, isolation, or target non-disclosure."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def _safe_copy_tree(source: Path, destination: Path, *, excludes: Iterable[str] = EXCLUDED_NAMES) -> None:
    source = source.resolve()
    if not source.is_dir():
        raise StageContractError(f"copy source is not a directory: {source}")
    excluded = set(excludes)
    destination.mkdir(parents=True, exist_ok=True)
    for current, dirnames, filenames in os.walk(source, topdown=True, followlinks=False):
        current_path = Path(current)
        relative = current_path.relative_to(source)
        kept: list[str] = []
        for dirname in sorted(dirnames):
            path = current_path / dirname
            if dirname in excluded:
                continue
            if path.is_symlink():
                raise StageContractError(f"symlink is prohibited in stage source: {(relative / dirname).as_posix()}")
            kept.append(dirname)
        dirnames[:] = kept
        target_dir = destination / relative
        target_dir.mkdir(parents=True, exist_ok=True)
        for filename in sorted(filenames):
            path = current_path / filename
            if path.is_symlink():
                raise StageContractError(f"symlink is prohibited in stage source: {(relative / filename).as_posix()}")
            shutil.copy2(path, target_dir / filename)


def _file_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not root.exists():
        return records
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise StageContractError(f"symlink is prohibited in a cold-start stage: {path}")
        if path.is_file():
            records.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "digest": sha256_file(path),
            })
    return records


def _copy_file(repository_root: Path, relative: str, reference_root: Path, copied: set[str]) -> None:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise StageContractError(f"unsafe reference path {relative!r}")
    source = repository_root / pure
    if not source.is_file():
        raise StageContractError(f"reference-pack source is missing: {relative}")
    target = reference_root / pure
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    copied.add(pure.as_posix())


def compile_reference_pack(repository_root: Path, task: Mapping[str, Any], route_resolution: Mapping[str, Any], output: Path) -> dict[str, Any]:
    """Compile a bounded pack without validation corpora, answers, or attempt data."""
    copied: set[str] = set()
    for relative in ("AGENTS.md", "VERSION", "START_HERE.md"):
        _copy_file(repository_root, relative, output, copied)
    for relative in (
        "docs/_meta/generated/route-index.json",
        route_resolution["entryTaskPacket"],
        route_resolution["activeTaskPacket"],
    ):
        _copy_file(repository_root, str(relative), output, copied)

    packet_paths = {str(route_resolution["entryTaskPacket"]), str(route_resolution["activeTaskPacket"])}
    for packet_relative in sorted(packet_paths):
        packet = read_json(repository_root / packet_relative)
        for document in packet.get("documents", []):
            _copy_file(repository_root, str(document["path"]), output, copied)
        for stage in packet.get("stages", []):
            child = repository_root / "docs" / "_meta" / "generated" / "task-packets" / f"{stage['route']}.json"
            if child.is_file():
                _copy_file(repository_root, child.relative_to(repository_root).as_posix(), output, copied)

    # Validation and authoring tools require immutable schemas and profiles, but
    # no corpus, completed example, release evidence, or evaluator data.
    for tree in (
        "docs/specifications/schemas",
        "profiles",
        "implementation/agent",
        "implementation/schematic",
    ):
        source = repository_root / tree
        destination = output / tree
        _safe_copy_tree(source, destination, excludes={"__pycache__", ".pytest_cache", ".git"})
        copied.update(path.relative_to(output).as_posix() for path in destination.rglob("*") if path.is_file())
    for relative in (
        "tools/agent_authoring.py",
        "tools/live_agent_authoring.py",
        "tools/docs/query_route.py",
    ):
        if (repository_root / relative).is_file():
            _copy_file(repository_root, relative, output, copied)

    records = _file_records(output)
    digest = sha256_bytes(canonical_json_bytes(records))
    return {
        "schema": "https://schemas.aixem.org/agent/reference-pack/1",
        "formatVersion": "1.0",
        "taskId": task["id"],
        "entryRoute": route_resolution["entryRoute"],
        "activeRoute": route_resolution["activeRoute"],
        "files": len(records),
        "bytes": sum(item["bytes"] for item in records),
        "digest": digest,
        "visibleFiles": records,
        "excluded": [
            "validation/**", "examples/**", "release/**", "site/**",
            "executor credentials", "prior attempts", "completed target solutions",
        ],
        "authority": "derived-reference-only",
    }


def _leakage_scan(stage: Path, forbidden_digests: Iterable[str] = ()) -> dict[str, Any]:
    matches: list[dict[str, str]] = []
    forbidden = set(forbidden_digests)
    scanned = 0
    for path in sorted(stage.rglob("*")):
        if not path.is_file() or path.name == "stage-manifest.json":
            continue
        scanned += 1
        rel = path.relative_to(stage).as_posix()
        lowered = {part.lower() for part in PurePosixPath(rel).parts}
        if lowered.intersection(LEAKAGE_NAMES):
            matches.append({"path": rel, "reason": "prohibited evaluator/oracle path"})
        digest = sha256_file(path)
        if digest in forbidden:
            matches.append({"path": rel, "reason": "forbidden completed-target digest"})
    return {"valid": not matches, "filesScanned": scanned, "matches": matches}


def build_stage(
    repository_root: Path,
    case_root: Path,
    attempt_id: str,
    output: Path,
    *,
    generated_at: str = FIXED_TIME,
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    case_root = case_root.resolve()
    task_path = case_root / "agent-task.json"
    start = case_root / "start"
    if not task_path.is_file() or not start.is_dir():
        raise StageContractError("case must contain agent-task.json and start/")
    task, resolution = load_and_resolve_task(task_path, repository_root)
    if output.exists():
        if any(output.iterdir()):
            raise StageContractError(f"fresh attempt destination is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    task_root = output / "task"
    reference_root = output / "reference"
    workspace_root = output / "workspace"
    state_root = output / "state"
    task_root.mkdir(); reference_root.mkdir(); workspace_root.mkdir(); state_root.mkdir()
    shutil.copy2(task_path, task_root / "agent-task.json")
    task_md = case_root / "TASK.md"
    if task_md.is_file():
        shutil.copy2(task_md, task_root / "TASK.md")
    else:
        (task_root / "TASK.md").write_text(str(task["prompt"]).rstrip() + "\n", encoding="utf-8")
    _safe_copy_tree(start, workspace_root)
    reference_pack = compile_reference_pack(repository_root, task, resolution, reference_root)
    workspace_snapshot = snapshot_workspace(workspace_root)
    case_metadata = read_json(case_root / "case.json") if (case_root / "case.json").is_file() else {}
    leakage = _leakage_scan(output, case_metadata.get("forbiddenCompletedDigests", []))
    if not leakage["valid"]:
        raise StageContractError("target leakage detected: " + json.dumps(leakage["matches"], sort_keys=True))

    visible_records = []
    for root_name in ("task", "reference", "workspace"):
        for record in _file_records(output / root_name):
            visible_records.append({**record, "path": f"{root_name}/{record['path']}"})
    visible_records.sort(key=lambda item: item["path"])
    start_authoritative = [
        {key: value for key, value in record.items() if key != "json"}
        for _path, record in sorted(workspace_snapshot["files"].items())
        if record["role"] == "authoritative"
    ]
    manifest: dict[str, Any] = {
        "schema": STAGE_SCHEMA,
        "formatVersion": STAGE_FORMAT_VERSION,
        "caseId": task["id"],
        "attemptId": attempt_id,
        "generatedAt": generated_at,
        "task": {
            "path": "task/agent-task.json",
            "digest": resolution["taskDigest"],
            "entryRoute": resolution["entryRoute"],
            "activeRoute": resolution["activeRoute"],
            "routeResolutionDigest": resolution["resolutionDigest"],
        },
        "referencePack": {
            "root": "reference",
            "digest": reference_pack["digest"],
            "files": reference_pack["files"],
            "bytes": reference_pack["bytes"],
        },
        "startWorkspace": {
            "root": "workspace",
            "snapshotDigest": workspace_snapshot["digest"],
            "authoritativeDigest": workspace_snapshot["authoritativeDigest"],
            "files": workspace_snapshot["fileCount"],
            "authoritativeFiles": start_authoritative,
        },
        "visibleFiles": visible_records,
        "writableRoots": ["workspace", "state"],
        "readOnlyRoots": ["task", "reference"],
        "effectiveWriteScope": resolution["effectiveWriteScope"],
        "excludedEvaluatorArtifacts": [
            "evaluator/invariants.json", "case secrets", "scoring metadata",
            "prior attempts", "Tier A repaired fixtures", "completed target render",
        ],
        "isolationProfile": {
            "filesystem": "fresh-copy",
            "freshState": True,
            "priorAttemptsVisible": False,
            "evaluatorArtifactsVisible": False,
            "credentialsStaged": False,
            "networkPolicy": "declared-by-executor",
        },
        "targetLeakageCheck": leakage,
        "createdBy": {"tool": "implementation.agent.cold_start_stage", "version": "1.0"},
        "authority": "derived-execution-only",
    }
    manifest["stageDigest"] = sha256_bytes(canonical_json_bytes(manifest))
    write_json(output / "stage-manifest.json", manifest)
    return manifest


def validate_stage(stage: Path, repository_root: Path) -> dict[str, Any]:
    stage = stage.resolve()
    errors: list[str] = []
    manifest_path = stage / "stage-manifest.json"
    if not manifest_path.is_file():
        return {"valid": False, "errors": ["stage-manifest.json is missing"]}
    try:
        manifest = read_json(manifest_path)
        schema_file = repository_root / "docs" / "specifications" / "schemas" / "agent" / "aixem-agent-stage-manifest-1.schema.json"
        validator = Draft202012Validator(read_json(schema_file), format_checker=FormatChecker())
        for issue in validator.iter_errors(manifest):
            errors.append("/" + "/".join(str(part) for part in issue.absolute_path) + ": " + issue.message)
    except (OSError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": [f"invalid stage manifest: {exc}"]}

    for root in ("task", "reference", "workspace", "state"):
        if not (stage / root).is_dir():
            errors.append(f"missing stage root {root}")
    if (stage / "state").is_dir() and any((stage / "state").iterdir()):
        errors.append("fresh stage state/ is not empty")
    leakage = _leakage_scan(stage)
    errors.extend(f"target leakage: {item['path']} ({item['reason']})" for item in leakage["matches"])
    try:
        task, resolution = load_and_resolve_task(stage / "task" / "agent-task.json", repository_root)
        if resolution["taskDigest"] != manifest.get("task", {}).get("digest"):
            errors.append("task digest mismatch")
        if resolution["resolutionDigest"] != manifest.get("task", {}).get("routeResolutionDigest"):
            errors.append("route resolution digest mismatch")
        if resolution["effectiveWriteScope"] != manifest.get("effectiveWriteScope"):
            errors.append("effective write scope mismatch")
    except (TaskContractError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"task contract invalid: {exc}")

    workspace = snapshot_workspace(stage / "workspace") if (stage / "workspace").is_dir() else None
    if workspace:
        if workspace["digest"] != manifest.get("startWorkspace", {}).get("snapshotDigest"):
            errors.append("start workspace snapshot digest mismatch")
        if workspace["authoritativeDigest"] != manifest.get("startWorkspace", {}).get("authoritativeDigest"):
            errors.append("start workspace authoritative digest mismatch")
    reference_records = _file_records(stage / "reference") if (stage / "reference").is_dir() else []
    reference_digest = sha256_bytes(canonical_json_bytes(reference_records))
    if reference_digest != manifest.get("referencePack", {}).get("digest"):
        errors.append("reference pack digest mismatch")
    expected_digest = dict(manifest)
    observed_stage_digest = expected_digest.pop("stageDigest", None)
    if sha256_bytes(canonical_json_bytes(expected_digest)) != observed_stage_digest:
        errors.append("stage manifest self-digest mismatch")
    return {
        "valid": not errors,
        "caseId": manifest.get("caseId"),
        "attemptId": manifest.get("attemptId"),
        "stageDigest": manifest.get("stageDigest"),
        "files": len(manifest.get("visibleFiles", [])),
        "targetLeakage": leakage,
        "errors": errors,
    }


def _immutable_tree_snapshot(root: Path) -> dict[str, Any]:
    """Create a deterministic file/symlink snapshot for an immutable stage root."""
    files: list[dict[str, Any]] = []
    symlinks: list[str] = []
    if not root.exists():
        return {"exists": False, "files": [], "symlinks": [], "digest": sha256_bytes(canonical_json_bytes([]))}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            symlinks.append(relative)
        elif path.is_file():
            files.append({"path": relative, "bytes": path.stat().st_size, "digest": sha256_file(path)})
    value = {"exists": True, "files": files, "symlinks": symlinks}
    value["digest"] = sha256_bytes(canonical_json_bytes(value))
    return value


def capture_immutable_stage(stage: Path) -> dict[str, Any]:
    """Capture executor-immutable task, reference, and manifest inputs."""
    stage = stage.resolve()
    manifest = stage / "stage-manifest.json"
    if manifest.is_symlink():
        manifest_record: dict[str, Any] = {"exists": True, "symlink": True, "digest": None}
    elif manifest.is_file():
        manifest_record = {"exists": True, "symlink": False, "bytes": manifest.stat().st_size, "digest": sha256_file(manifest)}
    else:
        manifest_record = {"exists": False, "symlink": False, "digest": None}
    payload = {
        "task": _immutable_tree_snapshot(stage / "task"),
        "reference": _immutable_tree_snapshot(stage / "reference"),
        "stageManifest": manifest_record,
    }
    payload["digest"] = sha256_bytes(canonical_json_bytes(payload))
    return payload


def verify_immutable_stage(stage: Path, baseline: Mapping[str, Any]) -> dict[str, Any]:
    """Verify that an executor did not alter declared read-only stage inputs."""
    observed = capture_immutable_stage(stage)
    errors: list[str] = []
    for root_name in ("task", "reference"):
        before = baseline.get(root_name, {})
        after = observed.get(root_name, {})
        if after.get("symlinks"):
            errors.append(f"{root_name} contains executor-introduced symlink(s): {', '.join(after['symlinks'])}")
        if before.get("digest") != after.get("digest"):
            before_files = {item["path"]: item for item in before.get("files", [])}
            after_files = {item["path"]: item for item in after.get("files", [])}
            for path in sorted(before_files.keys() - after_files.keys()):
                errors.append(f"immutable {root_name} file deleted: {path}")
            for path in sorted(after_files.keys() - before_files.keys()):
                errors.append(f"immutable {root_name} file added: {path}")
            for path in sorted(before_files.keys() & after_files.keys()):
                if before_files[path].get("digest") != after_files[path].get("digest"):
                    errors.append(f"immutable {root_name} file modified: {path}")
    before_manifest = baseline.get("stageManifest", {})
    after_manifest = observed.get("stageManifest", {})
    if after_manifest.get("symlink"):
        errors.append("stage-manifest.json became a symlink")
    if before_manifest.get("digest") != after_manifest.get("digest"):
        if not after_manifest.get("exists"):
            errors.append("stage-manifest.json was deleted")
        else:
            errors.append("stage-manifest.json was modified or replaced")
    return {
        "valid": not errors,
        "baselineDigest": baseline.get("digest"),
        "observedDigest": observed.get("digest"),
        "errors": errors,
        "immutableRoots": ["task", "reference", "stage-manifest.json"],
        "authority": "postflight-integrity-only",
    }
