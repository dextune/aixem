"""Adapters from existing AIXEM validators/renderers to Agent Diagnostic 1."""
from __future__ import annotations

import json
import math
from pathlib import Path, PurePosixPath
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMATIC_IMPLEMENTATION = REPOSITORY_ROOT / "implementation" / "schematic"
if str(SCHEMATIC_IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(SCHEMATIC_IMPLEMENTATION))

from component_core import (  # type: ignore  # noqa: E402
    AixemGraphicsError,
    eval_numeric,
    parse_aixem,
    schema_path,
    sha256_file,
)
from project_composition import PROJECT_SCHEMA_V2  # type: ignore  # noqa: E402
from render_project import (  # type: ignore  # noqa: E402
    DEFAULT_SCHEMA_ROOT,
    DEFAULT_STYLE,
    GridProjectRenderer,
    MultiSheetProjectRenderer,
)

from .diagnostics import (
    Diagnostic,
    assign_diagnostic_ids,
    diagnostics_to_dicts,
    make_diagnostic,
    normalize_exception,
)

VIEWER_MODEL_SCHEMA = REPOSITORY_ROOT / "docs" / "specifications" / "schemas" / "viewer" / "aixem-viewer-model-1.schema.json"

ROUTE_VALIDATOR_SELECTION: dict[str, tuple[str, ...]] = {
    "create-symbol": (
        "schematic.symbol_schema",
        "schematic.symbol_design",
        "schematic.authoring_binding",
    ),
    "create-schematic": (
        "schematic.semantic",
        "schematic.component_type_closure",
        "schematic.placement_closure",
        "schematic.authoring_binding",
        "schematic.grid",
    ),
    "route-nets": (
        "schematic.route_closure",
        "schematic.orthogonal",
        "schematic.junction",
        "schematic.grid",
    ),
    "compose-project": (
        "schematic.project_schema",
        "schematic.digest_lock",
        "schematic.semantic",
        "schematic.geometry_isolation",
    ),
    "route-project-nets": (
        "schematic.route_closure",
        "schematic.orthogonal",
        "schematic.deterministic",
        "schematic.workbench",
    ),
    "render-review": (
        "schematic.renderer_contract",
        "schematic.reference_viewer",
    ),
    "validate-project": (
        "schematic.semantic",
        "schematic.authoring_binding",
        "schematic.route_closure",
        "schematic.renderer_contract",
        "schematic.reference_viewer",
    ),
}


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return path.name


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_project_files(workspace: Path, explicit: Path | None = None) -> list[Path]:
    workspace = workspace.resolve()
    if explicit is not None:
        path = explicit if explicit.is_absolute() else workspace / explicit
        path = path.resolve()
        path.relative_to(workspace)
        if not path.is_file():
            raise FileNotFoundError(path)
        return [path]
    direct = sorted(workspace.glob("*.aixproj.json"))
    if direct:
        return direct
    # A staged evaluation may wrap one project in a case directory.  Avoid
    # selecting nested leaf manifests when a top-level project is present.
    recursive = sorted(workspace.rglob("*.aixproj.json"))
    shallowest = min((len(path.relative_to(workspace).parts) for path in recursive), default=0)
    return [path for path in recursive if len(path.relative_to(workspace).parts) == shallowest]


