#!/usr/bin/env python3
"""Build the deterministic AIXEM hierarchical-project conformance corpus."""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import re
import shutil
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ROOT / "validation" / "corpus" / "hierarchical-project-1"
BASE_LIBRARY = ROOT / "examples" / "authoring" / "03-multi-pin-ic" / "libraries" / "authoring.aixlib.json"
BASE_SYMBOL = ROOT / "examples" / "authoring" / "03-multi-pin-ic" / "symbols" / "controller-12.aixsym.json"

PORTS: dict[str, dict[str, Any]] = {
    "VCC": {"endpoint": "U1.9", "direction": "input", "role": "power", "side": "top", "xy": (75.0, 10.0)},
    "GND": {"endpoint": "U1.11", "direction": "passive", "role": "power", "side": "bottom", "xy": (75.0, 90.0)},
    "IN": {"endpoint": "U1.1", "direction": "input", "role": "signal", "side": "left", "xy": (10.0, 42.5)},
    "OUT": {"endpoint": "U1.5", "direction": "output", "role": "signal", "side": "right", "xy": (150.0, 42.5)},
    "CLK": {"endpoint": "U1.3", "direction": "input", "role": "clock", "side": "left", "xy": (10.0, 52.5)},
    "STATUS": {"endpoint": "U1.7", "direction": "output", "role": "signal", "side": "right", "xy": (150.0, 52.5)},
    "RESET": {"endpoint": "U1.2", "direction": "input", "role": "reset", "side": "left", "xy": (10.0, 47.5)},
    "ENABLE": {"endpoint": "U1.4", "direction": "input", "role": "control", "side": "left", "xy": (10.0, 57.5)},
    "AUX": {"endpoint": "U1.10", "direction": "passive", "role": "power", "side": "top", "xy": (85.0, 10.0)},
}

COMPONENT_POINTS = {
    "U1.1": (60.0, 42.5), "U1.2": (60.0, 47.5), "U1.3": (60.0, 52.5), "U1.4": (60.0, 57.5),
    "U1.5": (100.0, 42.5), "U1.6": (100.0, 47.5), "U1.7": (100.0, 52.5), "U1.8": (100.0, 57.5),
    "U1.9": (75.0, 30.0), "U1.10": (85.0, 30.0), "U1.11": (75.0, 70.0), "U1.12": (85.0, 70.0),
}
ALL_ENDPOINTS = [f"U1.{index}" for index in range(1, 13)]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value), encoding="utf-8", newline="\n")


