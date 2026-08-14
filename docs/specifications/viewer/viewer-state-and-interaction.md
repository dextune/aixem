---
id: AIXEM-SPEC-VIEWER-STATE-001
title: Viewer State and Interaction 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines deterministic Viewer Core runtime state, mode transitions, active-sheet behavior, selection, search,
  layer ownership, viewport transforms, and keyboard commands.
authority:
- viewer-state-contract
- viewer-interaction-contract
aliases:
- Viewer state
- Viewer Core
- pan zoom fit
agent:
  priority: critical
  estimated_tokens: 1426
  intents:
  - inspect-viewer
  - render-review
  - validate-project
depends_on:
- AIXEM-SPEC-VIEWER-001
related:
- AIXEM-SPEC-VIEWER-A11Y-001
- AIXEM-SPEC-VIEWER-SECURITY-001
navigation:
  group: viewer
  order: 40
artifacts:
  owns:
  - implementation/schematic/viewer/core.py
  consumes:
  - viewer-model.json
requirements:
- id: AIXEM-REQ-VIEWER-0003
  title: Deterministic initial state
  level: MUST
  statement: Identical Viewer Models MUST initialize to the same mode, active sheet, layer state, empty selection,
    search state, and fitted viewport.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v002_v003_multisheet_modes_and_hierarchy_navigation
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0003.json
- id: AIXEM-REQ-VIEWER-0008
  title: Sheet-scoped layer state
  level: MUST
  statement: Layer visibility MUST remain scoped by sheet and MUST NOT create semantic changes.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v007_sheet_scoped_layer_visibility
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0008.json
- id: AIXEM-REQ-VIEWER-0009
  title: Viewport operability
  level: MUST
  statement: Every required canvas view MUST provide pan, zoom-in, zoom-out, and fit behavior.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v010_pan_zoom_fit_per_view_state
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0009.json
- id: AIXEM-REQ-VIEWER-0010
  title: Keyboard operability
  level: MUST
  statement: Required Viewer controls MUST be operable through keyboard navigation.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_viewer_accessibility.py::ViewerAccessibilityConformanceTests.test_v011_keyboard_only_required_workflow
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0010.json
---

# Viewer State and Interaction 1

Viewer Core owns ephemeral presentation state only. State transitions are deterministic functions of the same Viewer Model and the same ordered user actions. State is neither written back to AIXEM files nor persisted in browser storage in P0.

## State Record

```text
mode
activeSheet
selection
searchQuery
visibleLayersBySheet
viewportByView
activeNavigatorCategory
navigatorOpen
inspectorOpen
```

The initial active sheet is the first deterministic project-preorder sheet. The default mode is Sheet, selection is empty, query is empty, category is Project for multi-sheet or Components for single-sheet, layer visibility follows `defaultVisible`, and each view starts fitted to its declared canvas.

<a id="AIXEM-REQ-VIEWER-0003"></a>

### AIXEM-REQ-VIEWER-0003 — Deterministic initial state

**MUST.** Identical Viewer Models MUST initialize to the same mode, active sheet, layer state, empty selection, search state, and fitted viewport.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v002_v003_multisheet_modes_and_hierarchy_navigation`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0003.json`

## View and Sheet Transitions

Mode controls are capability-driven. A single-sheet Viewer does not display semantically empty Overview or Composite controls. Selecting a sheet activates that sheet and enters Sheet mode. Selecting a component or local net activates its owning sheet. Selecting a project net may remain active across Overview and Composite.

Switching views does not mutate semantic data. Each view retains its own ephemeral viewport transform keyed as `sheet:<sheet-id>`, `overview`, or `composite`.

## Selection State

P0 permits one primary QID selection. Escape and Clear Selection clear it. Canvas, navigator, and search events call the same qualified selection path. A local-net selection does not expand to same-named nets on other sheets or to an entire project net. A project-net selection expands only to declared related project routes and interfaces.

## Search State

Search is case-insensitive over deterministic model-provided search text. Empty query restores the normal qualified navigator. Results preserve category/hierarchy/QID order. Selecting a result closes the search mode, updates active sheet/mode as needed, and opens the same inspector record as any other selection source.

## Layer State

Layer keys are `sheet-id + layer-id`. The same native layer ID on another sheet is independent. Visibility changes CSS/SVG presentation only; the object registry, selection, semantic memberships, and evidence digests remain unchanged.

<a id="AIXEM-REQ-VIEWER-0008"></a>

### AIXEM-REQ-VIEWER-0008 — Sheet-scoped layer state

**MUST.** Layer visibility MUST remain scoped by sheet and MUST NOT create semantic changes.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v007_sheet_scoped_layer_visibility`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0008.json`

## Viewport State

Each canvas has a source width, source height, and source unit. Fit computes a deterministic transform from the available viewport and declared canvas bounds. Zoom is anchored at the pointer when pointer coordinates are available; toolbar and keyboard zoom use the current viewport center. Pan changes only the viewport transform.

Source/layout coordinates remain distinct from CSS transforms. Sheet pointer coordinates map back through the inverse transform to declared sheet units.

<a id="AIXEM-REQ-VIEWER-0009"></a>

### AIXEM-REQ-VIEWER-0009 — Viewport operability

**MUST.** Every required canvas view MUST provide pan, zoom-in, zoom-out, and fit behavior.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_reference_viewer.py::ReferenceViewerConformanceTests.test_v010_pan_zoom_fit_per_view_state`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0009.json`

## Keyboard Profile

| Input | Required action |
|---|---|
| `0` | fit current view |
| `+` or `=` | zoom in |
| `-` | zoom out |
| `Escape` | clear selection and close transient panels |
| `/` | focus search |
| arrow keys on focused canvas | pan |
| normal Tab navigation | reach every toolbar, category, result, layer, and panel control |

Pointer pan supports middle-button drag and Space plus primary-button drag. Equivalent platform mappings are allowed only when documented and browser-tested.

<a id="AIXEM-REQ-VIEWER-0010"></a>

### AIXEM-REQ-VIEWER-0010 — Keyboard operability

**MUST.** Required Viewer controls MUST be operable through keyboard navigation.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_viewer_accessibility.py::ViewerAccessibilityConformanceTests.test_v011_keyboard_only_required_workflow`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0010.json`

## Persistence Boundary

Viewer Contract 1 does not use cookies, local storage, session storage, IndexedDB, service workers, or remote session APIs. This preserves reproducible startup and avoids creating an undeclared workspace/session authority format. Deep links or explicit session exports require a later compatible extension contract.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
