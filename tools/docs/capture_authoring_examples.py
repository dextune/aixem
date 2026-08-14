#!/usr/bin/env python3
"""Capture browser-rendered PNG evidence for all executable AIXEM authoring drawings."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "validation" / "evidence" / "pass-02" / "authoring-visuals"
CHROMIUM = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
FIXED_TIME = "2026-08-12T00:00:00Z"
RELEASE = f"AIXEM-SRP-{(ROOT / 'VERSION').read_text(encoding='utf-8').strip()}-2026-08-12"


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def html_for_svg(svg: str, title: str) -> str:
    return f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{title}</title><style>html,body{{margin:0;background:#f1f2ef}}main{{width:1600px;height:1000px;display:grid;place-items:center}}svg{{width:1600px;height:1000px;display:block;background:white}}</style></head><body><main>{svg}</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if not CHROMIUM:
        raise SystemExit("A Chromium-compatible browser is required.")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright is required. Install requirements-release.txt.") from exc

    roots = sorted(path for path in (ROOT / "examples" / "authoring").glob("[0-9][0-9]-*") if (path / "render" / "drawing.svg").is_file())
    args.output.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=CHROMIUM, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        for example in roots:
            source = example / "render" / "drawing.svg"
            target = args.output / f"{example.name}.png"
            page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
            page.set_content(html_for_svg(source.read_text(encoding="utf-8"), example.name), wait_until="load", timeout=30_000)
            page.wait_for_timeout(200)
            page.screenshot(path=str(target), full_page=False, animations="disabled")
            page.close()
            width, height = png_size(target)
            records.append({
                "example": example.name,
                "source": source.relative_to(ROOT).as_posix(),
                "file": target.relative_to(ROOT).as_posix(),
                "width": width,
                "height": height,
                "bytes": target.stat().st_size,
                "digest": sha256(target),
            })
        browser.close()
    payload = {
        "schema": "https://schemas.aixem.org/validation/authoring-visual-capture/1",
        "formatVersion": "1.0",
        "release": RELEASE,
        "generatedAt": FIXED_TIME,
        "valid": len(records) == 8 and all(item["width"] == 1600 and item["height"] == 1000 and item["bytes"] > 0 for item in records),
        "engine": "playwright-chromium-inline-svg",
        "networkAccess": "not used",
        "captures": records,
    }
    manifest = args.output.parent / "authoring-visual-capture.json"
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
