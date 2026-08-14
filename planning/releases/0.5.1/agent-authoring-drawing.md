# AIXEM 0.5.1 — Agent Authoring & Drawing Documentation Enhancement Plan

**Target release:** AIXEM 0.5.1  
**Plan status:** Implementation-ready  
**Baseline:** AIXEM 0.5.0 (2026-08-11)  
**Primary objective:** Make the AIXEM documentation sufficient for an AI agent to author component definitions, draw symbol graphics, bind semantic properties and ports, place components, route nets, render the result, inspect evidence, and repair defects without repository-wide discovery or renderer-code archaeology.  
**Documentation language:** English only.

---

## 1. Executive Summary

AIXEM 0.5.0 successfully established a strong documentation architecture: `AGENTS.md` is the mandatory entry point, `docs/` is the canonical documentation root, task routes are compiled into a route index, generated metadata is derived from canonical sources, and authority boundaries between semantics, symbol graphics, layout, style, and documentation are explicit.

The remaining weakness is not navigation. It is **authoring sufficiency**.

An agent can currently determine *which* documents to read, but those documents often stop at conceptual or normative statements. For concrete drawing work, the agent still has to inspect JSON Schema files, validated examples, or renderer implementation code to learn details such as:

- which `.aixsym.json` fields create visible geometry;
- how every graphic primitive is serialized;
- how a visible pin lead relates to a symbol `port` coordinate;
- how `labelVisible` and `numberVisible` affect automatic pin overlays;
- how semantic component ports map through `.aixlib.json` `portMap` into symbol ports;
- how semantic attributes map through `fieldMap` into text fields;
- field-value precedence and placement overrides;
- parameter and variant resolution precedence;
- how `.aixem` semantic nets correspond to `.aixlayout.json` connection geometry;
- how multi-terminal routes and explicit junctions are represented;
- which graphics/style values belong in the symbol asset and which belong in the schematic style profile;
- how rendered SVG/HTML and `resolved-scene.json` should be inspected and repaired.

AIXEM 0.5.1 shall close this gap by turning the current documentation set into an **agent-executable authoring manual** while preserving the route-first architecture of 0.5.0.

The desired end state is:

```text
User task
   ↓
AGENTS.md
   ↓
intent / composite-task classification
   ↓
route-index.json
   ↓
exact task route(s)
   ↓
small set of canonical authoring docs + worked recipes
   ↓
authoritative artifacts
   ↓
renderer / validators
   ↓
resolved scene + visual evidence
   ↓
local repair loop
   ↓
validated deliverable
```

A successful 0.5.1 release means an agent can complete the common authoring workflows using the documented route chain and **without inspecting `implementation/schematic/component_core.py` or searching unrelated repository content under normal conditions**.

---

## 2. Baseline Findings from AIXEM 0.5.0

### 2.1 What is already strong

The following 0.5.0 mechanisms should be preserved:

1. `AGENTS.md` as the mandatory repository entry point.
2. Route-first retrieval through `docs/_meta/generated/route-index.json`.
3. A default retrieval budget of 7 documents, 96 KiB, and depth 3.
4. Canonical documentation under `docs/`.
5. Stable document IDs and metadata front matter.
6. Normative versus informative document status.
7. Explicit authority boundaries:
   - semantic connectivity;
   - symbol graphics;
   - layout;
   - presentation/style;
   - documentation/reference.
8. Deterministic generated metadata and release manifests.
9. Requirement → validator → test → evidence traceability.
10. Vendor-neutral graphics and UI policy.

These are foundation assets, not targets for replacement.

### 2.2 Current route topology is structurally good but content-light

The current `create-symbol` route correctly chains:

```text
Component Model
→ Symbol Anatomy
→ Pins / Ports
→ Graphic Primitives
→ Symbol Authoring Guide
→ Symbol Lint
```

The problem is that the route does not yet deliver enough concrete serialization and rendering knowledge to execute the task efficiently.

Likewise, `create-schematic` and `route-nets` correctly lead the agent through authority, semantics, placement, and routing rules, but they do not provide enough fully worked `.aixem` and `.aixlayout.json` examples to make the transformation from intent to valid artifacts obvious.

### 2.3 Worked-example deficit

The principal authoring/reference documents in the current baseline contain essentially no JSON worked examples. The following current documents have no fenced code examples:

- `docs/symbols/authoring-guide.md`
- `docs/symbols/primitives.md`
- `docs/symbols/pins-and-ports.md`
- `docs/symbols/field-layout.md`
- `docs/symbols/variants.md`
- `docs/file-formats/aixsym.md`
- `docs/file-formats/aixlib.md`
- `docs/file-formats/aixlayout.md`
- `docs/file-formats/aixem.md`
- `docs/schematic/visual-language.md`
- `docs/specifications/schematic/visual-profile.md`
- `docs/specifications/symbols/symbol-contract.md`
- `docs/routing/net-routing.md`

This means an agent must infer serialization from schemas or examples instead of learning directly from the route-selected documentation.

### 2.4 The implementation supports richer behavior than the docs teach

The current symbol schema and renderer already support substantial authoring capability, including:

- graphic nodes: `group`, `use`, `line`, `polyline`, `polygon`, `rect`, `circle`, `ellipse`, `arc`, `path`, `text`, `image`, and `dimension`;
- symbol `coordinateSystem`, `bounds`, `anchors`, `layers`, `styles`, `graphics`, `ports`, `parameters`, `variants`, `definitions`, `paintServers`, `requiredFeatures`, and `provenance`;
- parameterized numeric expressions;
- reusable definitions and `use` nodes;
- `visibleWhen` predicates;
- variant graphics, parameter defaults, port overrides, and suppression;
- component presentation `fieldMap`, `portMap`, `defaultVariant`, and asset binding;
- placement fields, variant selection, and parameter overrides;
- deterministic resolved scene output.

These mechanisms need to become first-class documentation, not hidden implementation knowledge.

### 2.5 Critical runtime resolution rules are undocumented or under-documented

The baseline renderer effectively resolves several important chains that agents need to know.

#### Field resolution

Conceptually, field values resolve through:

```text
renderer defaults / identity fields
→ presentation.fieldMap from semantic attributes
→ semantic entity attributes
→ placement.fields overrides
→ symbol text node `field`
→ rendered text
```

The exact behavior must be documented and tested as a public renderer contract.

#### Variant selection

Current behavior resolves a variant in this order:

```text
placement.variant
→ presentation.defaultVariant
→ symbol.defaultVariant
```

#### Parameter resolution

Current behavior resolves symbol parameters from symbol defaults, then applies variant defaults and placement-level overrides. This precedence must be specified precisely and covered by examples.

#### Port binding

Current behavior requires a total `presentation.portMap` over component semantic ports and maps each semantic port to an existing, visible symbol port. This is a core authoring rule and should be taught with exact JSON examples.

### 2.6 Pin drawing semantics require explicit documentation

A symbol `port` represents the electrical connection coordinate. It is not, by itself, a complete visible pin graphic.

For many symbols, the author must create the visible lead geometry in `graphics[]` and make its endpoint coincide with the port coordinate. Pin labels/numbers can then be rendered from port metadata according to visibility settings.

This distinction needs a dedicated explanation and diagram because it is a common source of AI-generated symbol defects:

```text
symbol body ───── visible lead line ───── ● symbol port coordinate
                                            ↑
                                  semantic connection point
```

The documentation shall explicitly define:

