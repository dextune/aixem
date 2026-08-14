"""Deterministic evaluator-only predicates for cold-start live attempts."""
from __future__ import annotations

import fnmatch
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Callable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMATIC = REPOSITORY_ROOT / "implementation" / "schematic"
if str(SCHEMATIC) not in sys.path:
    sys.path.insert(0, str(SCHEMATIC))

from component_core import parse_aixem  # type: ignore  # noqa: E402

from .change_scope import canonical_json_bytes, sha256_bytes, snapshot_workspace
from .validator_adapter import render_workspace, validate_workspace

INVARIANT_SCHEMA = "https://schemas.aixem.org/agent/evaluation-invariant/1"
RESULT_SCHEMA = "https://schemas.aixem.org/agent/evaluation-result/1"
PREDICATES = {
    "validator-pass",
    "diagnostic-absent",
    "artifact-present",
    "authority-digest-unchanged",
    "symbol-port-set",
    "entity-present",
    "local-net-members",
    "project-net-members",
    "interface-binding",
    "render-deterministic",
}
PROHIBITED_ARGUMENT_KEYS = {
    "exactSource", "sourceEquality", "expectedSource", "goldenSource", "completedSolution",
    "oracleFile", "sourceDigestEquality", "byteEquality",
}


class InvariantError(RuntimeError):
    """The invariant manifest is invalid or attempts to encode a hidden answer."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_path(value: str) -> str:
    pure = PurePosixPath(value)
    if not value or pure.is_absolute() or ".." in pure.parts or (pure.parts and ":" in pure.parts[0]):
        raise InvariantError(f"unsafe evaluator path {value!r}")
    return pure.as_posix()


def _matches(path: str, pattern: str) -> bool:
    path = PurePosixPath(path).as_posix()
    pattern = PurePosixPath(pattern).as_posix()
    return fnmatch.fnmatchcase(path, pattern) or (pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:]))


def validate_invariant_manifest(manifest: Mapping[str, Any], schema_file: Path) -> dict[str, Any]:
    validator = Draft202012Validator(read_json(schema_file), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(manifest), key=lambda item: list(item.absolute_path))
    rendered: list[str] = []
    for issue in errors:
        rendered.append("/" + "/".join(str(part) for part in issue.absolute_path) + ": " + issue.message)
    for invariant in manifest.get("invariants", []):
        if invariant.get("predicate") not in PREDICATES:
            rendered.append(f"{invariant.get('id')}: unsupported predicate {invariant.get('predicate')!r}")
        arguments = invariant.get("arguments", {})
        prohibited = sorted(set(arguments) & PROHIBITED_ARGUMENT_KEYS)
        if prohibited:
            rendered.append(f"{invariant.get('id')}: hidden exact-source equality is prohibited: {prohibited}")
    if rendered:
        raise InvariantError("invalid Evaluation Invariant Contract 1 manifest: " + "; ".join(rendered[:30]))
    return dict(manifest)


def _one_path(workspace: Path, value: str) -> Path:
    value = _safe_path(value)
    matches = sorted(workspace.glob(value)) if any(char in value for char in "*?[") else [workspace / value]
    files = [path for path in matches if path.is_file()]
    if len(files) != 1:
        raise InvariantError(f"expected one file for {value!r}, observed {len(files)}")
    resolved = files[0].resolve()
    resolved.relative_to(workspace.resolve())
    return resolved


def _project_path(workspace: Path, arguments: Mapping[str, Any]) -> Path | None:
    value = arguments.get("project")
    if value:
        return _one_path(workspace, str(value))
    direct = sorted(workspace.glob("*.aixproj.json"))
    if len(direct) == 1:
        return direct[0]
    return None


def _canonical_member(member: Any) -> str:
    if isinstance(member, Mapping):
        return f"{member.get('sheet')}@{member.get('port')}"
    return str(member)


def _validation(workspace: Path, arguments: Mapping[str, Any], cache: dict[str, Any]) -> dict[str, Any]:
    route = str(arguments.get("route", "validate-project"))
    project = _project_path(workspace, arguments)
    key = f"{route}|{project}"
    if key not in cache:
        cache[key] = validate_workspace(workspace, route, project=project)
    return cache[key]


def _predicate_validator_pass(workspace: Path, arguments: Mapping[str, Any], context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    result = _validation(workspace, arguments, context["validationCache"])
    blocking = [item for item in result.get("diagnostics", []) if item.get("severity") == "error"]
    return not blocking, {"blockingDiagnostics": [item.get("code") for item in blocking], "diagnostics": len(result.get("diagnostics", []))}


def _predicate_diagnostic_absent(workspace: Path, arguments: Mapping[str, Any], context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    code = str(arguments["code"])
    result = _validation(workspace, arguments, context["validationCache"])
    observed = [item for item in result.get("diagnostics", []) if item.get("code") == code]
    return not observed, {"code": code, "observed": len(observed)}


def _predicate_artifact_present(workspace: Path, arguments: Mapping[str, Any], _context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    pattern = _safe_path(str(arguments["path"]))
    matches = sorted(path.relative_to(workspace).as_posix() for path in workspace.glob(pattern) if path.is_file())
    minimum = int(arguments.get("minimum", 1))
    return len(matches) >= minimum, {"pattern": pattern, "minimum": minimum, "matches": matches}


def _predicate_authority_digest_unchanged(workspace: Path, arguments: Mapping[str, Any], context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    baseline = {
        str(item["path"]): item
        for item in context["stageManifest"].get("startWorkspace", {}).get("authoritativeFiles", [])
    }
    current = snapshot_workspace(workspace)["files"]
    authorities = set(map(str, arguments.get("authorities", []) or []))
    patterns = [_safe_path(str(value)) for value in arguments.get("paths", []) or []]
    selected = {
        path: item for path, item in baseline.items()
        if (not authorities or item.get("authority") in authorities)
        and (not patterns or any(_matches(path, pattern) for pattern in patterns))
    }
    changed = []
    for path, before in sorted(selected.items()):
        after = current.get(path)
        if not after or after.get("digest") != before.get("digest"):
            changed.append(path)
    additions = []
    if authorities:
        for path, item in current.items():
            if item.get("role") == "authoritative" and item.get("authority") in authorities and path not in baseline:
                if not patterns or any(_matches(path, pattern) for pattern in patterns):
                    additions.append(path)
    valid = bool(selected) and not changed and not additions
    return valid, {"selected": len(selected), "changed": changed, "added": additions}


def _predicate_symbol_port_set(workspace: Path, arguments: Mapping[str, Any], _context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    path = _one_path(workspace, str(arguments["path"]))
    symbol = read_json(path).get("symbol", {})
    observed = sorted(str(port.get("id")) for port in symbol.get("ports", []))
    expected = sorted(map(str, arguments["ports"]))
    mode = str(arguments.get("mode", "exact"))
    valid = observed == expected if mode == "exact" else set(expected).issubset(observed)
    return valid, {"path": path.relative_to(workspace).as_posix(), "mode": mode, "expected": expected, "observed": observed}


def _predicate_entity_present(workspace: Path, arguments: Mapping[str, Any], _context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    path = _one_path(workspace, str(arguments["source"]))
    source = parse_aixem(path)
    entity = str(arguments["entity"])
    observed = source.get("entities", {}).get(entity)
    expected_type = arguments.get("componentType")
    valid = observed is not None and (expected_type is None or observed.get("attributes", {}).get("type") == expected_type)
    return valid, {"source": path.relative_to(workspace).as_posix(), "entity": entity, "observed": observed}


def _predicate_local_net_members(workspace: Path, arguments: Mapping[str, Any], _context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    path = _one_path(workspace, str(arguments["source"]))
    source = parse_aixem(path)
    net = str(arguments["net"])
    observed = sorted(map(str, source.get("nets", {}).get(net, [])))
    expected = sorted(map(str, arguments["members"]))
    mode = str(arguments.get("mode", "exact"))
    valid = observed == expected if mode == "exact" else set(expected).issubset(observed)
    return valid, {"source": path.relative_to(workspace).as_posix(), "net": net, "mode": mode, "expected": expected, "observed": observed}


def _predicate_project_net_members(workspace: Path, arguments: Mapping[str, Any], _context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    path = _one_path(workspace, str(arguments["project"]))
    project = read_json(path).get("project", {})
    net_id = str(arguments["net"])
    net = next((item for item in project.get("projectNets", []) if str(item.get("id")) == net_id), None)
    observed = sorted(_canonical_member(item) for item in (net or {}).get("members", []))
    expected = sorted(_canonical_member(item) for item in arguments["members"])
    mode = str(arguments.get("mode", "exact"))
    valid = observed == expected if mode == "exact" else set(expected).issubset(observed)
    return valid, {"project": path.relative_to(workspace).as_posix(), "net": net_id, "mode": mode, "expected": expected, "observed": observed}


def _predicate_interface_binding(workspace: Path, arguments: Mapping[str, Any], _context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    source_path = _one_path(workspace, str(arguments["source"]))
    project_path = _one_path(workspace, str(arguments["project"]))
    port = str(arguments["port"])
    local_net = str(arguments["localNet"])
    project_net = str(arguments["projectNet"])
    sheet = str(arguments["sheet"])
    source = parse_aixem(source_path)
    source_valid = port in source.get("ports", {}) and f"@{port}" in source.get("nets", {}).get(local_net, [])
    project = read_json(project_path).get("project", {})
    net = next((item for item in project.get("projectNets", []) if str(item.get("id")) == project_net), None)
    member = f"{sheet}@{port}"
    members = sorted(_canonical_member(item) for item in (net or {}).get("members", []))
    valid = source_valid and member in members
    return valid, {"sourceBinding": source_valid, "projectMember": member, "observedProjectMembers": members}


def _predicate_render_deterministic(workspace: Path, arguments: Mapping[str, Any], _context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    run_record = arguments.get("runRecord")
    if run_record:
        path = _one_path(workspace, str(run_record))
        determinism = read_json(path).get("final", {}).get("determinism", {})
        return bool(determinism.get("valid")), {"source": path.relative_to(workspace).as_posix(), "determinism": determinism}
    project = _project_path(workspace, arguments)
    repeats = int(arguments.get("repeats", 3))
    result = render_workspace(workspace, project=project, repeat_count=repeats)
    return bool(result.get("determinism", {}).get("valid")), {"determinism": result.get("determinism"), "diagnostics": result.get("diagnostics", [])}


HANDLERS: dict[str, Callable[[Path, Mapping[str, Any], dict[str, Any]], tuple[bool, dict[str, Any]]]] = {
    "validator-pass": _predicate_validator_pass,
    "diagnostic-absent": _predicate_diagnostic_absent,
    "artifact-present": _predicate_artifact_present,
    "authority-digest-unchanged": _predicate_authority_digest_unchanged,
    "symbol-port-set": _predicate_symbol_port_set,
    "entity-present": _predicate_entity_present,
    "local-net-members": _predicate_local_net_members,
    "project-net-members": _predicate_project_net_members,
    "interface-binding": _predicate_interface_binding,
    "render-deterministic": _predicate_render_deterministic,
}


def score_invariants(
    workspace: Path,
    manifest: Mapping[str, Any],
    stage_manifest: Mapping[str, Any],
    *,
    schema_file: Path,
) -> dict[str, Any]:
    manifest = validate_invariant_manifest(manifest, schema_file)
    workspace = workspace.resolve()
    before = snapshot_workspace(workspace)
    context = {"stageManifest": dict(stage_manifest), "validationCache": {}}
    results: list[dict[str, Any]] = []
    for invariant in manifest["invariants"]:
        try:
            passed, evidence = HANDLERS[str(invariant["predicate"])](workspace, invariant.get("arguments", {}), context)
            error = None
        except Exception as exc:  # noqa: BLE001
            passed = False
            evidence = {}
            error = str(exc)
        result = {
            "id": invariant["id"],
            "predicate": invariant["predicate"],
            "required": bool(invariant.get("required", True)),
            "status": "PASS" if passed else "FAIL",
            "passed": bool(passed),
            "evidence": evidence,
        }
        if error:
            result["error"] = error
        results.append(result)
    after = snapshot_workspace(workspace)
    authoritative_unchanged_by_scorer = before["authoritativeDigest"] == after["authoritativeDigest"]
    if not authoritative_unchanged_by_scorer:
        raise InvariantError("evaluator mutated authoritative workspace content")
    required = [item for item in results if item["required"]]
    passed_required = sum(item["passed"] for item in required)
    payload: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "formatVersion": "1.0",
        "caseId": manifest["caseId"],
        "stageDigest": stage_manifest.get("stageDigest"),
        "summary": {
            "invariants": len(results),
            "required": len(required),
            "passedRequired": passed_required,
            "failedRequired": len(required) - passed_required,
        },
        "passed": passed_required == len(required),
        "authoritativeWorkspaceUnchangedByEvaluator": authoritative_unchanged_by_scorer,
        "results": results,
        "authority": "derived-evaluator-only",
    }
    payload["resultDigest"] = sha256_bytes(canonical_json_bytes(payload))
    return payload


def _json_pointer_get(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise InvariantError(f"invalid JSON pointer {pointer!r}")
    current = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if token not in current:
                raise InvariantError(f"task basis pointer does not resolve: {pointer}")
            current = current[token]
        elif isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError) as exc:
                raise InvariantError(f"task basis pointer does not resolve: {pointer}") from exc
        else:
            raise InvariantError(f"task basis pointer does not resolve: {pointer}")
    return current


def _reference_documents(reference_root: Path) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    docs_root = reference_root / "docs"
    if not docs_root.is_dir():
        return documents
    for path in sorted(docs_root.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---\n"):
            continue
        end = text.find("\n---\n", 4)
        if end < 0:
            continue
        front = text[4:end]
        doc_id = None
        requirements: set[str] = set()
        for line in front.splitlines():
            stripped = line.strip()
            if stripped.startswith("id:") and doc_id is None:
                doc_id = stripped.split(":", 1)[1].strip().strip("'\"")
            if stripped.startswith("- id:"):
                requirements.add(stripped.split(":", 1)[1].strip().strip("'\""))
        if doc_id:
            documents[doc_id] = {
                "path": path.relative_to(reference_root).as_posix(),
                "requirements": requirements,
            }
    return documents


def audit_invariant_basis(
    task: Mapping[str, Any],
    manifest: Mapping[str, Any],
    *,
    reference_root: Path,
    schema_file: Path,
) -> dict[str, Any]:
    """Prove that hidden expectations originate in agent-visible inputs."""
    manifest = validate_invariant_manifest(manifest, schema_file)
    documents = _reference_documents(reference_root)
    results: list[dict[str, Any]] = []
    for invariant in manifest.get("invariants", []):
        errors: list[str] = []
        resolved: list[dict[str, Any]] = []
        for basis in invariant.get("basis", []):
            basis_type = basis.get("type")
            if basis_type == "task":
                pointer = str(basis.get("pointer"))
                try:
                    _json_pointer_get(task, pointer)
                    resolved.append({"type": "task", "pointer": pointer})
                except InvariantError as exc:
                    errors.append(str(exc))
            elif basis_type == "document":
                document_id = str(basis.get("documentId"))
                requirement_id = str(basis.get("requirementId"))
                document = documents.get(document_id)
                if not document:
                    errors.append(f"document basis is not staged: {document_id}")
                elif requirement_id not in document["requirements"]:
                    errors.append(f"requirement basis is not staged: {document_id}/{requirement_id}")
                else:
                    resolved.append({"type": "document", "documentId": document_id, "requirementId": requirement_id, "path": document["path"]})
            elif basis_type == "profile":
                relative = _safe_path(str(basis.get("path")))
                path = reference_root / relative
                if not path.is_file():
                    errors.append(f"profile basis is not staged: {relative}")
                else:
                    resolved.append({"type": "profile", "path": relative})
            else:
                errors.append(f"unsupported invariant basis type: {basis_type!r}")
        results.append({
            "id": invariant.get("id"),
            "valid": not errors and bool(resolved),
            "resolved": resolved,
            "errors": errors,
        })
    return {
        "valid": bool(results) and all(item["valid"] for item in results),
        "invariants": results,
        "summary": {
            "invariants": len(results),
            "passed": sum(item["valid"] for item in results),
            "failed": sum(not item["valid"] for item in results),
        },
        "authority": "evaluator-basis-audit-only",
    }
