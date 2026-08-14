# AIXEM 0.5.4 — Reference Viewer Contract Normalization Plan

**Proposed target release:** AIXEM 0.5.4 candidate  
**Plan status:** Implementation-ready  
**Baseline:** AIXEM 0.5.3 (2026-08-11)  
**Primary objective:** Replace the current loosely specified HTML viewer/workbench behavior with a versioned, deterministic, read-only AIXEM Reference Viewer contract that can inspect single-sheet and hierarchical multi-sheet projects without becoming an editor or semantic authority.  
**Compatibility objective:** Preserve all valid AIXEM 0.5.3 project, source, layout, symbol, library, resolved-scene, and rendering semantics.  
**Documentation language:** English only.

---

## 1. Executive Summary

AIXEM 0.5.3 now has a strong semantic and rendering foundation:

```text
.aixem
  local semantic authority
        ↓
.aixlayout
  local presentation authority
        ↓
.aixproj
  project composition authority
        ↓
resolved-scene / resolved-project-scene
  deterministic derived evidence
        ↓
SVG outputs
        ↓
viewer.html / workbench.html
```

The weak layer is the final consumption surface.

The current viewer/workbench implementation is useful as a proof of rendering, but it is not yet a sufficiently normalized product contract. It mixes visual profile guidance, renderer output naming, engineering-review UI, viewer behavior, and some editor-looking controls without defining a stable boundary between them.

The 0.5.4 goal is therefore **not** to add a large application framework or an editor. The goal is to turn the HTML viewing surface into a stable AIXEM specification.

The target architecture is:

```text
                       AUTHORITATIVE INPUTS
                .aixem / .aixlayout / .aixproj
                              │
                              ▼
                    Production Renderer
                              │
             ┌────────────────┴────────────────┐
             │                                 │
             ▼                                 ▼
      resolved-scene/1                resolved-project-scene/1
      drawing/sheet SVG               overview/composite SVG
             │                                 │
             └────────────────┬────────────────┘
                              ▼
                    Viewer Model Adapter
                   derived, non-authoritative
                              │
                              ▼
                       Viewer Core 1
      state + identity + navigation + selection + viewport
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      Reference Viewer 1              Review Workbench 1
       strict read-only              viewer + diagnostics
       viewer.html                    workbench.html
```

The most important rule is:

> **The Viewer may reveal, navigate, filter, highlight, and explain existing AIXEM semantics, but it may never create or modify circuit semantics, layout authority, project-net membership, or route geometry.**

The Reference Viewer should become the canonical HTML surface for looking at an AIXEM design. The Workbench should become a separate engineering-review profile built on the same Viewer Core. Neither should pretend to be an editor until an editor contract exists.

---

## 2. Baseline Findings from AIXEM 0.5.3

### 2.1 Existing strengths to preserve

The 0.5.3 implementation already provides important foundations:

1. deterministic SVG rendering;
2. deterministic `resolved-scene.json`;
3. deterministic `resolved-project-scene.json` for hierarchical projects;
4. qualified multi-sheet identities;
5. Sheet / Overview / Composite project views;
6. data-driven hierarchy navigation;
7. project-net and interface-port highlighting;
8. sheet-scoped layer controls;
9. local-only assets with remote dependencies denied;
10. static HTML output that can be reviewed without a backend;
11. Playwright/Chromium already available in release tooling;
12. screenshot evidence generation already exists.

These should be normalized rather than replaced.

### 2.2 Viewer and Workbench are currently not real separate products

The renderer contract names two different outputs:

```text
viewer.html    standalone SVG viewer
workbench.html engineering review interface
```

However, the current implementation writes the same generated HTML to both outputs.

This is true in both inspected baseline classes:

```text
GridProjectRenderer
MultiSheetProjectRenderer
```

and was confirmed in representative 0.5.3 outputs where the two files are byte-identical.

Therefore the current distinction is nominal rather than contractual.

### 2.3 Current Workbench Visual Profile is too shallow

The existing normative Workbench Visual Profile primarily fixes:

```text
remote presentation assets are not required
narrow/desktop inspection remains possible
```

The visual-language documentation additionally requires general engineering regions and semantic color independence.

Those are useful requirements, but they do not define:

- what a Viewer is;
- what a Workbench is;
- whether either is read-only;
- required view modes;
- required navigation behavior;
- required selection semantics;
- required inspector fields;
- required search semantics;
- required viewport controls;
- runtime state ownership;
- cross-view selection behavior;
- stable DOM identity;
- supported keyboard interaction;
- security behavior for embedded authored text;
- browser behavior conformance;
- viewer capability/version negotiation.

### 2.4 Current single-sheet UI exposes editor-like controls without editor authority

The existing single-sheet generated UI displays controls such as:

```text
Place wire
Place symbol
Place net label
Place junction
Place no-connect
Rotate selection
```

but these controls do not implement authoritative edit/write-back behavior.

This creates an undesirable ambiguity:

```text
looks like editor
≠
has editor contract
```

The Reference Viewer must not expose unsupported authoring affordances.

### 2.5 Current browser conformance is mostly structural

The current hierarchical tests verify important generated markers such as:

```text
data-mode="sheet"
data-mode="overview"
data-mode="composite"
data-open-sheet="..."
```

and verify that hierarchy is data-driven.

However, a proper Viewer contract also needs executable browser tests proving that controls actually behave correctly after page load.

Examples:

```text
mode switch works
qualified search returns the right object
sheet navigation changes the active sheet
project-net selection highlights the correct routes
layer toggle affects only the owning sheet
keyboard controls work
no external network request occurs
narrow viewport remains operable
```

### 2.6 Multi-sheet viewing behavior is under-specified

The 0.5.3 multi-sheet Workbench already provides the correct semantic views, but behavior such as pan, zoom, fit, per-view viewport state, selection persistence, and responsive panel behavior is not yet fixed by a normative contract.

That leaves too much implementation-specific behavior in a layer intended to become a reference product.

---

## 3. Scope and Conservative Design Principles

### 3.1 Normalize before expanding

P0 should standardize the existing viewing capabilities first.

Do not use this release to add:

- schematic editing;
- project editing;
- drag-and-drop placement;
- route editing;
- project save/write-back;
- collaboration;
- server APIs;
- online asset loading;
- vendor import/export;
- plugin systems.

### 3.2 The Viewer is a derived consumption surface

Authority remains:

```text
.aixem       semantic authority
.aixlayout   local presentation authority
.aixproj     project composition authority
```

The Viewer owns only ephemeral runtime state such as:

```text
active view mode
active sheet
selection
search query
visible layers
viewport transform
open/collapsed panels
```

Viewer state MUST NOT become circuit authority.

### 3.3 Reference Viewer and Review Workbench must be distinct

Define two product profiles over one shared core:

```text
AIXEM Reference Viewer 1
  read-only design inspection

AIXEM Review Workbench 1
  Reference Viewer 1
  + diagnostics/evidence/review surfaces
```

The Workbench is not an editor.

### 3.4 No fake controls

A control MUST satisfy one of these conditions:

```text
implemented and conformant
or
not rendered
```

Do not present inactive editor-like tools merely to resemble a CAD application.

### 3.5 No new authored authority format in P0

Do not create `.aixviewer`, `.aixworkspace`, or another user-authored file.

If a Viewer Model is introduced, it is **derived output only** and must be reproducible entirely from resolved renderer outputs.

