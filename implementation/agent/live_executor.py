"""Provider-neutral subprocess adapter for Live Executor Protocol 1."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
from typing import Any, Callable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from .change_scope import canonical_json_bytes, sha256_bytes
from .cold_start_stage import capture_immutable_stage, verify_immutable_stage
from .observation import read_events, sanitize_observation_log, validate_observation_log
from .secret_hygiene import SECRET_NAME_RE, SECRET_VALUE_RE, redact_text

EXECUTOR_SCHEMA = "https://schemas.aixem.org/agent/executor/1"
EXECUTOR_FORMAT_VERSION = "1.0"


class LiveExecutorError(RuntimeError):
    """An executor descriptor or launch boundary is unsafe or invalid."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def validate_executor_descriptor(descriptor: Mapping[str, Any], schema_file: Path) -> dict[str, Any]:
    validator = Draft202012Validator(read_json(schema_file), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(descriptor), key=lambda item: list(item.absolute_path))
    if errors:
        rendered = []
        for issue in errors[:20]:
            location = "/" + "/".join(str(part) for part in issue.absolute_path)
            rendered.append(f"{location}: {issue.message}")
        raise LiveExecutorError("invalid Live Executor Protocol 1 descriptor: " + "; ".join(rendered))
    for name, value in (descriptor.get("environment") or {}).items():
        if SECRET_NAME_RE.search(str(name)):
            raise LiveExecutorError(f"executor descriptor may not serialize credential-like environment key {name!r}")
        if SECRET_VALUE_RE.search(str(value)):
            raise LiveExecutorError(f"executor descriptor appears to contain a credential value in {name!r}")
    return dict(descriptor)


def _working_directory(stage: Path, policy: str) -> Path:
    mapping = {
        "stage-root": stage,
        "workspace": stage / "workspace",
        "reference-root": stage / "reference",
    }
    if policy not in mapping:
        raise LiveExecutorError(f"unsupported workingDirectoryPolicy {policy!r}")
    path = mapping[policy].resolve()
    path.relative_to(stage.resolve())
    return path


def _materialize_command(template: list[str], stage: Path) -> list[str]:
    substitutions = {
        "{stage}": str(stage.resolve()),
        "{task}": str((stage / "task" / "agent-task.json").resolve()),
        "{taskMarkdown}": str((stage / "task" / "TASK.md").resolve()),
        "{workspace}": str((stage / "workspace").resolve()),
        "{reference}": str((stage / "reference").resolve()),
        "{state}": str((stage / "state").resolve()),
        "{observationLog}": str((stage / "state" / "observation-log.jsonl").resolve()),
    }
    command: list[str] = []
    for token in template:
        value = str(token)
        for marker, replacement in substitutions.items():
            value = value.replace(marker, replacement)
        command.append(value)
    if not command:
        raise LiveExecutorError("executor command is empty")
    return command


def _terminate_process_tree(process: subprocess.Popen[bytes], grace_seconds: float = 0.5) -> dict[str, Any]:
    """Terminate the full executor process group when supported."""
    group_supported = os.name == "posix"
    graceful = False
    forced = False
    if process.poll() is not None:
        return {"groupTerminationSupported": group_supported, "gracefulTermination": True, "forcedKill": False}
    try:
        if group_supported:
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        try:
            process.wait(timeout=grace_seconds)
            graceful = True
        except subprocess.TimeoutExpired:
            forced = True
            if group_supported:
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait()
    except (ProcessLookupError, PermissionError, OSError):
        if process.poll() is None:
            forced = True
            process.kill()
            process.wait()
    return {
        "groupTerminationSupported": group_supported,
        "gracefulTermination": graceful,
        "forcedKill": forced,
    }


