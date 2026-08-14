"""Build and validate deterministic, non-authoritative AIXEM Viewer Model 1 data."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

VIEWER_MODEL_SCHEMA = "https://schemas.aixem.org/viewer/viewer-model/1"
VIEWER_CONTRACT = "aixem.reference-viewer@1"
DOM_CONTRACT = "1"
FORMAT_VERSION = "1.0"
SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "specifications"
    / "schemas"
    / "viewer"
    / "aixem-viewer-model-1.schema.json"
)

CATEGORY_ORDER = {
    "sheet": 0,
    "entity": 1,
    "local-net": 2,
    "interface": 3,
    "project-net": 4,
}
CATEGORY_LABELS = {
    "sheet": "Sheets",
    "entity": "Components",
    "local-net": "Local Nets",
    "interface": "Interface Ports",
    "project-net": "Project Nets",
}


class ViewerModelError(ValueError):
    """Fail-closed Viewer Model construction or closure error."""


def _display(value: Any) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return str(value)


def _properties(rows: Iterable[tuple[str, Any]]) -> list[dict[str, str]]:
    return [{"label": label, "value": _display(value)} for label, value in rows]


def _object(
    qid: str,
    kind: str,
    label: str,
    *,
    native_id: str,
    sheet: str | None,
    properties: Iterable[tuple[str, Any]],
    related_qids: Iterable[str] = (),
    representations: Iterable[str] = (),
    search_fields: Iterable[Any] = (),
) -> dict[str, Any]:
    text = " ".join(
        _display(value)
        for value in (qid, label, native_id, sheet or "", *search_fields)
        if value is not None
    ).strip().lower()
    return {
        "qid": qid,
        "kind": kind,
        "category": CATEGORY_LABELS[kind],
        "label": label,
        "nativeId": native_id,
        "sheet": sheet,
        "searchText": text,
        "properties": _properties(properties),
        "relatedQids": sorted(set(related_qids)),
        "representations": list(dict.fromkeys(representations)),
    }


def _diagnostic(code: str, message: str, *, severity: str = "info", status: str = "PASS") -> dict[str, str]:
    return {"code": code, "severity": severity, "status": status, "message": message}


def _search_index(objects: dict[str, dict[str, Any]], sheet_order: dict[str, int]) -> list[dict[str, Any]]:
    entries = [
        {
            "qid": item["qid"],
            "kind": item["kind"],
            "category": item["category"],
            "label": item["label"],
            "sheet": item["sheet"],
            "searchText": item["searchText"],
        }
        for item in objects.values()
    ]
    entries.sort(
        key=lambda item: (
            CATEGORY_ORDER[item["kind"]],
            sheet_order.get(item.get("sheet") or "", 1_000_000),
            item["qid"],
        )
    )
    return entries


def _layers(scene: dict[str, Any], sheet_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "sheet": sheet_id,
            "qualifiedId": f"layer:{sheet_id}:{item['id']}",
            "purpose": item.get("purpose", "presentation layer"),
            "order": int(item.get("order", 0)),
            "defaultVisible": bool(item.get("defaultVisible", True)),
            "locked": bool(item.get("locked", False)),
            "printable": bool(item.get("printable", True)),
        }
        for item in sorted(scene.get("layers", []), key=lambda value: (int(value.get("order", 0)), value["id"]))
    ]


def _single_interface_records(interface_ports: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in interface_ports or []:
        result.append(
            {
                "id": str(item["id"]),
                "direction": str(item.get("direction", "passive")),
                "role": str(item.get("role", "signal")),
                "localNet": item.get("localNet"),
                "projectNet": None,
                "coordinate": list(item.get("coordinate", [])),
            }
        )
    return sorted(result, key=lambda item: item["id"])


def build_single_sheet_viewer_model(
    scene: dict[str, Any],
    *,
    sheet_id: str = "main",
    interface_ports: list[dict[str, Any]] | None = None,
    release: str,
) -> dict[str, Any]:
    """Derive Viewer Model 1 for one resolved scene without adding circuit authority."""
    scene = copy.deepcopy(scene)
    project = scene["project"]
    title = str(project.get("title") or project["id"])
    layers = _layers(scene, sheet_id)
    interfaces = _single_interface_records(interface_ports)
    objects: dict[str, dict[str, Any]] = {}
    sheet_qid = f"sheet:{sheet_id}"
    objects[sheet_qid] = _object(
        sheet_qid,
        "sheet",
        title,
        native_id=sheet_id,
        sheet=sheet_id,
        properties=(
            ("Qualified ID", sheet_qid),
            ("Sheet", sheet_id),
            ("Title", title),
            ("Width", scene["sheet"]["width"]),
            ("Height", scene["sheet"]["height"]),
            ("Unit", scene.get("coordinateSystem", {}).get("unit", "mm")),
        ),
        representations=(f"sheet:{sheet_id}",),
        search_fields=(project.get("id"), title),
    )

    for item in sorted(scene.get("entities", []), key=lambda value: value["key"]):
        qid = f"entity:{sheet_id}:{item['key']}"
        placement = item.get("placement", {})
        objects[qid] = _object(
            qid,
            "entity",
            f"{item.get('reference', item['key'])} · {item.get('value', '')}".rstrip(" ·"),
            native_id=item["key"],
            sheet=sheet_id,
            properties=(
                ("Qualified ID", qid),
                ("Sheet", sheet_id),
                ("Entity ID", item["key"]),
                ("Reference", item.get("reference", "")),
                ("Value", item.get("value", "")),
                ("Component type", item.get("componentType", "")),
                ("Symbol ID", item.get("symbolId", "")),
                ("Variant", item.get("variant") or "default"),
                ("Placement", placement),
                ("Parameters", item.get("parameters", {})),
                ("Ports", item.get("ports", {})),
                ("Symbol digest", item.get("symbolDigest", "")),
            ),
            representations=(f"sheet:{sheet_id}",),
            search_fields=(item.get("reference"), item.get("value"), item.get("componentType"), item.get("symbolId")),
        )

    local_to_interface = {item.get("localNet"): item["id"] for item in interfaces if item.get("localNet")}
    for item in sorted(scene.get("nets", []), key=lambda value: value["name"]):
        qid = f"local-net:{sheet_id}:{item['name']}"
        interface_id = local_to_interface.get(item["name"])
        objects[qid] = _object(
            qid,
            "local-net",
            item["name"],
            native_id=item["name"],
            sheet=sheet_id,
            properties=(
                ("Qualified ID", qid),
                ("Sheet", sheet_id),
                ("Local net ID", item["name"]),
                ("Endpoint count", len(item.get("endpoints", []))),
                ("Endpoints", item.get("endpoints", [])),
                ("Path count", len(item.get("paths", []))),
                ("Junction count", len(item.get("junctions", []))),
                ("Related project net", "none"),
                ("Semantic authority", ".aixem"),
            ),
            related_qids=(),
            representations=(f"sheet:{sheet_id}",),
            search_fields=(item.get("endpoints", []), interface_id),
        )

    for item in interfaces:
        qid = f"interface:{sheet_id}:{item['id']}"
        local_qid = f"local-net:{sheet_id}:{item['localNet']}" if item.get("localNet") else None
        objects[qid] = _object(
            qid,
            "interface",
            f"{sheet_id} / @{item['id']}",
            native_id=item["id"],
            sheet=sheet_id,
            properties=(
                ("Qualified ID", qid),
                ("Sheet", sheet_id),
                ("Port ID", item["id"]),
                ("Direction", item["direction"]),
                ("Role", item["role"]),
                ("Local net", local_qid or "unconnected"),
                ("Project net", "unconnected"),
                ("Sheet coordinate", item.get("coordinate", [])),
            ),
            related_qids=([local_qid] if local_qid in objects else []),
            representations=(f"sheet:{sheet_id}",),
            search_fields=(item["direction"], item["role"], item.get("localNet")),
        )

    sheet_order = {sheet_id: 0}
    visible_layers = {sheet_id: {item["id"]: item["defaultVisible"] for item in layers}}
    diagnostics = [
        _diagnostic("VIEWER-READONLY-001", "Reference Viewer runtime state is derived and read-only."),
        _diagnostic("VIEWER-QID-001", f"{len(objects)} qualified objects indexed without ambiguity."),
        _diagnostic("VIEWER-ASSET-001", "The self-contained Viewer requires no remote presentation assets."),
    ]
    grid = scene.get("gridValidation", {})
    if grid:
        diagnostics.extend(
            [
                _diagnostic("GRID-001", f"{grid.get('placementsOnGrid', 0)}/{grid.get('placements', 0)} placements satisfy the declared snap grid."),
                _diagnostic("ROUTE-001", f"{grid.get('orthogonalSegments', 0)} orthogonal route segments are resolved."),
            ]
        )
    model = {
        "schema": VIEWER_MODEL_SCHEMA,
        "formatVersion": FORMAT_VERSION,
        "viewerContract": VIEWER_CONTRACT,
        "domContract": DOM_CONTRACT,
        "release": release,
        "project": {
            "id": project["id"],
            "title": title,
            "schema": "https://schemas.aixem.org/component-graphics/aixproj/1",
            "profile": project.get("profile", "circuit.schematic@1"),
            "multiSheet": False,
        },
        "capabilities": {
            "sheet": True,
            "overview": False,
            "composite": False,
            "hierarchy": False,
            "projectNets": False,
            "interfacePorts": bool(interfaces),
            "diagnostics": True,
            "qualifiedSearch": True,
            "sheetScopedLayers": True,
            "viewport": True,
            "readOnly": True,
            "offline": True,
        },
        "initialState": {
            "mode": "sheet",
            "activeSheet": sheet_id,
            "selection": None,
            "searchQuery": "",
            "activeNavigatorCategory": "entity",
            "visibleLayersBySheet": visible_layers,
        },
        "views": [
            {
                "id": "sheet",
                "label": "Sheet",
                "available": True,
                "canvases": [
                    {
                        "key": f"sheet:{sheet_id}",
                        "sheet": sheet_id,
                        "width": float(scene["sheet"]["width"]),
                        "height": float(scene["sheet"]["height"]),
                        "unit": scene.get("coordinateSystem", {}).get("unit", "mm"),
                    }
                ],
            }
        ],
        "hierarchy": [
            {
                "qid": sheet_qid,
                "id": sheet_id,
                "title": title,
                "parent": None,
                "children": [],
                "depth": 0,
                "order": 0,
            }
        ],
        "sheets": [
            {
                "qid": sheet_qid,
                "id": sheet_id,
                "title": title,
                "parent": None,
                "order": 0,
                "width": float(scene["sheet"]["width"]),
                "height": float(scene["sheet"]["height"]),
                "unit": scene.get("coordinateSystem", {}).get("unit", "mm"),
                "layers": layers,
            }
        ],
        "objects": objects,
        "searchIndex": _search_index(objects, sheet_order),
        "diagnostics": diagnostics,
        "statistics": {
            "sheets": 1,
            "entities": len(scene.get("entities", [])),
            "localNets": len(scene.get("nets", [])),
            "interfacePorts": len(interfaces),
            "projectNets": 0,
            "qualifiedObjects": len(objects),
        },
        "provenance": {
            "resolvedSceneSchema": scene.get("schema"),
            "renderer": scene.get("renderer", {}),
            "generatedAt": scene.get("generatedAt"),
            "hashes": scene.get("hashes", {}),
            "styleProfile": scene.get("styleProfile", {}),
            "authority": {
                "semantics": ".aixem",
                "presentation": ".aixlayout",
                "viewerState": "derived-non-authoritative",
            },
        },
    }
    validate_viewer_model(model)
    return model


def build_multi_sheet_viewer_model(
    project_scene: dict[str, Any],
    sheet_scenes: dict[str, dict[str, Any]],
    *,
    release: str,
) -> dict[str, Any]:
    """Derive Viewer Model 1 from resolved project and leaf scenes."""
    project_scene = copy.deepcopy(project_scene)
    sheet_scenes = copy.deepcopy(sheet_scenes)
    hierarchy = project_scene.get("hierarchy", [])
    sheet_order = {item["id"]: index for index, item in enumerate(hierarchy)}
    objects: dict[str, dict[str, Any]] = {}
    sheet_records: list[dict[str, Any]] = []
    visible_layers: dict[str, dict[str, bool]] = {}
    project_graph = project_scene.get("semanticGraph", {}).get("projectNets", [])
    local_to_project: dict[str, str] = {}
    interface_to_project: dict[str, str] = {}
    for net in project_graph:
        for member in net.get("members", []):
            local_to_project[member["qualifiedLocalNet"]] = net["qualifiedId"]
            interface_to_project[member["interface"]] = net["qualifiedId"]

    for item in hierarchy:
        sheet_id = item["id"]
        scene = sheet_scenes[sheet_id]
        qid = f"sheet:{sheet_id}"
        objects[qid] = _object(
            qid,
            "sheet",
            item["title"],
            native_id=sheet_id,
            sheet=sheet_id,
            properties=(
                ("Qualified ID", qid),
                ("Sheet", sheet_id),
                ("Title", item["title"]),
                ("Parent", item.get("parent") or "Root"),
                ("Hierarchy depth", item.get("depth", 0)),
                ("Width", scene["sheet"]["width"]),
                ("Height", scene["sheet"]["height"]),
                ("Unit", scene.get("coordinateSystem", {}).get("unit", "mm")),
            ),
            representations=(f"sheet:{sheet_id}", "overview", "composite"),
            search_fields=(item.get("parent"), item.get("children", [])),
        )
        layers = _layers(scene, sheet_id)
        visible_layers[sheet_id] = {layer["id"]: layer["defaultVisible"] for layer in layers}
        sheet_records.append(
            {
                "qid": qid,
                "id": sheet_id,
                "title": item["title"],
                "parent": item.get("parent"),
                "order": int(item.get("order", sheet_order[sheet_id])),
                "width": float(scene["sheet"]["width"]),
                "height": float(scene["sheet"]["height"]),
                "unit": scene.get("coordinateSystem", {}).get("unit", "mm"),
                "layers": layers,
            }
        )

        for entity in sorted(scene.get("entities", []), key=lambda value: value["key"]):
            entity_qid = f"entity:{sheet_id}:{entity['key']}"
            objects[entity_qid] = _object(
                entity_qid,
                "entity",
                f"{entity.get('reference', entity['key'])} · {entity.get('value', '')}".rstrip(" ·"),
                native_id=entity["key"],
                sheet=sheet_id,
                properties=(
                    ("Qualified ID", entity_qid),
                    ("Sheet", sheet_id),
                    ("Entity ID", entity["key"]),
                    ("Reference", entity.get("reference", "")),
                    ("Value", entity.get("value", "")),
                    ("Component type", entity.get("componentType", "")),
                    ("Symbol ID", entity.get("symbolId", "")),
                    ("Variant", entity.get("variant") or "default"),
                    ("Placement", entity.get("placement", {})),
                    ("Parameters", entity.get("parameters", {})),
                    ("Ports", entity.get("ports", {})),
                    ("Symbol digest", entity.get("symbolDigest", "")),
                ),
                representations=(f"sheet:{sheet_id}", "composite"),
                search_fields=(entity.get("reference"), entity.get("value"), entity.get("componentType"), entity.get("symbolId")),
            )

        for net in sorted(scene.get("nets", []), key=lambda value: value["name"]):
            local_qid = f"local-net:{sheet_id}:{net['name']}"
            project_qid = local_to_project.get(local_qid)
            objects[local_qid] = _object(
                local_qid,
                "local-net",
                f"{sheet_id} / {net['name']}",
                native_id=net["name"],
                sheet=sheet_id,
                properties=(
                    ("Qualified ID", local_qid),
                    ("Sheet", sheet_id),
                    ("Local net ID", net["name"]),
                    ("Endpoint count", len(net.get("endpoints", []))),
                    ("Endpoints", net.get("endpoints", [])),
                    ("Path count", len(net.get("paths", []))),
                    ("Junction count", len(net.get("junctions", []))),
                    ("Related project net", project_qid or "none"),
                    ("Semantic authority", ".aixem"),
                ),
                related_qids=(),
                representations=(f"sheet:{sheet_id}", "composite"),
                search_fields=(net.get("endpoints", []), project_qid),
            )

        summary = project_scene.get("interfaceSummaries", {}).get(sheet_id, {})
        for port in sorted(summary.get("ports", []), key=lambda value: value["id"]):
            interface_qid = f"interface:{sheet_id}:{port['id']}"
            project_qid = interface_to_project.get(interface_qid)
            local_qid = f"local-net:{sheet_id}:{port['localNet']}" if port.get("localNet") else None
            coordinate = None
            for mode in ("overview", "composite"):
                for anchor in project_scene.get("routing", {}).get(mode, {}).get("anchors", []):
                    if anchor.get("sheet") == sheet_id and anchor.get("port") == port["id"]:
                        coordinate = anchor.get("point")
                        break
                if coordinate is not None:
                    break
            related = [qid for qid in (local_qid, project_qid) if qid]
            objects[interface_qid] = _object(
                interface_qid,
                "interface",
                f"{sheet_id} / @{port['id']}",
                native_id=port["id"],
                sheet=sheet_id,
                properties=(
                    ("Qualified ID", interface_qid),
                    ("Sheet", sheet_id),
                    ("Port ID", port["id"]),
                    ("Direction", port.get("direction", "passive")),
                    ("Role", port.get("role", "signal")),
                    ("Local net", local_qid or "unconnected"),
                    ("Project net", project_qid or "unconnected"),
                    ("Sheet coordinate", coordinate or "not exposed"),
                ),
                related_qids=related,
                representations=(f"sheet:{sheet_id}", "overview", "composite"),
                search_fields=(port.get("direction"), port.get("role"), port.get("localNet"), project_qid),
            )

    for net in sorted(project_graph, key=lambda value: value["qualifiedId"]):
        qid = net["qualifiedId"]
        member_interfaces = [member["interface"] for member in net.get("members", [])]
        backing_local_nets = [member["qualifiedLocalNet"] for member in net.get("members", [])]
        participating_sheets = list(dict.fromkeys(member["sheet"] for member in net.get("members", [])))
        objects[qid] = _object(
            qid,
            "project-net",
            net["id"],
            native_id=net["id"],
            sheet=None,
            properties=(
                ("Qualified ID", qid),
                ("Project-net ID", net["id"]),
                ("Participating sheets", participating_sheets),
                ("Interface members", member_interfaces),
                ("Backing local nets", backing_local_nets),
                ("Transitive endpoint count", len(net.get("transitiveEndpoints", []))),
                ("Transitive endpoints", net.get("transitiveEndpoints", [])),
                ("Crosses hierarchy boundary", bool(net.get("crossesHierarchyBoundary"))),
            ),
            related_qids=member_interfaces,
            representations=("overview", "composite"),
            search_fields=(participating_sheets, member_interfaces, backing_local_nets),
        )

    overview = project_scene["routing"]["overview"]["canvas"]
    composite = project_scene["routing"]["composite"]["canvas"]
    diagnostics = [
        _diagnostic("VIEWER-READONLY-001", "Reference Viewer runtime state is derived and read-only."),
        _diagnostic("VIEWER-QID-001", f"{len(objects)} qualified objects indexed without ambiguity."),
        _diagnostic("VIEWER-MODES-001", "Sheet, Overview, and Composite modes are available from resolved project evidence."),
        _diagnostic("VIEWER-ASSET-001", "The self-contained Viewer requires no remote presentation assets."),
    ]
    for item in project_scene.get("diagnostics", []):
        severity = str(item.get("severity", "info")).lower()
        diagnostics.append(
            _diagnostic(
                str(item.get("code", "PROJECT-DIAGNOSTIC")),
                str(item.get("message", item)),
                severity=severity,
                status="FAIL" if severity == "error" else "PASS",
            )
        )
    first_sheet = hierarchy[0]["id"] if hierarchy else None
    if not first_sheet:
        raise ViewerModelError("VIEWER_NO_SHEETS: multi-sheet Viewer Model requires at least one sheet")
    model = {
        "schema": VIEWER_MODEL_SCHEMA,
        "formatVersion": FORMAT_VERSION,
        "viewerContract": VIEWER_CONTRACT,
        "domContract": DOM_CONTRACT,
        "release": release,
        "project": {
            "id": project_scene["project"]["id"],
            "title": project_scene["project"]["title"],
            "schema": project_scene["project"].get("schema", "https://schemas.aixem.org/component-graphics/aixproj/2"),
            "profile": project_scene["project"].get("profile", "aixem.schematic.multisheet@1"),
            "multiSheet": True,
        },
        "capabilities": {
            "sheet": True,
            "overview": True,
            "composite": True,
            "hierarchy": True,
            "projectNets": bool(project_graph),
            "interfacePorts": any(item["kind"] == "interface" for item in objects.values()),
            "diagnostics": True,
            "qualifiedSearch": True,
            "sheetScopedLayers": True,
            "viewport": True,
            "readOnly": True,
            "offline": True,
        },
        "initialState": {
            "mode": "sheet",
            "activeSheet": first_sheet,
            "selection": None,
            "searchQuery": "",
            "activeNavigatorCategory": "sheet",
            "visibleLayersBySheet": visible_layers,
        },
        "views": [
            {
                "id": "sheet",
                "label": "Sheet",
                "available": True,
                "canvases": [
                    {
                        "key": f"sheet:{item['id']}",
                        "sheet": item["id"],
                        "width": item["width"],
                        "height": item["height"],
                        "unit": item["unit"],
                    }
                    for item in sheet_records
                ],
            },
            {
                "id": "overview",
                "label": "Overview",
                "available": True,
                "canvases": [
                    {
                        "key": "overview",
                        "sheet": None,
                        "width": float(overview["width"]),
                        "height": float(overview["height"]),
                        "unit": "project-space",
                    }
                ],
            },
            {
                "id": "composite",
                "label": "Composite",
                "available": True,
                "canvases": [
                    {
                        "key": "composite",
                        "sheet": None,
                        "width": float(composite["width"]),
                        "height": float(composite["height"]),
                        "unit": "project-space",
                    }
                ],
            },
        ],
        "hierarchy": [
            {
                "qid": f"sheet:{item['id']}",
                "id": item["id"],
                "title": item["title"],
                "parent": item.get("parent"),
                "children": list(item.get("children", [])),
                "depth": int(item.get("depth", 0)),
                "order": int(item.get("order", sheet_order[item["id"]])),
            }
            for item in hierarchy
        ],
        "sheets": sheet_records,
        "objects": objects,
        "searchIndex": _search_index(objects, sheet_order),
        "diagnostics": diagnostics,
        "statistics": {
            **{key: int(value) for key, value in project_scene.get("statistics", {}).items()},
            "qualifiedObjects": len(objects),
        },
        "provenance": {
            "resolvedProjectSceneSchema": project_scene.get("schema"),
            "renderer": project_scene.get("renderer", {}),
            "generatedAt": project_scene.get("generatedAt"),
            "hashes": project_scene.get("hashes", {}),
            "authority": {
                **project_scene.get("authority", {}),
                "viewerState": "derived-non-authoritative",
            },
        },
    }
    validate_viewer_model(model)
    return model


def validate_viewer_model(model: dict[str, Any]) -> None:
    """Validate schema and semantic reference closure for Viewer Model 1."""
    if model.get("schema") != VIEWER_MODEL_SCHEMA:
        raise ViewerModelError(f"VIEWER_SCHEMA_UNSUPPORTED: {model.get('schema')!r}")
    if not SCHEMA_PATH.is_file():
        raise ViewerModelError(f"VIEWER_SCHEMA_MISSING: {SCHEMA_PATH}")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(model), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.absolute_path) or "$"
        raise ViewerModelError(f"VIEWER_SCHEMA_INVALID {location}: {first.message}")

    objects = model["objects"]
    for key, item in objects.items():
        if key != item["qid"]:
            raise ViewerModelError(f"VIEWER_QID_KEY_MISMATCH: {key} != {item['qid']}")
        expected_prefix = f"{item['kind']}:"
        if not key.startswith(expected_prefix):
            raise ViewerModelError(f"VIEWER_QID_KIND_MISMATCH: {key} is not {item['kind']}")
    unresolved: list[str] = []
    for item in objects.values():
        unresolved.extend(qid for qid in item.get("relatedQids", []) if qid not in objects)
    unresolved.extend(item["qid"] for item in model["searchIndex"] if item["qid"] not in objects)
    unresolved.extend(item["qid"] for item in model["hierarchy"] if item["qid"] not in objects)
    if unresolved:
        raise ViewerModelError(f"VIEWER_UNRESOLVED_QIDS: {sorted(set(unresolved))[:20]}")

    sheets = {item["id"] for item in model["sheets"]}
    active_sheet = model["initialState"]["activeSheet"]
    if active_sheet not in sheets:
        raise ViewerModelError(f"VIEWER_ACTIVE_SHEET_UNKNOWN: {active_sheet}")
    visible = model["initialState"]["visibleLayersBySheet"]
    if set(visible) != sheets:
        raise ViewerModelError("VIEWER_LAYER_SHEET_CLOSURE: visible layer state does not cover exactly the declared sheets")
    for sheet in model["sheets"]:
        declared_layers = {item["id"] for item in sheet["layers"]}
        if set(visible[sheet["id"]]) != declared_layers:
            raise ViewerModelError(f"VIEWER_LAYER_CLOSURE: {sheet['id']}")

    view_ids = [item["id"] for item in model["views"]]
    if len(view_ids) != len(set(view_ids)):
        raise ViewerModelError("VIEWER_DUPLICATE_VIEW_ID")
    if model["initialState"]["mode"] not in view_ids:
        raise ViewerModelError("VIEWER_INITIAL_MODE_UNAVAILABLE")
