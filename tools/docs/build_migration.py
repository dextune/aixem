#!/usr/bin/env python3
"""Build the auditable AIXEM 0.4 inventory and 0.5 migration map."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FIXED_TIME = "2026-08-11T00:00:00Z"
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]")
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".go", ".js", ".mjs", ".css", ".html", ".svg", ".txt", ".sh", ".fbs", ".iso-ebnf", ".mod", ""}

DOC_MAP: dict[str, list[str]] = {
    "README.md": ["README.md", "docs/index.md"],
    "START_HERE.md": ["START_HERE.md", "docs/getting-started/index.md"],
    "docs/00-release-overview.md": ["docs/releases/0.4.md", "docs/releases/0.5.md"],
    "docs/01-package-and-authority-map.md": ["docs/concepts/authority-model.md", "docs/architecture/artifact-store.md"],
    "docs/02-grid-schematic-visual-language.md": ["docs/schematic/visual-language.md", "docs/schematic/grid-system.md"],
    "docs/03-symbol-authoring-and-pin-model.md": ["docs/symbols/authoring-guide.md", "docs/symbols/pins-and-ports.md"],
    "docs/04-orthogonal-routing-and-net-semantics.md": ["docs/routing/orthogonal-routing.md", "docs/routing/net-routing.md"],
    "docs/05-reference-navigation-architecture.md": ["docs/agent/retrieval.md", "docs/agent/task-routing.md"],
    "docs/06-agent-task-execution-protocol.md": ["docs/agent/architecture.md", "docs/agent/validation-loop.md"],
    "docs/07-system-architecture-and-services.md": ["docs/architecture/system-overview.md", "docs/architecture/pipeline.md"],
    "docs/08-cache-digest-and-incremental-loading.md": ["docs/architecture/cache.md", "docs/concepts/deterministic-builds.md"],
    "docs/09-validation-and-three-loop-assurance.md": ["docs/conformance/validation.md", "docs/conformance/release-gates.md"],
    "docs/10-ip-independence-and-ui-boundary.md": ["docs/schematic/visual-language.md", "docs/architecture/adr/0003-vendor-neutral-ui.md"],
    "docs/11-migration-from-0.3.md": ["docs/conformance/compatibility-conformance.md", "legacy/0.4-migration-map.json"],
    "docs/12-roadmap.md": ["docs/releases/0.5.md", "PLAN-0.5.md"],
    "docs/adr/ADR-0040-grid-first-schematic.md": ["docs/architecture/adr/0001-canonical-doc-root.md", "docs/schematic/visual-language.md"],
    "docs/adr/ADR-0041-route-first-reference.md": ["docs/architecture/adr/0002-route-first-retrieval.md"],
    "docs/adr/ADR-0042-semantic-connectivity-authority.md": ["docs/concepts/authority-model.md", "docs/concepts/semantic-model.md"],
    "docs/adr/ADR-0043-independent-workbench.md": ["docs/architecture/adr/0003-vendor-neutral-ui.md"],
    "specifications/aixem-agent-task-route-profile-1.md": ["docs/specifications/agent/retrieval-profile.md", "docs/_meta/schema/task-route.schema.json"],
    "specifications/aixem-grid-schematic-profile-1.md": ["docs/specifications/schematic/grid-profile.md"],
    "specifications/aixem-workbench-ui-profile-1.md": ["docs/specifications/schematic/visual-profile.md"],
    "specifications/aixem-reference-navigation-profile-1.md": ["docs/agent/retrieval.md", "docs/specifications/agent/retrieval-profile.md"],
    "specifications/aixem-grid-schematic-style-1.aixstyle.json": ["profiles/aixem-grid-schematic-style-1.aixstyle.json"],
    "implementation/reference/generate_reference_content.py": ["tools/docs/aixem_docs.py"],
    "implementation/schematic/component_core.py": ["implementation/schematic/component_core.py"],
    "implementation/schematic/render_project.py": ["implementation/schematic/render_project.py"],
    "validation/screenshots/workbench-desktop.png": ["validation/evidence/pass-01/legacy-workbench-desktop.png"],
}

SCHEMA_TARGETS: dict[str, str] = {
    "aixem-reference-card-1.schema.json": "docs/specifications/schemas/reference-compatibility-1/aixem-reference-card-1.schema.json",
    "aixem-artifact-map-1.schema.json": "docs/specifications/schemas/reference-compatibility-1/aixem-artifact-map-1.schema.json",
    "aixem-schematic-style-1.schema.json": "docs/specifications/schemas/reference-compatibility-1/aixem-schematic-style-1.schema.json",
    "aixem-capability-index-1.schema.json": "docs/specifications/schemas/reference-compatibility-1/aixem-capability-index-1.schema.json",
    "aixem-reference-root-1.schema.json": "docs/specifications/schemas/reference-compatibility-1/aixem-reference-root-1.schema.json",
    "aixem-task-route-1.schema.json": "docs/specifications/schemas/reference-compatibility-1/aixem-task-route-1.schema.json",
    "aixem-reference-manifest-1.schema.json": "docs/specifications/schemas/reference-compatibility-1/aixem-reference-manifest-1.schema.json",
    "aixem-reference-domain-index-1.schema.json": "docs/specifications/schemas/reference-compatibility-1/aixem-reference-domain-index-1.schema.json",
    "aixem-component-library-1.schema.json": "docs/specifications/schemas/component-graphics-1/aixem-component-library-1.schema.json",
    "aixem-project-manifest-1.schema.json": "docs/specifications/schemas/component-graphics-1/aixem-project-manifest-1.schema.json",
    "aixem-explicit-layout-1.schema.json": "docs/specifications/schemas/component-graphics-1/aixem-explicit-layout-1.schema.json",
    "aixem-symbol-asset-1.schema.json": "docs/specifications/schemas/component-graphics-1/aixem-symbol-asset-1.schema.json",
}



def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def unwrap_source(path: Path, temp: Path) -> tuple[Path, str | None]:
    if path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            archive.extractall(temp)
        children = [p for p in temp.iterdir() if p.name != "__MACOSX"]
        root = children[0] if len(children) == 1 and children[0].is_dir() else temp
        return root, sha256_file(path)
    if not path.is_dir():
        raise SystemExit(f"Baseline path does not exist or is unsupported: {path}")
    children = [p for p in path.iterdir()]
    if len(children) == 1 and children[0].is_dir() and children[0].name.startswith("aixem-schematic-reference-platform-0.4"):
        return children[0], None
    return path, None


def contains_non_english_text(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    return bool(CJK_RE.search(text))


def classify(source: str) -> tuple[str, list[str], str]:
    if source in DOC_MAP:
        return "canonicalized", DOC_MAP[source], "The 0.4 source was normalized into the listed canonical 0.5 document or artifact."
    if source.startswith("docs/") and source.endswith(".md"):
        return "canonicalized", ["docs/"], "The authored 0.4 document was decomposed into the canonical 0.5 information architecture."
    if source.startswith("reference/"):
        return "generated", ["reference/", "docs/_meta/generated/"], "The 0.4 reference artifact is now generated from canonical English documentation and authored route metadata."
    if source.startswith("examples/electronics-grid-controller/"):
        if "/render/" in source or "/evidence/" in source:
            return "regenerated", [source], "The example output is regenerated deterministically from retained semantic, symbol, layout, and project inputs."
        return "retained", [source], "The example source is retained as an executable 0.5 reference project."
    if source.startswith("implementation/schematic/"):
        if "__pycache__" in source or source.endswith(".pyc"):
            return "discarded-build-cache", [], "Python bytecode is not a source artifact and is intentionally excluded from 0.5."
        if source.endswith("generate_baseline_examples.py") or source.endswith("generate_grid_controller.py"):
            return "superseded", ["implementation/schematic/render_project.py", "examples/electronics-grid-controller/"], "One-off 0.4 generation scripts were superseded by retained canonical inputs and deterministic rendering."
        return "retained", [source], "The deterministic renderer implementation remains applicable to 0.5."
    if source.startswith("implementation/reference/"):
        return "superseded", ["tools/docs/aixem_docs.py"], "Reference generation was consolidated into the canonical documentation compiler."
    if source.startswith("implementation/scripts/"):
        return "superseded", ["tools/docs/"], "Release and validation responsibilities moved to the documented 0.5 toolchain."
    if source.startswith("specifications/schemas/"):
        name = Path(source).name
        target = SCHEMA_TARGETS.get(name)
        if target:
            disposition = "retained" if "component-graphics-1" in target else "retained-compatibility-schema"
            return disposition, [target], "The machine-readable contract is preserved under the canonical schema catalog."
        return "reviewed-superseded", ["docs/specifications/schemas/index.md"], "The schema was reviewed but is not an active 0.5 contract."
    if source.startswith("specifications/"):
        return "canonicalized", ["docs/specifications/"], "The 0.4 specification was normalized into the canonical specification hierarchy."
    if source.startswith("baseline/"):
        return "archived-by-inventory", ["legacy/0.4-inventory.json"], "The nested 0.3 baseline is audit-preserved by digest and disposition rather than copied into the 0.5 source tree."
    if source.startswith("validation/"):
        return "retained-evidence", ["validation/"], "The useful evidence role is retained and regenerated under the 0.5 validation structure."
    return "reviewed-superseded", ["legacy/0.4-migration-map.json"], "The source was reviewed and is represented by the migration record; it is not an independent 0.5 authority."


def collect_declared_paths(root: Path) -> list[str]:
    index = root / "reference" / "index.aixref.json"
    if not index.is_file():
        return []
    try:
        data = json.loads(index.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    paths: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str) and (value.startswith("reference/") or value.startswith("docs/") or value.startswith("specifications/") or value.startswith("validation/") or value.startswith("implementation/")):
            paths.add(value.split("#", 1)[0])

    walk(data)
    return sorted(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path, help="Extracted 0.4 directory or the 0.4 ZIP archive")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="aixem-04-inventory-") as tmp_name:
        baseline_root, archive_digest = unwrap_source(args.baseline.resolve(), Path(tmp_name))
        files = [p for p in sorted(baseline_root.rglob("*")) if p.is_file()]
        inventory_records = []
        migration_records = []
        for path in files:
            rel = path.relative_to(baseline_root).as_posix()
            record = {
                "path": rel,
                "bytes": path.stat().st_size,
                "digest": sha256_file(path),
                "extension": path.suffix.lower(),
                "topLevel": rel.split("/", 1)[0],
                "containsNonEnglishText": contains_non_english_text(path),
            }
            inventory_records.append(record)
            disposition, targets, rationale = classify(rel)
            canonical_ids = []
            for target in targets:
                target_path = ROOT / target
                if target.startswith("docs/") and target_path.is_file() and target_path.suffix == ".md":
                    text = target_path.read_text(encoding="utf-8")
                    match = re.search(r"^id:\s*([^\n]+)$", text, re.MULTILINE)
                    if match:
                        canonical_ids.append(match.group(1).strip().strip("'\""))
            if not canonical_ids:
                if rel.startswith("reference/"):
                    canonical_ids = ["AIXEM-AGENT-RETRIEVAL-001"]
                elif rel.startswith("examples/"):
                    canonical_ids = ["AIXEM-EXAMPLE-CONTROLLER-001"]
                elif rel.startswith("implementation/"):
                    canonical_ids = ["AIXEM-ARCH-PIPELINE-001"]
                elif rel.startswith("specifications/schemas/"):
                    canonical_ids = ["AIXEM-SPEC-SCHEMAS-001"]
                elif rel.startswith("specifications/"):
                    canonical_ids = ["AIXEM-SPEC-INDEX-001"]
                elif rel.startswith("validation/"):
                    canonical_ids = ["AIXEM-CONF-VALIDATION-001"]
                elif rel.startswith("baseline/"):
                    canonical_ids = ["AIXEM-RELEASE-040-001"]
            migration_records.append({
                "source": rel,
                "sourceDigest": record["digest"],
                "disposition": disposition,
                "target": targets,
                "canonicalDocumentIds": sorted(set(canonical_ids)),
                "rationale": rationale,
            })
            if rel.startswith("specifications/schemas/") and Path(rel).name in SCHEMA_TARGETS:
                out = ROOT / SCHEMA_TARGETS[Path(rel).name]
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, out)
            if rel == "validation/screenshots/workbench-desktop.png":
                out = ROOT / "validation" / "evidence" / "pass-01" / "legacy-workbench-desktop.png"
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, out)

        disposition_counts = Counter(item["disposition"] for item in migration_records)
        top_counts = Counter(item["topLevel"] for item in inventory_records)
        extension_counts = Counter(item["extension"] or "<none>" for item in inventory_records)
        inventory = {
            "schema": "https://schemas.aixem.org/migration/baseline-inventory/1",
            "formatVersion": "1.0",
            "release": "AIXEM-SRP-0.5.0-2026-08-11",
            "generatedAt": FIXED_TIME,
            "source": {
                "release": "AIXEM-SRP-0.4-2026-08-10",
                "rootName": baseline_root.name,
                "archiveDigest": archive_digest,
            },
            "summary": {
                "files": len(inventory_records),
                "bytes": sum(item["bytes"] for item in inventory_records),
                "nonEnglishTextFiles": sum(bool(item["containsNonEnglishText"]) for item in inventory_records),
                "byTopLevel": dict(sorted(top_counts.items())),
                "byExtension": dict(sorted(extension_counts.items())),
            },
            "files": inventory_records,
        }
        migration = {
            "schema": "https://schemas.aixem.org/migration/path-map/1",
            "formatVersion": "1.0",
            "release": "AIXEM-SRP-0.5.0-2026-08-11",
            "generatedAt": FIXED_TIME,
            "sourceRelease": "AIXEM-SRP-0.4-2026-08-10",
            "summary": {"mappings": len(migration_records), "byDisposition": dict(sorted(disposition_counts.items()))},
            "mappings": migration_records,
        }
        present = {item["path"] for item in inventory_records}
        declared = collect_declared_paths(baseline_root)
        source_missing = [path for path in declared if path not in present]
        target_resolved = [path for path in source_missing if (ROOT / path).exists()]
        target_unresolved = [path for path in source_missing if not (ROOT / path).exists()]
        audit = {
            "schema": "https://schemas.aixem.org/migration/declared-artifact-audit/1",
            "formatVersion": "1.0",
            "release": "AIXEM-SRP-0.5.0-2026-08-11",
            "generatedAt": FIXED_TIME,
            "sourceRelease": "AIXEM-SRP-0.4-2026-08-10",
            "declaredPaths": declared,
            "present": [path for path in declared if path in present],
            "missing": source_missing,
            "sourceReleaseValid": not source_missing,
            "resolvedInTarget": target_resolved,
            "unresolvedInTarget": target_unresolved,
            "targetResolutionValid": not target_unresolved,
            "valid": not target_unresolved,
        }

        outputs = [
            (ROOT / "legacy" / "0.4-inventory.json", inventory),
            (ROOT / "legacy" / "0.4-migration-map.json", migration),
            (ROOT / "legacy" / "0.4-declared-artifact-audit.json", audit),
            (ROOT / "validation" / "evidence" / "pass-01" / "baseline-inventory.json", inventory),
            (ROOT / "validation" / "evidence" / "pass-01" / "migration-map.json", migration),
            (ROOT / "validation" / "evidence" / "pass-01" / "declared-artifact-audit.json", audit),
        ]
        for path, data in outputs:
            write_json(path, data)

        for filename, rows, fields in [
            (ROOT / "legacy" / "0.4-inventory.csv", inventory_records, ["path", "bytes", "digest", "extension", "topLevel", "containsNonEnglishText"]),
            (ROOT / "legacy" / "0.4-migration-map.csv", migration_records, ["source", "sourceDigest", "disposition", "target", "canonicalDocumentIds", "rationale"]),
        ]:
            filename.parent.mkdir(parents=True, exist_ok=True)
            with filename.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                for row in rows:
                    prepared = dict(row)
                    if isinstance(prepared.get("target"), list):
                        prepared["target"] = "; ".join(prepared["target"])
                    if isinstance(prepared.get("canonicalDocumentIds"), list):
                        prepared["canonicalDocumentIds"] = "; ".join(prepared["canonicalDocumentIds"])
                    writer.writerow(prepared)

        print(json.dumps({
            "baselineRoot": str(baseline_root),
            "inventoryFiles": len(inventory_records),
            "inventoryBytes": inventory["summary"]["bytes"],
            "mappings": len(migration_records),
            "declaredPaths": len(declared),
            "declaredMissing": len(audit["missing"]),
            "dispositions": dict(sorted(disposition_counts.items())),
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
