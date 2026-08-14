# AIXEM 0.5.3 — Hierarchical Multi-Sheet Composition & Project Routing Plan

**Target release:** AIXEM 0.5.3 candidate  
**Plan status:** Implementation-ready  
**Baseline:** AIXEM 0.5.2 (2026-08-11)  
**Primary objective:** Add a conservative, deterministic hierarchy layer that can load multiple independent schematic files, connect them through explicit semantic interfaces, route those connections at project level, and render the design as individual sheets, a hierarchy overview, or a single composite workspace.  
**Compatibility objective:** Preserve all valid AIXEM 0.5.2 single-sheet projects without migration.  
**Documentation language:** English only.

---

## 1. Executive Summary

AIXEM 0.5.2 already separates circuit meaning from drawing geometry correctly:

```text
.aixem
  entities / endpoints / local nets
        ↓
.aixlayout.json
  placement / local route geometry / layers
        ↓
.aixproj.json
  digest-locked project entry
        ↓
production renderer
```

The missing layer is **project composition**.

The actual 0.5.2 implementation currently assumes:

- one `.aixem` semantic source per project;
- one `.aixlayout.json` per project;
- one `sheet` object per layout;
- multiple `layers[]` only inside that one sheet;
- one source path and one layout path loaded directly by `ProjectRenderer`;
- local semantic nets with at least two semantic endpoints;
- no executable semantic sheet-port model;
- no executable cross-sheet project-net model;
- no real data-driven Workbench hierarchy.

The current `sheet-organization.md` and `hierarchical-reference.md` documents describe the intended direction, but they are informative guidance rather than an implemented multi-sheet contract.

AIXEM 0.5.3 should close this gap without collapsing many circuits into one giant source file and without abusing visual layers as schematic pages.

The target architecture is:

```text
                          AIXEM PROJECT
                              │
                         aixproj/2
                              │
          explicit sheet list + hierarchy + project nets
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
       POWER               CONTROL               I/O
          │                   │                   │
     power.aixem         control.aixem          io.aixem
       @VOUT                @VCC                @VCC
       @GND                 @GND                @GND
          │                   │                   │
     power.layout        control.layout         io.layout
          │                   │                   │
          └──────── semantic interface ports ────┘
                              │
                    Project Semantic Graph
                              │
                   deterministic project routing
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
      Sheet View         Overview View       Composite View
```

The key design rule remains unchanged:

> **Geometry never creates connectivity.**

Local circuit connectivity remains in `.aixem`. Cross-sheet connectivity is declared explicitly by `aixproj/2`. Layout files only provide coordinates and route geometry for already-declared semantic endpoints.

---

## 2. Baseline Findings from AIXEM 0.5.2

### 2.1 Existing strengths to preserve

AIXEM 0.5.2 already provides the required leaf-level foundation:

1. geometry-free semantic source;
2. explicit endpoint-based local net membership;
3. explicit no-connect intent;
4. explicit local layout and route geometry;
5. presentation layers inside a sheet;
6. digest-locked file references;
7. deterministic SVG and resolved-scene output;
8. total component-to-symbol port binding;
9. production renderer reuse across validation corpora;
10. route-first, low-context agent documentation.

0.5.3 should extend those contracts rather than replace them.

### 2.2 Current hard limitations

The 0.5.2 project schema contains single objects:

```text
project.source
project.layout
```

not:

```text
sources[]
layouts[]
sheets[]
```

The layout schema contains:

```text
layout.sheet
layout.layers[]
```

where `layers[]` are presentation layers, not schematic pages.

The renderer follows the same assumption and directly resolves one source and one layout.

### 2.3 Important semantic constraint discovered in the current parser

The current `.aixem` parser rejects a semantic net with fewer than two endpoints.

That matters for hierarchical design.

A common child sheet may contain:

```text
U1.VCC ──────────────── hierarchical VCC port
```

If the hierarchical port exists only in `aixproj/2`, the local `.aixem` source sees only one endpoint (`U1.VCC`) and cannot represent the local net cleanly under the current rule.

Therefore a correct multi-sheet design needs a **real semantic sheet/interface endpoint inside the leaf semantic model**.

This is the one narrowly justified semantic extension required by the current architecture.

### 2.4 Sheet versus Layer

The target hierarchy must be normative:

```text
Project
└── Sheet
    └── Layer
```

A **Sheet** is an independent semantic/layout unit.

A **Layer** is a presentation subdivision within one sheet.

The system must never use layers to simulate independent sheets.

---

## 3. Conservative Engineering Principles

### 3.1 Add only one new leaf semantic concept

P0 may add exactly one new semantic concept to `.aixem`:

> **Interface Port** — a top-level semantic endpoint representing a sheet boundary.

Do not add buses, module instances, page objects, global nets, or block instances to the `.aixem` grammar in the same release.

### 3.2 Use feature negotiation rather than breaking the base language

Preferred form:

```aixem
aixem 1.0
model control title="Controller"
feature component.graphics@1 required=true
feature explicit.layout@2 required=true
feature hierarchical.interface@1 required=true

port VCC direction=input role=power
port GND direction=passive role=power

component U1 type=example:mcu refdes=U1
net vcc = U1.VCC @VCC
net gnd = U1.GND @GND
```

The 0.5.3 contract should standardize `@<port-id>` as the interface-endpoint syntax. A grammar ADR should record the rationale and rejected alternatives, but implementation should not leave the lexical form open-ended.

Existing files that do not declare `hierarchical.interface@1` remain unchanged.

### 3.3 Keep existing schema URIs immutable

Do not mutate released v1 contracts silently.

Keep:

```text
.../aixproj/1
.../aixlayout/1
```

and add:

```text
.../aixproj/2
.../aixlayout/2
```

### 3.4 Keep local and project semantics separate

`.aixem` owns:

```text
local entities
local component endpoints
interface ports
local nets including interface endpoints
no-connect intent
```

`aixproj/2` owns:

```text
which sheets participate
sheet hierarchy
which interface ports are connected across sheets
project-net identity
project build lock and render policy
```

