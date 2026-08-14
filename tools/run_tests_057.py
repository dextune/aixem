#!/usr/bin/env python3
"""Run every AIXEM 0.5.7 test module in an isolated process and aggregate evidence.

The module boundary prevents browser/runtime resources from one conformance
family from affecting later families while still executing the complete
repository test inventory.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = "2026-08-12T00:00:00Z"
TEST_COUNT_RE = re.compile(r"Ran\s+(\d+)\s+tests?\s+in")


def tail(text: str, limit: int = 12000) -> str:
    return text if len(text) <= limit else text[-limit:]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def module_name(path: Path) -> str:
    return ".".join(path.relative_to(ROOT).with_suffix("").parts)


def run_module(module: str, timeout: int, verbosity: int) -> dict[str, Any]:
    command = [sys.executable, "-m", "unittest", f"-{'v' * max(1, verbosity)}", module]
    started = time.perf_counter()
    try:
        process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        combined = process.stdout + process.stderr
        match = TEST_COUNT_RE.search(combined)
        tests = int(match.group(1)) if match else 0
        status = "PASS" if process.returncode == 0 else "FAIL"
        return {
            "module": module,
            "command": command,
            "status": status,
            "valid": status == "PASS",
            "returnCode": process.returncode,
            "testsRun": tests,
            "durationSeconds": round(time.perf_counter() - started, 6),
            "stdoutTail": tail(process.stdout),
            "stderrTail": tail(process.stderr),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "module": module,
            "command": command,
            "status": "FAIL",
            "valid": False,
            "returnCode": 124,
            "testsRun": 0,
            "durationSeconds": round(time.perf_counter() - started, 6),
            "stdoutTail": tail((exc.stdout or "") if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", "replace")),
            "stderrTail": tail((exc.stderr or "") if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", "replace")),
            "timeout": timeout,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=900, help="timeout in seconds per test module")
    parser.add_argument("--verbosity", type=int, default=1)
    parser.add_argument("--output", type=Path, default=ROOT / "validation" / "test-results.json")
    parser.add_argument("--pattern", default="test_*.py")
    args = parser.parse_args()

    paths = sorted((ROOT / "tests").rglob(args.pattern))
    modules = [module_name(path) for path in paths if path.is_file()]
    started = time.perf_counter()
    results: list[dict[str, Any]] = []
    for module in modules:
        print(f"[tests] START {module}", flush=True)
        result = run_module(module, args.timeout, args.verbosity)
        results.append(result)
        print(f"[tests] {result['status']} {module} ({result['testsRun']} tests, {result['durationSeconds']}s)", flush=True)

    successful = all(item["valid"] for item in results)
    tests_run = sum(int(item["testsRun"]) for item in results)
    payload = {
        "schema": "https://schemas.aixem.org/validation/test-run/1",
        "formatVersion": "1.0",
        "release": f"AIXEM-SRP-{(ROOT / 'VERSION').read_text(encoding='utf-8').strip()}-2026-08-12",
        "generatedAt": FIXED_TIME,
        "executionMode": "isolated-test-module-processes",
        "successful": successful,
        "testsRun": tests_run,
        "moduleCount": len(results),
        "passedModules": sum(item["valid"] for item in results),
        "failedModules": sum(not item["valid"] for item in results),
        "durationSeconds": round(time.perf_counter() - started, 6),
        "failures": [item for item in results if not item["valid"]],
        "errors": [],
        "skipped": [],
        "modules": results,
    }
    write_json(args.output, payload)
    print(json.dumps({"successful": successful, "testsRun": tests_run, "modules": len(results), "failedModules": payload["failedModules"]}, sort_keys=True))
    return 0 if successful else 2


if __name__ == "__main__":
    raise SystemExit(main())
