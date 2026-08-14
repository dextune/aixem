"""Live Run Evidence 1 and attempt-set denominator integrity."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from .change_scope import canonical_json_bytes, sha256_bytes

LIVE_RUN_SCHEMA = "https://schemas.aixem.org/agent/live-run/1"
ATTEMPT_SET_SCHEMA = "https://schemas.aixem.org/agent/attempt-set/1"
TERMINAL_STATUSES = {"PASS", "FAIL", "TIMEOUT", "EXECUTOR_ERROR", "INVALID_STAGE"}
FIXED_TIME = "2026-08-12T00:00:00Z"


class LiveRunError(RuntimeError):
    """Live evidence is incomplete, contradictory, or denominator-unsafe."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def _status(
    stage_valid: bool,
    execution: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    run_record: Mapping[str, Any] | None,
    observation_consistency: Mapping[str, Any],
    secret_hygiene: Mapping[str, Any],
) -> str:
    if not stage_valid:
        return "INVALID_STAGE"
    if execution.get("status") == "TIMEOUT":
        return "TIMEOUT"
    if execution.get("status") == "EXECUTOR_ERROR" or not execution.get("processStarted"):
        return "EXECUTOR_ERROR"
    if not execution.get("stageIntegrity", {"valid": True}).get("valid", False):
        return "FAIL"
    if not observation_consistency.get("consistent", False):
        return "FAIL"
    if not secret_hygiene.get("valid", False):
        return "FAIL"
    run_conformant = bool(run_record and run_record.get("final", {}).get("conformant"))
    return "PASS" if evaluation.get("passed") and run_conformant else "FAIL"