`.aixlayout/2` owns:

```text
component positions
local route geometry
interface-port positions
local net paths reaching interface ports
layers
annotations
```

### 3.5 Never auto-connect by name

These must remain independent unless explicitly connected:

```text
power:gnd
control:gnd
io:gnd
```

Text equality is never connectivity authority.

Only a project semantic declaration may connect them.

### 3.6 Never flatten as the canonical model

The renderer may derive a global graph or one large composite SVG, but canonical sources remain separate leaf circuits.

Do not generate one rewritten mega-`.aixem` as the authoritative project representation.

### 3.7 Determinism before routing sophistication

The first project router should be simple, orthogonal, and deterministic.

Avoid stochastic force-directed layouts and complex optimization in P0.

---

## 4. Leaf Semantic Interface Contract

### 4.1 New `port` statement

Normative target grammar:

```text
port <id> [direction=<value>] [role=<value>] [label=<text>]
```

Example:

```aixem
port VIN direction=input role=power
port ENABLE direction=input role=control
port STATUS direction=output role=signal
port GND direction=passive role=power
```

### 4.2 Interface endpoint reference

Normative target endpoint token:

```text
@<port-id>
```

Example:

```aixem
net vin = F1.2 C1.1 @VIN
net enable = U1.EN @ENABLE
net status = U1.STATUS @STATUS
```

This solves the current minimum-two-endpoint restriction naturally:

```text
U1.EN + @ENABLE = 2 semantic endpoints
```

### 4.3 Interface port rules

Each interface port MUST:

- have a unique ID within the semantic model;
- be a real semantic endpoint;
- resolve in net and no-connect validation;
- occur in at most one local semantic net;
- not be both net-connected and no-connect;
- remain independent of presentation coordinates;
- remain stable across layout changes.

A project-connected interface port MUST belong to exactly one local semantic net.

### 4.4 Direction and role vocabulary

Keep P0 vocabulary small.

Recommended `direction` values:

```text
input
output
bidirectional
passive
```

Recommended optional `role` values:

```text
signal
power
clock
reset
control
analog
```

P0 should use these primarily for diagnostics and presentation.

Do not implement a full ERC type system during this release.

### 4.5 Local semantic authority

A project cannot change which local net an interface port belongs to.

For example:

```aixem
net vcc = U1.VCC @VCC
```

means `@VCC` belongs to local net `vcc`.

`aixproj/2` may connect `control:@VCC` to another sheet port, but it may not rebind `@VCC` to a different local net.

---

## 5. `aixlayout/2` Hierarchical Port Presentation

### 5.1 Why a layout v2 is needed

An interface port is semantic, but the renderer still needs to know where it appears on the sheet.

Do not put coordinates into `.aixem` or `aixproj/2`.

Add one presentation structure to `aixlayout/2`:

```text
sheetPorts[]
```

### 5.2 Preferred shape

```json
{
  "layout": {
    "designId": "control",
    "sheet": {
      "width": 297,
      "height": 210
    },
    "layers": [],
    "placements": [],
    "connections": [],
    "sheetPorts": [
      {
        "port": "VCC",
        "x": 10.0,
        "y": 40.0,
        "side": "left",
        "layer": "connections",
        "label": "VCC"
      }
    ]
  }
}
```

### 5.3 Existing route paths should reach interface endpoints

The existing local connection model should be extended so route sides may resolve either:

```text
entity.port
```

or:

```text
@interface-port
```

Example:

```json
{
  "net": "vcc",
  "paths": [
    {
      "from": { "endpoint": "U1.VCC" },
      "to": { "endpoint": "@VCC" },
      "via": [[40, 40]]
    }
  ]
}
```

The renderer resolves `@VCC` coordinates from `sheetPorts[]`.

### 5.4 Presentation closure

For every semantic interface port that is intended to be visible:

- exactly one `sheetPorts[]` placement must exist;
- the port ID must resolve to the local semantic model;
- coordinates must be valid;
- side/orientation must be deterministic;
- the local connection route must cover the interface endpoint when the port is net-connected.

### 5.5 No layout authority leakage

Changing:

```text
x
y
side
label
layer
```

must never change which local net or project net the port belongs to.

### 5.6 Interface-port visual glyph

The sheet-port marker should be a small grid-aligned schematic boundary glyph rendered from existing SVG/vector operations. It is not a new `.aixsym` primitive and does not require a component-library entry.

The visual profile should define only the minimum stable properties needed for consistency: anchor point, side/orientation, label offset, stroke class, and selected/highlight state.

---

## 6. `aixproj/2` Multi-Sheet Composition Contract

### 6.1 Core structure

Preferred project structure:

```json
{
  "schema": "https://schemas.aixem.org/component-graphics/aixproj/2",
  "formatVersion": "2.0",
  "project": {
    "id": "motor-controller",
    "title": "Motor Controller",
    "applicationProfile": "aixem.schematic.multisheet@1",
    "sheets": [
      {
        "id": "power",
        "title": "Power",
        "source": {
          "path": "circuits/power.aixem",
          "digest": "sha256:...",
          "mediaType": "text/x-aixem"
        },
        "layout": {
          "path": "layouts/power.aixlayout.json",
          "digest": "sha256:...",
          "mediaType": "application/json"
        }
      },
      {
        "id": "control",
        "title": "Controller",
        "source": {
          "path": "circuits/control.aixem",
          "digest": "sha256:...",
          "mediaType": "text/x-aixem"
        },
        "layout": {
          "path": "layouts/control.aixlayout.json",
          "digest": "sha256:...",
          "mediaType": "application/json"
        }
      }
    ],
    "projectNets": [
      {
        "id": "vcc_5v",
        "members": [
          { "sheet": "power", "port": "VOUT" },
          { "sheet": "control", "port": "VCC" }
        ]
      },
      {
        "id": "gnd",
        "members": [
          { "sheet": "power", "port": "GND" },
          { "sheet": "control", "port": "GND" }
        ]
      }
    ],
    "libraries": [
      {
        "path": "libraries/project.aixlib.json",
        "digest": "sha256:...",
        "mediaType": "application/json"
      }
    ],
    "renderPolicy": {
      "purpose": "schematic-review",
      "backend": "svg",
      "fontPolicy": "bundled-metrics",
      "remoteAssets": "deny"
    }
  }
}
```

