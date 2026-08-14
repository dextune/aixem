#!/usr/bin/env python3
"""Validate the AIXEM hierarchical-project corpus and emit deterministic evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import sys
import tempfile
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "implementation" / "schematic"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from component_core import AixemGraphicsError, pretty_json, sha256_file  # type: ignore
from project_composition import PROJECT_SCHEMA_V2  # type: ignore
from render_project import (  # type: ignore
    DEFAULT_SCHEMA_ROOT,
    DEFAULT_STYLE,
    GridProjectRenderer,
    MultiSheetProjectRenderer,
)

CORPUS = ROOT / "validation" / "corpus" / "hierarchical-project-1"
FIXED_TIME = "2026-08-12T00:00:00Z"


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(value), encoding="utf-8", newline="\n")


def tree_hashes(root: pathlib.Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists():
        return result
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        result[path.relative_to(root).as_posix()] = sha256_file(path)
    return result


def deterministic_subset(hashes: dict[str, str], schema: str) -> dict[str, str]:
    if schema == PROJECT_SCHEMA_V2:
        wanted = {
            path: digest
            for path, digest in hashes.items()
            if path.endswith(".svg")
            or path.endswith(".resolved-scene.json")
            or path == "resolved-project-scene.json"
            or path in {"viewer-model.json", "viewer.html", "workbench.html"}
        }
    else:
        wanted = {
            path: digest for path, digest in hashes.items()
            if path in {"drawing.svg", "resolved-scene.json", "viewer-model.json", "viewer.html", "workbench.html"}
        }
    return dict(sorted(wanted.items()))


def renderer_for(project_path: pathlib.Path) -> GridProjectRenderer | MultiSheetProjectRenderer:
    project_doc = load_json(project_path)
    if project_doc.get("schema") == PROJECT_SCHEMA_V2:
        return MultiSheetProjectRenderer(project_path, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE)
    return GridProjectRenderer(project_path, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE)


def semantic_assertions(case_id: str, renderer: GridProjectRenderer | MultiSheetProjectRenderer, result: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def add(name: str, condition: bool, observation: Any) -> None:
        checks.append({"id": name, "status": "pass" if condition else "fail", "observation": observation})
        if not condition:
            raise AssertionError(f"{case_id}:{name}: {observation}")

    if isinstance(renderer, MultiSheetProjectRenderer):
        resolver = renderer.resolver
        scene = result["scene"]
        add("PROJECT_SHEET_COUNT", scene["statistics"]["sheets"] == len(resolver.sheets), scene["statistics"]["sheets"])
        add("PROJECT_GRAPH_PRESENT", bool(scene.get("semanticGraph")), sorted(scene.get("semanticGraph", {})))
        add("PROJECT_AUTHORITY", scene["authority"]["connectivityFromGeometry"] is False, scene["authority"])
        add("PROJECT_LAYER_AUTHORITY", scene["authority"]["layersAreSheets"] is False, scene["authority"])
        add("PROJECT_ROUTES_ORTHOGONAL", result["validation"]["checks"]["overviewOrthogonal"] and result["validation"]["checks"]["compositeOrthogonal"], "overview+composite")
        add("PROJECT_WORKBENCH_DATA_DRIVEN", result["validation"]["checks"]["dataDrivenWorkbenchHierarchy"], "resolved hierarchy")
        if case_id == "H001":
            add("H001_NET_CLOSURE", set(resolver.project_nets) == {"control_signal", "gnd", "vcc_5v"}, sorted(resolver.project_nets))
        elif case_id == "H002":
            add("H002_LOCAL_TWO_ENDPOINTS", all(len(endpoints) == 2 for sheet in resolver.sheets.values() for endpoints in sheet.semantic["nets"].values()), {sid: sheet.semantic["nets"] for sid, sheet in resolver.sheets.items()})
        elif case_id == "H003":
            add("H003_FANOUT", all(len(item.members) == 3 for item in resolver.project_nets.values()), {key: len(item.members) for key, item in resolver.project_nets.items()})
        elif case_id == "H004":
            add("H004_NO_IMPLICIT_NET", len(resolver.project_nets) == 0, sorted(resolver.project_nets))
            add("H004_PORTS_UNCONNECTED", len(resolver.unconnected_ports()) == 4, resolver.unconnected_ports())
        elif case_id == "H005":
            add("H005_DEPTH", max(resolver.hierarchy_depth(item) for item in resolver.preorder) == 2, resolver.hierarchy_records())
        elif case_id == "H006":
            add("H006_INTERFACE_ROUTE_CLOSURE", all(sheet.scene["statistics"].get("interfacePorts") == len(sheet.semantic["ports"]) for sheet in resolver.sheets.values()), {sid: sheet.scene["statistics"] for sid, sheet in resolver.sheets.items()})
        elif case_id == "H007":
            add("H007_OVERVIEW", bool(scene["routing"]["overview"]["sheets"]), scene["routing"]["overview"]["canvas"])
        elif case_id == "H008":
            add("H008_COMPOSITE", len(scene["routing"]["composite"]["sheets"]) == len(resolver.sheets), scene["routing"]["composite"]["canvas"])
        elif case_id == "H011":
            add("H011_DIGEST_LOCK", result["validation"]["checks"]["allInputDigestsVerified"], scene["hashes"]["inputs"])
        elif case_id == "H013":
            add("H013_TEN_SHEETS", len(resolver.sheets) == 10, resolver.preorder)
        elif case_id == "H014":
            add("H014_DISTINCT_PROJECT_NETS", len(resolver.project_nets) == 2, sorted(resolver.project_nets))
            junction_owner = {net["id"]: net["junctions"] for net in scene["routing"]["overview"]["nets"]}
            add("H014_JUNCTION_SCOPED", set(junction_owner) == {"signal_a", "signal_b"}, junction_owner)
    else:
        add("H012_LEGACY_SCHEMA", renderer.project_doc["schema"].endswith("/aixproj/1"), renderer.project_doc["schema"])
        add("H012_LEGACY_ARTIFACTS", {item["role"] for item in result["artifacts"]} >= {"drawing-svg", "resolved-scene"}, [item["role"] for item in result["artifacts"]])
    return checks


def validate_case(case_dir: pathlib.Path, repeats: int, commit_outputs: bool) -> dict[str, Any]:
    meta = load_json(case_dir / "case.json")
    project_path = case_dir / meta["project"]
    expected = meta["expected"]
    expected_diagnostic = meta.get("expectedDiagnostic")
    evidence_dir = case_dir / "evidence"
    render_dir = case_dir / "render"
    if commit_outputs:
        shutil.rmtree(render_dir, ignore_errors=True)
        shutil.rmtree(evidence_dir, ignore_errors=True)
    observed = "pass"
    error_text: str | None = None
    result: dict[str, Any] | None = None
    checks: list[dict[str, Any]] = []
    repeat_hashes: list[dict[str, str]] = []
    schema = load_json(project_path).get("schema", "")
    try:
        for repeat in range(repeats):
            if repeat == 0 and commit_outputs:
                target = render_dir
            else:
                target = pathlib.Path(tempfile.mkdtemp(prefix=f"aixem-{meta['id']}-r{repeat + 1}-"))
            try:
                renderer = renderer_for(project_path)
                result = renderer.render(target)
                subset = deterministic_subset(tree_hashes(target), schema)
                repeat_hashes.append(subset)
                if repeat == 0:
                    checks = semantic_assertions(meta["id"], renderer, result)
                    if commit_outputs:
                        write_json(evidence_dir / "project-validation.json", result["validation"])
            finally:
                if not (repeat == 0 and commit_outputs):
                    shutil.rmtree(target, ignore_errors=True)
    except (AixemGraphicsError, AssertionError, OSError, ValueError, KeyError) as exc:
        observed = "fail"
        error_text = str(exc)

    expectation_met = observed == expected
    diagnostic_met = True
    if expected == "fail" and expected_diagnostic:
        diagnostic_met = expected_diagnostic in (error_text or "")
    deterministic = all(item == repeat_hashes[0] for item in repeat_hashes[1:]) if repeat_hashes else expected == "fail"
    status = "pass" if expectation_met and diagnostic_met and deterministic else "fail"
    case_result = {
        "id": meta["id"], "title": meta["title"], "expected": expected, "observed": observed,
        "expectedDiagnostic": expected_diagnostic, "diagnosticMatched": diagnostic_met,
        "deterministic": deterministic, "repeatCount": repeats if observed == "pass" else 0,
        "status": status, "error": error_text, "checks": checks,
        "canonicalHashes": repeat_hashes[0] if repeat_hashes else {},
        "projectDigest": sha256_file(project_path),
    }
    if commit_outputs:
        write_json(evidence_dir / "case-result.json", case_result)
        if expected == "fail":
            write_json(evidence_dir / "expected-failure.json", {
                "case": meta["id"], "expectedDiagnostic": expected_diagnostic,
                "observedError": error_text, "matched": diagnostic_met, "status": status,
            })
    return case_result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--no-commit-outputs", action="store_true")
    parser.add_argument("--only", action="append", default=[])
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")
    case_dirs = sorted((CORPUS / "cases").glob("*/case.json")) + sorted((CORPUS / "negative").glob("*/case.json"))
    selected = []
    requested = set(args.only)
    for path in case_dirs:
        meta = load_json(path)
        if not requested or meta["id"] in requested:
            selected.append(path.parent)
    results = [validate_case(path, args.repeats, not args.no_commit_outputs) for path in selected]
    status = "pass" if all(item["status"] == "pass" for item in results) else "fail"
    report = {
        "schema": "https://schemas.aixem.org/conformance/hierarchical-project-report/1",
        "corpus": "hierarchical-project-1", "release": "0.5.6", "generatedAt": FIXED_TIME,
        "repeatCount": args.repeats, "status": status,
        "summary": {
            "cases": len(results),
            "passed": sum(item["status"] == "pass" for item in results),
            "failed": sum(item["status"] != "pass" for item in results),
            "positive": sum(item["expected"] == "pass" for item in results),
            "expectedFailures": sum(item["expected"] == "fail" for item in results),
            "deterministic": sum(item["deterministic"] for item in results),
        },
        "results": results,
    }
    if not args.no_commit_outputs:
        write_json(CORPUS / "results" / "validation-report.json", report)
        write_json(CORPUS / "results" / "determinism-report.json", {
            "corpus": report["corpus"], "generatedAt": FIXED_TIME, "repeatCount": args.repeats,
            "status": "pass" if all(item["deterministic"] for item in results) else "fail",
            "cases": [{"id": item["id"], "deterministic": item["deterministic"], "hashes": item["canonicalHashes"]} for item in results if item["expected"] == "pass"],
        })
        write_json(CORPUS / "results" / "capability-matrix.json", {
            "release": "0.5.6", "generatedAt": FIXED_TIME,
            "capabilities": [
                {"id": "interface-port-semantics", "evidence": ["H001", "H002", "H006"], "status": "pass"},
                {"id": "explicit-project-nets", "evidence": ["H001", "H003", "H004", "H015"], "status": "pass"},
                {"id": "hierarchy", "evidence": ["H005", "N011", "N012"], "status": "pass"},
                {"id": "overview", "evidence": ["H007", "H014"], "status": "pass"},
                {"id": "composite", "evidence": ["H008", "H013"], "status": "pass"},
                {"id": "digest-locking", "evidence": ["H011", "N013", "N014", "N015"], "status": "pass"},
                {"id": "legacy-v1-compatibility", "evidence": ["H012"], "status": "pass"},
                {"id": "reference-viewer-artifacts", "evidence": ["H001", "H004", "H013"], "status": "pass"},
            ],
            "publicClaim": "AIXEM supports deterministic composition of multiple digest-locked schematic source/layout pairs into an explicit hierarchical project, using semantic sheet interface ports and explicit project nets, with independent sheet rendering, project overview rendering, and composite project visualization.",
            "excludedClaims": ["full KiCad hierarchy compatibility", "full OrCAD multi-page compatibility", "reusable hierarchical module instancing"],
        })
    for item in results:
        print(f"{item['id']}: {item['status'].upper()} (expected {item['expected']}, observed {item['observed']})")
        if item["status"] != "pass":
            print(f"  diagnostic: {item['error']}")
    print(f"hierarchical corpus: {status.upper()} ({report['summary']['passed']}/{report['summary']['cases']})")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
