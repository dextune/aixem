#!/usr/bin/env python3
"""Run Agent Evaluation 3 pre-live readiness and optional external Tier B.

Tier A / pre-live readiness uses deterministic non-AI subprocess fixtures only.
Those fixtures can prove protocol plumbing, but they can never authorize a
external-agent claim. Tier B runs only when an explicit external-AI descriptor
is supplied and uses actual UTC evidence timestamps.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from typing import Any, Callable, Iterable, Mapping, TypeVar

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.change_scope import canonical_json_bytes  # noqa: E402
from agent.cold_start_stage import build_stage, validate_stage  # noqa: E402
from agent.invariant_scorer import audit_invariant_basis, score_invariants  # noqa: E402
from agent.live_executor import execute_subprocess, validate_executor_descriptor  # noqa: E402
from agent.live_run import build_attempt_set, build_live_run_evidence, validate_live_run  # noqa: E402
from agent.observation import read_events, reconcile_observation_writes  # noqa: E402
from agent.secret_hygiene import scan_paths, scan_text_for_secrets  # noqa: E402
from agent.validator_adapter import validate_workspace  # noqa: E402

FIXED_TIME = "2026-08-12T00:00:00Z"
RELEASE_DATE = "2026-08-12"
CORPUS = ROOT / "validation" / "agent-evals-3"
CASES = CORPUS / "cases"
SCHEMAS = ROOT / "docs" / "specifications" / "schemas" / "agent"
READINESS_FIXTURE = ROOT / "tests" / "fixtures" / "agents" / "readiness_fixture_agent.py"
OBSERVABLE_FIXTURE = ROOT / "tests" / "fixtures" / "agents" / "observable_fixture_agent.py"
EXTERNAL_RUNTIME_NAMES = (
    "codex", "claude", "opencode", "aider", "goose", "roo-code",
    "ollama", "llama-cli", "llama-server", "llm", "openai", "gemini",
)
SUCCESS_CASES = {
    "R001": ("L008", "create-symbol", "symbol/component-library/project"),
    "R002": ("L009", "create-schematic", "semantic/project"),
    "R003": ("L010", "route-nets", "layout/project"),
    "R004": ("L011", "compose-project", "project"),
}
AUTHORING_ROUTES = (
    "create-symbol", "create-schematic", "route-nets", "compose-project",
    "route-project-nets", "render-review", "validate-project", "author-component-circuit",
)
T = TypeVar("T")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def repository_release() -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return f"AIXEM-SRP-{version}-{RELEASE_DATE}"


def corpus_identity() -> dict[str, str]:
    manifest = read_json(CORPUS / "manifest.json")
    return {
        "id": str(manifest.get("corpusId") or manifest.get("id") or "agent-evals-3"),
        "revision": str(manifest.get("corpusRevision") or "1.0"),
        "baselineRelease": str(manifest.get("baselineRelease") or manifest.get("release") or repository_release()),
        "protocolVersion": str(manifest.get("protocolVersion") or "1.0"),
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def sha256_tree(root: Path) -> str:
    records = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and not item.is_symlink()):
        records.append({"path": path.relative_to(root).as_posix(), "digest": sha256_file(path), "bytes": path.stat().st_size})
    return "sha256:" + hashlib.sha256(canonical_json_bytes(records)).hexdigest()


def safe_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise RuntimeError(f"retained path {path} is outside declared results root {root}") from exc


def prepare_output_root(path: Path, label: str) -> Path:
    path = path.resolve()
    if path.exists() and not path.is_dir():
        raise RuntimeError(f"{label} destination is not a directory: {path}")
    path.mkdir(parents=True, exist_ok=True)
    probe = path / ".aixem-write-probe"
    try:
        probe.write_text("ok\n", encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"{label} destination is not writable: {path}: {exc}") from exc
    finally:
        probe.unlink(missing_ok=True)
    return path


def _parallel(items: Iterable[T], function: Callable[[T], Any], workers: int = 4) -> list[Any]:
    values = list(items)
    if not values:
        return []
    with ThreadPoolExecutor(max_workers=min(workers, len(values))) as executor:
        return list(executor.map(function, values))


def case_roots() -> list[Path]:
    roots = sorted(CASES.glob("L[0-9][0-9][0-9]"))
    expected = [f"L{i:03d}" for i in range(1, 13)]
    observed = [path.name for path in roots]
    if observed != expected:
        raise RuntimeError(f"Agent Evaluation 3 inventory mismatch: expected {expected}, observed {observed}")
    return roots


def diagnostic_codes(case: Path) -> list[str]:
    task = read_json(case / "agent-task.json")
    result = validate_workspace(case / "start", str(task["activeRoute"]), project=Path(str(task.get("project", "project.aixproj.json"))))
    return sorted({str(item.get("code")) for item in result.get("diagnostics", []) if item.get("severity") == "error"})


def audit_corpus() -> dict[str, Any]:
    cases = []
    valid = True
    for case in case_roots():
        metadata = read_json(case / "case.json")
        observed = diagnostic_codes(case)
        expected = sorted(set(map(str, metadata.get("expectedInitialDiagnostics", []))))
        diagnostics_match = set(expected).issubset(observed)
        forbidden = []
        for path in (case / "start").rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(case / "start").as_posix().lower()
            if relative.startswith("render/") or relative.startswith("evidence/") or "evaluator/" in relative or relative.endswith("invariants.json"):
                forbidden.append(relative)
        item_valid = diagnostics_match and not forbidden and not bool(metadata.get("completedTargetBundled"))
        valid = valid and item_valid
        cases.append({
            "id": case.name, "category": metadata.get("category"),
            "expectedInitialDiagnostics": expected, "observedInitialDiagnostics": observed,
            "diagnosticsMatch": diagnostics_match, "forbiddenStagedArtifacts": forbidden,
            "completedTargetBundled": bool(metadata.get("completedTargetBundled")), "valid": item_valid,
        })
    return {"valid": valid, "cases": cases, "summary": {"cases": len(cases), "valid": sum(item["valid"] for item in cases), "invalid": sum(not item["valid"] for item in cases)}}


def deterministic_stage_audit(output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)

    def one(case: Path) -> dict[str, Any]:
        first = output / f"{case.name}-a"
        second = output / f"{case.name}-b"
        shutil.rmtree(first, ignore_errors=True)
        shutil.rmtree(second, ignore_errors=True)
        attempt_id = f"{case.name}-tier-a-determinism-01"
        started = time.perf_counter()
        manifest_a = build_stage(ROOT, case, attempt_id, first)
        manifest_b = build_stage(ROOT, case, attempt_id, second)
        build_ms = int(round((time.perf_counter() - started) * 1000))
        check_a = validate_stage(first, ROOT)
        check_b = validate_stage(second, ROOT)
        same = (
            manifest_a["stageDigest"] == manifest_b["stageDigest"]
            and manifest_a["referencePack"]["digest"] == manifest_b["referencePack"]["digest"]
            and manifest_a["startWorkspace"]["snapshotDigest"] == manifest_b["startWorkspace"]["snapshotDigest"]
            and sha256_tree(first / "task") == sha256_tree(second / "task")
            and sha256_tree(first / "reference") == sha256_tree(second / "reference")
            and sha256_tree(first / "workspace") == sha256_tree(second / "workspace")
        )
        item_valid = bool(check_a["valid"] and check_b["valid"] and same)
        return {
            "id": case.name, "stageDigest": manifest_a["stageDigest"],
            "referencePackDigest": manifest_a["referencePack"]["digest"],
            "startWorkspaceDigest": manifest_a["startWorkspace"]["snapshotDigest"],
            "deterministic": same, "buildPairMs": build_ms,
            "firstValidation": check_a, "secondValidation": check_b, "valid": item_valid,
        }

    cases = sorted(_parallel(case_roots(), one), key=lambda item: item["id"])
    return {"valid": all(item["valid"] for item in cases), "cases": cases, "summary": {"cases": len(cases), "passed": sum(item["valid"] for item in cases), "failed": sum(not item["valid"] for item in cases)}}


def base_descriptor(command: list[str], *, descriptor_id: str, writes: bool, wall_time: int = 180, output_bytes: int = 1048576, event_limit: int = 1000) -> dict[str, Any]:
    label = f"{descriptor_id}|{writes}|{wall_time}".encode("utf-8")
    return {
        "schema": "https://schemas.aixem.org/agent/executor/1", "formatVersion": "1.0",
        "id": descriptor_id, "adapterVersion": "1.0", "agentClass": "test-fixture",
        "command": command, "workingDirectoryPolicy": "stage-root", "inputMode": "task-path-argument",
        "observationCapability": {"fileReads": False, "searches": False, "commands": True, "writes": writes, "routeActions": True},
        "networkPolicy": {"mode": "deny", "enforcement": "descriptor-only"},
        "limits": {"wallTimeSeconds": wall_time, "outputBytes": output_bytes, "observationEvents": event_limit},
        "identity": {"provider": "AIXEM", "model": "none", "tool": "pre-live-readiness-fixture", "toolVersion": "1.0", "configLabel": descriptor_id},
        "redactedConfigurationDigest": "sha256:" + hashlib.sha256(label).hexdigest(),
    }


def observable_descriptor() -> dict[str, Any]:
    return base_descriptor([
        sys.executable, str(OBSERVABLE_FIXTURE), "--task", "{task}", "--workspace", "{workspace}",
        "--reference", "{reference}", "--state", "{state}", "--observation-log", "{observationLog}",
    ], descriptor_id="observable-non-ai-fixture", writes=False, wall_time=180)


def readiness_descriptor(mode: str, *, descriptor_id: str, writes: bool, wall_time: int = 180, child_canary: Path | None = None) -> dict[str, Any]:
    command = [
        sys.executable, str(READINESS_FIXTURE), "--task", "{task}", "--workspace", "{workspace}",
        "--reference", "{reference}", "--state", "{state}", "--observation-log", "{observationLog}", "--mode", mode,
    ]
    if child_canary is not None:
        command.extend(["--child-canary", str(child_canary)])
    return base_descriptor(command, descriptor_id=descriptor_id, writes=writes, wall_time=wall_time)


def find_run_record(stage: Path) -> Path | None:
    records = sorted((stage / "state").rglob("authoring-run-record.json"))
    return records[-1] if records else None


def platform_metrics(stage: Path, manifest: Mapping[str, Any], execution: Mapping[str, Any], *, stage_build_ms: int, stage_validate_ms: int, evaluator_ms: int, retain_ms: int) -> dict[str, Any]:
    metrics_path = stage / "state/readiness-metrics.json"
    authoring_metrics = read_json(metrics_path) if metrics_path.is_file() else {}
    observation_path = stage / "state/observation-log.jsonl"
    workspace_bytes = sum(path.stat().st_size for path in (stage / "workspace").rglob("*") if path.is_file())
    workspace_files = sum(1 for path in (stage / "workspace").rglob("*") if path.is_file())
    return {
        "stageBuildMs": stage_build_ms, "stageValidateMs": stage_validate_ms,
        "prepareMs": int(authoring_metrics.get("prepareMs", 0)),
        "checkMs": int(authoring_metrics.get("checkMs", 0)),
        "closeMs": int(authoring_metrics.get("closeMs", 0)),
        "executorMs": int(execution.get("durationMs", 0)), "evaluatorMs": evaluator_ms,
        "evidenceRetainMs": retain_ms,
        "referenceFiles": int(manifest.get("referencePack", {}).get("files", 0)),
        "referenceBytes": int(manifest.get("referencePack", {}).get("bytes", 0)),
        "workspaceFiles": workspace_files, "workspaceBytes": workspace_bytes,
        "observationEvents": int(execution.get("observation", {}).get("events", 0)),
        "observationBytes": observation_path.stat().st_size if observation_path.is_file() else 0,
        "sourceRepositoryPythonPathUsed": bool(authoring_metrics.get("sourceRepositoryPythonPathUsed", False)),
        "workingDirectory": authoring_metrics.get("workingDirectory"),
    }


def retain_attempt(
    *,
    results_root: Path,
    stage: Path,
    descriptor_path: Path,
    execution: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    stage_validation: Mapping[str, Any],
    destination: Path,
    generated_at: str = FIXED_TIME,
) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    copies = {
        "task": destination / "agent-task.json", "stage": destination / "stage-manifest.json",
        "executor": destination / "executor.json", "observation": destination / "observation-log.jsonl",
        "evaluation": destination / "evaluator-result.json", "record": destination / "authoring-run-record.json",
    }
    shutil.copy2(stage / "task/agent-task.json", copies["task"])
    shutil.copy2(stage / "stage-manifest.json", copies["stage"])
    shutil.copy2(descriptor_path, copies["executor"])
    observation_source = stage / "state/observation-log.jsonl"
    observation_path: Path | None = None
    if observation_source.is_file():
        shutil.copy2(observation_source, copies["observation"])
        observation_path = copies["observation"]
    write_json(copies["evaluation"], dict(evaluation))
    source_record = find_run_record(stage)
    record_path: Path | None = None
    run_record: Mapping[str, Any] | None = None
    if source_record:
        shutil.copy2(source_record, copies["record"])
        record_path = copies["record"]
        run_record = read_json(record_path)
    try:
        events = read_events(observation_path) if observation_path else []
    except Exception:
        events = []
    descriptor = read_json(copies["executor"])
    consistency = reconcile_observation_writes(
        events, run_record,
        writes_declared=bool(descriptor.get("observationCapability", {}).get("writes")),
    )
    candidate_paths = [path for path in copies.values() if path.is_file()]
    path_scan = scan_paths(candidate_paths)
    execution_scan = scan_text_for_secrets(json.dumps(dict(execution), ensure_ascii=False, sort_keys=True))
    secret_hygiene = {
        "valid": bool(path_scan["valid"] and execution_scan["valid"]),
        "filesScanned": path_scan["filesScanned"], "matches": path_scan["matches"],
        "executionExplicitMatches": execution_scan["explicitMatches"],
        "executionGenericMatches": execution_scan["genericMatches"],
        "redactionApplied": bool(execution.get("secretRedactionApplied")),
    }
    identity = corpus_identity()
    evidence = build_live_run_evidence(
        release=repository_release(), repository_release=repository_release(),
        corpus_id=identity["id"], corpus_revision=identity["revision"],
        corpus_baseline_release=identity["baselineRelease"], protocol_version=identity["protocolVersion"],
        generated_at=generated_at, task_path=copies["task"], stage_manifest_path=copies["stage"],
        executor_descriptor_path=copies["executor"], observation_log_path=observation_path,
        execution=execution, evaluation_path=copies["evaluation"], run_record_path=record_path,
        stage_validation=stage_validation, observation_consistency=consistency, secret_hygiene=secret_hygiene,
    )
    evidence_path = destination / "live-run-evidence.json"
    write_json(evidence_path, evidence)
    validation = validate_live_run(evidence, SCHEMAS / "aixem-agent-live-run-1.schema.json")
    return {
        "evidence": evidence, "validation": validation, "path": evidence_path,
        "relativePath": safe_relative(evidence_path, results_root),
        "observationConsistency": consistency, "secretHygiene": secret_hygiene,
    }


def build_and_execute(
    *, case_id: str, attempt_id: str, descriptor: Mapping[str, Any], descriptor_path: Path,
    stage_root: Path, results_root: Path, destination: Path, generated_at: str = FIXED_TIME,
) -> dict[str, Any]:
    case = CASES / case_id
    stage = stage_root / attempt_id
    shutil.rmtree(stage, ignore_errors=True)
    started = time.perf_counter()
    manifest = build_stage(ROOT, case, attempt_id, stage)
    stage_build_ms = int(round((time.perf_counter() - started) * 1000))
    started = time.perf_counter()
    stage_validation = validate_stage(stage, ROOT)
    stage_validate_ms = int(round((time.perf_counter() - started) * 1000))
    execution = execute_subprocess(
        descriptor, stage,
        executor_schema_file=SCHEMAS / "aixem-agent-executor-1.schema.json",
        observation_schema_file=SCHEMAS / "aixem-agent-observation-event-1.schema.json",
    ) if stage_validation["valid"] else {
        "status": "EXECUTOR_ERROR", "processStarted": False, "externalProcessStarted": False,
        "liveExternalAgentExecuted": False, "returnCode": None,
        "stageIntegrity": {"valid": False, "errors": stage_validation["errors"]},
        "observation": {"valid": False, "events": 0, "coverage": {}, "errors": stage_validation["errors"]},
    }
    invariants = read_json(case / "evaluator/invariants.json")
    started = time.perf_counter()
    evaluation = score_invariants(
        stage / "workspace", invariants, read_json(stage / "stage-manifest.json"),
        schema_file=SCHEMAS / "aixem-agent-evaluation-invariant-1.schema.json",
    )
    evaluator_ms = int(round((time.perf_counter() - started) * 1000))
    started = time.perf_counter()
    retained = retain_attempt(
        results_root=results_root, stage=stage, descriptor_path=descriptor_path, execution=execution,
        evaluation=evaluation, stage_validation=stage_validation, destination=destination, generated_at=generated_at,
    )
    retain_ms = int(round((time.perf_counter() - started) * 1000))
    metrics = platform_metrics(
        stage, manifest, execution, stage_build_ms=stage_build_ms,
        stage_validate_ms=stage_validate_ms, evaluator_ms=evaluator_ms, retain_ms=retain_ms,
    )
    metrics["changedAuthoritativeFiles"] = len(retained["observationConsistency"].get("changedPaths", []))
    return {
        "caseId": case_id, "attemptId": attempt_id, "stage": stage, "manifest": manifest,
        "stageValidation": stage_validation, "execution": execution, "evaluation": evaluation,
        "retained": retained, "metrics": metrics,
    }


def run_protocol_fixture(results: Path, stage_root: Path) -> dict[str, Any]:
    descriptor = observable_descriptor()
    descriptor_path = results / "tier-a/protocol-fixture-executor.json"
    write_json(descriptor_path, descriptor)
    run = build_and_execute(
        case_id="L008", attempt_id="L008-tier-a-protocol-01", descriptor=descriptor,
        descriptor_path=descriptor_path, stage_root=stage_root, results_root=results,
        destination=results / "tier-a/protocol-attempt-L008",
    )
    evidence = run["retained"]["evidence"]
    valid = bool(
        run["stageValidation"]["valid"] and run["execution"].get("processStarted")
        and run["execution"].get("observation", {}).get("valid")
        and run["execution"].get("stageIntegrity", {}).get("valid")
        and not run["execution"].get("liveExternalAgentExecuted")
        and evidence.get("terminalStatus") == "FAIL" and not evidence.get("claimEligible")
        and run["retained"]["validation"]["valid"]
    )
    return {
        "valid": valid, "purpose": "Tier A protocol exercise only; no repair is performed and no AI agent is executed.",
        "expectedTerminalStatus": "FAIL", "terminalStatus": evidence.get("terminalStatus"),
        "processStarted": run["execution"].get("processStarted"),
        "observationValid": run["execution"].get("observation", {}).get("valid"),
        "stageIntegrityValid": run["execution"].get("stageIntegrity", {}).get("valid"),
        "liveExternalAgentExecuted": run["execution"].get("liveExternalAgentExecuted"),
        "claimEligible": evidence.get("claimEligible"), "retainedEvidence": run["retained"]["relativePath"],
        "evidenceDigest": evidence.get("evidenceDigest"), "validation": run["retained"]["validation"],
    }


def run_success_matrix(results: Path, stage_root: Path) -> dict[str, Any]:
    def one(spec: tuple[str, tuple[str, str, str]]) -> dict[str, Any]:
        fixture_id, (case_id, route, authority) = spec
        descriptor = readiness_descriptor("success", descriptor_id=f"{fixture_id.lower()}-{route}", writes=True)
        descriptor_path = results / f"readiness/executors/{fixture_id}.json"
        write_json(descriptor_path, descriptor)
        run = build_and_execute(
            case_id=case_id, attempt_id=f"{fixture_id}-{case_id}-success-01", descriptor=descriptor,
            descriptor_path=descriptor_path, stage_root=stage_root, results_root=results,
            destination=results / f"readiness/success/{fixture_id}",
        )
        evidence = run["retained"]["evidence"]
        valid = bool(
            evidence.get("terminalStatus") == "PASS" and run["evaluation"].get("passed")
            and run["execution"].get("stageIntegrity", {}).get("valid")
            and run["retained"]["observationConsistency"].get("consistent")
            and run["retained"]["secretHygiene"].get("valid")
            and run["retained"]["validation"].get("valid")
            and not evidence.get("liveExternalAgentExecuted") and not evidence.get("claimEligible")
            and not run["metrics"].get("sourceRepositoryPythonPathUsed")
        )
        return {
            "id": fixture_id, "caseId": case_id, "route": route, "authority": authority,
            "terminalStatus": evidence.get("terminalStatus"), "valid": valid,
            "liveExternalAgentExecuted": evidence.get("liveExternalAgentExecuted"),
            "claimEligible": evidence.get("claimEligible"), "stageIntegrity": run["execution"].get("stageIntegrity"),
            "observationConsistency": run["retained"]["observationConsistency"],
            "secretHygiene": run["retained"]["secretHygiene"], "metrics": run["metrics"],
            "retainedEvidence": run["retained"]["relativePath"], "evidenceDigest": evidence.get("evidenceDigest"),
        }

    items = sorted(_parallel(SUCCESS_CASES.items(), one), key=lambda item: item["id"])
    return {"valid": all(item["valid"] for item in items), "fixtures": items, "summary": {"fixtures": len(items), "passed": sum(item["valid"] for item in items), "failed": sum(not item["valid"] for item in items)}}


def run_fault_matrix(results: Path, stage_root: Path, work: Path) -> dict[str, Any]:
    faults = [
        ("F001", "missing-executable", "EXECUTOR_ERROR", False),
        ("F002", "nonzero", "FAIL", False),
        ("F003", "timeout-after-mutation", "TIMEOUT", True),
        ("F004", "tamper-task", "FAIL", False),
        ("F005", "wrong-authority", "FAIL", True),
        ("F006", "generated-output", "FAIL", True),
        ("F007", "zero-exit-no-repair", "FAIL", True),
        ("F008", "close-failure", "FAIL", True),
        ("F009", "malformed-observation", "FAIL", False),
        ("F010", "secret-observation", "FAIL", False),
    ]

    def one(spec: tuple[str, str, str, bool]) -> dict[str, Any]:
        fault_id, mode, expected, writes = spec
        canary = work / f"{fault_id}-child-canary.txt" if mode == "timeout-after-mutation" else None
        if canary:
            canary.unlink(missing_ok=True)
        if mode == "missing-executable":
            descriptor = base_descriptor(["definitely-not-an-aixem-agent", "--task", "{task}"], descriptor_id=fault_id.lower(), writes=False, wall_time=2)
        else:
            descriptor = readiness_descriptor(mode, descriptor_id=fault_id.lower(), writes=writes, wall_time=1 if mode == "timeout-after-mutation" else 120, child_canary=canary)
        descriptor_path = results / f"readiness/executors/{fault_id}.json"
        write_json(descriptor_path, descriptor)
        run = build_and_execute(
            case_id="L008", attempt_id=f"{fault_id}-L008-01", descriptor=descriptor,
            descriptor_path=descriptor_path, stage_root=stage_root, results_root=results,
            destination=results / f"readiness/faults/{fault_id}",
        )
        evidence = run["retained"]["evidence"]
        if canary is not None:
            time.sleep(2.2)
        child_cleaned = not canary.exists() if canary is not None else True
        extra_valid = True
        if mode == "tamper-task":
            extra_valid = not bool(run["execution"].get("stageIntegrity", {}).get("valid"))
        if mode == "malformed-observation":
            extra_valid = not bool(run["execution"].get("observation", {}).get("valid"))
        if mode == "secret-observation":
            retained_text = "".join(path.read_text(encoding="utf-8", errors="replace") for path in (results / f"readiness/faults/{fault_id}").rglob("*") if path.is_file())
            extra_valid = "sk-fixture-secret-1234567890" not in retained_text and run["retained"]["secretHygiene"].get("valid")
        valid = bool(
            evidence.get("terminalStatus") == expected and run["retained"]["validation"].get("valid")
            and not evidence.get("liveExternalAgentExecuted") and not evidence.get("claimEligible")
            and child_cleaned and extra_valid
        )
        return {
            "id": fault_id, "mode": mode, "expectedTerminalStatus": expected,
            "terminalStatus": evidence.get("terminalStatus"), "valid": valid,
            "childProcessCleaned": child_cleaned,
            "stageIntegrityValid": run["execution"].get("stageIntegrity", {}).get("valid"),
            "processLifecycle": run["execution"].get("processLifecycle"),
            "observationValid": run["execution"].get("observation", {}).get("valid"),
            "observationConsistency": run["retained"]["observationConsistency"],
            "secretHygiene": run["retained"]["secretHygiene"],
            "retainedEvidence": run["retained"]["relativePath"], "evidenceDigest": evidence.get("evidenceDigest"),
        }

    items = sorted(_parallel(faults, one, workers=4), key=lambda item: item["id"])
    return {"valid": all(item["valid"] for item in items), "faults": items, "summary": {"faults": len(items), "passed": sum(item["valid"] for item in items), "failed": sum(not item["valid"] for item in items)}}


def invariant_fairness_audit(stage_root: Path) -> dict[str, Any]:
    def one(case: Path) -> dict[str, Any]:
        stage = stage_root / f"fairness-{case.name}"
        shutil.rmtree(stage, ignore_errors=True)
        build_stage(ROOT, case, f"{case.name}-fairness-01", stage)
        result = audit_invariant_basis(
            read_json(stage / "task/agent-task.json"), read_json(case / "evaluator/invariants.json"),
            reference_root=stage / "reference", schema_file=SCHEMAS / "aixem-agent-evaluation-invariant-1.schema.json",
        )
        return {"id": case.name, **result}

    items = sorted(_parallel(case_roots(), one), key=lambda item: item["id"])
    return {"valid": all(item["valid"] for item in items), "cases": items, "summary": {"cases": len(items), "passed": sum(item["valid"] for item in items), "failed": sum(not item["valid"] for item in items)}}


def route_readiness_matrix(success_matrix: Mapping[str, Any]) -> dict[str, Any]:
    live_case_routes: dict[str, list[str]] = {}
    for case in case_roots():
        task = read_json(case / "agent-task.json")
        live_case_routes.setdefault(str(task["activeRoute"]), []).append(case.name)
    success_routes = {str(item["route"]): str(item["id"]) for item in success_matrix.get("fixtures", []) if item.get("valid")}
    rows: list[dict[str, Any]] = []
    for route in AUTHORING_ROUTES:
        packet_path = ROOT / f"docs/_meta/generated/task-packets/{route}.json"
        packet = read_json(packet_path)
        kind = str(packet.get("kind"))
        writes = packet.get("writes") or {}
        authority = list(writes.get("authority", []))
        child_routes = [str(item.get("route")) for item in packet.get("stages", []) or []]
        packet_valid = packet.get("id") == route and packet_path.is_file()
        route_index = read_json(ROOT / "docs/_meta/generated/route-index.json")
        route_index_valid = route in {str(item.get("id")) for item in route_index.get("routes", [])}
        if kind == "composite":
            coverage = "composite-child-covered"
            covered = bool(child_routes) and all((child in live_case_routes) or (child in {"render-review", "validate-project"}) for child in child_routes)
        elif authority:
            coverage = "live-case-and-fixture" if route in success_routes else "live-case-covered"
            covered = route in live_case_routes and route in success_routes
        else:
            coverage = "non-authoritative-harness-entry"
            covered = route in {"route-project-nets", "render-review", "validate-project"} and authority == [] and bool(packet.get("validators"))
        row_valid = bool(packet_valid and route_index_valid and covered)
        rows.append({
            "route": route, "kind": kind, "writeAuthority": authority,
            "liveCases": sorted(live_case_routes.get(route, [])), "readinessFixture": success_routes.get(route),
            "childRoutes": child_routes, "coverage": coverage,
            "prepareCheckCloseSupport": bool(packet.get("validators")),
            "referencePackClosure": True, "validatorCount": len(packet.get("validators", [])),
            "routeIndexEntry": route_index_valid, "valid": row_valid,
        })
    return {"valid": len(rows) == len(AUTHORING_ROUTES) and all(item["valid"] for item in rows), "routes": rows, "summary": {"routes": len(rows), "passed": sum(item["valid"] for item in rows), "failed": sum(not item["valid"] for item in rows)}}


def run_tier_a(results: Path, work: Path) -> dict[str, Any]:
    corpus = audit_corpus()
    stages = deterministic_stage_audit(work / "deterministic-stages")
    protocol = run_protocol_fixture(results, work / "protocol-stages")
    success = run_success_matrix(results, work / "success-stages")
    faults = run_fault_matrix(results, work / "fault-stages", work)
    fairness = invariant_fairness_audit(work / "fairness-stages")
    routes = route_readiness_matrix(success)
    valid = bool(corpus["valid"] and stages["valid"] and protocol["valid"] and success["valid"] and faults["valid"] and fairness["valid"] and routes["valid"])
    identity = corpus_identity()
    payload = {
        "schema": "https://schemas.aixem.org/validation/agent-eval-3-tier-a/1", "formatVersion": "1.1",
        "release": repository_release(), "repositoryRelease": repository_release(), "corpus": identity,
        "generatedAt": FIXED_TIME, "executionMode": "deterministic-pre-live-readiness",
        "valid": valid, "preLiveReadiness": valid, "externalTierBExecuted": False,
        "liveExternalAgentExecuted": False, "claimAuthorized": False,
        "corpusAudit": corpus, "stageAudit": stages, "protocolFixture": protocol,
        "successMatrix": success, "faultMatrix": faults, "invariantFairness": fairness,
        "routeReadiness": routes,
        "summary": {
            "cases": 12, "corpusCasesValid": corpus["summary"]["valid"],
            "deterministicStages": stages["summary"]["passed"], "protocolFixtureValid": protocol["valid"],
            "successFixtures": success["summary"], "faultFixtures": faults["summary"],
            "fairInvariantCases": fairness["summary"]["passed"], "readyRoutes": routes["summary"]["passed"],
        },
        "claim": "Pre-live readiness validates deterministic platform boundaries only; no external AI agent was executed.",
    }
    write_json(results / "tier-a-results.json", payload)
    stage_integrity_valid = bool(
        all(item.get("stageIntegrity", {}).get("valid") is True for item in success.get("fixtures", []))
        and all(
            (item.get("stageIntegrityValid") is False) if item.get("mode") == "tamper-task"
            else (item.get("stageIntegrityValid") is True)
            for item in faults.get("faults", [])
        )
    )
    timeout_fault = next((item for item in faults["faults"] if item["mode"] == "timeout-after-mutation"), {})
    readiness = {
        "schema": "https://schemas.aixem.org/validation/pre-live-readiness/1", "formatVersion": "1.0",
        "release": repository_release(), "generatedAt": FIXED_TIME, "preLiveReadiness": valid,
        "runnerPortability": {"resultsRoot": str(results), "workRoot": str(work), "locationIndependent": True},
        "provenance": {"repositoryRelease": repository_release(), "corpus": identity, "tierAClock": "fixed-deterministic", "futureTierBClock": "actual-utc"},
        "stageIntegrity": {"valid": stage_integrity_valid},
        "processLifecycle": {"valid": bool(timeout_fault.get("childProcessCleaned")), "details": timeout_fault.get("processLifecycle")},
        "secretHygiene": {"valid": all(item["secretHygiene"]["valid"] for item in [*success["fixtures"], *faults["faults"]])},
        "observationConsistency": {"valid": all(item["observationConsistency"]["consistent"] for item in success["fixtures"])},
        "subprocessSuccessMatrix": success, "subprocessFaultMatrix": faults,
        "invariantFairness": fairness,
        "referencePackClosure": {"valid": success["valid"], "sourceRepositoryPythonPathUsed": any(item["metrics"].get("sourceRepositoryPythonPathUsed") for item in success["fixtures"])},
        "routeReadiness": routes,
        "platformBaseline": {"fixtures": [{"id": item["id"], **item["metrics"]} for item in success["fixtures"]]},
        "externalTierBExecuted": False, "liveExternalAgentExecuted": False,
        "liveClaimAuthorized": False, "valid": valid,
    }
    write_json(results / "readiness/readiness-report.json", readiness)
    return payload


def unavailable_tier_b_status() -> dict[str, Any]:
    available = {name: shutil.which(name) for name in EXTERNAL_RUNTIME_NAMES if shutil.which(name)}
    return {
        "schema": "https://schemas.aixem.org/validation/agent-eval-3-tier-b-status/1", "formatVersion": "1.1",
        "release": repository_release(), "repositoryRelease": repository_release(), "corpus": corpus_identity(),
        "generatedAt": FIXED_TIME, "clockMode": "not-executed", "executionMode": "live-external-agent",
        "executed": False, "attempts": 0, "liveExternalAgentExecuted": False,
        "claimAuthorized": False, "denominatorIntegrity": True, "availableRuntimeProbe": available,
        "reason": "No explicit external-AI executor descriptor was supplied; no live Tier B attempt was fabricated.",
        "claim": "No live external-agent execution occurred in this environment.", "valid": True,
    }


def run_external_tier_b(executor_path: Path, attempts_per_case: int, results: Path, work: Path) -> dict[str, Any]:
    descriptor = validate_executor_descriptor(read_json(executor_path), SCHEMAS / "aixem-agent-executor-1.schema.json")
    if descriptor.get("agentClass") != "external-ai":
        raise RuntimeError("Tier B requires agentClass=external-ai")
    descriptor_copy = results / "tier-b/executor.json"
    write_json(descriptor_copy, descriptor)
    expected_ids: list[str] = []
    evidences: list[dict[str, Any]] = []
    process_started = 0
    for case in case_roots():
        for attempt_index in range(1, attempts_per_case + 1):
            attempt_id = f"{case.name}-a{attempt_index:02d}"
            expected_ids.append(attempt_id)
            run = build_and_execute(
                case_id=case.name, attempt_id=attempt_id, descriptor=descriptor,
                descriptor_path=descriptor_copy, stage_root=work / "tier-b-stages", results_root=results,
                destination=results / "tier-b/attempts" / attempt_id, generated_at=utc_now(),
            )
            process_started += bool(run["execution"].get("processStarted"))
            if not run["retained"]["validation"]["valid"]:
                raise RuntimeError(f"invalid retained live-run evidence for {attempt_id}: {run['retained']['validation']['errors']}")
            evidences.append(run["retained"]["evidence"])
    attempt_set = build_attempt_set(
        release=repository_release(), executor_descriptor=descriptor,
        attempts=evidences, expected_attempt_ids=expected_ids, generated_at=utc_now(),
    )
    write_json(results / "tier-b/attempt-set.json", attempt_set)
    return {
        "schema": "https://schemas.aixem.org/validation/agent-eval-3-tier-b-status/1", "formatVersion": "1.1",
        "release": repository_release(), "repositoryRelease": repository_release(), "corpus": corpus_identity(),
        "generatedAt": utc_now(), "clockMode": "actual-utc", "executionMode": "live-external-agent",
        "executed": bool(process_started), "attempts": len(evidences), "processesStarted": process_started,
        "liveExternalAgentExecuted": attempt_set["liveExternalAgentExecuted"],
        "claimAuthorized": bool(attempt_set["liveExternalAgentExecuted"] and attempt_set["denominatorIntegrity"]),
        "denominatorIntegrity": attempt_set["denominatorIntegrity"], "attemptSet": "tier-b/attempt-set.json",
        "summary": attempt_set["summary"], "claim": attempt_set["claim"], "valid": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=CORPUS / "results")
    parser.add_argument("--work", type=Path)
    parser.add_argument("--external-executor", type=Path)
    parser.add_argument("--attempts-per-case", type=int, default=3)
    parser.add_argument("--tier-a-only", action="store_true")
    args = parser.parse_args()
    if args.attempts_per_case < 1:
        parser.error("--attempts-per-case must be at least 1")
    results = prepare_output_root(args.results, "results")
    start = time.perf_counter()
    if args.work:
        work_context = None
        work = prepare_output_root(args.work, "work")
    else:
        work_context = tempfile.TemporaryDirectory(prefix="aixem-agent-evals-3-")
        work = Path(work_context.name)
    try:
        tier_a = run_tier_a(results, work)
        tier_b = unavailable_tier_b_status() if args.tier_a_only or not args.external_executor else run_external_tier_b(args.external_executor.resolve(), args.attempts_per_case, results, work)
        write_json(results / "tier-b-status.json", tier_b)
        summary = {
            "schema": "https://schemas.aixem.org/validation/agent-eval-3-summary/1", "formatVersion": "1.1",
            "release": repository_release(), "repositoryRelease": repository_release(), "corpus": corpus_identity(),
            "generatedAt": FIXED_TIME if not tier_b["executed"] else utc_now(),
            "tierAValid": tier_a["valid"], "preLiveReadiness": tier_a["valid"],
            "tierBExecuted": tier_b["executed"], "liveExternalAgentExecuted": tier_b["liveExternalAgentExecuted"],
            "liveClaimAuthorized": tier_b["claimAuthorized"], "durationSeconds": round(time.perf_counter() - start, 6),
            "engineeringStatus": "LIVE_TIER_B_EXECUTED" if tier_b["liveExternalAgentExecuted"] else "PRE_LIVE_READINESS_PASS_TIER_B_PENDING",
            "valid": bool(tier_a["valid"] and tier_b["valid"]),
        }
        write_json(results / "summary.json", summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if summary["valid"] else 2
    finally:
        if work_context is not None:
            work_context.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
