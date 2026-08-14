#!/usr/bin/env python3
"""Build deterministic current AIXEM authoring examples and rendered evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples" / "authoring"
RENDERER = ROOT / "implementation" / "schematic" / "render_project.py"
SCHEMA_ROOT = ROOT / "docs" / "specifications" / "schemas" / "component-graphics-1"
FIXED_DATE = "2026-08-11"
CANONICAL_LIBRARY_DIR = "library/electronics/authoring"
CANONICAL_LIBRARY_FILE = "authoring-components.aixlib.json"


def pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty(value), encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def provenance(notes: str) -> dict[str, Any]:
    return {
        "author": "AIXEM project",
        "created": FIXED_DATE,
        "license": "CC0-1.0",
        "notes": notes,
        "origin": "AIXEM 0.5.1 authoring documentation",
    }


def layers() -> list[dict[str, Any]]:
    return [
        {"id": "body", "order": 10, "purpose": "symbol body and pin leads", "defaultVisible": True, "printable": True, "locked": True},
        {"id": "fields", "order": 20, "purpose": "bound text fields", "defaultVisible": True, "printable": True, "locked": False},
    ]


def styles() -> dict[str, Any]:
    return {
        "body": {"stroke": "#0c7772", "strokeWidth": 0.65, "strokeLinecap": "square", "strokeLinejoin": "miter", "fill": "#fffef8"},
        "line": {"stroke": "#0c7772", "strokeWidth": 0.65, "strokeLinecap": "square", "strokeLinejoin": "miter", "fill": "none"},
        "field": {"stroke": "none", "fill": "#17231d", "fontFamily": "Arial, sans-serif", "fontSize": 3.5, "fontWeight": 600},
        "value": {"stroke": "none", "fill": "#4f5e56", "fontFamily": "Arial, sans-serif", "fontSize": 3.0, "fontWeight": 400},
        "detail": {"stroke": "#0c7772", "strokeWidth": 0.5, "strokeLinecap": "square", "strokeLinejoin": "miter", "fill": "none"},
    }


def base_symbol(symbol_id: str, title: str, bounds: dict[str, float], *, description: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema": "https://schemas.aixem.org/component-graphics/aixsym/1",
        "formatVersion": "1.0",
        "symbol": {
            "id": symbol_id,
            "revision": "1.0.0",
            "title": title,
            "description": description,
            "purpose": "schematic-symbol",
            "coordinateSystem": {"unit": "mm", "yAxis": "down", "angleUnit": "deg", "angleDirection": "clockwise", "grid": 2.5},
            "bounds": bounds,
            "anchors": [{"id": "origin", "x": 0, "y": 0, "kind": "insertion"}],
            "layers": layers(),
            "styles": styles(),
            "graphics": [],
            "ports": [],
            "parameters": {},
            "variants": [],
            "definitions": {},
            "paintServers": {},
            "requiredFeatures": [],
            "metadata": metadata or {},
            "provenance": provenance(description),
        },
    }


def pin_lead(port: str, x1: Any, y1: Any, x2: Any, y2: Any, endpoint: str) -> dict[str, Any]:
    return {
        "type": "line", "id": f"lead-{port}", "role": "pin-lead", "layer": "body", "style": "line",
        "metadata": {"port": port, "portEndpoint": endpoint}, "x1": x1, "y1": y1, "x2": x2, "y2": y2,
    }


def field_node(field: str, x: Any, y: Any, *, style: str = "field", anchor: str = "middle") -> dict[str, Any]:
    return {
        "type": "text", "id": f"field-{field}", "role": f"{field}-field", "layer": "fields", "style": style,
        "field": field, "x": x, "y": y, "anchor": anchor, "baseline": "middle",
    }


def resistor_symbol(*, variants: bool = False) -> dict[str, Any]:
    doc = base_symbol(
        "authoring:resistor", "Authoring resistor", {"x": -20, "y": -12.5, "width": 40, "height": 25},
        description="Two-pin passive symbol with explicit lead-to-port coincidence.", metadata={"recipe": "two-pin-passive"},
    )
    s = doc["symbol"]
    s["parameters"] = {
        "body-length": {"type": "length", "default": 20, "minimum": 10, "maximum": 30, "unit": "mm"},
        "body-height": {"type": "length", "default": 7.5, "minimum": 5, "maximum": 12.5, "unit": "mm"},
        "lead-length": {"type": "length", "default": 5, "minimum": 2.5, "maximum": 10, "unit": "mm"},
    }
    half_body = {"op": "div", "args": [{"param": "body-length"}, 2]}
    left_body = {"op": "neg", "args": [half_body]}
    left_port = {"op": "neg", "args": [{"op": "add", "args": [half_body, {"param": "lead-length"}]}]}
    right_port = {"op": "add", "args": [half_body, {"param": "lead-length"}]}
    half_height = {"op": "div", "args": [{"param": "body-height"}, 2]}
    s["graphics"] = [
        pin_lead("1", left_port, 0, left_body, 0, "start"),
        pin_lead("2", half_body, 0, right_port, 0, "end"),
        field_node("reference", 0, -7.5),
        field_node("value", 0, 7.5, style="value"),
    ]
    s["ports"] = [
        {"id": "1", "name": "1", "number": "1", "x": left_port, "y": 0, "orientation": 180, "kind": "electrical", "labelVisible": False, "numberVisible": False, "snapRadius": 1.25},
        {"id": "2", "name": "2", "number": "2", "x": right_port, "y": 0, "orientation": 0, "kind": "electrical", "labelVisible": False, "numberVisible": False, "snapRadius": 1.25},
    ]
    iec_body = {
        "type": "rect", "id": "body-iec", "role": "body", "layer": "body", "style": "body",
        "x": left_body, "y": {"op": "neg", "args": [half_height]}, "width": {"param": "body-length"}, "height": {"param": "body-height"},
    }
    if variants:
        s["defaultVariant"] = "iec"
        s["variants"] = [
            {"id": "iec", "title": "IEC rectangular body", "parameterDefaults": {"body-length": 20}, "graphics": [iec_body]},
            {
                "id": "ansi", "title": "ANSI zig-zag body", "parameterDefaults": {"body-length": 25},
                "graphics": [{"type": "polyline", "id": "body-ansi", "role": "body", "layer": "body", "style": "line", "points": [[-12.5, 0], [-10, -3.75], [-5, 3.75], [0, -3.75], [5, 3.75], [10, -3.75], [12.5, 0]]}],
            },
        ]
    else:
        s["graphics"].insert(2, iec_body)
    return doc


def connector_symbol(count: int = 6) -> dict[str, Any]:
    height = (count - 1) * 5 + 5
    top = -height / 2
    doc = base_symbol(
        "authoring:connector-6", "Six-pin connector", {"x": -15, "y": top - 7.5, "width": 30, "height": height + 15},
        description="Repeated connector pins on a five millimetre pitch.", metadata={"recipe": "connector", "pinPitch": 5},
    )
    s = doc["symbol"]
    body_left, port_x = -5, -10
    s["graphics"] = [
        {"type": "rect", "id": "body", "role": "body", "layer": "body", "style": "body", "x": body_left, "y": top, "width": 10, "height": height},
        field_node("reference", 0, top - 5),
        field_node("value", 0, top + height + 5, style="value"),
    ]
    for index in range(count):
        number = str(index + 1)
        y = top + 2.5 + index * 5
        s["graphics"].append(pin_lead(number, port_x, y, body_left, y, "start"))
        s["ports"].append({
            "id": number, "name": f"P{number}", "number": number, "x": port_x, "y": y, "orientation": 180,
            "kind": "electrical", "labelVisible": True, "numberVisible": True, "snapRadius": 1.25,
        })
    return doc


def ic_symbol() -> dict[str, Any]:
    doc = base_symbol(
        "authoring:controller-12", "Twelve-pin controller", {"x": -25, "y": -27.5, "width": 50, "height": 55},
        description="Functional twelve-pin controller with grouped signal, power, and ground ports.", metadata={"recipe": "multi-pin-ic", "pinPitch": 5},
    )
    s = doc["symbol"]
    s["graphics"] = [
        {"type": "rect", "id": "body", "role": "body", "layer": "body", "style": "body", "x": -15, "y": -15, "width": 30, "height": 30},
        field_node("reference", 0, -20), field_node("value", 0, 20, style="value"),
        {"type": "text", "id": "family", "role": "body-label", "layer": "body", "style": "field", "text": "CTRL", "x": 0, "y": 0, "anchor": "middle", "baseline": "middle"},
    ]
    left = [("1", "AIN0", -7.5, "input"), ("2", "AIN1", -2.5, "input"), ("3", "SCL", 2.5, "bidirectional"), ("4", "SDA", 7.5, "bidirectional")]
    right = [("5", "PWM0", -7.5, "output"), ("6", "PWM1", -2.5, "output"), ("7", "TX", 2.5, "output"), ("8", "RX", 7.5, "input")]
    top = [("9", "VDD", -5, "power-input"), ("10", "AVDD", 5, "power-input")]
    bottom = [("11", "GND", -5, "power-input"), ("12", "AGND", 5, "power-input")]
    for number, name, y, kind in left:
        s["graphics"].append(pin_lead(number, -20, y, -15, y, "start"))
        s["ports"].append({"id": number, "name": name, "number": number, "x": -20, "y": y, "orientation": 180, "kind": "electrical", "labelVisible": True, "numberVisible": True, "snapRadius": 1.25, "metadata": {"semanticType": kind}})
    for number, name, y, kind in right:
        s["graphics"].append(pin_lead(number, 15, y, 20, y, "end"))
        s["ports"].append({"id": number, "name": name, "number": number, "x": 20, "y": y, "orientation": 0, "kind": "electrical", "labelVisible": True, "numberVisible": True, "snapRadius": 1.25, "metadata": {"semanticType": kind}})
    for number, name, x, kind in top:
        s["graphics"].append(pin_lead(number, x, -20, x, -15, "start"))
        s["ports"].append({"id": number, "name": name, "number": number, "x": x, "y": -20, "orientation": 270, "kind": "electrical", "labelVisible": True, "numberVisible": True, "snapRadius": 1.25, "metadata": {"semanticType": kind}})
    for number, name, x, kind in bottom:
        s["graphics"].append(pin_lead(number, x, 15, x, 20, "end"))
        s["ports"].append({"id": number, "name": name, "number": number, "x": x, "y": 20, "orientation": 90, "kind": "electrical", "labelVisible": True, "numberVisible": True, "snapRadius": 1.25, "metadata": {"semanticType": kind}})
    return doc


def binding_symbol() -> dict[str, Any]:
    doc = base_symbol(
        "authoring:sensor", "Bound sensor", {"x": -20, "y": -15, "width": 40, "height": 30},
        description="Two-port sensor demonstrating semantic-to-symbol port and field binding.", metadata={"recipe": "component-binding"},
    )
    s = doc["symbol"]
    s["graphics"] = [
        {"type": "rect", "id": "body", "role": "body", "layer": "body", "style": "body", "x": -10, "y": -5, "width": 20, "height": 10},
        pin_lead("p-left", -15, 0, -10, 0, "start"), pin_lead("p-right", 10, 0, 15, 0, "end"),
        field_node("reference", 0, -10), field_node("value", 0, 10, style="value"), field_node("deviceLabel", 0, 0, style="field"),
    ]
    s["ports"] = [
        {"id": "p-left", "name": "IN", "number": "1", "x": -15, "y": 0, "orientation": 180, "kind": "electrical", "labelVisible": True, "numberVisible": True, "snapRadius": 1.25},
        {"id": "p-right", "name": "OUT", "number": "2", "x": 15, "y": 0, "orientation": 0, "kind": "electrical", "labelVisible": True, "numberVisible": True, "snapRadius": 1.25},
    ]
    return doc


def terminal_symbol() -> dict[str, Any]:
    doc = base_symbol(
        "authoring:terminal", "Single terminal", {"x": -7.5, "y": -7.5, "width": 15, "height": 15},
        description="Single-port terminal used to isolate routing examples.", metadata={"recipe": "single-terminal"},
    )
    s = doc["symbol"]
    s["graphics"] = [
        pin_lead("1", 0, 0, 5, 0, "start"),
        {"type": "circle", "id": "body", "role": "body", "layer": "body", "style": "body", "cx": 5, "cy": 0, "r": 2.5},
        field_node("reference", 5, -5),
    ]
    s["ports"] = [{"id": "1", "name": "1", "number": "1", "x": 0, "y": 0, "orientation": 180, "kind": "electrical", "labelVisible": False, "numberVisible": False, "snapRadius": 1.25}]
    return doc


def pin_semantics(name: str, port_type: str) -> dict[str, Any]:
    """Return conservative explicit semantics for synthetic generic fixtures."""
    upper = name.upper()
    if upper in {"GND", "AGND"}:
        signal_class = "ground"
        tags = ["ground"]
        domain = "agnd" if upper == "AGND" else "gnd"
    elif port_type.startswith("power-"):
        signal_class = "power"
        tags = ["power"]
        domain = upper.lower()
    elif upper.startswith("AIN"):
        signal_class = "analog"
        tags = ["sense"]
        domain = None
    else:
        signal_class = "digital" if port_type in {"input", "output", "bidirectional", "tri-state", "open-collector", "open-emitter"} else "unspecified"
        mapping = {
            "SCL": ["i2c-clock", "communication"],
            "SDA": ["i2c-data", "communication"],
            "TX": ["uart-tx", "communication"],
            "RX": ["uart-rx", "communication"],
        }
        tags = mapping.get(upper, [])
        domain = None
    semantics: dict[str, Any] = {
        "profile": "aixem-pin-semantics-1",
        "signalClass": signal_class,
        "functionalTags": tags,
        "polarity": "active-low" if upper.endswith("_N") else "unspecified",
        "capabilities": [],
    }
    if domain:
        semantics["powerDomain"] = domain
    return semantics


def component(component_id: str, title: str, ports: list[tuple[str, str, str]], symbol_path: str, symbol_doc: dict[str, Any], *, kind: str = "device", field_map: dict[str, str] | None = None, port_map: dict[str, str] | None = None, properties: list[dict[str, Any]] | None = None, default_variant: str | None = None) -> dict[str, Any]:
    canonical_symbol_path = f"{CANONICAL_LIBRARY_DIR}/{Path(symbol_path).name}"
    presentation: dict[str, Any] = {
        "purpose": "primary-diagram",
        "asset": {"path": canonical_symbol_path, "digest": "PENDING", "symbolId": symbol_doc["symbol"]["id"], "revision": symbol_doc["symbol"]["revision"]},
        "portMap": port_map or {pid: pid for pid, _name, _type in ports},
        "fieldMap": field_map or {"reference": "refdes", "value": "value"},
    }
    if default_variant:
        presentation["defaultVariant"] = default_variant
    return {
        "id": component_id, "kind": kind, "displayName": title, "description": title,
        "classification": [],
        "metadata": {
            "partProvenance": {"status": "generic-template"},
            "semanticReady": True,
        },
        "ports": [
            {
                "id": pid,
                "name": name,
                "type": ptype,
                "required": False,
                "terminal": pid,
                "metadata": {"pinSemantics": pin_semantics(name, ptype)},
            }
            for pid, name, ptype in ports
        ],
        "properties": properties or [{"id": "refdes", "type": "string", "required": False}, {"id": "value", "type": "string", "required": False}],
        "presentations": [presentation],
    }


def library_doc(library_id: str, title: str, components: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "https://schemas.aixem.org/component-graphics/aixlib/1", "formatVersion": "1.0",
        "library": {
            "id": library_id, "version": "1.0.0", "title": title, "description": title,
            "namespace": "authoring", "components": components, "dependencies": [], "metadata": {"profile": "component.graphics@1"},
            "provenance": provenance(title),
        },
    }


def layout_doc(layout_id: str, design_id: str, title: str, placements: list[dict[str, Any]], connections: list[dict[str, Any]] | None = None, annotations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "schema": "https://schemas.aixem.org/component-graphics/aixlayout/1", "formatVersion": "1.0",
        "layout": {
            "id": layout_id, "designId": design_id, "purpose": "schematic-layout",
            "coordinateSystem": {"unit": "mm", "yAxis": "down", "angleUnit": "deg", "angleDirection": "clockwise", "grid": 2.5},
            "sheet": {"width": 160, "height": 100, "margin": 10, "titleBlock": {"title": title, "drawing": layout_id, "revision": "A", "sheet": "1/1"}},
            "layers": [
                {"id": "connections", "order": 10, "purpose": "semantic net routes", "defaultVisible": True, "printable": True, "locked": False},
                {"id": "symbols", "order": 20, "purpose": "component symbols", "defaultVisible": True, "printable": True, "locked": False},
                {"id": "annotation", "order": 30, "purpose": "notes", "defaultVisible": True, "printable": True, "locked": False},
            ],
            "styles": {
                "signal": {"stroke": "#24864a", "strokeWidth": 0.65, "strokeLinecap": "square", "strokeLinejoin": "miter", "fill": "none"},
                "note": {"stroke": "none", "fill": "#1b4e8c", "fontFamily": "Arial, sans-serif", "fontSize": 3.5},
            },
            "placements": placements, "connections": connections or [], "annotations": annotations or [],
            "metadata": {"routingMode": "orthogonal", "connectionAuthority": "semantic-source-only", "styleProfile": "aixem.schematic.grid-light"},
        },
    }


def project_doc(project_id: str, title: str, design_id: str, source_path: str, layout_path: str, library_path: str, output_paths: bool = True) -> dict[str, Any]:
    outputs = []
    if output_paths:
        outputs = [
            {"role": "engineering-workbench", "path": "render/workbench.html", "mediaType": "text/html"},
            {"role": "drawing-svg", "path": "render/drawing.svg", "mediaType": "image/svg+xml"},
            {"role": "resolved-scene", "path": "render/resolved-scene.json", "mediaType": "application/json"},
        ]
    return {
        "schema": "https://schemas.aixem.org/component-graphics/aixproj/1", "formatVersion": "1.0",
        "project": {
            "id": project_id, "title": title, "description": title, "status": "example",
            "applicationProfile": "circuit.schematic@1 + component.graphics@1 + aixem.schematic.grid-light@1",
            "features": ["component.graphics@1", "explicit.layout@1", "semantic-route-binding@1", "orthogonal-routing@1", "grid-snap@1"],
            "source": {"path": source_path, "digest": "PENDING", "id": design_id, "version": "1.0", "mediaType": "application/vnd.aixem+text"},
            "layout": {"path": layout_path, "digest": "PENDING", "id": f"{design_id}-layout", "version": "1.0", "mediaType": "application/vnd.aixem.layout+json"},
            "libraries": [{"path": library_path, "digest": "PENDING", "id": f"authoring:{design_id}-library", "version": "1.0.0", "mediaType": "application/vnd.aixem.library+json"}],
            "renderPolicy": {"backend": "svg", "purpose": "primary-diagram", "remoteAssets": "deny", "fontPolicy": "system-fallback", "unsupportedRequiredFeature": "reject", "defaultVariantPolicy": "library-default"},
            "outputs": outputs, "metadata": {"exampleDomain": "agent-authoring", "independentDesign": True, "styleProfile": "aixem.schematic.grid-light"},
            "provenance": {"author": "AIXEM project", "created": FIXED_DATE, "license": "CC0-1.0"},
        },
    }


def source_text(design_id: str, title: str, entities: list[str], nets: list[str], noconns: list[str]) -> str:
    lines = ["aixem 1.0", f'model {design_id} title="{title}"', "feature component.graphics@1 required=true", "feature explicit.layout@1 required=true", ""]
    lines.extend(entities)
    if nets:
        lines.append("")
        lines.extend(nets)
    if noconns:
        lines.append("")
        lines.extend(f"noconn {item}" for item in noconns)
    return "\n".join(lines) + "\n"


def make_example(name: str, title: str, design_id: str, symbols: dict[str, dict[str, Any]], components: list[dict[str, Any]], source: str, layout: dict[str, Any], readme: str, *, repair_report: dict[str, Any] | None = None) -> Path:
    root = EXAMPLES / name
    if root.exists():
        shutil.rmtree(root)
    library_root = root / CANONICAL_LIBRARY_DIR
    library_root.mkdir(parents=True)
    for filename, doc in symbols.items():
        write_json(library_root / filename, doc)
    # Replace locked asset digests after symbols exist.
    for item in components:
        for presentation in item["presentations"]:
            presentation["asset"]["digest"] = digest(root / presentation["asset"]["path"])
    library_path = root / CANONICAL_LIBRARY_DIR / CANONICAL_LIBRARY_FILE
    write_json(library_path, library_doc(f"authoring:{design_id}-library", f"{title} library", components))
    source_path = root / f"{design_id}.aixem"
    layout_path = root / f"{design_id}.aixlayout.json"
    write_text(source_path, source)
    write_json(layout_path, layout)
    project = project_doc(f"authoring:{design_id}", title, design_id, source_path.name, layout_path.name, f"{CANONICAL_LIBRARY_DIR}/{CANONICAL_LIBRARY_FILE}")
    project["project"]["source"]["digest"] = digest(source_path)
    project["project"]["layout"]["digest"] = digest(layout_path)
    project["project"]["libraries"][0]["digest"] = digest(library_path)
    write_json(root / "project.aixproj.json", project)
    write_text(root / "README.md", readme)
    if repair_report:
        write_json(root / "evidence" / "repair-report.json", repair_report)
    return root


def build_examples() -> list[Path]:
    if EXAMPLES.exists():
        shutil.rmtree(EXAMPLES)
    EXAMPLES.mkdir(parents=True)
    built: list[Path] = []

    # 01 — two-pin passive.
    sym = resistor_symbol()
    comp = component("authoring:resistor", "Resistor", [("1", "1", "passive"), ("2", "2", "passive")], "symbols/resistor.aixsym.json", sym, kind="passive")
    design = "two_pin_passive"
    source = source_text(design, "Two-pin passive", [
        "component R1 type=authoring:resistor refdes=R1 value=10k",
        "component R2 type=authoring:resistor refdes=R2 value=22k",
    ], ["net link = R1.2 R2.1"], ["R1.1", "R2.2"])
    layout = layout_doc(f"{design}-layout", design, "Two-pin passive", [
        {"entity": "R1", "x": 45, "y": 50, "layer": "symbols"},
        {"entity": "R2", "x": 85, "y": 50, "layer": "symbols"},
    ], [{"net": "link", "layer": "connections", "style": "signal", "paths": [{"from": {"endpoint": "R1.2"}, "to": {"endpoint": "R2.1"}}]}])
    built.append(make_example("01-two-pin-passive", "Two-pin Passive Authoring", design, {"resistor.aixsym.json": sym}, [comp], source, layout,
        """# Two-pin Passive Authoring Example