### 3.6 Viewer versioning is independent from circuit format versioning

A project may be:

```text
aixproj/1
or
aixproj/2
```

while being rendered by:

```text
AIXEM Reference Viewer Contract 1
```

Viewer contract version and project schema version must not be conflated.

---

## 4. Normative Terminology

The following terminology should be fixed in governance documentation.

### 4.1 Project

A complete AIXEM schematic design composition.

```text
Project
├─ Sheet
├─ Project Net
└─ Hierarchy
```

### 4.2 Sheet

An independent semantic/layout schematic unit.

### 4.3 Layer

A presentation subdivision inside one Sheet.

### 4.4 View

A visual projection of an already-resolved design.

Normative view IDs:

```text
sheet
overview
composite
```

### 4.5 Reference Viewer

A deterministic, read-only HTML inspection surface for AIXEM rendered products.

### 4.6 Review Workbench

A Reference Viewer-based engineering review surface that adds diagnostics and evidence presentation.

### 4.7 Editor

A future product capable of changing authoritative AIXEM content.

The term `Editor` MUST NOT be applied to the 0.5.4 Viewer or Workbench.

### 4.8 Viewer Core

The shared implementation layer that owns viewer-only runtime state and interaction behavior.

---

## 5. Reference Viewer Contract 1

Create a new top-level normative contract:

```text
docs/specifications/viewer/reference-viewer-contract.md
```

Recommended stable ID:

```text
AIXEM-SPEC-VIEWER-001
```

Recommended authority scope:

```text
reference-viewer-contract
```

### 5.1 Required output

A successful reference render MUST emit:

```text
viewer.html
```

`viewer.html` MUST be:

- deterministic from locked inputs;
- read-only;
- self-contained for P0;
- usable without a backend;
- usable without required network access;
- capable of presenting every required view supported by the input project;
- semantically inspectable through stable qualified identity.

### 5.2 Single-sheet required capability

For legacy/single-sheet projects:

```text
Sheet View             MUST
component selection    MUST
local-net selection    MUST
layer visibility       MUST
search                 MUST
pan                     MUST
zoom                    MUST
fit                     MUST
properties inspection  MUST
```

Overview and Composite controls SHOULD NOT be shown when they add no semantic value.

### 5.3 Multi-sheet required capability

For `aixproj/2` hierarchical projects:

```text
Sheet View               MUST
Overview View            MUST
Composite View           MUST
hierarchy navigation     MUST
qualified search         MUST
interface inspection     MUST
project-net inspection   MUST
sheet-scoped layers      MUST
cross-view highlighting  MUST
pan / zoom / fit         MUST
```

### 5.4 Read-only contract

The Reference Viewer MUST NOT:

```text
modify .aixem
modify .aixlayout
modify .aixproj
change semantic net membership
change project-net membership
move component authority
write route geometry
create junction semantics
create no-connect semantics
```

Runtime hiding/highlighting/viewport transforms are allowed because they do not alter authoritative data.

---

## 6. Review Workbench Contract 1

Create:

```text
docs/specifications/viewer/review-workbench-contract.md
```

Recommended stable ID:

```text
AIXEM-SPEC-WORKBENCH-001
```

### 6.1 Relationship

Normative relationship:

```text
Review Workbench 1
  extends Reference Viewer 1
```

The Workbench inherits all Viewer requirements.

### 6.2 Additional Workbench regions

The Workbench MAY add:

```text
validation diagnostics
render evidence
input/output digests
conformance status
routing metrics
release information
artifact provenance
```

### 6.3 Workbench must not imply authoring support

Remove or explicitly exclude fake authoring controls.

In P0 the Workbench is:

```text
engineering review surface
```

not:

```text
schematic editor
```

### 6.4 Distinct generated output

After 0.5.4:

```text
viewer.html != workbench.html
```

by contract and purpose.

They may share most Viewer Core code and styling, but the product profile and rendered regions must be distinguishable.

---

## 7. Viewer Model — Stable Derived Boundary

### 7.1 Purpose

The renderer currently directly manufactures large HTML strings from renderer-internal scene structures.

Introduce one derived adapter boundary:

```text
resolved scene(s)
      ↓
ViewerModelBuilder
      ↓
Viewer Model 1
      ↓
ReferenceViewerRenderer / ReviewWorkbenchRenderer
```

### 7.2 Authority

Viewer Model 1 is derived and non-authoritative.

It MUST NOT contain new circuit meaning absent from resolved inputs.

### 7.3 Machine-readable schema

Add:

```text
docs/specifications/schemas/viewer/aixem-viewer-model-1.schema.json
```

Recommended schema URI:

```text
https://schemas.aixem.org/viewer/viewer-model/1
```

### 7.4 Minimum Viewer Model fields

Recommended shape:

```json
{
  "schema": "https://schemas.aixem.org/viewer/viewer-model/1",
  "formatVersion": "1.0",
  "viewerContract": "aixem.reference-viewer@1",
  "project": {},
  "capabilities": {},
  "views": [],
  "hierarchy": [],
  "objects": {},
  "layers": {},
  "diagnostics": [],
  "provenance": {}
}
```

### 7.5 Required capability flags

Example:

```json
{
  "sheet": true,
  "overview": true,
  "composite": true,
  "hierarchy": true,
  "projectNets": true,
  "interfacePorts": true,
  "diagnostics": false
}
```

Reference Viewer and Workbench rendering should be driven from declared capability data rather than hard-coded project-type assumptions in UI templates.

### 7.6 No duplication of semantic authority

The Viewer Model may index existing data for efficient lookup, but must preserve provenance back to:

```text
resolved-scene
resolved-project-scene
source/layout/project digests
```

---

## 8. Stable Object Identity Contract

### 8.1 Qualified IDs

The viewer must standardize the resolved identity vocabulary already established by multi-sheet composition.

Required forms:

```text
sheet:<sheet-id>
entity:<sheet-id>:<entity-id>
local-net:<sheet-id>:<net-id>
interface:<sheet-id>:<port-id>
project-net:<project-net-id>
```

Optional later forms:

```text
endpoint:<sheet-id>:<entity-id>:<port-id>
junction:<sheet-id>:<net-id>:<junction-id>
```

### 8.2 Identity stability

Changing:

```text
zoom
pan
active view
search query
layer visibility
panel state
```

must not change object identity.

### 8.3 DOM identity

Create a stable DOM inspection contract.

Recommended attributes:

```html
data-aixem-kind="entity"
data-aixem-qid="entity:control:U1"
data-sheet="control"
data-entity="U1"
```

Project routes:

```html
data-aixem-kind="project-net"
data-aixem-qid="project-net:vcc_5v"
data-project-net="vcc_5v"
```

### 8.4 No ambiguous unqualified identity

A viewer must not treat:

```text
Power / U1
Control / U1
```

as one object merely because both use `U1`.

### 8.5 DOM IDs must remain unique

Every HTML/SVG `id` in one generated document MUST be unique.

Qualified AIXEM identity should use explicit `data-*` attributes rather than depending on opaque generated DOM IDs.

---

## 9. Viewer Runtime State Model

Create:

```text
docs/specifications/viewer/viewer-state-and-interaction.md
```

Recommended stable ID:

```text
AIXEM-SPEC-VIEWER-STATE-001
```

### 9.1 Required state

