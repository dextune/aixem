"""Deterministic Authoring Run Record 1 construction and loop analysis."""
from __future__ import annotations

import hashlib
import json
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from .diagnostics import diagnostic_state_digest

RUN_RECORD_SCHEMA = "https://schemas.aixem.org/agent/run-record/1"
RUN_RECORD_FORMAT_VERSION = "1.0"
FIXED_TIME = "2026-08-12T00:00:00Z"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def sha256_value(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def deterministic_run_id(task_id: str, task_packet_digest: str, baseline_authoritative_digest: str) -> str:
    seed = f"{task_id}\n{task_packet_digest}\n{baseline_authoritative_digest}".encode("utf-8")
    return "run-" + hashlib.sha256(seed).hexdigest()[:20]


def artifact_digest_map(snapshot: Mapping[str, Any], *, authoritative_only: bool = False) -> dict[str, str]:
    records: dict[str, str] = {}
    for path, record in sorted(dict(snapshot.get("files", {})).items()):
        if authoritative_only and record.get("role") != "authoritative":
            continue
        records[path] = str(record.get("digest"))
    return records


def _blocking_count(diagnostics: Iterable[Mapping[str, Any]]) -> int:
    return sum(1 for item in diagnostics if item.get("severity", "error") == "error")


def make_iteration_record(
    *,
    iteration: int,
    route: str,
    stage: str,
    diagnostics_before: Sequence[Mapping[str, Any]],
    change_set: Mapping[str, Any],
    diagnostics_after: Sequence[Mapping[str, Any]],
    validators: Iterable[str],
    rendered_evidence: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    before_digest = diagnostic_state_digest(diagnostics_before)
    after_digest = diagnostic_state_digest(diagnostics_after)
    before_count = _blocking_count(diagnostics_before)
    after_count = _blocking_count(diagnostics_after)
    changed = len(change_set.get("changed", []))
    return {
        "iteration": int(iteration),
        "route": route,
        "stage": stage,
        "diagnosticsBefore": [dict(item) for item in diagnostics_before],
        "diagnosticStateBefore": before_digest,
        "blockingBefore": before_count,
        "changeSet": dict(change_set),
        "changeSetDigest": sha256_value(change_set),
        "authoritativeDigestBefore": change_set.get("beforeAuthoritativeDigest"),
        "authoritativeDigestAfter": change_set.get("afterAuthoritativeDigest"),
        "diagnosticsAfter": [dict(item) for item in diagnostics_after],
        "diagnosticStateAfter": after_digest,
        "blockingAfter": after_count,
        "validatorsExecuted": sorted(set(validators)),
        "renderedEvidence": dict(sorted((rendered_evidence or {}).items())),
        "improved": after_count < before_count or (after_count == 0 and before_count == 0 and changed > 0),
    }


def detect_loop_state(iterations: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Detect unchanged blocking states and A→B→A oscillation."""
    if not iterations:
        return {"stalled": False, "oscillating": False, "atIteration": None, "stateDigest": None}
    latest = iterations[-1]
    stalled = bool(
        latest.get("blockingAfter", 0)
        and latest.get("diagnosticStateBefore") == latest.get("diagnosticStateAfter")
    )
    oscillating = False
    state_digest = None
    if len(iterations) >= 2:
        previous = iterations[-2]
        pair_before = (latest.get("authoritativeDigestBefore"), latest.get("diagnosticStateBefore"))
        previous_before = (previous.get("authoritativeDigestBefore"), previous.get("diagnosticStateBefore"))
        if pair_before == previous_before and latest.get("blockingAfter", 0):
            stalled = True
    if len(iterations) >= 3:
        states = [
            (item.get("authoritativeDigestAfter"), item.get("diagnosticStateAfter"))
            for item in iterations[-3:]
        ]
        if states[0] == states[2] and states[0] != states[1] and latest.get("blockingAfter", 0):
            oscillating = True
            state_digest = sha256_value(states[2])
    if stalled and state_digest is None:
        state_digest = str(latest.get("diagnosticStateAfter"))
    return {
        "stalled": stalled,
        "oscillating": oscillating,
        "atIteration": int(latest.get("iteration", len(iterations))) if (stalled or oscillating) else None,
        "stateDigest": state_digest,
    }


def _validate_relative_paths(records: Mapping[str, str]) -> None:
    for path in records:
        pure = PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts or not pure.parts:
            raise ValueError(f"unsafe run-record path: {path!r}")


def build_run_record(
    *,
    release: str,
    task_id: str,
    entry_route: str,
    active_route: str,
    task_packet_digest: str,
    baseline_snapshot: Mapping[str, Any],
    final_snapshot: Mapping[str, Any],
    route_chain: Sequence[str],
    iterations: Sequence[Mapping[str, Any]],
    final_diagnostics: Sequence[Mapping[str, Any]],
    render_artifacts: Mapping[str, str],
    determinism: Mapping[str, Any],
    execution_mode: str = "deterministic-harness",
    live_external_agent_executed: bool = False,
    executor: Mapping[str, Any] | None = None,
    generated_at: str = FIXED_TIME,
) -> dict[str, Any]:
    baseline_artifacts = artifact_digest_map(baseline_snapshot, authoritative_only=True)
    final_artifacts = artifact_digest_map(final_snapshot, authoritative_only=True)
    _validate_relative_paths(baseline_artifacts)
    _validate_relative_paths(final_artifacts)
    _validate_relative_paths(render_artifacts)
    scope_violations = sum(len(item.get("changeSet", {}).get("scopeViolations", [])) for item in iterations)
    generated_output_edits = sum(len(item.get("changeSet", {}).get("generatedOutputEdits", [])) for item in iterations)
    blocking = _blocking_count(final_diagnostics)
    loop = detect_loop_state(iterations)
    closed = (
        blocking == 0
        and scope_violations == 0
        and generated_output_edits == 0
        and bool(determinism.get("valid"))
        and not loop["stalled"]
        and not loop["oscillating"]
    )
    run_id = deterministic_run_id(task_id, task_packet_digest, str(baseline_snapshot.get("authoritativeDigest", "")))
    record: dict[str, Any] = {
        "schema": RUN_RECORD_SCHEMA,
        "formatVersion": RUN_RECORD_FORMAT_VERSION,
        "release": release,
        "generatedAt": generated_at,
        "runId": run_id,
        "taskId": task_id,
        "entryRoute": entry_route,
        "activeRoute": active_route,
        "taskPacketDigest": task_packet_digest,
        "execution": {
            "mode": execution_mode,
            "liveExternalAgentExecuted": bool(live_external_agent_executed),
            **({"executor": dict(executor)} if executor else {}),
        },
        "baseline": {
            "snapshotDigest": baseline_snapshot.get("digest"),
            "authoritativeDigest": baseline_snapshot.get("authoritativeDigest"),
            "artifactDigests": baseline_artifacts,
        },
        "routeChain": list(route_chain),
        "iterations": [dict(item) for item in iterations],
        "loopState": loop,
        "final": {
            "status": "CLOSED" if closed else "BLOCKED",
            "conformant": closed,
            "snapshotDigest": final_snapshot.get("digest"),
            "authoritativeDigest": final_snapshot.get("authoritativeDigest"),
            "authoritativeArtifactDigests": final_artifacts,
            "renderArtifactDigests": dict(sorted(render_artifacts.items())),
            "diagnostics": [dict(item) for item in final_diagnostics],
            "diagnosticCount": len(final_diagnostics),
            "blockingDiagnosticCount": blocking,
            "scopeViolationCount": scope_violations,
            "generatedOutputEditCount": generated_output_edits,
            "determinism": dict(determinism),
        },
    }
    record["recordDigest"] = sha256_value({key: value for key, value in record.items() if key != "recordDigest"})
    return record