This executable fixture proves body and lead geometry, exact lead-to-port coincidence, reference/value field binding, total port mapping, placement, and a straight semantic route.

Run `python implementation/schematic/render_project.py examples/authoring/01-two-pin-passive/project.aixproj.json` from the repository root.
"""))

    # 02 — connector.
    sym = connector_symbol()
    ports = [(str(i), f"P{i}", "passive") for i in range(1, 7)]
    comp = component("authoring:connector-6", "Six-pin connector", ports, "symbols/connector-6.aixsym.json", sym, kind="connector")
    design = "connector_6"
    source = source_text(design, "Six-pin connector", ["connector J1 type=authoring:connector-6 refdes=J1 value=FIELD_IO"], [], [f"J1.{i}" for i in range(1, 7)])
    layout = layout_doc(f"{design}-layout", design, "Six-pin connector", [{"entity": "J1", "x": 80, "y": 40, "layer": "symbols"}])
    built.append(make_example("02-connector", "Connector Authoring", design, {"connector-6.aixsym.json": sym}, [comp], source, layout,
        """# Connector Authoring Example

This executable fixture proves six pins on a 5 mm pitch, deterministic numbering and naming, a body derived from pin count, and total semantic-to-symbol port mapping.
"""))

    # 03 — multi-pin IC.
    sym = ic_symbol()
    port_types = {str(i): "passive" for i in range(1, 13)}
    for i in (1, 2, 4, 8): port_types[str(i)] = "input"
    for i in (5, 6, 7): port_types[str(i)] = "output"
    for i in (3,): port_types[str(i)] = "bidirectional"
    for i in (9, 10, 11, 12): port_types[str(i)] = "power-input"
    ports = [(str(i), next(p["name"] for p in sym["symbol"]["ports"] if p["id"] == str(i)), port_types[str(i)]) for i in range(1, 13)]
    comp = component("authoring:controller-12", "Twelve-pin controller", ports, "symbols/controller-12.aixsym.json", sym, kind="integrated-circuit")
    design = "controller_12"
    source = source_text(design, "Twelve-pin controller", ["component U1 type=authoring:controller-12 refdes=U1 value=AXC12"], [], [f"U1.{i}" for i in range(1, 13)])
    layout = layout_doc(f"{design}-layout", design, "Twelve-pin controller", [{"entity": "U1", "x": 80, "y": 40, "layer": "symbols"}])
    built.append(make_example("03-multi-pin-ic", "Multi-pin IC Authoring", design, {"controller-12.aixsym.json": sym}, [comp], source, layout,
        """# Multi-pin IC Authoring Example

