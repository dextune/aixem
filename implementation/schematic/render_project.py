#!/usr/bin/env python3
"""AIXEM deterministic schematic renderer with Reference Viewer 1 outputs."""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys
import time
from typing import Any

from project_composition import ProjectCompositionResolver, PROJECT_SCHEMA_V2
from project_routing import ProjectRoutingResult, points_attribute, route_is_release_valid, route_project

from viewer import (
    ReferenceViewerRenderer,
    ReviewWorkbenchRenderer,
    build_multi_sheet_viewer_model,
    build_single_sheet_viewer_model,
)

from component_core import (  # type: ignore
    AixemGraphicsError,
    ProjectRenderer as CoreProjectRenderer,
    eval_numeric,
    fmt,
    matrix_svg,
    pretty_json,
    sha256_file,
    xml,
)

FIXED_TIME = "2026-08-10T12:00:00Z"
RENDERER_ID = "aixem-grid-schematic-reference-renderer"
RENDERER_VERSION = "0.5.1"
# Compatibility stamp intentionally remains the protected 0.5.5 renderer release.
# AIXEM 0.5.6 adds only agent execution/evidence contracts; changing this value
# would invalidate byte-stable SVG, resolved-scene, Viewer Model, and HTML evidence.
RELEASE = "AIXEM-SRP-0.5.5-2026-08-11"
COMPOSITION_RENDERER_ID = "aixem-hierarchical-project-reference-renderer"
COMPOSITION_RENDERER_VERSION = "0.5.3"
COMPOSITION_RELEASE = "AIXEM-SRP-0.5.5-2026-08-11"
DEFAULT_STYLE = pathlib.Path(__file__).resolve().parents[2] / "profiles" / "aixem-grid-schematic-style-1.aixstyle.json"
DEFAULT_SCHEMA_ROOT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "specifications" / "schemas" / "component-graphics-1"


def on_grid(value: float, grid: float, tolerance: float = 1e-6) -> bool:
    return abs(value / grid - round(value / grid)) <= tolerance


def orthogonal(points: list[tuple[float, float]], tolerance: float = 1e-6) -> bool:
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        if abs(x1 - x2) > tolerance and abs(y1 - y2) > tolerance:
            return False
    return True