- which element owns visual lead geometry;
- which element owns electrical attachment coordinates;
- how `orientation` is interpreted;
- how label and number visibility affect renderer overlays;
- how to validate coincident endpoints;
- how grid alignment constrains both the visible lead and the port.

### 2.7 Style authority needs a formal precedence contract

The current baseline contains useful schematic style values in `profiles/aixem-grid-schematic-style-1.aixstyle.json`, including:

- 2.5 mm snap grid;
- 5 mm pin length;
- 5 mm pin pitch;
- square corner policy;
- outside field placement;
- orthogonal routing;
- 2.5 mm minimum route segment;
- explicit junction policy.

However, symbol assets also contain local `styles` with stroke widths, font sizes, colors, joins, and other presentation data.

0.5.1 must define which properties are intrinsic symbol fallback styles and which are project/profile presentation overrides. Any behavioral change must be introduced through an ADR and compatibility analysis rather than by silently changing the renderer.

---

## 3. 0.5.1 Product Goal

AIXEM 0.5.1 shall make the repository documentation sufficient for the following cold-start agent scenario:

> The agent is told only to follow `AGENTS.md` and is asked to create a new component, draw its schematic symbol, expose properties, place instances, connect them, render the schematic, and repair visual or conformance defects.

The agent should be able to:

1. identify the task as simple or composite;
2. resolve the correct route chain without repository-wide search;
3. understand the semantic component contract;
4. select a suitable symbol construction recipe;
5. serialize valid `.aixsym.json` without inspecting the schema manually;
6. create visible body and pin geometry aligned to the grid;
7. create and map semantic ports correctly;
8. create fields and bind them to semantic attributes;
9. use parameters and variants intentionally;
10. create or modify `.aixlib.json` presentation bindings;
11. create semantic entities and nets in `.aixem`;
12. place components and route connections in `.aixlayout.json`;
13. preserve junction/crossing semantics;
14. render SVG/workbench output;
15. inspect `resolved-scene.json` and validation evidence;
16. localize failures to the owning authority layer;
17. repair only the authoritative source that owns the defect;
18. re-render and revalidate until the project passes.

---

## 4. Non-Goals

0.5.1 is primarily an authoring/documentation and agent-operability release. The following are not required unless a documentation defect exposes a necessary compatibility fix:

- a new schematic file-format generation;
- a proprietary EDA compatibility layer;
- a new graphical editor;
- a new automatic router algorithm;
- a new symbol language replacing `.aixsym.json`;
- wholesale redesign of the workbench UI;
- repository-wide semantic changes unrelated to authoring sufficiency.

Schema or renderer changes are permitted only when necessary to remove ambiguity, make documented behavior testable, or fix an actual mismatch between documented and implemented contracts.

---

## 5. Design Principles for 0.5.1

### 5.1 Route-selected documents must be sufficient

A normal authoring task should not require code archaeology.

If the agent reaches for renderer source merely to understand a normal field, port, primitive, or precedence rule, the documentation is incomplete.

### 5.2 Worked examples are part of the interface contract

Normative rules explain what is legal. Worked examples explain how to author it correctly. Both are required for agent reliability.

### 5.3 Examples must be executable and drift-resistant

Documentation examples must be validated against the same schemas and renderer used by the project. Hand-copied snippets that can silently drift are unacceptable.

### 5.4 One rule, one authority

The same precedence or binding rule must not be independently restated as normative text in multiple documents. Guides should link to the normative owner and show examples.

### 5.5 Visual correctness is a first-class validation target

Passing JSON Schema does not guarantee a useful schematic symbol. Grid alignment, lead/port coincidence, field spacing, pin grouping, crossings, and legibility require explicit visual rules and review evidence.

### 5.6 Composite tasks must chain routes, not explode search scope

A task such as “create a new IC and connect it in a circuit” should execute a predictable route chain instead of widening a single route until it exceeds context limits.

### 5.7 All new and modified canonical documentation remains English-only

Canonical docs, metadata summaries, task routes, examples, conformance descriptions, generated site labels, and new agent instructions must remain English unless a future localization layer is explicitly introduced.

---

## 6. Target Documentation Architecture

The existing canonical structure remains, but 0.5.1 adds an authoring-focused layer.

```text
docs/
├── agent/
│   ├── authoring-orchestration.md          NEW
│   ├── visual-qa-loop.md                   NEW
│   └── ...
│
├── symbols/
│   ├── authoring-guide.md                  EXPAND
│   ├── authoring-cookbook.md               NEW
│   ├── aixsym-field-reference.md           NEW
│   ├── component-symbol-binding.md         NEW
│   ├── design-rules.md                     NEW
│   ├── primitives.md                       EXPAND
│   ├── pins-and-ports.md                   EXPAND
│   ├── field-layout.md                     EXPAND
│   ├── variants.md                         EXPAND
│   └── symbol-lint.md                      EXPAND
│
├── schematic/
│   ├── authoring-cookbook.md               NEW
│   ├── visual-language.md                  EXPAND
│   ├── placement.md                        EXPAND
│   └── ...
│
├── routing/
│   ├── routing-cookbook.md                 NEW
│   ├── net-routing.md                      EXPAND
│   ├── crossings-and-junctions.md          EXPAND
│   └── ...
│
├── file-formats/
│   ├── aixsym.md                           EXPAND
│   ├── aixlib.md                           EXPAND
│   ├── aixem.md                            EXPAND
│   ├── aixlayout.md                        EXPAND
│   └── ...
│
├── specifications/
│   ├── renderer/
│   │   └── renderer-contract.md            NEW
│   ├── symbols/
│   │   ├── symbol-contract.md              EXPAND
│   │   └── symbol-design-profile.md        NEW
│   └── ...
│
├── examples/
│   ├── authoring/
│   │   ├── two-pin-passive.md              NEW
│   │   ├── multi-pin-ic.md                 NEW
│   │   ├── connector.md                    NEW
│   │   ├── parameterized-variant.md        NEW
│   │   ├── component-binding.md            NEW
│   │   ├── two-terminal-routing.md         NEW
│   │   ├── multi-terminal-junction.md      NEW
│   │   └── visual-repair.md                NEW
│   └── ...
│
└── _meta/
    ├── routes/
    │   ├── create-symbol.yaml              MODIFY
    │   ├── create-schematic.yaml           MODIFY
    │   ├── route-nets.yaml                 MODIFY
    │   ├── validate-project.yaml           MODIFY
    │   ├── render-review.yaml              NEW
    │   └── author-component-circuit.yaml   NEW COMPOSITE ROUTE
    └── generated/
        ├── route-index.json                REGENERATE
        ├── task-packets/                   NEW DERIVED OUTPUT
        └── ...
```

---

## 7. New Canonical Documents

This section defines the minimum required new documents and their responsibilities.

### 7.1 `docs/symbols/authoring-cookbook.md`

**Proposed ID:** `AIXEM-SYMBOL-COOKBOOK-001`  
**Status:** Informative  
**Primary intents:** `create-symbol`, `author-component-circuit`

This is the main practical guide an agent should read when creating symbol geometry.

Required sections:

1. **Authoring Decision Tree**
   - passive two-pin symbol;
   - symmetric symbol;
   - connector;
   - multi-pin IC;
   - analog functional block;
   - parameterized/variant symbol.
2. **Coordinate and Origin Strategy**
   - origin selection;
   - body bounding box;
   - grid quantization;
   - preferred orientation;
   - symmetric placement rules.
