#!/usr/bin/env python3
"""Validate AIXEM symbol-expression and static-2D-block corpora through the production renderer.

The harness deliberately builds minimal synthetic AIXEM projects and invokes the existing
GridProjectRenderer. It does not contain an alternate symbol renderer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import shutil
import sys
import tempfile
import time
from collections import Counter, defaultdict
from datetime import date
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMATIC_DIR = ROOT / "implementation" / "schematic"
if str(SCHEMATIC_DIR) not in sys.path:
    sys.path.insert(0, str(SCHEMATIC_DIR))

from component_core import (  # type: ignore  # noqa: E402
    AixemGraphicsError,
    eval_numeric,
    eval_predicate,
    pretty_json,
    sha256_file,
    validate_json,
)
from render_project import (  # type: ignore  # noqa: E402
    DEFAULT_SCHEMA_ROOT,
    DEFAULT_STYLE,
    RENDERER_ID,
    RENDERER_VERSION,
    GridProjectRenderer,
)

RELEASE = "AIXEM-SRP-0.5.2-2026-08-11"
SYMBOL_CORPUS = ROOT / "validation" / "corpus" / "symbol-expressiveness-1"
B2D_CORPUS = ROOT / "validation" / "corpus" / "static-2d-block-1"
REPORTS = ROOT / "validation" / "reports"
HUMAN_REPORTS = ROOT / "validation" / "releases" / "0.5.2"
GRID_TOLERANCE = 1e-6

NODE_CAPABILITIES = {
    "line": "geometry.line",
    "polyline": "geometry.polyline",
    "polygon": "geometry.polygon",
    "rect": "geometry.rect",
    "circle": "geometry.circle",
    "ellipse": "geometry.ellipse",
    "arc": "geometry.arc",
    "path": "geometry.path",
    "text": "text.field",
    "image": "geometry.image",
    "dimension": "geometry.dimension",
    "group": "structure.group",
    "use": "structure.use",
}


class CorpusError(RuntimeError):
    """A conformance fixture or assertion failed."""


def canonical_json_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(value), encoding="utf-8", newline="\n")


def snap(value: float, grid: float = 2.5) -> float:
    return round(value / grid) * grid


def on_grid(value: float, grid: float = 2.5) -> bool:
    return abs(value / grid - round(value / grid)) <= GRID_TOLERANCE


def walk_nodes(nodes: Iterable[dict[str, Any]], definitions: dict[str, Any]) -> Iterable[dict[str, Any]]:
    """Walk source nodes once, including definition bodies but not expanding each use."""
    seen_defs: set[str] = set()

    def walk(node: dict[str, Any]) -> Iterable[dict[str, Any]]:
        yield node
        if node.get("type") == "group":
            for child in node.get("children", []):
                yield from walk(child)
        elif node.get("type") == "use":
            name = node.get("definition")
            if name in definitions and name not in seen_defs:
                seen_defs.add(name)
                yield from walk(definitions[name])

    for item in nodes:
        yield from walk(item)


def all_source_nodes(symbol: dict[str, Any]) -> list[dict[str, Any]]:
    definitions = symbol.get("definitions", {})
    nodes = list(walk_nodes(symbol.get("graphics", []), definitions))
    for variant in symbol.get("variants", []):
        nodes.extend(walk_nodes(variant.get("graphics", []), definitions))
    for paint in symbol.get("paintServers", {}).values():
        nodes.extend(walk_nodes(paint.get("graphics", []), definitions))
    return nodes


def default_parameters(symbol: dict[str, Any]) -> dict[str, Any]:
    return {name: definition["default"] for name, definition in symbol.get("parameters", {}).items()}


def default_fields(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "entity": "X1",
        "reference": "X1",
        "value": case["title"],
        "type": f"conformance:{case['id'].lower()}",
        "title": case["title"],
        "refdes": "X1",
    }


def active_variant(symbol: dict[str, Any]) -> dict[str, Any] | None:
    variant_id = symbol.get("defaultVariant")
    if not variant_id:
        return None
    return next((item for item in symbol.get("variants", []) if item["id"] == variant_id), None)


def resolved_port(symbol: dict[str, Any], port: dict[str, Any], parameters: dict[str, Any], fields: dict[str, Any]) -> dict[str, Any]:
    result = dict(port)
    variant = active_variant(symbol)
    if variant and port["id"] in variant.get("portOverrides", {}):
        result.update(variant["portOverrides"][port["id"]])
    result["visible"] = "visibleWhen" not in result or eval_predicate(result["visibleWhen"], parameters, fields)
    if result["visible"]:
        result["resolvedX"] = eval_numeric(result["x"], parameters)
        result["resolvedY"] = eval_numeric(result["y"], parameters)
    return result


def node_endpoint(node: dict[str, Any], endpoint: str, parameters: dict[str, Any]) -> tuple[float, float] | None:
    if node.get("type") != "line":
        return None
    if endpoint == "start":
        return eval_numeric(node["x1"], parameters), eval_numeric(node["y1"], parameters)
    if endpoint == "end":
        return eval_numeric(node["x2"], parameters), eval_numeric(node["y2"], parameters)
    return None


def infer_capabilities(symbol: dict[str, Any], case: dict[str, Any]) -> set[str]:
    caps: set[str] = set()
    for node in all_source_nodes(symbol):
        cap = NODE_CAPABILITIES.get(node.get("type", ""))
        if cap:
            caps.add(cap)
        if "visibleWhen" in node:
            caps.add("visibility.predicate")
        if node.get("type") == "text" and "field" not in node:
            has_bound_text = any(
                candidate.get("type") == "text" and "field" in candidate
                for candidate in all_source_nodes(symbol)
            )
            if not has_bound_text:
                caps.discard("text.field")
    if symbol.get("parameters"):
        caps.add("parameter.numeric")
    if symbol.get("variants"):
        caps.add("variant.graphics")
    if symbol.get("ports") or case.get("componentPorts"):
        caps.add("port.mapping")
    if len(symbol.get("ports", [])) >= 16:
        caps.add("scale.high-port-count")
    if symbol.get("paintServers"):
        if any(p.get("type") in {"linear-gradient", "radial-gradient"} for p in symbol["paintServers"].values()):
            caps.add("paint.gradient")
        if any(p.get("type") == "pattern" for p in symbol["paintServers"].values()):
            caps.add("paint.pattern")
    return caps


def geometry_signature(symbol: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    parameters = default_parameters(symbol)
    fields = default_fields(case)
    ports = [resolved_port(symbol, port, parameters, fields) for port in symbol.get("ports", [])]
    nodes = all_source_nodes(symbol)
    primitive_counts = Counter(node.get("type", "unknown") for node in nodes)
    return {
        "case": case["id"],
        "symbol": symbol["id"],
        "bounds": symbol["bounds"],
        "defaultVariant": symbol.get("defaultVariant"),
        "parameters": parameters,
        "ports": [
            {
                "id": p["id"],
                "visible": p["visible"],
                "x": p.get("resolvedX"),
                "y": p.get("resolvedY"),
                "orientation": p.get("orientation", 0),
            }
            for p in ports
        ],
        "fieldAnchors": [
            {"id": node.get("id"), "field": node.get("field"), "x": node.get("x"), "y": node.get("y")}
            for node in nodes
            if node.get("type") == "text" and "field" in node
        ],
        "primitiveCounts": dict(sorted(primitive_counts.items())),
        "definitions": sorted(symbol.get("definitions", {})),
        "variants": sorted(item["id"] for item in symbol.get("variants", [])),
        "requiredFeatures": sorted(symbol.get("requiredFeatures", [])),
        "capabilities": sorted(infer_capabilities(symbol, case)),
    }


def validate_case_contract(case_path: pathlib.Path, case_schema: pathlib.Path) -> dict[str, Any]:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    schema = json.loads(case_schema.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(case),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        rendered = [f"{'/'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in errors[:20]]
        raise CorpusError("invalid case contract: " + "; ".join(rendered))
    return case


def static_assertions(case: dict[str, Any], symbol_doc: dict[str, Any], symbol_path: pathlib.Path) -> dict[str, Any]:
    validate_json(symbol_doc, DEFAULT_SCHEMA_ROOT / "aixem-symbol-asset-1.schema.json", f"symbol:{case['id']}")
    symbol = symbol_doc["symbol"]
    issues: list[str] = []
    parameters = default_parameters(symbol)
    fields = default_fields(case)
    variants = {item["id"] for item in symbol.get("variants", [])}
    parameter_ids = set(symbol.get("parameters", {}))
    source_nodes = all_source_nodes(symbol)
    primitive_families = {node.get("type") for node in source_nodes}
    roles = {node.get("role") for node in source_nodes if node.get("role")}

    if len(symbol.get("ports", [])) != case["expectedPortCount"]:
        issues.append(f"expected {case['expectedPortCount']} symbol ports, observed {len(symbol.get('ports', []))}")
    visible_ports = [resolved_port(symbol, port, parameters, fields) for port in symbol.get("ports", [])]
    visible_count = sum(1 for port in visible_ports if port["visible"])
    if visible_count != case["expectedVisiblePortCount"]:
        issues.append(f"expected {case['expectedVisiblePortCount']} visible ports, observed {visible_count}")
    if set(case["expectedVariantIds"]) != variants:
        issues.append(f"variant inventory mismatch: expected={sorted(case['expectedVariantIds'])}, observed={sorted(variants)}")
    if set(case["expectedParameterIds"]) != parameter_ids:
        issues.append(f"parameter inventory mismatch: expected={sorted(case['expectedParameterIds'])}, observed={sorted(parameter_ids)}")
    missing_primitives = sorted(set(case["expectedPrimitiveFamilies"]) - primitive_families)
    if missing_primitives:
        issues.append(f"missing primitive families: {missing_primitives}")
    missing_roles = sorted(set(case["expectedFieldRoles"]) - roles)
    if missing_roles:
        issues.append(f"missing field roles: {missing_roles}")

    required_caps = set(case["requiredCapabilities"])
    inferred_caps = infer_capabilities(symbol, case)
    missing_caps = sorted(required_caps - inferred_caps)
    if missing_caps:
        issues.append(f"required capabilities not evidenced by source: {missing_caps}")

    port_ids = [port["id"] for port in symbol.get("ports", [])]
    component_port_ids = [port["id"] for port in case.get("componentPorts", [])]
    if len(port_ids) != len(set(port_ids)):
        issues.append("duplicate symbol port IDs")
    if len(component_port_ids) != len(set(component_port_ids)):
        issues.append("duplicate component port IDs")
    if set(port_ids) != set(component_port_ids):
        issues.append("component-port and symbol-port inventories differ")

    if case["expectedGridPolicy"] == "ports-on-2.5mm":
        off_grid = [p["id"] for p in visible_ports if p["visible"] and (not on_grid(p["resolvedX"]) or not on_grid(p["resolvedY"]))]
        if off_grid:
            issues.append(f"visible ports off 2.5 mm grid: {off_grid}")

    by_port = {p["id"]: p for p in visible_ports}
    lead_checks = 0
    for node in source_nodes:
        metadata = node.get("metadata", {})
        port_id = metadata.get("port")
        endpoint_name = metadata.get("portEndpoint")
        if not port_id or not endpoint_name:
            continue
        lead_checks += 1
        endpoint = node_endpoint(node, endpoint_name, parameters)
        port = by_port.get(port_id)
        if endpoint is None:
            issues.append(f"lead {node.get('id')} does not expose a mechanically checkable line endpoint")
        elif not port or not port["visible"]:
            issues.append(f"lead {node.get('id')} references missing/hidden port {port_id}")
        elif math.hypot(endpoint[0] - port["resolvedX"], endpoint[1] - port["resolvedY"]) > GRID_TOLERANCE:
            issues.append(f"lead {node.get('id')} endpoint does not coincide with port {port_id}")

    degenerate: list[str] = []
    for node in source_nodes:
        try:
            if node.get("type") == "line":
                a = (eval_numeric(node["x1"], parameters), eval_numeric(node["y1"], parameters))
                b = (eval_numeric(node["x2"], parameters), eval_numeric(node["y2"], parameters))
                if math.hypot(a[0] - b[0], a[1] - b[1]) <= GRID_TOLERANCE:
                    degenerate.append(node.get("id", "unnamed-line"))
            elif node.get("type") == "rect":
                if eval_numeric(node["width"], parameters) <= 0 or eval_numeric(node["height"], parameters) <= 0:
                    degenerate.append(node.get("id", "unnamed-rect"))
            elif node.get("type") == "circle" and eval_numeric(node["r"], parameters) <= 0:
                degenerate.append(node.get("id", "unnamed-circle"))
            elif node.get("type") == "ellipse" and (eval_numeric(node["rx"], parameters) <= 0 or eval_numeric(node["ry"], parameters) <= 0):
                degenerate.append(node.get("id", "unnamed-ellipse"))
        except AixemGraphicsError as exc:
            issues.append(f"numeric resolution failed for {node.get('id', node.get('type'))}: {exc}")
    if degenerate:
        issues.append(f"degenerate geometry: {degenerate}")

    bounds = symbol["bounds"]
    if float(bounds["width"]) <= 0 or float(bounds["height"]) <= 0:
        issues.append("invalid non-positive symbol bounds")

    if issues:
        raise CorpusError("; ".join(issues))
    signature = geometry_signature(symbol, case)
    return {
        "symbolDigest": sha256_file(symbol_path),
        "portCount": len(symbol.get("ports", [])),
        "visiblePortCount": visible_count,
        "leadCoincidenceChecks": lead_checks,
        "primitiveCounts": signature["primitiveCounts"],
        "capabilities": signature["capabilities"],
        "geometrySignature": signature,
        "geometrySignatureDigest": canonical_json_digest(signature),
    }


def build_synthetic_project(case: dict[str, Any], symbol_path: pathlib.Path, root: pathlib.Path) -> pathlib.Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "symbols").mkdir(exist_ok=True)
    (root / "libraries").mkdir(exist_ok=True)
    target_symbol = root / "symbols" / "symbol.aixsym.json"
    shutil.copyfile(symbol_path, target_symbol)
    symbol = json.loads(target_symbol.read_text(encoding="utf-8"))["symbol"]
    component_id = f"conformance:{case['id'].lower()}"
    model_id = f"corpus_{case['id'].lower()}"
    entity_id = "X1"

    ports = [
        {
            "id": p["id"],
            "name": p["name"],
            "required": p["required"],
            "terminal": p["id"],
            "type": p["type"],
        }
        for p in case["componentPorts"]
    ]
    field_map: dict[str, str] = {}
    if "reference-field" in case["expectedFieldRoles"]:
        field_map["reference"] = "refdes"
    if "value-field" in case["expectedFieldRoles"]:
        field_map["value"] = "value"
    library = {
        "schema": "https://schemas.aixem.org/component-graphics/aixlib/1",
        "formatVersion": "1.0",
        "library": {
            "id": f"conformance:{case['id'].lower()}-library",
            "version": "1.0.0",
            "title": f"{case['id']} synthetic conformance library",
            "description": "Generated wrapper for production-pipeline corpus validation.",
            "namespace": "conformance",
            "dependencies": [],
            "components": [
                {
                    "id": component_id,
                    "kind": "static-block" if case["tier"] == "b2d" else case["category"],
                    "displayName": case["title"],
                    "description": case["purpose"],
                    "classification": [],
                    "ports": ports,
                    "properties": [
                        {"id": "refdes", "type": "string", "required": False},
                        {"id": "value", "type": "string", "required": False},
                    ],
                    "presentations": [
                        {
                            "purpose": "primary-diagram",
                            "asset": {
                                "path": "symbols/symbol.aixsym.json",
                                "digest": sha256_file(target_symbol),
                                "symbolId": symbol["id"],
                                "revision": symbol["revision"],
                            },
                            "portMap": {p["id"]: p["id"] for p in case["componentPorts"]},
                            "fieldMap": field_map,
                        }
                    ],
                    "metadata": {"corpusCase": case["id"]},
                }
            ],
            "metadata": {"profile": "component.graphics@1", "generated": True},
            "provenance": {
                "author": "AIXEM project",
                "created": "2026-08-11",
                "license": "CC0-1.0",
                "origin": RELEASE,
                "notes": "Synthetic wrapper; source symbol remains the conformance fixture.",
            },
        },
    }
    library_path = root / "libraries" / "corpus.aixlib.json"
    write_json(library_path, library)

    title_literal = json.dumps(case["title"], ensure_ascii=False)
    source = "\n".join(
        [
            "aixem 1.0",
            f"model {model_id} title={title_literal}",
            "feature component.graphics@1 required=true",
            "feature explicit.layout@1 required=true",
            "",
            f"component {entity_id} type={component_id} refdes={entity_id} value={title_literal}",
            "",
        ]
    )
    source_path = root / "corpus.aixem"
    source_path.write_text(source, encoding="utf-8", newline="\n")

    bounds = symbol["bounds"]
    width = snap(max(180.0, float(bounds["width"]) + 80.0), 2.5)
    height = snap(max(120.0, float(bounds["height"]) + 75.0), 2.5)
    px = snap(25.0 - float(bounds["x"]))
    py = snap(25.0 - float(bounds["y"]))
    layout = {
        "schema": "https://schemas.aixem.org/component-graphics/aixlayout/1",
        "formatVersion": "1.0",
        "layout": {
            "id": f"{model_id}-layout",
            "designId": model_id,
            "purpose": "schematic-layout",
            "coordinateSystem": {
                "unit": "mm",
                "grid": 2.5,
                "yAxis": "down",
                "angleUnit": "deg",
                "angleDirection": "clockwise",
            },
            "sheet": {
                "width": width,
                "height": height,
                "margin": 10,
                "titleBlock": {
                    "title": f"{case['id']} — {case['title']}",
                    "drawing": f"{model_id}-layout",
                    "revision": "A",
                    "sheet": "1/1",
                },
            },
            "layers": [
                {"id": "connections", "order": 10, "purpose": "semantic net routes", "defaultVisible": True, "printable": True, "locked": False},
                {"id": "symbols", "order": 20, "purpose": "component symbols", "defaultVisible": True, "printable": True, "locked": False},
                {"id": "annotation", "order": 30, "purpose": "notes", "defaultVisible": True, "printable": True, "locked": False},
            ],
            "styles": {
                "signal": {"stroke": "#24864a", "strokeWidth": 0.65, "fill": "none", "strokeLinecap": "square", "strokeLinejoin": "miter"},
                "note": {"stroke": "none", "fill": "#1b4e8c", "fontFamily": "Arial, sans-serif", "fontSize": 3.5},
            },
            "placements": [{"entity": entity_id, "layer": "symbols", "x": px, "y": py}],
            "connections": [],
            "annotations": [],
            "metadata": {
                "connectionAuthority": "semantic-source-only",
                "routingMode": "orthogonal",
                "styleProfile": "aixem.schematic.grid-light",
                "corpusCase": case["id"],
            },
        },
    }
    layout_path = root / "corpus.aixlayout.json"
    write_json(layout_path, layout)

    project = {
        "schema": "https://schemas.aixem.org/component-graphics/aixproj/1",
        "formatVersion": "1.0",
        "project": {
            "id": f"conformance:{case['id'].lower()}",
            "title": f"{case['id']} {case['title']} conformance project",
            "description": "Generated only to exercise the existing production renderer.",
            "applicationProfile": "circuit.schematic@1 + component.graphics@1 + aixem.schematic.grid-light@1",
            "features": ["component.graphics@1", "explicit.layout@1", "grid-snap@1"],
            "source": {
                "id": model_id,
                "path": source_path.name,
                "mediaType": "application/vnd.aixem+text",
                "version": "1.0",
                "digest": sha256_file(source_path),
            },
            "layout": {
                "id": f"{model_id}-layout",
                "path": layout_path.name,
                "mediaType": "application/vnd.aixem.layout+json",
                "version": "1.0",
                "digest": sha256_file(layout_path),
            },
            "libraries": [
                {
                    "id": library["library"]["id"],
                    "path": "libraries/corpus.aixlib.json",
                    "mediaType": "application/vnd.aixem.library+json",
                    "version": "1.0.0",
                    "digest": sha256_file(library_path),
                }
            ],
            "outputs": [
                {"role": "drawing-svg", "path": "render/drawing.svg", "mediaType": "image/svg+xml"},
                {"role": "resolved-scene", "path": "render/resolved-scene.json", "mediaType": "application/json"},
            ],
            "renderPolicy": {
                "purpose": "primary-diagram",
                "backend": "svg",
                "fontPolicy": "system-fallback",
                "remoteAssets": "deny",
                "unsupportedRequiredFeature": "reject",
                "defaultVariantPolicy": "library-default",
            },
            "status": "controlled",
            "metadata": {"corpusCase": case["id"], "syntheticWrapper": True},
            "provenance": {"author": "AIXEM project", "created": "2026-08-11", "license": "CC0-1.0"},
        },
    }
    project_path = root / "project.aixproj.json"
    write_json(project_path, project)
    return project_path


def render_repeated(case: dict[str, Any], symbol_path: pathlib.Path, repeat: int, preserve: pathlib.Path | None) -> dict[str, Any]:
    svg_digests: list[str] = []
    scene_digests: list[str] = []
    durations: list[float] = []
    last_result: dict[str, Any] | None = None
    last_root: pathlib.Path | None = None
    temp_roots: list[tempfile.TemporaryDirectory[str]] = []
    try:
        for index in range(repeat):
            temp = tempfile.TemporaryDirectory(prefix=f"aixem-{case['id'].lower()}-")
            temp_roots.append(temp)
            work = pathlib.Path(temp.name)
            project = build_synthetic_project(case, symbol_path, work)
            started = time.perf_counter()
            renderer = GridProjectRenderer(project, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE)
            result = renderer.render(work / "render")
            durations.append((time.perf_counter() - started) * 1000.0)
            svg_digests.append(sha256_file(work / "render" / "drawing.svg"))
            scene_digests.append(sha256_file(work / "render" / "resolved-scene.json"))
            last_result = result
            last_root = work
        if len(set(svg_digests)) != 1:
            raise CorpusError(f"canonical SVG is not deterministic across {repeat} renders: {svg_digests}")
        if len(set(scene_digests)) != 1:
            raise CorpusError(f"resolved scene is not deterministic across {repeat} renders: {scene_digests}")
        assert last_result is not None and last_root is not None
        if preserve is not None:
            preserve.mkdir(parents=True, exist_ok=True)
            for name in ("drawing.svg", "resolved-scene.json", "render-manifest.json", "workbench.html"):
                shutil.copyfile(last_root / "render" / name, preserve / name)
            shutil.copyfile(last_root / "project.aixproj.json", preserve / "synthetic-project.aixproj.json")
        scene = last_result["scene"]
        return {
            "svgDigest": svg_digests[0],
            "sceneDigest": scene_digests[0],
            "repeat": repeat,
            "deterministic": True,
            "renderDurationMs": {
                "minimum": round(min(durations), 3),
                "maximum": round(max(durations), 3),
                "mean": round(sum(durations) / len(durations), 3),
            },
            "sceneStatistics": scene["statistics"],
            "rendererFeaturesUsed": sorted(scene["featuresUsed"]),
            "renderer": scene["renderer"],
            "styleProfile": scene["styleProfile"],
            "artifacts": {item["role"]: {"bytes": item["bytes"], "digest": item["digest"]} for item in last_result["artifacts"]},
            "validation": last_result["validation"],
        }
    finally:
        for temp in temp_roots:
            temp.cleanup()


def read_approved(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema": "https://schemas.aixem.org/conformance/approved-render-digests/1", "release": RELEASE, "cases": {}}
    value = json.loads(path.read_text(encoding="utf-8"))
    if "cases" not in value:
        value = {"schema": "https://schemas.aixem.org/conformance/approved-render-digests/1", "release": RELEASE, "cases": value}
    return value


def read_visual_reviews(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema": "https://schemas.aixem.org/conformance/visual-review/1", "release": RELEASE, "cases": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def check_visual_review(case: dict[str, Any], source_digest: str, svg_digest: str, reviews: dict[str, Any]) -> dict[str, Any]:
    review = reviews.get("cases", {}).get(case["id"])
    if not review:
        return {"status": "PENDING", "valid": False, "reason": "missing visual-review record"}
    issues: list[str] = []
    if review.get("sourceDigest") != source_digest:
        issues.append("source digest is stale")
    if review.get("svgDigest") != svg_digest:
        issues.append("SVG digest is stale")
    if review.get("result") != "PASS":
        issues.append(f"result is {review.get('result', 'missing')}")
    if not review.get("reviewer"):
        issues.append("reviewer missing")
    recorded = review.get("checks", {})
    missing = [check for check in case["manualReviewChecks"] if recorded.get(check) is not True]
    if missing:
        issues.append(f"checks not approved: {missing}")
    return {"status": "PASS" if not issues else "FAIL", "valid": not issues, "issues": issues, "record": review}


def multi_unit_probe(case_result: dict[str, Any], case: dict[str, Any], symbol_path: pathlib.Path) -> dict[str, Any]:
    expected = case.get("probe", {}).get("expectedResult", "NOT_SUPPORTED")
    with tempfile.TemporaryDirectory(prefix="aixem-s030-probe-") as temp_name:
        work = pathlib.Path(temp_name)
        project_path = build_synthetic_project(case, symbol_path, work)
        layout_path = work / "corpus.aixlayout.json"
        layout_doc = json.loads(layout_path.read_text(encoding="utf-8"))
        original = dict(layout_doc["layout"]["placements"][0])
        second = dict(original)
        second["x"] = float(second["x"]) + 100.0
        second["unit"] = "B"
        original["unit"] = "A"
        layout_doc["layout"]["placements"] = [original, second]
        write_json(layout_path, layout_doc)
        project_doc = json.loads(project_path.read_text(encoding="utf-8"))
        project_doc["project"]["layout"]["digest"] = sha256_file(layout_path)
        write_json(project_path, project_doc)
        duplicate_rejected = False
        duplicate_message = ""
        try:
            GridProjectRenderer(project_path, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE)
        except (AixemGraphicsError, ValueError, KeyError) as exc:
            duplicate_message = str(exc)
            duplicate_rejected = "duplicate placement entity" in duplicate_message

    # Current placement schema has no normative unit selector, and a single placement exposes all mapped ports.
    independently_placeable_units = False
    per_unit_port_subsets = False
    shared_identity = False
    result = "NOT_SUPPORTED"
    if independently_placeable_units and per_unit_port_subsets and shared_identity:
        result = "PASS"
    elif any((independently_placeable_units, per_unit_port_subsets, shared_identity)):
        result = "PARTIAL"
    valid = (
        case_result.get("automatedStatus") == "PASS"
        and duplicate_rejected
        and result == expected
    )
    return {
        "case": case["id"],
        "result": result,
        "expectedResult": expected,
        "valid": valid,
        "graphicalMonolith": case_result.get("automatedStatus"),
        "requiredSemanticProperties": {
            "oneSharedComponentIdentity": shared_identity,
            "independentlyPlaceableUnits": independently_placeable_units,
            "disjointPortSubsets": per_unit_port_subsets,
            "sharedReferenceAndValue": False,
            "unambiguousResolvedSceneIdentity": False,
        },
        "negativeTest": {
            "name": "duplicate-placement-entity-rejected",
            "pass": duplicate_rejected,
            "observed": duplicate_message,
        },
        "interpretation": "The current model can draw the monolithic FPGA shape, but cannot represent independently placeable unit presentations that share one semantic component identity. Variants were not misused as units.",
        "extensionDecision": "No speculative core extension was introduced in 0.5.2. A dedicated ADR is required before future multi-unit semantics are implemented.",
    }


def selected_case_entries(args: argparse.Namespace) -> list[tuple[pathlib.Path, dict[str, Any], pathlib.Path]]:
    corpora = [(SYMBOL_CORPUS, SYMBOL_CORPUS / "manifest.json")]
    if args.all or args.tier in {"b2d", "all"} or (args.case and args.case.startswith("B")):
        corpora.append((B2D_CORPUS, B2D_CORPUS / "manifest.json"))
    entries: list[tuple[pathlib.Path, dict[str, Any], pathlib.Path]] = []
    for corpus_root, manifest_path in corpora:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        case_schema = (corpus_root / manifest["caseSchema"]).resolve()
        for item in manifest["cases"]:
            if args.case and item["id"] != args.case:
                continue
            if args.tier and args.tier not in {"all", item["tier"]}:
                continue
            case_path = corpus_root / item["path"]
            case = validate_case_contract(case_path, case_schema)
            entries.append((corpus_root, case, case_path))
    if not entries:
        raise CorpusError("no cases matched the selection")
    return sorted(entries, key=lambda entry: entry[1]["id"])


def write_review_template(corpus_root: pathlib.Path, results: list[dict[str, Any]]) -> None:
    path = corpus_root / "results" / "visual-review.json"
    current = read_visual_reviews(path)
    current.update({"schema": "https://schemas.aixem.org/conformance/visual-review/1", "release": RELEASE, "profile": corpus_root.name})
    cases = current.setdefault("cases", {})
    for result in results:
        case = result["caseContract"]
        existing = cases.get(case["id"], {})
        cases[case["id"]] = {
            "reviewer": existing.get("reviewer", ""),
            "reviewDate": existing.get("reviewDate", ""),
            "sourceDigest": result["static"]["symbolDigest"],
            "svgDigest": result["render"]["svgDigest"],
            "result": existing.get("result", "PENDING"),
            "checks": {check: existing.get("checks", {}).get(check, False) for check in case["manualReviewChecks"]},
            "notes": existing.get("notes", ""),
        }
    write_json(path, current)


def summarize(results: list[dict[str, Any]], mu_result: dict[str, Any] | None) -> dict[str, Any]:
    by_tier: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        by_tier[result["tier"]].append(result)

    def tier_status(name: str, expected_count: int, include_visual: bool = True) -> dict[str, Any]:
        items = by_tier.get(name, [])
        automated_pass = sum(r["automatedStatus"] == "PASS" for r in items)
        visual_pass = sum(r["visualReview"]["status"] == "PASS" for r in items)
        return {
            "expectedCases": expected_count,
            "observedCases": len(items),
            "automatedPassed": automated_pass,
            "visualPassed": visual_pass,
            "status": "PASS" if len(items) == expected_count and automated_pass == expected_count and (not include_visual or visual_pass == expected_count) else "FAIL",
        }

    core = tier_status("core", 24)
    extended_only = tier_status("extended", 5)
    extended = {
        "status": "PASS" if core["status"] == "PASS" and extended_only["status"] == "PASS" else "FAIL",
        "core": core,
        "extendedCases": extended_only,
    }
    b2d = tier_status("b2d", 6)
    return {
        "release": RELEASE,
        "S-Core": core,
        "S-Extended": extended,
        "MU": mu_result or {"result": "NOT_RUN", "valid": False},
        "B2D": b2d,
    }


def emit_reports(results: list[dict[str, Any]], summary: dict[str, Any], mu_result: dict[str, Any] | None) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    symbol_results = [r for r in results if r["id"].startswith("S")]
    b2d_results = [r for r in results if r["id"].startswith("B")]

    capability_cases: dict[str, list[str]] = defaultdict(list)
    primitive_cases: dict[str, list[str]] = defaultdict(list)
    for result in results:
        for capability in result["static"]["capabilities"]:
            capability_cases[capability].append(result["id"])
        for primitive, count in result["static"]["primitiveCounts"].items():
            if count:
                primitive_cases[primitive].append(result["id"])

    capability_matrix = {
        "schema": "https://schemas.aixem.org/conformance/capability-matrix/1",
        "release": RELEASE,
        "capabilities": [
            {"capability": cap, "evidenceCases": sorted(ids), "result": "PASS"}
            for cap, ids in sorted(capability_cases.items())
        ] + [
            {"capability": "semantic.multi-unit-independent-placement", "evidenceCases": ["S030"], "result": (mu_result or {}).get("result", "NOT_RUN")},
            {"capability": "cad.dynamic-block-actions", "evidenceCases": [], "result": "NOT_IN_SCOPE"},
            {"capability": "cad.native-dwg-round-trip", "evidenceCases": [], "result": "NOT_IN_SCOPE"},
            {"capability": "cad.3d-brep", "evidenceCases": [], "result": "NOT_IN_SCOPE"},
        ],
    }
    primitive_matrix = {
        "schema": "https://schemas.aixem.org/conformance/primitive-usage-matrix/1",
        "release": RELEASE,
        "primitives": [{"primitive": p, "evidenceCases": sorted(ids)} for p, ids in sorted(primitive_cases.items())],
    }
    performance = {
        "schema": "https://schemas.aixem.org/conformance/corpus-performance/1",
        "release": RELEASE,
        "policy": "Observed baseline only; future releases may enforce reviewed relative-regression thresholds.",
        "cases": [
            {
                "id": r["id"],
                "sourceBytes": r["sourceBytes"],
                "primitiveCount": sum(r["static"]["primitiveCounts"].values()),
                "visiblePortCount": r["static"]["visiblePortCount"],
                "renderDurationMs": r["render"]["renderDurationMs"],
                "resolvedSceneBytes": r["render"]["artifacts"]["resolved-scene"]["bytes"],
                "svgBytes": r["render"]["artifacts"]["drawing-svg"]["bytes"],
            }
            for r in results
        ],
    }

    def corpus_payload(profile: str, items: list[dict[str, Any]], tier_summary: Any) -> dict[str, Any]:
        return {
            "schema": "https://schemas.aixem.org/conformance/corpus-results/1",
            "release": RELEASE,
            "profile": profile,
            "renderer": {"id": RENDERER_ID, "version": RENDERER_VERSION, "sourceDigest": sha256_file(ROOT / "implementation" / "schematic" / "render_project.py")},
            "symbolSchemaDigest": sha256_file(DEFAULT_SCHEMA_ROOT / "aixem-symbol-asset-1.schema.json"),
            "styleProfileDigest": sha256_file(DEFAULT_STYLE),
            "summary": tier_summary,
            "cases": items,
        }

    symbol_payload = corpus_payload("symbol-expressiveness-1", symbol_results, {k: summary[k] for k in ("S-Core", "S-Extended", "MU")})
    b2d_payload = corpus_payload("static-2d-block-1", b2d_results, summary["B2D"])
    write_json(SYMBOL_CORPUS / "results" / "corpus-results.json", symbol_payload)
    write_json(SYMBOL_CORPUS / "results" / "capability-matrix.json", capability_matrix)
    write_json(SYMBOL_CORPUS / "results" / "primitive-usage-matrix.json", primitive_matrix)
    write_json(SYMBOL_CORPUS / "results" / "performance-baseline.json", performance)
    write_json(B2D_CORPUS / "results" / "corpus-results.json", b2d_payload)
    write_json(B2D_CORPUS / "results" / "capability-matrix.json", capability_matrix)
    if mu_result:
        write_json(SYMBOL_CORPUS / "results" / "multi-unit-gap-report.json", mu_result)

    release_payload = {
        "schema": "https://schemas.aixem.org/conformance/symbol-expressiveness-report/1",
        "release": RELEASE,
        "generatedDate": str(date(2026, 8, 11)),
        "summary": summary,
        "capabilityMatrix": capability_matrix,
        "primitiveUsage": primitive_matrix,
        "performance": performance,
        "cases": symbol_results,
        "explicitExclusions": [
            "No KiCad or OrCAD native format compatibility.",
            "No exact vendor-library visual identity.",
            "No DWG/DXF round trip or AutoCAD Dynamic Block behavior.",
            "No 3D/B-rep, PCB footprint, SPICE, or screenshot-recognition capability claim.",
        ],
    }
    write_json(REPORTS / "symbol-expressiveness-0.5.2.json", release_payload)
    write_json(REPORTS / "static-2d-block-0.5.2.json", b2d_payload)
    if mu_result:
        write_json(REPORTS / "multi-unit-capability-0.5.2.json", mu_result)

    lines = [
        "# AIXEM 0.5.2 Symbol Expressiveness Conformance Report",
        "",
        f"**Release:** `{RELEASE}`  ",
        f"**Production renderer:** `{RENDERER_ID}` `{RENDERER_VERSION}`  ",
        "",
        "## Results",
        "",
        f"- S-Core: **{summary['S-Core']['status']}** ({summary['S-Core']['automatedPassed']}/24 automated, {summary['S-Core']['visualPassed']}/24 visual)",
        f"- S-Extended: **{summary['S-Extended']['status']}**",
        f"- MU: **{summary['MU'].get('result', 'NOT_RUN')}** (published independently)",
        f"- B2D: **{summary['B2D']['status']}** ({summary['B2D']['automatedPassed']}/6 automated, {summary['B2D']['visualPassed']}/6 visual)",
        "",
        "## Claim boundary",
        "",
        "AIXEM demonstrates the passed tiers against its self-authored representative corpus through the production `.aixsym` and renderer pipeline. This is not a native KiCad, OrCAD, DWG, DXF, or AutoCAD Dynamic Block compatibility claim.",
        "",
        "## Cases",
        "",
        "| ID | Tier | Automated | Visual | SVG digest |",
        "|---|---|---:|---:|---|",
    ]
    for r in symbol_results:
        lines.append(f"| {r['id']} | {r['tier']} | {r['automatedStatus']} | {r['visualReview']['status']} | `{r['render']['svgDigest']}` |")
    (HUMAN_REPORTS / "symbol-expressiveness.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    b_lines = [
        "# AIXEM 0.5.2 Static 2D Block Profile Report",
        "",
        f"**Result:** **{summary['B2D']['status']}**",
        "",
        "This profile covers deterministic static 2D vector blocks only. Dynamic Block actions, constraints, native DWG identity, round trip, and 3D CAD semantics are excluded.",
        "",
        "| ID | Automated | Visual | SVG digest |",
        "|---|---:|---:|---|",
    ]
    for r in b2d_results:
        b_lines.append(f"| {r['id']} | {r['automatedStatus']} | {r['visualReview']['status']} | `{r['render']['svgDigest']}` |")
    (HUMAN_REPORTS / "static-2d-block.md").write_text("\n".join(b_lines) + "\n", encoding="utf-8", newline="\n")

    if mu_result:
        mu_lines = [
            "# AIXEM 0.5.2 Multi-Unit Capability Result",
            "",
            f"**Result:** **{mu_result['result']}**",
            "",
            mu_result["interpretation"],
            "",
            mu_result["extensionDecision"],
        ]
        (HUMAN_REPORTS / "multi-unit-capability.md").write_text("\n".join(mu_lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--case", help="Run one case, for example S014 or B005")
    selection.add_argument("--tier", choices=["core", "extended", "probe", "b2d", "all"], help="Run one tier")
    selection.add_argument("--all", action="store_true", help="Run all symbol and static block cases")
    parser.add_argument("--repeat", type=int, default=1, help="Number of independent production renders per case")
    parser.add_argument("--emit-report", action="store_true", help="Write case outputs and aggregate reports")
    parser.add_argument("--update-approved-digests", action="store_true", help="Explicitly approve current deterministic render digests")
    parser.add_argument("--allow-pending-review", action="store_true", help="Do not fail solely for pending visual review")
    parser.add_argument("--write-review-template", action="store_true", help="Create/update digest-bound visual review templates")
    parser.add_argument("--json-out", type=pathlib.Path, help="Optional machine-readable invocation result")
    args = parser.parse_args()
    if not (args.case or args.tier or args.all):
        args.all = True
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    try:
        entries = selected_case_entries(args)
        results: list[dict[str, Any]] = []
        by_corpus: dict[pathlib.Path, list[dict[str, Any]]] = defaultdict(list)
        approved_by_corpus = {root: read_approved(root / "expected" / "approved-render-digests.json") for root, _, _ in entries}
        reviews_by_corpus = {root: read_visual_reviews(root / "results" / "visual-review.json") for root, _, _ in entries}

        for corpus_root, case, case_path in entries:
            symbol_path = case_path.parent / case["symbolPath"]
            symbol_doc = json.loads(symbol_path.read_text(encoding="utf-8"))
            started = time.perf_counter()
            preserve = corpus_root / "results" / "renders" / case["id"] if args.emit_report else None
            try:
                static = static_assertions(case, symbol_doc, symbol_path)
                render = render_repeated(case, symbol_path, args.repeat, preserve)
                approved = approved_by_corpus[corpus_root].get("cases", {}).get(case["id"])
                digest_status = "PASS" if approved and approved.get("svgDigest") == render["svgDigest"] and approved.get("sceneDigest") == render["sceneDigest"] else "PENDING"
                if approved and digest_status != "PASS":
                    digest_status = "FAIL"
                automated_status = "PASS"
                errors: list[str] = []
            except (CorpusError, AixemGraphicsError, OSError, ValueError, KeyError) as exc:
                static = {}
                render = {}
                digest_status = "FAIL"
                automated_status = "FAIL"
                errors = [str(exc)]
            visual = (
                check_visual_review(case, static.get("symbolDigest", ""), render.get("svgDigest", ""), reviews_by_corpus[corpus_root])
                if automated_status == "PASS"
                else {"status": "BLOCKED", "valid": False, "reason": "automated validation failed"}
            )
            result = {
                "id": case["id"],
                "title": case["title"],
                "tier": case["tier"],
                "corpus": corpus_root.name,
                "casePath": case_path.relative_to(ROOT).as_posix(),
                "symbolPath": symbol_path.relative_to(ROOT).as_posix(),
                "sourceBytes": symbol_path.stat().st_size,
                "caseContract": case,
                "automatedStatus": automated_status,
                "approvedDigestStatus": digest_status,
                "visualReview": visual,
                "static": static,
                "render": render,
                "durationMs": round((time.perf_counter() - started) * 1000.0, 3),
                "errors": errors,
            }
            results.append(result)
            by_corpus[corpus_root].append(result)
            print(f"{case['id']} {case['tier']}: automated={automated_status}; digest={digest_status}; visual={visual['status']}")

        if args.update_approved_digests:
            for corpus_root, items in by_corpus.items():
                approved = {
                    "schema": "https://schemas.aixem.org/conformance/approved-render-digests/1",
                    "release": RELEASE,
                    "profile": corpus_root.name,
                    "renderer": {"id": RENDERER_ID, "version": RENDERER_VERSION},
                    "cases": {
                        r["id"]: {
                            "sourceDigest": r["static"]["symbolDigest"],
                            "geometrySignatureDigest": r["static"]["geometrySignatureDigest"],
                            "svgDigest": r["render"]["svgDigest"],
                            "sceneDigest": r["render"]["sceneDigest"],
                        }
                        for r in items
                        if r["automatedStatus"] == "PASS"
                    },
                }
                write_json(corpus_root / "expected" / "approved-render-digests.json", approved)
                for r in items:
                    if r["automatedStatus"] == "PASS":
                        write_json(corpus_root / "expected" / "geometry-signatures" / f"{r['id']}.json", r["static"]["geometrySignature"])
                        r["approvedDigestStatus"] = "PASS"

        if args.write_review_template:
            for corpus_root, items in by_corpus.items():
                write_review_template(corpus_root, items)

        mu_result = None
        s030 = next((r for r in results if r["id"] == "S030" and r["automatedStatus"] == "PASS"), None)
        if s030:
            case_path = ROOT / s030["casePath"]
            mu_result = multi_unit_probe(s030, s030["caseContract"], case_path.parent / s030["caseContract"]["symbolPath"])

        summary = summarize(results, mu_result)
        if args.emit_report:
            emit_reports(results, summary, mu_result)
        payload = {
            "schema": "https://schemas.aixem.org/conformance/corpus-invocation/1",
            "release": RELEASE,
            "selection": {"case": args.case, "tier": args.tier, "all": args.all},
            "repeat": args.repeat,
            "summary": summary,
            "cases": results,
        }
        if args.json_out:
            write_json(args.json_out.resolve(), payload)

        automated_failures = [r["id"] for r in results if r["automatedStatus"] != "PASS"]
        digest_failures = [r["id"] for r in results if r["approvedDigestStatus"] == "FAIL"]
        visual_failures = [r["id"] for r in results if r["visualReview"]["status"] == "FAIL"]
        visual_pending = [r["id"] for r in results if r["visualReview"]["status"] in {"PENDING", "BLOCKED"}]
        print(f"cases: {len(results)}; automated failures: {len(automated_failures)}; visual failures: {len(visual_failures)}; visual pending: {len(visual_pending)}")
        if automated_failures or digest_failures or visual_failures:
            return 2
        if visual_pending and not args.allow_pending_review:
            return 3
        if mu_result and not mu_result["valid"]:
            return 4
        return 0
    except (CorpusError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
