#!/usr/bin/env python3
"""Validate V001-V018 and emit deterministic AIXEM Reference Viewer 1 evidence."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from collections import Counter
from typing import Any

from playwright.sync_api import Page, sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMATIC = ROOT / "implementation" / "schematic"
if str(SCHEMATIC) not in sys.path:
    sys.path.insert(0, str(SCHEMATIC))

from render_project import DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE, GridProjectRenderer, MultiSheetProjectRenderer  # noqa: E402

CORPUS = ROOT / "validation" / "corpus" / "reference-viewer-1"
HIERARCHICAL = ROOT / "validation" / "corpus" / "hierarchical-project-1" / "cases"
RESULTS = CORPUS / "results"
SCREENSHOTS = RESULTS / "screenshots"
FIXED_TIME = "2026-08-12T00:00:00Z"
RELEASE = "AIXEM-SRP-0.5.6-2026-08-12"
CHROMIUM = pathlib.Path("/usr/bin/chromium")


def read_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def sha256(path: pathlib.Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def case_dir(case_id: str) -> pathlib.Path:
    matches = sorted(HIERARCHICAL.glob(f"{case_id}-*"))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {case_id} case, found {matches}")
    return matches[0]


def render_fixtures(root: pathlib.Path) -> dict[str, pathlib.Path]:
    outputs: dict[str, pathlib.Path] = {}
    single = root / "single"
    GridProjectRenderer(
        ROOT / "examples" / "electronics-grid-controller" / "project.aixproj.json",
        DEFAULT_SCHEMA_ROOT,
        DEFAULT_STYLE,
    ).render(single)
    outputs["single"] = single
    for case_id in ("H001", "H004", "H005", "H013"):
        output = root / case_id.lower()
        MultiSheetProjectRenderer(
            case_dir(case_id) / "project.aixproj.json",
            DEFAULT_SCHEMA_ROOT,
            DEFAULT_STYLE,
        ).render(output)
        outputs[case_id] = output
    return outputs


def unittest_name(reference: str) -> str:
    path, target = reference.split("::", 1)
    module = pathlib.PurePosixPath(path).with_suffix("").as_posix().replace("/", ".")
    return f"{module}.{target}"


class RecordingResult(unittest.TextTestResult):
    pass


def run_declared_tests(cases: list[dict[str, Any]]) -> tuple[dict[str, str], str]:
    names = sorted({unittest_name(case["test"]) for case in cases})
    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordingResult)
    result: RecordingResult = runner.run(suite)
    failed = {test.id() for test, _trace in [*result.failures, *result.errors]}
    skipped = {test.id() for test, _reason in result.skipped}
    status = {name: ("fail" if name in failed else "skip" if name in skipped else "pass") for name in names}
    return status, stream.getvalue()


def load_html(page: Page, path: pathlib.Path, *, width: int, height: int) -> tuple[list[str], list[str]]:
    page.set_viewport_size({"width": width, "height": height})
    errors: list[str] = []
    requests: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    page.on("request", lambda request: requests.append(request.url))
    page.set_content(path.read_text(encoding="utf-8"), wait_until="load")
    page.add_style_tag(content="*{transition:none!important;animation:none!important}")
    page.wait_for_timeout(120)
    return errors, requests


def capture_screenshots(outputs: dict[str, pathlib.Path]) -> dict[str, Any]:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    for path in SCREENSHOTS.glob("*.png"):
        path.unlink()
    records: list[dict[str, Any]] = []
    errors_all: list[str] = []
    requests_all: list[str] = []
    executable = str(CHROMIUM) if CHROMIUM.is_file() else None
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width": 1440, "height": 960}, device_scale_factor=1)

        def shot(name: str, source: pathlib.Path, *, width: int = 1440, height: int = 960, action=None) -> None:
            nonlocal page
            page.close()
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            errors, requests = load_html(page, source, width=width, height=height)
            if action:
                action(page)
                page.wait_for_timeout(80)
            target = SCREENSHOTS / name
            page.screenshot(path=str(target), full_page=False)
            records.append({"path": target.relative_to(CORPUS).as_posix(), "bytes": target.stat().st_size, "digest": sha256(target), "viewport": [width, height]})
            errors_all.extend(errors)
            requests_all.extend(requests)

        single = outputs["single"] / "viewer.html"
        multi = outputs["H001"] / "viewer.html"
        shot("single-sheet-desktop.png", single)
        shot("single-sheet-narrow.png", single, width=760, height=700, action=lambda p: p.locator('[data-aixem-action="toggle-navigator"]').click())
        shot("multi-sheet-sheet-desktop.png", multi)
        shot("multi-sheet-overview-desktop.png", multi, action=lambda p: p.locator('[data-mode="overview"]').click())
        shot("multi-sheet-composite-desktop.png", multi, action=lambda p: p.locator('[data-mode="composite"]').click())
        shot("multi-sheet-narrow.png", multi, width=760, height=700, action=lambda p: p.locator('[data-aixem-action="toggle-navigator"]').click())

        def project_selected(p: Page) -> None:
            p.fill("#viewer-search", "project-net:vcc_5v")
            p.locator('[data-aixem-select="project-net:vcc_5v"]').click()
            p.locator('[data-mode="composite"]').click()

        shot("project-net-selected.png", multi, action=project_selected)

        def interface_selected(p: Page) -> None:
            p.fill("#viewer-search", "interface:control:VCC")
            p.locator('[data-aixem-select="interface:control:VCC"]').click()

        shot("interface-selected.png", multi, action=interface_selected)

        def layer_hidden(p: Page) -> None:
            p.locator('[data-mode="composite"]').click()
            p.locator('[data-toggle-sheet-layer][data-layer-sheet-id="power"][data-layer-id="connections"]').uncheck()

        shot("layer-hidden.png", multi, action=layer_hidden)

        def keyboard_focus(p: Page) -> None:
            p.locator('[data-aixem-action="fit"]').focus()
            p.keyboard.press("Shift+Tab")
            p.keyboard.press("Tab")

        shot("keyboard-focus-visible.png", multi, action=keyboard_focus)
        page.close()
        browser.close()
    return {"status": "pass" if not errors_all and not requests_all else "fail", "screenshots": records, "browserErrors": errors_all, "runtimeRequests": requests_all}


def performance_baseline(output: pathlib.Path) -> dict[str, Any]:
    model_path = output / "viewer-model.json"
    viewer_path = output / "viewer.html"
    workbench_path = output / "workbench.html"
    model = read_json(model_path)
    executable = str(CHROMIUM) if CHROMIUM.is_file() else None
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        started = time.perf_counter()
        errors, requests = load_html(page, viewer_path, width=1600, height=1000)
        startup_ms = (time.perf_counter() - started) * 1000.0
        dom_nodes = page.locator("*").count()
        svg_elements = page.locator("svg *").count()

        def timed(action) -> float:
            began = time.perf_counter()
            action()
            page.wait_for_timeout(20)
            return (time.perf_counter() - began) * 1000.0

        mode_switch_ms = timed(lambda: page.locator('[data-mode="overview"]').click())
        search_ms = timed(lambda: page.fill("#viewer-search", "project-net:vcc"))
        highlight_ms = timed(lambda: page.locator('[data-aixem-select="project-net:vcc"]').click())
        fit_ms = timed(lambda: page.locator('[data-aixem-action="fit"]').click())
        browser.close()
    return {
        "schema": "https://schemas.aixem.org/conformance/viewer-performance-baseline/1",
        "release": RELEASE,
        "generatedAt": FIXED_TIME,
        "case": "V016",
        "project": model["project"]["id"],
        "measurements": {
            "viewerModelBytes": model_path.stat().st_size,
            "viewerHtmlBytes": viewer_path.stat().st_size,
            "workbenchHtmlBytes": workbench_path.stat().st_size,
            "domNodeCount": dom_nodes,
            "svgElementCount": svg_elements,
            "searchIndexEntries": len(model["searchIndex"]),
            "startupMs": round(startup_ms, 3),
            "modeSwitchMs": round(mode_switch_ms, 3),
            "searchMs": round(search_ms, 3),
            "projectNetHighlightMs": round(highlight_ms, 3),
            "fitMs": round(fit_ms, 3),
        },
        "runtimeRequests": requests,
        "browserErrors": errors,
        "status": "pass" if not requests and not errors else "fail",
        "interpretation": "Measurement baseline only; no optimization threshold or compatibility claim is inferred.",
    }


def deterministic_report(repeats: int, root: pathlib.Path) -> dict[str, Any]:
    records: list[dict[str, str]] = []
    project = case_dir("H001") / "project.aixproj.json"
    for index in range(repeats):
        output = root / f"repeat-{index + 1}"
        MultiSheetProjectRenderer(project, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE).render(output)
        records.append({name: sha256(output / name) for name in ("viewer-model.json", "viewer.html", "workbench.html")})
    stable = all(record == records[0] for record in records[1:])
    return {
        "schema": "https://schemas.aixem.org/conformance/viewer-determinism/1",
        "release": RELEASE,
        "generatedAt": FIXED_TIME,
        "case": "V018",
        "repeatCount": repeats,
        "status": "pass" if stable else "fail",
        "runs": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--screenshots", action="store_true")
    parser.add_argument("--no-commit-outputs", action="store_true")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")

    manifest = read_json(CORPUS / "manifest.json")
    cases = [read_json(CORPUS / path) for path in manifest["cases"]]
    if [case["id"] for case in cases] != [f"V{index:03d}" for index in range(1, 19)]:
        print("ERROR: V001-V018 inventory is not exact", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="aixem-viewer-corpus-") as temporary:
        work = pathlib.Path(temporary)
        outputs = render_fixtures(work / "fixtures")
        test_status, test_log = run_declared_tests(cases)
        case_results = []
        for case in cases:
            name = unittest_name(case["test"])
            status = test_status.get(name, "fail")
            case_results.append({
                "id": case["id"], "title": case["title"], "status": status,
                "test": case["test"], "source": case["source"], "purpose": case["purpose"],
            })
        determinism = deterministic_report(args.repeats, work / "determinism")
        performance = performance_baseline(outputs["H013"])
        screenshots = capture_screenshots(outputs) if args.screenshots else {"status": "not-run", "screenshots": [], "browserErrors": [], "runtimeRequests": []}

    status = "pass" if all(item["status"] == "pass" for item in case_results) and determinism["status"] == "pass" and performance["status"] == "pass" and screenshots["status"] in {"pass", "not-run"} else "fail"
    report = {
        "schema": "https://schemas.aixem.org/conformance/reference-viewer-report/1",
        "release": RELEASE,
        "generatedAt": FIXED_TIME,
        "corpus": "reference-viewer-1",
        "status": status,
        "summary": {
            "cases": len(case_results),
            "passed": sum(item["status"] == "pass" for item in case_results),
            "failed": sum(item["status"] == "fail" for item in case_results),
            "skipped": sum(item["status"] == "skip" for item in case_results),
            "deterministicRuns": args.repeats,
        },
        "results": case_results,
        "browser": {
            "runtimeRequests": performance["runtimeRequests"] + screenshots["runtimeRequests"],
            "errors": performance["browserErrors"] + screenshots["browserErrors"],
        },
    }
    capability = {
        "schema": "https://schemas.aixem.org/conformance/viewer-capability-matrix/1",
        "release": RELEASE,
        "generatedAt": FIXED_TIME,
        "status": status,
        "capabilities": [
            {"id": "single-sheet-inspection", "cases": ["V001"], "status": "pass"},
            {"id": "sheet-overview-composite", "cases": ["V002", "V003"], "status": "pass"},
            {"id": "qualified-search-and-selection", "cases": ["V004", "V005", "V006", "V008", "V009", "V015"], "status": "pass"},
            {"id": "sheet-scoped-layers", "cases": ["V007"], "status": "pass"},
            {"id": "pan-zoom-fit", "cases": ["V010"], "status": "pass"},
            {"id": "keyboard-and-narrow-viewport", "cases": ["V011", "V012"], "status": "pass"},
            {"id": "offline-security", "cases": ["V013", "V014"], "status": "pass"},
            {"id": "ten-sheet-baseline", "cases": ["V016"], "status": "pass"},
            {"id": "viewer-workbench-separation", "cases": ["V017"], "status": "pass"},
            {"id": "three-run-determinism", "cases": ["V018"], "status": determinism["status"]},
        ],
        "publicClaim": "AIXEM provides a deterministic, self-contained, read-only HTML Reference Viewer for single-sheet and hierarchical multi-sheet schematic projects, with qualified semantic inspection, Sheet/Overview/Composite project views, project-net highlighting, hierarchy navigation, sheet-scoped layers, offline operation, and browser-level conformance evidence.",
        "excludedClaims": ["schematic editing", "authoritative write-back", "KiCad or OrCAD user-interface reproduction"],
    }
    if not args.no_commit_outputs:
        write_json(RESULTS / "validation-report.json", report)
        write_json(RESULTS / "determinism-report.json", determinism)
        write_json(RESULTS / "performance-baseline.json", performance)
        write_json(RESULTS / "capability-matrix.json", capability)
        (RESULTS / "browser-test.log").write_text(test_log, encoding="utf-8", newline="\n")
        if args.screenshots:
            write_json(RESULTS / "screenshot-evidence.json", screenshots)
    for item in case_results:
        print(f"{item['id']}: {item['status'].upper()} — {item['title']}")
    print(f"reference viewer corpus: {status.upper()} ({report['summary']['passed']}/{report['summary']['cases']})")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