The Viewer Core should explicitly model:

```text
mode
activeSheet
selection
searchQuery
visibleLayersBySheet
viewportByView
activeNavigatorCategory
```

### 9.2 Initial state must be deterministic

For the same Viewer Model, startup state must be deterministic.

Recommended initialization:

```text
mode = sheet
activeSheet = first deterministic project preorder sheet
selection = none
searchQuery = empty
layers = each layer.defaultVisible
viewport = fit active content
navigator category = project for multi-sheet, components for single-sheet
```

### 9.3 Runtime state is not persisted in P0

Do not use local storage, cookies, IndexedDB, or remote state persistence in P0.

Reason:

- avoids hidden user-state affecting review evidence;
- preserves reproducible startup behavior;
- keeps `viewer.html` portable;
- avoids creating an undeclared workspace/session format.

A future workspace product may define persistence separately.

---

## 10. View Mode Contract

### 10.1 Sheet View

Sheet View shows one resolved sheet at normal schematic scale.

Required behavior:

- one active sheet at a time;
- local layers apply only to that sheet;
- local-net selection highlights only the owning local net;
- interface ports are inspectable where supported;
- selecting a component from search opens its owning sheet;
- `Fit` fits the active sheet, not the whole project.

### 10.2 Overview View

Overview View shows hierarchy-aware sheet blocks and project nets.

Required behavior:

- project-net selection highlights the whole project net;
- selecting a sheet block may navigate to Sheet View;
- project connections remain semantic only through declared project nets;
- visual crossings do not imply connectivity;
- Overview must not fabricate hierarchy nodes.

### 10.3 Composite View

Composite View shows full sheet canvases in project space.

Required behavior:

- sheet identity remains visible and qualified;
- project-net routing connects transformed interface anchors;
- selecting a project net highlights every visible project-route segment and its participating interfaces;
- local nets remain scoped to their owning sheet;
- a local-net highlight must not accidentally highlight same-named nets in another sheet.

### 10.4 View switching

Switching view MUST NOT mutate design semantics.

The Viewer SHOULD preserve the active semantic selection when the selected object has a meaningful representation in the destination view.

Example:

```text
select project-net:vcc_5v in Overview
→ switch Composite
→ project-net:vcc_5v remains selected/highlighted
```

If an object has no representation in a view, the inspector may retain the selection while the canvas shows no direct glyph.

---

## 11. Viewport Interaction Contract

### 11.1 Required controls

Every canvas view MUST support:

```text
pan
zoom in
zoom out
fit
```

### 11.2 Pointer behavior

Recommended profile:

```text
mouse wheel / trackpad       zoom at pointer anchor
middle-drag                  pan
Space + primary drag         pan
```

Alternative browser/platform mappings may be allowed if behavior remains documented and testable.

### 11.3 Keyboard behavior

Minimum keyboard contract:

```text
0          fit current view
+ or =     zoom in
-          zoom out
Escape     clear selection
/          focus search
```

All toolbar functions must remain keyboard accessible through normal focus traversal even when shortcuts are unavailable.

### 11.4 Coordinate correctness

In Sheet View, pointer coordinate readout SHOULD map back to the sheet coordinate system and declared units.

Viewport CSS transforms must not be mistaken for source/layout coordinates.

### 11.5 Per-view viewport state

Maintain independent runtime transforms for:

```text
sheet:<sheet-id>
overview
composite
```

Switching views should not unnecessarily destroy the user’s previous inspection position.

This state is ephemeral and non-authoritative.

---

## 12. Selection and Inspector Contract

### 12.1 One primary semantic selection

P0 should use one primary selection at a time.

Required selection kinds:

```text
sheet
entity
local-net
interface
project-net
```

Multiple-selection is outside P0.

### 12.2 Entity inspector

Minimum fields:

```text
Qualified ID
Sheet
Entity ID
Reference
Value
Component type
Symbol ID
Variant
Placement
```

Where already available from the resolved scene, include:

```text
parameters
ports
symbol digest
```

### 12.3 Local-net inspector

Minimum fields:

```text
Qualified ID
Sheet
Local net ID
Endpoint count
Endpoints
Path count
Junction count
Related project net, if any
Semantic authority
```

### 12.4 Interface-port inspector

Minimum fields:

```text
Qualified ID
Sheet
Port ID
Direction
Role
Local net
Project net or unconnected
Sheet coordinate
```

### 12.5 Project-net inspector

Minimum fields:

```text
Qualified ID
Project-net ID
Participating sheets
Interface members
Backing local nets
Transitive endpoint count
Crosses hierarchy boundary
```

### 12.6 Selection closure

Selecting an object from:

```text
canvas
hierarchy
navigator
search result
```

must resolve to the same qualified identity and inspector result.

---

## 13. Search Contract

### 13.1 Search must be semantic and qualified

Search categories should include:

```text
Sheets
Components
Local Nets
Interface Ports
Project Nets
```

### 13.2 Required matching inputs

Search index should use normalized fields such as:

```text
qualified ID
sheet title
sheet ID
reference
value
entity ID
local net ID
interface port ID
project net ID
```

### 13.3 Deterministic result order

Recommended sort:

```text
category priority
→ project hierarchy preorder
→ stable qualified ID
```

### 13.4 Same-name isolation

A query for `gnd` may return:

```text
Power / local net / gnd
Control / local net / gnd
Project net / gnd
```

but these remain separate selectable identities.

### 13.5 Search must not load unrelated authority

The generated Viewer Model should already contain the compact indexes needed for inspection. Runtime search must not fetch source files or scan the repository.

---

## 14. Layer Visibility Contract

### 14.1 Sheet-scoped ownership

Layer state is keyed by:

```text
sheet-id + layer-id
```

not only by `layer-id`.

### 14.2 Default state

Initial visibility follows resolved layer `defaultVisible`.

### 14.3 Layer toggles are presentation-only

Hiding a layer:

- does not alter semantic objects;
- does not alter selection identity;
- does not alter project-net membership;
- does not change generated source evidence.

### 14.4 Composite handling

In P0, Composite View may expose either:

- active-sheet layer controls; or
- a clearly qualified per-sheet layer panel.

It MUST NOT silently synchronize same-named layers across sheets unless a later viewer profile explicitly defines that behavior.

---

## 15. Viewer Security Contract

Create:

```text
docs/specifications/viewer/viewer-security-and-embedding.md
```

Recommended stable ID:

```text
AIXEM-SPEC-VIEWER-SECURITY-001
```

### 15.1 Offline-first and no required network

P0 Reference Viewer MUST work with network unavailable.

It MUST NOT require:

```text
remote fonts
remote CSS
remote JavaScript
remote images
remote JSON
analytics
telemetry
```

### 15.2 No network side effects

Reference Viewer runtime MUST NOT initiate:

```text
fetch
XMLHttpRequest
WebSocket
EventSource
form submission
beacon/telemetry
```

### 15.3 Authored text is untrusted display data

All project titles, sheet titles, references, values, labels, IDs, and diagnostic messages must be escaped before insertion into HTML.

No authored string may be treated as executable HTML or JavaScript.

### 15.4 JSON embedding

Embedded JSON must safely escape HTML-closing sequences such as:

```text
</script>
```

and must parse identically to the derived Viewer Model.

### 15.5 Content Security Policy

Add a restrictive static CSP compatible with the self-contained implementation.

