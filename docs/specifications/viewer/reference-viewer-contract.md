---
id: AIXEM-SPEC-VIEWER-001
title: Reference Viewer Contract 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines the deterministic, self-contained, read-only AIXEM HTML viewer, Viewer Model boundary, qualified
  identity, views, inspection, and compatibility rules.
authority:
- reference-viewer-contract
- viewer-model-contract
- viewer-dom-contract
aliases:
- Reference Viewer
- viewer contract
- viewer.html
- Viewer Model 1
agent:
  priority: critical
  estimated_tokens: 2636
  intents:
  - inspect-viewer
  - render-review
  - validate-project
  - publish-release
depends_on:
- AIXEM-SPEC-RENDERER-001
- AIXEM-SPEC-PROJECT-COMPOSITION-001
- AIXEM-SPEC-VISUAL-PROFILE-001
related:
- AIXEM-SPEC-WORKBENCH-001
- AIXEM-SPEC-VIEWER-STATE-001
- AIXEM-SPEC-VIEWER-SECURITY-001
- AIXEM-CONF-REFERENCE-VIEWER-001
navigation:
  group: viewer
  order: 20
artifacts:
  owns:
  - implementation/schematic/viewer/model.py
  - implementation/schematic/viewer/reference_viewer.py
  - implementation/schematic/viewer/templates/reference-viewer.html.j2
  - docs/specifications/schemas/viewer/aixem-viewer-model-1.schema.json
  consumes:
  - resolved-scene.json
  - resolved-project-scene.json
  - drawing.svg
  - project-overview.svg
  - project-composite.svg
requirements:
- id: AIXEM-REQ-VIEWER-0001
  title: Read-only authority
  level: MUST
  statement: The Reference Viewer MUST NOT create or modify semantic, layout, or project-composition authority.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v001_single_sheet_reference_viewer
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0001.json
- id: AIXEM-REQ-VIEWER-0002
  title: Distinct Viewer and Workbench profiles
  level: MUST
  statement: viewer.html and workbench.html MUST implement separately declared Reference Viewer and Review Workbench
    profiles rather than nominal aliases.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v017_viewer_workbench_are_distinct_shared_profiles
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0002.json
- id: AIXEM-REQ-VIEWER-0004
  title: Canonical multi-sheet modes
  level: MUST
  statement: Hierarchical projects MUST expose Sheet, Overview, and Composite modes.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v002_v003_multisheet_modes_and_hierarchy_navigation
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0004.json
- id: AIXEM-REQ-VIEWER-0015
  title: Viewer Model schema closure
  level: MUST
  statement: The generated Viewer Model MUST validate against its published schema and contain no unresolved qualified-object
    references.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_viewer_security.py::ViewerSecurityConformanceTests.test_structural_negative_viewer_models_fail_closed
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0015.json
- id: AIXEM-REQ-VIEWER-0005
  title: Qualified object identity
  level: MUST
  statement: Viewer selection, search, and highlighting MUST use sheet-qualified identities wherever local names
    can collide.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v015_dom_identity_closure_and_unique_ids
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0005.json
- id: AIXEM-REQ-VIEWER-0006
  title: Selection and inspector closure
  level: MUST
  statement: The same qualified object selected through the canvas, navigator, or search MUST resolve to the same
    inspector identity.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v005_v006_project_net_and_interface_selection
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0006.json
- id: AIXEM-REQ-VIEWER-0007
  title: Project-net highlight closure
  level: MUST
  statement: Selecting a project net MUST highlight only routes and interfaces belonging to that declared project
    net.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v005_v006_project_net_and_interface_selection
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0007.json
- id: AIXEM-REQ-VIEWER-0016
  title: Deterministic viewer artifacts
  level: MUST
  statement: Three complete renders from identical staged inputs MUST produce byte-identical Viewer Model, viewer.html,
    and workbench.html artifacts.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v018_three_run_viewer_artifact_determinism
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0016.json
---

# Reference Viewer Contract 1

