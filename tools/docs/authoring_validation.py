#!/usr/bin/env python3
"""Validation helpers for AIXEM 0.5.1 executable authoring documentation."""
from __future__ import annotations

import json
import math
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = ROOT / "docs" / "specifications" / "schemas" / "component-graphics-1"
AUTHORING = ROOT / "examples" / "authoring"
IMPLEMENTATION = ROOT / "implementation" / "schematic"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from component_core import ProjectRenderer, eval_numeric, load_json, sha256_file  # noqa: E402
from render_project import GridProjectRenderer  # noqa: E402

SYMBOL_SCHEMA = SCHEMA_ROOT / "aixem-symbol-asset-1.schema.json"
LIBRARY_SCHEMA = SCHEMA_ROOT / "aixem-component-library-1.schema.json"
LAYOUT_SCHEMA = SCHEMA_ROOT / "aixem-explicit-layout-1.schema.json"
PROJECT_SCHEMA = SCHEMA_ROOT / "aixem-project-manifest-1.schema.json"
STYLE_PROFILE = ROOT / "profiles" / "aixem-grid-schematic-style-1.aixstyle.json"
SNIPPET_RE = re.compile(
    r"<!--\s*aixem-snippet:\s*([^\s#>]+)(#[^\s>]*)?\s*-->\s*"
    r"```json\s*(.*?)\s*```\s*<!--\s*/aixem-snippet\s*-->",
    re.DOTALL,
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str
    severity: str = "error"

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message, "severity": self.severity}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_json(path: Path, schema_path: Path) -> list[ValidationIssue]:
    data = read_json(path)
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    issues: list[ValidationIssue] = []
    for item in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        location = "/" + "/".join(str(part) for part in item.absolute_path)
        issues.append(ValidationIssue("schema", path.relative_to(ROOT).as_posix() + location, item.message))
    return issues


def json_pointer(value: Any, pointer: str | None) -> Any:
    if not pointer or pointer == "#":
        return value
    raw = pointer[1:] if pointer.startswith("#") else pointer
    if raw == "":
        return value
    if not raw.startswith("/"):
        raise ValueError(f"JSON Pointer must begin with '/': {pointer}")
    current = value
    for token in raw[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(token)]
        else:
            current = current[token]
    return current


def validate_snippet_blocks(paths: Iterable[Path] | None = None) -> dict[str, Any]:
    docs = list(paths) if paths is not None else sorted((ROOT / "docs").rglob("*.md"))
    issues: list[ValidationIssue] = []
    snippets = 0
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for match in SNIPPET_RE.finditer(text):
            snippets += 1
            rel_source, pointer, literal = match.groups()
            source = (ROOT / rel_source).resolve()
            try:
                source.relative_to(ROOT.resolve())
            except ValueError:
                issues.append(ValidationIssue("snippet-path", doc.relative_to(ROOT).as_posix(), f"Snippet source escapes repository: {rel_source}"))
                continue
            if not source.is_file():
                issues.append(ValidationIssue("snippet-missing", doc.relative_to(ROOT).as_posix(), f"Snippet source is missing: {rel_source}"))
                continue
            try:
                expected = json_pointer(read_json(source), pointer)
                observed = json.loads(literal)
            except Exception as exc:  # noqa: BLE001
                issues.append(ValidationIssue("snippet-parse", doc.relative_to(ROOT).as_posix(), f"Cannot resolve snippet {rel_source}{pointer or ''}: {exc}"))
                continue
            if observed != expected:
                issues.append(ValidationIssue("snippet-drift", doc.relative_to(ROOT).as_posix(), f"Snippet differs from {rel_source}{pointer or ''}"))
    return {"valid": not issues, "documents": len(docs), "snippets": snippets, "issues": [x.to_dict() for x in issues]}