The policy should deny by default and explicitly permit only the local inline resources needed by the generated document.

P0 should prohibit dynamic code construction such as `eval` and `new Function`.

### 15.6 No write-back

The Reference Viewer must not attempt filesystem writes or browser persistence of authoritative project data.

---

## 16. Accessibility and Operability Contract

Create or replace the shallow Workbench-only accessibility guidance with a Viewer-specific profile.

Recommended file:

```text
docs/specifications/viewer/viewer-accessibility-profile.md
```

Recommended stable ID:

```text
AIXEM-SPEC-VIEWER-A11Y-001
```

### 16.1 Keyboard operability

Every required viewer command must be reachable without a pointer.

### 16.2 Visible focus

Interactive controls must have a visible focus state independent from hover state.

### 16.3 Stateful controls

Mode, layer, and toggle controls should expose semantic state through appropriate attributes such as:

```text
aria-pressed
aria-selected
aria-expanded
aria-current
```

where applicable.

### 16.4 No color-only meaning

Selection, errors, connectivity, crossings, and junctions must remain understandable without color as the sole carrier.

This preserves the existing semantic-color-independence principle.

### 16.5 Navigator as accessible alternative to canvas hit targets

The canvas may contain many SVG objects. The qualified navigator must provide a practical keyboard-accessible path to semantic objects without forcing every SVG primitive into the page tab order.

### 16.6 Narrow viewport

At narrow sizes, required information should move into tabs/drawers/stacked panels rather than simply disappearing.

Hiding the inspector entirely is not sufficient for Reference Viewer conformance if inspection becomes impossible.

---

## 17. Visual Contract Boundary

### 17.1 Separate schematic visual language from application chrome

Current documentation partially mixes:

```text
schematic visual language
workbench presentation
```

Refactor authority so that:

```text
schematic visual profile
  owns drawing appearance

viewer visual profile
  owns viewer chrome and selection presentation
```

### 17.2 Viewer style may not alter drawing authority

Viewer CSS may:

```text
highlight
hide a presentation layer
show focus
show selection halo
change application chrome
```

but may not:

```text
move a port
move a component
move a route
change junction meaning
change text authority
change project-net membership
```

### 17.3 Vendor neutrality remains mandatory

Preserve ADR-0003:

- original AIXEM icons;
- original layout tokens;
- no vendor branding;
- no copied vendor UI assets;
- conventional CAD interaction patterns may be used without pixel replication.

---

## 18. Renderer and Viewer Boundary

### 18.1 Renderer owns deterministic resolved products

The renderer remains responsible for:

```text
SVG
resolved scene
resolved project scene
render manifest
project validation
```

### 18.2 Viewer adapter owns consumption indexes

The Viewer Model Builder owns:

```text
capability derivation
qualified object index
search index
view availability
inspector-ready projections
viewer provenance references
```

It may not invent semantic facts.

### 18.3 Viewer renderer owns HTML composition

The HTML viewer layer owns only:

```text
UI layout
embedded assets
Viewer Model embedding
runtime control wiring
presentation state
```

### 18.4 Do not generate HTML directly inside semantic renderer logic

The current `render_project.py` should be narrowed.

Recommended implementation split:

```text
implementation/schematic/
├── render_project.py
└── viewer/
    ├── __init__.py
    ├── model.py
    ├── core.py
    ├── reference_viewer.py
    ├── review_workbench.py
    └── templates/
        ├── viewer.html.j2
        └── workbench.html.j2
```

The existing Jinja2 dependency may be reused; do not add a web application framework.

---

## 19. Required Viewer Capabilities by Project Type

| Capability | aixproj/1 single-sheet | aixproj/2 multi-sheet |
|---|---:|---:|
| Sheet View | MUST | MUST |
| Overview View | N/A | MUST |
| Composite View | N/A | MUST |
| Hierarchy navigation | simple Root/Main allowed | MUST data-driven |
| Component selection | MUST | MUST |
| Local-net selection | MUST | MUST |
| Interface-port selection | when feature exists | MUST when ports exist |
| Project-net selection | N/A | MUST |
| Qualified search | SHOULD | MUST |
| Sheet-scoped layers | MUST | MUST |
| Pan / Zoom / Fit | MUST | MUST all views |
| Diagnostics | Viewer MAY omit | Workbench MUST show available diagnostics |
| Remote dependencies | MUST NOT require | MUST NOT require |
| Authoring/write-back | MUST NOT | MUST NOT |

---

## 20. Viewer DOM Contract

A stable DOM contract is useful for:

- automated conformance testing;
- browser integrations;
- screenshots and visual QA;
- future embedding;
- agent inspection.

### 20.1 Stable application markers

Recommended root:

```html
<div data-aixem-viewer="1"
     data-aixem-profile="reference-viewer"
     data-aixem-project="motor-controller">
```

### 20.2 View containers

```html
data-aixem-view="sheet"
data-aixem-view="overview"
data-aixem-view="composite"
```

### 20.3 Object markers

Use stable `data-aixem-kind` and `data-aixem-qid`.

Do not make conformance tests depend primarily on CSS class names intended only for styling.

### 20.4 Control markers

Recommended action vocabulary:

```text
data-aixem-action="mode:sheet"
data-aixem-action="mode:overview"
data-aixem-action="mode:composite"
data-aixem-action="zoom-in"
data-aixem-action="zoom-out"
data-aixem-action="fit"
data-aixem-action="clear-selection"
```

### 20.5 DOM contract versioning

Expose:

```html
data-aixem-dom-contract="1"
```

Breaking automation-visible DOM changes require a new DOM contract version even if CSS appearance changes do not.

---

## 21. Behavioral Conformance Corpus

Create:

```text
validation/corpus/reference-viewer-1/
```

### 21.1 Core cases

| ID | Case | Purpose |
|---|---|---|
| V001 | Legacy single-sheet viewer | Sheet-only Reference Viewer baseline |
| V002 | Multi-sheet three-mode viewer | Sheet / Overview / Composite behavior |
| V003 | Data-driven hierarchy navigation | real project hierarchy and active sheet |
| V004 | Same-name local nets | prove qualified identity/search isolation |
| V005 | Project-net selection | highlight all declared members/routes |
| V006 | Interface-port inspection | local/project relationship inspector |
| V007 | Sheet-scoped layer visibility | no cross-sheet layer leakage |
| V008 | Cross-view selection continuity | project-net persists across Overview/Composite |
| V009 | Component search navigation | result opens owning Sheet View |
| V010 | Pan/zoom/fit | deterministic supported viewport operations |
| V011 | Keyboard-only inspection | required controls operable without pointer |
| V012 | Narrow viewport | navigation/inspection remain available |
| V013 | Offline/network denial | zero external requests |
| V014 | Hostile authored text | HTML/script injection safely escaped |
| V015 | DOM qualified identity | no duplicate IDs or ambiguous QIDs |
| V016 | Ten-sheet project | scale and interaction baseline |
| V017 | Viewer/Workbench separation | distinct profiles from shared core |
| V018 | Three-run HTML determinism | viewer/workbench/model byte stability |

### 21.2 Visual cases

Capture at minimum:

```text
single-sheet desktop
single-sheet narrow
multi-sheet Sheet desktop
multi-sheet Overview desktop
multi-sheet Composite desktop
multi-sheet narrow
project-net selected
interface selected
layer hidden
keyboard focus visible
```