3. **Recipe: Two-Pin Passive**
   - complete minimal `.aixsym.json`;
   - body geometry;
   - two visible leads;
   - two ports exactly coincident with lead endpoints;
   - reference/value fields;
   - validation checklist.
4. **Recipe: Connector**
   - repeated pins on 5 mm pitch;
   - pin numbering and naming;
   - body enclosure;
   - port ordering.
5. **Recipe: Multi-Pin IC**
   - functional pin grouping;
   - left/right/top/bottom conventions;
   - power and ground grouping;
   - body sizing formula;
   - field placement;
   - pin-name and pin-number visibility.
6. **Recipe: Analog Functional Block**
   - grouped signal inputs/outputs;
   - power pins;
   - compact internal labels without decorative clutter.
7. **Recipe: Parameterized Symbol**
   - parameter definitions;
   - numeric expressions;
   - geometry driven by parameters.
8. **Recipe: Variant Symbol**
   - variant selection;
   - variant graphics;
   - `parameterDefaults`;
   - `portOverrides`;
   - invariant endpoint identity.
9. **Common Failure Patterns**
   - port not at lead endpoint;
   - labels colliding with body;
   - off-grid geometry;
   - semantic and symbol ports mismatched;
   - hidden mapped port;
   - unnecessary path complexity;
   - styles encoding semantic meaning.
10. **Author → Render → Inspect → Repair checklist**.

Every recipe must contain a complete or mechanically extractable validated JSON example.

### 7.2 `docs/symbols/aixsym-field-reference.md`

**Proposed ID:** `AIXEM-SYMBOL-AIXSYM-REF-001`  
**Status:** Reference; normative where directly restating schema contract  
**Primary intents:** `create-symbol`, `inspect-artifact`, `validate-project`

Purpose: provide an agent-readable field-level reference so routine authoring does not require opening the raw JSON Schema.

Required coverage:

- top-level symbol object;
- `id`, `title`, `description`, `purpose`, `revision`;
- `coordinateSystem`;
- `bounds`;
- `anchors`;
- `layers`;
- `styles`;
- `graphics`;
- `ports`;
- `parameters`;
- `variants`;
- `definitions`;
- `paintServers`;
- `requiredFeatures`;
- `provenance`;
- `defaultVariant`.

For each field include:

```text
Name
Type
Required/optional
Authority meaning
Renderer effect
Allowed/typical values
Default/fallback behavior
Interactions and precedence
Minimal JSON example
Validation failure mode
```

The reference must also enumerate every graphic primitive type and link to the detailed primitive guide.

### 7.3 `docs/symbols/component-symbol-binding.md`

**Proposed ID:** `AIXEM-SYMBOL-BINDING-001`  
**Status:** Normative/guide split: normative binding rules with worked informative examples  
**Primary intents:** `create-symbol`, `create-schematic`, `author-component-circuit`

This document shall explain the end-to-end binding chain:

```text
.aixlib component
   ├── component ports
   ├── component properties
   └── presentation
          ├── asset
          ├── portMap
          ├── fieldMap
          └── defaultVariant
                     ↓
                .aixsym asset
                     ↓
             semantic .aixem entity
                     ↓
                 placement
                     ↓
                renderer binding
```

Required sections:

1. component ID and symbol ID relationship;
2. presentation purpose selection;
3. asset path/digest/revision binding;
4. `portMap` direction and totality requirement;
5. `fieldMap` direction;
6. component property definitions;
7. semantic entity attributes;
8. placement field overrides;
9. default and explicit variant selection;
10. mapping failure examples;
11. complete component+symbol binding example;
12. validation procedures.

The document must clearly state that `portMap` is semantic component port ID → symbol port ID.

### 7.4 `docs/schematic/authoring-cookbook.md`

**Proposed ID:** `AIXEM-SCHEM-COOKBOOK-001`  
**Status:** Informative  
**Primary intents:** `create-schematic`, `author-component-circuit`

Required sections:

1. create a design model;
2. add semantic entities;
3. assign component type and properties;
4. define semantic nets;
5. represent no-connect intent;
6. add placements;
7. choose variants and field overrides;
8. route each net geometrically;
9. render and validate;
10. complete two-component example;
11. complete multi-component example;
12. semantic-vs-layout mistake table.

Each example must show `.aixem` and `.aixlayout.json` side by side and explicitly explain which facts belong in which file.

### 7.5 `docs/routing/routing-cookbook.md`

**Proposed ID:** `AIXEM-ROUTE-COOKBOOK-001`  
**Status:** Informative with links to normative routing rules  
**Primary intents:** `route-nets`, `create-schematic`, `author-component-circuit`

Required recipes:

1. straight two-terminal route;
2. one-bend orthogonal route;
3. multi-bend route around components;
4. three-terminal net with explicit junction;
5. crossing without connection;
6. crossing with connection;
7. route label placement;
8. reroute after component movement;
9. visual cleanup while preserving semantics.

Each recipe must show:

- semantic net endpoints;
- layout `from`/`to` endpoints;
- `via` geometry;
- junction representation;
- grid calculations;
- expected rendered topology;
- validator expectations.

### 7.6 `docs/specifications/symbols/symbol-design-profile.md`

**Proposed ID:** `AIXEM-SPEC-SYMBOL-DESIGN-001`  
**Status:** Normative  
**Primary intents:** `create-symbol`, `validate-project`

This document turns currently scattered graphics conventions into a measurable symbol-design profile.

Minimum normative topics:

- baseline grid and sub-grid rules;
- preferred body dimension quantization;
- pin pitch;
- visible lead length;
- required coincidence of lead endpoint and electrical port;
- body-to-pin clearance;
- pin-name clearance;
- pin-number clearance;
- reference/value field clearance;
- minimum text-to-geometry separation;
- body padding rules for multi-pin devices;
- functional grouping of pins;
- preferred signal-flow orientation;
- power and ground placement conventions;
- allowed use of arcs/path primitives;
- primitive economy rule;
- field placement policy;
- deterministic bounding rules;
- prohibited decorative ambiguity.

Values already established by the current style profile should be reused where appropriate rather than invented independently.

New requirement IDs should be introduced for rules that can be validated, for example:

- `AIXEM-REQ-SYMBOL-DESIGN-0001` — port coordinates on required snap grid;
- `AIXEM-REQ-SYMBOL-DESIGN-0002` — visible lead endpoint coincides with mapped electrical port;
- `AIXEM-REQ-SYMBOL-DESIGN-0003` — default pin pitch follows active design profile;
- `AIXEM-REQ-SYMBOL-DESIGN-0004` — reference/value text does not overlap body geometry;
- `AIXEM-REQ-SYMBOL-DESIGN-0005` — multi-pin body provides required pin-group clearance.

Exact IDs should be allocated through the existing requirement governance rules.

### 7.7 `docs/specifications/renderer/renderer-contract.md`

**Proposed ID:** `AIXEM-SPEC-RENDERER-001`  
**Status:** Normative  
**Primary intents:** `create-symbol`, `create-schematic`, `render-review`, `validate-project`

This document exposes behavior that currently exists primarily in renderer code.

Required sections:

1. renderer input contract;
2. component presentation selection;
3. asset loading and digest checks;
4. field-resolution precedence;
5. variant-selection precedence;
6. parameter-resolution precedence;
7. port resolution and transform behavior;
8. `visibleWhen` behavior;
9. reusable definitions and `use` expansion;
10. style resolution and precedence;
11. placement transforms;
12. route endpoint resolution;
13. SVG output contract;
14. `resolved-scene.json` contract;
15. workbench HTML relationship to SVG;
16. deterministic output obligations;
17. renderer failure conditions.