def schema_inventory() -> dict[str, list[str]]:
    symbol = read_json(SYMBOL_SCHEMA)
    library = read_json(LIBRARY_SCHEMA)
    layout = read_json(LAYOUT_SCHEMA)
    symbol_obj = symbol["properties"]["symbol"]
    component = library["$defs"]["component"]
    presentation = component["properties"]["presentations"]["items"]
    placement = layout["properties"]["layout"]["properties"]["placements"]["items"]
    connection = layout["properties"]["layout"]["properties"]["connections"]["items"]
    path = connection["properties"]["paths"]["items"]
    primitive_types: list[str] = []
    primitive_properties: set[str] = set()
    for option in symbol["$defs"]["node"]["oneOf"]:
        primitive_types.append(option["properties"]["type"]["const"])
        primitive_properties.update(option["properties"])
    return {
        "symbolTopLevel": sorted(symbol_obj["properties"]),
        "symbolPort": sorted(symbol["$defs"]["port"]["properties"]),
        "symbolParameter": sorted(symbol["$defs"]["parameterDefinition"]["properties"]),
        "symbolVariant": sorted(symbol["$defs"]["variant"]["properties"]),
        "primitiveTypes": sorted(primitive_types),
        "primitiveProperties": sorted(primitive_properties),
        "component": sorted(component["properties"]),
        "presentation": sorted(presentation["properties"]),
        "placement": sorted(placement["properties"]),
        "connection": sorted(connection["properties"]),
        "connectionPath": sorted(path["properties"]),
    }


COVERAGE_DOCS = {
    "symbolTopLevel": ROOT / "docs" / "symbols" / "aixsym-field-reference.md",
    "symbolPort": ROOT / "docs" / "symbols" / "pins-and-ports.md",
    "symbolParameter": ROOT / "docs" / "symbols" / "aixsym-field-reference.md",
    "symbolVariant": ROOT / "docs" / "symbols" / "variants.md",
    "primitiveTypes": ROOT / "docs" / "symbols" / "primitives.md",
    "primitiveProperties": ROOT / "docs" / "symbols" / "primitives.md",
    "component": ROOT / "docs" / "symbols" / "component-symbol-binding.md",
    "presentation": ROOT / "docs" / "symbols" / "component-symbol-binding.md",
    "placement": ROOT / "docs" / "file-formats" / "aixlayout.md",
    "connection": ROOT / "docs" / "file-formats" / "aixlayout.md",
    "connectionPath": ROOT / "docs" / "file-formats" / "aixlayout.md",
}


def validate_reference_coverage() -> dict[str, Any]:
    inventory = schema_inventory()
    issues: list[ValidationIssue] = []
    covered = 0
    total = 0
    by_group: dict[str, Any] = {}
    for group, fields in inventory.items():
        path = COVERAGE_DOCS[group]
        total += len(fields)
        if not path.is_file():
            issues.append(ValidationIssue("reference-missing", path.relative_to(ROOT).as_posix(), f"Coverage owner for {group} is missing"))
            by_group[group] = {"total": len(fields), "covered": 0, "missing": fields}
            continue
        text = path.read_text(encoding="utf-8")
        missing = [field for field in fields if f"`{field}`" not in text]
        group_covered = len(fields) - len(missing)
        covered += group_covered
        by_group[group] = {"total": len(fields), "covered": group_covered, "missing": missing, "document": path.relative_to(ROOT).as_posix()}
        for field in missing:
            issues.append(ValidationIssue("reference-gap", path.relative_to(ROOT).as_posix(), f"{group} field/type `{field}` is not documented"))
    return {"valid": not issues, "total": total, "covered": covered, "coverage": 1.0 if total == 0 else covered / total, "groups": by_group, "issues": [x.to_dict() for x in issues]}


def _defaults(symbol: dict[str, Any]) -> dict[str, Any]:
    return {name: definition["default"] for name, definition in symbol.get("parameters", {}).items()}