The sample is a target-shape example; exact media-type strings and any additional required lock fields must follow the existing project-lock policy and the final v2 schema.

### 6.2 Sheet identity

Each sheet MUST have:

```text
id
title
source ref
layout ref
```

Optional:

```text
parent
order
purpose
metadata
```

### 6.3 Project-net semantics

A project net declares equivalence between interface endpoints from different sheets.

Example:

```text
project-net vcc_5v
 ├─ power:@VOUT
 ├─ control:@VCC
 └─ io:@VCC
```

Each member must resolve to a declared `port` in the referenced leaf `.aixem` file.

### 6.4 Project-net closure rules

A project net MUST:

- have a unique project-level ID;
- contain at least two members;
- reference existing sheets;
- reference existing semantic interface ports;
- contain no duplicate member;
- not claim an interface port already owned by another project net in P0.

### 6.5 Transitive equivalence collision rule

Project-net validation must consider local semantic connectivity, not only direct member duplication.

If two interface ports belong to the same local net, they are already electrically equivalent inside the leaf sheet. They MUST NOT be assigned to two different project-net IDs.

Example invalid project:

```text
local sheet net: shared = @A @B U1.1
project-net X includes sheet:@A
project-net Y includes sheet:@B
```

Because `@A` and `@B` are connected by the same local semantic net, project nets `X` and `Y` would actually be one electrical equivalence class. The resolver must reject this as a project-net equivalence collision rather than silently short or merge named project nets.

Recommended diagnostic:

```text
PROJECT_NET_EQUIVALENCE_COLLISION
```

### 6.6 No name-based global nets

Add an explicit normative rule:

> Local net IDs and interface-port IDs do not become project-connected merely because their textual names match across sheets.

### 6.7 Legacy `aixproj/1`

`aixproj/1` remains supported exactly as a single-sheet project.

The implementation may normalize it internally as:

```text
Project
└─ Sheet(main)
   ├─ source = legacy project.source
   └─ layout = legacy project.layout
```

This normalization is derived behavior only and must not rewrite source files.

---

## 7. Hierarchy Model

### 7.1 Organizational hierarchy

P0 hierarchy uses an optional `parent` relation on sheet records.

Example:

```text
system
├─ power
├─ control
│  └─ debug
└─ io
```

Every node shown above is a real sheet in P0.

Do not introduce abstract grouping nodes until a concrete need is proven.

### 7.2 Hierarchy validation

Requirements:

- sheet IDs unique;
- parent sheet must exist;
- no self-parent;
- no cycles;
- deterministic root ordering;
- deterministic child ordering using explicit `order`, then stable ID.

### 7.3 Hierarchy does not imply connectivity

Parent-child relationships are organizational only.

This:

```text
control
└─ debug
```

creates no electrical connection by itself.

Connectivity exists only through `projectNets[]`.

### 7.4 No reusable hierarchical instances in P0

P0 sheets are project-unique identities.

The same source may not be instantiated repeatedly with independent semantic namespaces unless a later module-instance ADR explicitly defines that behavior.

---

## 8. Project Semantic Graph — The Missing Intermediate Layer

This graph is the principal new intermediate structure.

### 8.1 Graph form

For project net `vcc_5v`:

```text
ProjectNet(vcc_5v)
 ├─ SheetPort(power:@VOUT)
 │    └─ LocalNet(power:vout_5v)
 │         ├─ U1.OUT
 │         └─ @VOUT
 ├─ SheetPort(control:@VCC)
 │    └─ LocalNet(control:vcc)
 │         ├─ U2.VCC
 │         └─ @VCC
 └─ SheetPort(io:@VCC)
      └─ LocalNet(io:vcc)
           ├─ J1.VCC
           └─ @VCC
```

### 8.2 Required queries

The resolver must support deterministic answers to:

```text
Which sheets participate in project net X?
Which local net owns sheet port Y?
Which local endpoints are transitively connected through project net X?
Which project ports are unconnected?
Which project nets cross a hierarchy boundary?
Which leaf file owns a failing endpoint?
```

### 8.3 Qualified resolved identities

Recommended normalized identities:

```text
sheet:<sheet-id>
entity:<sheet-id>:<entity-id>
local-net:<sheet-id>:<net-id>
interface:<sheet-id>:<port-id>
project-net:<project-net-id>
```

These are resolved identifiers, not necessarily user-authored syntax.

### 8.4 Preserve provenance

The graph must retain:

```text
source path
source digest
layout path
layout digest
line or declaration owner where practical
```

so an AI agent or validator can repair the smallest owning file.

---

## 9. Project-Level Routing

### 9.1 Two routing layers

AIXEM must distinguish:

```text
LOCAL ROUTING
component/interface endpoints within one sheet
→ owned by aixlayout
```

from:

```text
PROJECT ROUTING
sheet interface ports between sheets in overview/composite space
→ derived from project-net semantics
```

### 9.2 P0 project router

Use a deterministic orthogonal algorithm.

Recommended sequence:

1. compute sheet block/canvas bounds;
2. transform sheet-port anchors to project coordinates;
3. escape outward from each sheet edge;
4. route horizontal/vertical trunks;
5. join multi-member nets at explicit deterministic junctions;
6. apply stable tie-break rules based on project-net ID and sheet order.

### 9.3 Junction semantics

Project routing follows the same conceptual rule as local routing:

- geometry crossing does not connect nets;
- branch junction inside one declared project net is explicit;
- different project nets can cross visually without connectivity.

### 9.4 P0 route diagnostics

Recommended IDs:

```text
PROJECT_ROUTE_UNRESOLVED_PORT
PROJECT_ROUTE_SHEET_INTERSECTION
PROJECT_ROUTE_OVERLAP
PROJECT_ROUTE_ZERO_LENGTH
PROJECT_ROUTE_NON_ORTHOGONAL
PROJECT_ROUTE_EXCESSIVE_BENDS
```

