#!/usr/bin/env python3
"""Create and independently verify the deterministic AIXEM 0.5.7 release ZIP."""
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

PACKAGE_ROOT_NAME = "aixem-schematic-reference-platform-0.5.7-2026-08-12"
OUTPUT = Path("/mnt/data") / f"{PACKAGE_ROOT_NAME}.zip"
SHA_OUTPUT = Path(str(OUTPUT) + ".sha256")
VERIFY_OUTPUT = Path(str(OUTPUT) + ".verification.json")
FIXED_TIME = "2026-08-12T00:00:00Z"
RELEASE = "AIXEM-SRP-0.5.7-2026-08-12"


def sha256_hex(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def unsafe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return path.is_absolute() or not path.parts or ".." in path.parts


def main() -> int:
    source_manifest = aixem_docs.verify_release_manifest(ROOT)
    if not source_manifest.get("valid"):
        print(
            "ERROR: source release manifest is invalid: " + "; ".join(source_manifest.get("errors", [])),
            file=sys.stderr,
        )
        return 2

    with tempfile.TemporaryDirectory(prefix="aixem-057-package-") as temporary:
        temporary_root = Path(temporary)
        staged = temporary_root / PACKAGE_ROOT_NAME
        shutil.copytree(
            ROOT,
            staged,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache", ".aixem-agent"),
            copy_function=shutil.copy2,
        )
        staged_manifest = aixem_docs.verify_release_manifest(staged)
        if not staged_manifest.get("valid"):
            print(
                "ERROR: staged release manifest is invalid: " + "; ".join(staged_manifest.get("errors", [])),
                file=sys.stderr,
            )
            return 2

        first = aixem_docs.deterministic_zip(staged, OUTPUT)
        repeat_path = temporary_root / "repeat.zip"
        second = aixem_docs.deterministic_zip(staged, repeat_path)
        deterministic = first["digest"] == second["digest"] and sha256_hex(OUTPUT) == sha256_hex(repeat_path)
        archive = aixem_docs.verify_archive(OUTPUT)

        with zipfile.ZipFile(OUTPUT) as zip_file:
            names = zip_file.namelist()
            crc_error = zip_file.testzip()

        duplicate_members = sum(count - 1 for count in Counter(names).values() if count > 1)
        unsafe_members = sum(1 for name in names if unsafe_member(name))
        top_level = sorted({PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts})
        one_top_level = top_level == [PACKAGE_ROOT_NAME]
        valid = (
            deterministic
            and archive.get("valid") is True
            and crc_error is None
            and one_top_level
            and duplicate_members == 0
            and unsafe_members == 0
            and staged_manifest.get("valid") is True
        )
        errors = list(archive.get("errors", []))
        if not deterministic:
            errors.append("repeat archive digest mismatch")
        if crc_error is not None:
            errors.append(f"ZIP CRC failure: {crc_error}")
        if not one_top_level:
            errors.append(f"unexpected top-level entries: {top_level}")
        if duplicate_members:
            errors.append(f"duplicate ZIP members: {duplicate_members}")
        if unsafe_members:
            errors.append(f"unsafe ZIP members: {unsafe_members}")

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
            "oneTopLevelDirectory": one_top_level,
            "topLevelDirectory": PACKAGE_ROOT_NAME,
            "duplicateMembers": duplicate_members,
            "unsafeMembers": unsafe_members,
            "containerIntegrity": "PASS" if archive.get("valid") and crc_error is None else "FAIL",
            "crcTest": "PASS" if crc_error is None else "FAIL",
            "sourceManifestVerification": source_manifest,
            "manifestVerification": staged_manifest,
            "deterministicPackaging": {
                "valid": deterministic,
                "firstDigest": first["digest"],
                "secondDigest": second["digest"],
                "firstSha256": sha256_hex(OUTPUT),
                "secondSha256": sha256_hex(repeat_path),
            },
            "errors": errors,
        }
        SHA_OUTPUT.write_text(f"{payload['sha256']}  {OUTPUT.name}\n", encoding="utf-8", newline="\n")
        VERIFY_OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