def execute_subprocess(
    descriptor: Mapping[str, Any],
    stage: Path,
    *,
    executor_schema_file: Path,
    observation_schema_file: Path,
    now: Callable[[], float] = time.time,
) -> dict[str, Any]:
    descriptor = validate_executor_descriptor(descriptor, executor_schema_file)
    stage = stage.resolve()
    if not (stage / "stage-manifest.json").is_file():
        raise LiveExecutorError(f"not a cold-start stage: {stage}")
    immutable_baseline = capture_immutable_stage(stage)
    command = _materialize_command(list(descriptor["command"]), stage)
    executable = shutil.which(command[0]) if not Path(command[0]).is_absolute() else command[0]
    if not executable or not Path(executable).is_file():
        stage_integrity = verify_immutable_stage(stage, immutable_baseline)
        return {
            "status": "EXECUTOR_ERROR",
            "processStarted": False,
            "externalProcessStarted": False,
            "liveExternalAgentExecuted": False,
            "returnCode": None,
            "error": f"executor is unavailable: {command[0]}",
            "command": [command[0], *["[ARG]" for _ in command[1:]]],
            "descriptorDigest": sha256_bytes(canonical_json_bytes(descriptor)),
            "executableDigest": None,
            "observation": {"valid": False, "events": 0, "errors": ["process did not start"], "coverage": descriptor["observationCapability"], "observedCounts": {}},
            "observationSanitization": {"valid": False, "parseValid": False, "events": 0, "redactionApplied": False, "redactions": 0, "errors": ["process did not start"]},
            "stageIntegrity": stage_integrity,
            "processLifecycle": {"groupTerminationSupported": os.name == "posix", "gracefulTermination": False, "forcedKill": False},
            "secretRedactionApplied": False,
        }

    limits = descriptor["limits"]
    timeout = int(limits["wallTimeSeconds"])
    output_limit = int(limits["outputBytes"])
    observation_path = stage / "state" / "observation-log.jsonl"
    observation_path.parent.mkdir(parents=True, exist_ok=True)
    cwd = _working_directory(stage, str(descriptor["workingDirectoryPolicy"]))

    environment = {
        "PATH": os.environ.get("PATH", ""),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "AIXEM_STAGE": str(stage),
        "AIXEM_TASK": str(stage / "task" / "agent-task.json"),
        "AIXEM_WORKSPACE": str(stage / "workspace"),
        "AIXEM_REFERENCE": str(stage / "reference"),
        "AIXEM_STATE": str(stage / "state"),
        "AIXEM_OBSERVATION_LOG": str(observation_path),
    }
    environment.update({str(key): str(value) for key, value in (descriptor.get("environment") or {}).items()})
    inherited_names = sorted(set(map(str, descriptor.get("inheritEnvironment", []) or [])))
    for name in inherited_names:
        if name in os.environ:
            environment[name] = os.environ[name]
    explicit_secrets = [
        str(environment[name])
        for name in inherited_names
        if name in environment and SECRET_NAME_RE.search(name)
    ]

    input_bytes: bytes | None = None
    if descriptor["inputMode"] == "stdin-task-json":
        input_bytes = (stage / "task" / "agent-task.json").read_bytes()
    elif descriptor["inputMode"] not in {"none", "task-path-argument"}:
        raise LiveExecutorError(f"unsupported inputMode {descriptor['inputMode']!r}")

    started_at = now()
    status = "COMPLETED"
    return_code: int | None = None
    timed_out = False
    launch_error: str | None = None
    lifecycle = {"groupTerminationSupported": os.name == "posix", "gracefulTermination": False, "forcedKill": False}
    with tempfile.TemporaryDirectory(prefix="aixem-live-executor-") as temp:
        stdout_path = Path(temp) / "stdout.bin"
        stderr_path = Path(temp) / "stderr.bin"
        try:
            with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=environment,
                    stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                    stdout=stdout_handle,
                    stderr=stderr_handle,
                    shell=False,
                    start_new_session=(os.name == "posix"),
                )
                try:
                    process.communicate(input=input_bytes, timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    lifecycle = _terminate_process_tree(process)
                    process.communicate()
                return_code = process.returncode
        except (OSError, ValueError) as exc:
            process = None
            launch_error = str(exc)

        if launch_error is not None:
            status = "EXECUTOR_ERROR"
        elif timed_out:
            status = "TIMEOUT"
        elif return_code != 0:
            status = "FAILED"

        stdout_raw = stdout_path.read_bytes() if stdout_path.is_file() else b""
        stderr_raw = stderr_path.read_bytes() if stderr_path.is_file() else b""
        stdout_truncated = len(stdout_raw) > output_limit
        stderr_truncated = len(stderr_raw) > output_limit
        stdout_raw = stdout_raw[:output_limit]
        stderr_raw = stderr_raw[:output_limit]
        stdout_text, stdout_redacted, stdout_redactions = redact_text(stdout_raw.decode("utf-8", "replace"), explicit_secrets)
        stderr_text, stderr_redacted, stderr_redactions = redact_text(stderr_raw.decode("utf-8", "replace"), explicit_secrets)

    sanitization = sanitize_observation_log(observation_path, explicit_secrets)
    if sanitization["parseValid"]:
        observation = validate_observation_log(
            observation_path,
            observation_schema_file,
            declared_coverage=descriptor["observationCapability"],
        )
    else:
        observation = {
            "valid": False,
            "events": 0,
            "errors": list(sanitization["errors"]),
            "coverage": descriptor["observationCapability"],
            "observedCounts": {},
        }
    observation_limit = int(limits["observationEvents"])
    if int(observation.get("events", 0)) > observation_limit:
        observation = dict(observation)
        observation["valid"] = False
        observation["errors"] = [
            *list(observation.get("errors", [])),
            f"observation event limit exceeded: {observation.get('events')} > {observation_limit}",
        ]
    try:
        events = read_events(observation_path)
    except Exception:
        events = []
    observed_kinds = {str(event.get("kind")) for event in events}
    proof_events = bool("task-open" in observed_kinds and observed_kinds.intersection({"route-resolve", "command", "validator", "file-write", "completion"}))
    process_started = launch_error is None
    stage_integrity = verify_immutable_stage(stage, immutable_baseline)
    live_executed = bool(
        descriptor.get("agentClass") == "external-ai"
        and process_started
        and observation.get("valid")
        and proof_events
        and stage_integrity.get("valid")
    )
    finished_at = now()
    sanitized_command = [str(Path(executable).name), *["[ARG]" for _ in command[1:]]]
    result: dict[str, Any] = {
        "status": status,
        "processStarted": process_started,
        "externalProcessStarted": process_started,
        "liveExternalAgentExecuted": live_executed,
        "returnCode": return_code,
        "timedOut": timed_out,
        "durationMs": max(0, int(round((finished_at - started_at) * 1000))),
        "command": sanitized_command,
        "workingDirectoryPolicy": descriptor["workingDirectoryPolicy"],
        "inputMode": descriptor["inputMode"],
        "descriptorDigest": sha256_bytes(canonical_json_bytes(descriptor)),
        "executableDigest": _digest_file(Path(executable)),
        "stdout": stdout_text,
        "stderr": stderr_text,
        "stdoutDigest": sha256_bytes(stdout_text.encode("utf-8")),
        "stderrDigest": sha256_bytes(stderr_text.encode("utf-8")),
        "outputTruncated": stdout_truncated or stderr_truncated,
        "secretRedactionApplied": stdout_redacted or stderr_redacted or bool(sanitization["redactionApplied"]),
        "secretRedactionCount": stdout_redactions + stderr_redactions + int(sanitization["redactions"]),
        "networkPolicy": descriptor["networkPolicy"],
        "inheritedEnvironmentNames": inherited_names,
        "observation": observation,
        "observationSanitization": sanitization,
        "stageIntegrity": stage_integrity,
        "processLifecycle": lifecycle,
        "executionProof": {
            "taskOpenObserved": "task-open" in observed_kinds,
            "observableActionObserved": proof_events,
            "observationLogDigest": observation.get("digest"),
        },
    }
    if launch_error:
        result["error"] = launch_error
    return result