At least the following current runtime precedence rules must be stated explicitly and backed by tests:

```text
variant:
placement.variant
→ presentation.defaultVariant
→ symbol.defaultVariant

fields:
base renderer identity/default fields
→ presentation.fieldMap-derived values
→ semantic entity attributes
→ placement.fields overrides

parameters:
symbol parameter defaults
→ selected variant parameterDefaults
→ placement.parameters overrides
```

If implementation and intended contract differ, do not merely document the discrepancy. Resolve it through an ADR, update tests, and preserve compatibility explicitly.

### 7.8 `docs/agent/authoring-orchestration.md`

**Proposed ID:** `AIXEM-AGENT-AUTHORING-001`  
**Status:** Normative agent execution policy  
**Primary intents:** composite tasks

This document defines task decomposition and route chaining.

Required composite workflow:

```text
create/modify component definition
        ↓
create/modify symbol
        ↓
bind component presentation
        ↓
create/modify semantic schematic
        ↓
place component instances
        ↓
route nets
        ↓
render and inspect
        ↓
validate project
```

It shall define:

- route entry conditions;
- route exit conditions;
- which outputs become inputs to the next route;
- when to reuse an existing symbol instead of creating one;
- when a task is graphics-only versus semantics-changing;
- how to recover from a missing route or missing document;
- maximum allowed search expansion;
- when to stop and report a contract conflict.

### 7.9 `docs/agent/visual-qa-loop.md`

**Proposed ID:** `AIXEM-AGENT-VISUAL-QA-001`  
**Status:** Normative workflow / informative heuristics  
**Primary intents:** `render-review`, `create-symbol`, `create-schematic`

Required loop:

```text
Author source artifact
→ run schema/lint
→ render
→ inspect project-validation.json
→ inspect resolved-scene.json
→ inspect SVG/workbench visually
→ classify defect by authority layer
→ repair authoritative source only
→ re-render
→ compare deterministic output
→ final validation
```

The document must provide a defect-to-authority matrix:

| Symptom | Likely owner |
|---|---|
| Wire ends short of pin | symbol port/lead geometry or layout endpoint resolution |
| Correct wire shape, wrong net | semantic source |
| Text overlaps body | symbol field layout / design profile |
| Component in wrong location | layout placement |
| Crossing appears connected unexpectedly | semantic junction/net representation or route junction data |
| Color/stroke only wrong | presentation/style |
| Missing pin name | symbol port metadata / visibility |
| Wrong displayed value | fieldMap, semantic attributes, or placement field override |

---

## 8. Existing Documents to Expand

### 8.1 `docs/symbols/authoring-guide.md`

Keep it short enough for route use, but convert it from a generic checklist into an executable sequence.

Add:

- explicit input artifact list;
- exact output artifact list;
- link to cookbook recipe selection;
- port/lead coincidence rule;
- field binding checkpoint;
- parameter/variant checkpoint;
- renderer review checkpoint;
- command or tool references for validation;
- “do not inspect renderer source unless the renderer contract is insufficient” rule.

### 8.2 `docs/symbols/primitives.md`

Expand into a primitive reference with a subsection for every supported node type:

- `group`
- `use`
- `line`
- `polyline`
- `polygon`
- `rect`
- `circle`
- `ellipse`
- `arc`
- `path`
- `text`
- `image`
- `dimension`

For each primitive provide:

- purpose;
- required fields;
- optional common fields;
- coordinate semantics;
- parameter-expression support;
- minimal valid JSON;
- recommended schematic use;
- discouraged misuse;
- output/rendering notes.

The documentation build should automatically verify that every primitive `type` declared in the JSON Schema has a matching section.

### 8.3 `docs/symbols/pins-and-ports.md`

Add a concrete explanation of:

- semantic port vs symbol port;
- symbol port vs visible pin lead;
- component `portMap` direction;
- `x`, `y`, `orientation`, `kind`;
- `name`, `number`;
- `labelVisible`, `numberVisible`;
- `snapRadius`;
- `visibleWhen`;
- variant `portOverrides`;
- port transform under placement rotation/mirroring;
- common mismatch diagnostics.

Include at least four diagrams/examples:

1. horizontal left pin;
2. horizontal right pin;
3. vertical power pin;
4. hidden/conditional pin case.

### 8.4 `docs/symbols/field-layout.md`

Add:

- field names and intended roles;
- `text` primitive with `field` binding;
- `fieldMap` relationship;
- semantic attribute fallback and override behavior;
- placement-level field overrides;
- reference/value placement rules;
- collision avoidance;
- rotation behavior;
- examples showing `reference`, `value`, and custom fields.

### 8.5 `docs/symbols/variants.md`

Add:

- exact variant-selection precedence;
- default variant behavior;
- variant graphics;
- parameter defaults;
- port overrides;
- suppression;
- endpoint identity invariants;
- a full IEC/ANSI resistor-style example based on validated assets.

### 8.6 `docs/file-formats/aixsym.md`

Make this the format overview, not a replacement for the full field reference.

Add:

- annotated top-level JSON skeleton;
- links to field reference and schema;
- minimal symbol example;
- extension and MIME semantics if applicable;
- version negotiation;
- deterministic serialization expectations;
- where asset digests are consumed.

### 8.7 `docs/file-formats/aixlib.md`

Add complete examples for:

- component properties;
- ports;
- presentations;
- `asset` binding;
- `fieldMap`;
- `portMap`;
- `defaultVariant`;
- digest/revision locking;
- multiple presentations.

### 8.8 `docs/file-formats/aixem.md`

Add:

- complete minimal semantic model;
- entity attributes;
- component type resolution;
- nets as endpoint membership;
- no-connect intent;
- clear statement that geometry is not stored here.

### 8.9 `docs/file-formats/aixlayout.md`

Add:

- placements;
- orientation/transform;
- variant/parameter/field overrides;
- route connections;
- endpoint references;
- `via` points;
- junctions;
- explicit separation between topology and geometry.

### 8.10 `docs/schematic/visual-language.md`

Add measurable authoring guidance rather than only presentation philosophy:

- preferred signal flow;
- grouping and alignment;
- whitespace rules;
- symbol spacing;
- wire channel spacing;
- junction visibility;
- label placement;
- avoidance of unnecessary wire jogs;
- hierarchy and visual density.

### 8.11 `docs/specifications/schematic/visual-profile.md`

Clarify its relationship to symbol-local styles. If style precedence changes, reference a new ADR and renderer contract rather than embedding implementation details only here.

### 8.12 `docs/specifications/symbols/symbol-contract.md`

Add or link normative requirements for:

- total port mapping;
- visible mapped-port constraint;
- deterministic parameter evaluation;
- stable variant semantics;
- local-only render dependencies;
- relationship between symbol asset and renderer contract.

### 8.13 `docs/routing/net-routing.md`

Keep normative routing rules concise, but add links to the routing cookbook and exact serialization examples for route endpoints and closure.

---

## 9. `AGENTS.md` Enhancement Plan

`AGENTS.md` remains the entry point, but 0.5.1 should make it more operational for drawing tasks.

### 9.1 Add explicit task classification

Add a decision table:

| Request type | Route |
|---|---|
| Create or modify only a symbol asset | `create-symbol` |
| Place existing components and define circuit semantics | `create-schematic` |
| Connect existing endpoints geometrically | `route-nets` |
| Render and inspect graphics | `render-review` |
| Create a new component and use it in a schematic | `author-component-circuit` composite workflow |
| Validate final output | `validate-project` |