This executable fixture proves functional pin grouping, left/right signal flow, top power pins, bottom ground pins, five millimetre pitch, compact body sizing, and automatic pin-name/number overlays.
"""))

    # 04 — parameterized variants and precedence.
    sym = resistor_symbol(variants=True)
    comp = component("authoring:resistor", "Variant resistor", [("1", "1", "passive"), ("2", "2", "passive")], "symbols/resistor-variant.aixsym.json", sym, kind="passive", default_variant="ansi")
    design = "parameterized_variant"
    source = source_text(design, "Parameterized variant", [
        "component R1 type=authoring:resistor refdes=R1 value=47k",
        "component R2 type=authoring:resistor refdes=R2 value=100k",
    ], ["net series = R1.2 R2.1"], ["R1.1", "R2.2"])
    layout = layout_doc(f"{design}-layout", design, "Parameterized variant", [
        {"entity": "R1", "x": 42.5, "y": 50, "layer": "symbols", "parameters": {"body-length": 30}},
        {"entity": "R2", "x": 100, "y": 50, "layer": "symbols", "variant": "iec", "parameters": {"body-height": 10}},
    ], [{"net": "series", "layer": "connections", "style": "signal", "paths": [{"from": {"endpoint": "R1.2"}, "to": {"endpoint": "R2.1"}, "via": [[72.5, 50], [80, 50]]}]}])
    built.append(make_example("04-parameterized-variant", "Parameterized Variant Authoring", design, {"resistor-variant.aixsym.json": sym}, [comp], source, layout,
        """# Parameterized Variant Authoring Example

