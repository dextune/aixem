#!/usr/bin/env python3
"""Measure the AIXEM 0.5.3 ten-sheet hierarchical reference baseline."""
from __future__ import annotations

import argparse
import json
import platform
import resource
import statistics
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMATIC = ROOT / "implementation" / "schematic"
if str(SCHEMATIC) not in sys.path:
    sys.path.insert(0, str(SCHEMATIC))

from component_core import sha256_file  # noqa: E402
from render_project import MultiSheetProjectRenderer  # noqa: E402

DEFAULT_PROJECT = ROOT / "validation" / "corpus" / "hierarchical-project-1" / "cases" / "H013-ten-sheet-scale-baseline" / "project.aixproj.json"
DEFAULT_OUTPUT = ROOT / "validation" / "corpus" / "hierarchical-project-1" / "results" / "performance-baseline.json"
FIXED_TIME = "2026-08-11T00:00:00Z"


def _round(value: float) -> float:
    return round(float(value), 6)


def _distribution(values: list[float]) -> dict[str, float]:
    return {
        "minimum": _round(min(values)),
        "median": _round(statistics.median(values)),
        "maximum": _round(max(values)),
    }


def _project_input_statistics(project_file: Path) -> dict[str, Any]:
    project_doc = json.loads(project_file.read_text(encoding="utf-8"))
    project = project_doc["project"]
    root = project_file.parent
    source_paths = [root / sheet["source"]["path"] for sheet in project["sheets"]]
    layout_paths = [root / sheet["layout"]["path"] for sheet in project["sheets"]]
    hierarchy = {sheet["id"]: sheet.get("parent") for sheet in project["sheets"]}

    def depth(sheet_id: str) -> int:
        count = 0
        parent = hierarchy[sheet_id]
        while parent:
            count += 1
            parent = hierarchy[parent]
        return count

    return {
        "sheetCount": len(project["sheets"]),
        "hierarchyDepth": max((depth(sheet["id"]) for sheet in project["sheets"]), default=0),
        "projectNetCount": len(project.get("projectNets", [])),
        "totalSourceBytes": sum(path.stat().st_size for path in source_paths),
        "totalLayoutBytes": sum(path.stat().st_size for path in layout_paths),
        "projectBytes": project_file.stat().st_size,
        "projectDigest": sha256_file(project_file),
    }


def run_once(project_file: Path) -> dict[str, Any]:
    tracemalloc.start()
    total_started = time.perf_counter()
    renderer = MultiSheetProjectRenderer(project_file)
    initialized = time.perf_counter()

    composite_started = time.perf_counter()
    composite_svg = renderer.build_composite_svg()
    composite_build_seconds = time.perf_counter() - composite_started

    with tempfile.TemporaryDirectory(prefix="aixem-h013-benchmark-") as tmp:
        render_started = time.perf_counter()
        result = renderer.render(Path(tmp))
        render_seconds = time.perf_counter() - render_started
        output_dir = Path(tmp)
        sizes = {
            "resolvedProjectSceneBytes": (output_dir / "resolved-project-scene.json").stat().st_size,
            "overviewSvgBytes": (output_dir / "project-overview.svg").stat().st_size,
            "compositeSvgBytes": (output_dir / "project-composite.svg").stat().st_size,
            "workbenchBytes": (output_dir / "workbench.html").stat().st_size,
            "totalRenderBytes": sum(path.stat().st_size for path in output_dir.rglob("*") if path.is_file()),
        }
        scene = result["scene"]

    total_seconds = time.perf_counter() - total_started
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    max_rss_bytes = int(max_rss * 1024) if sys.platform != "darwin" else int(max_rss)

    leaf_stats = [sheet.scene["statistics"] for sheet in renderer.resolver.sheets.values()]
    return {
        "timingsSeconds": {
            **{key: _round(value) for key, value in renderer.performance.items()},
            "initializationTotalSeconds": _round(initialized - total_started),
            "compositeSvgBuildSeconds": _round(composite_build_seconds),
            "outputRenderSeconds": _round(render_seconds),
            "totalSeconds": _round(total_seconds),
        },
        "counts": {
            "localEntityCount": sum(item["entities"] for item in leaf_stats),
            "localNetCount": sum(item["nets"] for item in leaf_stats),
            "interfacePortCount": sum(item["interfacePorts"] for item in leaf_stats),
            "projectNetCount": len(renderer.resolver.project_nets),
            "routeDiagnosticCount": len(scene["diagnostics"]),
        },
        "outputSizes": sizes,
        "memory": {
            "tracemallocCurrentBytes": current_memory,
            "tracemallocPeakBytes": peak_memory,
            "processMaxRssBytes": max_rss_bytes,
        },
        "compositeDigestProbe": len(composite_svg),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be at least 1")
    project_file = args.project.resolve()
    runs = [run_once(project_file) for _ in range(args.runs)]
    input_stats = _project_input_statistics(project_file)
    timing_keys = sorted(runs[0]["timingsSeconds"])
    payload = {
        "schema": "https://schemas.aixem.org/validation/hierarchical-performance/1",
        "formatVersion": "1.0",
        "release": "AIXEM-SRP-0.5.3-2026-08-11",
        "generatedAt": FIXED_TIME,
        "case": "H013",
        "project": project_file.relative_to(ROOT).as_posix(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "implementation": platform.python_implementation(),
        },
        "input": input_stats,
        "counts": runs[0]["counts"],
        "timingsSeconds": {
            key: _distribution([run["timingsSeconds"][key] for run in runs])
            for key in timing_keys
        },
        "outputSizes": runs[0]["outputSizes"],
        "memory": {
            key: {
                "minimum": min(run["memory"][key] for run in runs),
                "median": int(statistics.median(run["memory"][key] for run in runs)),
                "maximum": max(run["memory"][key] for run in runs),
            }
            for key in runs[0]["memory"]
        },
        "runs": runs,
        "result": "PASS" if all(run["counts"]["routeDiagnosticCount"] == 0 for run in runs) else "FAIL",
        "policy": {
            "measureBeforeOptimizing": True,
            "cacheAdded": False,
            "scaleGate": "Ten digest-locked sheets must resolve and render reliably without release-blocking diagnostics.",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": payload["result"],
        "runs": args.runs,
        "sheetCount": input_stats["sheetCount"],
        "medianTotalSeconds": payload["timingsSeconds"]["totalSeconds"]["median"],
        "peakMemoryBytes": payload["memory"]["tracemallocPeakBytes"]["maximum"],
        "output": args.output.relative_to(ROOT).as_posix(),
    }, indent=2, sort_keys=True))
    return 0 if payload["result"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