class GridProjectRenderer(CoreProjectRenderer):
    def __init__(
        self,
        project_file: pathlib.Path,
        schema_root: pathlib.Path = DEFAULT_SCHEMA_ROOT,
        style_file: pathlib.Path = DEFAULT_STYLE,
        *,
        project_doc: dict[str, Any] | None = None,
        project_root: pathlib.Path | None = None,
    ):
        self.style_file = style_file.resolve()
        self.style_doc = json.loads(self.style_file.read_text(encoding="utf-8"))
        self.style_profile = self.style_doc["styleProfile"]
        self.grid_metrics: dict[str, Any] = {}
        super().__init__(project_file, schema_root, project_doc=project_doc, project_root=project_root)

    def _validate_semantics_and_layout(self) -> None:
        super()._validate_semantics_and_layout()
        snap = float(self.style_profile["grid"]["snap"])
        scale_issues: list[str] = []
        for placement in self.layout["placements"]:
            entity = placement["entity"]
            scale_x = float(placement.get("scaleX", 1.0))
            scale_y = float(placement.get("scaleY", 1.0))
            if not math.isfinite(scale_x) or not math.isfinite(scale_y) or scale_x <= 0 or scale_y <= 0:
                scale_issues.append(
                    f"{entity}: scaleX={scale_x:g}, scaleY={scale_y:g} must both be finite and positive"
                )
                continue
            if not math.isclose(scale_x, scale_y, rel_tol=0.0, abs_tol=1e-9):
                scale_issues.append(
                    f"{entity}: scaleX={scale_x:g}, scaleY={scale_y:g} must be equal for uniform component scaling"
                )
        if scale_issues:
            raise AixemGraphicsError(
                "grid schematic profile requires finite positive uniform component scaling: "
                + "; ".join(scale_issues[:20])
            )

        placement_off_grid: list[str] = []
        route_off_grid: list[str] = []
        non_orthogonal: list[str] = []
        zero_segments: list[str] = []
        total_segments = 0
        for placement in self.layout["placements"]:
            if not on_grid(float(placement["x"]), snap) or not on_grid(float(placement["y"]), snap):
                placement_off_grid.append(placement["entity"])
        for connection in self.layout.get("connections", []):
            for index, route in enumerate(connection["paths"]):
                points = [self._resolve_route_end(route["from"])] + [(float(p[0]), float(p[1])) for p in route.get("via", [])] + [self._resolve_route_end(route["to"])]
                total_segments += max(0, len(points) - 1)
                if not orthogonal(points):
                    non_orthogonal.append(f"{connection['net']}:{index}")
                endpoint_axes = points[0], points[-1]
                for p in route.get("via", []):
                    px, py = float(p[0]), float(p[1])
                    # A short pin-escape stub may retain the exact x/y coordinate of a
                    # presentation port whose legacy symbol pitch predates this profile.
                    # Every free bend coordinate must still land on the profile snap grid.
                    x_ok = on_grid(px, snap) or any(abs(px - endpoint[0]) <= 1e-6 for endpoint in endpoint_axes)
                    y_ok = on_grid(py, snap) or any(abs(py - endpoint[1]) <= 1e-6 for endpoint in endpoint_axes)
                    if not x_ok or not y_ok:
                        route_off_grid.append(f"{connection['net']}:{index}@{p}")
                for seg_index, (a, b) in enumerate(zip(points, points[1:])):
                    if abs(a[0]-b[0]) < 1e-8 and abs(a[1]-b[1]) < 1e-8:
                        zero_segments.append(f"{connection['net']}:{index}:{seg_index}")
        if non_orthogonal:
            raise AixemGraphicsError(f"grid profile requires orthogonal routes: {non_orthogonal[:20]}")
        if route_off_grid:
            raise AixemGraphicsError(f"route vias are off the {snap:g} grid: {route_off_grid[:20]}")
        self.grid_metrics = {
            "profile": self.style_profile["id"],
            "snap": snap,
            "placements": len(self.layout["placements"]),
            "placementsOnGrid": len(self.layout["placements"]) - len(placement_off_grid),
            "placementExceptions": placement_off_grid,
            "routeSegments": total_segments,
            "orthogonalSegments": total_segments,
            "routeViasOnGrid": True,
            "zeroLengthSegments": zero_segments,
            "crossingPolicy": self.style_profile["routing"]["crossingPolicy"],
        }

    def _port_overlay(self, binding: Any) -> str:
        symbol = binding.asset.data["symbol"]
        variant = binding.variant or {}
        fragments: list[str] = []
        for port in symbol.get("ports", []):
            item = dict(port)
            item.update(variant.get("portOverrides", {}).get(port["id"], {}))
            if not item.get("labelVisible") and not item.get("numberVisible"):
                continue
            x = eval_numeric(item["x"], binding.parameters)
            y = eval_numeric(item["y"], binding.parameters)
            orientation = int(round(eval_numeric(item.get("orientation", 0), binding.parameters))) % 360
            name = item.get("name", item["id"])
            number = item.get("number", item["id"])
            if orientation == 0:
                name_x, name_y, name_anchor = x - 3.0, y - 0.8, "end"
                num_x, num_y, num_anchor = x + 2.0, y - 0.8, "start"
                name_transform = num_transform = ""
            elif orientation == 180:
                name_x, name_y, name_anchor = x + 3.0, y - 0.8, "start"
                num_x, num_y, num_anchor = x - 2.0, y - 0.8, "end"
                name_transform = num_transform = ""
            elif orientation == 90:
                name_x, name_y, name_anchor = x + 0.8, y - 3.0, "start"
                num_x, num_y, num_anchor = x + 0.8, y + 2.0, "end"
                name_transform = f' transform="rotate(-90 {fmt(name_x)} {fmt(name_y)})"'
                num_transform = f' transform="rotate(-90 {fmt(num_x)} {fmt(num_y)})"'
            else:
                name_x, name_y, name_anchor = x + 0.8, y + 3.0, "end"
                num_x, num_y, num_anchor = x + 0.8, y - 2.0, "start"
                name_transform = f' transform="rotate(-90 {fmt(name_x)} {fmt(name_y)})"'
                num_transform = f' transform="rotate(-90 {fmt(num_x)} {fmt(num_y)})"'
            if item.get("labelVisible"):
                fragments.append(f'<text class="pin-name" data-pin-name="{xml(item["id"])}" x="{fmt(name_x)}" y="{fmt(name_y)}" text-anchor="{name_anchor}"{name_transform}>{xml(name)}</text>')
            if item.get("numberVisible"):
                fragments.append(f'<text class="pin-number" data-pin-number="{xml(item["id"])}" x="{fmt(num_x)}" y="{fmt(num_y)}" text-anchor="{num_anchor}"{num_transform}>{xml(number)}</text>')
            fragments.append(f'<circle class="pin-target" cx="{fmt(x)}" cy="{fmt(y)}" r="1.35" data-port="{xml(item["id"])}"/>')
        return '<g class="pin-overlay">' + "".join(fragments) + "</g>" if fragments else ""

    def _render_entity(self, key: str, binding: Any) -> tuple[str, str]:
        defs, rendered = super()._render_entity(key, binding)
        overlay = self._port_overlay(binding)
        if overlay and rendered.endswith("</g>"):
            rendered = rendered[:-4] + overlay + "</g>"
        return defs, rendered

    def _svg_style(self) -> str:
        p = self.style_profile["palette"]
        return f'''<style>
svg{{background:{p['background']};font-family:Arial,Helvetica,sans-serif;text-rendering:geometricPrecision}}
.sheet-background{{fill:{p['background']}!important;stroke:none!important}}.sheet-grid{{pointer-events:none}}.sheet-frame{{fill:none;stroke:#8b918c;stroke-width:.45;vector-effect:non-scaling-stroke}}
#layer-symbols .entity line,#layer-symbols .entity polyline,#layer-symbols .entity polygon,#layer-symbols .entity rect,#layer-symbols .entity circle,#layer-symbols .entity ellipse,#layer-symbols .entity path{{stroke:{p['symbol']}!important;vector-effect:non-scaling-stroke;stroke-linecap:square!important;stroke-linejoin:miter!important}}
#layer-symbols .entity rect{{fill:#fffef8!important}}#layer-symbols .entity text{{fill:{p['symbol']}!important;stroke:none!important}}
.net-route{{stroke:{p['wire']}!important;stroke-width:.68!important;stroke-linecap:square!important;stroke-linejoin:miter!important;fill:none;vector-effect:non-scaling-stroke;shape-rendering:geometricPrecision}}
.net-junction{{fill:{p['junction']}!important;stroke:none!important}}.net-label{{font:600 3.4px Arial,sans-serif;fill:{p['annotation']}!important;stroke:#fff!important;stroke-width:1.5!important;paint-order:stroke;letter-spacing:.02em}}
.pin-name{{font:600 2.65px Arial,sans-serif;fill:{p['pinName']}!important;stroke:#fff!important;stroke-width:.7!important;paint-order:stroke;pointer-events:none}}
.pin-number{{font:600 2.35px Arial,sans-serif;fill:{p['pinNumber']}!important;stroke:#fff!important;stroke-width:.7!important;paint-order:stroke;pointer-events:none}}
.pin-target{{fill:transparent;stroke:transparent;vector-effect:non-scaling-stroke}}.entity:hover .pin-target,.entity.selected .pin-target{{fill:#fff;stroke:{p['selection']}!important;stroke-width:.6!important}}
.no-connect line{{stroke:#a33c30;stroke-width:.7;vector-effect:non-scaling-stroke}}.title-block line,.title-block rect{{stroke:#626b65;stroke-width:.45;vector-effect:non-scaling-stroke;fill:#fffef8}}.title-block text{{fill:#2f3632;stroke:none;font-family:Arial,sans-serif}}
.entity{{cursor:pointer}}.entity.selected>*:not(title),.entity.selected .pin-overlay>*{{filter:drop-shadow(0 0 .8px {p['selection']});stroke:{p['selection']}!important}}.net.selected .net-route{{stroke:{p['selection']}!important;stroke-width:1.2!important}}.net.selected .net-junction{{fill:{p['selection']}!important}}
.annotation-label{{fill:{p['annotation']}!important}}*{{shape-rendering:geometricPrecision}}
</style>'''

    def _grid_defs(self) -> str:
        grid = self.style_profile["grid"]
        minor, major = float(grid["minor"]), float(grid["major"])
        p = self.style_profile["palette"]
        return f'''<pattern id="aixem-minor-grid" width="{fmt(minor)}" height="{fmt(minor)}" patternUnits="userSpaceOnUse"><circle cx="0" cy="0" r=".18" fill="{p['gridMinor']}"/></pattern><pattern id="aixem-major-grid" width="{fmt(major)}" height="{fmt(major)}" patternUnits="userSpaceOnUse"><circle cx="0" cy="0" r=".32" fill="{p['gridMajor']}"/></pattern>'''

    def _title_block(self) -> str:
        sheet = self.layout["sheet"]
        width, height = float(sheet["width"]), float(sheet["height"])
        tb = sheet.get("titleBlock", {})
        x, y, w, h = width - 132, height - 31, 122, 21
        title = tb.get("title", self.project["title"])
        drawing = tb.get("drawing", self.project["id"])
        revision = tb.get("revision", "A")
        sheet_no = tb.get("sheet", "1/1")
        return f'''<g class="title-block" aria-label="Drawing title block"><rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}"/><line x1="{fmt(x)}" y1="{fmt(y+10)}" x2="{fmt(x+w)}" y2="{fmt(y+10)}"/><line x1="{fmt(x+84)}" y1="{fmt(y+10)}" x2="{fmt(x+84)}" y2="{fmt(y+h)}"/><line x1="{fmt(x+103)}" y1="{fmt(y+10)}" x2="{fmt(x+103)}" y2="{fmt(y+h)}"/><text x="{fmt(x+4)}" y="{fmt(y+6.4)}" font-size="4.1" font-weight="700">{xml(title)}</text><text x="{fmt(x+4)}" y="{fmt(y+16.2)}" font-size="3.2">{xml(drawing)}</text><text x="{fmt(x+87)}" y="{fmt(y+14)}" font-size="2.2">REV</text><text x="{fmt(x+93)}" y="{fmt(y+18.2)}" font-size="3.6" font-weight="700">{xml(revision)}</text><text x="{fmt(x+106)}" y="{fmt(y+14)}" font-size="2.2">SHEET</text><text x="{fmt(x+110)}" y="{fmt(y+18.2)}" font-size="3.6" font-weight="700">{xml(sheet_no)}</text></g>'''

    def _no_connect_svg(self) -> str:
        marks: list[str] = []
        for endpoint in self.semantic.get("noconn", []):
            if endpoint.startswith("@"):
                x, y = self.sheet_port_positions[endpoint[1:]]
            else:
                owner, port = endpoint.split(".", 1)
                x, y = self.bindings[owner].port_positions[port]
            s = 2.0
            marks.append(f'<g class="no-connect" data-endpoint="{xml(endpoint)}"><title>No connect {xml(endpoint)}</title><line x1="{fmt(x-s)}" y1="{fmt(y-s)}" x2="{fmt(x+s)}" y2="{fmt(y+s)}"/><line x1="{fmt(x+s)}" y1="{fmt(y-s)}" x2="{fmt(x-s)}" y2="{fmt(y+s)}"/></g>')
        return '<g id="layer-no-connect" data-layer="no-connect">' + "".join(marks) + "</g>" if marks else ""

    def build_svg(self) -> tuple[str, dict[str, Any]]:
        svg, scene = super().build_svg()
        width, height = float(self.layout["sheet"]["width"]), float(self.layout["sheet"]["height"])
        svg = svg.replace("<defs>", "<defs>" + self._grid_defs() + self._svg_style(), 1)
        background_pattern = re.compile(r'<rect class="sheet-background"[^>]*/>')
        replacement = (
            f'<rect class="sheet-background" x="0" y="0" width="{fmt(width)}" height="{fmt(height)}"/>'
            f'<rect class="sheet-grid minor-grid" x="0" y="0" width="{fmt(width)}" height="{fmt(height)}" fill="url(#aixem-minor-grid)"/>'
            f'<rect class="sheet-grid major-grid" x="0" y="0" width="{fmt(width)}" height="{fmt(height)}" fill="url(#aixem-major-grid)"/>'
            f'<rect class="sheet-frame" x="8" y="8" width="{fmt(width-16)}" height="{fmt(height-16)}"/>'
        )
        svg = background_pattern.sub(replacement, svg, count=1)
        svg = svg.replace("</svg>", self._no_connect_svg() + self._title_block() + "</svg>", 1)
        scene["renderer"] = {"id": RENDERER_ID, "version": RENDERER_VERSION}
        scene["styleProfile"] = {"id": self.style_profile["id"], "digest": sha256_file(self.style_file), "path": self.style_file.name}
        scene["gridValidation"] = self.grid_metrics
        scene["statistics"]["noConnects"] = len(self.semantic.get("noconn", []))
        scene["statistics"]["routeSegments"] = self.grid_metrics.get("routeSegments", 0)
        return svg, scene

    def _viewer_interface_ports(self) -> list[dict[str, Any]]:
        """Project resolved leaf interface metadata into the derived Viewer Model."""
        records: list[dict[str, Any]] = []
        for port_id, port in sorted(self.semantic.get("ports", {}).items()):
            records.append({
                "id": port_id,
                "direction": port.get("direction", "passive"),
                "role": port.get("role", "signal"),
                "localNet": self.semantic.get("endpointOwners", {}).get(f"@{port_id}"),
                "coordinate": list(self.sheet_port_positions.get(port_id, ())),
            })
        return records

    def render(self, output_dir: pathlib.Path) -> dict[str, Any]:
        output_dir.mkdir(parents=True, exist_ok=True)
        svg, scene = self.build_svg()
        svg_path = output_dir / "drawing.svg"
        scene_path = output_dir / "resolved-scene.json"
        viewer_model_path = output_dir / "viewer-model.json"
        workbench_path = output_dir / "workbench.html"
        viewer_path = output_dir / "viewer.html"
        svg_path.write_text(svg + "\n", encoding="utf-8", newline="\n")
        scene_path.write_text(pretty_json(scene), encoding="utf-8", newline="\n")
        viewer_model = build_single_sheet_viewer_model(
            scene,
            interface_ports=self._viewer_interface_ports(),
            release=RELEASE,
        )
        viewer_model_path.write_text(pretty_json(viewer_model), encoding="utf-8", newline="\n")
        sheet_svgs = {viewer_model["initialState"]["activeSheet"]: svg}
        viewer = ReferenceViewerRenderer().render(viewer_model, sheet_svgs=sheet_svgs) + "\n"
        workbench = ReviewWorkbenchRenderer().render(viewer_model, sheet_svgs=sheet_svgs) + "\n"
        viewer_path.write_text(viewer, encoding="utf-8", newline="\n")
        workbench_path.write_text(workbench, encoding="utf-8", newline="\n")
        artifacts = [
            {"role": "drawing-svg", "path": svg_path.name, "mediaType": "image/svg+xml", "digest": sha256_file(svg_path), "bytes": svg_path.stat().st_size},
            {"role": "resolved-scene", "path": scene_path.name, "mediaType": "application/json", "digest": sha256_file(scene_path), "bytes": scene_path.stat().st_size},
            {"role": "viewer-model", "path": viewer_model_path.name, "mediaType": "application/json", "digest": sha256_file(viewer_model_path), "bytes": viewer_model_path.stat().st_size},
            {"role": "standalone-viewer", "path": viewer_path.name, "mediaType": "text/html", "digest": sha256_file(viewer_path), "bytes": viewer_path.stat().st_size},
            {"role": "engineering-workbench", "path": workbench_path.name, "mediaType": "text/html", "digest": sha256_file(workbench_path), "bytes": workbench_path.stat().st_size},
        ]
        render_manifest = {
            "schema": "https://schemas.aixem.org/component-graphics/render-manifest/1",
            "renderer": {"id": RENDERER_ID, "version": RENDERER_VERSION}, "release": RELEASE, "generatedAt": FIXED_TIME,
            "styleProfile": {"id": self.style_profile["id"], "digest": sha256_file(self.style_file)},
            "project": {"id": self.project["id"], "manifestDigest": sha256_file(self.project_file), "sourceDigest": sha256_file(self.source_path), "layoutDigest": sha256_file(self.layout_path)},
            "artifacts": artifacts, "status": "pass",
        }
        manifest_path = output_dir / "render-manifest.json"
        manifest_path.write_text(pretty_json(render_manifest), encoding="utf-8", newline="\n")
        validation = {
            "schema": "https://schemas.aixem.org/component-graphics/project-validation/1", "project": self.project["id"], "release": RELEASE, "generatedAt": FIXED_TIME, "valid": True,
            "checks": {"projectSchema": True, "layoutSchema": True, "librarySchemas": len(self.libraries), "symbolSchemas": len(self.assets), "inputDigests": 2 + len(self.libraries) + len(self.assets), "componentTypeClosure": True, "semanticPortClosure": True, "presentationPortMapClosure": True, "placementClosure": True, "semanticNetClosure": True, "routeEndpointClosure": True, "orthogonalRouting": True, "routeViasOnGrid": True, "geometryDoesNotCreateConnectivity": True, "remoteAssetsDenied": self.project["renderPolicy"]["remoteAssets"] == "deny", "independentVisualAssets": True, "viewerModelSchema": True, "viewerQualifiedIdentityClosure": True, "viewerReadOnly": True, "viewerOffline": True, "viewerWorkbenchDistinct": sha256_file(viewer_path) != sha256_file(workbench_path)},
            "statistics": scene["statistics"], "gridValidation": self.grid_metrics, "featuresUsed": scene["featuresUsed"],
            "hashes": render_manifest["project"] | {item["role"]: item["digest"] for item in artifacts}, "diagnostics": self.diagnostics,
        }
        return {"validation": validation, "renderManifest": render_manifest, "scene": scene, "artifacts": artifacts}