### 9.2 Add composite route chaining

For a request such as “create a new 12-pin controller and connect it,” `AGENTS.md` shall direct the agent to:

```text
create-symbol
→ create-schematic
→ route-nets
→ render-review
→ validate-project
```

The agent must not treat the entire sequence as one unlimited search task.

### 9.3 Add artifact ownership checkpoints

Before editing, require the agent to classify each intended change:

```text
Component identity / endpoint set → .aixlib and semantic model
Visible body / pin graphics       → .aixsym
Instance position / rotation      → .aixlayout
Wire geometry                     → .aixlayout
Net membership                    → .aixem
Reference/value source            → semantic attrs / fieldMap / placement override
Stroke/color/font presentation    → symbol fallback style / active style profile per renderer contract
```

### 9.4 Add “documentation sufficiency before source-code inspection” rule

New rule:

> For normal authoring tasks, do not inspect renderer implementation code before reading the route-selected renderer contract and format reference. Source-code inspection is a fallback for an identified documentation/implementation discrepancy, not an ordinary discovery step.

### 9.5 Add stage-level completion checks

Each stage should have explicit exit conditions.

Example for symbol stage:

```text
[ ] Component endpoint contract is known
[ ] Symbol asset validates against schema
[ ] Every semantic port has a total mapping
[ ] Every mapped symbol port exists and is visible
[ ] Visible lead endpoint coincides with electrical port
[ ] Reference/value fields resolve
[ ] Grid/design-profile lint passes
[ ] Rendered symbol has been visually inspected
```

### 9.6 Add repair discipline

When visual output is wrong, `AGENTS.md` should require:

1. identify symptom;
2. map symptom to authority layer;
3. inspect resolved evidence;
4. modify only owning source;
5. regenerate;
6. compare before/after;
7. rerun narrow validator, then release validator if required.

---

## 10. Task Route Redesign

### 10.1 `create-symbol.yaml`

The route should prioritize practical authoring information while staying within the 7-document budget.

Recommended required sequence:

1. `AIXEM-CONCEPT-COMPONENT-001` — exact endpoint-contract section.
2. `AIXEM-SPEC-SYMBOL-DESIGN-001` — grid and symbol-design rules.
3. `AIXEM-SYMBOL-COOKBOOK-001` — recipe matching the component class.
4. `AIXEM-SYMBOL-AIXSYM-REF-001` — only exact fields/primitives needed.
5. `AIXEM-SYMBOL-BINDING-001` — port/field/presentation binding.
6. `AIXEM-SPEC-RENDERER-001` — only field/port/variant resolution sections when required.
7. `AIXEM-SYMBOL-LINT-001` — validation and evidence.

`Symbol Anatomy`, `Pins and Ports`, and `Primitives` remain canonical dependencies, but the route should use exact sections or conditional dependencies to avoid spending the entire budget on conceptual documents.

### 10.2 `create-schematic.yaml`

Recommended sequence:

1. authority/semantic model section;
2. schematic authoring cookbook;
3. grid/placement rules;
4. component-symbol binding section;
5. `.aixem`/`.aixlayout` format sections as exact references;
6. route-nets handoff;
7. project lock/validation.

### 10.3 `route-nets.yaml`

Recommended sequence:

1. net model;
2. routing normative rules;
3. routing cookbook matching topology;
4. crossings/junctions;
5. `.aixlayout` connection representation;
6. routing-agent behavior;
7. validation.

### 10.4 New `render-review.yaml`

Purpose: render and evaluate a completed symbol or schematic.

Steps:

1. renderer contract — input resolution;
2. visual QA loop;
3. symbol/schematic visual profile;
4. resolved-scene evidence reference;
5. validation architecture.

Expected outputs:

- deterministic SVG;
- workbench/viewer HTML where applicable;
- `resolved-scene.json`;
- validation report;
- visual review result.

### 10.5 New composite `author-component-circuit.yaml`

Prefer extending the route schema to support an ordered list of child routes rather than copying all their documents.

Conceptual form:

```yaml
id: author-component-circuit
kind: composite
stages:
  - route: create-symbol
    exit: symbol-ready
  - route: create-schematic
    exit: semantic-and-placement-ready
  - route: route-nets
    exit: routing-ready
  - route: render-review
    exit: visual-review-ready
  - route: validate-project
    exit: release-valid
```

If route schema v1.0 cannot represent composite routes, introduce a backward-compatible task-route schema revision and compiler support. Existing simple routes must remain valid.

---

## 11. Generated Agent Task Packets

Add a derived output layer:

```text
docs/_meta/generated/task-packets/
├── create-symbol.json
├── create-schematic.json
├── route-nets.json
├── render-review.json
└── author-component-circuit.json
```

These packets must not become independent authority. They should contain only compiled navigation/execution data such as:

- route ID;
- task class;
- ordered document IDs;
- exact section anchors;
- estimated bytes/tokens;
- expected input artifacts;
- expected output artifacts;
- validators;
- stage exit criteria;
- child routes for composites;
- source document digests.

This lets an agent obtain a compact execution map in one read while still loading authoritative content only when necessary.

Task packets must be regenerated from canonical docs and route metadata and included in manifest integrity checks.

---

## 12. Executable Documentation Examples

### 12.1 Golden example set

Create validated authoring examples that each isolate one concept.

Recommended source tree:

```text
examples/authoring/
├── 01-two-pin-passive/
├── 02-connector/
├── 03-multi-pin-ic/
├── 04-parameterized-variant/
├── 05-field-and-port-binding/
├── 06-two-terminal-route/
├── 07-multi-terminal-junction/
└── 08-visual-repair/
```

Each example should include only the artifacts needed for the concept and provide:

- source files;
- expected rendered SVG;
- expected `resolved-scene.json` subset or digest;
- validation result;
- README explaining the recipe;
- document links.

### 12.2 Required example classes

#### Example A — Two-pin passive

Proves:

- body + leads;
- port/lead coincidence;
- `reference` and `value` fields;
- `fieldMap` and `portMap`;
- basic placement and routing.

#### Example B — Connector

Proves:

- repeated pin pitch;
- numbering/naming;
- many total port mappings;
- body sizing from pin count.

#### Example C — Multi-pin IC

Proves:

- functional pin grouping;
- top/bottom power pins;
- left/right signal pins;
- field placement;
- compact rectangular body.

#### Example D — Parameterized variant

Proves:

- symbol parameter defaults;
- variant defaults;
- placement overrides;
- variant graphics;
- invariant endpoint semantics.

#### Example E — Field and port binding

Proves:

- semantic attributes;
- custom field mapping;
- placement override precedence;
- mapping error detection.

#### Example F — Multi-terminal junction

Proves:

- semantic multi-endpoint net;
- explicit geometric junction;
- crossing without accidental connectivity.

#### Example G — Visual repair

Begin with a deliberately invalid or poor artifact and document the repair path:

- lead endpoint mismatch;
- off-grid port;
- text collision;
- unnecessary route jog;
- incorrect junction marker.

The invalid inputs should live under a clearly marked test-fixture path and never be mistaken for canonical successful examples.

---

## 13. Example-Snippet Integrity

Manual duplication of JSON from examples into Markdown creates drift risk.

Implement one of the following approaches, in preference order:

### Option A — Source-backed include directives

Canonical docs reference JSON Pointer or named regions from validated example files. The site builder injects the snippet at build time.

Example conceptual syntax:

