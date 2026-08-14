#!/usr/bin/env python3
"""Deterministic AIXEM project-composition resolver for aixproj/2.

The resolver preserves leaf authority: each .aixem/.aixlayout pair is validated by the
production leaf renderer, while this module owns only sheet hierarchy, explicit project
nets, qualified identities, provenance, and project-level semantic queries.
"""
from __future__ import annotations

from dataclasses import dataclass
import pathlib
import time
from typing import Any, Callable, Iterable

from component_core import (  # type: ignore
    AixemGraphicsError,
    canonical_json_bytes,
    load_json,
    sha256_bytes,
    sha256_file,
    validate_declared_json,
    verify_ref,
    safe_resolve,
)

PROJECT_SCHEMA_V2 = "https://schemas.aixem.org/component-graphics/aixproj/2"
LAYOUT_SCHEMA_V2 = "https://schemas.aixem.org/component-graphics/aixlayout/2"


def project_error(code: str, message: str) -> AixemGraphicsError:
    return AixemGraphicsError(f"{code}: {message}")


@dataclass(frozen=True)
class ResolvedMember:
    sheet: str
    port: str
    local_net: str
    direction: str
    role: str

    @property
    def qualified_interface(self) -> str:
        return f"interface:{self.sheet}:{self.port}"

    @property
    def qualified_local_net(self) -> str:
        return f"local-net:{self.sheet}:{self.local_net}"


@dataclass
class ResolvedSheet:
    id: str
    title: str
    parent: str | None
    order: int | None
    record: dict[str, Any]
    source_path: pathlib.Path
    layout_path: pathlib.Path
    renderer: Any
    svg: str
    scene: dict[str, Any]

    @property
    def semantic(self) -> dict[str, Any]:
        return self.renderer.semantic

    @property
    def layout(self) -> dict[str, Any]:
        return self.renderer.layout

    @property
    def source_digest(self) -> str:
        return sha256_file(self.source_path)

    @property
    def layout_digest(self) -> str:
        return sha256_file(self.layout_path)

    @property
    def svg_digest(self) -> str:
        return sha256_bytes((self.svg + "\n").encode("utf-8"))

    @property
    def scene_digest(self) -> str:
        return sha256_bytes(canonical_json_bytes(self.scene))

    def local_net_for_port(self, port: str) -> str | None:
        return self.semantic.get("endpointOwners", {}).get(f"@{port}")


@dataclass
class ResolvedProjectNet:
    id: str
    label: str
    role: str | None
    members: list[ResolvedMember]
    metadata: dict[str, Any]


LeafFactory = Callable[[pathlib.Path, pathlib.Path, dict[str, Any], pathlib.Path], Any]


