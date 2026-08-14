"""Shared conservative secret redaction and retained-evidence scanning."""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

SECRET_NAME_RE = re.compile(
    r"(?:token|secret|password|passwd|api[_-]?key|credential|authorization|cookie)", re.I
)
# Require a token boundary so ordinary strings such as ``task-path-argument``
# are not mistaken for an ``sk-...`` credential.
SECRET_VALUE_RE = re.compile(
    r"(?i)(bearer\s+[A-Za-z0-9._~+/=-]{8,}|"
    r"(?<![A-Za-z0-9])(?:sk|pk|api)[-_][A-Za-z0-9_-]{12,}|"
    r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,})"
)


def redact_text(value: str, explicit_values: Iterable[str] = ()) -> tuple[str, bool, int]:
    """Redact explicit and credential-shaped values from text."""
    redacted = value
    changed = False
    count = 0
    secrets = sorted({str(item) for item in explicit_values if len(str(item)) >= 4}, key=len, reverse=True)
    for secret in secrets:
        occurrences = redacted.count(secret)
        if occurrences:
            redacted = redacted.replace(secret, "[REDACTED]")
            changed = True
            count += occurrences
    redacted, generic_count = SECRET_VALUE_RE.subn("[REDACTED]", redacted)
    return redacted, changed or generic_count > 0, count + generic_count


def redact_nested(value: Any, explicit_values: Iterable[str] = ()) -> tuple[Any, bool, int]:
    """Redact strings recursively while retaining the original JSON shape."""
    if isinstance(value, str):
        return redact_text(value, explicit_values)
    if isinstance(value, list):
        output: list[Any] = []
        changed = False
        count = 0
        for item in value:
            sanitized, item_changed, item_count = redact_nested(item, explicit_values)
            output.append(sanitized)
            changed = changed or item_changed
            count += item_count
        return output, changed, count
    if isinstance(value, Mapping):
        output: dict[str, Any] = {}
        changed = False
        count = 0
        for key, item in value.items():
            sanitized, item_changed, item_count = redact_nested(item, explicit_values)
            output[str(key)] = sanitized
            changed = changed or item_changed
            count += item_count
        return output, changed, count
    return value, False, 0


def scan_text_for_secrets(value: str, explicit_values: Iterable[str] = ()) -> dict[str, Any]:
    explicit = sorted({str(item) for item in explicit_values if len(str(item)) >= 4})
    explicit_matches = ["explicit-secret" for secret in explicit if secret in value]
    generic_matches = [match.group(0) for match in SECRET_VALUE_RE.finditer(value)]
    return {
        "valid": not explicit_matches and not generic_matches,
        "explicitMatches": explicit_matches,
        "genericMatches": generic_matches,
    }


def scan_paths(paths: Iterable[Path], explicit_values: Iterable[str] = ()) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    files_scanned = 0
    for path in sorted({Path(item) for item in paths}, key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        files_scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        scan = scan_text_for_secrets(text, explicit_values)
        if not scan["valid"]:
            matches.append({
                "path": path.as_posix(),
                "explicitMatches": scan["explicitMatches"],
                "genericMatches": scan["genericMatches"],
            })
    return {"valid": not matches, "filesScanned": files_scanned, "matches": matches}


def canonical_redacted_json(value: Any, explicit_values: Iterable[str] = ()) -> tuple[str, bool, int]:
    sanitized, changed, count = redact_nested(value, explicit_values)
    return json.dumps(sanitized, ensure_ascii=False, sort_keys=True), changed, count