Only correctness-affecting failures should block release.

---

## 10. Rendering Model

### 10.1 Preserve leaf rendering

Each sheet must render independently through the production leaf pipeline.

Outputs:

```text
sheets/power.svg
sheets/power.resolved-scene.json
sheets/control.svg
sheets/control.resolved-scene.json
...
```

### 10.2 Resolved project scene

Add:

```text
resolved-project-scene.json
```

Minimum content:

```text
project identity
schema/version
sheet hierarchy
per-sheet source/layout digests
per-sheet resolved-scene digests
interface ports
project nets
project routing geometry
composite transforms
project diagnostics
aggregate statistics
```

### 10.3 View A — Sheet View

Displays one sheet at normal schematic scale.

Requirements:

- current local layers remain available;
- interface-port symbols/labels are visible;
- selecting an interface port shows its local net and project net;
- navigation uses real hierarchy data;
- no wire is drawn directly through page boundaries.

### 10.4 View B — Project Overview

Displays each sheet as a compact block with exposed interface ports.

Example:

```text
┌──────── POWER ────────┐
│ VOUT              GND │
└─────────┬──────────┬──┘
          │          │
      VCC_5V        GND
          │          │
┌─────────▼──────────▼──┐
│      CONTROLLER       │
│ VCC               GND │
└───────────────────────┘
```

P0 block placement should be deterministic and hierarchy-aware.

### 10.5 View C — Composite View

Displays complete leaf sheet canvases in one large workspace.

Project-level wires connect transformed interface-port anchors between sheet canvases.

This view gives the user the requested one-screen representation while preserving independent source/layout files.

### 10.6 Composite identity

The composite renderer MUST preserve sheet scope in DOM/resolved IDs.

For example:

```text
data-sheet="control"
data-entity="U1"
data-local-net="vcc"
data-project-net="vcc_5v"
```

Do not flatten identity into ambiguous unqualified names.

### 10.7 P1 explicit overview layout

P0 should use deterministic auto-placement first.

If realistic projects prove that users need persistent manual sheet-block positions and project-wire bends, then add an evidence-gated P1 presentation sidecar, tentatively:

```text
.aixoverview.json
```

It may own only:

```text
sheet block positions
sheet transforms
project route bends
project annotations
```

It must never own project-net membership.

---

## 11. Renderer Refactoring

### 11.1 Current problem

The current `ProjectRenderer` couples:

```text
project loading
single source resolution
single layout resolution
leaf validation
leaf SVG generation
Workbench generation
```

That should not be duplicated per sheet.

### 11.2 Target internal structure

Recommended minimal refactor:

```text
LeafSheetResolver
  source + layout + libraries
  → resolved leaf semantic/layout scene

LeafSheetRenderer
  resolved leaf scene
  → SVG

ProjectCompositionResolver
  aixproj/2 + leaf scenes
  → hierarchy + interface graph + project nets

ProjectRouter
  resolved project graph
  → overview/composite route geometry

ProjectWorkbenchRenderer
  leaf scenes + project scene
  → multi-view Workbench
```

### 11.3 Compatibility wrapper

The existing public command/API that renders `aixproj/1` must continue to work.

Do not force callers to know whether the project is v1 or v2.

### 11.4 Shared libraries

P0 should keep the current project-level shared `libraries[]` behavior.

Do not introduce per-sheet library scopes unless a proven conflict requires them.

---

## 12. Workbench Integration

### 12.1 Remove fabricated hierarchy

The existing hard-coded hierarchy labels must be replaced with resolved project data.

For legacy v1:

```text
Root
└─ Main
```

For v2:

```text
Root
├─ Power
├─ Control
│  └─ Debug
└─ I/O
```

### 12.2 View selector

Add explicit modes:

```text
Sheet
Overview
Composite
```

Do not use layer checkboxes as page navigation.

### 12.3 Selection behavior

Selecting a project net should show:

```text
project-net ID
participating sheets
interface ports
backing local nets
project route segments
```

Selecting an interface port should show:

```text
sheet
port ID
direction
role
local net
project net
sheet coordinate
```

### 12.4 Layer controls

Layer visibility remains sheet-scoped.

P0 does not need synchronized global layer state.

### 12.5 Qualified search

Project search should distinguish:

```text
Power / U1
Control / U1
Power / local net / gnd
Control / local net / gnd
Project net / gnd
```

Same-named objects from different sheets must never collapse into one ambiguous result.

---

## 13. Agent Authoring and Retrieval

### 13.1 Preserve local routes

Existing routes remain local:

```text
create-schematic
create-symbol
route-nets
validate-project
```

`route-nets` must not become a project-wide route by default.

### 13.2 Add `compose-project`

Purpose:

- register/remove leaf sheets;
- define hierarchy;
- inspect leaf interface ports;
- declare/repair project nets;
- validate project graph closure.

Recommended retrieval order:

```text
project composition contract
→ project-net model
→ interface summaries
→ affected leaf sources only
```

### 13.3 Add `route-project-nets`

Purpose:

- inspect project-net membership;
- inspect resolved interface-port positions;
- generate or repair project-level overview/composite routes;
- never alter semantic membership merely to improve geometry.

### 13.4 Update `AGENTS.md`

Add mandatory rules:

> Structural ownership is Project → Sheet → Layer.

> A layer is not a schematic sheet.

> A leaf `.aixem` owns its interface ports and local net membership.

> `aixproj/2` owns only cross-sheet composition and project-net membership.

> Same names never imply cross-sheet electrical connectivity.

> Local wire geometry belongs to `route-nets`; project-level sheet-to-sheet geometry belongs to `route-project-nets`.

> Load interface summaries before loading unrelated full sheets.

### 13.5 Interface summaries

Generate a compact derived summary per sheet:

```json
{
  "sheet": "control",
  "sourceDigest": "sha256:...",
  "layoutDigest": "sha256:...",
  "ports": [
    { "id": "VCC", "direction": "input", "localNet": "vcc", "projectNet": "vcc_5v" },
    { "id": "GND", "direction": "passive", "localNet": "gnd", "projectNet": "gnd" }
  ]
}
```