class ProjectCompositionResolver:
    """Load and close an immutable aixproj/2 project against production leaf scenes."""

    def __init__(self, project_file: pathlib.Path, schema_root: pathlib.Path, leaf_factory: LeafFactory):
        self.project_file = project_file.resolve()
        self.project_root = self.project_file.parent
        self.schema_root = schema_root.resolve()
        self.project_doc = load_json(self.project_file)
        validate_declared_json(self.project_doc, self.schema_root, "project")
        if self.project_doc.get("schema") != PROJECT_SCHEMA_V2:
            raise project_error("PROJECT_SCHEMA_UNSUPPORTED", "ProjectCompositionResolver requires aixproj/2")
        self.project = self.project_doc["project"]
        self.leaf_factory = leaf_factory
        self.sheets: dict[str, ResolvedSheet] = {}
        self.project_nets: dict[str, ResolvedProjectNet] = {}
        self.interface_owner: dict[tuple[str, str], str] = {}
        self.diagnostics: list[dict[str, Any]] = []
        self._hierarchy_children: dict[str | None, list[str]] = {}
        self._preorder: list[str] = []
        self.performance: dict[str, float] = {}

        started = time.perf_counter()
        self._verify_reference_consistency()
        self.performance["referenceVerificationSeconds"] = time.perf_counter() - started

        started = time.perf_counter()
        self._validate_hierarchy_records()
        self.performance["hierarchyValidationSeconds"] = time.perf_counter() - started

        started = time.perf_counter()
        self._resolve_sheets()
        self.performance["leafResolveSeconds"] = time.perf_counter() - started

        started = time.perf_counter()
        self._resolve_project_nets()
        self.performance["projectGraphResolveSeconds"] = time.perf_counter() - started

        started = time.perf_counter()
        self._build_hierarchy_order()
        self.performance["hierarchyOrderSeconds"] = time.perf_counter() - started

    def _all_file_refs(self) -> Iterable[tuple[str, dict[str, Any]]]:
        for index, ref in enumerate(self.project["libraries"]):
            yield f"library[{index}]", ref
        for sheet in self.project["sheets"]:
            yield f"sheet[{sheet['id']}].source", sheet["source"]
            yield f"sheet[{sheet['id']}].layout", sheet["layout"]

    def _verify_reference_consistency(self) -> None:
        # Reject contradictory lock declarations before reading file contents. This gives
        # a precise project-level diagnostic instead of whichever digest mismatch happens
        # to be encountered first.
        refs = list(self._all_file_refs())
        observed_by_path: dict[pathlib.Path, tuple[str, str]] = {}
        for label, ref in refs:
            path = safe_resolve(self.project_root, ref["path"])
            prior = observed_by_path.get(path)
            if prior and prior[0] != ref["digest"]:
                raise project_error(
                    "PROJECT_REFERENCE_DIGEST_CONFLICT",
                    f"{label} reuses {ref['path']} with digest {ref['digest']} but {prior[1]} declared {prior[0]}",
                )
            observed_by_path[path] = (ref["digest"], label)
        for label, ref in refs:
            verify_ref(self.project_root, ref, label)

    def _validate_hierarchy_records(self) -> None:
        records = self.project["sheets"]
        ids = [item["id"] for item in records]
        if len(ids) != len(set(ids)):
            raise project_error("PROJECT_DUPLICATE_SHEET", "sheet IDs must be unique")
        known = set(ids)
        for item in records:
            parent = item.get("parent")
            if parent == item["id"]:
                raise project_error("PROJECT_HIERARCHY_SELF_PARENT", f"sheet {item['id']} cannot parent itself")
            if parent and parent not in known:
                raise project_error("PROJECT_HIERARCHY_UNKNOWN_PARENT", f"sheet {item['id']} references unknown parent {parent}")
        visiting: set[str] = set()
        visited: set[str] = set()
        by_id = {item["id"]: item for item in records}

        def visit(sheet_id: str, chain: list[str]) -> None:
            if sheet_id in visiting:
                cycle = chain[chain.index(sheet_id):] + [sheet_id]
                raise project_error("PROJECT_HIERARCHY_CYCLE", " -> ".join(cycle))
            if sheet_id in visited:
                return
            visiting.add(sheet_id)
            parent = by_id[sheet_id].get("parent")
            if parent:
                visit(parent, chain + [parent])
            visiting.remove(sheet_id)
            visited.add(sheet_id)

        for sheet_id in sorted(known):
            visit(sheet_id, [sheet_id])

    def _synthetic_leaf_project(self, sheet: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema": "https://schemas.aixem.org/component-graphics/aixproj/1",
            "formatVersion": "1.0",
            "project": {
                "id": f"{self.project['id']}:{sheet['id']}",
                "title": sheet["title"],
                "applicationProfile": self.project["applicationProfile"],
                "source": sheet["source"],
                "layout": sheet["layout"],
                "libraries": self.project["libraries"],
                "renderPolicy": self.project["renderPolicy"],
                "features": sorted(set(self.project.get("features", [])) | {"hierarchical.interface@1", "explicit.layout@2"}),
                "status": self.project.get("status", "draft"),
                "metadata": {"derivedLeaf": True, "owningProject": self.project["id"], "sheet": sheet["id"]},
            },
        }

    def _resolve_sheets(self) -> None:
        for record in sorted(self.project["sheets"], key=lambda item: item["id"]):
            source_path = verify_ref(self.project_root, record["source"], f"sheet[{record['id']}].source")
            layout_path = verify_ref(self.project_root, record["layout"], f"sheet[{record['id']}].layout")
            layout_doc = load_json(layout_path)
            if layout_doc.get("schema") != LAYOUT_SCHEMA_V2:
                raise project_error(
                    "PROJECT_LAYOUT_VERSION_REQUIRED",
                    f"sheet {record['id']} must use aixlayout/2 in an aixproj/2 project",
                )
            renderer = self.leaf_factory(
                self.project_file,
                self.schema_root,
                self._synthetic_leaf_project(record),
                self.project_root,
            )
            svg, scene = renderer.build_svg()
            scene["sheetIdentity"] = {
                "id": record["id"],
                "title": record["title"],
                "parent": record.get("parent"),
                "order": record.get("order"),
                "owningProject": self.project["id"],
            }
            self.sheets[record["id"]] = ResolvedSheet(
                id=record["id"],
                title=record["title"],
                parent=record.get("parent"),
                order=record.get("order"),
                record=record,
                source_path=source_path,
                layout_path=layout_path,
                renderer=renderer,
                svg=svg,
                scene=scene,
            )

    def _resolve_project_nets(self) -> None:
        net_ids = [item["id"] for item in self.project.get("projectNets", [])]
        if len(net_ids) != len(set(net_ids)):
            raise project_error("PROJECT_DUPLICATE_NET", "project-net IDs must be unique")
        local_equivalence_owners: dict[tuple[str, str], set[str]] = {}
        for record in sorted(self.project.get("projectNets", []), key=lambda item: item["id"]):
            members: list[ResolvedMember] = []
            seen_members: set[tuple[str, str]] = set()
            for member in record["members"]:
                key = (member["sheet"], member["port"])
                if key in seen_members:
                    raise project_error("PROJECT_NET_DUPLICATE_MEMBER", f"project net {record['id']} repeats {key[0]}:@{key[1]}")
                seen_members.add(key)
                sheet = self.sheets.get(member["sheet"])
                if sheet is None:
                    raise project_error("PROJECT_NET_UNKNOWN_SHEET", f"project net {record['id']} references {member['sheet']}")
                port = sheet.semantic.get("ports", {}).get(member["port"])
                if port is None:
                    raise project_error(
                        "PROJECT_NET_UNKNOWN_INTERFACE_PORT",
                        f"project net {record['id']} references {member['sheet']}:@{member['port']}",
                    )
                local_net = sheet.local_net_for_port(member["port"])
                if local_net is None:
                    raise project_error(
                        "PROJECT_PORT_NOT_LOCALLY_CONNECTED",
                        f"{member['sheet']}:@{member['port']} is not owned by a local semantic net",
                    )
                prior = self.interface_owner.get(key)
                if prior is not None and prior != record["id"]:
                    raise project_error(
                        "PROJECT_NET_DUPLICATE_OWNERSHIP",
                        f"{member['sheet']}:@{member['port']} belongs to both {prior} and {record['id']}",
                    )
                self.interface_owner[key] = record["id"]
                local_equivalence_owners.setdefault((member["sheet"], local_net), set()).add(record["id"])
                members.append(
                    ResolvedMember(
                        sheet=member["sheet"], port=member["port"], local_net=local_net,
                        direction=port["direction"], role=port["role"],
                    )
                )
            if len(members) < 2:
                raise project_error("PROJECT_NET_TOO_FEW_MEMBERS", f"project net {record['id']} requires at least two members")
            outputs = [item for item in members if item.direction == "output"]
            if len(outputs) > 1:
                self.diagnostics.append({
                    "id": "PROJECT_PORT_DIRECTION_CONFLICT",
                    "severity": "warning",
                    "projectNet": record["id"],
                    "message": "Multiple output interface ports participate in one project net; P0 records but does not run full ERC.",
                })
            roles = sorted({item.role for item in members})
            if len(roles) > 1:
                self.diagnostics.append({
                    "id": "PROJECT_PORT_ROLE_MIX",
                    "severity": "warning",
                    "projectNet": record["id"],
                    "roles": roles,
                    "message": "Mixed interface roles are diagnostic-only in P0.",
                })
            self.project_nets[record["id"]] = ResolvedProjectNet(
                id=record["id"], label=record.get("label", record["id"]), role=record.get("role"),
                members=members, metadata=record.get("metadata", {}),
            )
        collisions = [
            (sheet, local_net, sorted(owners))
            for (sheet, local_net), owners in sorted(local_equivalence_owners.items())
            if len(owners) > 1
        ]
        if collisions:
            sheet, local_net, owners = collisions[0]
            raise project_error(
                "PROJECT_NET_EQUIVALENCE_COLLISION",
                f"local-net:{sheet}:{local_net} collapses project nets {owners}",
            )

    @staticmethod
    def _sort_key(sheet: ResolvedSheet) -> tuple[int, str]:
        return (sheet.order if sheet.order is not None else 2**31 - 1, sheet.id)

    def _build_hierarchy_order(self) -> None:
        children: dict[str | None, list[str]] = {}
        for sheet in self.sheets.values():
            children.setdefault(sheet.parent, []).append(sheet.id)
        for parent, ids in children.items():
            ids.sort(key=lambda sheet_id: self._sort_key(self.sheets[sheet_id]))
        self._hierarchy_children = children
        preorder: list[str] = []

        def append_subtree(sheet_id: str) -> None:
            preorder.append(sheet_id)
            for child in children.get(sheet_id, []):
                append_subtree(child)

        for root in children.get(None, []):
            append_subtree(root)
        self._preorder = preorder

    @property
    def preorder(self) -> list[str]:
        return list(self._preorder)

    def hierarchy_depth(self, sheet_id: str) -> int:
        depth = 0
        current = self.sheets[sheet_id]
        while current.parent is not None:
            depth += 1
            current = self.sheets[current.parent]
        return depth

    def hierarchy_records(self) -> list[dict[str, Any]]:
        return [
            {
                "id": sheet_id,
                "title": self.sheets[sheet_id].title,
                "parent": self.sheets[sheet_id].parent,
                "order": self.sheets[sheet_id].order,
                "depth": self.hierarchy_depth(sheet_id),
                "children": list(self._hierarchy_children.get(sheet_id, [])),
            }
            for sheet_id in self._preorder
        ]

    def project_net_for_port(self, sheet: str, port: str) -> str | None:
        return self.interface_owner.get((sheet, port))

    def local_net_for_port(self, sheet: str, port: str) -> str | None:
        target = self.sheets.get(sheet)
        return target.local_net_for_port(port) if target else None

    def participating_sheets(self, project_net: str) -> list[str]:
        net = self.project_nets[project_net]
        return sorted({member.sheet for member in net.members}, key=lambda item: self._preorder.index(item))

    def transitive_endpoints(self, project_net: str) -> list[str]:
        result: set[str] = set()
        for member in self.project_nets[project_net].members:
            sheet = self.sheets[member.sheet]
            for endpoint in sheet.semantic["nets"][member.local_net]:
                if endpoint.startswith("@"):
                    result.add(f"interface:{member.sheet}:{endpoint[1:]}")
                else:
                    result.add(f"entity:{member.sheet}:{endpoint}")
        return sorted(result)

    def unconnected_ports(self) -> list[str]:
        result: list[str] = []
        for sheet_id in self._preorder:
            sheet = self.sheets[sheet_id]
            for port_id in sorted(sheet.semantic.get("ports", {})):
                if (sheet_id, port_id) not in self.interface_owner:
                    result.append(f"interface:{sheet_id}:{port_id}")
        return result

    def project_net_crosses_hierarchy_boundary(self, project_net: str) -> bool:
        # Every cross-sheet project net crosses at least one sheet/hierarchy boundary.
        # Parent relations remain organizational and never create connectivity.
        return len({member.sheet for member in self.project_nets[project_net].members}) > 1

    def interface_summaries(self) -> dict[str, dict[str, Any]]:
        summaries: dict[str, dict[str, Any]] = {}
        for sheet_id in self._preorder:
            sheet = self.sheets[sheet_id]
            ports = []
            for port_id, port in sorted(sheet.semantic.get("ports", {}).items()):
                ports.append({
                    "id": port_id,
                    "direction": port["direction"],
                    "role": port["role"],
                    "localNet": sheet.local_net_for_port(port_id),
                    "projectNet": self.project_net_for_port(sheet_id, port_id),
                })
            summaries[sheet_id] = {
                "sheet": sheet_id,
                "title": sheet.title,
                "sourceDigest": sheet.source_digest,
                "layoutDigest": sheet.layout_digest,
                "ports": ports,
            }
        return summaries

    def semantic_graph(self) -> dict[str, Any]:
        return {
            "identities": {
                "sheets": [f"sheet:{sheet_id}" for sheet_id in self._preorder],
                "interfaces": [
                    f"interface:{sheet_id}:{port_id}"
                    for sheet_id in self._preorder
                    for port_id in sorted(self.sheets[sheet_id].semantic.get("ports", {}))
                ],
                "projectNets": [f"project-net:{net_id}" for net_id in sorted(self.project_nets)],
            },
            "projectNets": [
                {
                    "id": net.id,
                    "qualifiedId": f"project-net:{net.id}",
                    "members": [
                        {
                            "sheet": member.sheet,
                            "port": member.port,
                            "interface": member.qualified_interface,
                            "localNet": member.local_net,
                            "qualifiedLocalNet": member.qualified_local_net,
                        }
                        for member in net.members
                    ],
                    "transitiveEndpoints": self.transitive_endpoints(net.id),
                    "crossesHierarchyBoundary": self.project_net_crosses_hierarchy_boundary(net.id),
                }
                for net in (self.project_nets[key] for key in sorted(self.project_nets))
            ],
            "unconnectedPorts": self.unconnected_ports(),
        }
