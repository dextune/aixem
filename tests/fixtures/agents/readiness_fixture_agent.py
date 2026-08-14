#!/usr/bin/env python3
"""Deterministic non-AI subprocess used for AIXEM pre-live readiness proof.

The fixture is intentionally case-specific and evaluator-side. It is never
staged into task/reference/workspace and can never authorize a live-AI claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time
from typing import Any

OBS_SCHEMA = "https://schemas.aixem.org/agent/observation-event/1"


def stable_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def project_file(workspace: Path) -> Path:
    projects = sorted(workspace.glob("*.aixproj.json"))
    if len(projects) != 1:
        raise RuntimeError(f"expected one top-level project, observed {len(projects)}")
    return projects[0]


def refresh_locks(workspace: Path) -> list[str]:
    """Refresh only existing AIXEM digest locks after an authority-local edit."""
    changed: list[str] = []
    project_path = project_file(workspace)
    project = read_json(project_path)
    root = project_path.parent
    for library_path in sorted(workspace.rglob("*.aixlib.json")):
        if any(part in {"render", "evidence", ".aixem-agent"} for part in library_path.relative_to(workspace).parts):
            continue
        library = read_json(library_path)
        dirty = False
        for component in library.get("library", {}).get("components", []):
            for presentation in component.get("presentations", []):
                asset = presentation.get("asset", {})
                relative = asset.get("path")
                if not relative:
                    continue
                target = (root / PurePosixPath(str(relative))).resolve()
                if target.is_file():
                    observed = sha256_file(target)
                    if asset.get("digest") != observed:
                        asset["digest"] = observed
                        dirty = True
        if dirty:
            stable_json(library_path, library)
            changed.append(library_path.relative_to(workspace).as_posix())
    body = project.get("project", {})
    dirty_project = False
    for ref in body.get("libraries", []):
        target = (root / PurePosixPath(ref["path"])).resolve()
        if target.is_file():
            observed = sha256_file(target)
            if ref.get("digest") != observed:
                ref["digest"] = observed
                dirty_project = True
    if project.get("schema", "").endswith("/aixproj/2"):
        for sheet in body.get("sheets", []):
            for key in ("source", "layout"):
                target = (root / PurePosixPath(sheet[key]["path"])).resolve()
                if target.is_file():
                    observed = sha256_file(target)
                    if sheet[key].get("digest") != observed:
                        sheet[key]["digest"] = observed
                        dirty_project = True
    else:
        for key in ("source", "layout"):
            target = (root / PurePosixPath(body[key]["path"])).resolve()
            if target.is_file():
                observed = sha256_file(target)
                if body[key].get("digest") != observed:
                    body[key]["digest"] = observed
                    dirty_project = True
    if dirty_project:
        stable_json(project_path, project)
        changed.append(project_path.relative_to(workspace).as_posix())
    return changed


def event(sequence: int, kind: str, **fields: Any) -> str:
    value = {"schema": OBS_SCHEMA, "formatVersion": "1.0", "sequence": sequence, "kind": kind, **fields}
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def append(log: Path, sequence: int, kind: str, **fields: Any) -> int:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(event(sequence, kind, **fields))
    return sequence + 1


def run(command: list[str], cwd: Path) -> tuple[subprocess.CompletedProcess[str], int]:
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started = time.monotonic()
    completed = subprocess.run(command, cwd=cwd, env=environment, text=True, capture_output=True, check=False)
    return completed, max(0, int(round((time.monotonic() - started) * 1000)))


def prepare_command(task: dict[str, Any], workspace: Path, reference: Path, state: Path) -> list[str]:
    command = [
        sys.executable, str(reference / "tools/agent_authoring.py"), "prepare",
        "--workspace", str(workspace), "--route", str(task["entryRoute"]),
        "--task-id", str(task["id"]).lower(), "--state-dir", str(state / "authoring"),
    ]
    if task["entryRoute"] != task["activeRoute"]:
        command.extend(["--stage-route", str(task["activeRoute"])])
    if task.get("project"):
        command.extend(["--project", str(task["project"])])
    return command


def apply_success(case_id: str, workspace: Path) -> list[str]:
    changed: list[str] = []
    if case_id == "L008":
        path = workspace / "library/electronics/authoring/repaired-resistor.aixsym.json"
        doc = read_json(path)
        port = next(item for item in doc["symbol"]["ports"] if str(item["id"]) == "1")
        lead = next(item for item in doc["symbol"]["graphics"] if item.get("id") == "lead-1")
        lead["x1"] = port["x"]
        lead["y1"] = port["y"]
        stable_json(path, doc)
        changed.append(path.relative_to(workspace).as_posix())
    elif case_id == "L009":
        path = workspace / "two_terminal_route.aixem"
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if not line.strip().startswith("net misbound_l009 =")]
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
        changed.append(path.relative_to(workspace).as_posix())
    elif case_id == "L010":
        path = workspace / "two_terminal_route.aixlayout.json"
        doc = read_json(path)
        via = doc["layout"]["connections"][0]["paths"][0]["via"]
        via[1][0] = via[0][0]
        stable_json(path, doc)
        changed.append(path.relative_to(workspace).as_posix())
    elif case_id == "L011":
        path = project_file(workspace)
        doc = read_json(path)
        members = doc["project"]["projectNets"][0]["members"]
        seen: set[tuple[str, str]] = set()
        deduplicated = []
        for member in members:
            key = (str(member.get("sheet")), str(member.get("port")))
            if key not in seen:
                seen.add(key)
                deduplicated.append(member)
        doc["project"]["projectNets"][0]["members"] = deduplicated
        stable_json(path, doc)
        changed.append(path.relative_to(workspace).as_posix())
    else:
        raise RuntimeError(f"unsupported success fixture case {case_id}")
    changed.extend(refresh_locks(workspace))
    return sorted(set(changed))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, default=Path(os.environ["AIXEM_TASK"]))
    parser.add_argument("--workspace", type=Path, default=Path(os.environ["AIXEM_WORKSPACE"]))
    parser.add_argument("--reference", type=Path, default=Path(os.environ["AIXEM_REFERENCE"]))
    parser.add_argument("--state", type=Path, default=Path(os.environ["AIXEM_STATE"]))
    parser.add_argument("--observation-log", type=Path, default=Path(os.environ["AIXEM_OBSERVATION_LOG"]))
    parser.add_argument("--mode", default="success", choices=[
        "success", "nonzero", "timeout-after-mutation", "tamper-task", "wrong-authority",
        "generated-output", "zero-exit-no-repair", "close-failure", "malformed-observation", "secret-observation",
    ])
    parser.add_argument("--child-canary", type=Path)
    args = parser.parse_args()
    task = read_json(args.task)
    args.state.mkdir(parents=True, exist_ok=True)
    sequence = 1
    if args.mode == "malformed-observation":
        args.observation_log.write_text('{"secret":"sk-malformed-secret-1234567890"\n', encoding="utf-8")
        return 0
    sequence = append(args.observation_log, sequence, "task-open", target="task/agent-task.json", result="opened")
    sequence = append(args.observation_log, sequence, "route-resolve", route=task["activeRoute"], target=f"reference/docs/_meta/generated/task-packets/{task['activeRoute']}.json", result="resolved")
    if args.mode == "secret-observation":
        secret = os.environ.get("AIXEM_TEST_API_KEY", "sk-fixture-secret-1234567890")
        append(args.observation_log, sequence, "completion", result=f"bearer {secret}", details={"nested": {"token": secret}})
        return 0
    if args.mode == "nonzero":
        append(args.observation_log, sequence, "executor-error", result="intentional nonzero fixture")
        return 7
    if args.mode == "tamper-task":
        args.task.write_text(args.task.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        append(args.observation_log, sequence, "completion", result="tampered task")
        return 0
    if args.mode == "timeout-after-mutation":
        project = project_file(args.workspace)
        project.write_text(project.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        sequence = append(args.observation_log, sequence, "file-write", target=f"workspace/{project.relative_to(args.workspace).as_posix()}", result="mutated before timeout")
        if args.child_canary:
            code = "import pathlib,time; time.sleep(2); pathlib.Path(%r).write_text('survived',encoding='utf-8')" % str(args.child_canary)
            subprocess.Popen([sys.executable, "-c", code])
        time.sleep(30)
        return 0

    prepared, prepare_ms = run(prepare_command(task, args.workspace, args.reference, args.state), args.reference)
    if prepared.returncode != 0:
        append(args.observation_log, sequence, "executor-error", tool="agent_authoring.prepare", result=prepared.stderr[-1000:] or prepared.stdout[-1000:])
        return prepared.returncode

    changed: list[str] = []
    if args.mode == "success":
        changed = apply_success(str(task["id"]), args.workspace)
    elif args.mode == "wrong-authority":
        source = next(args.workspace.glob("*.aixem"))
        source.write_text(source.read_text(encoding="utf-8") + "\n# wrong authority fixture\n", encoding="utf-8")
        changed = [source.relative_to(args.workspace).as_posix()]
    elif args.mode == "generated-output":
        target = args.workspace / "render/hand-edited.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("hand edited generated output\n", encoding="utf-8")
        changed = [target.relative_to(args.workspace).as_posix()]
    elif args.mode in {"zero-exit-no-repair", "close-failure"}:
        changed = []
    for relative in changed:
        sequence = append(args.observation_log, sequence, "file-write", target=f"workspace/{relative}", result="written")
    sequence = append(args.observation_log, sequence, "validator", tool="agent_authoring.check", result="started")
    checked, check_ms = run([sys.executable, str(args.reference / "tools/agent_authoring.py"), "check", "--state-dir", str(args.state / "authoring")], args.reference)
    sequence = append(args.observation_log, sequence, "validator", tool="agent_authoring.close", result="started")
    closed, close_ms = run([sys.executable, str(args.reference / "tools/agent_authoring.py"), "close", "--state-dir", str(args.state / "authoring")], args.reference)
    stable_json(args.state / "readiness-metrics.json", {
        "prepareMs": prepare_ms,
        "checkMs": check_ms,
        "closeMs": close_ms,
        "sourceRepositoryPythonPathUsed": False,
        "workingDirectory": "reference",
    })
    append(args.observation_log, sequence, "completion", result="closed" if closed.returncode == 0 else "blocked")
    sys.stdout.write(closed.stdout)
    sys.stderr.write(prepared.stderr + checked.stderr + closed.stderr)
    if args.mode == "zero-exit-no-repair":
        return 0
    return closed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