def _json_schema_diagnostics(path: Path, workspace: Path) -> list[Diagnostic]:
    try:
        instance = _read_json(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [make_diagnostic(
            "AIXEM-DIAG-SCHEMA-INVALID",
            f"Cannot parse JSON: {exc}",
            artifact=path,
            workspace_root=workspace,
            evidence={"validator": "json.parse"},
        )]
    schema_uri = str(instance.get("schema", "")) if isinstance(instance, Mapping) else ""
    if not schema_uri:
        return [make_diagnostic(
            "AIXEM-DIAG-SCHEMA-INVALID",
            "JSON artifact does not declare a schema URI.",
            artifact=path,
            workspace_root=workspace,
            evidence={"validator": "json.schema"},
        )]
    try:
        schema_file = schema_path(DEFAULT_SCHEMA_ROOT, schema_uri)
    except Exception as exc:  # noqa: BLE001
        return [normalize_exception(exc, artifact=path, workspace_root=workspace, validator="json.schema")]
    validator = Draft202012Validator(_read_json(schema_file), format_checker=FormatChecker())
    diagnostics: list[Diagnostic] = []
    for issue in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        path_parts = [str(part) for part in issue.absolute_path]
        pointer = "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in path_parts)
        code = "AIXEM-DIAG-SCHEMA-INVALID"
        if (
            schema_uri.endswith("/aixproj/2")
            and issue.validator == "uniqueItems"
            and "projectNets" in path_parts
            and "members" in path_parts
        ):
            code = "AIXEM-DIAG-PROJECT-NET-DUPLICATE-MEMBER"
        diagnostics.append(make_diagnostic(
            code,
            issue.message,
            artifact=path,
            json_pointer=pointer,
            workspace_root=workspace,
            evidence={
                "validator": "json.schema",
                "schema": schema_uri,
                "schemaPointer": "/" + "/".join(str(part) for part in issue.absolute_schema_path),
            },
        ))
    return diagnostics


def _defaults(symbol: Mapping[str, Any]) -> dict[str, Any]:
    return {name: definition["default"] for name, definition in symbol.get("parameters", {}).items()}


def _walk_nodes(nodes: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
    for node in nodes:
        yield node
        if node.get("type") == "group":
            yield from _walk_nodes(node.get("children", []))


def _close(a: tuple[float, float], b: tuple[float, float], tolerance: float = 1e-6) -> bool:
    return math.isclose(a[0], b[0], abs_tol=tolerance) and math.isclose(a[1], b[1], abs_tol=tolerance)


def _on_grid(value: float, grid: float, tolerance: float = 1e-6) -> bool:
    return abs(value / grid - round(value / grid)) <= tolerance


def validate_symbol_design(path: Path, workspace: Path, *, snap: float = 2.5) -> list[Diagnostic]:
    try:
        symbol = _read_json(path)["symbol"]
    except Exception:
        return []  # schema diagnostics own malformed documents
    parameters = _defaults(symbol)
    diagnostics: list[Diagnostic] = []
    ports: dict[str, tuple[float, float]] = {}
    for index, port in enumerate(symbol.get("ports", [])):
        port_id = str(port.get("id", index))
        try:
            point = (eval_numeric(port["x"], parameters), eval_numeric(port["y"], parameters))
            orientation = eval_numeric(port.get("orientation", 0), parameters) % 360
        except Exception as exc:  # noqa: BLE001
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-SYMBOL-PORT-EXPRESSION",
                f"Port {port_id} cannot resolve: {exc}",
                artifact=path,
                json_pointer=f"/symbol/ports/{index}",
                object_kind="symbol-port",
                object_id=port_id,
                workspace_root=workspace,
                evidence={"validator": "schematic.symbol_design"},
            ))
            continue
        ports[port_id] = point
        if not _on_grid(point[0], snap) or not _on_grid(point[1], snap):
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-SYMBOL-PORT-OFF-GRID",
                f"Port {port_id} at {point} is off the {snap:g} mm authoring grid.",
                artifact=path,
                json_pointer=f"/symbol/ports/{index}",
                object_kind="symbol-port",
                object_id=port_id,
                workspace_root=workspace,
                evidence={"validator": "schematic.symbol_design", "snap": snap},
            ))
        if orientation not in {0, 90, 180, 270}:
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-SYMBOL-PORT-ORIENTATION",
                f"Port {port_id} orientation {orientation:g} is not orthogonal.",
                artifact=path,
                json_pointer=f"/symbol/ports/{index}/orientation",
                object_kind="symbol-port",
                object_id=port_id,
                workspace_root=workspace,
                evidence={"validator": "schematic.symbol_design"},
            ))

    graphics = list(symbol.get("graphics", []))
    for variant in symbol.get("variants", []):
        graphics.extend(variant.get("graphics", []))
    leads: dict[str, tuple[float, float]] = {}
    for node in _walk_nodes(graphics):
        if node.get("role") != "pin-lead":
            continue
        metadata = node.get("metadata", {})
        port_id = str(metadata.get("port", ""))
        endpoint = metadata.get("portEndpoint")
        if node.get("type") != "line" or endpoint not in {"start", "end"} or not port_id:
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-SYMBOL-LEAD-MISSING",
                f"Pin lead {node.get('id', '<unnamed>')} must be a line with metadata.port and metadata.portEndpoint.",
                artifact=path,
                object_kind="symbol-primitive",
                object_id=str(node.get("id", "")),
                workspace_root=workspace,
                evidence={"validator": "schematic.symbol_design"},
            ))
            continue
        try:
            x_key, y_key = ("x1", "y1") if endpoint == "start" else ("x2", "y2")
            leads[port_id] = (eval_numeric(node[x_key], parameters), eval_numeric(node[y_key], parameters))
        except Exception as exc:  # noqa: BLE001
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-SYMBOL-PORT-EXPRESSION",
                f"Lead for port {port_id} cannot resolve: {exc}",
                artifact=path,
                object_kind="symbol-primitive",
                object_id=str(node.get("id", "")),
                workspace_root=workspace,
                evidence={"validator": "schematic.symbol_design"},
            ))
    for port_id, point in sorted(ports.items()):
        if port_id not in leads:
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-SYMBOL-LEAD-MISSING",
                f"Port {port_id} has no machine-associated visible pin lead.",
                severity="warning",
                artifact=path,
                object_kind="symbol-port",
                object_id=port_id,
                workspace_root=workspace,
                evidence={"validator": "schematic.symbol_design"},
            ))
        elif not _close(point, leads[port_id]):
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH",
                f"Port {port_id} is at {point}, but its visible lead ends at {leads[port_id]}.",
                artifact=path,
                object_kind="symbol-port",
                object_id=port_id,
                workspace_root=workspace,
                evidence={"validator": "schematic.symbol_design", "port": list(point), "leadEndpoint": list(leads[port_id])},
            ))

    recipe = symbol.get("metadata", {}).get("recipe")
    if recipe in {"connector", "multi-pin-ic"}:
        pitch = float(symbol.get("metadata", {}).get("pinPitch", 5))
        side_groups: dict[int, list[float]] = {0: [], 90: [], 180: [], 270: []}
        for port in symbol.get("ports", []):
            port_id = str(port.get("id"))
            if port_id not in ports:
                continue
            orientation = int(eval_numeric(port.get("orientation", 0), parameters)) % 360
            x, y = ports[port_id]
            side_groups[orientation].append(y if orientation in {0, 180} else x)
        for orientation, values in side_groups.items():
            unique = sorted(set(values))
            for first, second in zip(unique, unique[1:]):
                if not _on_grid(second - first, pitch):
                    diagnostics.append(make_diagnostic(
                        "AIXEM-DIAG-SYMBOL-PIN-PITCH",
                        f"Ports on orientation {orientation} use pitch {second-first:g}, expected a multiple of {pitch:g} mm.",
                        artifact=path,
                        workspace_root=workspace,
                        evidence={"validator": "schematic.symbol_design", "orientation": orientation, "pitch": pitch},
                    ))

    rects = [node for node in _walk_nodes(graphics) if node.get("role") == "body" and node.get("type") == "rect"]
    fields = [node for node in _walk_nodes(graphics) if node.get("type") == "text" and node.get("field") in {"reference", "value"}]
    for rect in rects:
        try:
            rx = eval_numeric(rect["x"], parameters)
            ry = eval_numeric(rect["y"], parameters)
            rw = eval_numeric(rect["width"], parameters)
            rh = eval_numeric(rect["height"], parameters)
        except Exception:
            continue
        for field in fields:
            try:
                fx = eval_numeric(field["x"], parameters)
                fy = eval_numeric(field["y"], parameters)
            except Exception:
                continue
            if rx <= fx <= rx + rw and ry <= fy <= ry + rh:
                diagnostics.append(make_diagnostic(
                    "AIXEM-DIAG-SYMBOL-FIELD-BODY-OVERLAP",
                    f"Field {field.get('field')} anchor ({fx:g},{fy:g}) lies inside body {rect.get('id', '<body>')}.",
                    artifact=path,
                    object_kind="symbol-field",
                    object_id=str(field.get("id", field.get("field", ""))),
                    workspace_root=workspace,
                    evidence={"validator": "schematic.symbol_design"},
                ))
    return diagnostics