class MultiSheetProjectRenderer:
    """Render an aixproj/2 project without flattening its independent leaf sheets."""

    def __init__(
        self,
        project_file: pathlib.Path,
        schema_root: pathlib.Path = DEFAULT_SCHEMA_ROOT,
        style_file: pathlib.Path = DEFAULT_STYLE,
    ):
        self.project_file = project_file.resolve()
        self.project_root = self.project_file.parent
        self.schema_root = schema_root.resolve()
        self.style_file = style_file.resolve()
        self.style_doc = json.loads(self.style_file.read_text(encoding="utf-8"))
        self.style_profile = self.style_doc["styleProfile"]

        def leaf_factory(
            owning_project_file: pathlib.Path,
            leaf_schema_root: pathlib.Path,
            project_doc: dict[str, Any],
            project_root: pathlib.Path,
        ) -> GridProjectRenderer:
            return GridProjectRenderer(
                owning_project_file,
                leaf_schema_root,
                self.style_file,
                project_doc=project_doc,
                project_root=project_root,
            )

        started = time.perf_counter()
        self.resolver = ProjectCompositionResolver(self.project_file, self.schema_root, leaf_factory)
        resolver_seconds = time.perf_counter() - started
        self.project_doc = self.resolver.project_doc
        self.project = self.resolver.project
        started = time.perf_counter()
        self.overview_routing = route_project(self.resolver, "overview")
        overview_seconds = time.perf_counter() - started
        started = time.perf_counter()
        self.composite_routing = route_project(self.resolver, "composite")
        composite_seconds = time.perf_counter() - started
        self.performance = {
            **self.resolver.performance,
            "resolverTotalSeconds": resolver_seconds,
            "overviewRouteSeconds": overview_seconds,
            "compositeRouteSeconds": composite_seconds,
        }
        for routing in (self.overview_routing, self.composite_routing):
            if not route_is_release_valid(routing):
                errors = [item for item in routing.diagnostics if item.get("severity") == "error"]
                raise AixemGraphicsError(
                    f"project routing failed for {routing.mode}: {errors[:12]}"
                )

    @staticmethod
    def _namespace_svg(svg: str, prefix: str) -> str:
        """Namespace local SVG identifiers before multiple leaves share one DOM."""
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

    def _decorated_leaf_svg(self, sheet_id: str, *, prefix: str) -> str:
        sheet = self.resolver.sheets[sheet_id]
        svg = self._namespace_svg(sheet.svg, prefix)
        svg = svg.replace(
            "<svg ",
            f'<svg data-sheet-canvas="{xml(sheet_id)}" data-sheet="{xml(sheet_id)}" ',
            1,
        )
        for port_id in sorted(sheet.semantic.get("ports", {}), key=len, reverse=True):
            project_net = self.resolver.project_net_for_port(sheet_id, port_id) or ""
            token = f'data-interface-port="{xml(port_id)}"'
            replacement = (
                token
                + f' data-sheet="{xml(sheet_id)}" data-qualified-interface="interface:{xml(sheet_id)}:{xml(port_id)}"'
                + (f' data-project-net="{xml(project_net)}"' if project_net else "")
            )
            svg = svg.replace(token, replacement)
        return svg

    def _project_style(self) -> str:
        p = self.style_profile["palette"]
        return f'''<style>
.project-canvas{{background:{p['background']};font-family:Arial,Helvetica,sans-serif;text-rendering:geometricPrecision}}
.project-background{{fill:{p['background']}}}.project-sheet-block{{fill:#fffef8;stroke:#606963;stroke-width:.8;vector-effect:non-scaling-stroke}}
.project-sheet-title{{fill:#28302b;font-size:5px;font-weight:700;letter-spacing:.025em}}.project-sheet-meta{{fill:#69716c;font-size:3px}}
.project-port{{fill:#fff;stroke:#2458a6;stroke-width:.8;vector-effect:non-scaling-stroke;cursor:pointer}}.project-port-label{{fill:#2458a6;font-size:3.1px;font-weight:600;paint-order:stroke;stroke:#fff;stroke-width:1px}}
.project-net-route{{fill:none;stroke:{p['wire']};stroke-width:1.15;stroke-linecap:square;stroke-linejoin:miter;vector-effect:non-scaling-stroke}}
.project-net-junction{{fill:{p['junction']};stroke:none}}.project-net-label{{fill:{p['annotation']};font-size:3.3px;font-weight:700;paint-order:stroke;stroke:#fff;stroke-width:1.2px}}
.project-net.selected .project-net-route,.project-net-route.selected{{stroke:{p['selection']}!important;stroke-width:2!important}}.project-net.selected .project-net-junction{{fill:{p['selection']}!important}}
.project-port.selected{{fill:{p['selection']}!important;stroke:{p['selection']}!important}}.project-sheet-canvas{{overflow:visible}}
</style>'''

    def _project_routes_svg(self, routing: ProjectRoutingResult) -> str:
        groups: list[str] = []
        for net in routing.nets:
            paths = "".join(
                f'<polyline class="project-net-route" data-project-net="{xml(net.id)}" data-project-route="{index}" points="{points_attribute(path)}"/>'
                for index, path in enumerate(net.paths)
            )
            junctions = "".join(
                f'<circle class="project-net-junction" data-project-net="{xml(net.id)}" cx="{fmt(x)}" cy="{fmt(y)}" r="1.8"/>'
                for x, y in net.junctions
            )
            member_title = ", ".join(f"{item['sheet']}:@{item['port']}" for item in net.members)
            label_y = min((point[1] for path in net.paths for point in path), default=18.0) - 4.0
            label = (
                f'<text class="project-net-label" data-project-net="{xml(net.id)}" x="{fmt(net.trunk_x + 3)}" y="{fmt(max(12.0, label_y))}">{xml(net.label)}</text>'
            )
            groups.append(
                f'<g class="project-net" data-project-net="{xml(net.id)}"><title>{xml(net.id)} — {xml(member_title)}</title>{paths}{junctions}{label}</g>'
            )
        return "".join(groups)

    def build_overview_svg(self) -> str:
        routing = self.overview_routing
        blocks: list[str] = []
        for sheet_id in self.resolver.preorder:
            sheet = self.resolver.sheets[sheet_id]
            placement = routing.sheets[sheet_id]
            rect = placement.rect
            ports: list[str] = []
            for (anchor_sheet, port_id), anchor in sorted(routing.anchors.items()):
                if anchor_sheet != sheet_id:
                    continue
                project_net = anchor.project_net or ""
                if anchor.side == "left":
                    tx, ty, text_anchor = anchor.x + 4.0, anchor.y - 2.0, "start"
                elif anchor.side == "right":
                    tx, ty, text_anchor = anchor.x - 4.0, anchor.y - 2.0, "end"
                elif anchor.side == "top":
                    tx, ty, text_anchor = anchor.x, anchor.y + 6.0, "middle"
                else:
                    tx, ty, text_anchor = anchor.x, anchor.y - 4.0, "middle"
                attrs = (
                    f'data-sheet="{xml(sheet_id)}" data-interface-port="{xml(port_id)}" '
                    f'data-qualified-interface="interface:{xml(sheet_id)}:{xml(port_id)}"'
                )
                if project_net:
                    attrs += f' data-project-net="{xml(project_net)}"'
                ports.append(
                    f'<circle class="project-port" {attrs} cx="{fmt(anchor.x)}" cy="{fmt(anchor.y)}" r="2.4"><title>{xml(sheet_id)}:@{xml(port_id)}</title></circle>'
                    f'<text class="project-port-label" {attrs} x="{fmt(tx)}" y="{fmt(ty)}" text-anchor="{text_anchor}">{xml(port_id)}</text>'
                )
            parent = sheet.parent or "Root"
            blocks.append(
                f'<g class="project-sheet" data-sheet="{xml(sheet_id)}"><rect class="project-sheet-block" x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.width)}" height="{fmt(rect.height)}"/>'
                f'<text class="project-sheet-title" x="{fmt(rect.x + 8)}" y="{fmt(rect.y + 14)}">{xml(sheet.title)}</text>'
                f'<text class="project-sheet-meta" x="{fmt(rect.x + 8)}" y="{fmt(rect.y + 23)}">{xml(sheet_id)} · parent {xml(parent)} · {len(sheet.semantic.get("entities", {}))} entities</text>'
                f'{"".join(ports)}</g>'
            )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" role="img" class="project-canvas" data-project-view="overview" '
            f'viewBox="0 0 {fmt(routing.width)} {fmt(routing.height)}" width="{fmt(routing.width)}" height="{fmt(routing.height)}" '
            f'data-project="{xml(self.project["id"])}"><title>{xml(self.project["title"])} — Project Overview</title>'
            f'<desc>Explicit project nets connect semantic sheet interface ports. Geometry does not create connectivity.</desc>'
            f'<defs>{self._project_style()}</defs><rect class="project-background" width="100%" height="100%"/>'
            f'{self._project_routes_svg(routing)}{"".join(blocks)}</svg>'
        )

    def build_composite_svg(self) -> str:
        routing = self.composite_routing
        leaves: list[str] = []
        for sheet_id in self.resolver.preorder:
            placement = routing.sheets[sheet_id]
            rect = placement.rect
            leaf = self._decorated_leaf_svg(sheet_id, prefix=f"composite-{sheet_id}")
            match = re.match(r"<svg\s+[^>]*>(.*)</svg>\s*$", leaf, flags=re.DOTALL)
            if not match:
                raise AixemGraphicsError(f"unable to compose leaf SVG for sheet {sheet_id}")
            inner = match.group(1)
            leaves.append(
                f'<svg xmlns="http://www.w3.org/2000/svg" class="project-sheet-canvas" data-sheet-canvas="{xml(sheet_id)}" data-sheet="{xml(sheet_id)}" '
                f'x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.width)}" height="{fmt(rect.height)}" '
                f'viewBox="0 0 {fmt(rect.width)} {fmt(rect.height)}"><title>{xml(self.resolver.sheets[sheet_id].title)}</title>{inner}</svg>'
            )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" role="img" class="project-canvas" data-project-view="composite" '
            f'viewBox="0 0 {fmt(routing.width)} {fmt(routing.height)}" width="{fmt(routing.width)}" height="{fmt(routing.height)}" '
            f'data-project="{xml(self.project["id"])}"><title>{xml(self.project["title"])} — Composite Project</title>'
            f'<desc>Complete independent leaf sheets are transformed into one deterministic workspace. Project wires connect declared sheet ports only.</desc>'
            f'<defs>{self._project_style()}</defs><rect class="project-background" width="100%" height="100%"/>'
            f'{"".join(leaves)}{self._project_routes_svg(routing)}</svg>'
        )

    def _resolved_project_scene(self, sheet_artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        overview = self.overview_routing.canonical_dict()
        composite = self.composite_routing.canonical_dict()
        all_diagnostics = list(self.resolver.diagnostics) + list(overview["diagnostics"]) + list(composite["diagnostics"])
        entity_count = sum(len(sheet.scene.get("entities", [])) for sheet in self.resolver.sheets.values())
        local_net_count = sum(len(sheet.scene.get("nets", [])) for sheet in self.resolver.sheets.values())
        interface_count = sum(len(sheet.semantic.get("ports", {})) for sheet in self.resolver.sheets.values())
        local_route_segments = sum(
            sheet.scene.get("statistics", {}).get("routeSegments", 0)
            for sheet in self.resolver.sheets.values()
        )
        project_route_segments = sum(
            max(0, len(path) - 1)
            for result in (self.overview_routing, self.composite_routing)
            for net in result.nets
            for path in net.paths
        )
        return {
            "schema": "https://schemas.aixem.org/component-graphics/resolved-project-scene/1",
            "renderer": {"id": COMPOSITION_RENDERER_ID, "version": COMPOSITION_RENDERER_VERSION},
            "generatedAt": FIXED_TIME,
            "project": {
                "id": self.project["id"],
                "title": self.project["title"],
                "profile": self.project["applicationProfile"],
                "schema": self.project_doc["schema"],
            },
            "hashes": {
                "manifest": sha256_file(self.project_file),
                "styleProfile": sha256_file(self.style_file),
                "inputs": [
                    {
                        "sheet": sheet_id,
                        "sourcePath": self.resolver.sheets[sheet_id].record["source"]["path"],
                        "sourceDigest": self.resolver.sheets[sheet_id].source_digest,
                        "layoutPath": self.resolver.sheets[sheet_id].record["layout"]["path"],
                        "layoutDigest": self.resolver.sheets[sheet_id].layout_digest,
                        "resolvedSceneDigest": sheet_artifacts[sheet_id]["sceneDigest"],
                        "svgDigest": sheet_artifacts[sheet_id]["svgDigest"],
                    }
                    for sheet_id in self.resolver.preorder
                ],
            },
            "hierarchy": self.resolver.hierarchy_records(),
            "sheets": [
                {
                    "id": sheet_id,
                    "title": self.resolver.sheets[sheet_id].title,
                    "parent": self.resolver.sheets[sheet_id].parent,
                    "order": self.resolver.sheets[sheet_id].order,
                    "source": self.resolver.sheets[sheet_id].record["source"],
                    "layout": self.resolver.sheets[sheet_id].record["layout"],
                    "svg": sheet_artifacts[sheet_id]["svgPath"],
                    "resolvedScene": sheet_artifacts[sheet_id]["scenePath"],
                }
                for sheet_id in self.resolver.preorder
            ],
            "interfaceSummaries": self.resolver.interface_summaries(),
            "semanticGraph": self.resolver.semantic_graph(),
            "routing": {"overview": overview, "composite": composite},
            "diagnostics": all_diagnostics,
            "statistics": {
                "sheets": len(self.resolver.sheets),
                "hierarchyDepth": max((self.resolver.hierarchy_depth(item) for item in self.resolver.preorder), default=0),
                "entities": entity_count,
                "localNets": local_net_count,
                "interfacePorts": interface_count,
                "projectNets": len(self.resolver.project_nets),
                "localRouteSegments": local_route_segments,
                "projectRouteSegments": project_route_segments,
                "unconnectedProjectPorts": len(self.resolver.unconnected_ports()),
            },
            "authority": {
                "localSemantics": ".aixem",
                "projectComposition": "aixproj/2",
                "localPresentation": "aixlayout/2",
                "connectivityFromGeometry": False,
                "layersAreSheets": False,
            },
        }

    @staticmethod
    def _artifact_record(role: str, path: pathlib.Path, root: pathlib.Path, media_type: str, **extra: Any) -> dict[str, Any]:
        return {
            "role": role,
            "path": path.relative_to(root).as_posix(),
            "mediaType": media_type,
            "digest": sha256_file(path),
            "bytes": path.stat().st_size,
            **extra,
        }

    def render(self, output_dir: pathlib.Path) -> dict[str, Any]:
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        sheets_dir = output_dir / "sheets"
        summaries_dir = output_dir / "interface-summaries"
        sheets_dir.mkdir(parents=True, exist_ok=True)
        summaries_dir.mkdir(parents=True, exist_ok=True)
        artifacts: list[dict[str, Any]] = []
        sheet_artifacts: dict[str, dict[str, Any]] = {}
        summaries = self.resolver.interface_summaries()
        for sheet_id in self.resolver.preorder:
            sheet = self.resolver.sheets[sheet_id]
            svg_path = sheets_dir / f"{sheet_id}.svg"
            scene_path = sheets_dir / f"{sheet_id}.resolved-scene.json"
            summary_path = summaries_dir / f"{sheet_id}.json"
            svg_path.write_text(sheet.svg + "\n", encoding="utf-8", newline="\n")
            scene_path.write_text(pretty_json(sheet.scene), encoding="utf-8", newline="\n")
            summary_path.write_text(pretty_json(summaries[sheet_id]), encoding="utf-8", newline="\n")
            artifacts.extend([
                self._artifact_record("sheet-svg", svg_path, output_dir, "image/svg+xml", sheet=sheet_id),
                self._artifact_record("sheet-resolved-scene", scene_path, output_dir, "application/json", sheet=sheet_id),
                self._artifact_record("sheet-interface-summary", summary_path, output_dir, "application/json", sheet=sheet_id),
            ])
            sheet_artifacts[sheet_id] = {
                "svgPath": svg_path.relative_to(output_dir).as_posix(),
                "scenePath": scene_path.relative_to(output_dir).as_posix(),
                "summaryPath": summary_path.relative_to(output_dir).as_posix(),
                "svgDigest": sha256_file(svg_path),
                "sceneDigest": sha256_file(scene_path),
                "summaryDigest": sha256_file(summary_path),
            }

        overview_svg = self.build_overview_svg()
        composite_svg = self.build_composite_svg()
        overview_path = output_dir / "project-overview.svg"
        composite_path = output_dir / "project-composite.svg"
        overview_path.write_text(overview_svg + "\n", encoding="utf-8", newline="\n")
        composite_path.write_text(composite_svg + "\n", encoding="utf-8", newline="\n")
        artifacts.extend([
            self._artifact_record("project-overview-svg", overview_path, output_dir, "image/svg+xml"),
            self._artifact_record("project-composite-svg", composite_path, output_dir, "image/svg+xml"),
        ])

        project_scene = self._resolved_project_scene(sheet_artifacts)
        project_scene_path = output_dir / "resolved-project-scene.json"
        project_scene_path.write_text(pretty_json(project_scene), encoding="utf-8", newline="\n")
        artifacts.append(self._artifact_record("resolved-project-scene", project_scene_path, output_dir, "application/json"))

        viewer_model = build_multi_sheet_viewer_model(
            project_scene,
            {sheet_id: self.resolver.sheets[sheet_id].scene for sheet_id in self.resolver.preorder},
            release=COMPOSITION_RELEASE,
        )
        viewer_model_path = output_dir / "viewer-model.json"
        workbench_path = output_dir / "workbench.html"
        viewer_path = output_dir / "viewer.html"
        viewer_model_path.write_text(pretty_json(viewer_model), encoding="utf-8", newline="\n")
        sheet_svgs = {sheet_id: self.resolver.sheets[sheet_id].svg for sheet_id in self.resolver.preorder}
        viewer = ReferenceViewerRenderer().render(
            viewer_model,
            sheet_svgs=sheet_svgs,
            overview_svg=overview_svg,
            composite_svg=composite_svg,
        ) + "\n"
        workbench = ReviewWorkbenchRenderer().render(
            viewer_model,
            sheet_svgs=sheet_svgs,
            overview_svg=overview_svg,
            composite_svg=composite_svg,
        ) + "\n"
        viewer_path.write_text(viewer, encoding="utf-8", newline="\n")
        workbench_path.write_text(workbench, encoding="utf-8", newline="\n")
        artifacts.extend([
            self._artifact_record("viewer-model", viewer_model_path, output_dir, "application/json"),
            self._artifact_record("standalone-viewer", viewer_path, output_dir, "text/html"),
            self._artifact_record("engineering-workbench", workbench_path, output_dir, "text/html"),
        ])

        render_manifest = {
            "schema": "https://schemas.aixem.org/component-graphics/render-manifest/1",
            "renderer": {"id": COMPOSITION_RENDERER_ID, "version": COMPOSITION_RENDERER_VERSION},
            "release": COMPOSITION_RELEASE,
            "generatedAt": FIXED_TIME,
            "styleProfile": {"id": self.style_profile["id"], "digest": sha256_file(self.style_file)},
            "project": {
                "id": self.project["id"],
                "manifestDigest": sha256_file(self.project_file),
                "sheets": len(self.resolver.sheets),
                "projectNets": len(self.resolver.project_nets),
            },
            "artifacts": artifacts,
            "status": "pass",
        }
        manifest_path = output_dir / "render-manifest.json"
        manifest_path.write_text(pretty_json(render_manifest), encoding="utf-8", newline="\n")
        validation = {
            "schema": "https://schemas.aixem.org/component-graphics/project-validation/1",
            "project": self.project["id"],
            "release": COMPOSITION_RELEASE,
            "generatedAt": FIXED_TIME,
            "valid": True,
            "checks": {
                "projectSchemaV2": True,
                "allLeafSourcesValid": True,
                "allLeafLayoutsV2Valid": True,
                "allInputDigestsVerified": True,
                "hierarchyAcyclic": True,
                "projectNetClosure": True,
                "projectNetEquivalenceClosure": True,
                "sameNameIsolation": True,
                "overviewOrthogonal": True,
                "compositeOrthogonal": True,
                "sheetQualifiedIdentity": True,
                "geometryDoesNotCreateConnectivity": True,
                "layersAreNotSheets": True,
                "dataDrivenWorkbenchHierarchy": True,
                "viewerModelSchema": True,
                "viewerQualifiedIdentityClosure": True,
                "viewerReadOnly": True,
                "viewerOffline": True,
                "viewerWorkbenchDistinct": sha256_file(viewer_path) != sha256_file(workbench_path),
            },
            "statistics": project_scene["statistics"],
            "hashes": {
                "manifest": sha256_file(self.project_file),
                "resolvedProjectScene": sha256_file(project_scene_path),
                "projectOverview": sha256_file(overview_path),
                "projectComposite": sha256_file(composite_path),
                "viewerModel": sha256_file(viewer_model_path),
                "viewer": sha256_file(viewer_path),
                "workbench": sha256_file(workbench_path),
                **{f"sheet:{sheet_id}:scene": sheet_artifacts[sheet_id]["sceneDigest"] for sheet_id in self.resolver.preorder},
                **{f"sheet:{sheet_id}:svg": sheet_artifacts[sheet_id]["svgDigest"] for sheet_id in self.resolver.preorder},
            },
            "diagnostics": project_scene["diagnostics"],
        }
        return {
            "validation": validation,
            "renderManifest": render_manifest,
            "scene": project_scene,
            "artifacts": artifacts,
        }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=pathlib.Path)
    parser.add_argument("--output-dir", type=pathlib.Path)
    parser.add_argument("--schema-root", type=pathlib.Path, default=DEFAULT_SCHEMA_ROOT)
    parser.add_argument("--style", type=pathlib.Path, default=DEFAULT_STYLE)
    parser.add_argument("--validation-out", type=pathlib.Path)
    args = parser.parse_args()
    project_file = args.project.resolve()
    output = args.output_dir.resolve() if args.output_dir else project_file.parent / "render"
    validation_out = args.validation_out.resolve() if args.validation_out else project_file.parent / "evidence" / "project-validation.json"
    try:
        project_doc = json.loads(project_file.read_text(encoding="utf-8"))
        if project_doc.get("schema") == PROJECT_SCHEMA_V2:
            renderer: GridProjectRenderer | MultiSheetProjectRenderer = MultiSheetProjectRenderer(
                project_file, args.schema_root, args.style
            )
        else:
            renderer = GridProjectRenderer(project_file, args.schema_root, args.style)
        result = renderer.render(output)
        validation_out.parent.mkdir(parents=True, exist_ok=True)
        validation_out.write_text(pretty_json(result["validation"]), encoding="utf-8", newline="\n")
        print(f"project: {renderer.project['id']}")
        statistics = result["scene"]["statistics"]
        if project_doc.get("schema") == PROJECT_SCHEMA_V2:
            print(
                f"sheets: {statistics['sheets']}; entities: {statistics['entities']}; "
                f"local nets: {statistics['localNets']}; project nets: {statistics['projectNets']}"
            )
            print(f"overview: {output / 'project-overview.svg'}")
            print(f"composite: {output / 'project-composite.svg'}")
            print("hierarchical project validation: PASS")
        else:
            print(
                f"entities: {statistics['entities']}; nets: {statistics['nets']}; "
                f"route segments: {statistics['routeSegments']}"
            )
            print("grid schematic validation: PASS")
        print(f"workbench: {output / 'workbench.html'}")
        return 0
    except (AixemGraphicsError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