### 21.3 Security negative fixtures

Include authored strings containing:

```text
<script>
</script>
<img onerror=...>
quotes
ampersands
angle brackets
Unicode control/edge cases
```

The exact text must display safely and never execute.

### 21.4 Structural negative fixtures

Viewer generation should fail closed for internally inconsistent derived inputs such as:

```text
duplicate qualified ID
missing referenced view object
project-net member absent from Viewer Model index
invalid active first sheet derivation
unsupported required Viewer Model schema
```

---

## 22. Browser-Level Conformance Tests

Add Playwright-based tests rather than relying only on HTML string inspection.

Recommended files:

```text
tests/conformance/test_reference_viewer.py
tests/conformance/test_viewer_security.py
tests/conformance/test_viewer_accessibility.py
```

### 22.1 Required browser assertions

Automate:

1. page loads with JavaScript enabled and network blocked;
2. no console errors;
3. default mode is deterministic;
4. hierarchy click changes active sheet;
5. mode controls switch visible view;
6. search returns correct qualified object;
7. component search result opens owning sheet;
8. local-net selection does not highlight same-name net in another sheet;
9. project-net selection highlights all expected project segments;
10. layer toggle affects only one qualified sheet/layer;
11. Escape clears selection;
12. `0` fits current view;
13. keyboard can reach required controls;
14. narrow viewport retains navigation and inspector access;
15. no network request is attempted;
16. hostile text does not create executable DOM nodes.

### 22.2 Deterministic HTML tests

For identical staged inputs, record hashes of:

```text
viewer-model.json, if emitted
viewer.html
workbench.html
```

across three complete renders.

### 22.3 Screenshot evidence

Extend the existing capture tool rather than adding another screenshot framework.

Screenshots should be evidence, not the only behavioral validator.

---

## 23. Proposed Normative Requirements

Use a dedicated requirement namespace.

### AIXEM-REQ-VIEWER-0001 — Read-only authority

**MUST.** The Reference Viewer MUST NOT create or modify semantic, layout, or project composition authority.

### AIXEM-REQ-VIEWER-0002 — Distinct Viewer and Workbench profiles

**MUST.** `viewer.html` and `workbench.html` MUST implement separately declared Reference Viewer and Review Workbench profiles rather than being nominal aliases.

### AIXEM-REQ-VIEWER-0003 — Deterministic initial state

**MUST.** Identical Viewer Models MUST initialize to the same mode, active sheet, layer state, and empty selection.

### AIXEM-REQ-VIEWER-0004 — Canonical multi-sheet modes

**MUST.** Hierarchical projects MUST expose Sheet, Overview, and Composite modes.

### AIXEM-REQ-VIEWER-0005 — Qualified object identity

**MUST.** Viewer selection/search/highlighting MUST use sheet-qualified identities where local names can collide.

### AIXEM-REQ-VIEWER-0006 — Selection/inspector closure

**MUST.** The same qualified object selected through canvas, navigator, or search MUST resolve to the same inspector identity.

### AIXEM-REQ-VIEWER-0007 — Project-net highlight closure

**MUST.** Selecting a project net MUST highlight only the routes/interfaces belonging to that declared project net.

### AIXEM-REQ-VIEWER-0008 — Sheet-scoped layer state

**MUST.** Layer visibility MUST remain scoped by sheet and MUST NOT create semantic changes.

### AIXEM-REQ-VIEWER-0009 — Viewport operability

**MUST.** Every required canvas view MUST provide pan, zoom-in, zoom-out, and fit behavior.

### AIXEM-REQ-VIEWER-0010 — Keyboard operability

**MUST.** Required viewer controls MUST be operable through keyboard navigation.

### AIXEM-REQ-VIEWER-0011 — Offline self-containment

**MUST.** P0 `viewer.html` MUST load and operate without required network access or remote assets.

### AIXEM-REQ-VIEWER-0012 — Untrusted text escaping

**MUST.** Authored text MUST be rendered as inert text and MUST NOT create executable HTML/JavaScript.

### AIXEM-REQ-VIEWER-0013 — No network side effects

**MUST.** Reference Viewer runtime MUST make zero external network requests during normal operation.

### AIXEM-REQ-VIEWER-0014 — Responsive inspection

**MUST.** Required navigation and inspection capabilities MUST remain reachable in the declared narrow viewport profile.

### AIXEM-REQ-VIEWER-0015 — Viewer Model schema closure

**MUST.** The generated Viewer Model MUST validate against its published schema and contain no unresolved qualified object references.

### AIXEM-REQ-VIEWER-0016 — Deterministic viewer artifacts

**MUST.** Three complete renders from identical staged inputs MUST produce byte-identical Viewer Model, `viewer.html`, and `workbench.html` artifacts.

---

## 24. Documentation Refactoring Plan

### 24.1 New normative documents

| Path | Role |
|---|---|
| `docs/specifications/viewer/reference-viewer-contract.md` | canonical Viewer product contract |
| `docs/specifications/viewer/review-workbench-contract.md` | engineering review extension |
| `docs/specifications/viewer/viewer-state-and-interaction.md` | runtime state and behavior |
| `docs/specifications/viewer/viewer-security-and-embedding.md` | offline/security/embedding boundary |
| `docs/specifications/viewer/viewer-accessibility-profile.md` | keyboard, focus, semantic state, narrow viewport |
| `docs/specifications/schemas/viewer/aixem-viewer-model-1.schema.json` | derived Viewer Model schema |
| `docs/conformance/reference-viewer.md` | Viewer conformance profile and public claims |

### 24.2 Existing documents to update

| Path | Change |
|---|---|
| `AGENTS.md` | state that Viewer/Workbench are derived read-only surfaces and never authority |
| `docs/specifications/renderer/renderer-contract.md` | define renderer→Viewer Model boundary and exact viewer/workbench output roles |
| `docs/specifications/schematic/visual-profile.md` | remove generic Workbench ownership now moved to Viewer specs; retain schematic presentation only where appropriate |
| `docs/schematic/visual-language.md` | narrow workbench-presentation language; link Viewer profile |
| `docs/architecture/adr/0003-vendor-neutral-ui.md` | clarify Reference Viewer vs Review Workbench vs future Editor |
| `docs/concepts/authority-model.md` | add Viewer runtime-state non-authority layer |
| `docs/concepts/deterministic-builds.md` | include Viewer Model and Viewer HTML determinism |
| `docs/conformance/release-gates.md` | add browser-level Reference Viewer gate |
| `docs/conformance/compatibility.md` | define Viewer contract version compatibility |
| `docs/getting-started/quick-start.md` | open `viewer.html` as the primary viewing surface; Workbench for diagnostics |
| `docs/examples/*` | point normal viewing to Viewer and review evidence to Workbench |
| `docs/_meta/navigation.yaml` | add Viewer specification group |
| `docs/_meta/conformance.yaml` | add viewer-specific validators |

### 24.3 Documentation authority cleanup

After 0.5.4 there should be one clear ownership path:

```text
Reference Viewer product behavior
  → reference-viewer-contract.md

runtime state and interactions
  → viewer-state-and-interaction.md

HTML security/embedding
  → viewer-security-and-embedding.md

application chrome/accessibility
  → viewer-accessibility-profile.md

schematic drawing appearance
  → schematic visual/profile documents

rendered semantic evidence
  → renderer / resolved-scene contracts
```