def _project_roots_for_libraries(workspace: Path, projects: Sequence[Path]) -> dict[Path, Path]:
    result: dict[Path, Path] = {}
    for project_path in projects:
        try:
            doc = _read_json(project_path)["project"]
        except Exception:
            continue
        root = project_path.parent
        for ref in doc.get("libraries", []):
            try:
                path = (root / PurePosixPath(ref["path"])).resolve()
                path.relative_to(workspace.resolve())
                result[path] = root
            except (KeyError, ValueError, OSError):
                continue
    return result


def validate_library_bindings(path: Path, workspace: Path, project_root: Path) -> list[Diagnostic]:
    try:
        library = _read_json(path)["library"]
    except Exception:
        return []
    diagnostics: list[Diagnostic] = []
    for component_index, component in enumerate(library.get("components", [])):
        component_id = str(component.get("id", component_index))
        semantic = {str(port.get("id")) for port in component.get("ports", [])}
        for presentation_index, presentation in enumerate(component.get("presentations", [])):
            pointer = f"/library/components/{component_index}/presentations/{presentation_index}"
            mapped = set(map(str, presentation.get("portMap", {}).keys()))
            if mapped != semantic:
                diagnostics.append(make_diagnostic(
                    "AIXEM-DIAG-BINDING-PORTMAP-INCOMPLETE",
                    f"{component_id} portMap keys {sorted(mapped)} do not equal semantic ports {sorted(semantic)}.",
                    artifact=path,
                    json_pointer=pointer + "/portMap",
                    object_kind="component-presentation",
                    object_id=component_id,
                    workspace_root=workspace,
                    evidence={"validator": "schematic.authoring_binding"},
                ))
            asset = presentation.get("asset", {})
            asset_rel = str(asset.get("path", ""))
            try:
                symbol_path = (project_root / PurePosixPath(asset_rel)).resolve()
                symbol_path.relative_to(workspace.resolve())
            except (ValueError, OSError):
                symbol_path = project_root / "__unsafe__"
            if not symbol_path.is_file():
                diagnostics.append(make_diagnostic(
                    "AIXEM-DIAG-BINDING-ASSET-MISSING",
                    f"Missing asset {asset_rel}.",
                    artifact=path,
                    json_pointer=pointer + "/asset/path",
                    object_kind="component-presentation",
                    object_id=component_id,
                    workspace_root=workspace,
                    evidence={"validator": "schematic.authoring_binding"},
                ))
                continue
            try:
                symbol_ports = {str(port.get("id")) for port in _read_json(symbol_path)["symbol"].get("ports", [])}
            except Exception:
                symbol_ports = set()
            unknown = sorted(set(map(str, presentation.get("portMap", {}).values())) - symbol_ports)
            if unknown:
                diagnostics.append(make_diagnostic(
                    "AIXEM-DIAG-BINDING-PORTMAP-TARGET-UNKNOWN",
                    f"{component_id} maps to unknown symbol ports {unknown}.",
                    artifact=path,
                    json_pointer=pointer + "/portMap",
                    object_kind="component-presentation",
                    object_id=component_id,
                    workspace_root=workspace,
                    evidence={"validator": "schematic.authoring_binding"},
                ))
            observed = sha256_file(symbol_path)
            if asset.get("digest") != observed:
                diagnostics.append(make_diagnostic(
                    "AIXEM-DIAG-BINDING-ASSET-DIGEST",
                    f"{component_id} symbol digest does not match: expected {asset.get('digest')}, observed {observed}.",
                    artifact=path,
                    json_pointer=pointer + "/asset/digest",
                    object_kind="component-presentation",
                    object_id=component_id,
                    workspace_root=workspace,
                    evidence={"validator": "schematic.authoring_binding", "referencedArtifact": _relative(symbol_path, workspace)},
                ))
    return diagnostics