```text
{{ include-json: examples/authoring/01-two-pin-passive/symbols/resistor.aixsym.json#/symbol/ports }}
```

### Option B — Snippet verification

If literal code fences remain in Markdown, add metadata identifying the canonical source and JSON Pointer, then compare normalized content during tests.

In either approach:

- examples must validate before docs build;
- snippets must fail CI if source changes without documentation regeneration;
- generated site snippets must be syntax highlighted;
- schema-version labels should be shown next to examples.

---

## 14. Renderer and Style Precedence Work

### 14.1 Create an ADR before behavioral changes

Add:

`docs/architecture/adr/0004-symbol-style-and-renderer-precedence.md`

The ADR must answer:

1. What is intrinsic symbol geometry?
2. What is local symbol fallback style?
3. What is project-level schematic style?
4. Which layer can override color, stroke, font, and visibility?
5. Which properties may never affect semantic connectivity?
6. How are old 0.5.0 symbol styles rendered under 0.5.1?

### 14.2 Recommended target model

Subject to compatibility validation:

```text
Symbol asset
  owns geometry, roles/classes, and deterministic fallback style

Active schematic style profile
  owns project-level presentation tokens and approved role overrides

Renderer
  resolves style deterministically according to documented precedence
```

No profile override may move a port, alter a semantic endpoint, change net membership, or redefine component identity.

### 14.3 Compatibility requirement

A 0.5.0 symbol that does not use any new optional 0.5.1 mechanism must continue to render deterministically and validly in 0.5.1 unless a formally documented compatibility defect requires a migration.

---

## 15. Validation and Tooling Enhancements

### 15.1 Documentation coverage validator

Add a validator that compares schema declarations with documentation coverage.

Suggested file:

`tests/docs/test_authoring_reference_coverage.py`

Checks:

- every `.aixsym` top-level property is documented;
- every symbol primitive type is documented;
- every port property is documented;
- parameter and variant fields are documented;
- component presentation mapping fields are documented;
- layout connection fields are documented;
- documented JSON field names resolve to the active schema.

### 15.2 JSON example validator

Suggested file:

`tests/docs/test_authoring_examples.py`

Checks:

- every JSON code example parses;
- complete examples validate against the declared schema;
- source-backed snippets resolve;
- referenced example paths exist;
- example schema versions match documentation metadata.

### 15.3 Symbol geometry lint expansion

Add validation for measurable design-profile rules that can be checked mechanically:

- port on allowed grid;
- lead endpoint matches port within tolerance;
- required port mapping is total;
- mapped port is visible;
- body bounds contain intended geometry;
- text anchors do not trivially overlap body bounding box where prohibited;
- pin spacing obeys profile for standard recipes;
- no unsupported primitive features are used.

Not every visual rule needs to be automated. Review-mode requirements may remain visual where geometry heuristics would be unreliable.

### 15.4 Renderer contract tests

Create dedicated tests for:

- field precedence;
- placement field override;
- variant precedence;
- parameter precedence;
- port mapping direction and totality;
- hidden mapped-port rejection;
- definition/use parameter propagation;
- deterministic resolved-scene output;
- deterministic SVG output.

### 15.5 Route sufficiency tests

Suggested file:

`tests/agent/test_authoring_routes.py`

Checks:

- `create-symbol` resolves within 7 documents and 96 KiB;
- required authoring docs exist;
- exact section anchors exist;
- composite route expands into allowed child routes;
- no route depends on generated output as normative authority;
- task packets reproduce route source digests.

### 15.6 English-only canonical documentation validation

Extend the existing language check so new authored documentation, route summaries, and site labels introduced in 0.5.1 are checked for the release language policy. Machine data such as external identifiers is exempt where necessary.

---

## 16. Agent Evaluation Harness

Static documentation completeness is not enough. 0.5.1 should include task-level agent evaluations that measure whether the route system actually enables drawing work.

Create:

```text
validation/agent-evals/
├── README.md
├── tasks/
├── expected/
├── results/
└── scoring.md
```

### 16.1 Evaluation task set

At minimum:

#### EVAL-01 — New two-pin component

Prompt goal: create a new passive component and symbol, bind reference/value, place two instances, connect them.

#### EVAL-02 — Six-pin connector

Prompt goal: create a connector with correct pin pitch, numbering, total port mapping, and field layout.

#### EVAL-03 — Twelve-pin controller

Prompt goal: create a functional multi-pin IC symbol grouped by signal role and connect it into a small circuit.

#### EVAL-04 — Variant override

Prompt goal: use a parameterized symbol, choose a non-default variant, and apply placement parameters.

#### EVAL-05 — Junction semantics

Prompt goal: route a three-endpoint net with one explicit junction and one unrelated crossing.

#### EVAL-06 — Field override

Prompt goal: map a semantic property to a symbol field and override that field for one placement.

#### EVAL-07 — Visual repair

Prompt goal: detect and fix a symbol whose lead endpoint and port coordinate do not coincide.

#### EVAL-08 — Authority-layer diagnosis

Prompt goal: diagnose a correct-looking route attached to the wrong semantic net without incorrectly modifying symbol geometry.

### 16.2 Scoring

Score each task on:

- route compliance;
- number of docs loaded;
- repository-wide search count;
- schema validity;
- semantic closure;
- port mapping correctness;
- grid compliance;
- route correctness;
- visual profile compliance;
- renderer success;
- conformance pass;
- unnecessary source-code inspection;
- deterministic rerender.

Suggested release target:

```text
Schema validity                    100%
Semantic/port closure              100%
Required route budget compliance   100%
Renderer success                   100%
Deterministic rerender             100%
Visual-review pass                 ≥ 95% task checks
Repository-wide search             0 for normal successful tasks
Renderer source inspection         0 for normal successful tasks
```

The evaluation harness may initially be human-triggered, but task fixtures and scoring criteria must be stored in the repository.

---

## 17. Documentation Site Enhancements

The static official documentation site should expose authoring workflows directly.

### 17.1 New navigation group

Add a prominent **Authoring** group:

```text
Authoring
├── Create a Component Symbol
├── AIXSYM Field Reference
├── Component ↔ Symbol Binding
├── Create a Schematic
├── Route Nets
├── Render and Review
└── Troubleshooting
```

### 17.2 Page-level improvements

Authoring pages should include:

- “Agent route” badge;
- document status badge;
- schema/version badge;
- inputs and outputs;
- authoritative owner;
- exact validation commands;
- code examples;
- rendered preview where useful;
- “common mistakes” section;
- related task route links.

### 17.3 Schema-aware reference pages

Where feasible, generate field tables from the active JSON Schema and merge them with authored explanations. This reduces drift while preserving human-readable guidance.

---

## 18. File-Level Change Matrix

### New canonical docs

| Path | Planned role |
|---|---|
| `docs/symbols/authoring-cookbook.md` | practical symbol recipes |
| `docs/symbols/aixsym-field-reference.md` | field-level `.aixsym` reference |
| `docs/symbols/component-symbol-binding.md` | `.aixlib` ↔ `.aixsym` ↔ semantic binding |
| `docs/symbols/design-rules.md` or normative spec link page | concise entry to symbol design profile |
| `docs/schematic/authoring-cookbook.md` | `.aixem` + `.aixlayout` recipes |
| `docs/routing/routing-cookbook.md` | worked routing patterns |
| `docs/specifications/symbols/symbol-design-profile.md` | measurable normative symbol design rules |
| `docs/specifications/renderer/renderer-contract.md` | deterministic renderer behavior/precedence |
| `docs/agent/authoring-orchestration.md` | route chaining and composite work |
| `docs/agent/visual-qa-loop.md` | render-inspect-repair loop |
| `docs/architecture/adr/0004-symbol-style-and-renderer-precedence.md` | style authority decision |

