---
id: AIXEM-SPEC-PROJECT-COMPOSITION-001
title: Project Composition Contract 2
status: normative
version: '2.0'
language: en
domain: specifications
kind: specification
summary: Defines digest-locked multi-sheet composition, organizational hierarchy, explicit project nets, qualified identity, and legacy v1 normalization.
authority:
- project-composition
- project-net-membership
- sheet-hierarchy
aliases:
- aixproj 2
- multi-sheet project
- hierarchical project
- project composition
agent:
  priority: critical
  estimated_tokens: 2084
  intents:
  - compose-project
  - route-project-nets
  - validate-project
depends_on:
- AIXEM-SPEC-PROJECT-LOCK-001
- AIXEM-SPEC-INTERFACE-PORT-001
- AIXEM-CONCEPT-PROJECT-NET-001
related:
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001
- AIXEM-FORMAT-AIXPROJ-001
- AIXEM-CONF-HIERARCHICAL-PROJECT-001
navigation:
  group: specifications
  order: 95
artifacts:
  owns:
  - docs/specifications/schemas/component-graphics-2/aixem-project-manifest-2.schema.json
  consumes:
  - validation/corpus/hierarchical-project-1/results/validation-report.json
requirements:
- id: AIXEM-REQ-HIER-0006
  title: Independent digest-locked sheets
  level: MUST
  statement: Every aixproj/2 sheet record MUST identify one independent source and layout pair whose required digests are verified before resolution.
  validator: schematic.digest_lock
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_multi_view_render_outputs_and_workbench_are_data_driven
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0006.json
- id: AIXEM-REQ-HIER-0007
  title: Explicit project-net membership
  level: MUST
  statement: Cross-sheet electrical equivalence MUST be declared only through projectNets members that resolve to semantic interface ports.
  validator: schematic.semantic
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_project_graph_queries_and_name_isolation
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0007.json
- id: AIXEM-REQ-HIER-0008
  title: No implicit name merge
  level: MUST
  statement: Equal local-net IDs, port IDs, or labels across sheets MUST NOT imply project connectivity.
  validator: schematic.geometry_isolation
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_project_graph_queries_and_name_isolation
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0008.json
- id: AIXEM-REQ-HIER-0009
  title: Acyclic organizational hierarchy
  level: MUST
  statement: Sheet parent relations MUST resolve to existing sheets, contain no self-parent relation, and form an acyclic deterministically ordered hierarchy.
  validator: schematic.project_schema
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_hierarchy_is_explicit_acyclic_and_deterministic
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0009.json
- id: AIXEM-REQ-HIER-0010
  title: Project-net equivalence collision rejection
  level: MUST
  statement: Interface ports already equivalent through one local net MUST NOT be assigned to different project-net IDs.
  validator: schematic.semantic
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_project_net_equivalence_collision_fails_closed
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0010.json
---

# Project Composition Contract 2

`aixproj/2` is the canonical multi-sheet composition boundary. It references independent leaf circuits, defines an organizational sheet hierarchy, declares cross-sheet electrical equivalence through explicit project nets, and locks every required input by digest.

> **Document ID:** `AIXEM-SPEC-PROJECT-COMPOSITION-001`  
> **Status:** Normative  
> **Version:** 2.0

## Canonical Structure

```text
Project
├── sheets[]
│   ├── source ref -> one .aixem leaf
│   ├── layout ref -> one .aixlayout.json leaf
│   ├── optional parent
│   └── optional order
├── projectNets[]
│   └── members[] -> {sheet, port}
├── libraries[]
└── renderPolicy
```

A project is not one flattened semantic source. Each leaf remains independently valid and independently renderable.

## Sheet Records

Every sheet record requires:

```text
id
title
source.path + source.digest + source.mediaType
layout.path + layout.digest + layout.mediaType
```

Optional `parent` and `order` fields organize navigation and deterministic placement. The parent relation has no electrical effect.

Sheet IDs are project-unique. AIXEM 0.5.3 does not define reusable module instances or repeated isolated namespaces; each sheet record represents one project-unique identity.

## Project Nets

A project net declares electrical equivalence between semantic interface ports:

```json
{
  "id": "vcc_5v",
  "members": [
    {"sheet": "power", "port": "VOUT"},
    {"sheet": "control", "port": "VCC"},
    {"sheet": "io", "port": "VCC"}
  ]
}
```

Each project net:

- has a project-unique ID;
- has at least two members;
- resolves every sheet and port;
- contains no duplicate member;
- owns each interface port at most once in the P0 profile;
- cannot split one local equivalence class into multiple project-net IDs.

The project may connect a port, but it cannot rebind the port to a different local net. Local ownership remains in the leaf `.aixem` source.

## No Name-Based Global Nets

Names are identifiers within their own authority scope. These objects are independent unless the project explicitly connects their interface ports:

```text
local-net:power:gnd
local-net:control:gnd
local-net:io:gnd
```