An agent should be able to compose a project from these summaries without opening every component and route in every sheet.

---

## 14. Conformance Corpus

Create:

```text
validation/corpus/hierarchical-project-1/
```

### 14.1 Core cases

| ID | Case | Purpose |
|---|---|---|
| H001 | Two-sheet power + control | base interface/project-net closure |
| H002 | Single local component endpoint + interface port | prove the new semantic endpoint solves the current 2-endpoint limitation |
| H003 | Three-sheet VCC/GND fan-out | multi-member project nets |
| H004 | Same-name local nets not connected | prove no implicit name merge |
| H005 | Three-level sheet hierarchy | hierarchy traversal and cycle validation |
| H006 | Interface-port local routing | `entity.port ↔ @PORT` route closure |
| H007 | Project Overview | deterministic sheet-block placement and project routing |
| H008 | Composite View | full leaf-scene composition |
| H009 | Missing/unknown interface port | fail closed with precise diagnostic |
| H010 | Duplicate project-net ownership | reject one interface port in multiple project nets |
| H011 | Digest-locked multi-sheet project | verify all referenced inputs |
| H012 | Legacy `aixproj/1` project | prove unchanged behavior |
| H013 | 10-sheet project | scale and deterministic ordering baseline |
| H014 | Cross-sheet route crossings | crossing versus project junction semantics |
| H015 | Local-net/project-net equivalence collision | reject two project-net IDs that become one through a leaf local net |

### 14.2 Required negative fixtures

Include:

```text
interface port declared twice
unknown @PORT in local net
interface port in two local nets
interface port both net-connected and noconn
layout sheetPort references unknown semantic port
missing required sheetPort presentation
project member references unknown sheet
project member references unknown interface port
project net with one member
same interface port in two project nets
two ports on one local net assigned to different project-net IDs
unknown hierarchy parent
hierarchy cycle
source digest mismatch
layout digest mismatch
same-name local nets without explicit project net
```

### 14.3 P1 overview-layout cases

Only if `.aixoverview.json` is approved:

```text
H101 explicit sheet placement
H102 explicit project-route bends
H103 manual project junction
H104 deterministic overview digest
```

---

## 15. Validation Requirements

### 15.1 Leaf semantic closure

For every sheet:

- all existing 0.5.2 entity/component endpoint checks pass;
- every `@PORT` resolves to a declared semantic interface port;
- every connected interface port belongs to exactly one local net;
- local net membership remains explicit;
- existing no-connect contradiction rules extend to interface ports.

### 15.2 Leaf layout closure

For every sheet:

- `designId` matches source model ID;
- placements remain valid;
- local connections reference existing local nets;
- route endpoints may resolve component endpoints or interface endpoints;
- all local semantic net endpoints, including `@PORT`, are covered by local route geometry;
- required interface-port presentation exists exactly once.

### 15.3 Project closure

For every project:

- sheet IDs unique;
- all source/layout digests verified;
- all leaf sources/layouts valid independently;
- hierarchy acyclic;
- project-net IDs unique;
- all project members resolve to semantic interface ports;
- each interface port belongs to at most one project net in P0;
- transitive local connectivity must not cause two different project-net IDs to collapse into one equivalence class;
- no project membership is inferred from local net name, label text, or geometry.

### 15.4 Deterministic rendering

Release verification must render each hierarchical corpus project at least three times.

Required identical outputs:

```text
per-sheet resolved-scene digest
per-sheet canonical SVG digest
resolved-project-scene digest
project-overview SVG digest
project-composite SVG digest
```

---

## 16. Failure Classification

### H-F1 — Local semantic source failure

Examples:

- duplicate interface port;
- unresolved `@PORT`;
- interface endpoint appears in conflicting local nets.

Action:

- fix leaf `.aixem` or parser/validator.

### H-F2 — Local layout failure

Examples:

- missing interface-port position;
- route does not cover `@PORT`.

Action:

- fix leaf `.aixlayout`.

### H-F3 — Project composition failure

Examples:

- unknown sheet;
- unknown interface port;
- hierarchy cycle.

Action:

- fix `aixproj/2`.

### H-F4 — Project-net semantic failure

Examples:

- duplicate member;
- one port in two project nets.

Action:

- fix project semantic graph.

### H-F5 — Project presentation/routing failure

Examples:

- overview route intersects a sheet block;
- composite route has non-orthogonal segment.

Action:

- fix project router/presentation, not semantic membership.

### H-F6 — Renderer defect

Example:

- valid `@PORT` resolves but renders at the wrong transformed position.

Action:

- renderer correction plus focused regression.

### H-F7 — Proven architecture gap

Example:

- same leaf design must be instantiated multiple times with independent namespaces.

Action:

- dedicated ADR and P2 extension gate.

---

## 17. Extension Gates

### 17.1 Reusable module instances

Do not implement in P0.

Open an ADR only when a real case requires:

```text
one source/layout module
× multiple project instances
with isolated entity/net namespaces
```

The ADR must resolve:

- instance identity;
- refdes uniqueness;
- local net namespace qualification;
- layout reuse/overrides;
- interface port parameterization;
- deterministic resolved IDs.

### 17.2 Bus/bundle ports

P0 interfaces are scalar ports.

Add buses only if a representative project proves scalar port count is unmanageable.

### 17.3 Global nets

No implicit global nets in P0.

Any future global-net capability must be explicit and namespace-controlled.

### 17.4 Manual project overview layout

Add `.aixoverview.json` only after deterministic auto-layout is proven insufficient by real corpus evidence.

---

## 18. Documentation Plan

### 18.1 New normative documents

| Path | Role |
|---|---|
| `docs/specifications/project/project-composition-contract.md` | multi-sheet project, hierarchy, project-net contract |
| `docs/specifications/core/interface-port-contract.md` | `.aixem` interface-port semantics and endpoint syntax |
| `docs/concepts/project-net-model.md` | local-net/project-net relationship |
| `docs/specifications/layout/hierarchical-sheet-port-contract.md` | interface-port presentation and route endpoint resolution |
| `docs/conformance/hierarchical-project.md` | conformance profile, gates, public claims |

