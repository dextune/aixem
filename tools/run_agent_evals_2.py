#!/usr/bin/env python3
"""Run AIXEM Agent Evaluation 2 Tier A and report Tier B truthfully."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
from typing import Any

import agent_authoring as authoring_harness

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "agent_authoring.py"
CORPUS = ROOT / "validation" / "agent-evals-2"
RESULTS = CORPUS / "results"
FIXED_TIME = "2026-08-11T00:00:00Z"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical(value), encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256();
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def project_file(workspace: Path) -> Path:
    direct = sorted(workspace.glob("*.aixproj.json"))
    if len(direct) != 1:
        raise RuntimeError(f"expected exactly one top-level project in {workspace}, got {len(direct)}")
    return direct[0]


def stable_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def refresh_locks(workspace: Path) -> None:
    """Refresh symbol/library/source/layout digests after an intentional start-state mutation."""
    project_path = project_file(workspace)
    project = read_json(project_path)
    project_root = project_path.parent
    # Library asset locks.
    for library_path in sorted(workspace.rglob("*.aixlib.json")):
        if any(part in {"render", "evidence"} for part in library_path.relative_to(workspace).parts):
            continue
        library = read_json(library_path)
        changed = False
        for component in library.get("library", {}).get("components", []):
            for presentation in component.get("presentations", []):
                asset = presentation.get("asset", {})
                rel = asset.get("path")
                if not rel:
                    continue
                target = (project_root / PurePosixPath(str(rel))).resolve()
                if target.is_file():
                    observed = sha256_file(target)
                    if asset.get("digest") != observed:
                        asset["digest"] = observed; changed = True
        if changed:
            stable_json(library_path, library)
    body = project.get("project", {})
    for ref in body.get("libraries", []):
        target = (project_root / PurePosixPath(ref["path"])).resolve()
        if target.is_file(): ref["digest"] = sha256_file(target)
    if project.get("schema", "").endswith("/aixproj/2"):
        for sheet in body.get("sheets", []):
            for key in ("source", "layout"):
                target = (project_root / PurePosixPath(sheet[key]["path"])).resolve()
                if target.is_file(): sheet[key]["digest"] = sha256_file(target)
    else:
        for key in ("source", "layout"):
            target = (project_root / PurePosixPath(body[key]["path"])).resolve()
            if target.is_file(): body[key]["digest"] = sha256_file(target)
    stable_json(project_path, project)


def mutate(case: dict[str, Any], workspace: Path) -> None:
    kind = case.get("mutation")
    if not kind:
        return
    if kind == "broken-lead-port":
        source = workspace / "fixtures/broken-lead-port.aixsym.json"
        target = workspace / "library/electronics/authoring/repaired-resistor.aixsym.json"
        broken = read_json(source)
        # Preserve the active presentation identity so this start state isolates
        # the intended lead/port defect instead of creating an unrelated binding failure.
        broken["symbol"]["id"] = "authoring:resistor"
        stable_json(target, broken); refresh_locks(workspace); return
    if kind == "duplicate-semantic-net":
        source = workspace / "two_terminal_route.aixem"
        source.write_text(source.read_text(encoding="utf-8") + "\nnet duplicate_signal = T1.1 T2.1\n", encoding="utf-8")
        refresh_locks(workspace); return
    if kind == "non-orthogonal-route":
        path = workspace / "two_terminal_route.aixlayout.json"; doc = read_json(path)
        doc["layout"]["connections"][0]["paths"][0]["via"][1][0] = 82.5
        stable_json(path, doc); refresh_locks(workspace); return
    if kind == "duplicate-project-member":
        path = project_file(workspace); doc = read_json(path)
        members = doc["project"]["projectNets"][0]["members"]
        members.append(dict(members[0])); stable_json(path, doc); return
    if kind == "field-body-overlap":
        path = workspace / "library/electronics/authoring/repaired-resistor.aixsym.json"; doc = read_json(path)
        for node in doc["symbol"].get("graphics", []):
            if node.get("type") == "text" and node.get("field") in {"reference", "value"}:
                node["x"] = 0; node["y"] = 0
        stable_json(path, doc); refresh_locks(workspace); return
    raise RuntimeError(f"unknown case mutation {kind!r}")


def restore_authoritative(fixture: Path, workspace: Path) -> None:
    suffixes = (".aixem", ".aixsym.json", ".aixlib.json", ".aixlayout.json", ".aixproj.json")
    for source in sorted(fixture.rglob("*")):
        if not source.is_file() or not source.name.endswith(suffixes):
            continue
        rel = source.relative_to(fixture); target = workspace / rel
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)


def run_cli(args: list[str], expected: set[int]) -> tuple[int, dict[str, Any], str]:
    proc = subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, text=True, capture_output=True, check=False, timeout=240)
    if proc.returncode not in expected:
        raise RuntimeError(f"agent_authoring {' '.join(args)} returned {proc.returncode}: {proc.stderr}\n{proc.stdout}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid CLI JSON: {proc.stdout}") from exc
    return proc.returncode, payload, proc.stderr


def execute_case(case: dict[str, Any], result_root: Path) -> dict[str, Any]:
    fixture = (ROOT / case["fixture"]).resolve()
    with tempfile.TemporaryDirectory(prefix=f"aixem-agent-eval-{case['id']}-") as td:
        temp = Path(td); workspace = temp / "workspace"; state = temp / "state"
        shutil.copytree(fixture, workspace)
        mutate(case, workspace)
        project_rel = project_file(workspace).relative_to(workspace).as_posix()
        _rc, prepared = authoring_harness.prepare(argparse.Namespace(
            workspace=workspace, route=case["entryRoute"], stage_route=None,
            task_id=case["id"].lower(), project=project_rel, state_dir=state,
        ))
        if _rc != 0:
            raise RuntimeError(f"prepare failed for {case['id']}: {prepared}")
        initial_codes = sorted({item["code"] for item in prepared["initialValidation"]["diagnostics"]})
        expected_codes = sorted(case.get("expectedInitialDiagnostics", []))
        missing = sorted(set(expected_codes) - set(initial_codes))
        if case.get("mutation"):
            restore_authoritative(fixture, workspace)
        check_rc, checked = authoring_harness.check(argparse.Namespace(state_dir=state))
        close_rc, closed = authoring_harness.close(argparse.Namespace(state_dir=state))
        run_record_path = state / "authoring-run-record.json"
        run_record = read_json(run_record_path) if run_record_path.is_file() else None
        retained_record = result_root / "runs" / f"{case['id']}-authoring-run-record.json"
        if run_record is not None:
            write_json(retained_record, run_record)
        pass_conditions = {
            "expectedInitialDiagnosticsObserved": not missing,
            "checkPassedAfterRepair": check_rc == 0 and bool(checked.get("valid")),
            "closePassed": close_rc == 0 and bool(closed.get("valid")),
            "zeroScopeViolations": bool(run_record and run_record["final"]["scopeViolationCount"] == 0),
            "zeroGeneratedOutputEdits": bool(run_record and run_record["final"]["generatedOutputEditCount"] == 0),
            "renderDeterministic": bool(run_record and run_record["final"]["determinism"].get("valid")),
            "liveClaimFalse": bool(run_record and not run_record["execution"]["liveExternalAgentExecuted"]),
        }
        return {
            "id": case["id"], "title": case["title"], "status": "pass" if all(pass_conditions.values()) else "fail",
            "executionMode": "deterministic-harness-replay", "liveExternalAgentExecuted": False,
            "entryRoute": case["entryRoute"], "mutation": case.get("mutation"),
            "expectedInitialDiagnostics": expected_codes, "observedInitialDiagnostics": initial_codes,
            "missingExpectedDiagnostics": missing, "passConditions": pass_conditions,
            "iterations": len(run_record.get("iterations", [])) if run_record else 0,
            "recordDigest": run_record.get("recordDigest") if run_record else None,
            "retainedRunRecord": retained_record.relative_to(result_root).as_posix() if run_record else None,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=RESULTS)
    parser.add_argument("--tier-b-command", help="Reserved external executor command; requires a separately supplied cold-start corpus and is not run against bundled completed fixtures.")
    parser.add_argument("--case", action="append", dest="case_ids", help="Run only the named A001-A012 case; repeatable.")
    parser.add_argument("--worker-case", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.tier_b_command:
        print("ERROR: Tier B requires a separately supplied cold-start corpus with hidden completed solutions; bundled fixtures are Tier A only.", file=sys.stderr)
        return 2
    manifest = read_json(CORPUS / "manifest.json")
    result_root = args.results.resolve(); result_root.mkdir(parents=True, exist_ok=True)
    (result_root / "runs").mkdir(parents=True, exist_ok=True)
    if args.worker_case:
        entry = next((item for item in manifest["cases"] if item["id"] == args.worker_case), None)
        if entry is None:
            print(f"ERROR: unknown Agent Evaluation 2 case {args.worker_case}", file=sys.stderr)
            return 2
        case = read_json(ROOT / entry["task"])
        item = execute_case(case, result_root)
        print(canonical(item), end="")
        return 0 if item["status"] == "pass" else 2
    results=[]
    selected = [item for item in manifest["cases"] if not args.case_ids or item["id"] in set(args.case_ids)]
    for entry in selected:
        case = read_json(ROOT / entry["task"])
        item = execute_case(case, result_root)
        results.append(item)
        write_json(result_root / "case-results" / f"{entry['id']}.json", item)
        print(f"{entry['id']}: {item['status']}", file=sys.stderr, flush=True)
    tier_a={
        "schema":"https://schemas.aixem.org/validation/agent-eval-2-results/1","formatVersion":"1.0",
        "release":"AIXEM-SRP-0.5.5-2026-08-11","generatedAt":FIXED_TIME,
        "tier":"A","executionMode":"deterministic-harness-replay","liveExternalAgentExecuted":False,
        "summary":{"cases":len(results),"passed":sum(item["status"]=="pass" for item in results),"failed":sum(item["status"]!="pass" for item in results)},
        "cases":results,
    }
    tier_a["valid"] = tier_a["summary"]["failed"] == 0
    write_json(result_root / "tier-a-results.json", tier_a)
    tier_b={
        "schema":"https://schemas.aixem.org/validation/agent-eval-2-tier-b-status/1","formatVersion":"1.0",
        "release":"AIXEM-SRP-0.5.5-2026-08-11","generatedAt":FIXED_TIME,
        "tier":"B","executionMode":"live-external-agent","executed":False,"liveExternalAgentExecuted":False,
        "executor":None,"cases":0,"passed":0,
        "claim":"No live external agent execution was performed. This release makes no Tier B live-agent success claim.",
        "valid":True,
    }
    write_json(result_root / "tier-b-status.json", tier_b)
    summary=["# Agent Evaluation 2 Summary","",f"- Tier A: **{tier_a['summary']['passed']}/{tier_a['summary']['cases']} PASS**",f"- Tier B executed: **no**",f"- Live external agent claim: **none**","", "Tier A proves the deterministic route-bounded harness and known repair replay. It must not be represented as cold-start live-agent generation.",""]
    (result_root / "summary.md").write_text("\n".join(summary),encoding="utf-8")
    print(canonical({"valid":tier_a["valid"] and tier_b["valid"],"tierA":tier_a["summary"],"tierBExecuted":False}),end="")
    return 0 if tier_a["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