def build_live_run_evidence(
    *,
    release: str,
    generated_at: str,
    task_path: Path,
    stage_manifest_path: Path,
    executor_descriptor_path: Path,
    observation_log_path: Path | None,
    execution: Mapping[str, Any],
    evaluation_path: Path,
    run_record_path: Path | None,
    stage_validation: Mapping[str, Any],
    repository_release: str | None = None,
    corpus_id: str = "agent-evals-3",
    corpus_revision: str = "1.0",
    corpus_baseline_release: str | None = None,
    protocol_version: str = "1.0",
    observation_consistency: Mapping[str, Any] | None = None,
    secret_hygiene: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    task = read_json(task_path)
    stage = read_json(stage_manifest_path)
    descriptor = read_json(executor_descriptor_path)
    evaluation = read_json(evaluation_path)
    run_record = read_json(run_record_path) if run_record_path and run_record_path.is_file() else None
    repository_release = repository_release or release
    corpus_baseline_release = corpus_baseline_release or release
    observation_consistency = dict(observation_consistency or {
        "coverageDeclared": False, "status": "UNAVAILABLE", "consistent": True, "authority": "change-set"
    })
    secret_hygiene = dict(secret_hygiene or {"valid": True, "filesScanned": 0, "matches": []})
    status = _status(bool(stage_validation.get("valid")), execution, evaluation, run_record, observation_consistency, secret_hygiene)
    live_executed = bool(execution.get("liveExternalAgentExecuted"))
    evidence: dict[str, Any] = {
        "schema": LIVE_RUN_SCHEMA,
        "formatVersion": "1.0",
        "release": release,
        "repositoryRelease": repository_release,
        "corpus": {"id": corpus_id, "revision": corpus_revision, "baselineRelease": corpus_baseline_release},
        "protocolVersion": protocol_version,
        "generatedAt": generated_at,
        "caseId": task["id"],
        "attemptId": stage["attemptId"],
        "terminalStatus": status,
        "task": {"path": task_path.name, "digest": sha256_file(task_path)},
        "stage": {"path": stage_manifest_path.name, "digest": sha256_file(stage_manifest_path), "stageDigest": stage.get("stageDigest")},
        "executor": {
            "id": descriptor["id"],
            "agentClass": descriptor["agentClass"],
            "provider": descriptor.get("identity", {}).get("provider"),
            "model": descriptor.get("identity", {}).get("model"),
            "tool": descriptor.get("identity", {}).get("tool"),
            "toolVersion": descriptor.get("identity", {}).get("toolVersion"),
            "configLabel": descriptor.get("identity", {}).get("configLabel"),
            "descriptorDigest": sha256_file(executor_descriptor_path),
        },
        "execution": dict(execution),
        "observation": {
            "path": observation_log_path.name if observation_log_path and observation_log_path.is_file() else None,
            "digest": sha256_file(observation_log_path) if observation_log_path and observation_log_path.is_file() else None,
            "coverage": execution.get("observation", {}).get("coverage", {}),
            "events": execution.get("observation", {}).get("events", 0),
            "valid": bool(execution.get("observation", {}).get("valid")),
        },
        "authoringRunRecord": {
            "path": run_record_path.name if run_record_path and run_record_path.is_file() else None,
            "digest": sha256_file(run_record_path) if run_record_path and run_record_path.is_file() else None,
            "recordDigest": run_record.get("recordDigest") if run_record else None,
            "conformant": bool(run_record and run_record.get("final", {}).get("conformant")),
        },
        "evaluation": {
            "path": evaluation_path.name,
            "digest": sha256_file(evaluation_path),
            "resultDigest": evaluation.get("resultDigest"),
            "passed": bool(evaluation.get("passed")),
            "summary": evaluation.get("summary"),
        },
        "stageValidation": dict(stage_validation),
        "stageIntegrity": dict(execution.get("stageIntegrity") or {"valid": True, "legacyAssumed": True, "errors": []}),
        "observationConsistency": observation_consistency,
        "secretHygiene": secret_hygiene,
        "liveExternalAgentExecuted": live_executed,
        "claimEligible": bool(live_executed and status in {"PASS", "FAIL", "TIMEOUT"}),
        "retentionRequired": True,
        "authority": "derived-live-evidence-only",
    }
    evidence["evidenceDigest"] = sha256_bytes(canonical_json_bytes(evidence))
    return evidence


def validate_live_run(evidence: Mapping[str, Any], schema_file: Path) -> dict[str, Any]:
    validator = Draft202012Validator(read_json(schema_file), format_checker=FormatChecker())
    errors = []
    for issue in validator.iter_errors(evidence):
        errors.append("/" + "/".join(str(part) for part in issue.absolute_path) + ": " + issue.message)
    if evidence.get("terminalStatus") not in TERMINAL_STATUSES:
        errors.append("invalid terminal status")
    expected = dict(evidence)
    observed_digest = expected.pop("evidenceDigest", None)
    if sha256_bytes(canonical_json_bytes(expected)) != observed_digest:
        errors.append("live run evidence digest mismatch")
    if evidence.get("liveExternalAgentExecuted") and not evidence.get("execution", {}).get("processStarted"):
        errors.append("live execution claim lacks process-start proof")
    if evidence.get("claimEligible") and not evidence.get("liveExternalAgentExecuted"):
        errors.append("claim eligibility without live execution")
    if evidence.get("terminalStatus") == "PASS":
        if not evidence.get("stageIntegrity", {}).get("valid"):
            errors.append("PASS evidence lacks immutable-stage integrity")
        if not evidence.get("observationConsistency", {}).get("consistent"):
            errors.append("PASS evidence has observation/Change-Set discrepancy")
        if not evidence.get("secretHygiene", {}).get("valid"):
            errors.append("PASS evidence failed secret hygiene")
        if not evidence.get("evaluation", {}).get("passed"):
            errors.append("PASS evidence lacks passing invariant evaluation")
        if not evidence.get("authoringRunRecord", {}).get("conformant"):
            errors.append("PASS evidence lacks conformant authoring run record")
    return {"valid": not errors, "errors": errors, "terminalStatus": evidence.get("terminalStatus")}


def build_attempt_set(
    *,
    release: str,
    executor_descriptor: Mapping[str, Any],
    attempts: Iterable[Mapping[str, Any]],
    expected_attempt_ids: Iterable[str],
    generated_at: str = FIXED_TIME,
) -> dict[str, Any]:
    attempts = [dict(item) for item in attempts]
    expected = sorted(set(map(str, expected_attempt_ids)))
    observed = sorted(str(item.get("attemptId")) for item in attempts)
    if observed != expected:
        raise LiveRunError(f"denominator integrity failure: expected {expected}, observed {observed}")
    if len(observed) != len(set(observed)):
        raise LiveRunError("attempt set contains duplicate attempt IDs")
    status_counts = {status: sum(item.get("terminalStatus") == status for item in attempts) for status in sorted(TERMINAL_STATUSES)}
    live_attempts = [item for item in attempts if item.get("liveExternalAgentExecuted")]
    pass_count = status_counts["PASS"]
    claim = None
    if live_attempts:
        identity = executor_descriptor.get("identity", {})
        claim = (
            f"Executor {executor_descriptor.get('id')}"
            f" ({identity.get('provider') or 'provider-unspecified'}/{identity.get('model') or 'model-unspecified'}) "
            f"completed {pass_count} of {len(attempts)} retained cold-start attempts."
        )
    payload: dict[str, Any] = {
        "schema": ATTEMPT_SET_SCHEMA,
        "formatVersion": "1.0",
        "release": release,
        "generatedAt": generated_at,
        "executor": {
            "id": executor_descriptor.get("id"),
            "agentClass": executor_descriptor.get("agentClass"),
            "identity": executor_descriptor.get("identity", {}),
        },
        "expectedAttemptIds": expected,
        "attempts": [
            {
                "caseId": item.get("caseId"),
                "attemptId": item.get("attemptId"),
                "terminalStatus": item.get("terminalStatus"),
                "liveExternalAgentExecuted": bool(item.get("liveExternalAgentExecuted")),
                "evidenceDigest": item.get("evidenceDigest"),
            }
            for item in attempts
        ],
        "summary": {
            "attempts": len(attempts),
            "liveAttempts": len(live_attempts),
            "passed": pass_count,
            "failed": status_counts["FAIL"],
            "timeouts": status_counts["TIMEOUT"],
            "executorErrors": status_counts["EXECUTOR_ERROR"],
            "invalidStages": status_counts["INVALID_STAGE"],
        },
        "denominatorIntegrity": True,
        "liveExternalAgentExecuted": bool(live_attempts),
        "claim": claim,
        "authority": "derived-live-evidence-only",
    }
    payload["attemptSetDigest"] = sha256_bytes(canonical_json_bytes(payload))
    return payload