### Existing canonical docs to modify

| Path | Main change |
|---|---|
| `AGENTS.md` | task classifier, composite workflows, drawing checkpoints, repair discipline |
| `docs/symbols/authoring-guide.md` | executable workflow and output checklist |
| `docs/symbols/primitives.md` | all primitive types + JSON examples |
| `docs/symbols/pins-and-ports.md` | visible lead vs electrical port, port fields, mapping |
| `docs/symbols/field-layout.md` | field binding, precedence, collision rules |
| `docs/symbols/variants.md` | selection/parameter precedence and examples |
| `docs/symbols/symbol-lint.md` | new design-profile checks |
| `docs/file-formats/aixsym.md` | annotated skeleton and links |
| `docs/file-formats/aixlib.md` | presentation, fieldMap, portMap examples |
| `docs/file-formats/aixem.md` | complete semantic example |
| `docs/file-formats/aixlayout.md` | placement and connection examples |
| `docs/schematic/visual-language.md` | measurable layout/drawing guidance |
| `docs/specifications/schematic/visual-profile.md` | style-authority relationship |
| `docs/specifications/symbols/symbol-contract.md` | binding/visibility/determinism links and requirements |
| `docs/routing/net-routing.md` | serialization anchors and cookbook links |
| `docs/routing/crossings-and-junctions.md` | complete 3-terminal/crossing examples |
| `docs/conformance/validation.md` | new authoring validators |
| `docs/conformance/test-suite.md` | new tests and evaluation coverage |
| `docs/_meta/navigation.yaml` | Authoring navigation |
| `docs/_meta/aliases.yaml` | authoring intents/terms |
| `docs/_meta/artifact-ownership.yaml` | renderer/style/binding ownership clarification |

### Route files

| Path | Change |
|---|---|
| `docs/_meta/routes/create-symbol.yaml` | practical recipe and renderer-binding coverage |
| `docs/_meta/routes/create-schematic.yaml` | cookbook and format coverage |
| `docs/_meta/routes/route-nets.yaml` | routing cookbook and layout representation |
| `docs/_meta/routes/validate-project.yaml` | authoring-design validators |
| `docs/_meta/routes/render-review.yaml` | new route |
| `docs/_meta/routes/author-component-circuit.yaml` | new composite route |

### Implementation/tooling

| Area | Planned change |
|---|---|
| documentation compiler | task packets, snippet includes/verification, schema reference extraction |
| route compiler | composite route support if required |
| renderer tests | explicit precedence and deterministic-output tests |
| symbol lint | design-profile checks |
| docs tests | schema/reference coverage checks |
| example validation | executable authoring fixtures |
| release integrity | include new generated artifacts and eval fixtures |

---

## 19. Detailed Implementation Sequence

### Phase 0 — Freeze and Inventory

1. Freeze 0.5.0 as the comparison baseline.
2. Record digests of all existing canonical authoring docs, routes, schemas, renderer implementation, style profile, and example assets.
3. Produce a field/behavior inventory from:
   - symbol schema;
   - component library schema;
   - layout schema;
   - current renderer;
   - existing validated examples.
4. Create a gap table: behavior/field → current doc owner → target 0.5.1 doc owner.
5. Mark each rule as normative, informative, generated, or implementation-only.

**Exit criterion:** every authoring-relevant schema field and runtime resolution behavior has one planned documentation owner.

### Phase 1 — Formalize Contracts

1. Write the renderer contract.
2. Write the symbol design profile.
3. Write the style/renderer precedence ADR.
4. Clarify component-symbol binding rules.
5. Add requirement IDs and conformance mappings.
6. Add renderer precedence tests before changing any behavior.

**Exit criterion:** agents no longer need renderer source to discover ordinary binding/precedence rules.

### Phase 2 — Build Practical Authoring Guides

1. Write symbol authoring cookbook.
2. Expand primitives reference.
3. Expand pins/ports and field layout.
4. Expand variants/parameters guidance.
5. Write schematic authoring cookbook.
6. Write routing cookbook.
7. Add complete examples for all common artifact interactions.

**Exit criterion:** all common authoring workflows have at least one end-to-end validated worked example.

### Phase 3 — Make Examples Executable

1. Add `examples/authoring/` fixtures.
2. Implement snippet inclusion or verification.
3. Validate every complete example against active schemas.
4. Render all successful fixtures.
5. Store deterministic expected evidence/digests where appropriate.

**Exit criterion:** documentation examples fail CI when they stop matching actual formats or renderer behavior.

### Phase 4 — Upgrade Agent Orchestration

1. Update `AGENTS.md`.
2. Add authoring orchestration doc.
3. Add visual QA loop doc.
4. Modify `create-symbol`, `create-schematic`, and `route-nets` routes.
5. Add `render-review` route.
6. Add composite `author-component-circuit` route.
7. Extend task-route schema/compiler only if necessary.
8. Generate task packets.

**Exit criterion:** a cold-start agent can resolve a composite drawing task without a repository-wide search.

### Phase 5 — Conformance and Evaluation

1. Add schema-to-doc coverage test.
2. Add authoring-example tests.
3. Add symbol design-profile lint rules.
4. Add renderer precedence tests.
5. Add route sufficiency tests.
6. Add agent-evaluation fixtures and scoring.
7. Run all existing 0.5.0 regression tests.

**Exit criterion:** all new documentation claims are backed by machine validation or explicit review-mode evidence.

### Phase 6 — Site Publication

1. Add Authoring navigation.
2. Publish field reference tables.
3. Add rendered example previews.
4. Add task-route badges and validation instructions.
5. Check desktop and narrow viewport rendering.
6. Regenerate search/index/manifest artifacts.

**Exit criterion:** official site users and agents can reach the same authoritative authoring knowledge through different navigation surfaces.

---

## 20. Three-Pass Refinement Loop

The implementation should be completed through three full refinement passes rather than a single write-and-publish cycle.

### PASS 1 — Completeness and Contract Closure

Focus: **Does every required rule have a canonical owner?**

Actions:

- compare schemas to docs;
- compare renderer behavior to renderer contract;
- compare style profile to symbol design profile;
- verify every supported primitive;
- verify every port/field/variant/parameter mechanism;
- verify every binding direction;
- verify every authoring route has exact section anchors;
- remove duplicated normative definitions.

Gate:

```text
Schema field coverage                100%
Primitive type coverage              100%
Renderer precedence coverage         100%
Task-route target existence          100%
Broken canonical links               0
Duplicate normative ownership        0 unresolved
```

### PASS 2 — Agent Usability and Drawing Quality

Focus: **Can an agent actually perform the work efficiently?**

Actions:

- run all authoring evaluation tasks from `AGENTS.md` only;
- record documents loaded;
- reject unnecessary repository-wide searches;
- inspect generated symbol graphics;
- inspect field/port bindings;
- inspect route topology;
- measure context budget;
- rewrite ambiguous sections;
- replace verbose generic guidance with high-density examples where possible.

Gate:

```text
Normal task repo-wide search         0
Normal task renderer-code lookup     0
Route budget violations              0
Schema-valid outputs                 100%
Semantic closure                     100%
Port mapping                         100%
Render success                       100%
Visual QA checks                     ≥95%
```

### PASS 3 — Release Integrity and Regression

