#!/usr/bin/env python3
"""Capture offline visual-review evidence for the AIXEM documentation site and schematic workbench."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "validation" / "evidence" / "pass-03"
CHROMIUM = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
FIXED_TIME = "2026-08-12T00:00:00Z"
RELEASE = f"AIXEM-SRP-{(ROOT / 'VERSION').read_text(encoding='utf-8').strip()}-2026-08-12"


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Visual capture is not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def inline_site_page(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    css = (ROOT / "site" / "assets" / "site.css").read_text(encoding="utf-8")
    html = re.sub(
        r'<link\s+rel=["\']stylesheet["\']\s+href=["\'][^"\']*site\.css["\']\s*/?>',
        lambda _: f"<style>{css}</style>",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    html = re.sub(r'<script\s+src=["\'][^"\']*(?:search-data|site)\.js["\']\s*></script>', "", html, flags=re.IGNORECASE)
    html = re.sub(
        r'<iframe\b[^>]*>.*?</iframe>',
        '<div class="note">Embedded example captured separately.</div>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def cases() -> list[dict[str, Any]]:
    def site_case(name: str, source: str, width: int = 1440, height: int = 1000, full_page: bool = True) -> dict[str, Any]:
        return {
            "name": name,
            "source": source,
            "html": inline_site_page(ROOT / source),
            "viewport": {"width": width, "height": height},
            "fullPage": full_page,
        }

    def workbench_case(name: str, source: str) -> dict[str, Any]:
        return {
            "name": name,
            "source": source,
            "html": (ROOT / source).read_text(encoding="utf-8"),
            "viewport": {"width": 1600, "height": 1000},
            "fullPage": False,
        }

    return [
        site_case("site-home-desktop.png", "site/index.html"),
        site_case("site-home-narrow.png", "site/index.html", 430, 900),
        site_case("authoring-home-desktop.png", "site/authoring/index.html"),
        site_case("symbol-cookbook-desktop.png", "site/symbols/authoring-cookbook.html"),
        site_case("renderer-contract-desktop.png", "site/specifications/renderer/renderer-contract.html"),
        site_case("requirements-desktop.png", "site/conformance/requirements.html"),
        workbench_case("schematic-workbench-desktop.png", "examples/electronics-grid-controller/render/workbench.html"),
        workbench_case("authoring-passive-workbench.png", "examples/authoring/01-two-pin-passive/render/workbench.html"),
        workbench_case("authoring-ic-workbench.png", "examples/authoring/03-multi-pin-ic/render/workbench.html"),
        workbench_case("authoring-junction-workbench.png", "examples/authoring/07-multi-terminal-junction/render/workbench.html"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    if not CHROMIUM:
        raise SystemExit("A Chromium-compatible browser is required for visual evidence capture.")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright is required for visual evidence capture. Install requirements-release.txt.") from exc

    records: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path=CHROMIUM,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        for case in cases():
            page = browser.new_page(viewport=case["viewport"], device_scale_factor=1)
            page.emulate_media(media="screen", reduced_motion="reduce")
            page.set_content(case["html"], wait_until="load", timeout=30_000)
            page.wait_for_timeout(350)
            target = args.output / case["name"]
            page.screenshot(path=str(target), full_page=case["fullPage"], animations="disabled")
            page.close()
            width, height = png_size(target)
            records.append({
                "file": target.relative_to(ROOT).as_posix(),
                "source": case["source"],
                "viewport": case["viewport"],
                "fullPage": case["fullPage"],
                "width": width,
                "height": height,
                "bytes": target.stat().st_size,
                "digest": sha256(target),
            })
        browser.close()

    payload = {
        "schema": "https://schemas.aixem.org/validation/visual-capture/1",
        "formatVersion": "1.0",
        "release": RELEASE,
        "generatedAt": FIXED_TIME,
        "valid": all(item["bytes"] > 0 and item["width"] > 0 and item["height"] > 0 for item in records),
        "engine": "playwright-chromium-set-content",
        "networkAccess": "not used",
        "captures": records,
    }
    manifest = args.output / "visual-capture.json"
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