The same rule applies to interface port labels and annotation text. There are no implicit global nets in the 0.5.3 P0 profile.

## Hierarchy

Hierarchy is an optional `parent` relation among real sheets. Validation requires:

- unique sheet IDs;
- an existing parent;
- no self-parent relation;
- no cycles;
- deterministic root and child order using explicit `order`, then stable ID.

Hierarchy is organizational. A parent-child relation never creates project-net membership.

## Qualified Resolved Identity

The project resolver emits unambiguous qualified identities:

```text
sheet:<sheet-id>
entity:<sheet-id>:<entity-id>
local-net:<sheet-id>:<net-id>
interface:<sheet-id>:<port-id>
project-net:<project-net-id>
```

This prevents same-named entities and local nets on different sheets from collapsing in search, selection, diagnostics, or generated DOM IDs.

## Project Semantic Graph

The resolver links project nets to their backing local semantic data without rewriting the leaves:

```text
ProjectNet(vcc_5v)
└── Interface(control:VCC)
    └── LocalNet(control:vcc)
        ├── U1.VCC
        └── @VCC
```

Required deterministic queries include participating sheets, local-net owner, transitive endpoints, unconnected ports, hierarchy crossings, and provenance ownership.

## Canonical New Library References

Project references remain safe, project-root relative, and digest locked. Newly authored reusable assets are referenced from `library/electronics/...` or `library/architecture/...`. Pre-0.5.9 paths such as `libraries/...` or `symbols/...` remain loadable when already present and explicitly referenced; they are not the destination for ordinary new authoring.

A nested self-contained project owns its own local `library/` subtree unless an explicit packaging/materialization workflow provides another project-local asset. Path traversal to a repository-level library is never permitted.

## Reference Security

All file paths are project-root relative. `..` path escape and silent remote dependencies are denied. Duplicate paths carrying contradictory declared digests are rejected before file resolution. Every required source, layout, library, and symbol digest is verified before semantic composition.

## Legacy v1 Compatibility

`aixproj/1` remains a supported single-sheet contract. Implementations may normalize it internally as:

```text
Project
└── Sheet(main)
```

This is a derived runtime view. The implementation must not rewrite the original project file, source, layout, SVG, or resolved-scene contract merely to support v2.

## Non-Goals

This release does not define reusable module instances, parameterized sheet instancing, bus ports, implicit global nets, canonical flattening, native KiCad/OrCAD hierarchy interchange, or interactive manual project routing.

## Evidence

- H001–H005 cover composition, fanout, name isolation, and hierarchy;
- H009, H010, and H015 cover unresolved members, duplicate ownership, and equivalence collision;
- H011 covers digest locking;
- H012 proves v1 behavior;
- H013 proves the ten-sheet baseline.

See [Hierarchical Project Conformance](../../conformance/hierarchical-project.md).


## Normative Requirements

<a id="AIXEM-REQ-HIER-0006"></a>

### AIXEM-REQ-HIER-0006 — Independent digest-locked sheets

**MUST.** Every aixproj/2 sheet record MUST identify one independent source and layout pair whose required digests are verified before resolution.

- Verification mode: `automated`
- Validator: `schematic.digest_lock`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_multi_view_render_outputs_and_workbench_are_data_driven`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0006.json`

<a id="AIXEM-REQ-HIER-0007"></a>

### AIXEM-REQ-HIER-0007 — Explicit project-net membership

**MUST.** Cross-sheet electrical equivalence MUST be declared only through projectNets members that resolve to semantic interface ports.

- Verification mode: `automated`
- Validator: `schematic.semantic`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_project_graph_queries_and_name_isolation`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0007.json`

<a id="AIXEM-REQ-HIER-0008"></a>

### AIXEM-REQ-HIER-0008 — No implicit name merge

**MUST.** Equal local-net IDs, port IDs, or labels across sheets MUST NOT imply project connectivity.

- Verification mode: `automated`
- Validator: `schematic.geometry_isolation`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_project_graph_queries_and_name_isolation`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0008.json`

<a id="AIXEM-REQ-HIER-0009"></a>

### AIXEM-REQ-HIER-0009 — Acyclic organizational hierarchy

**MUST.** Sheet parent relations MUST resolve to existing sheets, contain no self-parent relation, and form an acyclic deterministically ordered hierarchy.

- Verification mode: `automated`
- Validator: `schematic.project_schema`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_hierarchy_is_explicit_acyclic_and_deterministic`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0009.json`

<a id="AIXEM-REQ-HIER-0010"></a>

### AIXEM-REQ-HIER-0010 — Project-net equivalence collision rejection

**MUST.** Interface ports already equivalent through one local net MUST NOT be assigned to different project-net IDs.

- Verification mode: `automated`
- Validator: `schematic.semantic`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_project_net_equivalence_collision_fails_closed`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0010.json`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
