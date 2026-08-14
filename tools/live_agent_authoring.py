#!/usr/bin/env python3
"""Build, execute, score, and retain AIXEM 0.5.6 cold-start agent attempts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.change_scope import canonical_json_bytes  # noqa: E402
from agent.cold_start_stage import build_stage, validate_stage  # noqa: E402
from agent.invariant_scorer import score_invariants  # noqa: E402
from agent.live_executor import execute_subprocess  # noqa: E402
from agent.live_run import build_attempt_set, build_live_run_evidence, validate_live_run  # noqa: E402
from agent.observation import validate_observation_log  # noqa: E402

RELEASE = "AIXEM-SRP-0.5.6-2026-08-12"
FIXED_TIME = "2026-08-12T00:00:00Z"
SCHEMAS = ROOT / "docs" / "specifications" / "schemas" / "agent"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _copy_if_present(source: Path | None, destination: Path) -> Path | None:
    if source is None or not source.is_file():
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def _find_run_record(stage: Path) -> Path | None:
    candidates = sorted((stage / "state").rglob("authoring-run-record.json"))
    return candidates[-1] if candidates else None


def cmd_build_stage(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    manifest = build_stage(ROOT, args.case, args.attempt_id, args.output)
    return 0, {"valid": True, "stage": str(args.output), "manifest": manifest}


def cmd_validate_stage(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    result = validate_stage(args.stage, ROOT)
    return (0 if result["valid"] else 2), result


def cmd_validate_observation(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    descriptor = read_json(args.executor) if args.executor else {}
    result = validate_observation_log(
        args.log,
        SCHEMAS / "aixem-agent-observation-event-1.schema.json",
        declared_coverage=descriptor.get("observationCapability", {}),
    )
    return (0 if result["valid"] else 2), result


def cmd_execute(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    descriptor = read_json(args.executor)
    result = execute_subprocess(
        descriptor,
        args.stage,
        executor_schema_file=SCHEMAS / "aixem-agent-executor-1.schema.json",
        observation_schema_file=SCHEMAS / "aixem-agent-observation-event-1.schema.json",
    )
    return (0 if result["status"] == "COMPLETED" else 2), result


def cmd_score(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    result = score_invariants(
        args.workspace,
        read_json(args.invariants),
        read_json(args.stage_manifest),
        schema_file=SCHEMAS / "aixem-agent-evaluation-invariant-1.schema.json",
    )
    if args.output:
        write_json(args.output, result)
    return (0 if result["passed"] else 2), result


def cmd_run_attempt(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    stage_validation = validate_stage(args.stage, ROOT)
    descriptor = read_json(args.executor)
    if stage_validation["valid"]:
        execution = execute_subprocess(
            descriptor,
            args.stage,
            executor_schema_file=SCHEMAS / "aixem-agent-executor-1.schema.json",
            observation_schema_file=SCHEMAS / "aixem-agent-observation-event-1.schema.json",
        )
    else:
        execution = {
            "status": "EXECUTOR_ERROR", "processStarted": False, "externalProcessStarted": False,
            "liveExternalAgentExecuted": False, "returnCode": None,
            "error": "invalid cold-start stage", "observation": {"valid": False, "events": 0, "errors": stage_validation["errors"]},
        }

    stage_manifest = read_json(args.stage / "stage-manifest.json")
    evaluation = score_invariants(
        args.stage / "workspace",
        read_json(args.invariants),
        stage_manifest,
        schema_file=SCHEMAS / "aixem-agent-evaluation-invariant-1.schema.json",
    )
    retained = args.output.resolve()
    retained.mkdir(parents=True, exist_ok=True)
    task_path = _copy_if_present(args.stage / "task" / "agent-task.json", retained / "agent-task.json")
    stage_manifest_path = _copy_if_present(args.stage / "stage-manifest.json", retained / "stage-manifest.json")
    descriptor_path = _copy_if_present(args.executor, retained / "executor.json")
    observation_path = _copy_if_present(args.stage / "state" / "observation-log.jsonl", retained / "observation-log.jsonl")
    source_record = _find_run_record(args.stage)
    run_record_path = _copy_if_present(source_record, retained / "authoring-run-record.json")
    evaluation_path = retained / "evaluator-result.json"
    write_json(evaluation_path, evaluation)
    assert task_path and stage_manifest_path and descriptor_path
    evidence = build_live_run_evidence(
        release=RELEASE,
        generated_at=FIXED_TIME,
        task_path=task_path,
        stage_manifest_path=stage_manifest_path,
        executor_descriptor_path=descriptor_path,
        observation_log_path=observation_path,
        execution=execution,
        evaluation_path=evaluation_path,
        run_record_path=run_record_path,
        stage_validation=stage_validation,
    )
    evidence_path = retained / "live-run-evidence.json"
    write_json(evidence_path, evidence)
    schema_result = validate_live_run(evidence, SCHEMAS / "aixem-agent-live-run-1.schema.json")
    result = {
        "valid": schema_result["valid"],
        "terminalStatus": evidence["terminalStatus"],
        "liveExternalAgentExecuted": evidence["liveExternalAgentExecuted"],
        "claimEligible": evidence["claimEligible"],
        "evidence": str(evidence_path),
        "evidenceDigest": evidence["evidenceDigest"],
        "execution": execution,
        "evaluation": evaluation["summary"],
        "schemaValidation": schema_result,
    }
    return (0 if evidence["terminalStatus"] == "PASS" and schema_result["valid"] else 2), result


def cmd_aggregate(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    descriptor = read_json(args.executor)
    attempts = [read_json(path) for path in args.attempt]
    expected = args.expected_attempt_id or [str(item["attemptId"]) for item in attempts]
    result = build_attempt_set(
        release=RELEASE,
        executor_descriptor=descriptor,
        attempts=attempts,
        expected_attempt_ids=expected,
    )
    write_json(args.output, result)
    return 0, result


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-stage")
    build.add_argument("--case", type=Path, required=True)
    build.add_argument("--attempt-id", required=True)
    build.add_argument("--output", type=Path, required=True)
    build.set_defaults(handler=cmd_build_stage)

    validate = sub.add_parser("validate-stage")
    validate.add_argument("--stage", type=Path, required=True)
    validate.set_defaults(handler=cmd_validate_stage)

    observe = sub.add_parser("validate-observation")
    observe.add_argument("--log", type=Path, required=True)
    observe.add_argument("--executor", type=Path)
    observe.set_defaults(handler=cmd_validate_observation)

    execute = sub.add_parser("execute")
    execute.add_argument("--stage", type=Path, required=True)
    execute.add_argument("--executor", type=Path, required=True)
    execute.set_defaults(handler=cmd_execute)

    score = sub.add_parser("score")
    score.add_argument("--workspace", type=Path, required=True)
    score.add_argument("--stage-manifest", type=Path, required=True)
    score.add_argument("--invariants", type=Path, required=True)
    score.add_argument("--output", type=Path)
    score.set_defaults(handler=cmd_score)

    run_attempt = sub.add_parser("run-attempt")
    run_attempt.add_argument("--stage", type=Path, required=True)
    run_attempt.add_argument("--executor", type=Path, required=True)
    run_attempt.add_argument("--invariants", type=Path, required=True)
    run_attempt.add_argument("--output", type=Path, required=True)
    run_attempt.set_defaults(handler=cmd_run_attempt)

    aggregate = sub.add_parser("aggregate")
    aggregate.add_argument("--executor", type=Path, required=True)
    aggregate.add_argument("--attempt", type=Path, action="append", required=True)
    aggregate.add_argument("--expected-attempt-id", action="append")
    aggregate.add_argument("--output", type=Path, required=True)
    aggregate.set_defaults(handler=cmd_aggregate)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        code, payload = args.handler(args)
    except Exception as exc:  # noqa: BLE001
        code, payload = 2, {"valid": False, "status": "ERROR", "error": str(exc)}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