`R1` inherits the library presentation default variant (`ansi`) and its placement overrides the variant body length. `R2` explicitly selects `iec` and overrides body height. The resolved scene records the resulting variant and parameter values.
"""))

    # 05 — field and port binding.
    sym = binding_symbol()
    properties = [
        {"id": "refdes", "type": "string", "required": False},
        {"id": "rating", "type": "string", "required": False},
        {"id": "label", "type": "string", "required": False},
    ]
    comp = component(
        "authoring:sensor", "Bound sensor", [("in", "Input", "input"), ("out", "Output", "output")],
        "symbols/sensor.aixsym.json", sym, kind="sensor", field_map={"reference": "refdes", "value": "rating", "deviceLabel": "label"},
        port_map={"in": "p-left", "out": "p-right"}, properties=properties,
    )
    design = "field_port_binding"
    source = source_text(design, "Field and port binding", ["component S1 type=authoring:sensor refdes=S1 rating=3V3 label=TEMP"], [], ["S1.in", "S1.out"])
    layout = layout_doc(f"{design}-layout", design, "Field and port binding", [{"entity": "S1", "x": 80, "y": 50, "layer": "symbols", "fields": {"value": "5V_OVERRIDE"}}])
    built.append(make_example("05-field-and-port-binding", "Field and Port Binding", design, {"sensor.aixsym.json": sym}, [comp], source, layout,
        """# Field and Port Binding Example