Do not duplicate the same binding behavior across multiple documents.

---

## 25. Agent Retrieval and Authoring Guidance

### 25.1 Add a Viewer-specific route

Create:

```text
docs/_meta/routes/inspect-viewer.yaml
```

Purpose:

```text
inspect or modify Viewer behavior without loading unrelated semantic authoring documents
```

Recommended retrieval order:

```text
Reference Viewer Contract
→ Viewer State and Interaction
→ Viewer Model schema
→ affected renderer/viewer implementation
→ Viewer conformance cases
```

### 25.2 Update render-review route

`render-review` should distinguish:

```text
visual drawing defect
viewer interaction defect
workbench evidence defect
semantic defect
```

### 25.3 AGENTS.md mandatory rules

Add:

> `viewer.html` is a read-only derived presentation surface.

> `workbench.html` is a read-only engineering-review extension, not an editor.

> Viewer runtime state never changes `.aixem`, `.aixlayout`, or `.aixproj` authority.

> A Viewer defect must not be repaired by changing circuit semantics merely to satisfy presentation behavior.

> Search, selection, and highlighting operate on qualified resolved identities.

> Unsupported authoring controls must not be fabricated in the Viewer or Workbench.

---

## 26. Implementation Change Matrix

### 26.1 Viewer implementation

Recommended conservative split:

```text
implementation/schematic/viewer/
├── model.py
├── core.py
├── reference_viewer.py
├── review_workbench.py
└── templates/
    ├── reference-viewer.html.j2
    └── review-workbench.html.j2
```

### 26.2 Renderer integration

`implementation/schematic/render_project.py` should:

```text
resolve/render schematic artifacts
→ build Viewer Model
→ call viewer renderers
→ record viewer/workbench artifacts
```

It should no longer own large ad-hoc Viewer HTML behavior directly.

### 26.3 Shared Viewer Core

Viewer Core should centralize:

```text
state initialization
mode switching
active sheet
qualified selection
search
layer visibility
pan/zoom/fit
keyboard commands
inspector projection
```

Reference Viewer and Workbench must not duplicate this behavior independently.

### 26.4 Templates

Use static deterministic templates.

Requirements:

- no timestamp based on wall clock;
- no random IDs;
- no unordered iteration;
- stable serialized JSON key ordering;
- stable object order from project/hierarchy semantics;
- local inline assets only in P0.

---

## 27. Migration from Current 0.5.3 Viewer/Workbench

### 27.1 Preserve output filenames

Keep:

```text
viewer.html
workbench.html
```

so external paths do not need immediate migration.

### 27.2 Change their meanings explicitly

0.5.4 meaning:

```text
viewer.html
  AIXEM Reference Viewer 1

workbench.html
  AIXEM Review Workbench 1
```

### 27.3 Remove editor-like no-op controls

From Reference Viewer, remove:

```text
Place wire
Place symbol
Place label
Place junction
Place no-connect
Rotate as authoring command
Save/Undo/Redo authoring implication
```

unless they are later defined by an actual Editor contract.

### 27.4 Preserve useful inspection behavior

Retain and normalize:

```text
entity selection
net selection
project-net selection
interface selection
hierarchy
search
layers
diagnostics in Workbench
```

### 27.5 Legacy project normalization

A legacy single-sheet project may be presented as:

```text
Project
└─ Main
```

internally, but the Viewer should not fabricate a deep hierarchy or multi-sheet controls that do not exist.

---

## 28. Performance and Scale Policy

Measure before optimizing.

### 28.1 Record

```text
Viewer Model bytes
viewer.html bytes
workbench.html bytes
DOM node count
SVG element count
search index size
startup duration
mode-switch duration
search result duration
project-net highlight duration
fit duration
peak browser memory when available
```

### 28.2 H013 / V016 scale gate

The existing 10-sheet hierarchical baseline becomes the minimum Viewer scale gate.

Required:

- page loads reliably in controlled Chromium;
- all three views switch without error;
- qualified search remains functional;
- project-net selection remains functional;
- no pathological browser freeze is observed;
- measurements are recorded as the first Viewer performance baseline.

Do not introduce virtualization or complex caching unless measurements justify it.

---

## 29. Compatibility Policy

### 29.1 Circuit compatibility

0.5.4 Viewer normalization MUST NOT require changes to:

```text
.aixem grammar
.aixsym
.aixlib
aixlayout/1
aixlayout/2
aixproj/1
aixproj/2
```

### 29.2 Resolved output compatibility

Existing resolved scene formats remain renderer evidence contracts.

Viewer Model is an adapter layer and must not redefine them.

### 29.3 Viewer contract compatibility

Compatible Viewer Contract 1 implementations may change:

```text
visual spacing
non-semantic chrome styling
internal JavaScript organization
internal CSS class names
```

provided they preserve:

```text
required capabilities
state semantics
qualified identity
stable DOM contract markers
security requirements
behavioral conformance
```

### 29.4 Breaking changes

Require Viewer Contract 2 for incompatible changes to:

```text
required view modes
qualified identity semantics
Viewer Model schema
DOM automation contract
selection semantics
state initialization semantics
```

---

## 30. Security and Reproducibility Gate

Release must verify:

```text
remote assets                                 0
runtime network requests                      0
unsafe raw authored HTML insertion            0
eval/new Function                             0
random runtime-generated semantic IDs         0
duplicate qualified IDs                       0
viewer semantic write-back paths              0
```

Equivalent staged inputs must produce identical Viewer artifacts.

Browser runtime interaction does not need to serialize identically because it is ephemeral, but startup state and resulting state transitions for the same action sequence must be deterministic.

---

## 31. Implementation Sequence

### Phase 0 — Freeze 0.5.3 Viewer Baseline

1. Record current `viewer.html` and `workbench.html` digests for representative single-sheet and hierarchical cases.
2. Record that current paired outputs are byte-identical where applicable.
3. Capture current desktop screenshots.
4. Record current Workbench Visual Profile requirements.
5. Run full 0.5.3 tests and hierarchical corpus.
6. Preserve SVG/resolved-scene/project-scene baseline hashes.

**Exit criterion:** reproducible baseline proving Viewer normalization does not alter circuit rendering authority.

### Phase 1 — Fix Terminology and Authority

1. Update ADR-0003.
2. Define Reference Viewer, Review Workbench, future Editor.
3. Define read-only authority boundary.
4. Define Viewer runtime state as non-authoritative.
5. Remove documentation that implies Workbench is an editor.

**Exit criterion:** no conflicting terminology remains in normative docs.

### Phase 2 — Publish Viewer Contract 1

1. Write `reference-viewer-contract.md`.
2. Write `review-workbench-contract.md`.
3. Define capability matrix.
4. Define required view behavior.
5. Define required selection and inspector behavior.
6. Define compatibility rules.

**Exit criterion:** implementation can be judged conformant without reading renderer source.

### Phase 3 — Define Viewer Model 1

1. Write Viewer Model contract section.
2. Publish JSON schema.
3. Build deterministic Viewer Model adapter.
4. Validate qualified identity uniqueness.
5. Preserve provenance to resolved scene/project scene.
6. Add schema tests.

**Exit criterion:** Viewer rendering can consume one stable derived model rather than renderer-internal dictionaries.

### Phase 4 — Refactor Viewer Core