### 18.2 Existing documents to update

| Path | Change |
|---|---|
| `AGENTS.md` | Project → Sheet → Layer rule and ownership rules |
| `docs/file-formats/aixem.md` | `port` declaration, `@PORT`, feature negotiation |
| `docs/file-formats/aixproj.md` | v1 legacy and v2 multi-sheet forms |
| `docs/file-formats/aixlayout.md` | v1/v2 distinction and `sheetPorts[]` |
| `docs/concepts/semantic-model.md` | interface endpoints and project composition boundary |
| `docs/concepts/net-model.md` | local net versus project net |
| `docs/concepts/layout-model.md` | local route versus project route |
| `docs/schematic/sheet-organization.md` | align guidance with executable contract |
| `docs/examples/hierarchical-reference.md` | link to executable H001/H005 examples |
| `docs/routing/net-routing.md` | support `@PORT` local route endpoints |
| `docs/routing/routing-cookbook.md` | component-to-sheet-port recipe |
| `docs/agent/authoring-orchestration.md` | add composition/project-routing stages |
| `docs/agent/routing-agent.md` | local/project routing separation |
| `docs/conformance/release-gates.md` | hierarchical-project release gate |
| `docs/conformance/compatibility.md` | exact multi-sheet claim wording |
| `docs/_meta/navigation.yaml` | new composition/conformance entries |

### 18.3 Remove misleading hierarchy presentation

The release is not complete until:

- hard-coded Workbench hierarchy entries are removed;
- generated hierarchy reflects actual project data;
- informative docs no longer look like proof of unsupported v1 behavior;
- hierarchy claims point to executable corpus evidence.

---

## 19. File-Level Change Matrix

### 19.1 Schemas

```text
docs/specifications/schemas/component-graphics-2/
├── aixem-project-manifest-2.schema.json
└── aixem-explicit-layout-2.schema.json
```

The line-oriented `.aixem` interface feature remains governed by its grammar/specification and feature declarations rather than a JSON schema.

### 19.2 Implementation

Recommended minimal split:

```text
implementation/schematic/
├── component_core.py
├── project_composition.py
├── project_routing.py
└── render_project.py
```

Responsibilities:

```text
component_core.py
  local semantic parser, interface ports, leaf validation/render helpers

project_composition.py
  v1/v2 project loading, hierarchy, project graph, project-net closure

project_routing.py
  deterministic overview/composite routing

render_project.py
  output orchestration and multi-view Workbench
```

Do not broadly reorganize unrelated symbol-rendering code in the same release.

### 19.3 Tests

```text
tests/conformance/test_hierarchical_project.py
tests/docs/test_hierarchical_authoring_routes.py
```

Keep all current tests and corpora.

### 19.4 Corpus

```text
validation/corpus/hierarchical-project-1/
├── README.md
├── manifest.json
├── schema/
├── cases/H001-...-H015/
└── results/
```

### 19.5 Agent routes

```text
docs/_meta/routes/compose-project.yaml
docs/_meta/routes/route-project-nets.yaml
```

---

## 20. Implementation Sequence

### Phase 0 — Freeze 0.5.2 Baseline

1. Record `aixproj/1` schema digest.
2. Record `aixlayout/1` schema digest.
3. Record renderer digest/version.
4. Run full repository tests.
5. Run Symbol Expressiveness corpus.
6. Run Static 2D Block corpus.
7. Record current single-sheet canonical outputs.

**Exit criterion:** clean passing 0.5.2 baseline.

### Phase 1 — Specify Interface Port Semantics

1. Write interface-port contract.
2. Fix exact `port` grammar.
3. Fix exact interface endpoint syntax (`@PORT` preferred).
4. Define direction/role vocabulary.
5. Extend endpoint closure rules.
6. Define required feature `hierarchical.interface@1`.
7. Add parser-focused tests.

**Exit criterion:** H002 semantic fixture parses and validates without any project renderer work.

### Phase 2 — Implement `aixlayout/2`

1. Preserve all v1 fields/behavior.
2. Add `sheetPorts[]`.
3. Extend route endpoint resolution to semantic interface endpoints.
4. Extend route closure to include interface endpoints.
5. Render interface-port markers and labels.
6. Verify changing coordinates does not change semantics.

**Exit criterion:** H006 renders correctly as an independent sheet.

### Phase 3 — Define and Implement `aixproj/2`

1. Add immutable v2 schema.
2. Add `sheets[]`.
3. Add hierarchy parent/order metadata.
4. Add `projectNets[]`.
5. Verify every referenced source/layout/library digest.
6. Validate every leaf independently.
7. Resolve project-net members to semantic interface ports.
8. Build canonical project semantic graph.

**Exit criterion:** H001-H005 semantic/project closure passes before overview rendering.

### Phase 4 — Refactor Leaf Rendering

1. Separate leaf resolver from one-project assumption.
2. Keep legacy entry point.
3. Resolve N leaf scenes using shared libraries.
4. Generate one leaf SVG/resolved scene per sheet.
5. Compare legacy v1 outputs.

**Exit criterion:** H012 legacy regression passes and H001 emits two leaf scenes.

### Phase 5 — Project Overview

1. Deterministically order hierarchy.
2. Place sheet blocks.
3. Expose project ports around blocks.
4. Orthogonally route project nets.
5. Emit junction/crossing semantics.
6. Render `project-overview.svg`.

**Exit criterion:** H007 and H014 pass.

### Phase 6 — Composite View

1. Compute deterministic sheet-canvas transforms.
2. Place full leaf scenes into one project canvas.
3. Transform interface anchors to project coordinates.
4. Route project nets between transformed anchors.
5. Preserve sheet-qualified identities and layers.
6. Render `project-composite.svg`.

**Exit criterion:** H008 passes.

### Phase 7 — Resolved Project Scene

