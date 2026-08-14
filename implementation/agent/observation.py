"""Observation Event Contract 1 JSONL support.

Only externally observable actions are retained.  Private model reasoning and
chain-of-thought fields are rejected by construction.
"""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from .change_scope import canonical_json_bytes, sha256_bytes
from .secret_hygiene import redact_nested

OBSERVATION_SCHEMA = "https://schemas.aixem.org/agent/observation-event/1"
OBSERVATION_FORMAT_VERSION = "1.0"
EVENT_KINDS = {
    "task-open", "route-resolve", "document-open", "file-read", "search",
    "command", "validator", "render", "file-write", "file-delete",
    "completion", "executor-error",
}
FORBIDDEN_PRIVATE_FIELDS = {
    "chainOfThought", "chain_of_thought", "cot", "reasoning", "privateReasoning",
    "thoughts", "scratchpad", "internalMonologue", "promptTranscript",
}
COVERAGE_EVENT_KINDS = {
    "fileReads": {"task-open", "document-open", "file-read"},
    "searches": {"search"},
    "commands": {"command", "validator", "render"},
    "writes": {"file-write", "file-delete"},
    "routeActions": {"route-resolve"},
}


class ObservationError(RuntimeError):
    """The observable event stream violates Observation Event Contract 1."""


def _safe_target(value: str | None) -> str | None:
    if value is None:
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or (pure.parts and ":" in pure.parts[0]):
        raise ObservationError(f"unsafe observation target: {value!r}")
    return pure.as_posix()