1. Move Viewer logic out of monolithic renderer HTML construction.
2. Implement explicit state model.
3. Implement qualified selection.
4. Implement deterministic search.
5. Implement sheet-scoped layer state.
6. Implement shared pan/zoom/fit behavior.
7. Implement keyboard commands.

**Exit criterion:** Viewer Core passes unit tests independent of Workbench diagnostics.

### Phase 5 — Implement Reference Viewer 1

1. Build clean read-only Viewer layout.
2. Remove editor-like controls.
3. Implement single-sheet mode.
4. Implement hierarchical Sheet/Overview/Composite modes.
5. Implement navigator and inspector.
6. Implement view-aware viewport behavior.
7. Add stable DOM contract markers.

**Exit criterion:** V001-V010 pass.

### Phase 6 — Separate Review Workbench 1

1. Build Workbench as Viewer Core extension.
2. Add diagnostics/evidence panels.
3. Keep all semantic viewing behavior shared.
4. Prove `viewer.html` and `workbench.html` are distinct product profiles.
5. Ensure neither exposes unsupported editing.

**Exit criterion:** V017 passes and both profiles satisfy their respective contracts.

### Phase 7 — Security and Accessibility

1. Add restrictive CSP.
2. Prohibit network calls.
3. Add hostile-text fixtures.
4. Add focus-visible behavior.
5. Add ARIA state to toggles/tabs/navigation.
6. Implement narrow viewport panel strategy.
7. Validate keyboard-only workflow.

**Exit criterion:** V011-V014 pass.

### Phase 8 — Browser Conformance

1. Add Playwright behavior tests.
2. Block network during tests.
3. Fail on console errors.
4. Exercise every required mode/action.
5. Extend screenshot capture.
6. Add DOM/QID uniqueness checks.

**Exit criterion:** V001-V017 browser conformance passes.

### Phase 9 — Documentation and Agent Integration

1. Update renderer contract.
2. Update visual/profile ownership.
3. Update authority model.
4. Add `inspect-viewer` route.
5. Update `render-review` route.
6. Update `AGENTS.md`.
7. Regenerate cards/routes/navigation/site.
8. Run documentation dependency and traceability checks.

**Exit criterion:** Viewer behavior can be located through a short route without repository-wide search.

### Phase 10 — Release Closure

1. Run V001-V018.
2. Run all existing hierarchical corpus cases.
3. Run all 0.5.3 symbol/static/authoring regression corpora.
4. Render all reference outputs three times.
5. Compare circuit SVG/resolved-scene hashes against baseline where compatibility requires identity.
6. Verify Viewer/Workbench deterministic hashes.
7. Generate final capability matrix.
8. Generate Viewer conformance report.
9. Regenerate release manifest and integrity evidence.

---

## 32. Three-Pass Verification and Improvement Loop

### PASS 1 — Contract, Authority, and Structural Correctness

Focus:

> Is the Viewer now a formally bounded read-only product rather than an ad-hoc renderer UI?

Gate:

```text
Reference Viewer contract published            PASS
Review Workbench contract published            PASS
Viewer/Workbench/Editor terminology             PASS
Viewer runtime state non-authoritative          PASS
Viewer Model schema                             PASS
qualified identity closure                      PASS
legacy/single-sheet capability mapping          PASS
hierarchical capability mapping                 PASS
unsupported editor controls                     0
normative ownership conflicts                    0
```

A release-critical failure requires fixing the smallest owning contract and repeating PASS 1 completely.

### PASS 2 — Browser Behavior, Security, and Usability

Focus:

> Can a user reliably inspect the rendered circuit in a browser without semantic ambiguity, network dependency, or hidden unsupported behavior?

Gate:

```text
single-sheet Sheet View                         PASS
hierarchical Sheet View                         PASS
Overview View                                   PASS
Composite View                                  PASS
pan/zoom/fit all required canvases              PASS
hierarchy navigation                            PASS
qualified search                                PASS
component/local-net selection                   PASS
interface/project-net selection                 PASS
cross-view project-net highlighting             PASS
sheet-scoped layers                             PASS
keyboard-only required workflow                 PASS
narrow viewport inspection                      PASS
external runtime network requests               0
script/HTML injection executions                0
browser console errors                          0
critical interaction defects                    0
```

### PASS 3 — Regression, Determinism, Documentation, and Claims

Focus:

> Can the Viewer specification be released without damaging existing AIXEM rendering guarantees or overstating capabilities?

Gate:

```text
full repository test suite                      PASS
0.5.3 hierarchical corpus                       PASS
0.5.3 symbol corpus                             PASS
0.5.3 static block corpus                       PASS
authoring corpus                                PASS
V001-V018 viewer corpus                         PASS
legacy circuit rendering regression             PASS
three-run Viewer Model determinism              PASS
three-run viewer.html determinism               PASS
three-run workbench.html determinism            PASS
document dependency graph                       PASS
agent route resolution                          PASS
site/reference regeneration                     PASS
release manifest/integrity                      PASS
unsupported editor claims                       0
Viewer/Workbench role ambiguity                 0
```

A release-critical correction requires restarting PASS 3 from clean staged inputs.

---

## 33. Acceptance Criteria

### 33.1 Product identity

- [ ] `viewer.html` is formally defined as AIXEM Reference Viewer 1.
- [ ] `workbench.html` is formally defined as AIXEM Review Workbench 1.
- [ ] Viewer and Workbench are no longer nominal aliases.
- [ ] Neither is described as an editor.
- [ ] Unsupported authoring controls are absent.

### 33.2 Authority

- [ ] Viewer state is explicitly non-authoritative.
- [ ] Viewer behavior cannot change `.aixem`, `.aixlayout`, or `.aixproj` semantics.
- [ ] Highlighting and layer visibility are presentation-only.
- [ ] No geometry displayed by the Viewer creates connectivity.

### 33.3 Data contract

- [ ] Viewer Model 1 schema is published.
- [ ] Viewer Model is fully derivable from resolved renderer outputs.
- [ ] Viewer Model contains no new semantic authority.
- [ ] All QIDs resolve uniquely.
- [ ] Provenance to input/render digests is retained.

### 33.4 Single-sheet Viewer

- [ ] Sheet View works.
- [ ] Component selection works.
- [ ] Local-net selection works.
- [ ] Search works.
- [ ] Layer controls work.
- [ ] Pan/zoom/fit work.
- [ ] Inspector works.

### 33.5 Multi-sheet Viewer

- [ ] Sheet / Overview / Composite all work.
- [ ] Hierarchy is data-driven.
- [ ] Search is sheet-qualified.
- [ ] Interface ports are inspectable.
- [ ] Project nets are inspectable.
- [ ] Same-name local nets remain visually/semantically isolated.
- [ ] Project-net selection highlights declared membership across views.
- [ ] Layers remain sheet-scoped.

### 33.6 Security

- [ ] No required remote asset exists.
- [ ] No runtime network request occurs.
- [ ] Authored text is safely escaped.
- [ ] Embedded JSON cannot terminate executable script context.
- [ ] No `eval`/dynamic-code construction exists.
- [ ] Restrictive CSP is present.

### 33.7 Accessibility and responsiveness

- [ ] All required controls are keyboard reachable.
- [ ] Focus is visibly indicated.
- [ ] Toggle/tab state is programmatically exposed.
- [ ] Color is not the sole semantic cue.
- [ ] Narrow viewport retains navigation and inspection capability.