The Reference Viewer is the canonical AIXEM HTML surface for inspecting an already-resolved schematic design. It reveals, navigates, filters, highlights, and explains existing AIXEM semantics. It does not author, save, or reinterpret them.

## Product and Authority Boundary

Authoritative inputs remain `.aixem`, `.aixlayout.json`, and `.aixproj.json`. The production renderer owns SVG and resolved-scene evidence. Viewer Model 1 is a deterministic adapter over those products, and Viewer Core state is ephemeral presentation state.

The Viewer may change active mode, active sheet, selection, search text, visible layers, viewport transform, and panel state. None of these changes semantic endpoint closure, net membership, interface membership, placement authority, or route geometry. Unsupported authoring controls are not rendered.

<a id="AIXEM-REQ-VIEWER-0001"></a>

### AIXEM-REQ-VIEWER-0001 — Read-only authority

**MUST.** The Reference Viewer MUST NOT create or modify semantic, layout, or project-composition authority.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v001_single_sheet_reference_viewer`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0001.json`

The prohibited write surface includes semantic nets, project nets, hierarchy, component placement, route paths, junctions, no-connect markers, and all locked source digests.

<a id="AIXEM-REQ-VIEWER-0002"></a>

### AIXEM-REQ-VIEWER-0002 — Distinct Viewer and Workbench profiles

**MUST.** viewer.html and workbench.html MUST implement separately declared Reference Viewer and Review Workbench profiles rather than nominal aliases.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v017_viewer_workbench_are_distinct_shared_profiles`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0002.json`

`viewer.html` identifies `data-aixem-profile="reference-viewer"`. `workbench.html` identifies `data-aixem-profile="review-workbench"` and adds review-only evidence regions while reusing Viewer Core.

## Required Outputs and Project-Type Capabilities

A successful render emits `viewer-model.json`, `viewer.html`, and `workbench.html` in addition to the renderer evidence appropriate for the project type.

| Capability | Single-sheet `aixproj/1` | Hierarchical `aixproj/2` |
|---|---:|---:|
| Sheet view | MUST | MUST |
| Overview view | not shown | MUST |
| Composite view | not shown | MUST |
| Component/local-net inspection | MUST | MUST |
| Interface inspection | when present | when present |
| Project-net inspection | not applicable | MUST |
| Qualified search | MUST | MUST |
| Sheet-scoped layers | MUST | MUST |
| Pan, zoom, and fit | MUST | MUST in every view |
| Authoring/write-back | MUST NOT | MUST NOT |

<a id="AIXEM-REQ-VIEWER-0004"></a>

### AIXEM-REQ-VIEWER-0004 — Canonical multi-sheet modes

**MUST.** Hierarchical projects MUST expose Sheet, Overview, and Composite modes.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v002_v003_multisheet_modes_and_hierarchy_navigation`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0004.json`

## Viewer Model 1

Viewer Model 1 uses schema URI `https://schemas.aixem.org/viewer/viewer-model/1` and declares `viewerContract: aixem.reference-viewer@1`. It contains project metadata, capability flags, deterministic view records, hierarchy, qualified objects, sheet-scoped layers, diagnostics, search entries, initial state, and provenance.

The adapter may index or project existing resolved data for efficient use, but it may not invent a semantic fact absent from resolved evidence. Every object reference must close against the model object registry. Unsupported required schema versions fail closed.

<a id="AIXEM-REQ-VIEWER-0015"></a>

### AIXEM-REQ-VIEWER-0015 — Viewer Model schema closure

**MUST.** The generated Viewer Model MUST validate against its published schema and contain no unresolved qualified-object references.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_viewer_security.py::ViewerSecurityConformanceTests.test_structural_negative_viewer_models_fail_closed`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0015.json`

## Stable Qualified Identity

The canonical forms are:

```text
sheet:<sheet-id>
entity:<sheet-id>:<entity-id>
local-net:<sheet-id>:<net-id>
interface:<sheet-id>:<port-id>
project-net:<project-net-id>
```

Local names never substitute for qualified identity. `Power / U1` and `Control / U1` remain distinct even if their native entity IDs match. Zoom, pan, view mode, search, visibility, and panel state never change a QID.