def _make_renderer(project_path: Path):
    project_doc = _read_json(project_path)
    if project_doc.get("schema") == PROJECT_SCHEMA_V2:
        return MultiSheetProjectRenderer(project_path, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE)
    return GridProjectRenderer(project_path, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE)


def validate_renderer_structure(project_path: Path, workspace: Path) -> tuple[list[Diagnostic], Any | None]:
    try:
        renderer = _make_renderer(project_path)
    except Exception as exc:  # noqa: BLE001
        return [normalize_exception(exc, artifact=project_path, workspace_root=workspace, validator="schematic.renderer_contract")], None
    diagnostics: list[Diagnostic] = []
    if isinstance(renderer, GridProjectRenderer):
        for entity in renderer.grid_metrics.get("placementExceptions", []):
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-LAYOUT-PLACEMENT-OFF-GRID",
                f"Placement {entity} is off the active grid.",
                artifact=renderer.layout_path,
                object_kind="placement",
                object_id=str(entity),
                workspace_root=workspace,
                evidence={"validator": "schematic.grid", "snap": renderer.grid_metrics.get("snap")},
            ))
        for segment in renderer.grid_metrics.get("zeroLengthSegments", []):
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-ROUTE-ZERO-LENGTH",
                f"Route contains zero-length segment {segment}.",
                artifact=renderer.layout_path,
                object_kind="route-segment",
                object_id=str(segment),
                workspace_root=workspace,
                evidence={"validator": "schematic.orthogonal"},
            ))
    return diagnostics, renderer


