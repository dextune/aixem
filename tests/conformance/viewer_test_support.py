"""Shared deterministic browser helpers for AIXEM Reference Viewer conformance."""
from __future__ import annotations

import atexit
import contextlib
import hashlib
import json
import pathlib
import sys
import tempfile
from collections.abc import Iterator
from typing import Any

from playwright.sync_api import Browser, Page, Playwright, sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMATIC = ROOT / "implementation" / "schematic"
if str(SCHEMATIC) not in sys.path:
    sys.path.insert(0, str(SCHEMATIC))

from render_project import DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE, GridProjectRenderer, MultiSheetProjectRenderer  # noqa: E402

CORPUS = ROOT / "validation" / "corpus" / "hierarchical-project-1" / "cases"
CHROMIUM = pathlib.Path("/usr/bin/chromium")


def case_dir(case_id: str) -> pathlib.Path:
    matches = sorted(CORPUS.glob(f"{case_id}-*"))
    if len(matches) != 1:
        raise AssertionError(f"expected one {case_id} case, found {matches}")
    return matches[0]


def render_single(output: pathlib.Path) -> dict[str, Any]:
    project = ROOT / "examples" / "electronics-grid-controller" / "project.aixproj.json"
    return GridProjectRenderer(project, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE).render(output)


def render_multi(case_id: str, output: pathlib.Path) -> dict[str, Any]:
    project = case_dir(case_id) / "project.aixproj.json"
    return MultiSheetProjectRenderer(project, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE).render(output)


def read_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_hex(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ViewerFixture:
    """Render representative outputs once for one test class."""

    def __init__(self, *case_ids: str, include_single: bool = True):
        self._temporary = tempfile.TemporaryDirectory(prefix="aixem-viewer-tests-")
        self.root = pathlib.Path(self._temporary.name)
        self.outputs: dict[str, pathlib.Path] = {}
        if include_single:
            target = self.root / "single"
            render_single(target)
            self.outputs["single"] = target
        for case_id in case_ids:
            target = self.root / case_id.lower()
            render_multi(case_id, target)
            self.outputs[case_id] = target

    def close(self) -> None:
        self._temporary.cleanup()

    def html(self, key: str, product: str = "viewer") -> str:
        return (self.outputs[key] / f"{product}.html").read_text(encoding="utf-8")

    def model(self, key: str) -> dict[str, Any]:
        return read_json(self.outputs[key] / "viewer-model.json")


_PLAYWRIGHT: Playwright | None = None
_BROWSER: Browser | None = None


def _shared_browser() -> Browser:
    global _PLAYWRIGHT, _BROWSER
    if _BROWSER is None or not _BROWSER.is_connected():
        _PLAYWRIGHT = sync_playwright().start()
        executable = str(CHROMIUM) if CHROMIUM.is_file() else None
        _BROWSER = _PLAYWRIGHT.chromium.launch(
            headless=True,
            executable_path=executable,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
    return _BROWSER


def _close_shared_browser() -> None:
    global _PLAYWRIGHT, _BROWSER
    if _BROWSER is not None:
        try:
            _BROWSER.close()
        except Exception:
            pass
        _BROWSER = None
    if _PLAYWRIGHT is not None:
        try:
            _PLAYWRIGHT.stop()
        except Exception:
            pass
        _PLAYWRIGHT = None


atexit.register(_close_shared_browser)


@contextlib.contextmanager
def browser_page(html: str, *, width: int = 1440, height: int = 960) -> Iterator[tuple[Page, list[str], list[str]]]:
    """Load a self-contained Viewer without a document/network request."""
    page = _shared_browser().new_page(viewport={"width": width, "height": height})
    errors: list[str] = []
    requests: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    page.on("request", lambda request: requests.append(request.url))
    page.set_content(html, wait_until="load")
    page.wait_for_timeout(80)
    try:
        yield page, errors, requests
    finally:
        page.close()