Focus: **Is 0.5.1 deterministic, compatible, and publishable?**

Actions:

- run full documentation build twice and compare generated metadata;
- render golden examples repeatedly and compare digests;
- run full repository test suite;
- verify legacy 0.5.0 example compatibility;
- verify English-only docs policy;
- verify release manifest completeness;
- verify ZIP/package integrity;
- perform final human visual review of site and workbench outputs.

Gate:

```text
Full tests                           PASS
Generated docs deterministic         PASS
Golden renders deterministic         PASS
0.5.0 baseline examples              PASS or documented migration
Requirement traceability             100%
Manifest coverage                    100%
Release-critical diagnostics         0
```

If a pass fails, repair and rerun that pass before advancing. The release must not report a pass that was not actually executed.

---

## 21. Acceptance Criteria by Workflow

### 21.1 Create a new symbol

An agent starting from `AGENTS.md` must be able to:

- find the symbol route;
- select the correct recipe;
- create a valid symbol file;
- create visible body and lead geometry;
- create ports at exact connection coordinates;
- bind reference/value fields;
- validate geometry;
- render and visually inspect output;
- complete within the route budget.

### 21.2 Bind a component to a symbol

The docs must make it unambiguous how to:

- define semantic component ports;
- define component properties;
- point to the symbol asset;
- map every semantic port through `portMap`;
- map properties through `fieldMap`;
- resolve asset digest/revision;
- choose a default variant;
- diagnose incomplete or invalid mappings.

### 21.3 Place and connect components

The docs must make it unambiguous how to:

- create semantic entities;
- define nets;
- create no-connect intent;
- place all entities;
- resolve all route endpoints;
- add orthogonal bends;
- add explicit junctions;
- distinguish crossing from connectivity;
- render and validate route closure.

### 21.4 Use parameters and variants

The docs must state and demonstrate:

- parameter type definitions;
- defaults and bounds;
- numeric expressions;
- variant parameter defaults;
- placement parameter overrides;
- variant selection precedence;
- port override restrictions;
- endpoint identity invariants.

### 21.5 Diagnose visual defects

The agent must be able to determine from documentation whether a defect belongs to:

- semantic source;
- component library;
- symbol asset;
- layout;
- style profile;
- renderer;
- generated evidence.

It must then modify the authoritative owner and rerun the appropriate validation loop.

---

## 22. Definition of Done

AIXEM 0.5.1 Agent Authoring & Drawing Documentation work is complete only when all conditions below are met.

### Documentation

- [ ] All new canonical docs exist with stable IDs and metadata.
- [ ] All new/modified canonical docs are English-only.
- [ ] Every `.aixsym` authoring field is covered by an agent-readable reference.
- [ ] Every supported graphic primitive has a minimal valid example.
- [ ] `portMap`, `fieldMap`, field precedence, variant precedence, and parameter precedence are documented.
- [ ] Visible pin lead vs electrical port semantics are explicitly documented.
- [ ] `.aixem` vs `.aixlayout` authority separation is demonstrated with complete examples.
- [ ] Multi-terminal routing and junction behavior are demonstrated.
- [ ] Style precedence is resolved by ADR and renderer contract.

### Agent navigation

- [ ] `AGENTS.md` includes task classification and composite chaining.
- [ ] `create-symbol`, `create-schematic`, `route-nets`, `render-review`, and composite authoring routes resolve.
- [ ] Routes stay within the configured context budget.
- [ ] Generated task packets are deterministic and manifest-covered.
- [ ] Normal authoring tasks do not require repository-wide search.

### Examples

- [ ] Two-pin passive golden example passes.
- [ ] Connector golden example passes.
- [ ] Multi-pin IC golden example passes.
- [ ] Parameter/variant golden example passes.
- [ ] Field/port binding golden example passes.
- [ ] Multi-terminal junction golden example passes.
- [ ] Visual-repair fixture proves the repair workflow.
- [ ] Documentation snippets are source-backed or mechanically verified.

### Validation

- [ ] Schema/reference coverage validator passes.
- [ ] Example validator passes.
- [ ] Renderer precedence tests pass.
- [ ] Symbol geometry lint passes.
- [ ] Route sufficiency tests pass.
- [ ] Agent evaluation suite meets release thresholds.
- [ ] Existing 0.5.0 regression suite passes.
- [ ] Deterministic rerender checks pass.
- [ ] Requirement traceability is complete.
- [ ] Release manifest and package integrity pass.

---

## 23. Recommended 0.5.1 Deliverables

The final 0.5.1 release package should contain at minimum:

```text
AGENTS.md
README.md
IMPLEMENTATION_STATUS.md

0.5.1 release notes

canonical docs with all new authoring material
updated routes and metadata
compiled route index
generated task packets
schema-aware references

examples/authoring/*
rendered golden outputs
validation evidence
agent evaluation fixtures/results

updated documentation site
updated renderer/reference tests
updated conformance mappings
release manifest
final validation report
```

The final validation report should include a dedicated **Agent Authoring Readiness** section showing:

- number of authoring docs;
- field/primitive coverage percentages;
- route budgets;
- evaluation-task results;
- number of repository-wide searches needed per successful eval;
- number of renderer-source inspections needed per successful eval;
- deterministic render results;
- unresolved documentation gaps, if any.

---

## 24. Priority Order

If the work must be staged, execute in this order:

### P0 — Required before claiming agent drawing readiness

1. renderer contract;
2. symbol design profile;
3. component-symbol binding guide;
4. symbol authoring cookbook;
5. `.aixsym` field/primitive reference;
6. schematic authoring cookbook;
7. routing cookbook;
8. `AGENTS.md` composite workflow update;
9. route changes;
10. executable golden examples;
11. renderer/binding precedence tests;
12. symbol lead/port geometry validation.

### P1 — Required for release-quality usability

1. task packets;
2. visual QA route;
3. agent evaluation harness;
4. source-backed documentation snippets;
5. schema-aware generated reference tables;
6. official site Authoring navigation.

### P2 — Follow-up optimization

1. richer visual-quality metrics;
2. additional cookbook device classes;
3. auto-generated symbol templates;
4. authoring assistant CLI helpers;
5. future localization layer.

P2 items must not delay the core documentation sufficiency target.

---

## 25. Final Target State

The intended 0.5.1 relationship is:

```text
                         ┌─────────────────────┐
                         │      AGENTS.md      │
                         └──────────┬──────────┘
                                    │
                           classify task intent
                                    │
                         ┌──────────▼──────────┐
                         │ route-index / pack │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
          create-symbol       create-schematic    route-nets
                  │                 │                 │
                  └────────────┬────┴─────┬──────────┘
                               │          │
                     canonical authoring docs
                               │
              ┌────────────────┼────────────────┐
              │                │                │
          .aixsym          .aixlib          .aixem/.aixlayout
              │                │                │
              └────────────────┴───────┬────────┘
                                       │
                              renderer contract
                                       │
                              deterministic render
                                       │
                   ┌───────────────────┴───────────────────┐
                   │                                       │
            resolved-scene.json                     workbench/SVG
                   │                                       │
                   └───────────────────┬───────────────────┘
                                       │
                               visual QA loop
                                       │
                               conformance tests
                                       │
                                final artifact
```

The key quality bar is simple:

> **An AI agent should be able to learn how AIXEM draws, binds, places, connects, renders, and validates a schematic by following the documented route chain, rather than reverse-engineering the implementation.**

That is the defining objective of AIXEM 0.5.1.
