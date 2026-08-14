"""Shared deterministic HTML/SVG preparation for AIXEM Viewer product profiles."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup

TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates"
BASE_CANVAS_SCALE = 2.0


def safe_json_for_script(value: Any) -> Markup:
    """Serialize JSON deterministically without allowing script-context termination."""
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    text = (
        text.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    return Markup(text)


def namespace_svg(svg: str, prefix: str) -> str:
    """Namespace all local SVG IDs before multiple canvases share one HTML DOM."""
    safe_prefix = re.sub(r"[^A-Za-z0-9_-]", "-", prefix)
    names = set(re.findall(r'\bid="([^"]+)"', svg))
    mapping = {name: f"{safe_prefix}-{name}" for name in names}
    svg = re.sub(
        r'\bid="([^"]+)"',
        lambda match: f'id="{mapping.get(match.group(1), match.group(1))}"',
        svg,
    )
    svg = re.sub(
        r'url\(#([^\)]+)\)',
        lambda match: f"url(#{mapping.get(match.group(1), match.group(1))})",
        svg,
    )
    svg = re.sub(
        r'((?:xlink:)?href)="#([^"]+)"',
        lambda match: f'{match.group(1)}="#{mapping.get(match.group(2), match.group(2))}"',
        svg,
    )
    svg = re.sub(
        r'aria-labelledby="([^"]+)"',
        lambda match: 'aria-labelledby="' + " ".join(mapping.get(token, token) for token in match.group(1).split()) + '"',
        svg,
    )
    return svg


def _append_tag_attrs(full_tag: str, attributes: str) -> str:
    if "data-aixem-qid=" in full_tag:
        return full_tag
    closing = "/>" if full_tag.endswith("/>") else ">"
    return full_tag[: -len(closing)].rstrip() + " " + attributes + closing


def _decorate_by_attribute(
    svg: str,
    attribute: str,
    kind: str,
    qid_builder,
    *,
    require_sheet: bool = False,
) -> str:
    pattern = re.compile(rf'<[A-Za-z][A-Za-z0-9:._-]*\b[^<>]*\b{re.escape(attribute)}="([^"]+)"[^<>]*?/?>')

    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "data-aixem-qid=" in tag:
            return tag
        sheet_match = re.search(r'\bdata-sheet="([^"]+)"', tag)
        sheet = sheet_match.group(1) if sheet_match else None
        if require_sheet and not sheet:
            return tag
        qid = qid_builder(match.group(1), sheet)
        return _append_tag_attrs(tag, f'data-aixem-kind="{kind}" data-aixem-qid="{qid}"')

    return pattern.sub(replace, svg)


def decorate_sheet_svg(svg: str, sheet_id: str, *, prefix: str) -> str:
    """Add stable Viewer DOM identity to a leaf SVG copy without modifying renderer evidence."""
    svg = namespace_svg(svg, prefix)
    svg = re.sub(
        r"<svg\s+",
        (
            f'<svg data-sheet-canvas="{sheet_id}" data-sheet="{sheet_id}" '
            f'data-aixem-kind="sheet" data-aixem-qid="sheet:{sheet_id}" '
        ),
        svg,
        count=1,
    )
    # Leaf objects do not need a pre-existing data-sheet marker because the owning
    # sheet is fixed by this canvas boundary.
    svg = _decorate_by_attribute(
        svg,
        "data-entity",
        "entity",
        lambda native_id, _sheet: f"entity:{sheet_id}:{native_id}",
    )
    svg = _decorate_by_attribute(
        svg,
        "data-net-group",
        "local-net",
        lambda native_id, _sheet: f"local-net:{sheet_id}:{native_id}",
    )
    svg = _decorate_by_attribute(
        svg,
        "data-interface-port",
        "interface",
        lambda native_id, _sheet: f"interface:{sheet_id}:{native_id}",
    )
    return svg


def decorate_project_svg(svg: str, *, view: str, prefix: str) -> str:
    """Add stable Viewer DOM identity to Overview/Composite SVG copies.

    Composite canvases contain complete leaf SVGs.  Their entity and local-net
    groups inherit sheet ownership from the nearest ``data-sheet-canvas`` root
    rather than repeating ``data-sheet`` on every descendant.  A small XML walk
    therefore preserves the qualified-identity closure that flat regular
    expressions cannot safely infer.  The renderer evidence SVG is never
    modified; this operation applies only to the HTML-embedded Viewer copy.
    """
    namespaced = namespace_svg(svg, prefix)
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    try:
        root = ET.fromstring(namespaced)
    except ET.ParseError as exc:
        raise ValueError(f"VIEWER_SVG_INVALID: {view}: {exc}") from exc
    root.set("data-aixem-canvas", view)

    def walk(element: ET.Element, inherited_sheet: str | None = None) -> None:
        sheet = element.get("data-sheet") or element.get("data-sheet-canvas") or inherited_sheet
        kind: str | None = None
        qid: str | None = None
        if element.get("data-interface-port") is not None and sheet:
            kind = "interface"
            qid = f"interface:{sheet}:{element.get('data-interface-port')}"
        elif element.get("data-entity") is not None and sheet:
            kind = "entity"
            qid = f"entity:{sheet}:{element.get('data-entity')}"
        elif element.get("data-net-group") is not None and sheet:
            kind = "local-net"
            qid = f"local-net:{sheet}:{element.get('data-net-group')}"
        elif element.get("data-project-net") is not None:
            kind = "project-net"
            qid = f"project-net:{element.get('data-project-net')}"
        elif element.get("data-sheet") is not None or element.get("data-sheet-canvas") is not None:
            sheet_id = element.get("data-sheet") or element.get("data-sheet-canvas")
            if sheet_id:
                kind = "sheet"
                qid = f"sheet:{sheet_id}"
        if kind and qid and element.get("data-aixem-qid") is None:
            element.set("data-aixem-kind", kind)
            element.set("data-aixem-qid", qid)
        for child in element:
            walk(child, sheet)

    walk(root)
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)


def jinja_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_ROOT)),
        autoescape=select_autoescape(enabled_extensions=("html", "j2"), default_for_string=True),
        undefined=StrictUndefined,
        keep_trailing_newline=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def prepare_template_context(
    model: dict[str, Any],
    *,
    sheet_svgs: dict[str, str],
    overview_svg: str | None,
    composite_svg: str | None,
    profile: str,
) -> dict[str, Any]:
    sheets_by_id = {item["id"]: item for item in model["sheets"]}
    sheet_canvases: list[dict[str, Any]] = []
    for item in model["views"][0]["canvases"]:
        sheet_id = item["sheet"]
        if sheet_id not in sheet_svgs:
            raise ValueError(f"VIEWER_SVG_MISSING: sheet {sheet_id}")
        sheet_canvases.append(
            {
                **item,
                "title": sheets_by_id[sheet_id]["title"],
                "pixelWidth": round(float(item["width"]) * BASE_CANVAS_SCALE, 6),
                "pixelHeight": round(float(item["height"]) * BASE_CANVAS_SCALE, 6),
                "svg": Markup(decorate_sheet_svg(sheet_svgs[sheet_id], sheet_id, prefix=f"{profile}-sheet-{sheet_id}")),
            }
        )

    project_canvases: dict[str, dict[str, Any]] = {}
    for view in model["views"]:
        if view["id"] not in {"overview", "composite"}:
            continue
        raw = overview_svg if view["id"] == "overview" else composite_svg
        if raw is None:
            raise ValueError(f"VIEWER_SVG_MISSING: {view['id']}")
        canvas = view["canvases"][0]
        project_canvases[view["id"]] = {
            **canvas,
            "title": view["label"],
            "pixelWidth": round(float(canvas["width"]) * BASE_CANVAS_SCALE, 6),
            "pixelHeight": round(float(canvas["height"]) * BASE_CANVAS_SCALE, 6),
            "svg": Markup(decorate_project_svg(raw, view=view["id"], prefix=f"{profile}-{view['id']}")),
        }

    hierarchy_depth = {item["qid"]: int(item.get("depth", 0)) for item in model["hierarchy"]}
    groups: list[dict[str, Any]] = []
    for kind, label in (
        ("sheet", "Sheets"),
        ("entity", "Components"),
        ("local-net", "Local Nets"),
        ("interface", "Interface Ports"),
        ("project-net", "Project Nets"),
    ):
        entries = [
            {**item, "depth": hierarchy_depth.get(item["qid"], 0)}
            for item in model["searchIndex"]
            if item["kind"] == kind
        ]
        if entries:
            groups.append({"kind": kind, "label": label, "entries": entries})

    provenance_rows = [
        {"label": "Viewer contract", "value": model["viewerContract"]},
        {"label": "DOM contract", "value": model["domContract"]},
        {"label": "Project schema", "value": model["project"]["schema"]},
        {"label": "Renderer", "value": json.dumps(model["provenance"].get("renderer", {}), ensure_ascii=False, sort_keys=True)},
        {"label": "Resolved evidence", "value": model["provenance"].get("resolvedProjectSceneSchema") or model["provenance"].get("resolvedSceneSchema") or "unknown"},
        {"label": "Viewer state", "value": "derived, ephemeral, non-authoritative"},
    ]
    return {
        "model": model,
        "model_json": safe_json_for_script(model),
        "profile": profile,
        "profile_label": "Reference Viewer" if profile == "reference-viewer" else "Review Workbench",
        "sheet_canvases": sheet_canvases,
        "project_canvases": project_canvases,
        "navigator_groups": groups,
        "provenance_rows": provenance_rows,
        "base_canvas_scale": BASE_CANVAS_SCALE,
    }
