#!/usr/bin/env python3
"""Deterministic reference renderer for the AIXEM component-graphics profile candidate.

This implementation intentionally treats source/library semantics as authoritative and
never infers connectivity from coincident geometry. It is non-normative and exists to
validate the candidate .aixproj/.aixlib/.aixsym/.aixlayout structure.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import math
import mimetypes
import pathlib
import re
import shlex
import sys
from dataclasses import dataclass
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

FIXED_TIME = "2026-08-10T00:00:00Z"
RENDERER_ID = "aixem-component-graphics-reference-renderer"
RENDERER_VERSION = "0.5.1"
SUPPORTED_SOURCE_FEATURES = {"component.graphics@1", "explicit.layout@1", "explicit.layout@2", "hierarchical.interface@1"}
SUPPORTED_SYMBOL_FEATURES = {"definition-use", "compound-path", "quadratic-bezier", "cubic-bezier", "elliptical-arc", "vector-pattern", "gradient", "dimension", "digest-locked-raster-image"}

SCHEMA_FILES = {
    "https://schemas.aixem.org/component-graphics/aixproj/1": ("component-graphics-1", "aixem-project-manifest-1.schema.json"),
    "https://schemas.aixem.org/component-graphics/aixproj/2": ("component-graphics-2", "aixem-project-manifest-2.schema.json"),
    "https://schemas.aixem.org/component-graphics/aixlib/1": ("component-graphics-1", "aixem-component-library-1.schema.json"),
    "https://schemas.aixem.org/component-graphics/aixsym/1": ("component-graphics-1", "aixem-symbol-asset-1.schema.json"),
    "https://schemas.aixem.org/component-graphics/aixlayout/1": ("component-graphics-1", "aixem-explicit-layout-1.schema.json"),
    "https://schemas.aixem.org/component-graphics/aixlayout/2": ("component-graphics-2", "aixem-explicit-layout-2.schema.json"),
}

INTERFACE_PORT_DIRECTIONS = {"input", "output", "bidirectional", "passive"}
INTERFACE_PORT_ROLES = {"signal", "power", "clock", "reset", "control", "analog"}
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


class AixemGraphicsError(RuntimeError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    return sha256_bytes(path.read_bytes())


def fmt(value: float | int) -> str:
    value = float(value)
    if abs(value) < 0.0000005:
        value = 0.0
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def xml(value: Any) -> str:
    return html.escape(str(value), quote=True)


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise AixemGraphicsError(f"cannot read JSON {path}: {exc}") from exc


def safe_resolve(base: pathlib.Path, relative: str) -> pathlib.Path:
    if pathlib.PurePosixPath(relative).is_absolute() or ".." in pathlib.PurePosixPath(relative).parts:
        raise AixemGraphicsError(f"unsafe project-relative path: {relative}")
    candidate = (base / pathlib.PurePosixPath(relative)).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise AixemGraphicsError(f"path escapes project root: {relative}") from exc
    return candidate


def validate_json(instance: Any, schema_path: pathlib.Path, label: str) -> None:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    if errors:
        rendered = []
        for issue in errors[:20]:
            location = "/".join(str(part) for part in issue.absolute_path) or "$"
            rendered.append(f"{label}:{location}: {issue.message}")
        if len(errors) > 20:
            rendered.append(f"... {len(errors) - 20} more schema errors")
        raise AixemGraphicsError("\n".join(rendered))


def schema_path(schema_root: pathlib.Path, schema_uri: str) -> pathlib.Path:
    """Resolve immutable v1/v2 schemas from either a family directory or the schemas root."""
    if schema_uri not in SCHEMA_FILES:
        raise AixemGraphicsError(f"unsupported schema URI: {schema_uri!r}")
    family, filename = SCHEMA_FILES[schema_uri]
    root = schema_root.resolve()
    candidates = [root / filename, root / family / filename, root.parent / family / filename]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise AixemGraphicsError(f"schema file is missing for {schema_uri}: {filename}")


def validate_declared_json(instance: Any, schema_root: pathlib.Path, label: str) -> None:
    validate_json(instance, schema_path(schema_root, str(instance.get("schema", ""))), label)


def verify_ref(project_root: pathlib.Path, ref: dict[str, Any], label: str) -> pathlib.Path:
    path = safe_resolve(project_root, ref["path"])
    if not path.is_file():
        raise AixemGraphicsError(f"{label} is missing: {ref['path']}")
    observed = sha256_file(path)
    if observed != ref["digest"]:
        raise AixemGraphicsError(f"{label} digest mismatch: expected {ref['digest']}, observed {observed}")
    return path


def parse_attributes(tokens: list[str], start: int = 0) -> dict[str, str]:
    result: dict[str, str] = {}
    for token in tokens[start:]:
        if "=" not in token:
            raise AixemGraphicsError(f"expected key=value token, got {token!r}")
        key, value = token.split("=", 1)
        if not key or key in result:
            raise AixemGraphicsError(f"invalid or duplicate attribute {key!r}")
        result[key] = value
    return result


def parse_aixem(path: pathlib.Path) -> dict[str, Any]:
    entities: dict[str, dict[str, Any]] = {}
    ports: dict[str, dict[str, Any]] = {}
    nets: dict[str, list[str]] = {}
    noconn: set[str] = set()
    features: list[dict[str, Any]] = []
    uses: list[dict[str, Any]] = []
    header: dict[str, Any] = {}
    model: dict[str, Any] | None = None
    seen_header = False

    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            tokens = shlex.split(stripped, posix=True)
        except ValueError as exc:
            raise AixemGraphicsError(f"{path.name}:{line_number}: {exc}") from exc
        if not tokens:
            continue
        keyword = tokens[0]
        if keyword == "aixem":
            if seen_header or len(tokens) != 2:
                raise AixemGraphicsError(f"{path.name}:{line_number}: invalid aixem header")
            header = {"version": tokens[1]}
            seen_header = True
        elif keyword == "model":
            if len(tokens) < 3:
                raise AixemGraphicsError(f"{path.name}:{line_number}: invalid model statement")
            model = {"id": tokens[1], **parse_attributes(tokens, 2)}
        elif keyword == "port":
            if len(tokens) < 2 or not IDENTIFIER_RE.fullmatch(tokens[1]):
                raise AixemGraphicsError(f"{path.name}:{line_number}: invalid interface port statement")
            port_id = tokens[1]
            if port_id in ports:
                raise AixemGraphicsError(f"{path.name}:{line_number}: duplicate interface port {port_id}")
            attrs = parse_attributes(tokens, 2)
            direction = attrs.get("direction", "passive")
            role = attrs.get("role", "signal")
            if direction not in INTERFACE_PORT_DIRECTIONS:
                raise AixemGraphicsError(f"{path.name}:{line_number}: unsupported interface port direction {direction!r}")
            if role not in INTERFACE_PORT_ROLES:
                raise AixemGraphicsError(f"{path.name}:{line_number}: unsupported interface port role {role!r}")
            ports[port_id] = {"id": port_id, "direction": direction, "role": role, "label": attrs.get("label", port_id), "attributes": attrs, "line": line_number}
        elif keyword in {"component", "connector", "instance"}:
            if len(tokens) < 3:
                raise AixemGraphicsError(f"{path.name}:{line_number}: invalid {keyword} statement")
            key = tokens[1]
            if key in entities:
                raise AixemGraphicsError(f"{path.name}:{line_number}: duplicate entity {key}")
            entities[key] = {"key": key, "kind": keyword, "attributes": parse_attributes(tokens, 2), "line": line_number}
        elif keyword == "net":
            if "=" not in tokens or len(tokens) < 5:
                raise AixemGraphicsError(f"{path.name}:{line_number}: invalid net statement")
            equals = tokens.index("=")
            if equals != 2:
                raise AixemGraphicsError(f"{path.name}:{line_number}: expected net <key> = <endpoints>")
            name = tokens[1]
            if name in nets:
                raise AixemGraphicsError(f"{path.name}:{line_number}: duplicate net {name}")
            nets[name] = tokens[3:]
        elif keyword == "noconn":
            if len(tokens) != 2:
                raise AixemGraphicsError(f"{path.name}:{line_number}: invalid noconn")
            endpoint = tokens[1]
            if endpoint in noconn:
                raise AixemGraphicsError(f"{path.name}:{line_number}: duplicate noconn {endpoint}")
            noconn.add(endpoint)
        elif keyword == "feature":
            if len(tokens) < 2:
                raise AixemGraphicsError(f"{path.name}:{line_number}: invalid feature statement")
            features.append({"id": tokens[1], **parse_attributes(tokens, 2), "line": line_number})
        elif keyword == "use":
            if len(tokens) < 4 or tokens[2] != "=":
                raise AixemGraphicsError(f"{path.name}:{line_number}: invalid use statement")
            uses.append({"alias": tokens[1], "uri": tokens[3], **parse_attributes(tokens, 4), "line": line_number})
        else:
            # Other WD 0.4 statements are preserved as source but not needed by this renderer.
            continue

    if not seen_header or model is None:
        raise AixemGraphicsError(f"{path.name}: missing aixem header or model statement")

    feature_map = {item["id"]: item for item in features}
    if ports or any(endpoint.startswith("@") for endpoints in nets.values() for endpoint in endpoints) or any(endpoint.startswith("@") for endpoint in noconn):
        feature = feature_map.get("hierarchical.interface@1")
        if feature is None or str(feature.get("required", "false")).lower() != "true":
            raise AixemGraphicsError(f"{path.name}: interface ports require feature hierarchical.interface@1 required=true")

    endpoint_owner: dict[str, str] = {}
    for net, endpoints in nets.items():
        if len(endpoints) < 2:
            raise AixemGraphicsError(f"net {net} has fewer than two endpoints")
        for endpoint in endpoints:
            if endpoint.startswith("@"):
                port_id = endpoint[1:]
                if not port_id or port_id not in ports:
                    raise AixemGraphicsError(f"unknown interface endpoint {endpoint} in net {net}")
            if endpoint in endpoint_owner:
                raise AixemGraphicsError(f"endpoint {endpoint} occurs in both {endpoint_owner[endpoint]} and {net}")
            endpoint_owner[endpoint] = net
    for endpoint in noconn:
        if endpoint.startswith("@") and endpoint[1:] not in ports:
            raise AixemGraphicsError(f"unknown interface endpoint {endpoint} in noconn")
    overlap = sorted(noconn.intersection(endpoint_owner))
    if overlap:
        raise AixemGraphicsError(f"endpoints both connected and noconn: {overlap}")

    return {
        "header": header,
        "model": model,
        "entities": entities,
        "ports": ports,
        "nets": nets,
        "endpointOwners": endpoint_owner,
        "noconn": sorted(noconn),
        "features": features,
        "uses": uses,
        "sourceDigest": sha256_file(path),
        "sourcePath": str(path),
    }


def eval_numeric(expr: Any, parameters: dict[str, Any]) -> float:
    if isinstance(expr, bool):
        raise AixemGraphicsError("boolean is not a numeric expression")
    if isinstance(expr, (int, float)):
        return float(expr)
    if not isinstance(expr, dict):
        raise AixemGraphicsError(f"invalid numeric expression: {expr!r}")
    if "param" in expr:
        name = expr["param"]
        if name not in parameters:
            raise AixemGraphicsError(f"unknown parameter {name}")
        value = parameters[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise AixemGraphicsError(f"parameter {name} is not numeric")
        return float(value)
    op = expr.get("op")
    args = [eval_numeric(arg, parameters) for arg in expr.get("args", [])]
    if op == "add": return sum(args)
    if op == "sub":
        if not args: raise AixemGraphicsError("sub requires arguments")
        return args[0] - sum(args[1:])
    if op == "mul":
        result = 1.0
        for arg in args: result *= arg
        return result
    if op == "div":
        if len(args) != 2 or args[1] == 0: raise AixemGraphicsError("div requires two arguments and non-zero divisor")
        return args[0] / args[1]
    if op == "min": return min(args)
    if op == "max": return max(args)
    if op == "clamp":
        if len(args) != 3: raise AixemGraphicsError("clamp requires value, minimum, maximum")
        return max(args[1], min(args[2], args[0]))
    if op == "neg":
        if len(args) != 1: raise AixemGraphicsError("neg requires one argument")
        return -args[0]
    if op == "abs":
        if len(args) != 1: raise AixemGraphicsError("abs requires one argument")
        return abs(args[0])
    raise AixemGraphicsError(f"unsupported numeric operation {op!r}")


def eval_value(expr: Any, parameters: dict[str, Any], fields: dict[str, Any]) -> Any:
    if not isinstance(expr, dict):
        return expr
    if "param" in expr:
        return parameters.get(expr["param"])
    if "field" in expr:
        return fields.get(expr["field"])
    raise AixemGraphicsError(f"invalid value expression {expr!r}")


def eval_predicate(expr: Any, parameters: dict[str, Any], fields: dict[str, Any]) -> bool:
    if isinstance(expr, bool):
        return expr
    op = expr["op"]
    if op == "and": return all(eval_predicate(arg, parameters, fields) for arg in expr["args"])
    if op == "or": return any(eval_predicate(arg, parameters, fields) for arg in expr["args"])
    if op == "not": return not eval_predicate(expr["arg"], parameters, fields)
    left = eval_value(expr["left"], parameters, fields)
    right_raw = expr["right"]
    if isinstance(right_raw, list):
        right = [eval_value(item, parameters, fields) for item in right_raw]
    else:
        right = eval_value(right_raw, parameters, fields)
    if op == "eq": return left == right
    if op == "ne": return left != right
    if op == "lt": return left < right
    if op == "lte": return left <= right
    if op == "gt": return left > right
    if op == "gte": return left >= right
    if op == "in": return left in right
    raise AixemGraphicsError(f"unsupported predicate operation {op!r}")


def matrix_multiply(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, ...]:
    a1,b1,c1,d1,e1,f1 = left
    a2,b2,c2,d2,e2,f2 = right
    return (
        a1*a2 + c1*b2,
        b1*a2 + d1*b2,
        a1*c2 + c1*d2,
        b1*c2 + d1*d2,
        a1*e2 + c1*f2 + e1,
        b1*e2 + d1*f2 + f1,
    )


def transform_point(matrix: tuple[float, ...], point: tuple[float, float]) -> tuple[float, float]:
    a,b,c,d,e,f = matrix
    x,y = point
    return a*x+c*y+e, b*x+d*y+f


def placement_matrix(placement: dict[str, Any], symbol: dict[str, Any], layout_cs: dict[str, Any]) -> tuple[float, ...]:
    scale_x = float(placement.get("scaleX", 1)) * (-1 if placement.get("mirrorX", False) else 1)
    scale_y = float(placement.get("scaleY", 1)) * (-1 if placement.get("mirrorY", False) else 1)
    if symbol["coordinateSystem"]["yAxis"] != layout_cs["yAxis"]:
        scale_y *= -1
    angle = float(placement.get("rotation", 0))
    # SVG positive rotation is clockwise in a down-axis coordinate system.
    if layout_cs["angleDirection"] == "counterclockwise":
        angle = -angle
    radians = math.radians(angle)
    cos_a, sin_a = math.cos(radians), math.sin(radians)
    translate = (1.0, 0.0, 0.0, 1.0, float(placement["x"]), float(placement["y"]))
    rotate = (cos_a, sin_a, -sin_a, cos_a, 0.0, 0.0)
    scale = (scale_x, 0.0, 0.0, scale_y, 0.0, 0.0)
    return matrix_multiply(translate, matrix_multiply(rotate, scale))


def matrix_svg(matrix: Iterable[float]) -> str:
    return "matrix(" + " ".join(fmt(item) for item in matrix) + ")"


def style_attributes(style: dict[str, Any], paint_prefix: str = "") -> str:
    mapping = {
        "stroke": "stroke", "strokeWidth": "stroke-width", "strokeLinecap": "stroke-linecap",
        "strokeLinejoin": "stroke-linejoin", "strokeMiterlimit": "stroke-miterlimit",
        "dashOffset": "stroke-dashoffset", "fill": "fill", "fillRule": "fill-rule",
        "opacity": "opacity", "fontFamily": "font-family", "fontSize": "font-size",
        "fontWeight": "font-weight", "fontStyle": "font-style", "textDecoration": "text-decoration",
        "letterSpacing": "letter-spacing", "pointerEvents": "pointer-events",
    }
    attrs: list[str] = []
    for key, svg_key in mapping.items():
        if key not in style:
            continue
        value = style[key]
        if key in {"fill", "stroke"} and isinstance(value, str) and value.startswith("paint:"):
            value = f"url(#{paint_prefix}{value[6:]})"
        attrs.append(f'{svg_key}="{xml(value)}"')
    if "dashArray" in style:
        attrs.append('stroke-dasharray="' + " ".join(fmt(v) for v in style["dashArray"]) + '"')
    return " ".join(attrs)


@dataclass
class LoadedAsset:
    path: pathlib.Path
    data: dict[str, Any]
    digest: str


@dataclass
class EntityBinding:
    source: dict[str, Any]
    component: dict[str, Any]
    presentation: dict[str, Any]
    asset: LoadedAsset
    placement: dict[str, Any]
    parameters: dict[str, Any]
    fields: dict[str, Any]
    variant: dict[str, Any] | None
    matrix: tuple[float, ...]
    port_positions: dict[str, tuple[float, float]]


class ProjectRenderer:
    def __init__(
        self,
        project_file: pathlib.Path,
        schema_root: pathlib.Path,
        *,
        project_doc: dict[str, Any] | None = None,
        project_root: pathlib.Path | None = None,
    ):
        self.project_file = project_file.resolve()
        self.project_root = (project_root or self.project_file.parent).resolve()
        self.schema_root = schema_root.resolve()
        self.project_doc = project_doc if project_doc is not None else load_json(self.project_file)
        validate_declared_json(self.project_doc, self.schema_root, "project")
        self.project = self.project_doc["project"]
        self.source_path = verify_ref(self.project_root, self.project["source"], "source")
        self.layout_path = verify_ref(self.project_root, self.project["layout"], "layout")
        self.layout_doc = load_json(self.layout_path)
        validate_declared_json(self.layout_doc, self.schema_root, "layout")
        self.layout = self.layout_doc["layout"]
        self.semantic = parse_aixem(self.source_path)
        for feature in self.semantic["features"]:
            required = str(feature.get("required", "false")).lower() == "true"
            if required and feature["id"] not in SUPPORTED_SOURCE_FEATURES:
                raise AixemGraphicsError(f"unsupported required source feature {feature['id']}")
        self.libraries: list[tuple[pathlib.Path, dict[str, Any]]] = []
        self.components: dict[str, tuple[dict[str, Any], pathlib.Path]] = {}
        self.assets: dict[str, LoadedAsset] = {}
        self.bindings: dict[str, EntityBinding] = {}
        self.sheet_port_positions: dict[str, tuple[float, float]] = {}
        self.sheet_port_presentations: dict[str, dict[str, Any]] = {}
        self.diagnostics: list[dict[str, Any]] = []
        self.primitive_count = 0
        self.feature_usage: set[str] = set()
        self._load_libraries()
        self._bind_entities()
        self._validate_semantics_and_layout()

    def _load_libraries(self) -> None:
        for index, ref in enumerate(self.project["libraries"]):
            path = verify_ref(self.project_root, ref, f"library[{index}]")
            doc = load_json(path)
            validate_declared_json(doc, self.schema_root, f"library[{index}]")
            library = doc["library"]
            self.libraries.append((path, library))
            for component in library["components"]:
                component_id = component["id"]
                if component_id in self.components:
                    raise AixemGraphicsError(f"duplicate component type across libraries: {component_id}")
                self.components[component_id] = (component, path)

    def _load_asset(self, presentation: dict[str, Any]) -> LoadedAsset:
        ref = presentation["asset"]
        path = safe_resolve(self.project_root, ref["path"])
        if not path.is_file():
            raise AixemGraphicsError(f"symbol asset is missing: {ref['path']}")
        observed = sha256_file(path)
        if observed != ref["digest"]:
            raise AixemGraphicsError(f"symbol asset digest mismatch for {ref['path']}")
        cache_key = str(path)
        if cache_key not in self.assets:
            doc = load_json(path)
            validate_declared_json(doc, self.schema_root, f"symbol:{path.name}")
            symbol = doc["symbol"]
            unknown_features = sorted(set(symbol.get("requiredFeatures", [])) - SUPPORTED_SYMBOL_FEATURES)
            if unknown_features:
                raise AixemGraphicsError(f"unsupported required symbol features for {ref['path']}: {unknown_features}")
            if symbol["id"] != ref["symbolId"] or symbol["revision"] != ref["revision"]:
                raise AixemGraphicsError(f"symbol identity mismatch for {ref['path']}")
            self.assets[cache_key] = LoadedAsset(path=path, data=doc, digest=observed)
        return self.assets[cache_key]

    def _resolve_parameters(self, symbol: dict[str, Any], placement: dict[str, Any], variant: dict[str, Any] | None) -> dict[str, Any]:
        result: dict[str, Any] = {}
        definitions = symbol.get("parameters", {})
        for name, definition in definitions.items():
            result[name] = definition["default"]
        if variant:
            result.update(variant.get("parameterDefaults", {}))
        result.update(placement.get("parameters", {}))
        unknown = sorted(set(result) - set(definitions))
        if unknown:
            raise AixemGraphicsError(f"unknown symbol parameters: {unknown}")
        for name, definition in definitions.items():
            value = result[name]
            kind = definition["type"]
            if kind in {"number", "length", "angle"}:
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise AixemGraphicsError(f"parameter {name} must be numeric")
                if "minimum" in definition and value < definition["minimum"]:
                    raise AixemGraphicsError(f"parameter {name} below minimum")
                if "maximum" in definition and value > definition["maximum"]:
                    raise AixemGraphicsError(f"parameter {name} above maximum")
            elif kind == "integer" and (isinstance(value, bool) or not isinstance(value, int)):
                raise AixemGraphicsError(f"parameter {name} must be integer")
            elif kind == "boolean" and not isinstance(value, bool):
                raise AixemGraphicsError(f"parameter {name} must be boolean")
            elif kind == "string" and not isinstance(value, str):
                raise AixemGraphicsError(f"parameter {name} must be string")
            elif kind == "enum" and value not in definition.get("values", []):
                raise AixemGraphicsError(f"parameter {name} is outside its value set")
        return result

    def _bind_entities(self) -> None:
        placements = {item["entity"]: item for item in self.layout["placements"]}
        if len(placements) != len(self.layout["placements"]):
            raise AixemGraphicsError("duplicate placement entity")
        missing = sorted(set(self.semantic["entities"]) - set(placements))
        extra = sorted(set(placements) - set(self.semantic["entities"]))
        if missing or extra:
            raise AixemGraphicsError(f"placement closure mismatch: missing={missing}, extra={extra}")

        for key, entity in sorted(self.semantic["entities"].items()):
            type_id = entity["attributes"].get("type")
            if not type_id or type_id not in self.components:
                raise AixemGraphicsError(f"entity {key} has unresolved component type {type_id!r}")
            component, _library_path = self.components[type_id]
            presentations = [p for p in component["presentations"] if p["purpose"] == self.project["renderPolicy"]["purpose"]]
            if not presentations:
                presentations = component["presentations"]
            presentation = presentations[0]
            asset = self._load_asset(presentation)
            symbol = asset.data["symbol"]
            placement = placements[key]
            variant_id = placement.get("variant") or presentation.get("defaultVariant") or symbol.get("defaultVariant")
            variants = {item["id"]: item for item in symbol.get("variants", [])}
            variant = variants.get(variant_id) if variant_id else None
            if variant_id and variant is None:
                raise AixemGraphicsError(f"entity {key} requests unknown variant {variant_id}")
            parameters = self._resolve_parameters(symbol, placement, variant)
            fields: dict[str, Any] = {
                "entity": key,
                "reference": entity["attributes"].get("refdes", key),
                "value": entity["attributes"].get("value", component["displayName"]),
                "type": type_id,
                "title": component["displayName"],
            }
            for field_name, attribute_name in presentation.get("fieldMap", {}).items():
                fields[field_name] = entity["attributes"].get(attribute_name, "")
            fields.update(entity["attributes"])
            fields.update(placement.get("fields", {}))
            matrix = placement_matrix(placement, symbol, self.layout["coordinateSystem"])
            symbol_ports = {port["id"]: port for port in symbol["ports"]}
            semantic_ports = {port["id"]: port for port in component["ports"]}
            if set(presentation["portMap"]) != set(semantic_ports):
                raise AixemGraphicsError(f"component {type_id} presentation portMap is not total")
            port_positions: dict[str, tuple[float, float]] = {}
            for semantic_port, symbol_port_id in presentation["portMap"].items():
                if symbol_port_id not in symbol_ports:
                    raise AixemGraphicsError(f"component {type_id} maps to unknown symbol port {symbol_port_id}")
                port = dict(symbol_ports[symbol_port_id])
                if variant and symbol_port_id in variant.get("portOverrides", {}):
                    port.update(variant["portOverrides"][symbol_port_id])
                if "visibleWhen" in port and not eval_predicate(port["visibleWhen"], parameters, fields):
                    raise AixemGraphicsError(f"mapped symbol port {symbol_port_id} is hidden for entity {key}")
                local = (eval_numeric(port["x"], parameters), eval_numeric(port["y"], parameters))
                port_positions[semantic_port] = transform_point(matrix, local)
            self.bindings[key] = EntityBinding(
                source=entity, component=component, presentation=presentation, asset=asset,
                placement=placement, parameters=parameters, fields=fields, variant=variant,
                matrix=matrix, port_positions=port_positions,
            )

    def _validate_endpoint(self, endpoint: str) -> None:
        if endpoint.startswith("@"):
            port_id = endpoint[1:]
            if not port_id or port_id not in self.semantic.get("ports", {}):
                raise AixemGraphicsError(f"interface endpoint does not exist: {endpoint}")
            return
        if "." not in endpoint:
            raise AixemGraphicsError(f"malformed endpoint {endpoint}")
        owner, port = endpoint.split(".", 1)
        if owner not in self.bindings:
            raise AixemGraphicsError(f"endpoint owner does not exist: {endpoint}")
        if port not in self.bindings[owner].port_positions:
            raise AixemGraphicsError(f"endpoint port does not exist: {endpoint}")

    def _validate_semantics_and_layout(self) -> None:
        if self.layout["designId"] != self.semantic["model"]["id"]:
            raise AixemGraphicsError("layout designId does not match source model ID")
        layer_ids = {item["id"] for item in self.layout["layers"]}
        if len(layer_ids) != len(self.layout["layers"]):
            raise AixemGraphicsError("layout contains duplicate layer IDs")

        sheet_ports = self.layout.get("sheetPorts", [])
        if sheet_ports and self.layout_doc.get("schema") != "https://schemas.aixem.org/component-graphics/aixlayout/2":
            raise AixemGraphicsError("sheetPorts require aixlayout/2")
        for item in sheet_ports:
            port_id = item["port"]
            if port_id in self.sheet_port_presentations:
                raise AixemGraphicsError(f"duplicate sheetPort presentation for {port_id}")
            if port_id not in self.semantic.get("ports", {}):
                raise AixemGraphicsError(f"layout sheetPort references unknown semantic port {port_id}")
            layer = item.get("layer", "connections")
            if layer not in layer_ids:
                raise AixemGraphicsError(f"sheetPort {port_id} references unknown layer {layer}")
            x, y = float(item["x"]), float(item["y"])
            width, height = float(self.layout["sheet"]["width"]), float(self.layout["sheet"]["height"])
            if x < 0 or y < 0 or x > width or y > height:
                raise AixemGraphicsError(f"sheetPort {port_id} coordinate is outside the sheet")
            self.sheet_port_positions[port_id] = (x, y)
            self.sheet_port_presentations[port_id] = item
        expected_ports = set(self.semantic.get("ports", {}))
        if expected_ports:
            if self.layout_doc.get("schema") != "https://schemas.aixem.org/component-graphics/aixlayout/2":
                raise AixemGraphicsError("semantic interface ports require aixlayout/2")
            missing_ports = sorted(expected_ports - set(self.sheet_port_presentations))
            extra_ports = sorted(set(self.sheet_port_presentations) - expected_ports)
            if missing_ports or extra_ports:
                raise AixemGraphicsError(f"sheetPort presentation closure mismatch: missing={missing_ports}, extra={extra_ports}")

        for placement in self.layout["placements"]:
            if placement.get("layer", "symbols") not in layer_ids:
                raise AixemGraphicsError(f"placement {placement['entity']} references unknown layer")
        for endpoints in self.semantic["nets"].values():
            for endpoint in endpoints:
                self._validate_endpoint(endpoint)
        for endpoint in self.semantic["noconn"]:
            self._validate_endpoint(endpoint)

        connection_by_net: dict[str, dict[str, Any]] = {}
        referenced_endpoints: dict[str, set[str]] = {}
        for connection in self.layout.get("connections", []):
            net = connection["net"]
            if net not in self.semantic["nets"]:
                raise AixemGraphicsError(f"layout references unknown net {net}")
            if net in connection_by_net:
                raise AixemGraphicsError(f"layout has duplicate connection record for net {net}")
            if connection.get("layer", "connections") not in layer_ids:
                raise AixemGraphicsError(f"connection {net} references unknown layer")
            connection_by_net[net] = connection
            referenced_endpoints[net] = set()
            allowed = set(self.semantic["nets"][net])
            for route in connection["paths"]:
                for side in ("from", "to"):
                    endpoint = route[side].get("endpoint")
                    if endpoint:
                        if endpoint not in allowed:
                            raise AixemGraphicsError(f"route for net {net} references endpoint {endpoint} outside semantic net")
                        self._validate_endpoint(endpoint)
                        referenced_endpoints[net].add(endpoint)
        missing_connections = sorted(set(self.semantic["nets"]) - set(connection_by_net))
        if missing_connections:
            raise AixemGraphicsError(f"semantic nets have no layout connection: {missing_connections}")
        for net, endpoints in self.semantic["nets"].items():
            missing = sorted(set(endpoints) - referenced_endpoints[net])
            if missing:
                raise AixemGraphicsError(f"layout does not route all semantic endpoints of net {net}: {missing}")

    def _node_visible(self, node: dict[str, Any], parameters: dict[str, Any], fields: dict[str, Any], suppressed: set[str]) -> bool:
        if node.get("id") in suppressed:
            return False
        return "visibleWhen" not in node or eval_predicate(node["visibleWhen"], parameters, fields)

    def _node_common(self, node: dict[str, Any], binding: EntityBinding | None, asset_prefix: str, semantic_attrs: str = "") -> tuple[str, str]:
        attrs: list[str] = []
        if node.get("id"):
            attrs.append(f'id="{xml(asset_prefix + node["id"])}"')
        if node.get("layer"):
            attrs.append(f'data-symbol-layer="{xml(node["layer"])}"')
        if node.get("role"):
            attrs.append(f'data-role="{xml(node["role"])}"')
        if node.get("classes"):
            attrs.append(f'class="{xml(" ".join(node["classes"]))}"')
        if node.get("transform"):
            attrs.append(f'transform="{matrix_svg(tuple(node["transform"]))}"')
        if semantic_attrs:
            attrs.append(semantic_attrs)
        style = {}
        if binding and node.get("style"):
            style = binding.asset.data["symbol"]["styles"].get(node["style"], {})
        if style:
            attrs.append(style_attributes(style, asset_prefix + "paint-"))
        return " ".join(attrs), node.get("style", "")

    def _path_data(self, commands: list[dict[str, Any]], parameters: dict[str, Any]) -> str:
        result: list[str] = []
        for command in commands:
            cmd = command["cmd"]
            if cmd in {"M", "L"}:
                result.append(f"{cmd} {fmt(eval_numeric(command['x'], parameters))} {fmt(eval_numeric(command['y'], parameters))}")
            elif cmd == "Q":
                result.append("Q " + " ".join(fmt(eval_numeric(command[k], parameters)) for k in ("x1", "y1", "x", "y")))
            elif cmd == "C":
                result.append("C " + " ".join(fmt(eval_numeric(command[k], parameters)) for k in ("x1", "y1", "x2", "y2", "x", "y")))
            elif cmd == "A":
                result.append("A " + " ".join([
                    fmt(eval_numeric(command["rx"], parameters)), fmt(eval_numeric(command["ry"], parameters)),
                    fmt(eval_numeric(command["rotation"], parameters)), "1" if command["largeArc"] else "0",
                    "1" if command["sweep"] else "0", fmt(eval_numeric(command["x"], parameters)), fmt(eval_numeric(command["y"], parameters)),
                ]))
            elif cmd == "Z":
                result.append("Z")
        return " ".join(result)

    def _render_node(self, node: dict[str, Any], binding: EntityBinding, asset_prefix: str, suppressed: set[str], definitions: dict[str, Any], local_parameters: dict[str, Any] | None = None, depth: int = 0) -> str:
        if depth > 64:
            raise AixemGraphicsError("symbol definition recursion exceeds 64 levels")
        parameters = binding.parameters if local_parameters is None else local_parameters
        fields = binding.fields
        if not self._node_visible(node, parameters, fields, suppressed):
            return ""
        self.primitive_count += 1
        node_type = node["type"]
        common, _style = self._node_common(node, binding, asset_prefix)
        if node_type == "group":
            children = "".join(self._render_node(child, binding, asset_prefix, suppressed, definitions, parameters, depth+1) for child in node["children"])
            return f"<g {common}>{children}</g>"
        if node_type == "use":
            name = node["definition"]
            if name not in definitions:
                raise AixemGraphicsError(f"unknown symbol definition {name}")
            next_params = dict(parameters)
            for key, value in node.get("parameters", {}).items():
                next_params[key] = eval_value(value, parameters, fields)
            child = self._render_node(definitions[name], binding, asset_prefix, suppressed, definitions, next_params, depth+1)
            self.feature_usage.add("definition-use")
            return f"<g {common} data-definition=\"{xml(name)}\">{child}</g>"
        if node_type == "line":
            values = {k: fmt(eval_numeric(node[k], parameters)) for k in ("x1", "y1", "x2", "y2")}
            return f'<line {common} x1="{values["x1"]}" y1="{values["y1"]}" x2="{values["x2"]}" y2="{values["y2"]}"/>'
        if node_type in {"polyline", "polygon"}:
            points = " ".join(f"{fmt(eval_numeric(p[0], parameters))},{fmt(eval_numeric(p[1], parameters))}" for p in node["points"])
            tag = "polygon" if node_type == "polygon" or node.get("closed") else "polyline"
            return f'<{tag} {common} points="{points}"/>'
        if node_type == "rect":
            attrs = " ".join(f'{k}="{fmt(eval_numeric(node[k], parameters))}"' for k in ("x", "y", "width", "height"))
            for key in ("rx", "ry"):
                if key in node: attrs += f' {key}="{fmt(eval_numeric(node[key], parameters))}"'
            return f"<rect {common} {attrs}/>"
        if node_type == "circle":
            attrs = " ".join(f'{k}="{fmt(eval_numeric(node[k], parameters))}"' for k in ("cx", "cy", "r"))
            return f"<circle {common} {attrs}/>"
        if node_type == "ellipse":
            attrs = " ".join(f'{k}="{fmt(eval_numeric(node[k], parameters))}"' for k in ("cx", "cy", "rx", "ry"))
            return f"<ellipse {common} {attrs}/>"
        if node_type == "arc":
            cx, cy = eval_numeric(node["cx"], parameters), eval_numeric(node["cy"], parameters)
            rx, ry = eval_numeric(node["rx"], parameters), eval_numeric(node["ry"], parameters)
            start, sweep = eval_numeric(node["startAngle"], parameters), eval_numeric(node["sweepAngle"], parameters)
            start_r, end_r = math.radians(start), math.radians(start+sweep)
            x1, y1 = cx+rx*math.cos(start_r), cy+ry*math.sin(start_r)
            x2, y2 = cx+rx*math.cos(end_r), cy+ry*math.sin(end_r)
            large = 1 if abs(sweep) > 180 else 0
            sweep_flag = 1 if sweep >= 0 else 0
            d = f"M {fmt(x1)} {fmt(y1)} A {fmt(rx)} {fmt(ry)} 0 {large} {sweep_flag} {fmt(x2)} {fmt(y2)}"
            self.feature_usage.add("elliptical-arc")
            return f'<path {common} d="{d}"/>'
        if node_type == "path":
            self.feature_usage.add("compound-path")
            commands = {item["cmd"] for item in node["commands"]}
            if "C" in commands: self.feature_usage.add("cubic-bezier")
            if "Q" in commands: self.feature_usage.add("quadratic-bezier")
            if "A" in commands: self.feature_usage.add("elliptical-arc")
            extra = f' fill-rule="{xml(node["fillRule"])}"' if "fillRule" in node else ""
            return f'<path {common}{extra} d="{xml(self._path_data(node["commands"], parameters))}"/>'
        if node_type == "text":
            text_value = node.get("text", "")
            if "field" in node:
                text_value = fields.get(node["field"], "")
            attrs = [f'x="{fmt(eval_numeric(node["x"], parameters))}"', f'y="{fmt(eval_numeric(node["y"], parameters))}"']
            if "rotation" in node:
                x = eval_numeric(node["x"], parameters); y = eval_numeric(node["y"], parameters); angle = eval_numeric(node["rotation"], parameters)
                attrs.append(f'transform="rotate({fmt(angle)} {fmt(x)} {fmt(y)})"')
            if "anchor" in node: attrs.append(f'text-anchor="{xml(node["anchor"])}"')
            if "baseline" in node: attrs.append(f'dominant-baseline="{xml(node["baseline"])}"')
            return f'<text {common} {" ".join(attrs)}>{xml(text_value)}</text>'
        if node_type == "image":
            source = node["source"]
            image_path = safe_resolve(self.project_root, source["path"])
            if not image_path.is_file() or sha256_file(image_path) != source["digest"]:
                raise AixemGraphicsError(f"invalid image source {source['path']}")
            media = source["mediaType"]
            if media not in {"image/png", "image/jpeg", "image/webp"}:
                raise AixemGraphicsError("unsafe image media type")
            payload = base64.b64encode(image_path.read_bytes()).decode("ascii")
            attrs = " ".join(f'{k}="{fmt(eval_numeric(node[k], parameters))}"' for k in ("x", "y", "width", "height"))
            self.feature_usage.add("digest-locked-raster-image")
            return f'<image {common} {attrs} href="data:{media};base64,{payload}"/>'
        if node_type == "dimension":
            p1 = (eval_numeric(node["from"][0], parameters), eval_numeric(node["from"][1], parameters))
            p2 = (eval_numeric(node["to"][0], parameters), eval_numeric(node["to"][1], parameters))
            offset = eval_numeric(node["offset"], parameters)
            return self._dimension_svg(p1, p2, offset, node.get("text"), node.get("unit", ""), int(node.get("precision", 0)), common)
        raise AixemGraphicsError(f"unsupported node type {node_type}")

    def _dimension_svg(self, p1: tuple[float,float], p2: tuple[float,float], offset: float, text: str | None, unit: str, precision: int, common: str) -> str:
        dx, dy = p2[0]-p1[0], p2[1]-p1[1]
        length = math.hypot(dx, dy)
        if length == 0: raise AixemGraphicsError("zero-length dimension")
        nx, ny = -dy/length, dx/length
        q1, q2 = (p1[0]+nx*offset, p1[1]+ny*offset), (p2[0]+nx*offset, p2[1]+ny*offset)
        label = text if text is not None else f"{length:.{precision}f}{unit}"
        mx, my = (q1[0]+q2[0])/2, (q1[1]+q2[1])/2
        self.feature_usage.add("dimension")
        return (
            f'<g {common} class="dimension">'
            f'<line x1="{fmt(p1[0])}" y1="{fmt(p1[1])}" x2="{fmt(q1[0])}" y2="{fmt(q1[1])}"/>'
            f'<line x1="{fmt(p2[0])}" y1="{fmt(p2[1])}" x2="{fmt(q2[0])}" y2="{fmt(q2[1])}"/>'
            f'<line x1="{fmt(q1[0])}" y1="{fmt(q1[1])}" x2="{fmt(q2[0])}" y2="{fmt(q2[1])}" marker-start="url(#dimension-arrow)" marker-end="url(#dimension-arrow)"/>'
            f'<text class="dimension-label" x="{fmt(mx)}" y="{fmt(my-2)}" text-anchor="middle" fill="#17231d" stroke="none" font-family="Arial, sans-serif" font-size="3">{xml(label)}</text></g>'
        )

    def _paint_servers(self, binding: EntityBinding, prefix: str) -> str:
        symbol = binding.asset.data["symbol"]
        result: list[str] = []
        for name, paint in sorted(symbol.get("paintServers", {}).items()):
            pid = prefix + "paint-" + name
            if paint["type"] == "pattern":
                body = "".join(self._render_node(node, binding, prefix+"pattern-", set(), symbol.get("definitions", {})) for node in paint["graphics"])
                rotation = paint.get("rotation", 0)
                transform = f' patternTransform="rotate({fmt(rotation)})"' if rotation else ""
                result.append(f'<pattern id="{xml(pid)}" patternUnits="userSpaceOnUse" x="{fmt(paint.get("x",0))}" y="{fmt(paint.get("y",0))}" width="{fmt(paint["width"])}" height="{fmt(paint["height"])}"{transform}>{body}</pattern>')
                self.feature_usage.add("vector-pattern")
            elif paint["type"] in {"linear-gradient", "radial-gradient"}:
                tag = "linearGradient" if paint["type"] == "linear-gradient" else "radialGradient"
                keys = ("x1","y1","x2","y2") if tag == "linearGradient" else ("cx","cy","r","fx","fy")
                attrs = " ".join(f'{k}="{fmt(paint[k])}"' for k in keys if k in paint)
                stops = "".join(f'<stop offset="{fmt(stop["offset"]*100)}%" stop-color="{xml(stop["color"])}" stop-opacity="{fmt(stop.get("opacity",1))}"/>' for stop in paint["stops"])
                result.append(f'<{tag} id="{xml(pid)}" gradientUnits="userSpaceOnUse" {attrs}>{stops}</{tag}>')
                self.feature_usage.add("gradient")
        return "".join(result)

    def _render_entity(self, key: str, binding: EntityBinding) -> tuple[str, str]:
        symbol = binding.asset.data["symbol"]
        prefix = re.sub(r"[^a-zA-Z0-9_-]", "-", f"{key}-")
        suppressed = set(binding.variant.get("suppress", []) if binding.variant else [])
        graphics = list(symbol["graphics"])
        if binding.variant:
            graphics.extend(binding.variant.get("graphics", []))
        defs = self._paint_servers(binding, prefix)
        body = "".join(self._render_node(node, binding, prefix, suppressed, symbol.get("definitions", {})) for node in graphics)
        entity_label = f"{binding.fields.get('reference', key)} — {binding.component['displayName']}"
        attrs = (
            f'data-entity="{xml(key)}" data-component-type="{xml(binding.component["id"])}" '
            f'aria-label="{xml(entity_label)}" tabindex="0" class="entity symbol-instance" '
            f'transform="{matrix_svg(binding.matrix)}"'
        )
        return defs, f'<g {attrs}><title>{xml(entity_label)}</title>{body}</g>'

    def _resolve_route_end(self, item: dict[str, Any]) -> tuple[float, float]:
        if "point" in item:
            return float(item["point"][0]), float(item["point"][1])
        endpoint = item["endpoint"]
        if endpoint.startswith("@"):
            port_id = endpoint[1:]
            if port_id not in self.sheet_port_positions:
                raise AixemGraphicsError(f"PROJECT_ROUTE_UNRESOLVED_PORT: {endpoint}")
            return self.sheet_port_positions[port_id]
        owner, port = endpoint.split(".", 1)
        return self.bindings[owner].port_positions[port]

    def _render_sheet_port(self, port_id: str, item: dict[str, Any]) -> str:
        semantic = self.semantic["ports"][port_id]
        x, y = self.sheet_port_positions[port_id]
        side = item.get("side", "right")
        label = item.get("label", semantic.get("label", port_id))
        offsets = {
            "left": ((4.0, 0.0), (6.0, -1.2), "start", "M 0 0 L 4 -2 L 4 2 Z"),
            "right": ((-4.0, 0.0), (-6.0, -1.2), "end", "M 0 0 L -4 -2 L -4 2 Z"),
            "top": ((0.0, 4.0), (0.0, 7.0), "middle", "M 0 0 L -2 4 L 2 4 Z"),
            "bottom": ((0.0, -4.0), (0.0, -6.0), "middle", "M 0 0 L -2 -4 L 2 -4 Z"),
        }
        line_delta, label_delta, anchor, path = offsets[side]
        lx, ly = x + line_delta[0], y + line_delta[1]
        tx, ty = x + label_delta[0], y + label_delta[1]
        local_net = self.semantic.get("endpointOwners", {}).get(f"@{port_id}", "")
        return (
            f'<g class="sheet-port" data-interface-port="{xml(port_id)}" data-local-net="{xml(local_net)}" '
            f'data-direction="{xml(semantic["direction"])}" data-role="{xml(semantic["role"])}" transform="translate({fmt(x)} {fmt(y)})">'
            f'<title>Interface port {xml(port_id)}</title><path d="{path}" fill="#ffffff" stroke="#2458a6" stroke-width=".8"/>'
            f'</g><line class="sheet-port-stub" data-interface-port="{xml(port_id)}" x1="{fmt(x)}" y1="{fmt(y)}" x2="{fmt(lx)}" y2="{fmt(ly)}" stroke="#2458a6" stroke-width=".8"/>'
            f'<text class="sheet-port-label" data-interface-port="{xml(port_id)}" x="{fmt(tx)}" y="{fmt(ty)}" text-anchor="{anchor}" '
            f'font-family="Arial, sans-serif" font-size="3.2" font-weight="600" fill="#2458a6">{xml(label)}</text>'
        )

    def _layout_style_attrs(self, style_name: str | None, default: dict[str, Any]) -> str:
        style = dict(default)
        if style_name:
            style.update(self.layout.get("styles", {}).get(style_name, {}))
        return style_attributes(style)

    def build_svg(self) -> tuple[str, dict[str, Any]]:
        sheet = self.layout["sheet"]
        width, height = float(sheet["width"]), float(sheet["height"])
        layer_order = {item["id"]: item["order"] for item in self.layout["layers"]}
        defs_parts = [
            '<marker id="dimension-arrow" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto-start-reverse" markerUnits="strokeWidth"><path d="M 6 0 L 0 3 L 6 6" fill="none" stroke="context-stroke"/></marker>'
        ]
        entities_by_layer: dict[str, list[tuple[int, str]]] = {}
        entity_scene: list[dict[str, Any]] = []
        for key, binding in sorted(self.bindings.items(), key=lambda item: (layer_order.get(item[1].placement.get("layer", "symbols"), 0), item[1].placement.get("zIndex", 0), item[0])):
            defs, svg = self._render_entity(key, binding)
            defs_parts.append(defs)
            layer = binding.placement.get("layer", "symbols")
            entities_by_layer.setdefault(layer, []).append((binding.placement.get("zIndex", 0), svg))
            entity_scene.append({
                "key": key,
                "kind": binding.source["kind"],
                "componentType": binding.component["id"],
                "reference": binding.fields.get("reference", key),
                "value": binding.fields.get("value", ""),
                "symbolId": binding.asset.data["symbol"]["id"],
                "symbolDigest": binding.asset.digest,
                "variant": binding.variant["id"] if binding.variant else None,
                "parameters": binding.parameters,
                "placement": binding.placement,
                "ports": {name: [round(point[0],6), round(point[1],6)] for name, point in sorted(binding.port_positions.items())},
            })

        sheet_ports_by_layer: dict[str, list[str]] = {}
        interface_scene: list[dict[str, Any]] = []
        for port_id, item in sorted(self.sheet_port_presentations.items()):
            layer = item.get("layer", "connections")
            sheet_ports_by_layer.setdefault(layer, []).append(self._render_sheet_port(port_id, item))
            semantic_port = self.semantic["ports"][port_id]
            point = self.sheet_port_positions[port_id]
            interface_scene.append({
                "id": port_id,
                "direction": semantic_port["direction"],
                "role": semantic_port["role"],
                "label": item.get("label", semantic_port.get("label", port_id)),
                "localNet": self.semantic.get("endpointOwners", {}).get(f"@{port_id}"),
                "position": [round(point[0], 6), round(point[1], 6)],
                "side": item.get("side", "right"),
                "layer": layer,
            })

        connections_by_layer: dict[str, list[str]] = {}
        net_scene: list[dict[str, Any]] = []
        for connection in sorted(self.layout.get("connections", []), key=lambda item: item["net"]):
            net = connection["net"]
            layer = connection.get("layer", "connections")
            style = self._layout_style_attrs(connection.get("style"), {"stroke":"#2458a6","strokeWidth":1.5,"fill":"none","strokeLinecap":"round","strokeLinejoin":"round"})
            paths_svg: list[str] = []
            scene_paths: list[list[list[float]]] = []
            for route_index, route in enumerate(connection["paths"]):
                points = [self._resolve_route_end(route["from"])] + [(float(p[0]),float(p[1])) for p in route.get("via", [])] + [self._resolve_route_end(route["to"])]
                point_attr = " ".join(f"{fmt(x)},{fmt(y)}" for x,y in points)
                route_style = self._layout_style_attrs(route.get("style"), {}) if route.get("style") else ""
                attrs = style + (" " + route_style if route_style else "")
                paths_svg.append(f'<polyline data-net="{xml(net)}" data-route="{route_index}" class="net-route" points="{point_attr}" {attrs}/>' )
                scene_paths.append([[round(x,6),round(y,6)] for x,y in points])
            junctions = "".join(f'<circle data-net="{xml(net)}" class="net-junction" cx="{fmt(p[0])}" cy="{fmt(p[1])}" r="2.2" fill="#2458a6"/>' for p in connection.get("junctions", []))
            labels = "".join(f'<text data-net="{xml(net)}" class="net-label" x="{fmt(item["x"])}" y="{fmt(item["y"])}" transform="rotate({fmt(item.get("rotation",0))} {fmt(item["x"])} {fmt(item["y"])})">{xml(item["text"])}</text>' for item in connection.get("labels", []))
            connections_by_layer.setdefault(layer, []).append(f'<g data-net-group="{xml(net)}" class="net"><title>Net {xml(net)}</title>{"".join(paths_svg)}{junctions}{labels}</g>')
            net_scene.append({"name": net, "endpoints": self.semantic["nets"][net], "paths": scene_paths, "junctions": connection.get("junctions", [])})

        annotations_by_layer: dict[str, list[str]] = {}
        for annotation in self.layout.get("annotations", []):
            layer = annotation.get("layer", "annotation")
            style = self._layout_style_attrs(annotation.get("style"), {"stroke":"#44505c","strokeWidth":1,"fill":"none","fontFamily":"Arial, sans-serif","fontSize":11})
            if annotation["type"] == "text":
                anchor = annotation.get("anchor", "start")
                angle = annotation.get("rotation", 0)
                svg = f'<text data-annotation="{xml(annotation["id"])}" x="{fmt(annotation["x"])}" y="{fmt(annotation["y"])}" text-anchor="{anchor}" transform="rotate({fmt(angle)} {fmt(annotation["x"])} {fmt(annotation["y"])})" {style}>{xml(annotation["text"])}</text>'
            elif annotation["type"] == "polyline":
                pts = " ".join(f"{fmt(p[0])},{fmt(p[1])}" for p in annotation["points"])
                tag = "polygon" if annotation.get("closed") else "polyline"
                svg = f'<{tag} data-annotation="{xml(annotation["id"])}" points="{pts}" {style}/>'
            else:
                svg = self._dimension_svg(tuple(annotation["from"]), tuple(annotation["to"]), float(annotation["offset"]), annotation.get("text"), annotation.get("unit", ""), int(annotation.get("precision",0)), style)
            annotations_by_layer.setdefault(layer, []).append(svg)

        layer_groups: list[str] = []
        for layer in sorted(self.layout["layers"], key=lambda item: (item["order"], item["id"])):
            layer_id = layer["id"]
            content = []
            content.extend(svg for _z, svg in sorted(entities_by_layer.get(layer_id, []), key=lambda item:item[0]))
            content.extend(sheet_ports_by_layer.get(layer_id, []))
            content.extend(connections_by_layer.get(layer_id, []))
            content.extend(annotations_by_layer.get(layer_id, []))
            visibility = "" if layer.get("defaultVisible", True) else ' style="display:none"'
            layer_groups.append(f'<g id="layer-{xml(layer_id)}" data-layer="{xml(layer_id)}" data-purpose="{xml(layer["purpose"])}"{visibility}>{"".join(content)}</g>')

        title = self.project["title"]
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" role="img" '
            f'viewBox="0 0 {fmt(width)} {fmt(height)}" width="{fmt(width)}" height="{fmt(height)}" '
            f'aria-labelledby="aixem-title aixem-desc" data-project="{xml(self.project["id"])}">'
            f'<title id="aixem-title">{xml(title)}</title><desc id="aixem-desc">AIXEM deterministic symbol-graphics rendering. Connectivity follows the semantic source, not geometry.</desc>'
            f'<defs>{"".join(defs_parts)}</defs>'
            f'<rect class="sheet-background" x="0" y="0" width="{fmt(width)}" height="{fmt(height)}" fill="#ffffff" stroke="#cbd3dc" stroke-width="1"/>'
            f'{"".join(layer_groups)}</svg>'
        )
        scene = {
            "schema": "https://schemas.aixem.org/component-graphics/resolved-scene/1",
            "renderer": {"id": RENDERER_ID, "version": RENDERER_VERSION},
            "generatedAt": FIXED_TIME,
            "project": {"id": self.project["id"], "title": title, "profile": self.project["applicationProfile"]},
            "hashes": {
                "source": sha256_file(self.source_path), "layout": sha256_file(self.layout_path),
                "libraries": [sha256_file(path) for path,_ in self.libraries],
                "symbolAssets": sorted(asset.digest for asset in self.assets.values()),
            },
            "coordinateSystem": self.layout["coordinateSystem"],
            "sheet": self.layout["sheet"],
            "layers": self.layout["layers"],
            "entities": entity_scene,
            "nets": net_scene,
            "diagnostics": self.diagnostics,
            "featuresUsed": sorted(self.feature_usage),
            "statistics": {"entities": len(entity_scene), "nets": len(net_scene), "symbolAssets": len(self.assets), "primitives": self.primitive_count},
        }
        if interface_scene:
            scene["interfacePorts"] = interface_scene
            scene["statistics"]["interfacePorts"] = len(interface_scene)
        return svg, scene

    def build_viewer(self, svg: str, scene: dict[str, Any]) -> str:
        """Legacy internal compatibility helper.

        This is not Reference Viewer Contract 1. The production AIXEM 0.5.4+
        path is render_project.py through implementation/schematic/viewer/.
        Keep this helper only for historical direct-render compatibility.
        """
        entity_items = "".join(
            f'<button type="button" class="list-item entity-item" data-select-entity="{xml(item["key"])}"><b>{xml(item["reference"])}</b><span>{xml(item["componentType"])}</span></button>'
            for item in scene["entities"]
        )
        net_items = "".join(
            f'<button type="button" class="list-item net-item" data-select-net="{xml(item["name"])}"><b>{xml(item["name"])}</b><span>{len(item["endpoints"])} endpoints</span></button>'
            for item in scene["nets"]
        )
        layer_items = "".join(
            f'<label class="layer-item"><input type="checkbox" data-toggle-layer="{xml(item["id"])}" {"checked" if item.get("defaultVisible",True) else ""}><span>{xml(item["id"])}</span><small>{xml(item["purpose"])}</small></label>'
            for item in sorted(scene["layers"], key=lambda x:(x["order"],x["id"]))
        )
        scene_json = json.dumps(scene, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
        return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{xml(self.project["title"])} — AIXEM Viewer</title>
<meta name="aixem-document-id" content="AIXEM-EXAMPLE-{xml(self.project["id"].upper().replace('.', '-'))}">
<meta name="aixem-release" content="AIXEM-IB-0.3-2026-08-10"><meta name="aixem-baseline" content="AIXEM-WD-0.4-2026-08-10"><meta name="aixem-revision" content="1.0"><meta name="aixem-language" content="Korean primary">
<style>
:root{{--bg:#eef1f4;--panel:#ffffff;--ink:#17212b;--muted:#687481;--line:#d7dde4;--accent:#2458a6;--accent-soft:#eaf1fb;--danger:#b12d2d}}*{{box-sizing:border-box}}html,body{{margin:0;min-height:100%;font-family:Inter,Arial,sans-serif;color:var(--ink);background:var(--bg)}}button,input{{font:inherit}}.skip{{position:absolute;left:-9999px}}.skip:focus{{left:12px;top:12px;z-index:9;background:#fff;padding:8px}}header{{height:68px;background:#101820;color:white;display:flex;align-items:center;justify-content:space-between;padding:0 22px;gap:20px}}header h1{{margin:0;font-size:18px;font-weight:650}}header p{{margin:4px 0 0;color:#bdc7d1;font-size:12px}}.badge{{border:1px solid #40505f;padding:6px 9px;font-size:11px;letter-spacing:.08em;text-transform:uppercase}}main{{height:calc(100vh - 68px);display:grid;grid-template-columns:310px minmax(0,1fr)}}aside{{background:var(--panel);border-right:1px solid var(--line);overflow:auto;padding:16px}}.section{{margin-bottom:20px}}.section h2{{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 9px}}.list{{display:grid;gap:5px}}.list-item{{border:1px solid transparent;background:#f7f8fa;text-align:left;padding:8px 9px;display:grid;gap:2px;cursor:pointer}}.list-item:hover,.list-item.active{{border-color:var(--accent);background:var(--accent-soft)}}.list-item b{{font-size:12px}}.list-item span{{font-size:10px;color:var(--muted);overflow:hidden;text-overflow:ellipsis}}.layer-item{{display:grid;grid-template-columns:20px 1fr;gap:0 7px;align-items:center;padding:6px 3px;font-size:12px}}.layer-item small{{grid-column:2;color:var(--muted)}}.stage{{position:relative;overflow:hidden}}.toolbar{{position:absolute;z-index:3;left:16px;top:16px;display:flex;gap:6px;padding:6px;background:#fff;border:1px solid var(--line);box-shadow:0 6px 20px #1b28351a}}.toolbar button{{border:1px solid var(--line);background:#fff;min-width:34px;height:32px;cursor:pointer}}.toolbar button:hover{{border-color:var(--accent)}}#viewport{{width:100%;height:100%;overflow:hidden;background:#dfe4e9;cursor:grab}}#viewport.dragging{{cursor:grabbing}}#canvas{{width:100%;height:100%;transform-origin:0 0;user-select:none}}#canvas svg{{width:100%;height:100%;display:block;background:white}}.entity,.net-route,.net-junction{{transition:opacity .12s,filter .12s,stroke-width .12s}}svg.has-selection .entity:not(.selected),svg.has-selection .net:not(.selected){{opacity:.18}}.entity.selected{{filter:drop-shadow(0 0 4px #ff9f1c)}}.entity.selected>*:not(title){{stroke:#d86e00!important}}.net.selected{{opacity:1!important}}.net.selected .net-route{{stroke:#d64242!important;stroke-width:3.5!important}}.net.selected .net-junction{{fill:#d64242!important}}.entity:focus{{outline:none;filter:drop-shadow(0 0 5px #2458a6)}}.net-label{{font:600 7px Arial,sans-serif;fill:#2458a6;stroke:none}}.dimension text{{font:10px Arial,sans-serif;fill:#394552;stroke:none}}.status{{position:absolute;right:16px;bottom:16px;background:#101820e8;color:#fff;padding:8px 10px;font-size:11px;max-width:50%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}@media(max-width:800px){{header{{height:auto;min-height:64px;padding:12px 14px}}main{{height:calc(100vh - 72px);grid-template-columns:1fr}}aside{{display:none}}.toolbar{{left:8px;top:8px}}.status{{right:8px;bottom:8px;max-width:80%}}}}
</style></head><body><a class="skip" href="#main">Skip to main content</a><header><div><h1>{xml(self.project["title"])}</h1><p>{xml(self.project["applicationProfile"])} · geometry is derived, semantics remain in source/library</p></div><span class="badge">AIXEM IB 0.3</span></header><main id="main"><aside aria-label="Project explorer"><section class="section"><h2>Layers</h2>{layer_items}</section><section class="section"><h2>Entities</h2><div class="list">{entity_items}</div></section><section class="section"><h2>Nets / Relations</h2><div class="list">{net_items}</div></section></aside><section class="stage" aria-label="Drawing viewport"><div class="toolbar"><button id="fit" title="Fit">Fit</button><button id="zin" title="Zoom in">+</button><button id="zout" title="Zoom out">−</button><button id="clear" title="Clear selection">×</button></div><div id="viewport"><div id="canvas">{svg}</div></div><div id="status" class="status">Ready · {len(scene["entities"])} entities · {len(scene["nets"])} nets</div></section></main><script type="application/json" id="scene-data">{scene_json}</script><script>
(()=>{{const viewport=document.getElementById('viewport'),canvas=document.getElementById('canvas'),svg=canvas.querySelector('svg'),status=document.getElementById('status');let scale=1,tx=0,ty=0,drag=false,lastX=0,lastY=0;function apply(){{canvas.style.transform=`translate(${{tx}}px,${{ty}}px) scale(${{scale}})`}}function fit(){{scale=1;tx=0;ty=0;apply()}}function clear(){{svg.classList.remove('has-selection');svg.querySelectorAll('.selected').forEach(x=>x.classList.remove('selected'));document.querySelectorAll('.list-item.active').forEach(x=>x.classList.remove('active'));status.textContent='Ready · {len(scene["entities"])} entities · {len(scene["nets"])} nets'}}function selectEntity(key){{clear();svg.classList.add('has-selection');const target=svg.querySelector(`[data-entity="${{CSS.escape(key)}}"]`);if(target)target.classList.add('selected');document.querySelector(`[data-select-entity="${{CSS.escape(key)}}"]`)?.classList.add('active');status.textContent='Entity · '+key}}function selectNet(key){{clear();svg.classList.add('has-selection');svg.querySelector(`[data-net-group="${{CSS.escape(key)}}"]`)?.classList.add('selected');document.querySelector(`[data-select-net="${{CSS.escape(key)}}"]`)?.classList.add('active');status.textContent='Net · '+key}}document.querySelectorAll('[data-select-entity]').forEach(b=>b.addEventListener('click',()=>selectEntity(b.dataset.selectEntity)));document.querySelectorAll('[data-select-net]').forEach(b=>b.addEventListener('click',()=>selectNet(b.dataset.selectNet)));svg.querySelectorAll('[data-entity]').forEach(g=>{{g.addEventListener('click',e=>{{e.stopPropagation();selectEntity(g.dataset.entity)}});g.addEventListener('keydown',e=>{{if(e.key==='Enter'||e.key===' ')selectEntity(g.dataset.entity)}})}});svg.querySelectorAll('[data-net-group]').forEach(g=>g.addEventListener('click',e=>{{e.stopPropagation();selectNet(g.dataset.netGroup)}}));svg.addEventListener('click',clear);document.querySelectorAll('[data-toggle-layer]').forEach(i=>i.addEventListener('change',()=>{{const g=svg.querySelector(`[data-layer="${{CSS.escape(i.dataset.toggleLayer)}}"]`);if(g)g.style.display=i.checked?'':'none'}}));document.getElementById('fit').onclick=fit;document.getElementById('zin').onclick=()=>{{scale=Math.min(6,scale*1.2);apply()}};document.getElementById('zout').onclick=()=>{{scale=Math.max(.2,scale/1.2);apply()}};document.getElementById('clear').onclick=clear;viewport.addEventListener('wheel',e=>{{e.preventDefault();const next=Math.max(.2,Math.min(6,scale*(e.deltaY<0?1.1:.9)));scale=next;apply()}},{{passive:false}});viewport.addEventListener('pointerdown',e=>{{drag=true;lastX=e.clientX;lastY=e.clientY;viewport.setPointerCapture(e.pointerId);viewport.classList.add('dragging')}});viewport.addEventListener('pointermove',e=>{{if(!drag)return;tx+=e.clientX-lastX;ty+=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;apply()}});viewport.addEventListener('pointerup',()=>{{drag=false;viewport.classList.remove('dragging')}});fit()}})();
</script></body></html>'''

    def render(self, output_dir: pathlib.Path) -> dict[str, Any]:
        output_dir.mkdir(parents=True, exist_ok=True)
        svg, scene = self.build_svg()
        svg_path = output_dir / "drawing.svg"
        scene_path = output_dir / "resolved-scene.json"
        viewer_path = output_dir / "viewer.html"
        svg_path.write_text(svg + "\n", encoding="utf-8", newline="\n")
        scene_path.write_text(pretty_json(scene), encoding="utf-8", newline="\n")
        viewer_path.write_text(self.build_viewer(svg, scene) + "\n", encoding="utf-8", newline="\n")
        artifacts = [
            {"role":"drawing-svg","path":svg_path.name,"mediaType":"image/svg+xml","digest":sha256_file(svg_path),"bytes":svg_path.stat().st_size},
            {"role":"resolved-scene","path":scene_path.name,"mediaType":"application/json","digest":sha256_file(scene_path),"bytes":scene_path.stat().st_size},
            {"role":"standalone-viewer","path":viewer_path.name,"mediaType":"text/html","digest":sha256_file(viewer_path),"bytes":viewer_path.stat().st_size},
        ]
        render_manifest = {
            "schema":"https://schemas.aixem.org/component-graphics/render-manifest/1",
            "renderer":{"id":RENDERER_ID,"version":RENDERER_VERSION},
            "generatedAt":FIXED_TIME,
            "project":{"id":self.project["id"],"manifestDigest":sha256_file(self.project_file),"sourceDigest":sha256_file(self.source_path),"layoutDigest":sha256_file(self.layout_path)},
            "artifacts":artifacts,
            "status":"pass",
        }
        manifest_path = output_dir / "render-manifest.json"
        manifest_path.write_text(pretty_json(render_manifest), encoding="utf-8", newline="\n")
        validation = {
            "schema":"https://schemas.aixem.org/component-graphics/project-validation/1",
            "project":self.project["id"],
            "generatedAt":FIXED_TIME,
            "valid":True,
            "checks":{
                "projectSchema":True,"layoutSchema":True,"librarySchemas":len(self.libraries),"symbolSchemas":len(self.assets),
                "inputDigests":2+len(self.libraries)+len(self.assets),"componentTypeClosure":True,"semanticPortClosure":True,
                "presentationPortMapClosure":True,"placementClosure":True,"semanticNetClosure":True,"routeEndpointClosure":True,
                "remoteAssetsDenied":self.project["renderPolicy"]["remoteAssets"]=="deny",
            },
            "statistics":scene["statistics"],
            "featuresUsed":scene["featuresUsed"],
            "hashes":render_manifest["project"] | {item["role"]:item["digest"] for item in artifacts},
            "diagnostics":self.diagnostics,
        }
        return {"validation":validation,"renderManifest":render_manifest,"scene":scene,"artifacts":artifacts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=pathlib.Path)
    parser.add_argument("--output-dir", type=pathlib.Path)
    parser.add_argument("--schema-root", type=pathlib.Path)
    parser.add_argument("--validation-out", type=pathlib.Path)
    args = parser.parse_args()
    project_file = args.project.resolve()
    default_schema = pathlib.Path(__file__).resolve().parents[2] / "specification-candidates" / "schemas"
    output = args.output_dir.resolve() if args.output_dir else project_file.parent / "render"
    validation_out = args.validation_out.resolve() if args.validation_out else project_file.parent / "evidence" / "project-validation.json"
    try:
        renderer = ProjectRenderer(project_file, args.schema_root or default_schema)
        result = renderer.render(output)
        validation_out.parent.mkdir(parents=True, exist_ok=True)
        validation_out.write_text(pretty_json(result["validation"]), encoding="utf-8", newline="\n")
        print(f"project: {renderer.project['id']}")
        print(f"entities: {result['scene']['statistics']['entities']}; nets: {result['scene']['statistics']['nets']}; symbols: {result['scene']['statistics']['symbolAssets']}")
        print(f"viewer: {output / 'viewer.html'}")
        print("validation: PASS")
        return 0
    except AixemGraphicsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