The component semantic ports `in` and `out` map to symbol ports `p-left` and `p-right`. Semantic properties map to `reference`, `value`, and `deviceLabel`; the placement-level `value` override wins and renders as `5V_OVERRIDE`.
"""))

    # 06 — two-terminal orthogonal route.
    sym = terminal_symbol()
    comp = component("authoring:terminal", "Terminal", [("1", "1", "passive")], "symbols/terminal.aixsym.json", sym, kind="connector")
    design = "two_terminal_route"
    source = source_text(design, "Two-terminal route", [
        "connector T1 type=authoring:terminal refdes=T1 value=SOURCE",
        "connector T2 type=authoring:terminal refdes=T2 value=SINK",
    ], ["net signal = T1.1 T2.1"], [])
    layout = layout_doc(f"{design}-layout", design, "Two-terminal route", [
        {"entity": "T1", "x": 40, "y": 35, "layer": "symbols"},
        {"entity": "T2", "x": 120, "y": 60, "layer": "symbols"},
    ], [{"net": "signal", "layer": "connections", "style": "signal", "paths": [{"from": {"endpoint": "T1.1"}, "to": {"endpoint": "T2.1"}, "via": [[80, 35], [80, 60]]}], "labels": [{"text": "SIGNAL", "x": 82.5, "y": 32.5}]}])
    built.append(make_example("06-two-terminal-route", "Two-terminal Routing", design, {"terminal.aixsym.json": sym}, [comp], source, layout,
        """# Two-terminal Routing Example