The root document exposes `data-aixem-viewer="1"`, `data-aixem-profile`, `data-aixem-project`, and `data-aixem-dom-contract="1"`. Semantic canvas objects expose `data-aixem-kind` and `data-aixem-qid`. Action controls expose stable `data-aixem-action` markers. HTML and SVG IDs must be unique.

<a id="AIXEM-REQ-VIEWER-0005"></a>

### AIXEM-REQ-VIEWER-0005 — Qualified object identity

**MUST.** Viewer selection, search, and highlighting MUST use sheet-qualified identities wherever local names can collide.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v015_dom_identity_closure_and_unique_ids`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0005.json`

## View Contracts

### Sheet

Sheet view presents one resolved sheet. Local layers and local-net highlighting are confined to the owning sheet. Selecting a component or local net from search opens the owning sheet. Fit targets that sheet only.

### Overview

Overview presents resolved sheet blocks, interface anchors, hierarchy, and explicit project nets. Visual crossings do not create connectivity. Selecting a sheet navigates to its Sheet view; selecting a project net highlights exactly its declared overview routes and interfaces.

### Composite

Composite presents complete transformed sheet canvases in project space. Embedded leaf objects retain their sheet-qualified identity. Project-net routes join transformed interface anchors; same-named local nets in different sheets remain isolated.

Selection is preserved across views when the selected QID has a representation in the destination. The inspector may retain a selection that has no canvas glyph in the destination without fabricating one.

## Selection, Search, and Inspector

One primary semantic selection is active at a time. Required kinds are sheet, entity, local net, interface, and project net. Canvas, navigator, and search selection all resolve through the object registry.

Search indexes qualified ID, sheet ID/title, reference, value, entity ID, local-net ID, interface-port ID, and project-net ID. Results are ordered by category, project hierarchy preorder, and stable QID. Runtime search does not fetch source files or scan the repository.

The inspector shows only fields available in resolved evidence. Entity inspection includes identity, reference, value, type, symbol, variant, placement, parameters, ports, and symbol digest when available. Net and interface inspection reports scope, membership, endpoints, route/junction counts, and project relationships without changing authority.

<a id="AIXEM-REQ-VIEWER-0006"></a>

### AIXEM-REQ-VIEWER-0006 — Selection and inspector closure

**MUST.** The same qualified object selected through the canvas, navigator, or search MUST resolve to the same inspector identity.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v005_v006_project_net_and_interface_selection`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0006.json`

<a id="AIXEM-REQ-VIEWER-0007"></a>

### AIXEM-REQ-VIEWER-0007 — Project-net highlight closure

**MUST.** Selecting a project net MUST highlight only routes and interfaces belonging to that declared project net.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v005_v006_project_net_and_interface_selection`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0007.json`

## Determinism and Compatibility

Viewer contract versioning is independent from `.aixproj` and `.aixlayout` schema versioning. Viewer Contract 1 may serve valid v1 and v2 projects. Compatible implementations may alter non-semantic spacing, chrome styling, CSS class names, and internal JavaScript organization while preserving capabilities, initial state, QIDs, DOM contract markers, security, and behavioral conformance.

A breaking change to required views, QID semantics, Viewer Model schema, DOM automation markers, selection semantics, or deterministic initialization requires a new Viewer Contract version. Circuit schemas and resolved renderer formats are not revised by this contract.

<a id="AIXEM-REQ-VIEWER-0016"></a>

### AIXEM-REQ-VIEWER-0016 — Deterministic viewer artifacts

**MUST.** Three complete renders from identical staged inputs MUST produce byte-identical Viewer Model, viewer.html, and workbench.html artifacts.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v018_three_run_viewer_artifact_determinism`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0016.json`

## Non-Goals

Viewer Contract 1 excludes placement editing, wire drawing, route modification, property editing, project-net editing, hierarchy editing, save/write-back, undo/redo, collaboration, server APIs, remote project loading, plugins, waveform viewing, PCB/Gerber viewing, and vendor editor emulation.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
