#!/usr/bin/env python3
"""Create and independently verify the deterministic AIXEM 0.5.4 release ZIP."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOC_TOOLS = ROOT / "tools" / "docs"
if str(DOC_TOOLS) not in sys.path:
    sys.path.insert(0, str(DOC_TOOLS))

import aixem_docs  # noqa: E402

PACKAGE_ROOT_NAME = "aixem-schematic-reference-platform-0.5.4-2026-08-11"
OUTPUT = Path("/mnt/data") / f"{PACKAGE_ROOT_NAME}.zip"
SHA_OUTPUT = Path(str(OUTPUT) + ".sha256")
VERIFY_OUTPUT = Path(str(OUTPUT) + ".verification.json")
FIXED_TIME = "2026-08-11T00:00:00Z"
RELEASE = "AIXEM-SRP-0.5.4-2026-08-11"


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source_manifest = aixem_docs.verify_release_manifest(ROOT)
    if not source_manifest.get("valid"):
        print("ERROR: source release manifest is invalid: " + "; ".join(source_manifest.get("errors", [])), file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="aixem-054-package-") as temporary:
        temporary_root = Path(temporary)
        staged = temporary_root / PACKAGE_ROOT_NAME
        shutil.copytree(
            ROOT,
            staged,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
            copy_function=shutil.copy2,
        )
        staged_manifest = aixem_docs.verify_release_manifest(staged)
        if not staged_manifest.get("valid"):
            print("ERROR: staged release manifest is invalid: " + "; ".join(staged_manifest.get("errors", [])), file=sys.stderr)
            return 2

        first = aixem_docs.deterministic_zip(staged, OUTPUT)
        repeat_path = temporary_root / "repeat.zip"
        second = aixem_docs.deterministic_zip(staged, repeat_path)
        deterministic = first["digest"] == second["digest"]
        archive = aixem_docs.verify_archive(OUTPUT)
        with zipfile.ZipFile(OUTPUT) as zip_file:
            names = zip_file.namelist()
        duplicate_members = sum(count - 1 for count in Counter(names).values() if count > 1)
        unsafe_members = sum(
            1 for name in names
            if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts or not PurePosixPath(name).parts
        )
        top_level = sorted({PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts})
        valid = deterministic and archive.get("valid") is True and top_level == [PACKAGE_ROOT_NAME]
        payload = {
            "schema": "https://schemas.aixem.org/release/archive-verification/1",
            "formatVersion": "1.0",
            "release": RELEASE,
            "generatedAt": FIXED_TIME,
            "valid": valid,
            "archive": OUTPUT.name,
            "bytes": OUTPUT.stat().st_size,
            "digest": first["digest"],
            "sha256": sha256_hex(OUTPUT),
            "members": archive.get("members"),
            "oneTopLevelDirectory": top_level == [PACKAGE_ROOT_NAME],
            "topLevelDirectory": PACKAGE_ROOT_NAME,
            "duplicateMembers": duplicate_members,
            "unsafeMembers": unsafe_members,
            "containerIntegrity": "PASS" if archive.get("valid") else "FAIL",
            "manifestVerification": staged_manifest,
            "deterministicPackaging": {
                "valid": deterministic,
                "firstDigest": first["digest"],
                "secondDigest": second["digest"],
            },
            "errors": archive.get("errors", [])
            + ([] if deterministic else ["repeat archive digest mismatch"])
            + ([] if top_level == [PACKAGE_ROOT_NAME] else [f"unexpected top-level entries: {top_level}"]),
        }
        SHA_OUTPUT.write_text(f"{payload['sha256']}  {OUTPUT.name}\n", encoding="utf-8", newline="\n")
        VERIFY_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