This executable fixture shows semantic endpoint membership and a one-channel orthogonal route with two explicit bends. Geometry remains in `.aixlayout.json`; net membership remains in `.aixem`.
"""))

    # 07 — multi-terminal junction plus unrelated crossing.
    sym = terminal_symbol()
    comp = component("authoring:terminal", "Terminal", [("1", "1", "passive")], "symbols/terminal.aixsym.json", sym, kind="connector")
    design = "multi_terminal_junction"
    source = source_text(design, "Multi-terminal junction", [
        *[f"connector T{i} type=authoring:terminal refdes=T{i} value=T{i}" for i in range(1, 6)]
    ], ["net bus = T1.1 T2.1 T3.1", "net cross = T4.1 T5.1"], [])
    placements = [
        {"entity": "T1", "x": 25, "y": 50, "layer": "symbols"},
        {"entity": "T2", "x": 85, "y": 25, "layer": "symbols"},
        {"entity": "T3", "x": 115, "y": 50, "layer": "symbols"},
        {"entity": "T4", "x": 85, "y": 35, "layer": "symbols"},
        {"entity": "T5", "x": 85, "y": 65, "layer": "symbols"},
    ]
    connections = [
        {"net": "bus", "layer": "connections", "style": "signal", "paths": [
            {"from": {"endpoint": "T1.1"}, "to": {"point": [75, 50]}},
            {"from": {"endpoint": "T2.1"}, "to": {"point": [75, 50]}, "via": [[75, 25]]},
            {"from": {"endpoint": "T3.1"}, "to": {"point": [75, 50]}},
        ], "junctions": [[75, 50]], "labels": [{"text": "BUS", "x": 77.5, "y": 47.5}]},
        {"net": "cross", "layer": "connections", "style": "signal", "paths": [
            {"from": {"endpoint": "T4.1"}, "to": {"endpoint": "T5.1"}}
        ], "labels": [{"text": "CROSS / NO JUNCTION", "x": 95, "y": 42.5}]},
    ]
    layout = layout_doc(f"{design}-layout", design, "Multi-terminal junction", placements, connections)
    built.append(make_example("07-multi-terminal-junction", "Multi-terminal Junction", design, {"terminal.aixsym.json": sym}, [comp], source, layout,
        """# Multi-terminal Junction Example