1. Emit project graph.
2. Include per-sheet digests.
3. Include hierarchy.
4. Include interface summaries.
5. Include project-route geometry.
6. Include aggregate diagnostics/statistics.

**Exit criterion:** project evidence is sufficient to inspect hierarchy without reading renderer source.

### Phase 8 — Workbench Integration

1. Remove hard-coded hierarchy.
2. Add Sheet / Overview / Composite selector.
3. Add sheet navigation.
4. Add project-net highlighting.
5. Add interface-port inspection.
6. Keep layer controls sheet-scoped.
7. Add qualified project search.

**Exit criterion:** all visible hierarchy is data-driven.

### Phase 9 — Agent Integration

1. Add `compose-project` route.
2. Add `route-project-nets` route.
3. Update `AGENTS.md`.
4. Generate per-sheet interface summaries.
5. Validate route token/context budgets.
6. Confirm local edit tasks do not require loading all sheets.

**Exit criterion:** project composition is agent-friendly without repository-wide search.

### Phase 10 — Corpus, Documentation, Release Closure

1. Complete H001-H015.
2. Complete negative fixtures.
3. Generate capability matrix.
4. Update normative/informative docs.
5. Regenerate reference cards/routes/indexes/site.
6. Run three complete verification passes.
7. Regenerate release manifest and integrity evidence.

---

## 21. Three-Pass Verification and Improvement Loop

### PASS 1 — Semantic and Structural Correctness

Focus:

> Can independent circuit files be connected through explicit semantic boundaries without weakening local authority?

Gate:

```text
legacy aixproj/1                         PASS
legacy aixlayout/1                       PASS
interface-port grammar                   PASS
@PORT endpoint closure                   PASS
local net minimum endpoint rule          PASS with interface endpoint
sheet-port layout closure                PASS
multi-sheet aixproj/2                    PASS
hierarchy acyclic                        PASS
project-net closure                      PASS
same-name local net isolation            PASS
unclassified semantic failures           0
```

If any release-critical failure occurs, fix the smallest owning contract and repeat PASS 1 completely.

### PASS 2 — Rendering, Routing, Scale, and Agent Usability

Focus:

> Can the hierarchy be drawn, navigated, and edited without flattening the project?

Gate:

```text
per-sheet rendering                      PASS
interface-port visual attachment         PASS
project overview                          PASS
orthogonal project routing               PASS
junction/crossing semantics              PASS
composite view                            PASS
sheet-qualified identity                 PASS
data-driven Workbench hierarchy          PASS
sheet-scoped layers                       PASS
qualified search                          PASS
compose-project agent route              PASS
route-project-nets agent route           PASS
10-sheet H013 baseline                    PASS
critical visual defects                   0
```

### PASS 3 — Regression, Determinism, and Claim Integrity

Focus:

> Can the feature be released without damaging 0.5.2 guarantees or overstating hierarchical capability?

Gate:

```text
full repository test suite               PASS
0.5.2 Symbol Expressiveness corpus       PASS
0.5.2 Static 2D Block corpus             PASS
H001-H015 hierarchical corpus            PASS
negative fixtures                        expected failures
legacy output regression                 PASS
three repeated complete renders          identical digests
schema publication                       PASS
reference/site regeneration              PASS
release manifest/integrity               PASS
fabricated hierarchy entries              0
implicit global-net behavior              0
unsupported compatibility claims          0
```

A release-critical correction requires restarting PASS 3 from clean staged inputs.

---

## 22. Acceptance Criteria

### 22.1 Compatibility

- [ ] Valid `aixproj/1` files remain valid.
- [ ] Valid `aixlayout/1` files remain valid.
- [ ] Existing `.aixem` files without hierarchical feature declarations remain behaviorally unchanged.
- [ ] `.aixsym` and `.aixlib` require no format change.
- [ ] All 0.5.2 conformance corpora still pass.

### 22.2 Interface semantics

- [ ] `.aixem` supports explicit semantic interface ports under a declared feature.
- [ ] Interface ports are valid semantic net endpoints.
- [ ] A one-component-pin off-sheet connection is representable as `entity.port + @PORT`.
- [ ] Interface endpoints obey duplicate/conflict/no-connect rules.

### 22.3 Multi-sheet composition

- [ ] One `aixproj/2` may reference at least 10 independent source/layout pairs.
- [ ] Each sheet validates independently.
- [ ] Hierarchy is explicit and cycle-free.
- [ ] Project nets explicitly connect semantic interface ports.
- [ ] Same-named local nets remain independent without explicit project-net membership.
- [ ] Two interface ports already connected by one local net cannot be assigned to conflicting project-net IDs.

### 22.4 Presentation

- [ ] `aixlayout/2` places interface ports without owning their semantics.
- [ ] Local routing reaches `@PORT` endpoints.
- [ ] Sheet View renders interface ports.
- [ ] Project Overview renders all participating sheets and project nets.
- [ ] Composite View renders complete sheets in one workspace.
- [ ] Project routes are deterministic and orthogonal under P0 profile.
- [ ] Layers remain distinct from sheets.

### 22.5 Workbench

- [ ] Hierarchy is generated from project data.
- [ ] Hard-coded hierarchy is removed.
- [ ] Sheet / Overview / Composite modes exist.
- [ ] Project-net selection links to participating sheet/local nets.
- [ ] Search results are sheet-qualified.

### 22.6 Agent readiness

- [ ] `compose-project` route exists.
- [ ] `route-project-nets` route exists.
- [ ] `AGENTS.md` states Project → Sheet → Layer authority.
- [ ] Agent guidance prohibits implicit cross-sheet name matching.
- [ ] Interface summaries allow composition without loading full unrelated sheets.

### 22.7 Determinism and evidence

- [ ] H001-H015 pass.
- [ ] Negative fixtures fail with expected diagnostics.
- [ ] Three complete render runs produce identical canonical digests.
- [ ] Release report and capability matrix are generated.
- [ ] All source/layout/library references are digest verified.

---

## 23. Performance Policy

Measure before optimizing.

Record:

