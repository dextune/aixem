#!/usr/bin/env python3
"""Observable non-AI fixture executor used only for Tier A protocol tests."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def event(sequence: int, kind: str, **fields):
    value = {"schema": "https://schemas.aixem.org/agent/observation-event/1", "formatVersion": "1.0", "sequence": sequence, "kind": kind, **fields}
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def append(log: Path, sequence: int, kind: str, **fields) -> int:
    with log.open("a", encoding="utf-8") as handle:
        handle.write(event(sequence, kind, **fields))
    return sequence + 1


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, default=Path(os.environ["AIXEM_TASK"]))
    parser.add_argument("--workspace", type=Path, default=Path(os.environ["AIXEM_WORKSPACE"]))
    parser.add_argument("--reference", type=Path, default=Path(os.environ["AIXEM_REFERENCE"]))
    parser.add_argument("--state", type=Path, default=Path(os.environ["AIXEM_STATE"]))
    parser.add_argument("--observation-log", type=Path, default=Path(os.environ["AIXEM_OBSERVATION_LOG"]))
    args = parser.parse_args()
    task = json.loads(args.task.read_text(encoding="utf-8"))
    args.state.mkdir(parents=True, exist_ok=True)
    sequence = 1
    sequence = append(args.observation_log, sequence, "task-open", target="task/agent-task.json", result="opened")
    sequence = append(args.observation_log, sequence, "route-resolve", route=task["activeRoute"], target=f"reference/docs/_meta/generated/task-packets/{task['activeRoute']}.json", result="resolved")
    project = task.get("project")
    authoring = args.reference / "tools" / "agent_authoring.py"
    harness_state = args.state / "authoring"
    prepare = [sys.executable, str(authoring), "prepare", "--workspace", str(args.workspace), "--route", task["entryRoute"], "--task-id", task["id"].lower(), "--state-dir", str(harness_state)]
    if task["entryRoute"] != task["activeRoute"]:
        prepare.extend(["--stage-route", task["activeRoute"]])
    if project:
        prepare.extend(["--project", project])
    sequence = append(args.observation_log, sequence, "command", tool="agent_authoring.prepare", result="started")
    prepared = run(prepare, args.reference)
    if prepared.returncode != 0:
        append(args.observation_log, sequence, "executor-error", tool="agent_authoring.prepare", result=prepared.stderr[-1000:] or prepared.stdout[-1000:])
        return prepared.returncode
    sequence = append(args.observation_log, sequence, "validator", tool="agent_authoring.check", result="started")
    checked = run([sys.executable, str(authoring), "check", "--state-dir", str(harness_state)], args.reference)
    sequence = append(args.observation_log, sequence, "validator", tool="agent_authoring.close", result="started")
    closed = run([sys.executable, str(authoring), "close", "--state-dir", str(harness_state)], args.reference)
    result = "closed" if closed.returncode == 0 else "blocked"
    append(args.observation_log, sequence, "completion", result=result)
    sys.stdout.write(closed.stdout)
    sys.stderr.write(checked.stderr + closed.stderr)
    return closed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