def _walk_nodes(nodes: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    for node in nodes:
        yield node
        if node.get("type") == "group":
            yield from _walk_nodes(node.get("children", []))


def _close(a: tuple[float, float], b: tuple[float, float], tolerance: float = 1e-6) -> bool:
    return math.isclose(a[0], b[0], abs_tol=tolerance) and math.isclose(a[1], b[1], abs_tol=tolerance)


def _on_grid(value: float, grid: float, tolerance: float = 1e-6) -> bool:
    return abs(value / grid - round(value / grid)) <= tolerance


def lint_symbol(path: Path, *, profile_snap: float = 2.5) -> dict[str, Any]:
    issues = validate_json(path, SYMBOL_SCHEMA)
    if issues:
        return {"valid": False, "path": path.relative_to(ROOT).as_posix(), "checks": 1, "issues": [x.to_dict() for x in issues]}
    doc = read_json(path)
    symbol = doc["symbol"]
    parameters = _defaults(symbol)
    ports: dict[str, tuple[float, float]] = {}
    checks = 0
    for port in symbol["ports"]:
        try:
            point = (eval_numeric(port["x"], parameters), eval_numeric(port["y"], parameters))
        except Exception as exc:  # noqa: BLE001
            issues.append(ValidationIssue("port-expression", path.relative_to(ROOT).as_posix(), f"Port {port['id']} cannot resolve: {exc}"))
            continue
        ports[port["id"]] = point
        checks += 2
        if not _on_grid(point[0], profile_snap) or not _on_grid(point[1], profile_snap):
            issues.append(ValidationIssue("symbol-grid", path.relative_to(ROOT).as_posix(), f"Port {port['id']} at {point} is off the {profile_snap:g} mm authoring grid"))
        orientation = eval_numeric(port["orientation"], parameters) % 360
        if orientation not in {0, 90, 180, 270}:
            issues.append(ValidationIssue("port-orientation", path.relative_to(ROOT).as_posix(), f"Port {port['id']} orientation {orientation:g} is not orthogonal"))

    leads: dict[str, tuple[float, float]] = {}
    all_graphics = list(symbol.get("graphics", []))
    for variant in symbol.get("variants", []):
        all_graphics.extend(variant.get("graphics", []))
    for node in _walk_nodes(all_graphics):
        if node.get("role") != "pin-lead":
            continue
        metadata = node.get("metadata", {})
        port_id = str(metadata.get("port", ""))
        endpoint = metadata.get("portEndpoint")
        checks += 1
        if node.get("type") != "line" or endpoint not in {"start", "end"} or not port_id:
            issues.append(ValidationIssue("lead-metadata", path.relative_to(ROOT).as_posix(), f"Pin lead {node.get('id', '<unnamed>')} must be a line with metadata.port and metadata.portEndpoint"))
            continue
        key = ("x1", "y1") if endpoint == "start" else ("x2", "y2")
        point = (eval_numeric(node[key[0]], parameters), eval_numeric(node[key[1]], parameters))
        leads[port_id] = point
    for port_id, point in ports.items():
        checks += 1
        if port_id not in leads:
            issues.append(ValidationIssue("lead-missing", path.relative_to(ROOT).as_posix(), f"Port {port_id} has no machine-associated visible pin lead", "warning"))
        elif not _close(point, leads[port_id]):
            issues.append(ValidationIssue("lead-port-mismatch", path.relative_to(ROOT).as_posix(), f"Port {port_id} is at {point}, but its visible lead ends at {leads[port_id]}"))

    recipe = symbol.get("metadata", {}).get("recipe")
    if recipe in {"connector", "multi-pin-ic"}:
        pitch = float(symbol.get("metadata", {}).get("pinPitch", 5))
        side_groups: dict[int, list[float]] = {0: [], 90: [], 180: [], 270: []}
        for port in symbol["ports"]:
            orientation = int(eval_numeric(port["orientation"], parameters)) % 360
            x, y = ports[port["id"]]
            side_groups[orientation].append(y if orientation in {0, 180} else x)
        for orientation, values in side_groups.items():
            unique = sorted(set(values))
            for a, b in zip(unique, unique[1:]):
                checks += 1
                if not _on_grid(b - a, pitch):
                    issues.append(ValidationIssue("pin-pitch", path.relative_to(ROOT).as_posix(), f"Ports on orientation {orientation} use pitch {b-a:g}, expected a multiple of {pitch:g} mm"))

    # A minimal field/body collision check for rectangular bodies and bound text anchors.
    rects = [node for node in _walk_nodes(all_graphics) if node.get("role") == "body" and node.get("type") == "rect"]
    fields = [node for node in _walk_nodes(all_graphics) if node.get("type") == "text" and node.get("field") in {"reference", "value"}]
    for rect in rects:
        try:
            rx = eval_numeric(rect["x"], parameters); ry = eval_numeric(rect["y"], parameters)
            rw = eval_numeric(rect["width"], parameters); rh = eval_numeric(rect["height"], parameters)
        except Exception:  # variant-specific expression may require a local context; renderer tests cover it.
            continue
        for field in fields:
            fx = eval_numeric(field["x"], parameters); fy = eval_numeric(field["y"], parameters)
            checks += 1
            if rx <= fx <= rx + rw and ry <= fy <= ry + rh:
                issues.append(ValidationIssue("field-body-overlap", path.relative_to(ROOT).as_posix(), f"Field {field['field']} anchor ({fx:g},{fy:g}) lies inside body {rect.get('id', '<body>')}"))

    errors = [issue for issue in issues if issue.severity == "error"]
    return {"valid": not errors, "path": path.relative_to(ROOT).as_posix(), "checks": checks, "issues": [x.to_dict() for x in issues]}


def validate_library_bindings(path: Path, project_root: Path) -> dict[str, Any]:
    issues = validate_json(path, LIBRARY_SCHEMA)
    checks = 1
    if issues:
        return {"valid": False, "path": path.relative_to(ROOT).as_posix(), "checks": checks, "issues": [x.to_dict() for x in issues]}
    data = read_json(path)["library"]
    for component in data["components"]:
        semantic = {port["id"] for port in component["ports"]}
        properties = {item["id"] for item in component["properties"]}
        for presentation in component["presentations"]:
            checks += 4
            mapped = set(presentation["portMap"])
            if mapped != semantic:
                issues.append(ValidationIssue("portmap-total", path.relative_to(ROOT).as_posix(), f"{component['id']} portMap keys {sorted(mapped)} do not equal semantic ports {sorted(semantic)}"))
            symbol_path = project_root / presentation["asset"]["path"]
            if not symbol_path.is_file():
                issues.append(ValidationIssue("asset-missing", path.relative_to(ROOT).as_posix(), f"Missing asset {presentation['asset']['path']}"))
                continue
            symbol = read_json(symbol_path)["symbol"]
            symbol_ports = {port["id"] for port in symbol["ports"]}
            unknown_targets = sorted(set(presentation["portMap"].values()) - symbol_ports)
            if unknown_targets:
                issues.append(ValidationIssue("portmap-target", path.relative_to(ROOT).as_posix(), f"{component['id']} maps to unknown symbol ports {unknown_targets}"))
            if presentation["asset"]["digest"] != sha256_file(symbol_path):
                issues.append(ValidationIssue("asset-digest", path.relative_to(ROOT).as_posix(), f"{component['id']} symbol digest does not match"))
            unknown_fields = sorted(set(presentation.get("fieldMap", {}).values()) - properties)
            if unknown_fields:
                issues.append(ValidationIssue("fieldmap-source", path.relative_to(ROOT).as_posix(), f"{component['id']} fieldMap references undefined component properties {unknown_fields}"))
    return {"valid": not [x for x in issues if x.severity == "error"], "path": path.relative_to(ROOT).as_posix(), "checks": checks, "issues": [x.to_dict() for x in issues]}


def validate_authoring_example(root: Path, *, check_determinism: bool = True) -> dict[str, Any]:
    issues: list[ValidationIssue] = []
    checks = 0
    project = root / "project.aixproj.json"
    issues.extend(validate_json(project, PROJECT_SCHEMA)); checks += 1
    layout = next(root.glob("*.aixlayout.json"))
    issues.extend(validate_json(layout, LAYOUT_SCHEMA)); checks += 1
    for library in sorted((root / "library").rglob("*.aixlib.json")):
        result = validate_library_bindings(library, root)
        checks += result["checks"]
        issues.extend(ValidationIssue(**item) for item in result["issues"])
    for symbol in sorted((root / "library").rglob("*.aixsym.json")):
        result = lint_symbol(symbol)
        checks += result["checks"]
        issues.extend(ValidationIssue(**item) for item in result["issues"])
    if [x for x in issues if x.severity == "error"]:
        return {"valid": False, "id": root.name, "checks": checks, "issues": [x.to_dict() for x in issues]}
    try:
        renderer = GridProjectRenderer(project, SCHEMA_ROOT, STYLE_PROFILE)
        with tempfile.TemporaryDirectory(prefix="aixem-authoring-render-") as temp:
            out = Path(temp)
            renderer.render(out)
            checks += 1
            if check_determinism:
                expected = root / "render"
                for name in ("drawing.svg", "resolved-scene.json", "viewer-model.json", "render-manifest.json", "viewer.html", "workbench.html"):
                    checks += 1
                    if not (expected / name).is_file():
                        issues.append(ValidationIssue("render-missing", root.relative_to(ROOT).as_posix(), f"Missing committed render artifact {name}"))
                    elif sha256_file(expected / name) != sha256_file(out / name):
                        issues.append(ValidationIssue("render-drift", root.relative_to(ROOT).as_posix(), f"Rendered {name} differs from committed golden output"))
    except Exception as exc:  # noqa: BLE001
        issues.append(ValidationIssue("render", root.relative_to(ROOT).as_posix(), str(exc)))
    return {"valid": not [x for x in issues if x.severity == "error"], "id": root.name, "checks": checks, "issues": [x.to_dict() for x in issues]}


def validate_all_authoring_examples(*, check_determinism: bool = True) -> dict[str, Any]:
    roots = sorted(path for path in AUTHORING.glob("[0-9][0-9]-*") if (path / "project.aixproj.json").is_file())
    results = [validate_authoring_example(root, check_determinism=check_determinism) for root in roots]
    broken = AUTHORING / "08-visual-repair" / "fixtures" / "broken-lead-port.aixsym.json"
    broken_result = lint_symbol(broken) if broken.is_file() else {"valid": True, "issues": []}
    broken_codes = {item["code"] for item in broken_result.get("issues", [])}
    expected_failure = "lead-port-mismatch" in broken_codes and not broken_result["valid"]
    return {
        "valid": bool(results) and all(item["valid"] for item in results) and expected_failure,
        "examples": len(results),
        "checks": sum(item["checks"] for item in results),
        "expectedBrokenFixtureDetected": expected_failure,
        "results": results,
        "brokenFixture": broken_result,
    }


def validate_renderer_contract_examples() -> dict[str, Any]:
    issues: list[ValidationIssue] = []
    checks = 0
    variant_scene = read_json(AUTHORING / "04-parameterized-variant" / "render" / "resolved-scene.json")
    by_key = {item["key"]: item for item in variant_scene["entities"]}
    checks += 4
    if by_key.get("R1", {}).get("variant") != "ansi":
        issues.append(ValidationIssue("variant-precedence", "examples/authoring/04-parameterized-variant", "R1 did not resolve presentation.defaultVariant=ansi"))
    if by_key.get("R2", {}).get("variant") != "iec":
        issues.append(ValidationIssue("variant-precedence", "examples/authoring/04-parameterized-variant", "R2 placement.variant did not override the presentation default"))
    if by_key.get("R1", {}).get("parameters", {}).get("body-length") != 30:
        issues.append(ValidationIssue("parameter-precedence", "examples/authoring/04-parameterized-variant", "R1 placement parameter did not override the variant default"))
    if by_key.get("R2", {}).get("parameters", {}).get("body-height") != 10:
        issues.append(ValidationIssue("parameter-precedence", "examples/authoring/04-parameterized-variant", "R2 placement parameter did not override the symbol default"))

    binding_root = AUTHORING / "05-field-and-port-binding"
    renderer = ProjectRenderer(binding_root / "project.aixproj.json", SCHEMA_ROOT)
    binding = renderer.bindings["S1"]
    checks += 5
    expected_fields = {"reference": "S1", "value": "5V_OVERRIDE", "deviceLabel": "TEMP"}
    for key, expected in expected_fields.items():
        if binding.fields.get(key) != expected:
            issues.append(ValidationIssue("field-precedence", binding_root.relative_to(ROOT).as_posix(), f"Field {key} resolved to {binding.fields.get(key)!r}, expected {expected!r}"))
    if set(binding.port_positions) != {"in", "out"}:
        issues.append(ValidationIssue("portmap-direction", binding_root.relative_to(ROOT).as_posix(), "Resolved port positions are not keyed by semantic component port IDs"))
    if binding.presentation["portMap"] != {"in": "p-left", "out": "p-right"}:
        issues.append(ValidationIssue("portmap-direction", binding_root.relative_to(ROOT).as_posix(), "portMap direction is not semantic component port to symbol port"))
    return {"valid": not issues, "checks": checks, "issues": [x.to_dict() for x in issues]}


def main() -> int:
    coverage = validate_reference_coverage()
    snippets = validate_snippet_blocks()
    examples = validate_all_authoring_examples()
    renderer = validate_renderer_contract_examples()
    result = {"valid": all(item["valid"] for item in (coverage, snippets, examples, renderer)), "referenceCoverage": coverage, "snippets": snippets, "examples": examples, "rendererContract": renderer}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