```text
sheet count
hierarchy depth
local entity count
local net count
interface port count
project net count
total source bytes
total layout bytes
leaf resolve duration
project graph resolve duration
overview route duration
composite render duration
resolved project scene size
SVG sizes
Workbench size
peak process memory when available
```

Initial scale gate:

- H013 with 10 sheets must complete reliably in the controlled reference environment;
- no unexplained pathological scaling should appear;
- 0.5.3 establishes the first project-scale baseline;
- caching is added only if measurements justify it.

---

## 24. Security and Reproducibility

Multi-sheet loading increases reference count but does not change the security model.

Requirements:

- project-root-relative file references only;
- no `..` path escape;
- every required source/layout/library digest verified before use;
- no silent remote dependencies;
- duplicate paths with contradictory digests rejected;
- hierarchy ordering independent of filesystem enumeration;
- auto-layout and auto-routing use deterministic sort keys;
- resolved project output records all input digests.

---

## 25. Non-Goals for 0.5.3 P0

Keep these explicitly outside P0:

- repeated reusable hierarchical module instances;
- parameterized sheet/module instancing;
- bus/bundle interface ports;
- differential-pair project semantics;
- implicit global nets;
- name-based automatic cross-sheet connectivity;
- canonical flattening into one `.aixem` file;
- interactive drag-edit project routing;
- native KiCad hierarchy import/export;
- native OrCAD hierarchy import/export;
- SPICE subcircuit semantics;
- PCB hierarchy/routing;
- distributed/remote sheet sources;
- stochastic project graph layout;
- new symbol graphic primitives.

---

## 26. Recommended Public Capability Claim

If all P0 gates pass, the release may state:

> AIXEM supports deterministic composition of multiple digest-locked schematic source/layout pairs into an explicit hierarchical project, using semantic sheet interface ports and explicit project nets, with independent sheet rendering, project overview rendering, and composite project visualization.

Do not state:

> AIXEM is fully KiCad hierarchical compatible.

Do not state:

> AIXEM is fully OrCAD multi-page compatible.

Do not claim reusable hierarchical module instancing until that capability has its own contract and conformance evidence.

---

## 27. Recommended Priority

### P0 — Implement now

1. freeze legacy v1 contracts;
2. add `hierarchical.interface@1` to `.aixem`;
3. add semantic `port` declarations and interface endpoint references;
4. add `aixlayout/2.sheetPorts[]`;
5. allow local routes to terminate at semantic interface ports;
6. add `aixproj/2.sheets[]`;
7. add explicit hierarchy parent relation;
8. add explicit `projectNets[]`;
9. build project semantic graph;
10. preserve independent leaf rendering;
11. implement deterministic Project Overview;
12. implement deterministic Composite View;
13. replace hard-coded Workbench hierarchy;
14. add `compose-project` and `route-project-nets` routes;
15. add H001-H015 corpus;
16. perform three-pass verification.

### P1 — After P0 stability

1. persistent manual overview/composite layout sidecar if proven necessary;
2. manual project-route bend control;
3. richer project annotations/title organization;
4. multi-sheet print/export organization;
5. project-route quality metrics.

### P2 — Evidence-gated only

1. reusable hierarchical module descriptors;
2. repeated module instances with namespace isolation;
3. bus/bundle interface ports;
4. controlled explicit global-net semantics;
5. parameterized hierarchical modules.

---

## 28. Definition of Done

AIXEM 0.5.3 hierarchical multi-sheet work is complete only when:

### Authority model

- [ ] Leaf `.aixem` files own local components, local nets, and semantic interface ports.
- [ ] `aixproj/2` owns cross-sheet hierarchy and project-net membership.
- [ ] `aixlayout/2` owns interface-port coordinates and local routing presentation only.
- [ ] Geometry cannot create project connectivity.
- [ ] Layers cannot act as sheets.

### Compatibility

- [ ] Legacy `aixproj/1` and `aixlayout/1` remain valid.
- [ ] Existing non-hierarchical `.aixem` behavior is unchanged.
- [ ] 0.5.2 corpora and tests still pass.

### Functionality

- [ ] Multiple independent circuit files load in one project.
- [ ] Off-sheet leaf connections have real semantic interface endpoints.
- [ ] Project nets connect sheet ports explicitly.
- [ ] Hierarchy resolves deterministically.
- [ ] Sheet, Overview, and Composite views render correctly.
- [ ] Workbench hierarchy is fully data-driven.

### Agent usability

- [ ] An agent can inspect sheet interfaces without opening all leaf body data.
- [ ] An agent can edit a single sheet independently.
- [ ] An agent can compose and route project nets through dedicated routes.

### Evidence

- [ ] H001-H015 pass.
- [ ] Negative cases fail correctly.
- [ ] Three complete render cycles are deterministic.
- [ ] Release capability matrix is generated.
- [ ] No unsupported hierarchy/compatibility claim remains.

---

## 29. Final Target State

```text
                         project.aixproj.json v2
                                  │
                 hierarchy + explicit project nets
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
      POWER                    CONTROL                     I/O
        │                         │                         │
   power.aixem              control.aixem               io.aixem
   @VOUT @GND               @VCC @GND                 @VCC @GND
        │                         │                         │
   power.layout v2          control.layout v2          io.layout v2
        │                         │                         │
   local routes              local routes               local routes
        │                         │                         │
        └─────────────── semantic interface boundary ─────┘
                                  │
                        Project Semantic Graph
                                  │
                       deterministic project router
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
        Sheet View           Overview View         Composite View
            │                     │                     │
            └─────────────────────┼─────────────────────┘
                                  │
                     resolved-project-scene.json
                                  │
                       data-driven Workbench
```

The 0.5.3 quality bar should be:

> **Each circuit remains a real independent circuit file. Each sheet exposes explicit semantic boundary ports. A project graph connects only those declared boundaries. Local routing stays local, project routing stays project-level, and every one-screen or hierarchical visualization is a deterministic derivation of those authorities.**

This closes the present multi-file/multi-sheet gap with the smallest defensible semantic expansion while preserving AIXEM's core strengths: explicit connectivity, deterministic rendering, conservative versioning, and efficient AI-agent authoring.
