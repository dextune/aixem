#!/usr/bin/env python3
"""Deterministic orthogonal project routing for AIXEM overview and composite views."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from component_core import fmt  # type: ignore


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def contains_interior(self, x: float, y: float, epsilon: float = 1e-6) -> bool:
        return self.left + epsilon < x < self.right - epsilon and self.top + epsilon < y < self.bottom - epsilon


@dataclass
class SheetPlacement:
    sheet: str
    title: str
    depth: int
    rect: Rect
    transform: dict[str, float]


@dataclass
class PortAnchor:
    sheet: str
    port: str
    side: str
    x: float
    y: float
    local_net: str | None
    project_net: str | None
    direction: str
    role: str


@dataclass
class RoutedProjectNet:
    id: str
    label: str
    role: str | None
    members: list[dict[str, Any]]
    paths: list[list[tuple[float, float]]]
    junctions: list[tuple[float, float]]
    trunk_x: float


@dataclass
class ProjectRoutingResult:
    mode: str
    width: float
    height: float
    sheets: dict[str, SheetPlacement]
    anchors: dict[tuple[str, str], PortAnchor]
    nets: list[RoutedProjectNet]
    diagnostics: list[dict[str, Any]] = field(default_factory=list)

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "canvas": {"width": round(self.width, 6), "height": round(self.height, 6)},
            "sheets": [
                {
                    "id": item.sheet,
                    "title": item.title,
                    "depth": item.depth,
                    "rect": [round(item.rect.x, 6), round(item.rect.y, 6), round(item.rect.width, 6), round(item.rect.height, 6)],
                    "transform": {key: round(value, 6) for key, value in sorted(item.transform.items())},
                }
                for item in (self.sheets[key] for key in self.sheets)
            ],
            "anchors": [
                {
                    "sheet": anchor.sheet,
                    "port": anchor.port,
                    "side": anchor.side,
                    "point": [round(anchor.x, 6), round(anchor.y, 6)],
                    "localNet": anchor.local_net,
                    "projectNet": anchor.project_net,
                    "direction": anchor.direction,
                    "role": anchor.role,
                }
                for anchor in (self.anchors[key] for key in sorted(self.anchors))
            ],
            "nets": [
                {
                    "id": net.id,
                    "label": net.label,
                    "role": net.role,
                    "members": net.members,
                    "paths": [[[round(x, 6), round(y, 6)] for x, y in path] for path in net.paths],
                    "junctions": [[round(x, 6), round(y, 6)] for x, y in net.junctions],
                    "trunkX": round(net.trunk_x, 6),
                }
                for net in self.nets
            ],
            "diagnostics": self.diagnostics,
        }


def _overview_dimensions(resolver: Any, sheet_id: str) -> tuple[float, float]:
    sheet = resolver.sheets[sheet_id]
    side_counts = {side: 0 for side in ("left", "right", "top", "bottom")}
    for item in sheet.layout.get("sheetPorts", []):
        side_counts[item.get("side", "right")] += 1
    height = max(88.0, 42.0 + 16.0 * max(side_counts["left"], side_counts["right"], 1))
    width = max(180.0, 80.0 + 18.0 * max(side_counts["top"], side_counts["bottom"], 1))
    return width, height


def _distributed_positions(start: float, length: float, count: int, margin: float = 24.0) -> list[float]:
    if count <= 0:
        return []
    if count == 1:
        return [start + length / 2.0]
    usable = max(0.0, length - 2.0 * margin)
    return [start + margin + usable * index / (count - 1) for index in range(count)]


def place_overview(resolver: Any) -> tuple[dict[str, SheetPlacement], dict[tuple[str, str], PortAnchor]]:
    placements: dict[str, SheetPlacement] = {}
    anchors: dict[tuple[str, str], PortAnchor] = {}
    y = 50.0
    # Reserve deterministic left-side routing lanes for every project net so no
    # branch or label can escape the project canvas when ports face left.
    base_x = 70.0 + max(0, len(resolver.project_nets) - 1) * 10.0
    for sheet_id in resolver.preorder:
        depth = resolver.hierarchy_depth(sheet_id)
        width, height = _overview_dimensions(resolver, sheet_id)
        x = base_x + depth * 38.0
        rect = Rect(x=x, y=y, width=width, height=height)
        placements[sheet_id] = SheetPlacement(sheet=sheet_id, title=resolver.sheets[sheet_id].title, depth=depth, rect=rect, transform={"x": x, "y": y, "scale": 1.0})
        port_items = {side: [] for side in ("left", "right", "top", "bottom")}
        for item in resolver.sheets[sheet_id].layout.get("sheetPorts", []):
            port_items[item.get("side", "right")].append(item)
        for side in port_items:
            port_items[side].sort(key=lambda item: item["port"])
        vertical = {
            "left": _distributed_positions(rect.top, rect.height, len(port_items["left"]), 22.0),
            "right": _distributed_positions(rect.top, rect.height, len(port_items["right"]), 22.0),
        }
        horizontal = {
            "top": _distributed_positions(rect.left, rect.width, len(port_items["top"]), 28.0),
            "bottom": _distributed_positions(rect.left, rect.width, len(port_items["bottom"]), 28.0),
        }
        for side in ("left", "right"):
            for item, py in zip(port_items[side], vertical[side]):
                px = rect.left if side == "left" else rect.right
                port = resolver.sheets[sheet_id].semantic["ports"][item["port"]]
                anchors[(sheet_id, item["port"])] = PortAnchor(
                    sheet=sheet_id, port=item["port"], side=side, x=px, y=py,
                    local_net=resolver.local_net_for_port(sheet_id, item["port"]),
                    project_net=resolver.project_net_for_port(sheet_id, item["port"]),
                    direction=port["direction"], role=port["role"],
                )
        for side in ("top", "bottom"):
            for item, px in zip(port_items[side], horizontal[side]):
                py = rect.top if side == "top" else rect.bottom
                port = resolver.sheets[sheet_id].semantic["ports"][item["port"]]
                anchors[(sheet_id, item["port"])] = PortAnchor(
                    sheet=sheet_id, port=item["port"], side=side, x=px, y=py,
                    local_net=resolver.local_net_for_port(sheet_id, item["port"]),
                    project_net=resolver.project_net_for_port(sheet_id, item["port"]),
                    direction=port["direction"], role=port["role"],
                )
        y += height + 92.0
    return placements, anchors


def place_composite(resolver: Any) -> tuple[dict[str, SheetPlacement], dict[tuple[str, str], PortAnchor]]:
    placements: dict[str, SheetPlacement] = {}
    anchors: dict[tuple[str, str], PortAnchor] = {}
    y = 60.0
    project_net_count = max(1, len(resolver.project_nets))
    gap = 115.0 + min(project_net_count, 20) * 3.0
    base_x = 70.0 + max(0, len(resolver.project_nets) - 1) * 10.0
    for sheet_id in resolver.preorder:
        sheet = resolver.sheets[sheet_id]
        depth = resolver.hierarchy_depth(sheet_id)
        width = float(sheet.layout["sheet"]["width"])
        height = float(sheet.layout["sheet"]["height"])
        x = base_x + depth * 40.0
        rect = Rect(x=x, y=y, width=width, height=height)
        placements[sheet_id] = SheetPlacement(sheet=sheet_id, title=sheet.title, depth=depth, rect=rect, transform={"x": x, "y": y, "scale": 1.0})
        for item in sheet.layout.get("sheetPorts", []):
            local_x, local_y = sheet.renderer.sheet_port_positions[item["port"]]
            port = sheet.semantic["ports"][item["port"]]
            anchors[(sheet_id, item["port"])] = PortAnchor(
                sheet=sheet_id, port=item["port"], side=item.get("side", "right"),
                x=x + local_x, y=y + local_y,
                local_net=resolver.local_net_for_port(sheet_id, item["port"]),
                project_net=resolver.project_net_for_port(sheet_id, item["port"]),
                direction=port["direction"], role=port["role"],
            )
        y += height + gap
    return placements, anchors


def _clean_points(points: Iterable[tuple[float, float]]) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    for point in points:
        rounded = (round(float(point[0]), 6), round(float(point[1]), 6))
        if not result or result[-1] != rounded:
            result.append(rounded)
    return result


def _orthogonal(path: list[tuple[float, float]], epsilon: float = 1e-6) -> bool:
    return all(abs(a[0] - b[0]) <= epsilon or abs(a[1] - b[1]) <= epsilon for a, b in zip(path, path[1:]))


def _segment_hits_rect(a: tuple[float, float], b: tuple[float, float], rect: Rect, epsilon: float = 1e-6) -> bool:
    if abs(a[0] - b[0]) <= epsilon:
        x = a[0]
        y1, y2 = sorted((a[1], b[1]))
        return rect.left + epsilon < x < rect.right - epsilon and max(y1, rect.top + epsilon) < min(y2, rect.bottom - epsilon)
    if abs(a[1] - b[1]) <= epsilon:
        y = a[1]
        x1, x2 = sorted((a[0], b[0]))
        return rect.top + epsilon < y < rect.bottom - epsilon and max(x1, rect.left + epsilon) < min(x2, rect.right - epsilon)
    return True


def _branch_path(anchor: PortAnchor, rect: Rect, trunk_x: float, net_index: int, global_left: float) -> tuple[list[tuple[float, float]], tuple[float, float]]:
    escape = 14.0
    lane_delta = (net_index + 1) * 3.0
    if anchor.side == "right":
        escape_point = (rect.right + escape, anchor.y)
        attach_y = anchor.y + lane_delta
        points = [(anchor.x, anchor.y), escape_point, (escape_point[0], attach_y), (trunk_x, attach_y)]
    elif anchor.side == "top":
        escape_point = (anchor.x, rect.top - escape)
        attach_y = escape_point[1] - lane_delta
        points = [(anchor.x, anchor.y), escape_point, (anchor.x, attach_y), (trunk_x, attach_y)]
    elif anchor.side == "bottom":
        escape_point = (anchor.x, rect.bottom + escape)
        attach_y = escape_point[1] + lane_delta
        points = [(anchor.x, anchor.y), escape_point, (anchor.x, attach_y), (trunk_x, attach_y)]
    else:
        escape_point = (rect.left - escape, anchor.y)
        left_lane = global_left - net_index * 10.0
        attach_y = rect.top - 26.0 - lane_delta
        points = [
            (anchor.x, anchor.y), escape_point, (left_lane, anchor.y),
            (left_lane, attach_y), (trunk_x, attach_y),
        ]
    cleaned = _clean_points(points)
    return cleaned, cleaned[-1]


def route_project(resolver: Any, mode: str) -> ProjectRoutingResult:
    if mode == "overview":
        placements, anchors = place_overview(resolver)
    elif mode == "composite":
        placements, anchors = place_composite(resolver)
    else:
        raise ValueError(f"unsupported project routing mode {mode}")
    if not placements:
        return ProjectRoutingResult(mode=mode, width=200.0, height=120.0, sheets={}, anchors={}, nets=[])

    min_left = min(item.rect.left for item in placements.values())
    max_right = max(item.rect.right for item in placements.values())
    max_bottom = max(item.rect.bottom for item in placements.values())
    global_left = min_left - 48.0
    routed: list[RoutedProjectNet] = []
    diagnostics: list[dict[str, Any]] = []
    segment_owners: dict[tuple[tuple[float, float], tuple[float, float]], str] = {}

    for net_index, net_id in enumerate(sorted(resolver.project_nets)):
        net = resolver.project_nets[net_id]
        trunk_x = max_right + 70.0 + net_index * 24.0
        paths: list[list[tuple[float, float]]] = []
        attachments: list[tuple[float, float]] = []
        members: list[dict[str, Any]] = []
        for member in sorted(net.members, key=lambda item: (resolver.preorder.index(item.sheet), item.port)):
            key = (member.sheet, member.port)
            if key not in anchors:
                diagnostics.append({
                    "id": "PROJECT_ROUTE_UNRESOLVED_PORT", "severity": "error",
                    "projectNet": net_id, "member": f"{member.sheet}:@{member.port}",
                })
                continue
            anchor = anchors[key]
            path, attachment = _branch_path(anchor, placements[member.sheet].rect, trunk_x, net_index, global_left)
            paths.append(path)
            attachments.append(attachment)
            members.append({
                "sheet": member.sheet, "port": member.port, "localNet": member.local_net,
                "anchor": [round(anchor.x, 6), round(anchor.y, 6)], "side": anchor.side,
            })
        unique_y = sorted({point[1] for point in attachments})
        if len(unique_y) > 1:
            paths.append([(trunk_x, unique_y[0]), (trunk_x, unique_y[-1])])
        junctions = sorted(set(attachments), key=lambda item: (item[1], item[0]))
        routed_net = RoutedProjectNet(
            id=net_id, label=net.label, role=net.role, members=members,
            paths=paths, junctions=junctions, trunk_x=trunk_x,
        )
        routed.append(routed_net)

        for path_index, path in enumerate(paths):
            if not _orthogonal(path):
                diagnostics.append({"id": "PROJECT_ROUTE_NON_ORTHOGONAL", "severity": "error", "projectNet": net_id, "path": path_index})
            if len(path) - 2 > 6:
                diagnostics.append({"id": "PROJECT_ROUTE_EXCESSIVE_BENDS", "severity": "warning", "projectNet": net_id, "path": path_index, "bends": len(path) - 2})
            for segment_index, (a, b) in enumerate(zip(path, path[1:])):
                if a == b:
                    diagnostics.append({"id": "PROJECT_ROUTE_ZERO_LENGTH", "severity": "error", "projectNet": net_id, "path": path_index, "segment": segment_index})
                    continue
                normalized = tuple(sorted((a, b)))  # type: ignore[arg-type]
                prior = segment_owners.get(normalized)
                if prior and prior != net_id:
                    diagnostics.append({"id": "PROJECT_ROUTE_OVERLAP", "severity": "warning", "projectNet": net_id, "otherProjectNet": prior, "segment": [list(a), list(b)]})
                segment_owners[normalized] = net_id
                # The first segment of a branch is allowed to leave its owning sheet through the declared side.
                owner_sheet = members[path_index]["sheet"] if path_index < len(members) else None
                for sheet_id, placement in placements.items():
                    if segment_index == 0 and owner_sheet == sheet_id:
                        continue
                    if _segment_hits_rect(a, b, placement.rect):
                        diagnostics.append({
                            "id": "PROJECT_ROUTE_SHEET_INTERSECTION", "severity": "error",
                            "projectNet": net_id, "path": path_index, "segment": segment_index, "sheet": sheet_id,
                        })

    route_points = [point for net in routed for path in net.paths for point in path]
    min_x = min([placement.rect.left for placement in placements.values()] + [point[0] for point in route_points])
    max_trunk = max((net.trunk_x for net in routed), default=max_right)
    width = max_trunk + 65.0
    height = max_bottom + 60.0
    if min_x < 0:
        diagnostics.append({"id": "PROJECT_ROUTE_CANVAS_NEGATIVE_MARGIN", "severity": "error", "minimumX": round(min_x, 6)})
    return ProjectRoutingResult(
        mode=mode, width=width, height=height, sheets=placements, anchors=anchors,
        nets=routed, diagnostics=diagnostics,
    )


def route_is_release_valid(result: ProjectRoutingResult) -> bool:
    return not any(item.get("severity") == "error" for item in result.diagnostics)


def points_attribute(path: list[tuple[float, float]]) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in path)