### 33.8 Determinism

- [ ] Viewer Model is byte-stable for equivalent locked inputs.
- [ ] `viewer.html` is byte-stable.
- [ ] `workbench.html` is byte-stable.
- [ ] Three complete render runs produce identical Viewer artifact digests.

### 33.9 Evidence

- [ ] V001-V018 pass.
- [ ] Browser behavior tests pass.
- [ ] Screenshot evidence is regenerated.
- [ ] Capability matrix is generated.
- [ ] Requirement traceability is complete.
- [ ] Three verification passes are recorded.

---

## 34. Non-Goals for 0.5.4 P0

Explicitly outside this release:

- editing component placement;
- drawing wires;
- changing routes;
- changing project nets;
- changing hierarchy;
- changing properties;
- saving `.aixem`/`.aixlayout`/`.aixproj`;
- undo/redo authoring model;
- multi-user collaboration;
- cloud synchronization;
- server-side viewer runtime;
- arbitrary remote project loading;
- filesystem workspace management;
- reusable Viewer plugin API;
- custom JavaScript extensions;
- vendor-compatible editor UI;
- KiCad/OrCAD editor emulation;
- PCB/Gerber viewing;
- waveform/simulation viewing;
- mobile-first editing.

These require separate evidence and contracts.

---

## 35. P1 / P2 Extension Gates

### P1 — After Reference Viewer 1 stability

Evidence-gated candidates:

1. optional URL fragment/deep-link state for a selected QID;
2. optional print-focused view;
3. optional export of current SVG view;
4. project overview mini-map;
5. large-project search indexing optimization;
6. collapse/expand hierarchy state;
7. explicit pin/endpoint-level selection contract;
8. richer diagnostic filtering;
9. optional non-authoritative session state serialization.

### P2 — Separate product decision

Only after a dedicated ADR:

```text
AIXEM Editor
```

Possible capabilities:

- edit placement;
- route wires;
- edit component properties;
- edit interface ports;
- edit project nets;
- save authoritative files;
- undo/redo;
- structured command model.

The Editor must not be smuggled into the Viewer contract incrementally.

---

## 36. Recommended Public Capability Claim

If all P0 gates pass, the release may state:

> **AIXEM provides a deterministic, self-contained, read-only HTML Reference Viewer for single-sheet and hierarchical multi-sheet schematic projects, with qualified semantic inspection, Sheet/Overview/Composite project views, project-net highlighting, hierarchy navigation, sheet-scoped layers, offline operation, and browser-level conformance evidence.**

Do not state:

> AIXEM provides a schematic editor.

Do not state:

> The Workbench can author or save circuits.

Do not state:

> AIXEM reproduces KiCad or OrCAD user interfaces.

---

## 37. Recommended Priority

### P0 — Implement now

1. freeze the current Viewer baseline;
2. normalize Viewer/Workbench/Editor terminology;
3. publish Reference Viewer Contract 1;
4. publish Review Workbench Contract 1;
5. define Viewer Model 1 and schema;
6. define qualified DOM identity contract;
7. define explicit Viewer state model;
8. refactor shared Viewer Core;
9. remove fake authoring controls;
10. implement normalized pan/zoom/fit;
11. normalize Sheet/Overview/Composite behavior;
12. normalize selection and inspector behavior;
13. normalize qualified search;
14. normalize sheet-scoped layer behavior;
15. add security/CSP/text-escaping requirements;
16. add keyboard and responsive inspection requirements;
17. add Playwright behavioral conformance;
18. add V001-V018 corpus;
19. update agent routes and documentation ownership;
20. run three complete verification passes.

### P1 — Stability improvements only

1. deep links;
2. print/export presentation;
3. endpoint-level inspection;
4. large-project UI optimization;
5. optional session-state export.

### P2 — Separate Editor program

No editing functionality enters Viewer 1 without a new architecture decision and specification family.

---

## 38. Definition of Done

AIXEM Viewer normalization is complete only when all of the following are true.

### Specification

- [ ] A Reference Viewer has one canonical normative contract.
- [ ] A Review Workbench has one canonical extension contract.
- [ ] Viewer state/interaction has a canonical owner.
- [ ] Viewer security/embedding has a canonical owner.
- [ ] Viewer accessibility has a canonical owner.
- [ ] Viewer Model has a published machine-readable schema.

### Architecture

- [ ] Viewer consumes resolved evidence rather than redefining circuit semantics.
- [ ] Viewer Model is derived only.
- [ ] Viewer Core is shared by Viewer and Workbench.
- [ ] Renderer logic is no longer coupled to a monolithic ad-hoc HTML implementation.
- [ ] Viewer and Workbench are distinct outputs with distinct roles.

### Behavior

- [ ] Single-sheet projects are fully inspectable.
- [ ] Hierarchical projects support Sheet/Overview/Composite.
- [ ] Pan/zoom/fit are consistent.
- [ ] Qualified search is deterministic.
- [ ] Selection resolves through qualified identity.
- [ ] Project-net highlighting is correct across views.
- [ ] Sheet layer state is isolated.
- [ ] Inspector content is defined and deterministic.

### Safety

- [ ] Viewer is strictly read-only.
- [ ] No fake editor actions remain.
- [ ] No network request is required or emitted.
- [ ] Authored text cannot execute code.
- [ ] CSP and escaping tests pass.

### Accessibility

- [ ] Required controls work with keyboard only.
- [ ] Focus is visible.
- [ ] required state is exposed semantically.
- [ ] narrow viewport remains inspectable.

### Evidence

- [ ] V001-V018 pass.
- [ ] existing 0.5.3 circuit conformance remains green.
- [ ] three complete Viewer renders are byte-deterministic.
- [ ] screenshots are regenerated.
- [ ] requirement traceability has no gap.
- [ ] all three release verification passes are complete.

---

## 39. Final Target State

```text
                           AIXEM PROJECT
                                │
                  authoritative design formats
                                │
                                ▼
                        Production Renderer
                                │
           ┌────────────────────┴────────────────────┐
           │                                         │
           ▼                                         ▼
   resolved-scene/1                        resolved-project-scene/1
   leaf drawing SVG                        overview/composite SVG
           │                                         │
           └────────────────────┬────────────────────┘
                                │
                                ▼
                         Viewer Model 1
                     derived / deterministic
                                │
                                ▼
                          Viewer Core 1
              ┌─────────────────┼─────────────────┐
              │                 │                 │
          Navigation         Selection         Viewport
              │                 │                 │
      Project→Sheet      Qualified QIDs      Pan/Zoom/Fit
      Search/Layers      Inspector           View state
              └─────────────────┼─────────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
       Reference Viewer 1            Review Workbench 1
          viewer.html                  workbench.html
         strict read-only             read-only + evidence
                 │                             │
                 └──────────────┬──────────────┘
                                │
                                ▼
                      Browser Conformance
               Playwright + deterministic evidence
```

The 0.5.4 quality bar should be:

> **AIXEM does not merely emit an HTML page that happens to display a schematic. It publishes a versioned Reference Viewer contract in which every visible object has stable qualified identity, every interaction is read-only and deterministic, every multi-sheet view derives from declared project semantics, and the browser behavior itself is conformance-tested.**

This gives AIXEM a proper viewing standard without prematurely turning the reference platform into a large editor application.