The `bus` net has three semantic endpoints and three route branches meeting at one explicit junction. The unrelated `cross` net intersects the bus geometry without sharing semantic membership or a bus junction marker.
"""))

    # 08 — visual repair fixture and corrected project.
    repaired = resistor_symbol()
    broken = copy.deepcopy(repaired)
    broken["symbol"]["id"] = "authoring:broken-resistor"
    broken["symbol"]["title"] = "Broken lead/port fixture"
    # Make the visible left lead stop 2.5 mm short of the electrical port while remaining schema-valid.
    broken["symbol"]["graphics"][0]["x1"] = -12.5
    comp = component("authoring:resistor", "Repaired resistor", [("1", "1", "passive"), ("2", "2", "passive")], "symbols/repaired-resistor.aixsym.json", repaired, kind="passive")
    design = "visual_repair"
    source = source_text(design, "Visual repair", ["component R1 type=authoring:resistor refdes=R1 value=1k"], [], ["R1.1", "R1.2"])
    layout = layout_doc(f"{design}-layout", design, "Visual repair", [{"entity": "R1", "x": 80, "y": 50, "layer": "symbols"}])
    root = make_example("08-visual-repair", "Visual Repair", design, {"repaired-resistor.aixsym.json": repaired}, [comp], source, layout,
        """# Visual Repair Example