def validate_workspace(
    workspace: Path,
    route: str,
    *,
    project: Path | None = None,
    validators: Iterable[str] | None = None,
) -> dict[str, Any]:
    workspace = workspace.resolve()
    selected_validators = tuple(validators or ROUTE_VALIDATOR_SELECTION.get(route, ROUTE_VALIDATOR_SELECTION["validate-project"]))
    diagnostics: list[Diagnostic] = []
    projects = find_project_files(workspace, project)

    json_files = sorted(
        path for path in workspace.rglob("*.json")
        if ".aixem-agent" not in path.parts and not any(part in {"render", "evidence", "fixtures"} for part in path.relative_to(workspace).parts)
        and path.name.endswith((".aixsym.json", ".aixlib.json", ".aixlayout.json", ".aixproj.json"))
    )
    for path in json_files:
        diagnostics.extend(_json_schema_diagnostics(path, workspace))

    if route in {"create-symbol", "create-schematic", "route-nets", "render-review", "validate-project"}:
        for path in sorted(workspace.rglob("*.aixsym.json")):
            if any(part in {"render", "evidence", "fixtures", ".aixem-agent"} for part in path.relative_to(workspace).parts):
                continue
            diagnostics.extend(validate_symbol_design(path, workspace))
        project_roots = _project_roots_for_libraries(workspace, projects)
        for path in sorted(workspace.rglob("*.aixlib.json")):
            if any(part in {"render", "evidence", "fixtures", ".aixem-agent"} for part in path.relative_to(workspace).parts):
                continue
            diagnostics.extend(validate_library_bindings(path, workspace, project_roots.get(path.resolve(), workspace)))

    if route in {"create-schematic", "route-nets", "compose-project", "route-project-nets", "render-review", "validate-project"}:
        for source in sorted(workspace.rglob("*.aixem")):
            if any(part in {".aixem-agent", "fixtures"} for part in source.relative_to(workspace).parts):
                continue
            try:
                parse_aixem(source)
            except Exception as exc:  # noqa: BLE001
                diagnostics.append(normalize_exception(exc, artifact=source, workspace_root=workspace, validator="schematic.semantic"))

    renderers: list[Any] = []
    if route != "create-symbol" or projects:
        for project_path in projects:
            project_diagnostics, renderer = validate_renderer_structure(project_path, workspace)
            diagnostics.extend(project_diagnostics)
            if renderer is not None:
                renderers.append(renderer)

    normalized = assign_diagnostic_ids(diagnostics)
    blocking = sum(item.severity == "error" for item in normalized)
    return {
        "schema": "https://schemas.aixem.org/agent/validation-result/1",
        "formatVersion": "1.0",
        "route": route,
        "validatorsExecuted": sorted(set(selected_validators)),
        "projectFiles": [_relative(path, workspace) for path in projects],
        "diagnostics": [item.to_dict() for item in normalized],
        "summary": {
            "diagnostics": len(normalized),
            "blocking": blocking,
            "warnings": sum(item.severity == "warning" for item in normalized),
            "projects": len(projects),
        },
        "valid": blocking == 0,
    }


