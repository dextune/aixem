"""Agent Task Contract 1 validation and route-authority resolution.

A task is a non-authoritative request envelope.  It may narrow a route's write
scope but can never grant authority that the selected route does not already
own.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from .change_scope import canonical_json_bytes, scope_summary

TASK_SCHEMA = "https://schemas.aixem.org/agent/task/1"
TASK_FORMAT_VERSION = "1.0"
TASK_SCHEMA_FILE = "aixem-agent-task-1.schema.json"


class TaskContractError(RuntimeError):
    """The request envelope or selected route violates Agent Task Contract 1."""


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_relative(value: str) -> str:
    pure = PurePosixPath(value)
    if not value or pure.is_absolute() or ".." in pure.parts or (pure.parts and ":" in pure.parts[0]):
        raise TaskContractError(f"unsafe task-relative path: {value!r}")
    return pure.as_posix()


def _matches(path: str, pattern: str) -> bool:
    path = PurePosixPath(path).as_posix()
    pattern = PurePosixPath(pattern).as_posix()
    return fnmatch.fnmatchcase(path, pattern) or (
        pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:])
    )


def schema_path(repository_root: Path) -> Path:
    return repository_root / "docs" / "specifications" / "schemas" / "agent" / TASK_SCHEMA_FILE


def validate_task_document(task: Mapping[str, Any], repository_root: Path) -> dict[str, Any]:
    path = schema_path(repository_root)
    if not path.is_file():
        raise TaskContractError(f"task schema is missing: {path}")
    validator = Draft202012Validator(read_json(path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(task), key=lambda item: list(item.absolute_path))
    if errors:
        rendered = []
        for issue in errors[:20]:
            location = "/" + "/".join(str(part) for part in issue.absolute_path)
            rendered.append(f"{location or '/'}: {issue.message}")
        raise TaskContractError("invalid Agent Task Contract 1 document: " + "; ".join(rendered))
    return dict(task)


def _packet(repository_root: Path, route: str) -> tuple[Path, dict[str, Any]]:
    path = repository_root / "docs" / "_meta" / "generated" / "task-packets" / f"{route}.json"
    if not path.is_file():
        raise TaskContractError(f"compiled task packet is missing for route {route!r}")
    packet = read_json(path)
    if packet.get("id") != route:
        raise TaskContractError(f"task packet identity mismatch for route {route!r}")
    return path, packet


def resolve_task_route(task: Mapping[str, Any], repository_root: Path) -> dict[str, Any]:
    """Resolve the active packet and prove that task constraints only narrow it."""
    task = validate_task_document(task, repository_root)
    entry_route = str(task["entryRoute"])
    entry_path, entry_packet = _packet(repository_root, entry_route)
    active_route = task.get("activeRoute")

    if entry_packet.get("kind") == "composite":
        child_routes = [str(item["route"]) for item in entry_packet.get("stages", [])]
        if not active_route:
            raise TaskContractError(
                f"composite route {entry_route!r} requires activeRoute for an executable attempt; "
                f"allowed children: {', '.join(child_routes)}"
            )
        if active_route not in child_routes:
            raise TaskContractError(f"activeRoute {active_route!r} is not a child of {entry_route!r}")
        active_path, active_packet = _packet(repository_root, str(active_route))
        route_chain = [entry_route, str(active_route)]
    else:
        if active_route and active_route != entry_route:
            raise TaskContractError("a simple entry route cannot select a different activeRoute")
        active_route = entry_route
        active_path, active_packet = entry_path, entry_packet
        route_chain = [entry_route]

    route_writes = active_packet.get("writes")
    if not isinstance(route_writes, Mapping):
        raise TaskContractError(f"active route {active_route!r} has no write-scope contract")
    route_scope = scope_summary(route_writes)
    constraints = dict(task.get("writeConstraints", {}) or {})

    requested_authorities = set(map(str, constraints.get("writableAuthorities", []) or []))
    route_authorities = set(route_scope["authority"])
    if not requested_authorities.issubset(route_authorities):
        excess = sorted(requested_authorities - route_authorities)
        raise TaskContractError(f"task attempts to widen route authority: {excess}")

    requested_paths = [safe_relative(str(value)) for value in constraints.get("writablePaths", []) or []]
    for path in requested_paths:
        if not any(_matches(path, pattern) for pattern in route_scope["artifacts"]):
            raise TaskContractError(f"task writable path is outside route artifact scope: {path}")
        if any(_matches(path, pattern) for pattern in route_scope["prohibited"]):
            raise TaskContractError(f"task writable path is prohibited by the route: {path}")

    task_prohibited = [safe_relative(str(value)) for value in constraints.get("prohibitedPaths", []) or []]
    task_validators = sorted(set(map(str, constraints.get("requiredValidators", []) or [])))
    effective_scope = {
        "authority": sorted(requested_authorities if requested_authorities else route_authorities),
        "artifacts": sorted(requested_paths if requested_paths else route_scope["artifacts"]),
        "derived": route_scope["derived"],
        "prohibited": sorted(set(route_scope["prohibited"]) | set(task_prohibited)),
        "constraints": route_scope["constraints"],
    }
    validators = sorted(set(map(str, active_packet.get("validators", []) or [])) | set(task_validators))
    result = {
        "entryRoute": entry_route,
        "activeRoute": str(active_route),
        "routeChain": route_chain,
        "routingMode": task["routingMode"],
        "entryTaskPacket": entry_path.relative_to(repository_root).as_posix(),
        "entryTaskPacketDigest": sha256_file(entry_path),
        "activeTaskPacket": active_path.relative_to(repository_root).as_posix(),
        "activeTaskPacketDigest": sha256_file(active_path),
        "routeWriteScope": route_scope,
        "effectiveWriteScope": effective_scope,
        "validators": validators,
        "taskDigest": sha256_bytes(canonical_json_bytes(task)),
        "authority": "derived-execution-only",
    }
    result["resolutionDigest"] = sha256_bytes(canonical_json_bytes(result))
    return result


def load_and_resolve_task(path: Path, repository_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    task = read_json(path)
    if not isinstance(task, Mapping):
        raise TaskContractError("agent task must be a JSON object")
    normalized = validate_task_document(task, repository_root)
    return normalized, resolve_task_route(normalized, repository_root)
