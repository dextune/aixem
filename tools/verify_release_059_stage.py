#!/usr/bin/env python3
"""Execute one bounded stage of an AIXEM 0.5.9 clean verification pass."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.verify_release_059 as v  # noqa: E402

TEST_WORK_ROOT = v.TEST_WORK_ROOT


def state_path(cycle: int) -> Path:
    return TEST_WORK_ROOT / f"run-{cycle:02d}" / "stage-state.json"


def load_state(cycle: int) -> dict:
    path = state_path(cycle)
    if not path.is_file():
        raise v.VerificationError(f"pass {cycle} stage state is missing")
    return v.read_json(path)


def save_state(cycle: int, state: dict) -> None:
    v.write_json(state_path(cycle), state)


def append_commands(state: dict, commands: list[dict]) -> None:
    state.setdefault("commands", []).extend(commands)


def prepare(cycle: int) -> None:
    if cycle == 1:
        shutil.rmtree(v.RUNS, ignore_errors=True)
        shutil.rmtree(TEST_WORK_ROOT, ignore_errors=True)
    cycle_dir = v.RUNS / f"run-{cycle:02d}"
    shutil.rmtree(cycle_dir, ignore_errors=True)
    shutil.rmtree(TEST_WORK_ROOT / f"run-{cycle:02d}", ignore_errors=True)
    cycle_dir.mkdir(parents=True, exist_ok=True)
    v.reset_generated_outputs()
    started = time.perf_counter()
    commands = []
    compile_files = [
        "implementation/schematic/authoring_integrity.py",
        "implementation/schematic/placement_assist.py",
        "implementation/agent/change_scope.py",
        "implementation/agent/diagnostics.py",
        "tools/placement_assist.py",
        "tools/validate_authoring_integrity.py",
        "tools/run_tests_059.py",
        "tools/verify_release_059.py",
        "tools/verify_release_059_stage.py",
        "tools/package_release_059.py",
    ]
    commands.append(v.run([sys.executable, "-m", "py_compile", *compile_files], label=f"pass {cycle} Python compilation", timeout=300))
    commands.append(v.run([sys.executable, "tools/docs/build_all.py"], label=f"pass {cycle} documentation build 1", timeout=1200))
    first = v.generated_map()
    commands.append(v.run([sys.executable, "tools/docs/build_all.py"], label=f"pass {cycle} documentation build 2", timeout=1200))
    second = v.generated_map()
    changed = sorted(path for path in set(first) | set(second) if first.get(path) != second.get(path))
    if changed:
        raise v.VerificationError(f"pass {cycle} generated output drift: {changed[:20]}")
    commands.append(v.run([sys.executable, "tools/docs/audit_repository_docs.py", "--require-redirects"], label=f"pass {cycle} document audit", timeout=900))
    commands.append(v.run([sys.executable, "tools/docs/validate_docs.py"], label=f"pass {cycle} documentation validation", timeout=900))
    commands.append(v.run([sys.executable, "tools/docs/authoring_validation.py"], label=f"pass {cycle} authoring validation", timeout=900))
    state = {
        "cycle": cycle,
        "startedAtMonotonic": started,
        "commands": commands,
        "reproducibility": {"valid": True, "files": len(second), "changed": []},
        "stages": {"prepare": "PASS"},
    }
    save_state(cycle, state)
    print(json.dumps({"cycle": cycle, "stage": "prepare", "valid": True, "generatedFiles": len(second)}, sort_keys=True))


def agent3(cycle: int) -> None:
    state = load_state(cycle)
    commands = [
        v.run([sys.executable, "tools/build_agent_evals_3.py"], label=f"pass {cycle} Agent Evaluation 3 corpus build", timeout=900),
        v.run([sys.executable, "tools/run_agent_evals_3.py", "--tier-a-only"], label=f"pass {cycle} Agent Evaluation 3 Tier A", timeout=3600),
    ]
    append_commands(state, commands)
    state.setdefault("stages", {})["agent3"] = "PASS"
    save_state(cycle, state)
    print(json.dumps({"cycle": cycle, "stage": "agent3", "valid": True}, sort_keys=True))


def agent2(cycle: int) -> None:
    state = load_state(cycle)
    commands = [v.run([sys.executable, "tools/run_agent_evals_2.py"], label=f"pass {cycle} Agent Evaluation 2", timeout=1800)]
    append_commands(state, commands)
    state.setdefault("stages", {})["agent2"] = "PASS"
    save_state(cycle, state)
    print(json.dumps({"cycle": cycle, "stage": "agent2", "valid": True}, sort_keys=True))

def preflight(cycle: int) -> None:
    state = load_state(cycle)
    command = v.prepare_repository_self_test(cycle)
    append_commands(state, [command])
    state.setdefault("stages", {})["preflight"] = "PASS"
    save_state(cycle, state)
    print(json.dumps({"cycle": cycle, "stage": "preflight", "valid": True}, sort_keys=True))


def merge_tests(cycle: int, shard_count: int) -> None:
    state = load_state(cycle)
    paths = [TEST_WORK_ROOT / f"run-{cycle:02d}" / f"test-shard-{index}.json" for index in range(shard_count)]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise v.VerificationError(f"pass {cycle} missing test shards: {missing}")
    command = v.run(
        [sys.executable, "tools/run_tests_059.py", "--merge-shards", *[str(path) for path in paths], "--output", "validation/test-results.json"],
        label=f"pass {cycle} repository test aggregation",
        timeout=300,
    )
    result = v.read_json(v.VALIDATION / "test-results.json")
    if result.get("successful") is not True:
        raise v.VerificationError(f"pass {cycle} repository test aggregation failed")
    retained_dir = v.RUNS / f"run-{cycle:02d}"
    retained_dir.mkdir(parents=True, exist_ok=True)
    for source in paths:
        shutil.copy2(source, retained_dir / source.name)
    shard_commands = []
    for path in paths:
        payload = v.read_json(path)
        shard_commands.append({
            "label": f"pass {cycle} {path.stem}",
            "command": payload.get("modules", [{}])[0].get("command", ["tools/run_tests_059.py"]),
            "returnCode": 0,
            "durationSeconds": payload.get("durationSeconds", 0.0),
            "stdoutTail": "",
            "stderrTail": "",
            "status": "PASS",
            "valid": True,
            "testsRun": payload.get("testsRun"),
            "moduleCount": payload.get("moduleCount"),
        })
    append_commands(state, shard_commands + [command])
    state["tests"] = result
    state.setdefault("stages", {})["tests"] = "PASS"
    save_state(cycle, state)
    print(json.dumps({"cycle": cycle, "stage": "tests", "valid": True, "testsRun": result.get("testsRun"), "modules": result.get("moduleCount")}, sort_keys=True))


def corpora(cycle: int) -> None:
    state = load_state(cycle)
    commands = [
        v.run([sys.executable, "tools/validate_symbol_corpus.py", "--all", "--repeat", "3", "--emit-report"], label=f"pass {cycle} symbol and Static 2D corpus", timeout=3600),
        v.run([sys.executable, "tools/validate_hierarchical_corpus.py", "--repeats", "3"], label=f"pass {cycle} hierarchical corpus", timeout=3600),
        v.run([sys.executable, "tools/validate_reference_viewer_corpus.py", "--repeats", "3", "--screenshots"], label=f"pass {cycle} Viewer corpus", timeout=3600),
    ]
    append_commands(state, commands)
    state.setdefault("stages", {})["corpora"] = "PASS"
    save_state(cycle, state)
    print(json.dumps({"cycle": cycle, "stage": "corpora", "valid": True}, sort_keys=True))


def close(cycle: int) -> None:
    state = load_state(cycle)
    required = {"prepare", "agent3", "agent2", "preflight", "tests", "corpora"}
    observed = {name for name, status in state.get("stages", {}).items() if status == "PASS"}
    if not required.issubset(observed):
        raise v.VerificationError(f"pass {cycle} incomplete stages: {sorted(required-observed)}")
    test_result = state["tests"]
    checks = [
        v.check("integrated-plan-and-structure", **v._check_args(v.plan_and_structure_check(), "Integrated plan mapping and authoring structure are closed.")),
        v.check("documentation-relationships", **v._check_args(v.documentation_relationship_check(), "Canonical documents, routes, snippets, and repository relationships are closed.")),
        v.check("agent-pre-live-boundary", **v._check_args(v.agent_results_check(), "Agent Tier A/readiness is green and external Tier B remains unexecuted.")),
        v.check("corpus-regression", **v._check_args(v.corpus_check(), "Symbol, hierarchy, and Viewer corpora are green.")),
        v.check("protected-baseline", **v._check_args(v.protected_baseline_check(cycle), "Protected 0.5.8.1 schema/renderer/Viewer/drawing baseline is unchanged.")),
        v.check("repository-tests", bool(test_result.get("successful")), "Complete isolated repository test inventory passed.", testsRun=test_result.get("testsRun"), modules=test_result.get("moduleCount"), failedModules=test_result.get("failedModules")),
        v.check("generated-reproducibility", state["reproducibility"]["valid"], "Two clean documentation builds produced identical generated digests.", files=state["reproducibility"].get("files"), changed=state["reproducibility"].get("changed", [])),
    ]
    valid = all(item.get("valid") is True for item in checks)
    if not valid:
        errors = [error for item in checks for error in item.get("errors", [])]
        raise v.VerificationError(f"pass {cycle} close failed: {errors}")
    summary = {
        "schema": "https://schemas.aixem.org/validation/verification-pass/1",
        "formatVersion": "1.0",
        "release": v.RELEASE_ID,
        "generatedAt": v.FIXED_TIME,
        "pass": cycle,
        "cleanStart": True,
        "status": "PASS",
        "valid": True,
        "durationSeconds": round(sum(float(item.get("durationSeconds", 0.0)) for item in state.get("commands", [])), 6),
        "tests": {"testsRun": test_result.get("testsRun"), "moduleCount": test_result.get("moduleCount"), "failedModules": test_result.get("failedModules")},
        "commands": state.get("commands", []),
        "checks": checks,
        "externalTierBExecuted": False,
        "liveExternalAgentExecuted": False,
        "liveClaimAuthorized": False,
        "errors": [],
    }
    cycle_dir = v.RUNS / f"run-{cycle:02d}"
    v.write_json(cycle_dir / "summary.json", summary)
    v.write_text(cycle_dir / "report.md", v.render_cycle_report(summary))
    v.copy_cycle_snapshot(cycle_dir)
    state.setdefault("stages", {})["close"] = "PASS"
    save_state(cycle, state)
    print(json.dumps({"cycle": cycle, "stage": "close", "valid": True, "testsRun": test_result.get("testsRun")}, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycle", type=int, required=True)
    parser.add_argument("--stage", choices=("prepare", "agent3", "agent2", "preflight", "merge-tests", "corpora", "close"), required=True)
    parser.add_argument("--shard-count", type=int, default=8)
    args = parser.parse_args()
    try:
        {"prepare": prepare, "agent3": agent3, "agent2": agent2, "preflight": preflight, "corpora": corpora, "close": close}.get(args.stage, lambda cycle: merge_tests(cycle, args.shard_count))(args.cycle)
        return 0
    except Exception as exc:  # fail closed with one stage-local error
        print(f"[verify-059-stage] FAIL {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