def _walk_forbidden(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            child = f"{path}/{key}"
            if str(key) in FORBIDDEN_PRIVATE_FIELDS:
                found.append(child)
            found.extend(_walk_forbidden(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_walk_forbidden(item, f"{path}/{index}"))
    return found


def make_event(
    sequence: int,
    kind: str,
    *,
    target: str | None = None,
    route: str | None = None,
    tool: str | None = None,
    result: str | None = None,
    elapsed_ms: int | None = None,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if kind not in EVENT_KINDS:
        raise ObservationError(f"unsupported observation kind {kind!r}")
    event: dict[str, Any] = {
        "schema": OBSERVATION_SCHEMA,
        "formatVersion": OBSERVATION_FORMAT_VERSION,
        "sequence": int(sequence),
        "kind": kind,
    }
    if target is not None:
        event["target"] = _safe_target(target)
    if route is not None:
        event["route"] = route
    if tool is not None:
        event["tool"] = tool
    if result is not None:
        event["result"] = result
    if elapsed_ms is not None:
        event["elapsedMs"] = max(0, int(elapsed_ms))
    if details:
        event["details"] = dict(details)
    forbidden = _walk_forbidden(event)
    if forbidden:
        raise ObservationError("private reasoning fields are prohibited: " + ", ".join(forbidden))
    return event


def write_events(path: Path, events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    normalized = [dict(event) for event in events]
    path.parent.mkdir(parents=True, exist_ok=True)
    data = b"".join(canonical_json_bytes(event) for event in normalized)
    path.write_bytes(data)
    return {"path": path.as_posix(), "events": len(normalized), "digest": sha256_bytes(data)}


def append_event(path: Path, event: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as handle:
        handle.write(canonical_json_bytes(dict(event)))


def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ObservationError(f"invalid observation JSONL line {line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ObservationError(f"observation line {line_number} is not an object")
        events.append(value)
    return events


def validate_events(
    events: Iterable[Mapping[str, Any]],
    schema_file: Path,
    *,
    declared_coverage: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    normalized = [dict(event) for event in events]
    expected_sequence = 1
    for event in normalized:
        forbidden = _walk_forbidden(event)
        if forbidden:
            errors.append("private reasoning fields: " + ", ".join(forbidden))
        for issue in validator.iter_errors(event):
            location = "/" + "/".join(str(part) for part in issue.absolute_path)
            errors.append(f"event {event.get('sequence')}{location}: {issue.message}")
        if event.get("sequence") != expected_sequence:
            errors.append(f"expected sequence {expected_sequence}, observed {event.get('sequence')}")
        expected_sequence += 1
        try:
            _safe_target(event.get("target"))
        except ObservationError as exc:
            errors.append(str(exc))

    kinds = [str(event.get("kind")) for event in normalized]
    observed = {
        name: sum(kind in accepted for kind in kinds)
        for name, accepted in COVERAGE_EVENT_KINDS.items()
    }
    declared = dict(declared_coverage or {})
    coverage = {name: bool(declared.get(name, False)) for name in COVERAGE_EVENT_KINDS}
    unsupported_claims = sorted(set(declared) - set(COVERAGE_EVENT_KINDS))
    if unsupported_claims:
        errors.append("unsupported coverage claims: " + ", ".join(unsupported_claims))
    serialized = b"".join(canonical_json_bytes(event) for event in normalized)
    return {
        "valid": not errors,
        "events": len(normalized),
        "digest": sha256_bytes(serialized),
        "coverage": coverage,
        "observedCounts": observed,
        "errors": errors,
    }


def validate_observation_log(path: Path, schema_file: Path, *, declared_coverage: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return validate_events(read_events(path), schema_file, declared_coverage=declared_coverage)



def sanitize_observation_log(path: Path, explicit_secrets: Iterable[str] = ()) -> dict[str, Any]:
    """Sanitize official observation evidence before validation and retention.

    A malformed raw stream is replaced by an empty official stream.  This
    ensures a malformed line cannot become a credential-retention bypass.
    The caller still receives ``parseValid=false`` and therefore cannot claim
    successful observation coverage.
    """
    if not path.is_file():
        return {"valid": False, "parseValid": False, "events": 0, "redactionApplied": False, "redactions": 0, "errors": ["observation log is missing"]}
    try:
        events = read_events(path)
    except ObservationError as exc:
        path.write_bytes(b"")
        return {"valid": False, "parseValid": False, "events": 0, "redactionApplied": False, "redactions": 0, "errors": [str(exc)]}
    sanitized_events: list[dict[str, Any]] = []
    changed = False
    redactions = 0
    for event in events:
        sanitized, item_changed, item_count = redact_nested(event, explicit_secrets)
        sanitized_events.append(dict(sanitized))
        changed = changed or item_changed
        redactions += item_count
    write_events(path, sanitized_events)
    return {
        "valid": True,
        "parseValid": True,
        "events": len(sanitized_events),
        "redactionApplied": changed,
        "redactions": redactions,
        "errors": [],
    }


def _workspace_relative_target(value: str | None) -> str | None:
    if value is None:
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or (pure.parts and ":" in pure.parts[0]):
        raise ObservationError(f"unsafe observation target: {value!r}")
    parts = list(pure.parts)
    if parts and parts[0] == "workspace":
        parts = parts[1:]
    if not parts:
        return None
    return PurePosixPath(*parts).as_posix()


def change_set_paths(run_record: Mapping[str, Any] | None) -> list[str]:
    """Return final mutation paths from Change-Set evidence.

    Change-Set remains the only mutation authority.  This helper merely
    normalizes the several retained forms used by historical run records.
    """
    if not run_record:
        return []
    paths: set[str] = set()
    change_sets: list[Mapping[str, Any]] = []
    for iteration in run_record.get("iterations", []) or []:
        if isinstance(iteration, Mapping) and isinstance(iteration.get("changeSet"), Mapping):
            change_sets.append(iteration["changeSet"])
    if isinstance(run_record.get("changeSet"), Mapping):
        change_sets.append(run_record["changeSet"])
    for change_set in change_sets:
        for item in change_set.get("changed", []) or []:
            raw = item.get("path") if isinstance(item, Mapping) else item
            if raw:
                normalized = _workspace_relative_target(str(raw))
                if normalized:
                    paths.add(normalized)
        for key in ("added", "modified", "deleted", "changedPaths"):
            for item in change_set.get(key, []) or []:
                raw = item.get("path") if isinstance(item, Mapping) else item
                if raw:
                    normalized = _workspace_relative_target(str(raw))
                    if normalized:
                        paths.add(normalized)
    return sorted(paths)


def reconcile_observation_writes(
    events: Iterable[Mapping[str, Any]],
    run_record: Mapping[str, Any] | None,
    *,
    writes_declared: bool,
) -> dict[str, Any]:
    """Compare write telemetry with Change-Set truth without changing authority."""
    observed: set[str] = set()
    unsafe: list[str] = []
    for event in events:
        if event.get("kind") not in {"file-write", "file-delete"}:
            continue
        try:
            normalized = _workspace_relative_target(event.get("target"))
        except ObservationError:
            unsafe.append(str(event.get("target")))
            continue
        if normalized:
            observed.add(normalized)
    changed = set(change_set_paths(run_record))
    if not writes_declared:
        return {
            "coverageDeclared": False,
            "status": "UNAVAILABLE",
            "changedPaths": sorted(changed),
            "observedWritePaths": sorted(observed),
            "missingObservedWrites": [],
            "unmatchedObservedWrites": [],
            "unsafeObservedTargets": unsafe,
            "consistent": not unsafe,
            "authority": "change-set",
        }
    missing = sorted(changed - observed)
    unmatched = sorted(observed - changed)
    return {
        "coverageDeclared": True,
        "status": "CONSISTENT" if not missing and not unmatched and not unsafe else "DISCREPANCY",
        "changedPaths": sorted(changed),
        "observedWritePaths": sorted(observed),
        "missingObservedWrites": missing,
        "unmatchedObservedWrites": unmatched,
        "unsafeObservedTargets": unsafe,
        "consistent": not missing and not unmatched and not unsafe,
        "authority": "change-set",
    }