`fixtures/broken-lead-port.aixsym.json` is intentionally schema-valid but violates the symbol design profile: the left visible lead endpoint does not coincide with port `1`. The project uses the repaired asset, and `evidence/repair-report.json` records the authority-layer diagnosis and correction.
""", repair_report={
            "schema": "https://schemas.aixem.org/validation/visual-repair/1", "formatVersion": "1.0", "generatedAt": "2026-08-11T00:00:00Z", "status": "pass",
            "symptom": "Left wire target would be separated from the visible pin lead.", "owner": "symbol asset geometry",
            "broken": {"path": "fixtures/broken-lead-port.aixsym.json", "port": "1", "leadEndpoint": [-12.5, 0], "portCoordinate": [-15, 0]},
            "repair": {"path": "library/electronics/authoring/repaired-resistor.aixsym.json", "leadEndpoint": [-15, 0], "portCoordinate": [-15, 0]},
        })
    write_json(root / "fixtures" / "broken-lead-port.aixsym.json", broken)
    built.append(root)

    index = {
        "schema": "https://schemas.aixem.org/examples/authoring-index/1", "formatVersion": "1.0", "release": "AIXEM-SRP-0.5.9-2026-08-12",
        "generatedAt": "2026-08-11T00:00:00Z",
        "examples": [{"id": path.name, "project": f"examples/authoring/{path.name}/project.aixproj.json", "readme": f"examples/authoring/{path.name}/README.md"} for path in built],
    }
    write_json(EXAMPLES / "index.json", index)
    write_text(EXAMPLES / "README.md", """# AIXEM Authoring Golden Examples

These deterministic fixtures back the current authoring manuals and canonical project-local library structure. Every successful project validates against the active schemas, renders locally with locked inputs, and emits `resolved-scene.json`, SVG, workbench HTML, and project-validation evidence.

## Registered Examples

- [01 — Two-pin passive](01-two-pin-passive/README.md)
- [02 — Connector](02-connector/README.md)
- [03 — Multi-pin IC](03-multi-pin-ic/README.md)
- [04 — Parameterized variant](04-parameterized-variant/README.md)
- [05 — Field and port binding](05-field-and-port-binding/README.md)
- [06 — Two-terminal route](06-two-terminal-route/README.md)
- [07 — Multi-terminal junction](07-multi-terminal-junction/README.md)
- [08 — Visual repair](08-visual-repair/README.md)

The `08-visual-repair/fixtures` directory contains a deliberately defective design-profile fixture; it is not a successful canonical symbol.
""")
    return built


def render_examples(paths: list[Path]) -> None:
    for root in paths:
        command = [sys.executable, str(RENDERER), str(root / "project.aixproj.json"), "--schema-root", str(SCHEMA_ROOT), "--output-dir", str(root / "render"), "--validation-out", str(root / "evidence" / "project-validation.json")]
        proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if proc.returncode != 0:
            raise RuntimeError(f"render failed for {root.name}:\n{proc.stdout}\n{proc.stderr}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-render", action="store_true", help="Write source fixtures without renderer outputs.")
    args = parser.parse_args()
    paths = build_examples()
    if not args.no_render:
        render_examples(paths)
    print(f"authoring examples: {len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