def _artifact_digest_map(directory: Path, workspace: Path) -> dict[str, str]:
    return {
        _relative(path, workspace): sha256_file(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _validate_viewer_model(path: Path, workspace: Path) -> list[Diagnostic]:
    if not path.is_file():
        return [make_diagnostic(
            "AIXEM-DIAG-UNSUPPORTED-CAPABILITY",
            "Production render did not emit viewer-model.json.",
            artifact=path,
            workspace_root=workspace,
            evidence={"validator": "schematic.reference_viewer"},
        )]
    validator = Draft202012Validator(_read_json(VIEWER_MODEL_SCHEMA), format_checker=FormatChecker())
    diagnostics: list[Diagnostic] = []
    instance = _read_json(path)
    for issue in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        pointer = "/" + "/".join(str(part) for part in issue.absolute_path)
        diagnostics.append(make_diagnostic(
            "AIXEM-DIAG-SCHEMA-INVALID",
            f"Viewer Model 1: {issue.message}",
            artifact=path,
            json_pointer=pointer,
            workspace_root=workspace,
            evidence={"validator": "schematic.reference_viewer"},
        ))
    return diagnostics


def render_workspace(
    workspace: Path,
    *,
    project: Path | None = None,
    repeat_count: int = 3,
) -> dict[str, Any]:
    """Render all selected projects and prove byte identity across repeats."""
    workspace = workspace.resolve()
    projects = find_project_files(workspace, project)
    diagnostics: list[Diagnostic] = []
    actual_artifacts: dict[str, str] = {}
    deterministic_runs: list[dict[str, str]] = []
    for project_path in projects:
        output = project_path.parent / "render"
        try:
            renderer = _make_renderer(project_path)
            renderer.render(output)
            actual_artifacts.update(_artifact_digest_map(output, workspace))
            diagnostics.extend(_validate_viewer_model(output / "viewer-model.json", workspace))
        except Exception as exc:  # noqa: BLE001
            diagnostics.append(normalize_exception(exc, artifact=project_path, workspace_root=workspace, validator="schematic.renderer_contract"))
            continue

        project_runs: list[dict[str, str]] = []
        for _index in range(repeat_count):
            with tempfile.TemporaryDirectory(prefix="aixem-agent-render-") as temporary:
                temp_output = Path(temporary) / "render"
                try:
                    fresh = _make_renderer(project_path)
                    fresh.render(temp_output)
                    digest_map = {
                        path.relative_to(temp_output).as_posix(): sha256_file(path)
                        for path in sorted(temp_output.rglob("*")) if path.is_file()
                    }
                    project_runs.append(digest_map)
                except Exception as exc:  # noqa: BLE001
                    diagnostics.append(normalize_exception(exc, artifact=project_path, workspace_root=workspace, validator="schematic.deterministic"))
                    break
        deterministic_runs.extend(project_runs)
        if project_runs and any(item != project_runs[0] for item in project_runs[1:]):
            diagnostics.append(make_diagnostic(
                "AIXEM-DIAG-RENDERER-DETERMINISM",
                f"Project {_relative(project_path, workspace)} produced different artifacts across {len(project_runs)} repeat renders.",
                artifact=project_path,
                workspace_root=workspace,
                evidence={"validator": "schematic.deterministic", "repeatCount": len(project_runs)},
            ))

    normalized = assign_diagnostic_ids(diagnostics)
    blocking = sum(item.severity == "error" for item in normalized)
    changed: list[str] = []
    if deterministic_runs:
        reference = deterministic_runs[0]
        changed = sorted({path for run in deterministic_runs[1:] for path in set(reference) | set(run) if reference.get(path) != run.get(path)})
    return {
        "valid": blocking == 0 and not changed and bool(projects),
        "projects": [_relative(path, workspace) for path in projects],
        "artifacts": dict(sorted(actual_artifacts.items())),
        "diagnostics": [item.to_dict() for item in normalized],
        "determinism": {
            "valid": not changed and len(deterministic_runs) == repeat_count * len(projects),
            "repeatCount": repeat_count,
            "projectRuns": len(deterministic_runs),
            "changed": changed,
        },
    }