def digest(path: pathlib.Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def file_ref(path: str, absolute: pathlib.Path, media_type: str, *, ref_id: str | None = None, version: str = "1.0") -> dict[str, Any]:
    ref: dict[str, Any] = {"path": path, "digest": digest(absolute), "mediaType": media_type, "version": version}
    if ref_id:
        ref["id"] = ref_id
    return ref


def copy_assets(case_dir: pathlib.Path) -> dict[str, Any]:
    symbol_path = case_dir / "symbols" / "controller-12.aixsym.json"
    library_path = case_dir / "libraries" / "authoring.aixlib.json"
    symbol_path.parent.mkdir(parents=True, exist_ok=True)
    library_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(BASE_SYMBOL, symbol_path)
    library = json.loads(BASE_LIBRARY.read_text(encoding="utf-8"))
    library["library"]["components"][0]["presentations"][0]["asset"]["digest"] = digest(symbol_path)
    write_json(library_path, library)
    return file_ref(
        "libraries/authoring.aixlib.json", library_path,
        "application/vnd.aixem.library+json", ref_id="hierarchical:reference-library", version="1.0.0",
    )


def route_points(endpoint: str, target: tuple[float, float]) -> list[list[float]]:
    start = COMPONENT_POINTS[endpoint]
    if abs(start[0] - target[0]) < 1e-9 or abs(start[1] - target[1]) < 1e-9:
        return []
    # Horizontal escape first; all coordinates are on the 2.5 mm reference grid.
    return [[target[0], start[1]]]


def make_source(model_id: str, title: str, interface_ports: list[str], *, shared_groups: list[list[str]] | None = None) -> str:
    shared_groups = shared_groups or []
    lines = [
        "aixem 1.0",
        f'model {model_id} title="{title}"',
        "feature component.graphics@1 required=true",
        "feature explicit.layout@2 required=true",
        "feature hierarchical.interface@1 required=true",
        "",
    ]
    for port_id in interface_ports:
        spec = PORTS[port_id]
        lines.append(f"port {port_id} direction={spec['direction']} role={spec['role']} label={port_id}")
    lines.extend(["", "component U1 type=authoring:controller-12 refdes=U1 value=AXC12", ""])
    grouped: set[str] = set()
    for group_index, group in enumerate(shared_groups, 1):
        first = group[0]
        endpoint = PORTS[first]["endpoint"]
        grouped.update(group)
        lines.append(f"net shared_{group_index} = {endpoint} " + " ".join(f"@{item}" for item in group))
    for port_id in interface_ports:
        if port_id in grouped:
            continue
        spec = PORTS[port_id]
        lines.append(f"net {port_id.lower()} = {spec['endpoint']} @{port_id}")
    used_component_endpoints = {PORTS[item]["endpoint"] for item in interface_ports}
    for endpoint in ALL_ENDPOINTS:
        if endpoint not in used_component_endpoints:
            lines.append(f"noconn {endpoint}")
    return "\n".join(lines) + "\n"


def make_layout(model_id: str, title: str, interface_ports: list[str], *, shared_groups: list[list[str]] | None = None) -> dict[str, Any]:
    shared_groups = shared_groups or []
    shared_owner: dict[str, str] = {}
    for index, group in enumerate(shared_groups, 1):
        for port_id in group:
            shared_owner[port_id] = f"shared_{index}"
    connections: list[dict[str, Any]] = []
    grouped_done: set[str] = set()
    for port_id in interface_ports:
        spec = PORTS[port_id]
        net_id = shared_owner.get(port_id, port_id.lower())
        if net_id in grouped_done:
            continue
        if net_id.startswith("shared_"):
            group = next(group for group in shared_groups if port_id in group)
            origin_endpoint = PORTS[group[0]]["endpoint"]
            paths = []
            for member in group:
                target = tuple(PORTS[member]["xy"])
                path: dict[str, Any] = {"from": {"endpoint": origin_endpoint}, "to": {"endpoint": f"@{member}"}}
                via = route_points(origin_endpoint, target)
                if via:
                    path["via"] = via
                paths.append(path)
            connections.append({"net": net_id, "layer": "connections", "paths": paths})
            grouped_done.add(net_id)
        else:
            target = tuple(spec["xy"])
            path = {"from": {"endpoint": spec["endpoint"]}, "to": {"endpoint": f"@{port_id}"}}
            via = route_points(spec["endpoint"], target)
            if via:
                path["via"] = via
            connections.append({"net": net_id, "layer": "connections", "paths": [path]})
    sheet_ports = [
        {"port": port_id, "x": PORTS[port_id]["xy"][0], "y": PORTS[port_id]["xy"][1], "side": PORTS[port_id]["side"], "layer": "connections", "label": port_id}
        for port_id in interface_ports
    ]
    return {
        "schema": "https://schemas.aixem.org/component-graphics/aixlayout/2",
        "formatVersion": "2.0",
        "layout": {
            "id": f"{model_id}-layout", "designId": model_id, "purpose": "schematic-layout",
            "coordinateSystem": {"unit": "mm", "yAxis": "down", "angleUnit": "deg", "angleDirection": "clockwise", "grid": 2.5},
            "sheet": {"width": 160, "height": 100, "margin": 10, "titleBlock": {"title": title, "drawing": model_id, "revision": "A", "sheet": "1/1"}},
            "layers": [
                {"id": "connections", "order": 10, "purpose": "semantic net routes and sheet ports", "defaultVisible": True, "locked": False, "printable": True},
                {"id": "symbols", "order": 20, "purpose": "component symbols", "defaultVisible": True, "locked": False, "printable": True},
                {"id": "annotation", "order": 30, "purpose": "notes", "defaultVisible": True, "locked": False, "printable": True},
            ],
            "styles": {
                "signal": {"fill": "none", "stroke": "#24864a", "strokeLinecap": "square", "strokeLinejoin": "miter", "strokeWidth": 0.65},
                "note": {"fill": "#1b4e8c", "stroke": "none", "fontFamily": "Arial, sans-serif", "fontSize": 3.5},
            },
            "placements": [{"entity": "U1", "x": 80, "y": 50, "layer": "symbols"}],
            "sheetPorts": sheet_ports,
            "connections": connections,
            "annotations": [],
            "metadata": {"connectionAuthority": "semantic-source-only", "structuralOwnership": "Project -> Sheet -> Layer", "routingMode": "orthogonal"},
        },
    }


def write_leaf(case_dir: pathlib.Path, sheet_id: str, ports: list[str], *, parent: str | None = None, order: int | None = None, shared_groups: list[list[str]] | None = None) -> dict[str, Any]:
    case_token = re.sub(r"[^a-z0-9]+", "-", case_dir.name.lower()).strip("-")
    model_id = f"{case_token}:{sheet_id}"
    title = sheet_id.replace("-", " ").title()
    source_path = case_dir / "circuits" / f"{sheet_id}.aixem"
    layout_path = case_dir / "layouts" / f"{sheet_id}.aixlayout.json"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(make_source(model_id, title, ports, shared_groups=shared_groups), encoding="utf-8", newline="\n")
    write_json(layout_path, make_layout(model_id, title, ports, shared_groups=shared_groups))
    record: dict[str, Any] = {
        "id": sheet_id,
        "title": title,
        "source": file_ref(f"circuits/{sheet_id}.aixem", source_path, "text/x-aixem", ref_id=model_id),
        "layout": file_ref(f"layouts/{sheet_id}.aixlayout.json", layout_path, "application/json", ref_id=f"{model_id}-layout", version="2.0"),
    }
    if parent is not None:
        record["parent"] = parent
    if order is not None:
        record["order"] = order
    return record


def project_doc(case_id: str, title: str, sheets: list[dict[str, Any]], project_nets: list[dict[str, Any]], library_ref: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "https://schemas.aixem.org/component-graphics/aixproj/2",
        "formatVersion": "2.0",
        "project": {
            "id": f"hierarchical:{case_id.lower()}", "title": title,
            "description": f"Hierarchical conformance case {case_id}: {title}",
            "applicationProfile": "aixem.schematic.multisheet@1",
            "sheets": sheets, "projectNets": project_nets, "libraries": [library_ref],
            "features": ["component.graphics@1", "explicit.layout@2", "hierarchical.interface@1", "project-net@1", "deterministic-project-routing@1"],
            "renderPolicy": {"purpose": "primary-diagram", "backend": "svg", "fontPolicy": "system-fallback", "remoteAssets": "deny", "defaultVariantPolicy": "library-default", "unsupportedRequiredFeature": "reject"},
            "status": "example",
            "metadata": {"corpus": "hierarchical-project-1", "case": case_id, "geometryCreatesConnectivity": False, "layersAreSheets": False},
            "provenance": {"author": "AIXEM project", "created": "2026-08-11", "license": "CC0-1.0"},
            "outputs": [
                {"role": "project-overview-svg", "path": "render/project-overview.svg", "mediaType": "image/svg+xml"},
                {"role": "project-composite-svg", "path": "render/project-composite.svg", "mediaType": "image/svg+xml"},
                {"role": "resolved-project-scene", "path": "render/resolved-project-scene.json", "mediaType": "application/json"},
                {"role": "engineering-workbench", "path": "render/workbench.html", "mediaType": "text/html"},
            ],
        },
    }


def write_case(case_id: str, title: str, sheet_specs: list[tuple[str, list[str], str | None, int | None, list[list[str]] | None]], project_nets: list[dict[str, Any]], *, expected: str = "pass", diagnostic: str | None = None, assertions: list[str] | None = None) -> pathlib.Path:
    case_dir = CORPUS / "cases" / f"{case_id}-{title.lower().replace(' ', '-').replace('/', '-')}"
    case_dir.mkdir(parents=True, exist_ok=True)
    library_ref = copy_assets(case_dir)
    sheets = [write_leaf(case_dir, sid, ports, parent=parent, order=order, shared_groups=groups) for sid, ports, parent, order, groups in sheet_specs]
    write_json(case_dir / "project.aixproj.json", project_doc(case_id, title, sheets, project_nets, library_ref))
    write_json(case_dir / "case.json", {
        "id": case_id, "title": title, "expected": expected,
        "expectedDiagnostic": diagnostic,
        "assertions": assertions or [],
        "project": "project.aixproj.json",
    })
    return case_dir


def member(sheet: str, port: str) -> dict[str, str]:
    return {"sheet": sheet, "port": port}


def net(net_id: str, *members: tuple[str, str], role: str | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"id": net_id, "members": [member(sheet, port) for sheet, port in members]}
    if role:
        value["role"] = role
    return value


def make_legacy_case() -> None:
    case_id, title = "H012", "Legacy aixproj v1"
    case_dir = CORPUS / "cases" / "H012-legacy-aixproj-v1"
    case_dir.mkdir(parents=True, exist_ok=True)
    library_ref = copy_assets(case_dir)
    source = case_dir / "legacy.aixem"
    source.write_text(
        "aixem 1.0\nmodel legacy_h012 title=\"Legacy single sheet\"\nfeature component.graphics@1 required=true\nfeature explicit.layout@1 required=true\n\ncomponent U1 type=authoring:controller-12 refdes=U1 value=AXC12\n"
        + "".join(f"noconn U1.{index}\n" for index in range(1, 13)),
        encoding="utf-8", newline="\n",
    )
    layout = make_layout("legacy_h012", "Legacy single sheet", [])
    layout["schema"] = "https://schemas.aixem.org/component-graphics/aixlayout/1"
    layout["formatVersion"] = "1.0"
    layout["layout"].pop("sheetPorts", None)
    layout_path = case_dir / "legacy.aixlayout.json"
    write_json(layout_path, layout)
    project = {
        "schema": "https://schemas.aixem.org/component-graphics/aixproj/1", "formatVersion": "1.0",
        "project": {
            "id": "hierarchical:h012-legacy", "title": title,
            "applicationProfile": "circuit.schematic@1 + component.graphics@1",
            "source": file_ref("legacy.aixem", source, "application/vnd.aixem+text", ref_id="legacy_h012"),
            "layout": file_ref("legacy.aixlayout.json", layout_path, "application/vnd.aixem.layout+json", ref_id="legacy_h012-layout"),
            "libraries": [library_ref],
            "renderPolicy": {"purpose": "primary-diagram", "backend": "svg", "fontPolicy": "system-fallback", "remoteAssets": "deny", "defaultVariantPolicy": "library-default", "unsupportedRequiredFeature": "reject"},
            "features": ["component.graphics@1", "explicit.layout@1"], "status": "example",
            "metadata": {"corpus": "hierarchical-project-1", "case": case_id},
            "outputs": [], "provenance": {"author": "AIXEM project", "created": "2026-08-11", "license": "CC0-1.0"},
        },
    }
    write_json(case_dir / "project.aixproj.json", project)
    write_json(case_dir / "case.json", {"id": case_id, "title": title, "expected": "pass", "project": "project.aixproj.json", "assertions": ["legacy-v1-output-path", "legacy-v1-behavior"]})


def mutate_negative(case_id: str, title: str, mutator: Any, diagnostic: str, *, expected: str = "fail") -> None:
    template = CORPUS / "cases" / "H001-two-sheet-power-+-control"
    case_dir = CORPUS / "negative" / f"{case_id}-{title.lower().replace(' ', '-').replace('/', '-')}"
    if case_dir.exists():
        shutil.rmtree(case_dir)
    shutil.copytree(template, case_dir)
    for generated in (case_dir / "render", case_dir / "evidence"):
        if generated.exists():
            shutil.rmtree(generated)
    mutator(case_dir)
    # Re-lock every reference except when the fixture deliberately tests a digest mismatch.
    project_path = case_dir / "project.aixproj.json"
    project = json.loads(project_path.read_text(encoding="utf-8"))
    preserve_source_mismatch = diagnostic in {"source digest mismatch", "PROJECT_REFERENCE_DIGEST_CONFLICT"}
    preserve_layout_mismatch = diagnostic == "layout digest mismatch"
    for sheet in project["project"]["sheets"]:
        source_path = case_dir / sheet["source"]["path"]
        layout_path = case_dir / sheet["layout"]["path"]
        if not preserve_source_mismatch:
            sheet["source"]["digest"] = digest(source_path)
        if not preserve_layout_mismatch:
            sheet["layout"]["digest"] = digest(layout_path)
    lib_ref = project["project"]["libraries"][0]
    lib_ref["digest"] = digest(case_dir / lib_ref["path"])
    write_json(project_path, project)
    write_json(case_dir / "case.json", {"id": case_id, "title": title, "expected": expected, "expectedDiagnostic": diagnostic, "project": "project.aixproj.json", "assertions": []})


def refresh_refs(case_dir: pathlib.Path) -> None:
    project_path = case_dir / "project.aixproj.json"
    project = json.loads(project_path.read_text(encoding="utf-8"))
    for sheet in project["project"]["sheets"]:
        sheet["source"]["digest"] = digest(case_dir / sheet["source"]["path"])
        sheet["layout"]["digest"] = digest(case_dir / sheet["layout"]["path"])
    project["project"]["libraries"][0]["digest"] = digest(case_dir / project["project"]["libraries"][0]["path"])
    write_json(project_path, project)


def build() -> None:
    if CORPUS.exists():
        shutil.rmtree(CORPUS)
    (CORPUS / "cases").mkdir(parents=True)
    (CORPUS / "negative").mkdir(parents=True)
    (CORPUS / "results").mkdir(parents=True)

    base_sheets = [
        ("power", ["VCC", "GND", "OUT"], None, 10, None),
        ("control", ["VCC", "GND", "IN"], None, 20, None),
    ]
    base_nets = [net("vcc_5v", ("power", "VCC"), ("control", "VCC"), role="power"), net("gnd", ("power", "GND"), ("control", "GND"), role="power"), net("control_signal", ("power", "OUT"), ("control", "IN"), role="signal")]
    write_case("H001", "Two sheet power + control", base_sheets, base_nets, assertions=["explicit-interface-closure", "project-net-closure"])
    write_case("H002", "Single local endpoint + interface port", [("source", ["OUT"], None, 10, None), ("sink", ["IN"], None, 20, None)], [net("signal", ("source", "OUT"), ("sink", "IN"))], assertions=["two-semantic-endpoints-per-local-net"])
    write_case("H003", "Three sheet VCC GND fanout", [("power", ["VCC", "GND"], None, 10, None), ("control", ["VCC", "GND"], None, 20, None), ("io", ["VCC", "GND"], None, 30, None)], [net("vcc_5v", ("power", "VCC"), ("control", "VCC"), ("io", "VCC"), role="power"), net("gnd", ("power", "GND"), ("control", "GND"), ("io", "GND"), role="power")], assertions=["multi-member-project-net"])
    write_case("H004", "Same name local nets not connected", [("alpha", ["VCC", "GND"], None, 10, None), ("beta", ["VCC", "GND"], None, 20, None)], [], assertions=["same-name-isolation", "zero-implicit-project-nets"])
    write_case("H005", "Three level sheet hierarchy", [("system", ["VCC"], None, 10, None), ("control", ["VCC", "OUT"], "system", 10, None), ("debug", ["IN"], "control", 10, None)], [net("vcc", ("system", "VCC"), ("control", "VCC"), role="power"), net("debug_signal", ("control", "OUT"), ("debug", "IN"))], assertions=["hierarchy-depth-two", "organizational-hierarchy-only"])
    h006_nets = [net("vcc_5v", ("driver", "VCC"), ("receiver", "VCC"), role="power"), net("gnd", ("driver", "GND"), ("receiver", "GND"), role="power"), net("control_signal", ("driver", "OUT"), ("receiver", "IN"), role="signal")]
    write_case("H006", "Interface port local routing", [("driver", ["VCC", "GND", "OUT"], None, 10, None), ("receiver", ["VCC", "GND", "IN"], None, 20, None)], h006_nets, assertions=["entity-to-interface-route-closure"])
    write_case("H007", "Project Overview", base_sheets, base_nets, assertions=["overview-svg", "deterministic-block-placement", "orthogonal-project-routing"])
    write_case("H008", "Composite View", base_sheets, base_nets, assertions=["composite-svg", "full-leaf-scenes", "sheet-qualified-dom"])
    h009 = write_case("H009", "Missing unknown interface port", base_sheets, [net("bad", ("power", "VCC"), ("control", "MISSING"))], expected="fail", diagnostic="PROJECT_NET_UNKNOWN_INTERFACE_PORT", assertions=["fail-closed"])
    h010 = write_case("H010", "Duplicate project net ownership", base_sheets, [net("one", ("power", "VCC"), ("control", "VCC")), net("two", ("power", "VCC"), ("control", "GND"))], expected="fail", diagnostic="PROJECT_NET_DUPLICATE_OWNERSHIP", assertions=["single-project-net-owner"])
    write_case("H011", "Digest locked multi sheet project", base_sheets, base_nets, assertions=["all-required-digests-verified"])
    make_legacy_case()
    ten_specs = [(f"sheet-{index:02d}", ["VCC", "GND"], None if index == 1 else "sheet-01", index, None) for index in range(1, 11)]
    write_case("H013", "Ten sheet scale baseline", ten_specs, [net("vcc", *((sid, "VCC") for sid, *_rest in ten_specs), role="power"), net("gnd", *((sid, "GND") for sid, *_rest in ten_specs), role="power")], assertions=["ten-independent-leaves", "stable-ordering"])
    write_case("H014", "Cross sheet route crossings", [("left", ["OUT", "STATUS"], None, 10, None), ("right", ["IN", "CLK"], None, 20, None)], [net("signal_a", ("left", "OUT"), ("right", "CLK")), net("signal_b", ("left", "STATUS"), ("right", "IN"))], assertions=["crossing-is-not-junction", "project-junction-explicit"])
    write_case("H015", "Local net project net equivalence collision", [("bridge", ["VCC", "AUX"], None, 10, [["VCC", "AUX"]]), ("sink-a", ["VCC"], None, 20, None), ("sink-b", ["VCC"], None, 30, None)], [net("one", ("bridge", "VCC"), ("sink-a", "VCC")), net("two", ("bridge", "AUX"), ("sink-b", "VCC"))], expected="fail", diagnostic="PROJECT_NET_EQUIVALENCE_COLLISION", assertions=["transitive-equivalence-rejected"])

    # Additional negative fixtures from the implementation plan.
    def source_edit(case_dir: pathlib.Path, func: Any, sheet: str = "power") -> None:
        path = case_dir / "circuits" / f"{sheet}.aixem"
        path.write_text(func(path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")

    def layout_edit(case_dir: pathlib.Path, func: Any, sheet: str = "power") -> None:
        path = case_dir / "layouts" / f"{sheet}.aixlayout.json"
        doc = json.loads(path.read_text(encoding="utf-8")); func(doc); write_json(path, doc)

    def project_edit(case_dir: pathlib.Path, func: Any) -> None:
        path = case_dir / "project.aixproj.json"; doc = json.loads(path.read_text(encoding="utf-8")); func(doc); write_json(path, doc)

    mutate_negative("N001", "Duplicate interface port", lambda d: source_edit(d, lambda s: s.replace("port VCC", "port VCC direction=input role=power\nport VCC", 1)), "duplicate interface port")
    mutate_negative("N002", "Unknown interface endpoint", lambda d: source_edit(d, lambda s: s.replace("@VCC", "@UNKNOWN", 1)), "unknown interface endpoint @UNKNOWN")
    mutate_negative("N003", "Interface port in two local nets", lambda d: source_edit(d, lambda s: s.replace("net gnd", "net conflict = U1.10 @VCC\nnet gnd", 1)), "endpoint @VCC occurs in both")
    mutate_negative("N004", "Interface port net and noconn conflict", lambda d: source_edit(d, lambda s: s + "noconn @VCC\n"), "endpoints both connected and noconn")
    mutate_negative("N005", "Layout references unknown sheet port", lambda d: layout_edit(d, lambda doc: doc["layout"]["sheetPorts"].append({"port": "UNKNOWN", "x": 10, "y": 20, "side": "left", "layer": "connections"})), "layout sheetPort references unknown semantic port")
    mutate_negative("N006", "Missing required sheet port presentation", lambda d: layout_edit(d, lambda doc: doc["layout"]["sheetPorts"].pop(0)), "sheetPort presentation closure mismatch")
    mutate_negative("N007", "Project member unknown sheet", lambda d: project_edit(d, lambda doc: doc["project"]["projectNets"][0]["members"].__setitem__(1, {"sheet": "missing", "port": "VCC"})), "PROJECT_NET_UNKNOWN_SHEET")
    mutate_negative("N008", "Project member unknown interface port", lambda d: project_edit(d, lambda doc: doc["project"]["projectNets"][0]["members"].__setitem__(1, {"sheet": "control", "port": "UNKNOWN"})), "PROJECT_NET_UNKNOWN_INTERFACE_PORT")
    mutate_negative("N009", "Project net one member", lambda d: project_edit(d, lambda doc: doc["project"]["projectNets"][0].__setitem__("members", doc["project"]["projectNets"][0]["members"][:1])), "is too short")
    mutate_negative("N010", "Interface port in two project nets", lambda d: project_edit(d, lambda doc: doc["project"]["projectNets"].append(net("duplicate", ("power", "VCC"), ("control", "GND")))), "PROJECT_NET_DUPLICATE_OWNERSHIP")
    mutate_negative("N011", "Unknown hierarchy parent", lambda d: project_edit(d, lambda doc: doc["project"]["sheets"][1].__setitem__("parent", "missing")), "PROJECT_HIERARCHY_UNKNOWN_PARENT")
    mutate_negative("N012", "Hierarchy cycle", lambda d: project_edit(d, lambda doc: (doc["project"]["sheets"][0].__setitem__("parent", "control"), doc["project"]["sheets"][1].__setitem__("parent", "power"))), "PROJECT_HIERARCHY_CYCLE")
    mutate_negative("N013", "Source digest mismatch", lambda d: project_edit(d, lambda doc: doc["project"]["sheets"][0]["source"].__setitem__("digest", "sha256:" + "0" * 64)), "source digest mismatch")
    mutate_negative("N014", "Layout digest mismatch", lambda d: project_edit(d, lambda doc: doc["project"]["sheets"][0]["layout"].__setitem__("digest", "sha256:" + "0" * 64)), "layout digest mismatch")
    mutate_negative("N015", "Duplicate path contradictory digest", lambda d: project_edit(d, lambda doc: doc["project"]["sheets"][1].__setitem__("source", {**doc["project"]["sheets"][0]["source"], "digest": "sha256:" + "1" * 64})), "PROJECT_REFERENCE_DIGEST_CONFLICT")

    readme = """# Hierarchical Project Conformance Corpus 1\n\nThis executable corpus covers AIXEM 0.5.3 hierarchical interface ports, immutable `aixlayout/2` and `aixproj/2` contracts, explicit project nets, hierarchy validation, deterministic overview/composite routing, legacy v1 compatibility, and negative fail-closed behavior.\n\n- `cases/H001` through `H015` map directly to the release plan.\n- `negative/N001` through `N015` exercise focused validation failures.\n- Every project is self-contained and digest locked.\n- Generated render/evidence outputs are produced by `tools/validate_hierarchical_corpus.py`.\n\nConnectivity is never inferred from geometry or matching names. Structural ownership is always Project → Sheet → Layer.\n"""
    (CORPUS / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    manifest = {
        "id": "hierarchical-project-1", "release": "0.5.3", "generatedAt": "2026-08-11T00:00:00Z",
        "cases": sorted(path.relative_to(CORPUS).as_posix() for path in (CORPUS / "cases").glob("*/case.json")),
        "negativeFixtures": sorted(path.relative_to(CORPUS).as_posix() for path in (CORPUS / "negative").glob("*/case.json")),
        "authority": {"project": "aixproj/2", "leafSemantics": ".aixem", "leafPresentation": "aixlayout/2", "geometryCreatesConnectivity": False},
    }
    write_json(CORPUS / "manifest.json", manifest)


if __name__ == "__main__":
    build()
    print(f"built {CORPUS}")
