"""Deterministic workspace snapshots and route-bounded authoring change sets."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from schematic.authoring_integrity import validate_library_artifact_path

CHANGE_SET_SCHEMA = "https://schemas.aixem.org/agent/change-set/1"
CHANGE_SET_FORMAT_VERSION = "1.0"
SNAPSHOT_SCHEMA = "https://schemas.aixem.org/agent/workspace-snapshot/1"

DEFAULT_EXCLUDES = {
    ".aixem-agent",
    "__pycache__",
    ".pytest_cache",
    ".git",
}
DERIVED_DIRECTORY_NAMES = {"render", "evidence"}
DERIVED_FILENAMES = {
    "viewer.html",
    "workbench.html",
    "viewer-model.json",
    "resolved-scene.json",
    "resolved-project-scene.json",
    "render-manifest.json",
    "project-validation.json",
    "drawing.svg",
    "project-overview.svg",
    "project-composite.svg",
}


class UnsafeWorkspaceError(RuntimeError):
    """A workspace path escaped its root or used a symbolic link."""


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def classify_artifact(path: str) -> tuple[str, str]:
    """Return ``(role, authority)`` for one workspace-relative path."""
    pure = PurePosixPath(path)
    name = pure.name
    parts = set(pure.parts)
    if "fixtures" in parts:
        return "support", "none"
    if parts.intersection(DERIVED_DIRECTORY_NAMES) or name in DERIVED_FILENAMES:
        return "derived", "none"
    if name.endswith(".aixsym.json"):
        return "authoritative", "symbol"
    if name.endswith(".aixlib.json"):
        return "authoritative", "component-library"
    if name.endswith(".aixlayout.json"):
        return "authoritative", "layout"
    if name.endswith(".aixproj.json"):
        return "authoritative", "project"
    if name.endswith(".aixem"):
        return "authoritative", "semantic"
    return "support", "none"


def _path_matches(path: str, pattern: str) -> bool:
    path = PurePosixPath(path).as_posix()
    pattern = PurePosixPath(pattern).as_posix()
    if fnmatch.fnmatchcase(path, pattern):
        return True
    if pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:]):
        return True
    return False


def _is_excluded(rel: PurePosixPath, excludes: set[str]) -> bool:
    return any(part in excludes for part in rel.parts)


def _load_json_if_applicable(path: Path, role: str) -> Any | None:
    if role != "authoritative" or path.suffix != ".json":
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def snapshot_workspace(root: Path, *, excludes: Iterable[str] = DEFAULT_EXCLUDES) -> dict[str, Any]:
    """Snapshot files without following symlinks.

    AIXEM authoring evidence must never normalize an unsafe tree into an
    apparently valid snapshot, so any symlink fails closed.
    """
    root = root.resolve()
    if not root.is_dir():
        raise UnsafeWorkspaceError(f"workspace is not a directory: {root}")
    excluded = set(excludes)
    files: dict[str, dict[str, Any]] = {}
    unsafe: list[str] = []
    for current, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        rel_current = current_path.relative_to(root)
        kept_dirs: list[str] = []
        for dirname in sorted(dirnames):
            path = current_path / dirname
            rel = PurePosixPath((rel_current / dirname).as_posix())
            if _is_excluded(rel, excluded):
                continue
            if path.is_symlink():
                unsafe.append(rel.as_posix())
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in sorted(filenames):
            path = current_path / filename
            rel_path = path.relative_to(root)
            rel = PurePosixPath(rel_path.as_posix())
            if _is_excluded(rel, excluded):
                continue
            if path.is_symlink():
                unsafe.append(rel.as_posix())
                continue
            try:
                resolved = path.resolve(strict=True)
                resolved.relative_to(root)
            except (OSError, ValueError):
                unsafe.append(rel.as_posix())
                continue
            role, authority = classify_artifact(rel.as_posix())
            record: dict[str, Any] = {
                "path": rel.as_posix(),
                "bytes": path.stat().st_size,
                "digest": sha256_file(path),
                "role": role,
                "authority": authority,
            }
            json_value = _load_json_if_applicable(path, role)
            if json_value is not None:
                record["json"] = json_value
            files[rel.as_posix()] = record
    if unsafe:
        raise UnsafeWorkspaceError("unsafe workspace paths: " + ", ".join(sorted(unsafe)))
    digest_records = [
        {key: value for key, value in record.items() if key != "json"}
        for _path, record in sorted(files.items())
    ]
    authoritative_records = [record for record in digest_records if record["role"] == "authoritative"]
    return {
        "schema": SNAPSHOT_SCHEMA,
        "formatVersion": "1.0",
        "workspace": ".",
        "fileCount": len(files),
        "authoritativeFileCount": len(authoritative_records),
        "digest": sha256_bytes(canonical_json_bytes(digest_records)),
        "authoritativeDigest": sha256_bytes(canonical_json_bytes(authoritative_records)),
        "files": files,
    }


def _escape_pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def json_changed_pointers(before: Any, after: Any, base: str = "") -> list[str]:
    """Return deterministic leaf pointers that differ between two JSON values."""
    if type(before) is not type(after):
        return [base or ""]
    if isinstance(before, Mapping):
        result: list[str] = []
        for key in sorted(set(before) | set(after), key=str):
            pointer = f"{base}/{_escape_pointer(str(key))}"
            if key not in before or key not in after:
                result.append(pointer)
            else:
                result.extend(json_changed_pointers(before[key], after[key], pointer))
        return result
    if isinstance(before, list):
        result = []
        for index in range(max(len(before), len(after))):
            pointer = f"{base}/{index}"
            if index >= len(before) or index >= len(after):
                result.append(pointer)
            else:
                result.extend(json_changed_pointers(before[index], after[index], pointer))
        return result
    return [] if before == after else [base or ""]


def _constraint_for(path: str, scope: Mapping[str, Any]) -> Mapping[str, Any] | None:
    for item in scope.get("constraints", []) or []:
        if _path_matches(path, str(item.get("pattern", ""))):
            return item
    return None


def _constraint_result(
    path: str,
    operation: str,
    before: Mapping[str, Any] | None,
    after: Mapping[str, Any] | None,
    scope: Mapping[str, Any],
) -> tuple[bool, list[str], str | None]:
    constraint = _constraint_for(path, scope)
    if not constraint:
        return True, [], None
    policy = str(constraint.get("policy", ""))
    if policy == "digest-only":
        if operation != "modified" or before is None or after is None or "json" not in before or "json" not in after:
            return False, [], "digest-only policy requires an existing JSON artifact"
        pointers = json_changed_pointers(before["json"], after["json"])
        valid = bool(pointers) and all(PurePosixPath(pointer).name == "digest" for pointer in pointers)
        return valid, pointers, None if valid else "project lock update changed fields other than digest"
    if policy == "no-delete":
        return operation != "deleted", [], None if operation != "deleted" else "artifact deletion is prohibited"
    if policy == "new-library-artifact-canonical":
        issues = validate_library_artifact_path(path, operation=operation)
        if not issues:
            return True, [], None
        message = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        return False, [], message
    return False, [], f"unknown write constraint policy {policy!r}"


def build_change_set(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    route: str,
    scope: Mapping[str, Any],
    iteration: int,
    required_validators: Iterable[str] = (),
    allow_derived_changes: bool = False,
) -> dict[str, Any]:
    before_files = dict(before.get("files", {}))
    after_files = dict(after.get("files", {}))
    allowed_authority = set(scope.get("authority", []) or [])
    artifact_patterns = list(scope.get("artifacts", []) or [])
    derived_patterns = list(scope.get("derived", []) or [])
    prohibited_patterns = list(scope.get("prohibited", []) or [])
    changes: list[dict[str, Any]] = []
    generated_edits: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []

    for path in sorted(set(before_files) | set(after_files)):
        old = before_files.get(path)
        new = after_files.get(path)
        if old and new and old.get("digest") == new.get("digest"):
            continue
        operation = "added" if old is None else "deleted" if new is None else "modified"
        reference = new or old or {}
        role = str(reference.get("role", "support"))
        authority = str(reference.get("authority", "none"))
        is_prohibited = any(_path_matches(path, pattern) for pattern in prohibited_patterns)
        generated = role == "derived" or any(_path_matches(path, pattern) for pattern in derived_patterns) or is_prohibited
        pattern_allowed = any(_path_matches(path, pattern) for pattern in artifact_patterns)
        authority_allowed = role == "authoritative" and authority in allowed_authority
        constraint_valid, changed_pointers, constraint_error = _constraint_result(path, operation, old, new, scope)
        allowed = authority_allowed and pattern_allowed and constraint_valid and not generated
        if generated and allow_derived_changes and not is_prohibited:
            allowed = True

        record: dict[str, Any] = {
            "path": path,
            "operation": operation,
            "role": role,
            "authority": authority,
            "beforeDigest": old.get("digest") if old else None,
            "afterDigest": new.get("digest") if new else None,
            "allowed": bool(allowed),
        }
        if changed_pointers:
            record["changedPointers"] = changed_pointers
        changes.append(record)

        if generated and not allow_derived_changes:
            generated_record = {**record, "reason": "derived output changed before the harness render boundary"}
            generated_edits.append(generated_record)
            violations.append({"path": path, "kind": "generated-output-edit", "message": generated_record["reason"]})
            continue
        if not allowed:
            if constraint_error:
                kind = "write-constraint"
                message = constraint_error
            elif role != "authoritative":
                kind = "non-authoritative-edit"
                message = f"{role} artifact is not writable by an authoring route"
            elif authority not in allowed_authority:
                kind = "authority-scope"
                message = f"authority {authority!r} is outside route {route!r}"
            elif not pattern_allowed:
                kind = "artifact-scope"
                message = f"artifact path does not match route {route!r} write patterns"
            else:
                kind = "prohibited-path"
                message = "artifact path is explicitly prohibited"
            violations.append({"path": path, "kind": kind, "message": message})

    return {
        "schema": CHANGE_SET_SCHEMA,
        "formatVersion": CHANGE_SET_FORMAT_VERSION,
        "iteration": int(iteration),
        "route": route,
        "beforeSnapshotDigest": before.get("digest"),
        "afterSnapshotDigest": after.get("digest"),
        "beforeAuthoritativeDigest": before.get("authoritativeDigest"),
        "afterAuthoritativeDigest": after.get("authoritativeDigest"),
        "changed": changes,
        "generatedOutputEdits": generated_edits,
        "scopeViolations": violations,
        "requiredValidators": sorted(set(required_validators)),
        "valid": not violations,
    }


def scope_summary(scope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "authority": sorted(set(scope.get("authority", []) or [])),
        "artifacts": sorted(set(scope.get("artifacts", []) or [])),
        "derived": sorted(set(scope.get("derived", []) or [])),
        "prohibited": sorted(set(scope.get("prohibited", []) or [])),
        "constraints": sorted(
            [dict(item) for item in scope.get("constraints", []) or []],
            key=lambda item: (str(item.get("pattern", "")), str(item.get("policy", ""))),
        ),
    }
