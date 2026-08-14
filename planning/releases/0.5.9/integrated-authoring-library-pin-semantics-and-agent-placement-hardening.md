# AIXEM 0.5.2 — Integrated Authoring, Library Integrity, Pin Semantics, and Agent Placement Hardening Plan

**Integrated plan version:** 0.5.2  
**Plan status:** consolidated implementation-ready draft  
**Source plan A:** AIXEM 0.5.9 — Authoring Grid, Symbol Sizing, Task Guides, Library Structure, Provenance, and Part Integrity Hardening Plan  
**Source plan B:** AIXEM 0.5.10 — Pin Electrical Semantics, Agent Placement Strategy, and Authoring Decision Guidance Hardening Plan  
**Integration rule:** both source scopes are retained; overlapping Agent guidance, placement, validation, provenance, and compatibility concerns are treated as one implementation program rather than competing authorities.  
**Core file-format impact:** no schema URI/version bump intended by either source plan  
**Renderer / Viewer impact:** no feature expansion intended  
**Simulation engine impact:** none; simulation remains a future backend integration  
**Auto-layout engine impact:** no global solver; deterministic placement assist plus Agent-guided placement strategy only  
**External AI execution:** unchanged from the active baseline policy  

---

## 1. Integrated Objective

This 0.5.2 document consolidates both source plans into one execution plan.

The integrated objective is to make AIXEM sufficiently deterministic and semantically explicit that a fresh AI Agent can:

```text
find the correct authoring guidance
    -> create or select a valid reusable part
    -> preserve source provenance
    -> author complete component and pin semantics
    -> size symbols from the G/P/M rhythm
    -> place components using explicit semantic evidence
    -> route on the authoritative grid
    -> validate structural, part-semantic, bounded electrical,
       and circuit-intent claims separately
    -> preserve compatibility and deterministic rendering
```

without taking any of the following shortcuts:

```text
arbitrary library path
geometry-only component ID multiplication
unsourced concrete part identity
pin name -> invented electrical truth
symbol appearance -> component identity
visual proximity -> semantic connectivity
compactness -> placement correctness
render PASS -> datasheet correctness
basic electrical compatibility -> simulation correctness
metadata -> solver model
```

The integrated release remains deliberately conservative. It strengthens the authoring contract, Agent decision procedure, validation layers, and future simulation readiness without adding a global auto-layout engine, datasheet crawler, universal component taxonomy, full ERC engine, or simulation solver.

---

## 2. Unified Authority Model

The combined plan uses the following authority split:

```text
.aixlib.json component ports
    -> stable endpoint identity
    -> electrical behavior through port.type
    -> extended pin meaning through metadata.pinSemantics
    -> component provenance and minimum semantic contract

.aixsym.json
    -> reusable graphic presentation
    -> symbol-local ports and visual geometry

portMap
    -> semantic component endpoint <-> graphic symbol endpoint

.aixem
    -> schematic entities and semantic net membership

.aixlayout.json
    -> component placement and route geometry

active style profile
    -> G/P/M grid and symbol construction rhythm

Agent task guides
    -> informative execution façade

canonical specifications / validators
    -> normative requirements and machine-checkable conformance
```

The Agent guide layer never becomes a second normative specification.

---

## 3. Unified Validation Claim Hierarchy

The combined plan retains and extends the source-plan claim separation:

```text
schema / binding / geometry / deterministic render
    -> STRUCTURAL_PASS

part provenance + source-bound pinout + minimum semantic attributes
    -> PART_SEMANTIC_PASS

pin semantic profile + bounded static electrical compatibility
    -> PIN_SEMANTIC / COMPATIBILITY RESULT

actual circuit-use review
    -> CIRCUIT_INTENT_REVIEW_PASS
```

A compatibility precheck may produce:

```text
PASS
WARN
ERROR
NOT_EVALUATED
```

but must not claim electrical safety, timing correctness, voltage compatibility, simulation correctness, or production readiness.

---

## 4. Unified Agent Authoring Chain

The consolidated task path is:

```text
AGENTS.md / REFERENCE.md
    -> docs/authoring/guides/index.md
    -> create-library-part OR select-library-part
    -> create-schematic
    -> place-components
    -> route-nets
    -> render-review
    -> validate-project
```

For an existing circuit:

```text
modify-existing-schematic
    -> freeze unaffected valid authority
    -> change the smallest semantic/layout region
    -> preserve unrelated coordinates and route geometry
    -> regenerate derived artifacts
    -> compare and validate
```

---

## 5. Unified P0 Scope

The combined P0 implementation scope is:

1. canonical `library/<electronics|architecture>/...` new-artifact structure;
2. generic lower-kebab namespace and file naming;
3. component-level provenance and source-or-placeholder discipline;
4. semantic component contract and geometry-clone protection;
5. structural-vs-semantic-vs-intent validation claim separation;
6. G/P/M symbol-sizing rhythm;
7. grid authority closure and deterministic snap/magnetic assist;
8. task-oriented Agent guide layer;
9. Pin Electrical Semantics Profile;
10. pin semantic validation;
11. bounded electrical compatibility precheck;
12. `place-components.md`;
13. `select-library-part.md`;
14. `modify-existing-schematic.md`;
15. route/reference chaining and retrieval-budget preservation;
16. agent-visible example/generator migration;
17. focused path/provenance/pin/ERC/placement fixtures;
18. full inherited regression;
19. five independent clean verification passes after the last fix.

---

# TRACK A — FOUNDATION AUTHORING, LIBRARY, PROVENANCE, GRID, AND GUIDE HARDENING

The following track incorporates the complete detailed scope of the former 0.5.9 plan. Historical source-version references inside this track describe the origin and compatibility context of that scope; implementation is governed by this integrated 0.5.2 plan.

### 1. Executive Summary

AIXEM 0.5.8.1 is ready for external-agent integration at the execution-harness level, but five authoring-discipline gaps remain worth closing before the first real agent is attached:

1. **placement is grid-valid but still reactive** — the system validates the 2.5 mm grid after an edit but does not yet provide a bounded deterministic snap/alignment suggestion before the edit;
2. **symbol sizing is specified but not sufficiently task-facing** — the current Symbol Design Profile already defines grid-quantized body dimensions, 5 mm pin pitch/lead defaults, and a pin-count-derived body-span rule, but those rules are distributed across the symbol profile, cookbook, field-layout, and example corpus rather than exposed as one concise sizing rhythm that a fresh Agent can apply immediately;
3. **library artifact placement is under-specified** — `.aixlib.json` and `.aixsym.json` have strong content contracts, but there is no canonical project-root directory contract that tells an agent where a newly created reusable part belongs;
4. **part provenance and semantic integrity are not closed strongly enough** — the existing schemas already provide a `sourceUri` field inside library/symbol provenance, but it is optional, library provenance is file-level rather than component-ID-level, and no rule prevents an Agent from creating a specific real-world part identity with an invented pinout or from generating many new IDs by cloning geometry alone;
5. **task guidance is distributed rather than task-indexed** — practical material exists under `docs/symbols/`, `docs/schematic/`, `docs/routing/`, `docs/agent/`, and generated task packets, but there is no single authored task-guide directory where an Agent can start with “create a library part”, “create a schematic”, “route nets”, or “compose a project” and immediately obtain the workflow, authority boundary, output location, validation commands, and links to the normative owners.

The library-location gap is already proven to be operationally relevant. In the 0.5.8.1 baseline:

- the `create-symbol` route allows writes to `**/*.aixsym.json` and `**/*.aixlib.json` anywhere inside the authorized workspace;
- the project composition contract only requires paths to be safe and project-root relative;
- `.aixlib.json` defines library content and digest locking but does not define a canonical storage root;
- official authoring examples are generated under `libraries/` and `symbols/`;
- no authoring rule explicitly says that reusable library artifacts must not be created under `examples/`;
- the component `classification` field is semantic metadata, not a governed directory taxonomy and is frequently empty.

Therefore an AI agent that is asked to "create a library part" has enough information to build a technically valid symbol/library, but not enough information to choose a stable repository/project location. Creating `examples/parts/...`, `parts/...`, `libraries/...`, or another plausible structure is not currently contradicted strongly enough by the canonical authoring contract.

0.5.9 should fix this without designing a universal component taxonomy.

The canonical new-authoring shape shall be:

```text
<project-root>/
├── project.aixproj.json
├── ... project sources ...
└── library/
    ├── electronics/
    │   └── <semantic-namespace...>/
    │       ├── <library-name>.aixlib.json
    │       └── <symbol-name>.aixsym.json
    └── architecture/
        └── <semantic-namespace...>/
            ├── <library-name>.aixlib.json
            └── <symbol-name>.aixsym.json
```

Only the first level is centrally classified in 0.5.9:

```text
library/electronics/
library/architecture/
```

Everything below that level remains intentionally extensible. AIXEM governs **how names are formed and how existing namespaces are reused**, not a fixed global catalog of second-level categories.

This is important for long-term generality. AIXEM should be able to represent:

```text
library/electronics/passive/resistor/...
library/electronics/integrated-circuit/microcontroller/vendor-family/...
library/electronics/connectivity/board-connector/...

library/architecture/opening/door/...
library/architecture/electrical/device/...
library/architecture/annotation/fire-safety/...
```

without the core standard having to pre-approve `passive`, `microcontroller`, `door`, `fire-safety`, or any future category.

0.5.9 must also close the distinction between **graphic validity** and **part validity**.

The required claim hierarchy is:

```text
schema / binding / geometry / deterministic render PASS
    = STRUCTURAL PASS only

component provenance + pinout/source review + minimum semantic attributes
    = PART SEMANTIC REVIEW PASS

part semantic review + actual circuit-use review
    = CIRCUIT INTENT REVIEW PASS
```

A successful SVG render MUST NOT be described as proof that a manufacturer part number, datasheet pinout, electrical role, rating, or intended circuit use is correct.

For a component ID that claims one specific real-world/orderable part, 0.5.9 requires component-level provenance with a stable `sourceUri` identifying the source datasheet. If that concrete identity cannot be sourced confidently, the component must be explicitly marked as a placeholder and must not receive a semantic-ready claim. Generic component templates remain allowed only when they make no false claim to a specific real manufacturer part.

Geometry reuse remains legal and desirable. **Geometry-only ID multiplication does not.** Several real parts may legitimately share one symbol asset, but every component ID must still own a reviewable semantic contract consisting of pin/terminal inventory, relevant properties, provenance status/source, and presentation binding.

0.5.9 also introduces a deliberately small **task-oriented guide façade** without creating a second source of truth:

```text
AGENTS.md
    -> REFERENCE.md
    -> docs/authoring/guides/index.md
    -> task-specific guide
    -> authored task route / generated task packet
    -> canonical specification / cookbook / validator
```

The guides are informative execution maps. Normative rules remain in their existing canonical owners. `AGENTS.md` only points to the guide index and never becomes a copy of the task manuals.

0.5.9 also absorbs the previously planned 0.5.8.2 grid/snap work. The result should be the last deterministic authoring-structure release before real Agent Tier B execution.

---

### 2. Baseline Review — Grid and Placement

#### 2.1 Existing grid system is already strong

The reference schematic profile already defines:

```text
base snap grid    G = 2.5 mm
minor grid          = 2.5 mm
pin pitch         P = 5.0 mm = 2G
major grid        M = 10 mm  = 4G
pin length          = 5.0 mm
routing             = orthogonal
minimum route       = 2.5 mm
```

Existing validators already detect:

- off-grid component origins;
- off-grid route bends;
- non-orthogonal routes;
- symbol ports outside the permitted authoring grid;
- missing/invalid placement closure.

The remaining grid weakness is therefore not missing conformance. It is missing **proactive deterministic placement assistance** and incomplete route visibility of the canonical placement rules.

#### 2.2 Placement guidance exists but is split across documents

AIXEM already recommends:

- left-to-right signal flow;
- functional grouping;
- shared rows and columns for related components;
- repeated visual rhythm;
- a practical 5 mm channel near routing and symbol bodies;
- preserving whitespace before compressing symbols or text.

However the normal `create-schematic` cold-start packet does not directly stage the canonical Component Placement document, while `route-nets` does not directly stage all hard grid/route-constraint owners.

#### 2.3 Grid authority needs one explicit owner

`.aixlayout.json` carries `coordinateSystem.grid`, while conformance is actually governed by the active style profile `grid.snap`.

Current examples use matching values, so no failure occurs. The contract should still be closed before live authoring:

```text
active styleProfile.grid.snap
    = schematic placement/routing snap authority

layout.coordinateSystem.grid
    = serialized declaration that MUST agree with the active profile
      under Grid Schematic Profile 1

symbol-local coordinate grid
    = symbol-authoring metadata only;
      cannot override schematic placement/routing snap
```

---

### 3. Baseline Review — Library Structure and Naming

#### 3.1 Strong content contracts already exist

AIXEM 0.5.8.1 already has clear authority for:

```text
.aixlib.json  -> reusable component definitions, endpoint/property contracts,
                 presentations, port/field maps, locked asset references

.aixsym.json  -> reusable symbol graphics, ports, variants, and presentation geometry

.aixproj.json -> project-level references to libraries and digest locks
```

The library format requires schema validity and local digest-locked symbol references. Component/symbol binding direction is also well defined.

This work must be preserved.

#### 3.2 Missing canonical project-library location — confirmed gap

There is no normative rule equivalent to:

```text
new reusable library artifacts MUST be created below <project-root>/library/
```

Instead, current rules only establish project-relative safe paths.

That makes several locations technically plausible to an agent:

```text
libraries/
symbols/
parts/
examples/parts/
assets/components/
my-library/
```

The format layer cannot distinguish which one was intended.

#### 3.3 Official examples actively reinforce the old ambiguous structure

The 0.5.8.1 authoring examples are generated in structures such as:

```text
examples/authoring/01-two-pin-passive/
├── libraries/authoring.aixlib.json
└── symbols/resistor.aixsym.json
```

The electronics grid-controller example follows the same pattern.

The example generator itself writes to `libraries/` and symbol files to `symbols/`.

This is valid historical behavior, but it means an AI agent using the examples as structural precedent has no reason to infer the desired new `library/<domain>/...` structure.

#### 3.4 `create-symbol` write scope is path-wide

The current route authorizes:

```text
**/*.aixsym.json
**/*.aixlib.json
```

and allows project-manifest digest updates.

That is appropriate for editing existing arbitrary paths, but insufficient for **new artifact placement** because it does not distinguish:

```text
edit an existing legacy artifact at its declared location
```

from:

```text
create a brand-new reusable artifact
```

0.5.9 must make that distinction.

#### 3.5 Existing `classification` metadata is not a directory taxonomy

Component definitions include a `classification` field, but 0.5.8.1 does not make it a controlled path taxonomy and examples may leave it empty.

0.5.9 MUST NOT turn this field into a mandatory universal classification system merely to solve folder placement.

Directory classification and semantic component classification remain related but separate concerns.

#### 3.6 `examples/` must remain example authority, not reusable-library authority

`examples/` exists to demonstrate authored projects and patterns. It should not become the default destination for newly requested reusable parts.

A live agent may read and adapt an example, but unless the explicit task is **authoring an example fixture**, it must not create production/reusable library artifacts under `examples/`.

This distinction must appear directly in the authoring route and Agent guidance.

---


### 4. Baseline Review — Part Provenance, Bulk Generation, and Validation Claim Boundaries

#### 4.1 `sourceUri` already exists, but the current ownership level is insufficient

The 0.5.8.1 component-library and symbol-asset provenance schemas already define:

```text
origin
license
author
created
sourceUri?       optional
sourceDigest?    optional
```

This is useful and should be preserved.

However:

- `.aixlib.json` provenance is attached to the library object, which may contain many component IDs;
- `.aixsym.json` provenance describes graphic-symbol origin, not necessarily the semantic truth of every component bound to that symbol;
- `sourceUri` is optional;
- the component object itself has no first-class per-ID provenance field;
- therefore a library containing multiple concrete devices cannot currently prove, from its normal component contract alone, which datasheet supports which component ID.

0.5.9 should close this at the **authoring-profile/validator level** without forcing a new core file-format version.

#### 4.2 Placeholder semantics are not strongly closed in the current component-graphics contract

The safe behavior for an Agent must be explicit:

```text
exact real part requested
    + authoritative source available
        -> datasheet-backed component

exact real part requested
    + authoritative source unavailable/uncertain
        -> placeholder
        -> no semantic-ready claim
```

The Agent must never invent a plausible pinout, obtain a clean render, and treat that as evidence that the real part is correct.

#### 4.3 Generic templates must not be confused with unsourced real parts

0.5.9 distinguishes:

```text
datasheet-backed
generic-template
placeholder
```

`generic-template` is valid only when the component intentionally represents a generic class and does not claim a specific real manufacturer part.

Examples include a generic resistor type, generic connector class, generic architectural symbol template, and conformance fixture.

It is not a loophole for an unsourced concrete part number.

#### 4.4 Geometry reuse is legitimate; geometry-only component-ID multiplication is not

AIXEM correctly separates component semantics from symbol graphics, so several components may share one `.aixsym.json`.

The missing rule is the inverse:

> Reusing or copying graphics does not justify minting new semantic component IDs.

Every component ID needs a semantic basis:

```text
identity
pin/terminal inventory
relevant property contract
provenance status
source identity or explicit placeholder/generic status
presentation binding
```

#### 4.5 Current symbol conformance proves structure/rendering, not datasheet truth

The existing symbol-expressiveness path proves schema validity, binding, geometry, production rendering, determinism, and visual readability.

It does not by itself prove:

- manufacturer datasheet use;
- pin-number/name correctness against that source;
- minimum real-part semantic completeness;
- suitability for an actual circuit role;
- absolute-maximum, thermal, safety, or regulatory correctness.

0.5.9 must state this claim boundary directly.

#### 4.6 Pinout/source correctness is a structured review gate

0.5.9 should not add a datasheet crawler, PDF parser, vendor catalog importer, or automatic electrical-design verifier.

The validator can mechanically enforce provenance completeness and review-evidence integrity. A human or explicitly identified Agent-assisted review records whether the component pinout and selected semantic properties agree with the cited source.

That is the appropriate pre-live boundary.

### 5. Baseline Review — Symbol Sizing and Grid-Proportional Dimensions

#### 5.1 Existing sizing rules are stronger than the task-facing guidance

The 0.5.8.1 Symbol Design Profile already establishes the correct foundation:

```text
G = 2.5 mm   active snap / body quantization unit
P = 5.0 mm   standard pin pitch = 2G
M = 10 mm    major grid = 4G
standard visible lead = 5.0 mm = 2G
```

It also states that body width and height should be quantized to the active grid and that, for a side containing `N` repeated pins, the body must reserve at least:

```text
(N - 1) × P
```

for pin-center span plus one total pin pitch of body padding in that axis.

For the reference profile this is equivalent to the practical minimum envelope:

```text
minimum repeated-pin body span
    = (N - 1) × P + P
    = N × P
```

before additional space is added for long pin names, internal function text, grouping separators, or other required presentation.

The problem is not the absence of a sizing concept. The problem is that an Agent creating a new library part must currently combine that rule from several documents.

#### 5.2 Sizing must remain proportional, not a fixed component catalog

0.5.9 MUST NOT prescribe one absolute width/height for every resistor, MCU, connector, architectural object, or future domain.

The generic authoring rule should instead be:

```text
determine required content
    -> determine required pin-group span
    -> add G/P-based padding and text channels
    -> quantize outward to G
    -> compare against the nearest validated corpus recipe
    -> enlarge when readability requires it
```

This preserves generality while producing visually consistent symbols.

#### 5.3 Recommended reference rhythm

For Grid Schematic Profile 1, the task-facing guide should expose the following rhythm:

```text
body edge coordinates               -> multiples of G
body width / height                  -> multiples of G
standard repeated pin pitch          -> P = 2G
standard visible lead                -> P = 2G
outermost repeated-pin center
to body end in the group axis        -> at least G preferred
ordinary internal text/body padding  -> at least G preferred
identity field separation            -> outside body; use >= G where measurable
repeated group envelope              -> at least (N - 1)P + 2G
```

The final rule above is the existing one-pitch total padding expressed as `G` on both ends under the reference profile.

These values are a **reference-profile construction rhythm**, not a new universal file-format constraint.

#### 5.4 Reference corpus remains the visual precedent

Class-specific dimensions should be learned from validated AIXEM corpus patterns rather than from a hard global size table.

For example, the current validated two-pin passive recipe uses grid-quantized proportions and the multi-pin recipes derive body height from pin count. 0.5.9 should expose these as **recommended starting patterns**, while the generic sizing contract remains formula-based.

---

### 6. Baseline Review — Task-Oriented Agent Guides

#### 6.1 Practical guides exist, but they are distributed

The current repository already has useful authoring material, including:

```text
docs/symbols/authoring-guide.md
docs/symbols/symbol-authoring-cookbook.md
docs/schematic/schematic-authoring-cookbook.md
docs/schematic/placement.md
docs/routing/routing-cookbook.md
docs/agent/schematic-authoring.md
docs/agent/symbol-generation.md
docs/agent/routing-agent.md
docs/agent/authoring-orchestration.md
docs/_meta/routes/*.yaml
docs/_meta/generated/task-packets/*.json
```

This is technically rich, but it represents several different document roles:

- normative contracts;
- domain guides;
- worked cookbooks;
- Agent operating policy;
- authored task routes;
- generated task packets.

There is no dedicated authored folder whose only purpose is:

> “I need to perform task X. Show me the shortest practical procedure and then point me to the exact canonical owners.”

#### 6.2 Generated task packets are not a replacement for authored guides

Task packets are excellent machine-readable execution maps, but they are generated navigation products. They are not the best place to explain:

- what the task means;
- how to choose the project/authoring root;
- where new files belong;
- the important default `G/P/M` values;
- what should be edited and what must remain derived;
- which common mistakes to avoid;
- what constitutes completion.

A concise authored task guide can explain those decisions and then link to the generated packet and normative references.

#### 6.3 `docs/authoring/` is the correct home

Do not create a new top-level documentation domain merely to host task guides.

Use the existing authoring domain:

```text
docs/authoring/
├── index.md
└── guides/
    ├── index.md
    ├── create-library-part.md
    ├── create-schematic.md
    ├── route-nets.md
    ├── compose-project.md
    ├── author-component-circuit.md
    ├── render-review.md
    └── validate-project.md
```

This keeps the documentation vocabulary stable and places “how to do work” beneath the existing authoring information architecture.

#### 6.4 Guide role is informative and bounded

Each task guide:

- is informative, not a new normative owner;
- names exactly one primary task route, except the composite guide;
- links to the canonical requirement owners rather than copying them;
- links to the authored route YAML and generated task packet;
- provides the expected input/output paths and authority boundary;
- provides only the most important defaults required to start;
- provides validation and stop conditions;
- remains small enough for immediate Agent retrieval.

Recommended size policy:

```text
target: 4–8 KiB authored Markdown
hard ceiling: 12 KiB per task guide
```

If a guide needs more detail, that detail belongs in the linked cookbook/reference/specification.


### 7. Design Principles

#### P1 — One canonical root for newly authored project libraries

For new reusable artifacts:

```text
<project-root>/library/
```

is the canonical storage root.

Use singular `library`, not competing `library/`, `libraries/`, `parts/`, or `symbols/` roots.

#### P2 — Only first-level domain taxonomy is controlled

0.5.9 defines exactly two first-level domains:

```text
electronics
architecture
```

`electronics` is the broad electrical/electronic schematic-part domain. It is not restricted to semiconductor electronics.

No second-level category list is standardized in 0.5.9.

#### P3 — Below the domain, govern naming rather than taxonomy

AIXEM should not have to update its core standard whenever a new industry or part category appears.

Below the first-level domain, the agent may create a semantically appropriate hierarchy, subject to generic naming/reuse rules.

#### P4 — Reuse an existing namespace before creating a synonym

Before adding a directory segment, inspect the existing domain subtree.

If an existing path accurately represents the requested category, reuse it.

Do not create parallel synonyms such as:

```text
passive/
passives/
passive-components/
```

inside the same library domain without an explicit migration/ownership reason.

#### P5 — Paths aid retrieval; IDs retain semantic identity

The path helps humans and agents find assets, but the stable IDs inside `.aixlib.json` and `.aixsym.json` remain semantic identity.

Moving a file does not silently redefine its component/symbol identity.

#### P6 — New placement rules must not invalidate repair of legacy content

0.5.9 may require canonical paths for **newly created** library artifacts while still allowing an agent to repair an existing referenced artifact at a historical path.

#### P7 — Grid legality and visual rhythm are separate

Hard grid validity remains machine enforced. Alignment rhythm remains advisory unless objectively measurable.

#### P8 — Placement assist is advisory only

The helper proposes legal coordinates. `.aixlayout.json` remains placement authority.

#### P9 — No silent movement or library mutation

Placement assist does not move neighboring components. Library guidance does not auto-reorganize existing trees during unrelated tasks.

#### P10 — No speculative universal taxonomy

Do not introduce manufacturer databases, ECLASS/ETIM mappings, BOM taxonomies, building classification standards, or a globally frozen component tree in 0.5.9.

---


#### P11 — Symbol size derives from grid rhythm and content, not arbitrary freehand dimensions

A new symbol should start from `G/P/M`, pin-group span, field channels, and a validated corpus pattern. Fixed per-part dimensions are guidance, not universal authority.

#### P12 — Task guides are execution façades, not authority

`docs/authoring/guides/` may summarize the shortest operational path, but every binding rule must still resolve to a canonical specification/contract/requirement.

#### P13 — One task guide should answer one immediate job

Do not create generic “everything about authoring” manuals in the guide layer. A guide is selected by task intent and should make the next authoritative read obvious.

#### P14 — Fast guidance must preserve route budgets

Task guides improve first-hop retrieval. They must not cause every route to load more documents than the existing `7 documents / 96 KiB / depth 3` budget.


#### P15 — Concrete part identity requires source provenance

A component that claims a specific real manufacturer/orderable part must cite the source that defines that identity and pinout. Missing or uncertain source truth must be explicit, never guessed.

#### P16 — Component identity is semantic, not geometric

Symbol geometry may be shared. A new component ID must not exist merely because geometry was copied or renamed.

#### P17 — Render PASS is a structural claim

Renderer success proves that declared structure can be resolved and drawn deterministically. It does not certify datasheet accuracy, minimum semantic completeness, or circuit suitability.

#### P18 — Semantic review evidence is bounded and source-linked

Pinout/source consistency and circuit-intent review must be recorded against exact component/library/source digests. 0.5.9 does not automate datasheet interpretation or electrical-safety engineering.

## PART I — GRID AND PLACEMENT HARDENING

### 8. Canonical Grid Vocabulary

Define consistently:

```text
G = active style profile grid.snap
P = active style profile symbol.pinPitch
M = active style profile grid.major
O = active style profile grid.origin
```

Reference profile:

```text
G = 2.5 mm
P = 5.0 mm = 2G
M = 10 mm  = 4G
O = [0, 0]
```

`G` is the minimum legal component-origin and free-route-bend quantum for the active reference schematic profile.

---


### 9. Grid-Proportional Symbol Sizing Rhythm

#### 9.1 Purpose

Make symbol size selection predictable for a fresh Agent without creating a universal part-size catalog or automatic symbol-layout solver.

The normative owner remains the existing Symbol Design Profile. The 0.5.9 work consolidates its rules into an immediately usable construction method and strengthens the cookbook/task-guide links.

#### 9.2 Reference quantities

For Grid Schematic Profile 1:

```text
G = 2.5 mm
P = 5.0 mm = 2G
M = 10 mm  = 4G
L = 5.0 mm = 2G  standard visible lead
```

#### 9.3 Body quantization

Body extents SHOULD resolve to `G` multiples.

When an intended content-derived dimension is not a legal multiple:

```text
bodyDimension = ceil-to-grid(requiredDimension, G)
```

Sizing always rounds outward. It must never shrink a pin/text requirement to fit a preferred nominal size.

#### 9.4 Repeated pin-group envelope

For `N >= 1` pins on one side with pitch `P`:

```text
pinCenterSpan = (N - 1) × P
minimumBodySpanInGroupAxis = pinCenterSpan + 2G
```

Under the reference profile `2G = P`, so:

```text
minimumBodySpanInGroupAxis = N × P
```

This gives `G` of preferred padding beyond the outermost repeated pin centers at both ends.

If pin names, numbers, grouping labels, or internal functional labels require more room, increase the body to the next legal `G` multiple.

#### 9.5 Two-pin and simple-symbol rhythm

Do not force all simple parts into one box.

For ordinary two-pin/passive-style construction:

- preserve standard lead length `L = 2G` when the recipe uses visible leads;
- keep body extents on `G`;
- start from the closest validated corpus recipe;
- preserve symmetry around the insertion origin where the symbol class is symmetric;
- enlarge rather than compress lead length, pin pitch, or field channels.

The current validated passive corpus may be documented as an example starting proportion, but its exact dimensions are not a universal MUST for every two-pin symbol.

#### 9.6 Connectors and high-pin-count blocks

For connectors and functional IC blocks:

- use `P` as repeated pin pitch;
- derive the group-axis body span using the formula above;
- use consistent group pitch on the same side;
- reserve additional `G`-quantized space for long labels and functional group breaks;
- do not reduce `P` merely to fit more pins;
- split into multi-unit presentation only when the existing multi-unit/component contract says that is the clearer representation.

#### 9.7 Text and field clearance

Sizing must account for text before graphics are considered complete.

Preferred construction guidance:

```text
internal body text padding        >= G where practical
identity field/body separation    >= G where practical
pin-name channel                  must remain readable and non-overlapping
reference/value fields            remain outside body under the existing profile
```

Where the existing normative field-layout contract is stricter, it wins.

#### 9.8 Size selection order

The task-facing algorithm is:

```text
1. select nearest validated symbol recipe
2. identify side pin groups and required labels
3. compute pin-center spans using P
4. add G-based end padding / text channels
5. choose body dimensions
6. quantize outward to G
7. place standard leads using L
8. render and inspect
9. enlarge only at G increments if clearance fails
```

#### 9.9 No automatic mutation

0.5.9 does not add an automatic symbol-size mutation tool.

The sizing rhythm is a deterministic authoring guide plus validation/corpus expectation. A future tool may be justified only by real Agent evidence.


### 10. Deterministic Snap Semantics

#### 10.1 Scalar snap

Define a language-independent operation:

```text
snap(v, O, G)
```

that returns the nearest legal coordinate relative to the declared origin.

Midpoint ties MUST use one explicit cross-tool rule. Recommended:

```text
round-half-away-from-zero
```

Do not inherit Python/JavaScript runtime-specific rounding behavior as an accidental contract.

#### 10.2 Point snap

```text
snapPoint(x, y) = [snap(x, Ox, G), snap(y, Oy, G)]
```

Finite input only. NaN/infinity/malformed values fail before a suggestion is produced.

#### 10.3 Idempotence

An already legal coordinate remains unchanged except for canonical number serialization.

---

### 11. Conservative Magnetic Alignment Assist

#### 11.1 Acquisition window

Use:

```text
alignmentWindow = G
```

No new profile field is needed.

#### 11.2 Candidate axes

After base quantization, inspect existing legal component origins on the same sheet.

Candidate alignment exists when:

```text
abs(existingX - snappedX) <= G
abs(existingY - snappedY) <= G
```

#### 11.3 Bounded candidate set

Generate at most:

```text
base snapped point
best X-aligned point
best Y-aligned point
best X+Y aligned point
```

Deduplicate equal coordinates.

#### 11.4 Deterministic ranking

Use stable ranking:

1. legal candidate;
2. X+Y alignment;
3. single-axis alignment;
4. base grid snap;
5. smallest displacement from base point;
6. smallest displacement from proposed point;
7. stable numeric `(x, y)` tie-break.

Input JSON ordering and filesystem enumeration must not affect the result.

#### 11.5 No topology inference

The helper does not infer that components sharing a net should move next to each other.

Functional layout remains an agent reasoning task guided by canonical documentation.

---

### 12. Placement Rhythm Guidance

#### Hard requirements (`MUST`)

- component origins are on `G`;
- route free bends are on `G`;
- placement coordinates are finite;
- placement closure is exact;
- under Grid Schematic Profile 1, serialized layout grid agrees with active-profile snap.

#### Preferred rules (`SHOULD`)

- related components share legal rows/columns where this improves readability;
- repeated stages preserve comparable row/column rhythm;
- ordinary spacing uses multiples of `P` or `M` when practical;
- one `P` (5 mm) channel is preserved between unrelated symbol bodies and adjacent routing where practical;
- normal signal flow proceeds left-to-right;
- whitespace is preferred before shrinking useful symbols/text.

Do not make subjective composition quality a blocking validator.

---

### 13. Close Grid Authority Precedence

Amend the existing canonical owners so all say the same thing:

```text
styleProfile.grid.snap
    -> active schematic snap authority

layout.coordinateSystem.grid
    -> serialized declaration; MUST agree under Grid Schematic Profile 1

symbol coordinate-system grid
    -> symbol-local authoring metadata only
```

Validate reference-profile coherence:

```text
layout.grid == profile.grid.snap
profile.grid.minor == profile.grid.snap
profile.grid.major / profile.grid.snap is integral
profile.symbol.pinPitch / profile.grid.snap is integral
```

Add stable diagnostic:

```text
AIXEM-DIAG-LAYOUT-GRID-PROFILE-MISMATCH
```

---

### 14. Repair Agent Route Visibility for Placement/Routing

#### `create-schematic`

Keep the existing seven-document budget. Directly include the canonical Component Placement owner.

Recommended packet:

```text
1 Authority Model
2 Schematic Authoring Cookbook
3 Grid and Snap System
4 Component Placement
5 Component/Symbol Binding
6 .aixem format
7 .aixlayout format
```

#### `route-nets`

Directly expose hard geometry owners:

```text
1 Net Model
2 Semantic Net Routing
3 Routing Cookbook
4 Grid and Snap System
5 Route Constraints
6 Crossings and Junctions
7 .aixlayout format
```

Preserve:

```text
max documents <= 7
max bytes <= 96 KiB
max dependency depth <= 3
```

---

### 15. Minimal Placement-Assist Tool

Recommended implementation:

```text
implementation/schematic/placement_assist.py
tools/placement_assist.py
```

Initial command only:

```text
suggest
```

Structured output must include:

```text
input coordinate
active profile
G / P / M / origin
base snapped coordinate
selected coordinate
alignment type: none | x | y | xy
alignment references
candidate count
warnings
mutated = false
authority = derived-advisory-only
```

The tool MUST NOT:

- write `.aixlayout.json`;
- move neighboring placements;
- edit `.aixem`;
- modify net routing;
- update project/library/symbol authority.

---

## PART II — CANONICAL PROJECT LIBRARY STRUCTURE

### 16. Define the Project Library Root

#### 16.1 Authoring root and project-root relationship

For this contract, **authoring root** is the root directory assigned to the Agent for durable authored project assets.

In the AIXEM reference-platform repository, the authoring root is the repository root. In a standalone user schematic project, it is normally that project's root. In a cold-start evaluation stage, it is the staged workspace root or the explicitly selected project root inside that workspace.

The existing `.aixproj.json` security model remains unchanged: manifest references are resolved relative to the owning project root and may not escape via `..`. A nested self-contained example project therefore cannot reach upward into a repository-level library by path escape; it either owns its own local `library/` subtree or participates in an explicit packaging/materialization workflow.

This distinction prevents two opposite mistakes:

```text
ordinary repository-level request: "create a reusable library part"
    -> <repository-root>/library/...

explicit task: "modify this self-contained example project"
    -> <example-project-root>/library/...
```

The Agent MUST resolve the active authoring/project root before choosing a destination. It must not select `examples/` merely because examples were read as references.

#### 16.2 Canonical root for new reusable artifacts

Every newly created reusable component library or symbol asset intended to belong to the active authoring project MUST live below:

```text
<authoring-root>/library/
```

For a manifest-owned standalone project, this normally equals:

```text
<project-root>/library/
```

The canonical root is singular:

```text
library/
```

Do not create new competing roots such as:

```text
libraries/
parts/
components/
symbols/
example-parts/
```

for newly authored reusable content.

#### 16.3 Examples are not the default library root

An Agent MUST NOT create reusable project library content beneath:

```text
examples/
validation/
render/
evidence/
docs/
```

unless the active task explicitly owns authoring of that fixture/documentation area.

A symbol/library task operating on an ordinary project should therefore never decide that `examples/parts/` is an acceptable production library destination merely because examples are available as references.

---

### 17. First-Level Library Domain Contract

0.5.9 defines only two canonical first-level domains:

```text
library/electronics/
library/architecture/
```

#### `electronics`

Broad electrical/electronic schematic parts, including but not limited to:

- passive electrical components;
- semiconductor/electronic devices;
- power devices;
- electromechanical devices;
- connectors;
- ICs/controllers;
- protection and measurement devices.

This list is explanatory only. It does not create second-level folders by specification.

#### `architecture`

Building/architectural drawing components and symbols that belong to the architectural domain rather than the electronic circuit-part domain.

This first-level folder is an **organizational namespace only** in 0.5.9. Its existence does not claim IFC/BIM semantics, architectural-rule conformance, building-code intelligence, or full CAD behavior that AIXEM has not independently specified and tested.

Again, 0.5.9 does not standardize lower categories such as `door`, `window`, `fire-safety`, or `electrical-plan`.

#### Closed first-level vocabulary

New first-level directories are invalid for new authoring in 0.5.9 unless the canonical domain vocabulary is deliberately extended in a future governance change.

Examples of invalid first-level roots for new parts:

```text
library/common/
library/misc/
library/mechanical/
library/parts/
library/custom/
```

This is intentionally strict only at level 1.

---

### 18. Generic Namespace Rules Below the Domain

AIXEM must remain extensible below `electronics/` and `architecture/`.

#### 18.1 Directory segment syntax

Every semantic namespace segment below the domain MUST use lower-kebab-case:

```regex
^[a-z0-9]+(?:-[a-z0-9]+)*$
```

Examples:

```text
passive
resistor
power-management
microcontroller
board-connector
fire-safety
single-leaf-door
```

Disallowed:

```text
Passive
passive_parts
passive parts
01-passive
final
new-folder
```

Numeric tokens are allowed when they are genuine identity, not ordering prefixes.

#### 18.2 Namespace semantics

Each directory segment SHOULD describe a stable semantic grouping, not a transient workflow state.

Prefer:

```text
library/electronics/passive/resistor/
```

over:

```text
library/electronics/parts/new/final/resistors/
```

#### 18.3 Reuse-before-create rule

Before creating a new namespace segment, the Agent MUST inspect the existing selected domain subtree.

Decision order:

```text
exact existing semantic namespace
    -> reuse
near-equivalent existing namespace
    -> reuse the established vocabulary
no accurate namespace
    -> create the minimum new lower-kebab segment(s)
```

This prevents taxonomy drift without requiring a universal controlled taxonomy.

#### 18.4 Minimal necessary depth

There is no fixed second-level taxonomy and no hard universal maximum depth in 0.5.9.

However the Agent SHOULD use the shallowest hierarchy that keeps identity clear. A path should not encode every metadata property.

Avoid directory levels for mutable attributes such as:

```text
voltage rating
color
stock status
project instance reference
placement orientation
render variant
```

unless the attribute is genuinely part of the reusable library's semantic identity.

#### 18.5 Manufacturer/product namespaces

Manufacturer or product-family segments MAY appear below the domain when they are necessary to identify a reusable family.

Example:

```text
library/electronics/integrated-circuit/microcontroller/stm32/
```

AIXEM does not require manufacturer segmentation for generic parts.

#### 18.6 No generic catch-all namespace as a substitute for classification

New content SHOULD NOT be placed in generic buckets such as:

```text
misc
other
temp
new
parts
components
unknown
```

when a meaningful semantic namespace can be identified.

---

### 19. Library and Symbol File Naming

#### 19.1 General filename syntax

New `.aixlib.json` and `.aixsym.json` filenames MUST use lower-kebab-case before the required compound extension.

```regex
^[a-z0-9]+(?:-[a-z0-9]+)*\.aixlib\.json$
^[a-z0-9]+(?:-[a-z0-9]+)*\.aixsym\.json$
```

#### 19.2 Library filename rule

A `.aixlib.json` filename identifies the reusable **collection/scope** it contains.

Good:

```text
resistors.aixlib.json
power-connectors.aixlib.json
stm32.aixlib.json
door-symbols.aixlib.json
```

Avoid context-free names:

```text
library.aixlib.json
parts.aixlib.json
components.aixlib.json
new.aixlib.json
final.aixlib.json
```

#### 19.3 Symbol filename rule

A `.aixsym.json` filename identifies the reusable graphic/presentation identity, not a project instance reference.

Good:

```text
resistor-iec.aixsym.json
resistor-ansi.aixsym.json
stm32f4-100pin.aixsym.json
single-leaf-door.aixsym.json
```

Avoid:

```text
r1.aixsym.json
u3.aixsym.json
part1.aixsym.json
symbol-final.aixsym.json
```

`R1`, `U3`, etc. are schematic instance references, not reusable library identity.

#### 19.4 Co-location principle

A library file and the symbol assets primarily owned by the same semantic namespace SHOULD be colocated under that semantic namespace when practical.

Example:

```text
library/electronics/passive/resistor/
├── resistors.aixlib.json
├── resistor-iec.aixsym.json
└── resistor-ansi.aixsym.json
```

This deliberately avoids requiring parallel global `libraries/` and `symbols/` trees.

AIXEM still permits a library to reference a different safe project-relative asset path when genuine reuse requires it.

#### 19.5 Identity remains inside the file

Filename/path MUST NOT replace:

- component ID;
- library ID/version;
- symbol ID/revision;
- digest lock.

The existing internal identity/digest contract remains authoritative.

---

### 20. Project Manifest and Asset Path Rules

#### 20.1 Project references remain project-root relative

Keep the current safe-path model.

For newly authored canonical library content, `project.libraries[].path` should resolve to:

```text
library/electronics/**/<name>.aixlib.json
```

or:

```text
library/architecture/**/<name>.aixlib.json
```

#### 20.2 Symbol presentation paths

A `.aixlib.json` presentation `asset.path` remains safe and project-root relative under the current implementation model.

New canonical assets should therefore resolve inside the same `library/<domain>/...` tree.

Example:

```json
{
  "path": "library/electronics/passive/resistor/resistor-iec.aixsym.json"
}
```

#### 20.3 Digest locking unchanged

Moving/creating the artifact still requires the existing digest-lock workflow and any required `.aixproj.json` digest-only update.

No new identity registry is introduced.

---

### 21. New-vs-Existing Artifact Authoring Semantics

This distinction is necessary to preserve compatibility.

#### 21.1 New artifact mode

When the task creates a new reusable library or symbol artifact:

```text
new .aixlib.json -> MUST be below library/<allowed-domain>/...
new .aixsym.json -> MUST be below library/<allowed-domain>/...
```

#### 21.2 Existing artifact repair mode

When a task edits an artifact already referenced by the project/task at a historical safe path:

```text
libraries/authoring.aixlib.json
symbols/resistor.aixsym.json
```

AIXEM MAY allow in-place repair without forcing an unrelated migration.

This prevents 0.5.9 from converting every bug fix into a directory-migration operation.

#### 21.3 Explicit migration task

Moving existing legacy library content into the canonical 0.5.9 tree is a deliberate migration action. It must update:

- project library paths;
- symbol asset paths;
- digests;
- task/evidence references when relevant;
- generated fixtures if the source is generator-owned.

No silent automatic moves.

---

### 22. Component-Level Part Provenance Profile

#### 22.1 Preserve existing file-level provenance

Existing provenance keeps its current meaning:

```text
library.provenance
    -> authorship/license/origin of the library artifact

symbol.provenance
    -> authorship/license/origin of the graphic symbol artifact
```

Neither one alone proves per-component datasheet truth when a library contains multiple component IDs.

#### 22.2 Use a component-level profile without a core schema-version bump

The current component object already permits a free-form `metadata` object. 0.5.9 uses it for a bounded authoring profile:

```json
{
  "metadata": {
    "partProvenance": {
      "status": "datasheet-backed",
      "manufacturer": "Example Semiconductor",
      "partNumber": "ABC1234",
      "sourceKind": "manufacturer-datasheet",
      "sourceUri": "https://vendor.example/datasheets/abc1234.pdf",
      "sourceDigest": "sha256:..."
    }
  }
}
```

The 0.5.9 validator and authoring contract make this structure normative for new part authoring.

This preserves backward compatibility and avoids a new `.aixlib` schema URI/version solely for provenance discipline.

#### 22.3 Provenance status vocabulary

Use exactly:

```text
datasheet-backed
generic-template
placeholder
```

##### `datasheet-backed`

Use when the component claims a specific real-world product identity.

Required:

```text
manufacturer
partNumber or stable product identifier
sourceKind = manufacturer-datasheet
sourceUri
```

`sourceDigest` SHOULD be recorded when the exact reviewed source is available as a stable captured artifact.

Prefer the manufacturer's official datasheet over reseller/community sources when an official primary source exists.

##### `generic-template`

Use only for intentionally generic semantic classes.

Rules:

- do not claim an exact manufacturer part number;
- make generic/template intent clear;
- still provide complete ports, properties, and presentation binding.

##### `placeholder`

Use when a specific concrete part is requested or tentatively identified but source truth is missing, incomplete, or uncertain.

Required:

```text
status = placeholder
placeholderReason
```

A placeholder can be retained only with truthful incomplete status and cannot receive semantic-ready approval until resolved.

#### 22.4 `sourceUri` does not imply live-network validation

`sourceUri` identifies the authority reviewed for the concrete part.

Normal validation checks URI syntax and evidence binding; it does not require fetching the URI on every build.

This keeps builds reproducible and avoids coupling authoring to network availability.

---

### 23. Semantic Component Contract and Bulk-Generation Discipline

#### 23.1 Semantics precede graphics

Recommended authoring order:

```text
classify provenance status
    -> establish component identity
    -> establish pin/terminal inventory
    -> establish minimum semantic properties
    -> select/reuse/create presentation symbol
    -> bind semantic ports to symbol ports
    -> render
    -> semantic review
```

Do not begin by copying geometry and then invent semantic IDs around it.

#### 23.2 Required semantic contract per component ID

Every component ID must have at minimum:

```text
stable component id
displayName
kind
functional description
complete declared port/terminal inventory
property declarations required to distinguish/use the component
partProvenance status
presentation binding with total required portMap
```

For a datasheet-backed concrete part, additionally require:

```text
manufacturer
partNumber or stable product identifier
sourceUri
pinout/source review evidence
```

0.5.9 does not invent one universal detailed property catalog across electronics and architecture.

#### 23.3 Geometry reuse is allowed; geometry cloning as semantic generation is not

Legitimate:

```text
component A ─┐
component B ─┼──> same locked symbol asset digest
component C ─┘
```

when each component has its own valid semantic contract.

Prohibited:

```text
copy geometry
-> change only ID/displayName
-> emit many "parts"
-> no distinct pinout/property/source basis
```

#### 23.4 Family datasheets and shared sources

One manufacturer datasheet may legitimately define several part numbers.

Multiple component IDs may cite the same `sourceUri`, but each must declare its exact product identity and any pin/property differences.

A shared source is not permission for ID-only cloning.

#### 23.5 Derived semantic signatures

The validator should derive:

```text
portSignature
propertySignature
provenanceSignature
presentationSignature
```

These help detect suspicious new batches but are not new component identity.

A batch is suspicious when new IDs differ only by ID/display text while semantic/provenance signatures provide no legitimate distinction.

#### 23.6 No catalog ingestion

0.5.9 does not add manufacturer APIs, datasheet crawling, automatic PDF extraction, web part search, BOM enrichment, or PLM/ERP integration.

---

### 24. Validation Claim Layers for Library Parts

#### 24.1 Structural PASS

Structural validation includes:

```text
JSON/schema validity
component-port uniqueness
presentation binding validity
portMap closure
symbol lint
grid/geometry validity
deterministic renderer success
render digest stability
```

Required claim wording:

> Structural/render PASS confirms that the authored component-symbol structure is valid and deterministically renderable. It does not independently verify datasheet truth or circuit suitability.

#### 24.2 Part Semantic Review PASS

A datasheet-backed concrete part may receive semantic-review PASS only when all applicable checks are recorded:

```text
concrete identity matches cited source
manufacturer / part number present
sourceUri present
pin numbers/terminal identities checked against source
pin names/functions checked against source
electrical/functional pin types reviewed
minimum semantic properties reviewed for intended library use
component -> symbol portMap reviewed
placeholder status is false
no unresolved provenance defect remains
```

Review evidence binds:

```text
component ID
library digest
symbol digest(s)
sourceUri
sourceDigest when available
review timestamp
reviewer mode/identity
result
```

#### 24.3 Minimum property review

Use a small universal base:

- sufficient identity to know what the component claims to be;
- non-empty functional description;
- variant-distinguishing properties represented where applicable;
- task-required/design-selection properties not silently omitted;
- existing unit/enum property rules preserved.

Domain-specific detailed completeness remains profile-specific rather than becoming one giant universal list.

#### 24.4 Circuit Intent Review

When a component is used in an actual schematic/project, review at minimum:

```text
Does the component serve the requested functional role?
Are the intended signal/power/control pins the ones connected?
Are required pins accounted for?
Are deliberate no-connects intentional and explicit?
Are task-relevant component properties present and plausible relative to the source/task?
Does the selected presentation preserve endpoint identity?
```

This is a design-review requirement, not proof of absolute-maximum, thermal, regulatory, or electrical-safety correctness.

#### 24.5 Placeholder outcome

A placeholder may structurally render but must be reported distinctly:

```text
structuralPass = true
partSemanticReview = PLACEHOLDER
semanticReady = false
```

#### 24.6 Review evidence remains derived

Review records live in validation/cold-start state evidence. They do not become component authority and must not be hand-edited to redefine source truth.

### 25. Agent Route and Write-Scope Hardening for Library Creation

#### 25.1 `create-symbol` route must expose location rules

The route should directly stage a canonical library-structure owner or a concise canonical section of an existing authoring owner.

The agent must learn, within its normal task packet:

```text
new reusable artifact? -> project-root/library/<domain>/...
existing referenced artifact? -> repair in place unless migration requested
example fixture task? -> only then write inside examples/fixture-owned path
```

Do not make the Agent search the whole repository for this distinction.

#### 25.2 New-artifact path policy

Extend route/change-scope validation so a new `.aixlib.json` or `.aixsym.json` produced by ordinary `create-symbol` work is valid only below:

```text
library/electronics/**
library/architecture/**
```

#### 25.3 Existing-file exception

If a file already existed in the baseline Change-Set and is explicitly within route authority, it may be modified at its existing safe path.

The validator must distinguish `added` from `modified`, which Change-Set already records.

#### 25.4 Project digest-only rule preserved

`*.aixproj.json` remains writable only under the existing digest/path-reference constraints required by the route.

#### 25.5 Examples protection

For ordinary symbol/library authoring, newly added paths below `examples/**` are prohibited.

Example-generation tests/builders may use their own dedicated build path and are not governed as a live project authoring destination.

---

### 26. Canonical Documentation Changes

Prefer extending existing owners rather than creating many documents.

#### Required updates

- `.aixlib.json Component Library` — clarify file-level provenance vs component semantic provenance; define the 0.5.9 `metadata.partProvenance` profile and placeholder/semantic-ready claim boundary;
- `.aixsym.json Symbol Asset` — clarify that symbol provenance describes graphic-asset origin and does not by itself prove bound-component datasheet truth;
- `Symbol Design Profile` — consolidate grid-proportional sizing terminology, repeated-pin envelope formula, outward `G` quantization, and text-clearance expansion rules;
- `Symbol Authoring Guide` — expose the sizing decision sequence and link it from the library-part task guide;
- `Symbol Authoring Cookbook` — reference the common `G/P/M` rhythm and state that geometry reuse does not create semantic component identity;
- `Symbol Lint` — state the structural-only claim boundary and mechanical provenance/semantic diagnostics;
- `Symbol Expressiveness Conformance` — state that S-Core/S-Extended render PASS proves graphical/structural expressiveness, not manufacturer pinout/datasheet correctness;
- `Conformance Validation` — add part semantic review and circuit-intent review as distinct layers from renderer validity;
- `Component Model` — explain reusable identity is not derived from path;
- `Component to Symbol Binding` — update examples to canonical project-root-relative asset paths;
- `Symbol Authoring Guide` — add location/namespace/filename decision flow;
- `Authoring Orchestration` — distinguish new artifact creation from existing artifact repair;
- `Project Composition Contract` — document canonical new-authoring library paths while preserving safe legacy references;
- `Component Placement`, grid owners, layout format, route docs — absorb the grid/snap changes from the former 0.5.8.2 plan.

#### One canonical library-layout owner

If no current document cleanly owns directory placement/naming, add exactly one normative owner, recommended:

```text
docs/specifications/components/library-layout-contract.md
```

Suggested ID:

```text
AIXEM-SPEC-LIBRARY-LAYOUT-001
```

It should own only:

- project library root;
- first-level domain vocabulary;
- lower-level naming/reuse rules;
- file naming;
- new-vs-existing authoring semantics;
- component provenance-status policy for newly authored parts;
- concrete real-part source-or-placeholder rule;
- geometry reuse vs semantic-ID generation boundary;
- prohibited destinations;
- path/provenance conformance.

Do not turn it into another `.aixlib` content specification.

#### AGENTS.md

Keep `AGENTS.md` short. Add only a routing-level rule such as:

```text
New reusable component/symbol artifacts belong under project-root/library/<domain>/.
Use REFERENCE.md/task routes for the canonical library-layout and naming contract.
Do not create reusable project parts under examples/ unless the task explicitly owns an example fixture.
```

Detailed taxonomy/naming examples belong in the canonical contract/guide, not AGENTS.md.

#### Root REFERENCE.md and library entrypoint

Add a category pointer for:

```text
component/symbol library authoring
    -> library/README.md
    -> create-symbol route
    -> library layout contract
    -> .aixlib / .aixsym contracts
```

Add a concise non-normative `library/README.md` at the authoring/repository root library. It is a navigation entrypoint, not a second specification. It should state only:

- this tree contains reusable authored library assets;
- first-level domains are `electronics` and `architecture`;
- detailed naming/path authority is owned by the canonical library-layout contract;
- examples/validation fixtures are not the default reusable-library destination.

Detailed naming rules must stay in canonical docs so `library/README.md` cannot drift into a competing authority.

This preserves the 0.5.8.1 root chaining requirement while making the desired output location obvious to both humans and Agents.

---


## PART III — TASK-ORIENTED AGENT GUIDE LAYER

### 27. Create the Task Guide Directory

Add:

```text
docs/authoring/guides/
├── index.md
├── create-library-part.md
├── create-schematic.md
├── route-nets.md
├── compose-project.md
├── author-component-circuit.md
├── render-review.md
└── validate-project.md
```

Do not create a new documentation domain. These files use the existing `authoring` domain and `guide`/`index` kinds.

The guide index must be directly reachable from:

```text
AGENTS.md
REFERENCE.md
docs/authoring/index.md
```

`AGENTS.md` should contain only a compact pointer such as:

```text
For common authoring operations, start at docs/authoring/guides/index.md,
then follow the selected task route and canonical references.
```

### 28. Standard Task-Guide Template

Every guide must use the same compact structure:

```text
1. Task
2. Use this guide when / do not use it when
3. Primary route ID
4. Authored route + generated task packet
5. Required inputs
6. Authority allowed to change
7. Canonical output location
8. Important default profile values
9. Short execution sequence
10. Canonical reference table
11. Validators / tools
12. Completion criteria
13. Stop / fail-closed conditions
14. Common mistakes
15. Evidence / outputs
```

#### 28.1 Reference table format

Each guide should include an explicit table:

```text
Document
Stable ID
Why this task needs it
Normative / informative
Required section or requirement IDs
```

This lets an Agent load only the next required owner.

#### 28.2 Normative duplication prohibition

A task guide must not silently become a second specification.

If it uses binding words such as MUST/SHALL, the statement must either:

- be a direct concise restatement with linked requirement ID; or
- be replaced by non-normative wording such as “the canonical contract requires...”.

Automated documentation audit should detect guide-local normative requirement IDs or orphan authority scopes.

#### 28.3 Guide size budget

```text
preferred authored size: 4–8 KiB
hard maximum: 12 KiB
```

The goal is immediate orientation, not exhaustive explanation.

---

### 29. `create-library-part.md`

This is the first document an Agent should use for a request such as:

```text
create a resistor library part
make a new MCU symbol
add a reusable door symbol
create a reusable component and symbol
```

It must state early:

```text
new reusable asset root
    = <project-root>/library/<domain>/...

first-level domain
    = electronics | architecture
```

It must explain the normal artifact relationship:

```text
.aixlib.json
    -> reusable semantic/component definitions and presentation bindings

.aixsym.json
    -> reusable graphic symbol asset(s)
```

and that one reusable part may therefore involve more than one JSON file.

Required quick decisions:

1. determine the active project/authoring root;
2. classify the requested part as `datasheet-backed`, `generic-template`, or `placeholder`;
3. for a specific real part, resolve `manufacturer`, `partNumber`, and `sourceUri` before inventing pins or geometry;
4. classify only the first-level library domain;
5. reuse an existing lower namespace when semantically appropriate;
6. select lower-kebab path and filenames;
7. author the component semantic contract first: identity, pin/terminal inventory, minimum properties, and provenance;
8. select/reuse/create the required `.aixsym.json` asset(s);
9. apply `G/P/M` sizing rhythm;
10. bind ports/fields/presentation and lock asset digests;
11. run structural/schema/binding/render validation;
12. run part semantic review; if placed in a circuit, run circuit-intent review;
13. close with explicit structural/semantic/placeholder status.

The guide must contain two prominent rules:

> `render PASS` is a structural result. It is not proof that a concrete part number, datasheet pinout, or intended circuit use is correct.

> Reuse a symbol asset when appropriate; never create additional component IDs merely by copying geometry. Every component ID needs its own semantic pin/property/provenance contract.

Direct references must include at minimum:

- Library Layout Contract;
- `.aixlib.json` component provenance/semantic contract;
- Part Semantic Review / conformance guidance;
- Symbol Design Profile;
- Symbol Authoring Cookbook;
- `.aixlib.json` reference;
- `.aixsym.json` reference;
- Component-to-Symbol Binding;
- Symbol Lint;
- `create-symbol` route/task packet.

---

### 30. `create-schematic.md`

This guide must make the authority split obvious:

```text
.aixem            semantic entities/nets
.aixlayout.json   placements and routing geometry
.aixproj.json     project composition/digest references
```

It must expose:

```text
G = 2.5 mm
P = 5.0 mm
M = 10 mm
```

for the reference profile and link directly to Component Placement and the placement-assist command.

Short workflow:

```text
resolve component/library references
-> author semantic entities/nets
-> create placements
-> use deterministic snap/alignment suggestion when useful
-> check placement closure
-> hand off to route-nets
```

Do not duplicate routing recipes in this guide.

---

### 31. `route-nets.md`

The guide must provide the shortest route from closed semantic nets to legal route geometry:

```text
semantic net membership
-> endpoint resolution
-> G-aligned orthogonal path
-> explicit junctions
-> crossing clarity
-> route closure
-> deterministic render
```

Direct references include:

- Net Model;
- Grid and Snap System;
- Route Constraints;
- Routing Cookbook;
- Crossings and Junctions;
- `.aixlayout.json`;
- `route-nets` task packet.

---

### 32. `compose-project.md`

The guide should cover only project composition:

```text
sheet/project registration
interface ports
project nets
hierarchical references
digest/path closure
```

It must explicitly distinguish project-net semantics from derived Overview/Composite routing.

Direct references include the Project Composition Contract and `compose-project` route.

---

### 33. `author-component-circuit.md`

This is the end-to-end guide for a request that combines part creation and circuit authoring.

It should not repeat every child guide.

Instead it presents the stable chain:

```text
create-library-part
-> create-schematic
-> route-nets
-> render-review
-> validate-project
```

and links to each child guide plus the `author-component-circuit` composite route/task packet.

---

### 34. `render-review.md`

Keep this guide read-only in authority terms.

State near the top:

```text
render PASS
    = structural / geometry / binding / deterministic-render success
    != datasheet correctness
    != pinout/source verification
    != minimum semantic property completeness
    != circuit-intent approval
```

It explains:

```text
authoritative source
-> deterministic renderer
-> resolved scene
-> SVG
-> Reference Viewer / Review Workbench
-> visual QA
```

and clearly states that derived render/Viewer files are never repaired directly.

---

### 35. `validate-project.md`

For projects using newly authored library parts, distinguish:

```text
structural validation
part semantic review
circuit intent review
placeholder status
```

A project summary must not collapse these into one undifferentiated `render PASS`.

This guide is the compact closure path:

```text
narrow validator
-> route/change-scope checks
-> deterministic regeneration
-> conformance suites
-> evidence
-> close
```

It must link to diagnostics, conformance, and run-record/evidence owners without embedding their complete schemas.

---

### 36. Root and Local Chaining

The final retrieval chain must be explicit and machine-tested:

```text
AGENTS.md
    -> docs/authoring/guides/index.md

REFERENCE.md
    -> docs/authoring/guides/index.md
    -> library/README.md

docs/authoring/guides/index.md
    -> each task guide

task guide
    -> authored route YAML
    -> generated task packet
    -> canonical owners

library/README.md
    -> create-library-part guide
    -> Library Layout Contract
```

An Agent asked to create a library part must be able to reach the output-path rule and sizing rule without searching the whole repository.

---

## PART IV — VALIDATION, MIGRATION, AND RELEASE CLOSURE


### 37. Example and Generator Migration Strategy

The current official authoring examples teach `libraries/` + `symbols/`. Leaving all agent-visible examples unchanged would undermine the new rule.

#### P0 migration

Migrate **agent-visible current authoring examples** and their owning generators to the canonical structure.

Example target:

```text
examples/authoring/01-two-pin-passive/
└── library/
    └── electronics/
        └── passive/
            └── resistor/
                ├── resistors.aixlib.json
                └── resistor.aixsym.json
```

The exact lower taxonomy is illustrative and may be kept simpler where appropriate. The important conformance is:

```text
library/electronics/... or library/architecture/...
```

#### Generated-fixture rule

Never hand-move generator-owned fixtures. Update the generator input/logic and regenerate.

#### Historical/evaluator fixtures

Do not mass-migrate every historical validation fixture merely for aesthetics.

Classify fixtures into:

1. **agent-visible current precedent** — migrate;
2. **current new-authoring conformance fixture** — migrate/add canonical fixture;
3. **historical compatibility fixture** — retain legacy path intentionally;
4. **generated renderer/corpus result** — regenerate only if its owner changes.

This preserves compatibility evidence while ensuring an agent's normal examples teach the new structure.

---

### 38. Diagnostics and Validation

Add a small, stable diagnostic set.

Recommended:

```text
AIXEM-DIAG-LIBRARY-PATH-NONCANONICAL
AIXEM-DIAG-LIBRARY-DOMAIN-UNKNOWN
AIXEM-DIAG-LIBRARY-NAME-INVALID
AIXEM-DIAG-LAYOUT-GRID-PROFILE-MISMATCH
```

#### `LIBRARY-PATH-NONCANONICAL`

Use when a **new** library/symbol artifact is created outside canonical `library/<domain>/...` during ordinary authoring.

#### `LIBRARY-DOMAIN-UNKNOWN`

Use when the first-level domain is not one of:

```text
electronics
architecture
```

#### `LIBRARY-NAME-INVALID`

Use for invalid path segment or filename syntax.

#### `LIBRARY-PART-SOURCE-REQUIRED`

A specific concrete real-world part has no valid `sourceUri`.

#### `LIBRARY-PART-PLACEHOLDER-UNDECLARED`

Concrete identity is unsupported by source evidence and has not been explicitly marked placeholder.

#### `LIBRARY-PART-PROVENANCE-INVALID`

Examples:

```text
status=datasheet-backed but manufacturer/partNumber/sourceUri missing
status=placeholder but placeholderReason missing
status=generic-template but exact manufacturer part identity is claimed
```

#### `LIBRARY-COMPONENT-SEMANTIC-CLONE`

A newly generated batch differs only by ID/display text or duplicated geometry without distinct semantic pin/property/provenance justification.

Do not trigger merely because legitimate components share the same symbol asset.

#### `LIBRARY-PART-MINIMUM-ATTRIBUTES-MISSING`

The component lacks the minimum semantic contract required by its provenance class.

#### `LIBRARY-PART-PINOUT-REVIEW-MISSING`

A datasheet-backed component is about to receive semantic-ready status without source-bound pinout review evidence.

#### `LIBRARY-PART-INTENT-REVIEW-INCOMPLETE`

A workflow claims circuit-intent review completion without the required exact component/source/digest-bound review items.

#### Claim-separation rule

No report may convert `render PASS` into `datasheet verified`, `semantic-ready`, or `circuit intent approved` without the corresponding evidence.

#### Compatibility behavior

Existing baseline artifacts at historical safe paths do not fail only because their path predates 0.5.9.

Validation must know whether a path is `added` versus `modified` when enforcing the new-location rule.

---

### 39. Focused Library Fixtures

Do not build a giant parts taxonomy corpus.

Add a small path/naming fixture set.

#### LBY001 — New electronics library valid

```text
library/electronics/passive/resistor/resistors.aixlib.json
library/electronics/passive/resistor/resistor-iec.aixsym.json
```

PASS.

#### LBY002 — New architecture library valid

```text
library/architecture/opening/door/door-symbols.aixlib.json
library/architecture/opening/door/single-leaf-door.aixsym.json
```

PASS.

The lower categories are fixture examples, not globally reserved taxonomy.

#### LBY003 — Unknown first-level domain

```text
library/mechanical/...
```

FAIL with domain diagnostic.

#### LBY004 — Arbitrary examples location

```text
examples/parts/resistor.aixsym.json
```

created by ordinary `create-symbol` task -> FAIL.

#### LBY005 — Legacy existing artifact repair

Existing baseline:

```text
libraries/authoring.aixlib.json
symbols/resistor.aixsym.json
```

modify in place under an explicit repair task -> PASS.

#### LBY006 — New legacy-style root

Newly add:

```text
libraries/new-part.aixlib.json
```

under ordinary authoring -> FAIL.

#### LBY007 — Naming syntax

```text
library/electronics/Power Parts/New_Resistor.aixsym.json
```

FAIL.

#### LBY008 — Reuse existing namespace

Given existing:

```text
library/electronics/passive/resistor/
```

a deterministic namespace-selection fixture must not create sibling `passive-components/resistors/` for the same test intent.

This can be a policy/tooling test rather than a full semantic AI classification test.

---

### 40. Focused Part Provenance and Semantic-Integrity Fixtures

Keep this set compact; it proves policy boundaries, not catalog coverage.

#### PRT001 — Datasheet-backed concrete part

Concrete component includes `manufacturer`, `partNumber`, `sourceUri`, complete pin/terminal inventory, minimum semantic attributes, and source-bound pinout review.

PASS.

#### PRT002 — Concrete part without source

Exact manufacturer part number, no `sourceUri`, not placeholder.

FAIL with `LIBRARY-PART-SOURCE-REQUIRED`.

#### PRT003 — Explicit placeholder

Exact requested part cannot be sourced reliably.

```text
status = placeholder
placeholderReason = ...
```

Structural render may PASS, but `semanticReady=false`.

#### PRT004 — Generic template

Generic resistor/connector/architectural template claims no specific manufacturer part and has a complete internal semantic contract.

PASS as `generic-template`.

#### PRT005 — Geometry-only ID multiplication

Several new component IDs differ only by ID/display text while pin/property/provenance content supplies no real distinction.

FAIL with `LIBRARY-COMPONENT-SEMANTIC-CLONE`.

#### PRT006 — Legitimate shared symbol asset

Several sourced component IDs share one `.aixsym.json` digest but each has explicit part identity/provenance and independently reviewable semantic contract.

PASS.

#### PRT007 — Render succeeds, pinout review missing

Schema/binding/render PASS, but no source-bound pinout review.

Expected:

```text
structuralPass = true
partSemanticReview = INCOMPLETE
semanticReady = false
```

#### PRT008 — Review bound to wrong source/component

Pinout review references a different component ID, source URI, or library digest.

FAIL semantic review.

#### PRT009 — Minimum attributes missing

Concrete sourced part lacks required identity/description/pin/property contract.

FAIL.

#### PRT010 — Circuit intent not reviewed

Project claims circuit-intent review complete but role, required pins/no-connects, or task-relevant property-use review is incomplete.

FAIL the intent-review claim while preserving valid lower-layer results.

### 41. Grid/Placement Focused Fixtures

Retain the former 0.5.8.2 minimal grid set.

#### G001 — Already legal

```text
proposed [62.5, 42.5] -> unchanged
```

#### G002 — Quantized

```text
proposed [63.1, 42.2] -> base [62.5, 42.5]
```

#### G003 — Magnetic row

Existing row `y=40.0`, snapped candidate `y=42.5`, `G=2.5` -> legal Y-alignment candidate selected under deterministic policy.

#### G004 — Outside acquisition window

Axis more than `G` away is not acquired.

#### G005 — Grid mismatch

```text
layout.grid = 5.0
profile.snap = 2.5
```

FAIL closed.

---

### 42. Tests to Add

At minimum:

```text
reference grid remains 2.5 mm
major grid remains 10 mm
pin pitch remains 5 mm
layout/profile grid mismatch fails
snap midpoint semantics deterministic
snap idempotent on legal points
magnetic alignment bounded to G
candidate ordering independent from source ordering
placement assist performs no mutation

symbol body dimensions quantize outward to G
standard visible lead remains P = 2G under reference profile
repeated pin-group minimum span follows (N - 1)P + 2G
sizing guidance never reduces pin pitch to fit a body
sizing guidance expands to next G when field/pin clearance requires it
task guide exposes G/P/M sizing defaults for library-part creation

existing file-level provenance remains valid
component metadata.partProvenance validates
datasheet-backed concrete part requires manufacturer + partNumber + sourceUri
placeholder requires explicit reason
generic-template cannot claim an exact verified manufacturer part identity
concrete unsourced part cannot receive semantic-ready status
family parts may share sourceUri only with explicit per-ID identity/semantic contract
geometry reuse across component IDs is permitted
geometry-only component-ID multiplication is rejected
derived port/property/provenance/presentation signatures are deterministic
render PASS is reported as structural only
datasheet-backed semantic-ready status requires source-bound pinout review evidence
review evidence mismatch on component/source/library digest fails
minimum semantic attributes are reviewed
circuit-intent review has separate completion status
placeholder may structurally render but remains semanticReady=false

new library root is singular library/
new artifact requires electronics or architecture first-level domain
lower semantic segments accept lower-kebab-case
unknown first-level domain rejected
invalid segment/filename syntax rejected
new artifact below examples rejected for ordinary create-symbol
new artifact below libraries/ rejected for ordinary create-symbol
existing legacy library path can be modified in explicit repair
project manifest resolves canonical library paths project-root relatively
library asset.path resolves canonical symbol path
asset digest locking still enforced
create-symbol route stages library-layout guidance
create-symbol route does not require repository-wide search to choose output path
root REFERENCE chain reaches library-layout owner
AGENTS remains bounded and links rather than duplicates details
docs/authoring/guides/index.md is reachable directly from AGENTS and REFERENCE
guide index links every required task guide exactly once
each task guide declares a primary route or composite route
each task guide links authored route YAML and generated task packet
each task guide contains canonical reference table
task guides contain no competing authority scope
task guides stay within 12 KiB authored size
create-library-part guide exposes canonical library root, artifact relationship, naming, sizing, binding, and validation
create-schematic guide exposes grid/placement authority without duplicating routing cookbook
route-nets guide exposes Grid and Snap + Route Constraints
library/README links create-library-part guide and canonical library-layout owner
agent-visible examples use canonical library root
historical compatibility fixture remains readable

create-schematic route contains Component Placement
route-nets route contains Grid and Snap System and Route Constraints
route budgets remain <= 7 docs / 96 KiB / depth 3
cold-start reference pack contains placement assist and library-layout guidance
```

---

### 43. Compatibility and Migration

#### No core schema-version bump

0.5.9 should not require new versions of:

```text
.aixem
.aixlayout.json
.aixsym.json
.aixlib.json
.aixproj.json
```

The change is primarily an **authoring/path/review contract**, not a data-model redesign.

The new component provenance discipline uses the already-allowed `component.metadata.partProvenance` profile plus validation policy. 0.5.9 therefore does not require a new core `.aixlib` schema URI/version solely for this work.

#### Existing project references remain valid

A pre-0.5.9 project whose manifest safely references:

```text
libraries/foo.aixlib.json
symbols/foo.aixsym.json
```

remains loadable and repairable.

0.5.9 does not redefine safe legacy files as corrupt.

#### New authoring uses canonical layout

All newly created reusable artifacts in 0.5.9 ordinary authoring use:

```text
library/electronics/...
library/architecture/...
```

#### Migration is explicit

A future project may deliberately migrate old paths, but migration requires reference/digest updates and regression proof. It is not a side effect of symbol repair.

#### Render stability

For unchanged authoritative inputs, protected renderer/Viewer outputs remain unchanged.

---

### 44. Explicit Non-Goals

0.5.9 MUST NOT add:

- global automatic component placement;
- force-directed/simulated-annealing/solver-based layout;
- automatic neighbor movement;
- automatic rerouting after snap;
- GUI magnet/drag behavior;
- graphical editor;
- machine-learning placement;
- a universal electronics taxonomy below level 1;
- a universal architecture taxonomy below level 1;
- a universal fixed body-size table for every component class;
- automatic symbol body resizing or pin-layout solving;
- a second normative rule set inside task guides;
- one task guide per every internal utility or validator;
- ECLASS/ETIM/IFC/OmniClass/UniClass integration;
- manufacturer catalog ingestion;
- datasheet crawling or automatic PDF pinout extraction;
- automatic truth verification by fetching every `sourceUri`;
- automatic electrical-safety/rating certification;
- internet part search;
- BOM/ERP/PLM database services;
- a package manager/registry for libraries;
- cross-project central library service;
- automatic deduplication by fuzzy component similarity;
- forced migration of all historical fixtures;
- new component/symbol primitives;
- new routing algorithms;
- new Viewer editing capability;
- provider-specific Agent behavior;
- actual external Agent execution.

The release is strictly a **deterministic authoring discipline and project library-organization hardening** release.

---

### 45. Implementation Phases

#### Phase 0 — Freeze exact 0.5.8.1 baseline

Record:

- protected technical hashes;
- grid/profile values;
- current symbol sizing rules and corpus dimensions;
- current task packets and route budgets;
- current guide/cookbook locations;
- current example/generator library paths;
- existing library/symbol path references;
- repository/corpus baselines;
- external Agent claim flags remain false.

#### Phase 1 — Publish canonical library-layout and part-integrity contract

Add/update the single canonical authority for:

- `library/` root;
- `electronics` / `architecture` domains;
- lower hierarchy naming;
- file naming;
- new-vs-existing artifact policy;
- component provenance-status vocabulary;
- concrete-part `sourceUri` requirement;
- explicit placeholder behavior;
- geometry reuse vs semantic-ID generation boundary;
- structural-vs-semantic validation claim separation;
- prohibited destinations.

Wire it into metadata, navigation, traceability, root reference chaining, and `library/README.md`.

#### Phase 2 — Consolidate grid-proportional symbol sizing

Update the existing Symbol Design Profile and authoring/cookbook surfaces to expose one consistent sizing method:

- body dimensions quantized outward to `G`;
- `P`-based repeated pin span;
- `2G` total end padding under the reference profile;
- standard lead length `2G`;
- text/field expansion by `G` increments;
- corpus-first class-specific starting proportions.

Do not add an auto-sizing engine or core schema change.

#### Phase 3 — Close grid authority and placement guidance

Absorb the complete approved 0.5.8.2 grid/snap contract:

- active-profile authority;
- layout grid coherence;
- placement hard/preferred rules;
- deterministic quantization;
- bounded magnetic alignment.

#### Phase 4 — Establish the task-oriented Agent guide layer

Create:

```text
docs/authoring/guides/
```

with the index and seven initial guides.

Add the standard guide template and documentation checks.

Wire:

```text
AGENTS.md
REFERENCE.md
docs/authoring/index.md
library/README.md
```

to the new guide entrypoints while keeping AGENTS concise.

#### Phase 5 — Repair route retrieval

Update:

- `create-symbol` to stage library-location/naming/sizing/provenance/semantic-integrity guidance;
- `create-schematic` to stage Component Placement;
- `route-nets` to stage direct hard grid/route constraints;
- composite route docs to point to the matching task guides where useful.

Preserve task-packet budgets.

#### Phase 6 — Implement placement-assist helper

Add pure deterministic implementation and read-only CLI.

No authority mutation.

#### Phase 7 — Implement library path/naming and part-integrity validation

Add:

- canonical new-artifact path validator;
- first-level domain validator;
- lower-kebab segment/file validator;
- added-vs-modified compatibility logic;
- examples/non-authoritative destination protection;
- `partProvenance` profile validator;
- concrete source/placeholder validator;
- minimum semantic-attribute checks;
- semantic-clone batch detector using derived signatures;
- source-bound semantic-review evidence validator;
- truthful structural/semantic/intent status aggregation.

#### Phase 8 — Update current example generators

Migrate agent-visible current authoring examples by editing generator ownership, not generated results by hand.

Where examples demonstrate symbol sizing, ensure they identify the `G/P/M` construction rhythm or linked corpus recipe.

Retain explicit historical compatibility fixtures where useful.

#### Phase 9 — Cold-start staging closure

Prove a fresh stage contains:

- concise AGENTS pointer;
- `docs/authoring/guides/index.md`;
- task-specific guide for the active route;
- library-layout contract for library creation;
- Symbol Design Profile / sizing references for part creation;
- `.aixlib` / `.aixsym` contracts needed by route;
- component provenance/placeholder/bulk-generation guidance for part creation;
- structural-vs-semantic validation claim guidance;
- placement/grid documents for relevant tasks;
- placement-assist CLI.

No source-repository search fallback.

#### Phase 10 — Add focused fixtures and diagnostics

Implement:

- G001-G005 grid/placement behavior;
- LBY001-LBY008 library path/naming behavior;
- PRT001-PRT010 provenance/semantic-integrity/claim-boundary behavior;
- focused sizing-rule tests;
- task-guide reachability/role/size/reference tests.

Do not create a new large corpus.

#### Phase 11 — Regenerate derived products

Regenerate:

- document index;
- route index;
- task packets;
- requirement traceability;
- documentation site;
- reference pack;
- documentation relationship audit;
- examples/corpus outputs owned by changed generators;
- release evidence;
- release manifest.

#### Phase 12 — Full technical regression

Before the inherited suites, run a focused part-integrity review proving that render-only PASS cannot authorize semantic-ready status.

Run all existing:

- repository tests;
- Agent Evaluation Tier A;
- historical agent evaluation;
- symbol/static corpus;
- hierarchical project corpus;
- Reference Viewer corpus;
- pre-live readiness fixtures;
- document relationship/governance audit;
- protected circuit/render/Viewer hash checks.

#### Phase 13 — Five independent clean verification passes

Because 0.5.9 changes route-visible authoring guidance, canonical output paths, sizing guidance, and first-hop task navigation, run **five independent clean passes** after the last fix.

Each pass starts from clean generated outputs.

If any pass finds a new defect:

1. repair at the smallest owning layer;
2. invalidate the current consecutive-pass count;
3. restart five clean passes from the corrected state.

This is the final deterministic authoring-structure closure before external Agent integration.

### 46. Acceptance Criteria

#### Grid / placement

- [ ] `G = 2.5 mm`, `P = 5 mm`, `M = 10 mm` remain unchanged for the reference profile.
- [ ] Active profile is explicitly the schematic snap authority.
- [ ] Layout/profile grid mismatch fails closed.
- [ ] Component Placement is directly staged for `create-schematic`.
- [ ] Hard grid legality is separate from preferred alignment rhythm.
- [ ] Deterministic quantization is specified and tested.
- [ ] Magnetic X/Y alignment is bounded to `G`.
- [ ] Placement assist never mutates authoritative files.

#### Symbol sizing

- [ ] Symbol Design Profile exposes one explicit `G/P/M` sizing vocabulary.
- [ ] Body dimensions are guided to quantize outward to `G`.
- [ ] Repeated pin-group minimum body span is documented as `(N - 1)P + 2G` for the reference profile.
- [ ] Standard visible lead remains `P = 2G` unless an active profile/recipe explicitly differs.
- [ ] The sizing sequence considers pin names, numbers, fields, and internal labels before finalizing body dimensions.
- [ ] Agents are told to enlarge by `G` increments rather than compress `P` or standard lead length to resolve collisions.
- [ ] Class-specific exact sizes remain cookbook/corpus precedents, not universal MUST values.
- [ ] No automatic symbol-size mutation engine is introduced.

#### Task-oriented Agent guides

- [ ] `docs/authoring/guides/index.md` exists.
- [ ] The initial guide set contains `create-library-part`, `create-schematic`, `route-nets`, `compose-project`, `author-component-circuit`, `render-review`, and `validate-project`.
- [ ] `AGENTS.md` links the guide index without embedding detailed task manuals.
- [ ] `REFERENCE.md` links the guide index as the common “how do I do X?” entrypoint.
- [ ] `docs/authoring/index.md` links the guide index.
- [ ] Each task guide declares its route, inputs, authority, output location, short procedure, canonical references, validators, completion criteria, and stop conditions.
- [ ] Each task guide links the authored route and generated task packet.
- [ ] Each guide stays within the 12 KiB hard limit.
- [ ] No task guide owns a competing normative authority scope.
- [ ] Root/guide/route/reference chains have no broken links or orphaned guide.
- [ ] Cold-start staging includes the matching task guide for covered authoring routes.

#### Part provenance and semantic integrity

- [ ] Existing library/symbol file-level provenance keeps its current meaning.
- [ ] Newly authored component IDs use the 0.5.9 `metadata.partProvenance` profile.
- [ ] A concrete real-part identity requires `manufacturer`, `partNumber`/stable product ID, and `sourceUri`.
- [ ] A concrete part without reliable source evidence is explicitly `placeholder`.
- [ ] Placeholder requires a reason and cannot receive `semanticReady=true`.
- [ ] `generic-template` is allowed only when no exact real manufacturer part is claimed.
- [ ] A single symbol asset may legitimately serve several semantically valid component IDs.
- [ ] Geometry copying or ID/display-name substitution alone cannot create validated component identities.
- [ ] Every component ID has a complete pin/terminal contract, minimum semantic attributes, provenance status, and presentation binding.
- [ ] Datasheet-backed semantic-ready status requires source-bound pinout review evidence.
- [ ] `render PASS` is explicitly reported as structural only.
- [ ] Part semantic review and circuit-intent review have separate results.
- [ ] Circuit-intent review checks role, intended connected pins, required pins/no-connects, task-relevant properties, and endpoint-preserving presentation.
- [ ] Review evidence is bound to exact component/library/symbol/source identity/digests.
- [ ] No datasheet crawler, catalog importer, or automatic electrical-safety claim is introduced.

#### Canonical library root

- [ ] New reusable project-library artifacts use `<authoring-root>/library/`, normally `<project-root>/library/` for standalone projects.
- [ ] A repository-level reusable-library task in the AIXEM workspace resolves to repository-root `library/`, not `examples/parts/`.
- [ ] The canonical root is singular `library`.
- [ ] New ordinary authoring does not create reusable artifacts under `examples/`, `parts/`, `libraries/`, or a standalone `symbols/` root.

#### First-level domain

- [ ] `electronics` is accepted.
- [ ] `architecture` is accepted.
- [ ] Unknown first-level domains are rejected for new authoring.
- [ ] No second-level controlled taxonomy is introduced.

#### Generic hierarchy

- [ ] Lower hierarchy segments use lower-kebab-case.
- [ ] Existing semantic namespaces are reused before synonyms are created where deterministically knowable.
- [ ] No hard fixed depth is imposed.
- [ ] Mutable project-instance properties are not required in directory structure.

#### File naming

- [ ] New `.aixlib.json` names are lower-kebab and semantically scoped.
- [ ] New `.aixsym.json` names are lower-kebab and represent reusable identity, not `R1/U3` instance names.
- [ ] Internal library/component/symbol IDs remain authoritative identity.

#### Compatibility

- [ ] Existing safe pre-0.5.9 library/symbol paths remain loadable.
- [ ] Existing explicit legacy artifacts can be repaired in place.
- [ ] New legacy-style artifact paths are blocked during ordinary new creation.
- [ ] Explicit migration updates project/asset paths and digests correctly.

#### Agent retrieval

- [ ] `create-symbol` directly reveals canonical output-location and naming rules.
- [ ] `create-schematic` directly reveals Component Placement.
- [ ] `route-nets` directly reveals Grid and Snap + Route Constraints.
- [ ] Task packet limits remain unchanged.
- [ ] Cold-start reference pack contains all required contracts and advisory tooling.
- [ ] Agent does not need repository-wide search to decide where a new part belongs.
- [ ] `create-library-part` tells the Agent to resolve provenance status before inventing concrete pins/geometry.
- [ ] The Agent can reach the structural-vs-semantic validation boundary directly from the library-part guide.
- [ ] Batch creation guidance permits shared symbol assets but prohibits geometry-only semantic ID multiplication.

#### Documentation/root chaining

- [ ] `REFERENCE.md` exposes both the task-guide index and the component/symbol library authoring chain.
- [ ] `AGENTS.md` directly points common authoring work to `docs/authoring/guides/index.md`.
- [ ] `docs/authoring/guides/index.md` provides one-hop links to all initial task guides.
- [ ] Task guides link the canonical owners required for their task and do not require repository-wide search.
- [ ] `REFERENCE.md` links the component/symbol library authoring chain.
- [ ] `library/README.md` is a concise non-normative navigation entrypoint and links the canonical owner.
- [ ] `AGENTS.md` remains concise and only points to the detailed contract.
- [ ] Canonical section indexes cover the new/updated document owner.
- [ ] No orphan document is introduced.
- [ ] No conflicting normative owner is introduced.

#### Examples and precedent

- [ ] Current agent-visible authoring examples teach `library/<domain>/...`.
- [ ] Example generators, not generated files, own the migration.
- [ ] At least one historical legacy-path fixture remains intentionally supported.

#### Regression / claims

- [ ] Existing circuit semantics unchanged.
- [ ] Existing renderer/Viewer behavior unchanged for unchanged sources.
- [ ] Existing pre-live harness remains green.
- [ ] Existing symbol-expressiveness render results remain valid but are not reinterpreted as datasheet correctness evidence.
- [ ] Synthetic/generic conformance fixtures are identified as generic/conformance artifacts, not sourced manufacturer parts.
- [ ] Five independent clean verification passes succeed consecutively after the final fix.
- [ ] `externalTierBExecuted = false`.
- [ ] `liveExternalAgentExecuted = false`.
- [ ] `liveClaimAuthorized = false`.

---

### 47. Priority

#### P0 — Complete before first real Agent

1. canonical `library/<domain>/...` new-artifact structure;
2. `electronics` / `architecture` first-level classification;
3. lower-kebab reusable namespace/file naming;
4. component-level provenance status and concrete `sourceUri` rule;
5. explicit placeholder behavior for unsourced/uncertain concrete parts;
6. semantic bulk-generation rule preventing geometry-only component-ID multiplication;
7. structural render PASS vs part-semantic/circuit-intent review separation;
8. grid-proportional symbol sizing rhythm;
9. deterministic placement snap/magnetic assist;
10. grid authority coherence;
11. task-oriented guide directory and standard guide template;
12. direct root -> guide -> route -> canonical-reference chaining;
13. route visibility for library path, provenance, semantic integrity, sizing, placement, and routing rules;
14. new-vs-existing compatibility behavior;
15. agent-visible example/generator migration;
16. focused diagnostics/tests;
17. five clean verification passes.

#### P1 — Consider only after real Agent evidence

- namespace suggestion scoring based on actual Agent misclassification;
- symbol/body collision recommendation;
- route-length-aware placement candidate scoring;
- semantic functional-block placement hints;
- richer library search/indexing;
- library alias/deprecation metadata if real migrations become frequent.

#### P2 — Separate future architecture decisions

- central cross-project library registry;
- remote package manager;
- vendor catalog sync;
- universal industry taxonomy;
- GUI library browser/editor;
- global auto-layout or placement/routing optimizer.

---

### 48. Definition of Done

AIXEM 0.5.9 is complete when a fresh AI authoring task can follow both of these paths without guessing.

#### Agent task-guide path

```text
root entrypoint
    -> AGENTS.md / REFERENCE.md
    -> docs/authoring/guides/index.md
    -> task-specific guide
    -> authored route / generated task packet
    -> canonical requirement owners
    -> validator / evidence
```

#### Library-part provenance and semantic-integrity path

```text
create-library-part
    -> decide: datasheet-backed | generic-template | placeholder
    -> if concrete: capture manufacturer + partNumber + sourceUri
    -> author semantic pin/terminal/property contract
    -> reuse/create graphic symbol presentation
    -> bind and digest-lock
    -> structural/schema/render validation
    -> source-bound pinout + minimum-property review
    -> if used in circuit: circuit-intent review
    -> publish separate structural / semantic / intent statuses
```

The system must reject this false shortcut:

```text
copy geometry
    -> assign new component IDs
    -> render succeeds
    -> claim "verified parts"
```

#### Library-part sizing path

```text
create-library-part guide
    -> resolve project root + library domain
    -> select nearest validated symbol recipe
    -> apply G/P/M sizing rhythm
    -> compute repeated pin span
    -> quantize body outward to G
    -> preserve standard lead/pitch
    -> create .aixlib + required .aixsym asset(s)
    -> bind / digest-lock
    -> lint / render / inspect
```

#### Placement path

```text
create-schematic
    ↓
Component Placement + Grid contract visible
    ↓
G = 2.5 mm resolved from active profile
    ↓
optional placement-assist suggest
    ↓
legal deterministic snap/alignment candidate
    ↓
Agent explicitly edits .aixlayout.json
    ↓
Change-Set captures mutation
    ↓
existing conformance validates actual source
```

#### Reusable library path

```text
create-symbol
    ↓
identify project root
    ↓
determine task is NEW artifact vs EXISTING repair
    ↓
NEW artifact
    ↓
select first-level domain:
    electronics | architecture
    ↓
inspect existing domain namespace
    ↓
reuse existing semantic hierarchy when appropriate
    or create minimum lower-kebab namespace
    ↓
create:
    library/<domain>/<semantic-namespace...>/<name>.aixlib.json
    library/<domain>/<semantic-namespace...>/<name>.aixsym.json
    ↓
update project/library asset paths and digests
    ↓
validate schema + binding + path + naming + digest
    ↓
close authoring loop
```

The system must be able to state truthfully:

```text
canonical authoring/project library root    complete
first-level domain classification          complete
lower-level taxonomy                       intentionally open
lower-level naming/reuse discipline        complete
new-vs-existing path behavior              complete
examples are not production library root   complete
component provenance status                complete
concrete part sourceUri rule               complete
placeholder truthfulness                   complete
geometry-only semantic ID cloning          prohibited
render-vs-semantic claim boundary          complete
pinout/source review gate                  complete
circuit-intent review gate                 complete
grid authority                             complete
deterministic snap semantics               complete
bounded magnetic placement assist          complete
auto-placement                             intentionally absent
universal parts taxonomy                    intentionally absent
external Agent execution                   not yet performed
```



---

### 49. Final Library-Part Validation Claim Matrix

0.5.9 must use these result meanings consistently:

| Result | What it proves | What it does NOT prove |
|---|---|---|
| `STRUCTURAL_PASS` | schema, binding, geometry, grid, symbol lint, deterministic render | datasheet pinout correctness, part selection, ratings, circuit suitability |
| `PART_SEMANTIC_PASS` | provenance policy, concrete identity, pinout-source review, minimum semantic attributes, binding review | full electrical-design correctness or safety |
| `GENERIC_TEMPLATE_PASS` | coherent generic component class with no false concrete identity | existence of a manufacturer product |
| `PLACEHOLDER` | unresolved/uncertain concrete intent is explicit | semantic/production readiness |
| `CIRCUIT_INTENT_REVIEW_PASS` | selected component contract was reviewed against stated role and pin/property use | absolute-max, thermal, regulatory, or unimplemented ERC/DRC certification |

No report may collapse these into one ambiguous `PASS`.

### Final 0.5.9 Authoring Retrieval Model

The release should close with the following practical model:

```text
“What do I need to do?”
        |
        v
docs/authoring/guides/index.md
        |
        +--> create-library-part
        |       |
        |       +--> library/<electronics|architecture>/...
        |       +--> G/P/M sizing rhythm
        |       +--> .aixlib / .aixsym / binding
        |
        +--> create-schematic
        |       |
        |       +--> semantic authority
        |       +--> placement + snap assist
        |
        +--> route-nets
        |       |
        |       +--> orthogonal G-aligned routing
        |
        +--> compose-project
        +--> author-component-circuit
        +--> render-review
        +--> validate-project
                |
                v
      canonical specifications
                |
                v
      validators / evidence / close
```

The 0.5.9 quality bar is:

> **A fresh Agent must not have to invent a library location, invent symbol proportions, infer a grid-alignment policy, fabricate a concrete part without source evidence, or treat a successful render as proof of semantic correctness. AIXEM must provide one short task guide, one bounded route, one canonical authority chain, source-or-placeholder provenance discipline, semantic-ID integrity, and separately reported structural/part/circuit review results without adding a datasheet crawler, automatic layout engine, editor, or universal parts taxonomy.**

---

# TRACK B — PIN ELECTRICAL SEMANTICS, ERC PREPARATION, AND AGENT PLACEMENT STRATEGY

The following track incorporates the complete detailed scope of the former 0.5.10 plan. It builds on Track A inside this same 0.5.2 plan rather than defining a separate release.

### 1. Executive Summary

AIXEM 0.5.9 closes the major pre-live authoring gaps around canonical library location, part provenance, semantic part integrity, symbol sizing rhythm, grid authority, deterministic snap assistance, and task-oriented Agent guides.

The next conservative hardening step should not expand AIXEM into a simulator or global auto-layout solver. Instead it should make two existing strengths substantially more useful:

1. **component ports already own stable electrical endpoint identity and an electrical `type`, but the semantics are too shallow for robust ERC preparation, richer Agent reasoning, and future simulation-model binding;**
2. **placement already has grid, flow, grouping, and collision rules, but the Agent still lacks one explicit strategic decision procedure for turning circuit intent into repeatable component placement.**

0.5.10 therefore adds one bounded semantic profile and one bounded placement strategy.

The central design is:

```text
component port
    |
    +-- id / name / terminal
    +-- type                  -> electrical connection behavior
    +-- required              -> connectivity obligation
    +-- metadata.pinSemantics -> function, signal class, polarity,
                                 differential pairing, power-domain hint,
                                 capabilities, alternate functions
```

The existing `port.type` remains authoritative for basic electrical drive/connection behavior. It is not replaced by a larger all-purpose taxonomy.

The new metadata profile adds **orthogonal semantic facets** that help an Agent answer questions such as:

- Is this pin primarily analog, digital, power, ground, reference, or mixed-signal?
- Is the signal active-low?
- Is it one member of an explicitly declared differential pair?
- Does it belong to an explicit power-domain hint?
- Does the physical terminal expose alternate source-backed functions?
- Is a placement preference based on explicit semantics or merely on a visual/name heuristic?

This is enough to improve:

- part authoring quality;
- pinout review;
- static electrical-consistency checks;
- Agent placement decisions;
- future ERC;
- future simulation-model terminal mapping.

It is intentionally **not** enough to claim analog simulation correctness, voltage-limit safety, timing correctness, or device-model fidelity.

For placement, the release adds a new task guide:

```text
docs/authoring/guides/place-components.md
```

The guide defines how an Agent should transform semantic circuit information into `.aixlayout.json` placement while preserving the existing authority split.

The placement sequence becomes:

```text
semantic closure
    -> evidence-quality classification
    -> freeze existing valid anchors when editing
    -> identify explicit functional regions
    -> choose boundary/primary anchors
    -> place principal components
    -> place explicitly related support components
    -> align semantic pin groups
    -> reserve routing channels
    -> perform route-feasibility review
    -> local G/M-grid refinement
    -> render / validate / repair
```

The strategy prioritizes **semantic correctness and readability over compactness**.

The Agent must not invent functional relationships merely to make a visually attractive drawing.

---

### 2. Baseline Findings

#### 2.1 Existing pin model is already a strong base

The current component-library schema already gives each component port:

```text
id
name
type
description?
terminal?
required?
metadata?
```

The current electrical `type` vocabulary already includes:

```text
input
output
bidirectional
passive
power-input
power-output
open-collector
open-emitter
tri-state
no-connect
unspecified
```

and domain-generic values used outside ordinary electronics.

This is enough to establish endpoint identity and basic connection behavior.

The problem is not that pin attributes are absent. The problem is that **all remaining semantic meaning is currently pushed into unstructured metadata or naming convention**.

Examples of information not yet normalized strongly enough include:

```text
clock
reset
enable
analog
digital
reference
ground
active-low
differential-positive
differential-negative
power-domain association
alternate MCU/FPGA pin functions
source-backed pin capabilities
```

#### 2.2 `type` must not become an overloaded universal field

A pin may simultaneously be:

```text
type = input
signal class = digital
functional tag = reset
polarity = active-low
power domain = vddio
```

Trying to encode all of this into one huge `type` enum would create unstable combinatorial values such as:

```text
digital-active-low-reset-input
analog-bidirectional-reference
```

That is not suitable for a durable standard.

0.5.10 therefore preserves `type` as one axis and defines additional orthogonal axes.

#### 2.3 Existing placement rules define legality, not enough decision strategy

The current placement authority already provides the correct high-level sequence:

```text
establish page zones and signal flow
place connectors and power boundaries
place functional blocks
align related pin rows
reserve routing channels
run collision and grid checks
```

The existing visual language also already prefers:

- left-to-right signal flow;
- functional grouping;
- supplies above and returns below where useful;
- shared rows and columns;
- whitespace before compression.

Those rules should remain authoritative.

The remaining gap is that a fresh Agent still needs to decide:

- which components are anchors;
- what evidence is strong enough to form a functional block;
- when an existing placement should be preserved;
- how to rank two equally legal positions;
- when to prioritize pin alignment over compactness;
- when route feasibility justifies a local move;
- when not to infer a relationship;
- how explicit pin semantics should affect placement.

0.5.10 closes this as an informative Agent strategy, not a new geometry authority.

---

## PART I — PIN ELECTRICAL SEMANTICS HARDENING

### 3. Design Principles

#### P1 — Stable endpoint identity remains primary

A pin's semantic identity remains its component port ID.

Pin name, terminal number, symbol position, and visual order must never replace stable endpoint identity.

#### P2 — `port.type` remains the basic electrical-behavior class

`port.type` continues to answer:

> What kind of electrical connection/drive behavior does this endpoint expose?

Do not replace it with functional names such as `clock`, `reset`, or `uart-tx`.

#### P3 — Functional meaning is orthogonal to electrical behavior

A clock pin can be an input or an output.

A reset pin can be active-high or active-low.

An analog pin can be input, output, bidirectional, or passive depending on device behavior.

The model must preserve these dimensions separately.

#### P4 — Do not create a universal pin-function taxonomy

AIXEM should provide a small core vocabulary and stable token syntax, while allowing source-backed domain-specific tags.

#### P5 — New semantics must remain source-reviewable

For a datasheet-backed component, detailed pin semantics must be reviewable against the cited source.

The Agent must not add capabilities or alternate functions merely because a pin name looks familiar.

#### P6 — Future simulation readiness does not mean simulation semantics now

0.5.10 may make endpoint meaning easier to bind later to SPICE, IBIS, Verilog-A, or another backend.

It must not define solver-specific terminal ordering, model equations, voltage limits, timing models, or analysis directives in this release.

---

### 4. Canonical Pin Electrical Semantics Profile

Add one normative owner:

```text
docs/specifications/components/pin-electrical-semantics-profile.md
```

Recommended ID:

```text
AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
```

The document owns:

- meaning of `port.type`;
- `metadata.pinSemantics` profile;
- semantic facet precedence;
- source-review expectations;
- internal consistency rules;
- future ERC/simulation boundary.

It must not own symbol geometry or wire routing.

---

### 5. Preserve Existing `port.type`

Keep the existing ordinary electronics values as the electrical behavior axis:

```text
input
output
bidirectional
passive
power-input
power-output
open-collector
open-emitter
tri-state
no-connect
unspecified
```

Existing architecture/generic values remain compatible with their current domain contracts.

Recommended interpretation:

| `type` | Meaning |
|---|---|
| `input` | receives a signal and is not normally an active driver |
| `output` | actively drives a signal |
| `bidirectional` | may receive or drive depending on component state |
| `passive` | no directional drive assumption |
| `power-input` | consumes/accepts supply or return connection |
| `power-output` | provides a supply rail or power source |
| `open-collector` | sinking/open driver requiring external network interpretation |
| `open-emitter` | sourcing/open driver requiring external network interpretation |
| `tri-state` | active driver that may enter a high-impedance state |
| `no-connect` | physical terminal must not participate in normal connectivity |
| `unspecified` | behavior is intentionally unresolved; not an ERC-ready claim |

This table must be treated as electrical behavior, not full circuit correctness.

---

### 6. `metadata.pinSemantics` Profile

Use the already-available port metadata extension surface.

Recommended shape:

```json
{
  "id": "reset-n",
  "name": "RESET_N",
  "terminal": "14",
  "type": "input",
  "required": true,
  "metadata": {
    "pinSemantics": {
      "profile": "aixem-pin-semantics-1",
      "signalClass": "digital",
      "functionalTags": [
        "reset"
      ],
      "polarity": "active-low",
      "powerDomain": "vddio",
      "capabilities": []
    }
  }
}
```

#### 6.1 `profile`

Required when `pinSemantics` exists:

```text
aixem-pin-semantics-1
```

This allows future evolution without redefining unversioned metadata.

#### 6.2 `signalClass`

Closed initial vocabulary:

```text
analog
digital
mixed-signal
power
ground
reference
rf
unspecified
```

Purpose:

- placement grouping;
- review;
- future ERC/simulation adapter hints.

It does not define waveform or voltage.

#### 6.3 `functionalTags`

Open, lower-kebab-case semantic tags.

Recommended core examples:

```text
clock
reset
enable
power
ground
reference
oscillator
communication
programming
debug
test
chip-select
interrupt
sense
feedback
shield
chassis
```

Protocol-specific tags may be used when source-backed:

```text
i2c-clock
i2c-data
spi-clock
spi-mosi
spi-miso
uart-tx
uart-rx
usb-data
can-high
can-low
```

The standard does not attempt to enumerate every future function.

#### 6.4 `polarity`

Closed vocabulary:

```text
unspecified
active-high
active-low
positive
negative
```

Use:

- `active-high` / `active-low` for control/logic meaning;
- `positive` / `negative` for paired/polarized signal meaning.

Polarity does not replace `type`.

#### 6.5 `differentialPair`

Optional:

```json
{
  "id": "usb2-data",
  "member": "positive"
}
```

or:

```json
{
  "id": "usb2-data",
  "member": "negative"
}
```

Rules:

- pair ID is stable within the component definition;
- one pair may have at most one positive and one negative physical member in the basic profile;
- pairing does not imply route geometry by itself;
- the routing/placement Agent may use it only as a preference after semantic closure.

#### 6.6 `powerDomain`

Optional stable semantic hint such as:

```text
vdd
vddio
avdd
dvdd
vcore
vbat
```

It is **not** a voltage value and is not a substitute for a net or component property.

Its purpose is to group related pins and assist future constraint/model binding.

#### 6.7 `capabilities`

Open, source-backed lower-kebab tokens.

Examples:

```text
interrupt-capable
clock-capable
adc-capable
dac-capable
wake-capable
open-drain-capable
high-drive-capable
```

Capabilities describe what the terminal can support, not which function is currently active in the circuit.

#### 6.8 `alternateFunctions`

Optional for muxed terminals.

Recommended form:

```json
[
  {
    "name": "PA9",
    "functionalTags": ["gpio"]
  },
  {
    "name": "USART1_TX",
    "functionalTags": ["uart-tx"]
  },
  {
    "name": "TIM1_CH2",
    "functionalTags": ["timer-output"]
  }
]
```

Rules:

- alternate functions all belong to the same physical terminal;
- they do not create additional component endpoints;
- their presence must be source-backed for datasheet-backed components;
- selected runtime/device configuration is outside the 0.5.10 component-format scope.

---

### 7. Explicitly Excluded Pin Attributes

Do not add the following to the base pin-semantics profile in 0.5.10:

```text
absolute maximum voltage
operating voltage range
input threshold equations
output impedance
rise/fall time
frequency limit
thermal limit
ESD rating
SPICE terminal index
IBIS model terminal
simulation initial condition
waveform source
logic state
runtime mux selection
```

These belong to future electrical-constraint or simulation-binding profiles.

Mixing them into a general pin metadata profile now would create premature solver-specific coupling.

---

### 8. Pin Semantic Consistency Validation

Add a focused validator layer.

Recommended diagnostics:

```text
AIXEM-DIAG-PIN-SEMANTICS-PROFILE-INVALID
AIXEM-DIAG-PIN-SIGNAL-CLASS-INVALID
AIXEM-DIAG-PIN-FUNCTION-TAG-INVALID
AIXEM-DIAG-PIN-POLARITY-INCONSISTENT
AIXEM-DIAG-PIN-DIFFERENTIAL-PAIR-INCOMPLETE
AIXEM-DIAG-PIN-ALTERNATE-FUNCTION-INVALID
AIXEM-DIAG-PIN-SOURCE-REVIEW-INCOMPLETE
AIXEM-DIAG-PIN-NOCONNECT-CONTRADICTION
```

#### 8.1 Hard failures

Examples:

```text
type=no-connect + required=true
invalid pinSemantics profile version
invalid functional tag syntax
one differential pair declares two positive members
alternate function entry has no stable name
datasheet-backed semantic-ready claim includes unreviewed source-dependent pin semantics
```

#### 8.2 Review-level warnings

Examples:

```text
signalClass=unspecified on an otherwise semantic-ready complex IC
active-low polarity with no functional/control context
powerDomain specified on unrelated signalClass without justification
bidirectional or tri-state multi-driver topology requiring higher-level review
```

Warnings must not be silently converted to hard electrical-design claims.

---

### 9. ERC-Preparatory Compatibility Layer

0.5.10 should add only a **bounded static compatibility precheck**, not claim a complete ERC engine.

Recommended base outcomes:

```text
PASS
WARN
ERROR
NOT_EVALUATED
```

Examples:

| Situation | Result |
|---|---|
| `output` + one or more `input` | normally PASS |
| multiple ordinary `output` drivers | ERROR |
| `power-output` + `power-input` | normally PASS |
| multiple `power-output` sources on one local net | ERROR unless a future explicit rule allows it |
| connected `no-connect` | ERROR |
| only inputs on a locally closed net | WARN; source may be hierarchical/external |
| multiple `open-collector` drivers | WARN; external bias network not automatically proven |
| multiple `tri-state` drivers | WARN; enable exclusivity not automatically proven |
| multiple `bidirectional` endpoints | WARN or NOT_EVALUATED |
| `unspecified` involved | NOT_EVALUATED / WARN, never semantic PASS by assumption |

The checker must never claim:

```text
electrically safe
timing correct
voltage compatible
simulation correct
production ready
```

based only on the compatibility matrix.

---

### 10. Provenance and Pin-Semantics Review Binding

Extend the 0.5.9 part semantic review so datasheet-backed components record that the following were reviewed where applicable:

```text
terminal number
canonical pin name
port.type
signalClass
polarity
differential pairing
alternate functions
declared capabilities
powerDomain hint
```

The evidence should bind to:

```text
component ID
library digest
sourceUri
sourceDigest when captured
pin-semantics profile version
review timestamp
review result
```

A graphic symbol's metadata remains presentation evidence and must not redefine these component-port semantics.

---

### 11. Future Simulation Binding Boundary

The current component model already has an asset-model attachment surface. 0.5.10 should preserve a clean future path:

```text
AIXEM component ports
    -> future Simulation Binding Contract
    -> simulation model terminal map
    -> locked model asset
    -> backend-specific netlist / simulation IR
```

Future example:

```text
component port "gate"
    -> simulation terminal "G"

component port "drain"
    -> simulation terminal "D"

component port "source"
    -> simulation terminal "S"
```

0.5.10 must **not** define the terminal map format yet.

The release should only state that:

- stable component port IDs are the future source side of simulation mapping;
- `metadata.pinSemantics` may assist adapter selection and validation;
- component `models` remain potential locked model assets;
- solver-specific mapping and parameter transfer require a separate future architecture plan.

This avoids prematurely binding AIXEM to SPICE alone.

---

## PART II — AGENT COMPONENT PLACEMENT STRATEGY

### 12. Add `place-components.md`

Add:

```text
docs/authoring/guides/place-components.md
```

Recommended ID:

```text
AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001
```

Status:

```text
informative
```

Primary route:

```text
create-schematic
```

The guide does not own placement legality. It points to:

- Component Placement;
- Grid and Snap System;
- Grid-First Visual Language;
- `.aixlayout.json`;
- Component Model;
- Net Model;
- Pin Electrical Semantics Profile;
- placement-assist tool.

---

### 13. Placement Evidence Hierarchy

The Agent must distinguish explicit semantics from weak inference.

Use the following evidence order:

#### Tier A — Explicit authority

Highest confidence:

```text
semantic net membership
component type/kind
component port.type
metadata.pinSemantics
project/sheet interface declarations
explicit user placement constraints
explicit no-connect intent
existing valid authoritative placement
```

#### Tier B — Stable component metadata

Useful but secondary:

```text
component descriptions
properties
classification
presentation pin groups
validated library namespace
```

#### Tier C — Naming heuristics

Weak hints only:

```text
VCC
GND
RESET_N
TX
RX
SCL
SDA
CLK
```

Names may help rank visually equivalent positions.

Names must never:

- invent a connection;
- change a port type;
- create a differential pair;
- convert an unsourced pin into a semantic-ready pin;
- override explicit Tier A semantics.

---

### 14. Strategic Placement Sequence

The guide must teach the following deterministic sequence.

#### Stage 1 — Close semantics before geometry

Before placement:

- all intended entities must resolve;
- semantic nets/no-connect declarations must be known;
- library/component identities must resolve;
- symbol bounds and mapped endpoints must resolve.

The Agent must not place a component in order to decide what it connects to.

#### Stage 2 — Freeze protected existing placement

For an existing schematic edit:

```text
existing valid placement
    = frozen by default
```

Move an existing component only when:

- the user explicitly requests global rearrangement;
- a new hard collision/constraint makes preservation impossible;
- a local move materially resolves a documented placement/routing defect.

This establishes minimal-diff behavior.

#### Stage 3 — Establish page flow and boundaries

Prefer:

```text
primary signal flow: left -> right
inputs/interfaces: left or boundary nearest source
outputs/interfaces: right or boundary nearest destination
power sources/boundaries: upper/edge zones where readable
returns/ground: lower zones where readable
```

These are preferences, not electrical truth.

#### Stage 4 — Identify explicit functional regions

Group only when supported by Tier A/B evidence.

Examples:

```text
power stage
clock/reset region
analog front end
digital processing
communication interface
sensor input
driver/output stage
```

Do not fabricate a functional block from visual similarity alone.

#### Stage 5 — Choose anchors

Anchor priority:

1. user-fixed placements;
2. sheet/project interface components;
3. external connectors;
4. explicit power-entry/source boundaries;
5. principal/high-connectivity functional devices;
6. clocks/reference sources when explicitly identified;
7. repeated-stage primary components.

Anchors should normally be placed before low-degree support components.

#### Stage 6 — Place principal components

Place the main device of each explicit functional region.

Prefer orientation that:

- exposes incoming semantic pin groups toward upstream components;
- exposes outgoing groups toward downstream components;
- leaves power/return groups readable;
- reduces immediate routing crossings;
- preserves symbol conventions.

Do not rotate solely to save area if it harms semantic readability.

#### Stage 7 — Place explicitly related support components

Relationship evidence may include:

```text
shared local nets
explicit functional tags
component kind
explicit circuit intent
pin semantic domains
```

Examples:

- a capacitor explicitly identified as decoupling may be placed near the associated power pin/group;
- an explicitly tagged pull-up network may be placed near the signal/power region it serves;
- an oscillator/crystal block may be placed near explicitly identified oscillator pins;
- a connector/transceiver pair may be placed as one interface region;
- a differential pair endpoint region may be kept geometrically coherent.

Important rule:

> Do not infer that every capacitor on a supply net is a decoupling capacitor or that every resistor on a digital net is a pull-up.

If function is not explicit, use neutral placement and preserve reviewability.

#### Stage 8 — Align pin groups, not merely body centers

Prefer positions where semantically related pin groups line up with their destinations.

The Agent should optimize for:

```text
endpoint readability
orthogonal exits
shared route channels
low crossing count
```

rather than blindly aligning every component body.

#### Stage 9 — Reserve routing channels

Before routing, reserve whitespace proportional to:

- pin density;
- expected fanout;
- number of net groups;
- branch/junction requirements;
- differential-pair preference where explicit;
- large multi-pin device edge density.

Do not pack components tightly and expect the routing stage to repair the layout.

#### Stage 10 — Route-feasibility review

Before final placement closure, estimate:

```text
likely bend count
likely crossings
pin escape congestion
channel blockage
long detours
junction density
```

This is a geometric feasibility check only.

It must not change semantic net membership.

#### Stage 11 — Local refinement

Refinement should use `G`, `P`, and `M` rhythm.

Typical order:

```text
remove hard collision
restore grid legality
restore required whitespace
reduce obvious route crossing
align related endpoint rows/columns
normalize repeated-stage rhythm
reduce unnecessary area
```

Compactness comes last.

#### Stage 12 — Render and validate

The Agent must finish with:

```text
placement closure
grid validation
collision/legibility review
route feasibility / actual routing
deterministic render
visual QA
```

---

### 15. Placement Decision Priority

When two candidate layouts conflict, use this precedence:

```text
1. semantic correctness
2. explicit user/fixed constraints
3. authority preservation / minimal existing movement
4. hard placement legality
5. non-overlap and readable fields
6. explicit functional grouping
7. endpoint/pin-group alignment
8. route feasibility / crossing reduction
9. repeated visual rhythm
10. whitespace
11. compactness
12. stable deterministic tie-break
```

This ordering is important.

A smaller drawing is not automatically a better engineering drawing.

---

### 16. Deterministic Tie-Breaking

For otherwise equivalent candidates, use stable order such as:

```text
existing coordinate preservation
lowest movement distance
major-grid alignment
pin-group alignment count
estimated route bend count
estimated crossing count
stable component ID
numeric x
numeric y
```

Do not let:

```text
JSON object order
filesystem order
hash-map iteration
non-deterministic model phrasing
```

change the chosen final placement when the semantic inputs are identical.

The exact numeric scorer does not need to be standardized in 0.5.10; the **precedence order** does.

---

### 17. Pin-Semantics-Aware Placement Guidance

The new pin profile should improve placement without becoming a design solver.

#### Power / ground

When explicitly classified:

- keep power-entry/source relationships visible;
- avoid burying required supply pins inside unrelated signal routing;
- group clearly related power-domain support parts;
- preserve ground/return readability.

Do not infer a single global ground when the semantic project contains separate domains.

#### Analog / digital / mixed-signal

When explicit `signalClass` values exist:

- avoid unnecessary intermixing of unrelated analog and high-fanout digital regions;
- place mixed-signal devices at the boundary between their explicit regions when practical.

This is placement guidance, not noise-integrity proof.

#### Reset / enable / clock

When explicit functional tags exist:

- keep source-to-consumer direction readable;
- avoid unnecessary long detours;
- keep shared clock/reset distribution visually recognizable.

This does not perform timing analysis.

#### Differential pairs

When explicit pair metadata exists:

- favor placement that allows both pair members to leave/arrive coherently;
- avoid creating avoidable geometric asymmetry before routing.

This does not claim matched impedance or PCB-length matching.

#### Alternate-function pins

The Agent must not place a part based on an alternate function unless the circuit intent actually selects or uses that function.

Capabilities are not active configuration.

---

## PART III — ADDITIONAL AGENT DOCUMENT REVIEW

### 18. Existing Guide Coverage Assessment

After the 0.5.9 task-guide layer, the main tasks are already covered:

```text
create-library-part
create-schematic
route-nets
compose-project
author-component-circuit
render-review
validate-project
```

The current Agent domain also already covers:

```text
retrieval
task routing
symbol generation
schematic authoring
routing
authoring orchestration
visual QA
validation loop
failure policy
cold-start execution
```

Therefore 0.5.10 should not create many new manuals.

The missing high-value decisions are narrower.

---

### 19. P0 Additional Guide 1 — `place-components.md`

Add as defined above.

Reason:

`create-schematic.md` should remain a short workflow façade. Detailed strategic placement inside that file would either make it too large or duplicate the normative Component Placement contract.

This guide fills a genuine decision gap.

---

### 20. P0 Additional Guide 2 — `select-library-part.md`

Add:

```text
docs/authoring/guides/select-library-part.md
```

Purpose:

An Agent often needs to **use an existing part**, not create one.

The current authoring chain is stronger for creation than selection.

The guide should teach:

```text
requested functional intent
    -> locate candidate component IDs
    -> prefer semantic/provenance-ready candidate
    -> verify pin/terminal contract
    -> verify required properties
    -> select presentation
    -> bind project/library digest
    -> use component ID in .aixem
```

Required rules:

- do not select by symbol appearance alone;
- do not select by filename alone;
- do not substitute an unsourced concrete part for a sourced exact part;
- do not use `placeholder` as production-ready merely because it renders;
- verify ports/properties before instance creation;
- preserve component ID and library digest authority.

This is particularly important once the library grows.

Primary route:

```text
create-schematic
```

No new execution route is required initially.

---

### 21. P0 Additional Guide 3 — `modify-existing-schematic.md`

Add:

```text
docs/authoring/guides/modify-existing-schematic.md
```

Purpose:

New-circuit authoring and modification of an existing validated schematic are not the same operation.

The Agent needs explicit locality rules.

Required workflow:

```text
identify requested semantic delta
    -> freeze unaffected authority
    -> determine smallest affected component/net/layout region
    -> update semantics first if needed
    -> update only affected placement/routes
    -> preserve unaffected coordinates and route geometry
    -> regenerate derived output
    -> compare before/after
```

Core principle:

> Existing valid authoritative layout is evidence and should be preserved unless the task or a concrete defect requires movement.

Required stop condition:

If the requested change would force a wide placement/routing rewrite, the Agent must report the scope expansion rather than silently redraw the page.

This guide materially reduces AI-generated layout churn.

---

### 22. Do Not Add a Separate Power/Ground Agent Guide Yet

Power and ground are critical, but a dedicated guide would currently split authority across:

- pin semantics;
- component placement;
- net semantics;
- create-schematic;
- future ERC.

For 0.5.10, add compact power/ground sections to:

```text
pin-electrical-semantics-profile.md
place-components.md
create-schematic.md
validate-project.md
```

Only create a dedicated `author-power-domains.md` later if real Agent evaluations show repeated failure.

---

### 23. Do Not Add a Separate ERC Guide Yet

0.5.10 should add:

- pin semantic consistency validation;
- bounded compatibility prechecks;
- validate-project guidance.

A dedicated ERC task guide should wait until AIXEM owns a true ERC engine with a larger rule set.

Otherwise the documentation would imply a capability stronger than the implementation.

---

### 24. Do Not Add a Simulation Guide Yet

The pin semantics work deliberately prepares for future simulation.

However a simulation guide would be premature until AIXEM defines at least:

```text
Simulation Binding Contract
Simulation IR or netlist compiler contract
model-role vocabulary
component-port -> model-terminal mapping
parameter mapping
analysis directive model
result/evidence model
```

Until then, simulation belongs in a future architecture plan, not the active Agent task surface.

---

### 25. P1 Guide Candidates After Real Agent Evidence

Only consider these after live authoring shows a repeated need:

#### `plan-sheet-structure.md`

Use if Agents repeatedly create over-dense single-sheet circuits or poor hierarchical boundaries.

#### `author-power-domains.md`

Use if power-domain mistakes remain common after pin semantics and placement guidance.

#### `reuse-circuit-pattern.md`

Use if repeated functional stages become common and Agents need a deterministic copy/rebind workflow.

These are deliberately not P0.

---

## PART IV — DOCUMENT AND ROUTE INTEGRATION

### 26. Update Existing Normative Documents

#### `Component Model`

Clarify:

```text
port.type = electrical behavior
pinSemantics = additional orthogonal endpoint semantics
presentation does not own electrical meaning
```

#### `.aixlib.json Component Library`

Document the `metadata.pinSemantics` profile and its relation to:

- ports;
- part provenance;
- models;
- presentations.

#### `Pins, Ports, and Endpoint Mapping`

Clarify that symbol metadata such as visual `semanticType` is derived/presentation-facing and cannot override component-port semantics.

#### `Component Placement`

Keep legality and canonical placement requirements here.

Add links to the informative Agent placement strategy without copying the strategy into the normative owner.

#### `Conformance Validation`

Add distinct outcomes for:

```text
pin semantic profile validation
bounded electrical compatibility precheck
part semantic review
circuit intent review
```

Do not collapse them into `render PASS`.

---

### 27. Update Existing Task Guides

#### `create-library-part.md`

Add:

```text
author port.type first
add pinSemantics only from justified source/intent
review alternate functions/capabilities for datasheet-backed parts
do not put solver parameters into pinSemantics
```

#### `create-schematic.md`

Add direct hand-off:

```text
select-library-part
-> place-components
-> route-nets
```

and explain when each guide is needed.

#### `route-nets.md`

Use explicit differential-pair and signal-class semantics only as routing preferences.

Do not infer missing semantics.

#### `validate-project.md`

Add:

```text
pin semantic validity
basic compatibility outcome
semantic review status
intent review status
```

#### `author-component-circuit.md`

Update stable chain:

```text
create-library-part
-> create-schematic
-> place-components
-> route-nets
-> render-review
-> validate-project
```

---

### 28. Update Existing Agent Guides

#### `docs/agent/symbol-generation.md`

Replace vague "classify pins by function and direction" wording with the explicit axis model:

```text
electrical behavior -> port.type
functional meaning  -> pinSemantics
presentation side   -> symbol port geometry
```

#### `docs/agent/schematic-authoring.md`

Add a direct link to `place-components.md` and minimal-change behavior for existing layouts.

#### `docs/agent/authoring-orchestration.md`

Add the rule:

```text
placement strategy may rank geometry
but may not change semantic net membership
```

and explicitly preserve the route write boundary.

---

### 29. Guide Index Chaining

Target chain:

```text
AGENTS.md
    -> REFERENCE.md
    -> docs/authoring/guides/index.md
        -> create-library-part
        -> select-library-part
        -> create-schematic
        -> place-components
        -> route-nets
        -> compose-project
        -> modify-existing-schematic
        -> author-component-circuit
        -> render-review
        -> validate-project
```

Keep the guide index compact.

Do not place full pin semantics or placement rules inside `AGENTS.md`.

---

### 30. Retrieval Budget

Preserve the existing bounded retrieval policy.

A placement-focused `create-schematic` packet should not load every authoring guide at once.

Recommended approach:

```text
create-schematic route
    -> create-schematic guide
    -> Component Placement
    -> Grid and Snap
    -> Component Model
    -> .aixem
    -> .aixlayout
    -> selected one of:
         place-components
         select-library-part
```

If route budgets require it, treat `select-library-part` and `place-components` as task-intent-selected alternatives rather than always-on additions.

---

## PART V — TESTS AND FIXTURES

### 31. Pin Semantic Fixtures

#### PIN001 — Digital active-low reset input

```text
type=input
signalClass=digital
functionalTags=[reset]
polarity=active-low
```

PASS.

#### PIN002 — Differential pair complete

Two ports:

```text
pair=usb2-data positive
pair=usb2-data negative
```

PASS.

#### PIN003 — Differential pair duplicate member

Two positive members with the same pair ID.

FAIL.

#### PIN004 — No-connect contradiction

```text
type=no-connect
required=true
```

FAIL.

#### PIN005 — Datasheet-backed alternate functions reviewed

Source-backed MCU terminal with multiple alternate functions and valid review evidence.

PASS.

#### PIN006 — Unsourced invented capability

Datasheet-backed component receives a new capability not represented in review evidence.

Semantic-ready claim FAIL.

#### PIN007 — Geometry does not override semantics

Symbol metadata says `input` while component port is `output`.

Presentation must not redefine component semantics; diagnostic/review required.

#### PIN008 — Stable signature

Equivalent pin semantic objects serialized in different JSON key order produce the same derived validation signature.

PASS.

---

### 32. ERC-Preparatory Fixtures

#### ERC001

One `output` driving two `input` endpoints.

PASS.

#### ERC002

Two ordinary `output` endpoints on the same closed net.

ERROR.

#### ERC003

One `power-output` and multiple `power-input`.

PASS at basic compatibility layer.

#### ERC004

Two `power-output` endpoints on the same closed local net.

ERROR.

#### ERC005

Multiple `tri-state` drivers.

WARN / NOT_EVALUATED, not automatic PASS.

#### ERC006

Multiple `open-collector` endpoints.

WARN; external bias/network semantics not automatically proven.

#### ERC007

Connected `no-connect`.

ERROR.

#### ERC008

Input-only local net.

WARN unless another explicit hierarchy/interface source explains it.

---

### 33. Placement Strategy Fixtures

These fixtures should validate deterministic **policy outcomes**, not attempt to prove one globally optimal layout.

#### PLC001 — Existing valid placement preserved

Add one unrelated component to an existing validated page.

Unaffected component coordinates remain unchanged.

#### PLC002 — Explicit anchor priority

User-fixed connector and principal IC remain anchors while support components move around them.

PASS.

#### PLC003 — Semantic grouping beats compactness

Two legal placements exist; one is smaller but creates an avoidable functional crossing.

Choose the semantically clearer candidate.

#### PLC004 — Names cannot create connectivity

`RESET_N` label/name exists but no semantic net says it connects to a reset source.

Placement may use the name as a weak hint but must not create a connection.

#### PLC005 — Explicit differential pair preference

Pair metadata exists.

Placement preserves a coherent exit/arrival region for both pair members.

#### PLC006 — No pair metadata

Names look like `D+` / `D-` but no semantic pair is declared.

Agent must not elevate this to verified differential semantics.

#### PLC007 — Explicit decoupling relation

Component metadata/circuit intent identifies a capacitor as decoupling for a power pin group.

Near placement is preferred.

#### PLC008 — Generic capacitor

No decoupling intent exists.

Agent must not invent the role solely from capacitance or proximity.

#### PLC009 — Major-grid tie-break

Two semantically equivalent positions exist.

Stable major-grid / ID tie-break selects one deterministically.

#### PLC010 — Local repair

One newly introduced collision can be solved by moving one affected support component.

Do not globally rearrange the sheet.

---

### 34. Documentation Tests

Add tests proving:

```text
pin semantics normative owner exists and is indexed
component model links pin semantics owner
aixlib reference links pin semantics owner
pins-and-ports cannot claim presentation metadata as semantic authority
create-library-part guide links pin semantics owner
place-components guide links placement/grid/layout/component/net owners
select-library-part guide exists and stays within guide size limit
modify-existing-schematic guide exists and states minimal-diff behavior
guide index links every P0 guide exactly once
create-schematic can reach place-components without repository-wide search
route budgets remain within configured limits
AGENTS remains concise
no competing normative placement strategy owner is introduced
no simulation capability is claimed
no full ERC capability is claimed
```

---

## PART VI — IMPLEMENTATION PHASES

### 35. Phase 0 — Freeze 0.5.9 Baseline

Record:

- component-library schema digest;
- current port type vocabulary;
- current component examples;
- task guide index;
- create-schematic route packet;
- placement/grid contracts;
- protected renderer/viewer outputs;
- current validation claims.

---

### 36. Phase 1 — Publish Pin Electrical Semantics Profile

Add the single normative owner.

Define:

- electrical behavior axis;
- metadata profile;
- token rules;
- internal consistency;
- provenance/review relation;
- simulation boundary.

Update metadata/index/traceability.

---

### 37. Phase 2 — Implement Pin Semantic Validator

Add validation for:

- profile shape;
- token syntax;
- polarity consistency;
- pair closure;
- no-connect contradiction;
- alternate-function structure;
- source-review completeness.

Do not add a solver.

---

### 38. Phase 3 — Add Bounded Compatibility Precheck

Implement only the clearly supportable static cases.

Report uncertain topologies as `WARN` or `NOT_EVALUATED`.

Do not use false `PASS` defaults.

---

### 39. Phase 4 — Create Placement Strategy Guide

Add `place-components.md`.

Ensure:

- Tier A/B/C evidence hierarchy;
- anchor strategy;
- local-edit preservation;
- functional grouping;
- route-channel reservation;
- pin-semantics-aware preferences;
- deterministic tie-break;
- no connectivity inference.

---

### 40. Phase 5 — Add Selection and Existing-Edit Guides

Add:

```text
select-library-part.md
modify-existing-schematic.md
```

Keep each task guide below the existing hard size ceiling.

Do not create new execution routes unless later testing proves route-level separation necessary.

---

### 41. Phase 6 — Repair Route Chaining

Update route/reference links so:

```text
create-library-part
    -> pin semantics

create-schematic
    -> select existing part when needed
    -> place components
    -> route nets

validate-project
    -> pin semantic + compatibility outcomes
```

Preserve retrieval budgets.

---

### 42. Phase 7 — Update Examples

Add or update a small number of current agent-visible examples:

1. active-low reset pin;
2. differential pair;
3. mixed power/digital IC;
4. MCU alternate-function pin metadata;
5. deterministic placement example;
6. local-edit preservation example.

Do not create a large vendor-part corpus.

---

### 43. Phase 8 — Regenerate Derived Documentation

Regenerate:

- document indexes;
- route indexes;
- task packets;
- requirement traceability;
- documentation site;
- reference packs;
- relationship audit;
- validation evidence.

---

### 44. Phase 9 — Full Regression

Run inherited:

- repository/document tests;
- authoring route tests;
- schema/binding tests;
- symbol corpus;
- hierarchical corpus;
- Reference Viewer corpus;
- pre-live authoring harness;
- deterministic render checks;
- protected technical hash checks.

Pin semantic changes must not alter existing renderer output for unchanged source inputs.

---

### 45. Phase 10 — Five Clean Verification Passes

After the last fix, perform five independent clean passes.

Each pass must include:

```text
fresh generated-output cleanup
documentation build
route/task-packet build
pin semantic fixtures
compatibility prechecks
placement policy fixtures
existing regression suites
deterministic render checks
relationship/traceability audit
```

If a new defect is discovered:

```text
repair smallest owner
-> reset consecutive pass count
-> restart 5-pass verification
```

---

## PART VII — ACCEPTANCE CRITERIA

### 46. Pin Semantics

- [ ] Existing stable component port IDs remain endpoint authority.
- [ ] Existing `port.type` remains the electrical-behavior axis.
- [ ] `metadata.pinSemantics` has an explicit profile version.
- [ ] `signalClass` is separately represented.
- [ ] functional tags use stable lower-kebab tokens.
- [ ] polarity is explicit and separate from `type`.
- [ ] differential-pair membership is explicit and validated.
- [ ] optional power-domain hints do not replace actual nets or voltage properties.
- [ ] alternate functions do not create extra physical endpoints.
- [ ] source-backed components require review for detailed pin semantics.
- [ ] no-connect contradictions fail.
- [ ] no universal pin-function taxonomy is introduced.
- [ ] no solver-specific values are added to the base pin-semantics profile.

### 47. ERC Preparation

- [ ] obvious output/output conflicts are detected.
- [ ] power-source conflicts are detected at the bounded static layer.
- [ ] uncertain tri-state/open-collector/bidirectional cases remain warnings or unevaluated.
- [ ] input-only nets are not falsely declared correct.
- [ ] compatibility results do not claim electrical safety or simulation correctness.
- [ ] `render PASS` remains independent from electrical compatibility.

### 48. Placement Strategy

- [ ] `place-components.md` exists.
- [ ] placement guide is informative, not a second geometry authority.
- [ ] semantic closure precedes placement.
- [ ] existing valid placements are preserved by default during edits.
- [ ] explicit anchors are placed before low-priority support parts.
- [ ] functional grouping requires evidence.
- [ ] Tier C names cannot create semantic facts.
- [ ] pin groups are considered, not just body-center alignment.
- [ ] routing channels are reserved before dense packing.
- [ ] compactness is lower priority than readability and route feasibility.
- [ ] differential/power/analog placement preferences require explicit semantics.
- [ ] final tie-breaking is deterministic.
- [ ] placement strategy never changes net membership.

### 49. Agent Documentation

- [ ] `select-library-part.md` exists.
- [ ] existing-part selection uses semantic/provenance identity, not symbol appearance.
- [ ] `modify-existing-schematic.md` exists.
- [ ] existing-edit guidance enforces smallest affected authority region.
- [ ] wide redraw is not silently performed during a local edit.
- [ ] no separate power-domain guide is added without evidence.
- [ ] no separate ERC guide overclaims capability.
- [ ] no simulation task guide is added before simulation contracts exist.
- [ ] guide index remains compact and route-budget compatible.

### 50. Compatibility

- [ ] no core file-format URI/version bump is required.
- [ ] old components without `pinSemantics` remain readable.
- [ ] absence of new metadata does not corrupt historical libraries.
- [ ] new semantic-ready complex electronics may be held to stronger authoring/profile requirements.
- [ ] unchanged authoritative inputs produce unchanged render/viewer outputs.
- [ ] current provenance/part-integrity rules remain intact.

---

## PART VIII — PRIORITY

### 51. P0

Complete before expanding AIXEM toward simulation or stronger live-agent authoring:

1. Pin Electrical Semantics Profile.
2. Pin semantic validation.
3. Bounded electrical compatibility precheck.
4. `place-components.md`.
5. `select-library-part.md`.
6. `modify-existing-schematic.md`.
7. create-library-part / create-schematic / validate-project integration.
8. route/reference chaining.
9. focused fixtures.
10. five clean verification passes.

### 52. P1

Only after Agent evaluation evidence:

- richer placement-candidate scoring tool;
- route-length-aware placement suggestion;
- explicit power-domain authoring guide;
- sheet-boundary planning guide;
- repeated-stage reuse guide;
- more detailed ERC rule families.

### 53. P2 — Separate Future Architecture

Do not absorb these into 0.5.10:

- full ERC engine;
- SPICE/IBIS/Verilog-A binding contract;
- simulation IR;
- simulation model terminal mapping;
- parameter mapping;
- waveform/stimulus definition;
- DC/AC/transient directives;
- simulation result model;
- global auto-placement optimizer;
- placement/routing solver;
- PCB placement/routing;
- signal-integrity/timing analysis.

---

## 54. Definition of Done

0.5.10 is complete when an Agent can follow this semantic chain:

```text
datasheet / generic intent
    -> component port identity
    -> electrical port.type
    -> pinSemantics
    -> presentation binding
    -> source-bound review
```

and then use those semantics in a schematic authoring chain:

```text
select/create component
    -> close semantic connectivity
    -> place-components strategy
    -> deterministic .aixlayout placement
    -> route-nets
    -> render-review
    -> validate-project
```

without taking the following invalid shortcuts:

```text
pin name -> invented electrical meaning
symbol position -> endpoint identity
visual proximity -> semantic connection
compact layout -> better circuit
capability -> active function
render PASS -> ERC PASS
ERC precheck -> simulation correctness
metadata -> solver model
```

The target quality statement is:

> **AIXEM 0.5.10 should give an AI Agent enough explicit pin semantics to reason about electrical role, functional intent, polarity, differential pairing, and bounded compatibility, and enough placement strategy to build or modify a readable deterministic schematic without inventing connectivity or globally rearranging valid work. The release must improve future ERC/simulation readiness while deliberately stopping before solver-specific simulation contracts or global auto-layout.**

---

# INTEGRATED IMPLEMENTATION ORDER

## I1 — Freeze and inventory the active implementation baseline

Capture:

- authoritative source hashes;
- schema/profile versions;
- current route/task-packet budgets;
- current library paths;
- current grid and symbol-profile values;
- existing examples/generators;
- protected renderer/Viewer outputs;
- current claim/evidence state.

## I2 — Establish canonical library and component-integrity authority

Implement Track A library layout, naming, new-vs-existing path semantics, component provenance, placeholder, semantic-clone, and validation-claim contracts.

## I3 — Consolidate grid and symbol construction rhythm

Implement G/P/M authority, outward body quantization, repeated pin-group envelope, placement-grid coherence, deterministic snap, and bounded magnetic alignment.

## I4 — Establish and chain the task-guide façade

Create/update:

```text
docs/authoring/guides/
    create-library-part.md
    select-library-part.md
    create-schematic.md
    place-components.md
    route-nets.md
    compose-project.md
    modify-existing-schematic.md
    author-component-circuit.md
    render-review.md
    validate-project.md
```

Keep guide size and retrieval budgets bounded.

## I5 — Publish Pin Electrical Semantics Profile

Add the normative pin-semantics owner and integrate it with:

- Component Model;
- `.aixlib.json`;
- Pins/Ports/Endpoint Mapping;
- part semantic review;
- Agent symbol-generation guidance.

## I6 — Implement semantic validation and bounded compatibility

Implement:

- pin profile validation;
- polarity and pair consistency;
- no-connect contradictions;
- source-review completeness;
- conservative compatibility outcomes.

Do not claim full ERC.

## I7 — Implement Agent placement strategy

Wire explicit evidence hierarchy, anchor selection, functional grouping, pin-group alignment, routing-channel reservation, route-feasibility review, local refinement, and deterministic tie-breaking.

Preserve existing valid placement by default during edits.

## I8 — Repair route/retrieval integration

Ensure each common authoring task reaches only the necessary guide and canonical owners within the existing route limits.

## I9 — Update generator-owned examples and focused fixtures

Teach the canonical library structure, pin semantics, and placement strategy through current examples while retaining explicit compatibility fixtures.

## I10 — Regenerate all derived products

Regenerate indexes, task packets, reference packs, documentation site, traceability, relationship audit, example outputs, and release evidence.

## I11 — Full regression

Run all inherited suites plus the new:

```text
G / LBY / PRT
PIN / ERC / PLC
documentation / route-budget
deterministic render
protected technical hash
```

checks.

## I12 — Five clean verification passes

After the final fix:

1. clean derived outputs;
2. rebuild/regenerate;
3. run focused new tests;
4. run all inherited regression;
5. run documentation/relationship/traceability audit;
6. verify deterministic outputs.

Any newly found defect resets the consecutive-pass count to zero.

---

# INTEGRATED ACCEPTANCE SUMMARY

The integrated 0.5.2 plan is complete only when all source-plan acceptance requirements are satisfied together and the system can truthfully state:

```text
canonical project-library root                  complete
library first-level domain classification       complete
lower-level naming/reuse discipline             complete
new-vs-existing path behavior                   complete
component provenance / source-or-placeholder    complete
geometry-only semantic ID cloning               prohibited
grid authority                                  complete
G/P/M symbol sizing rhythm                      complete
deterministic placement assist                  complete
task-oriented Agent guide chain                 complete
pin electrical behavior axis                    complete
extended pin semantic profile                   complete
differential/polarity/function semantics        complete
bounded electrical compatibility precheck       complete
Agent strategic placement guidance              complete
existing schematic minimal-diff guidance        complete
existing library-part selection guidance        complete
render-vs-semantic claim separation             complete
part semantic review                            complete
circuit-intent review                           complete
full ERC engine                                 intentionally absent
global auto-layout solver                       intentionally absent
simulation binding / solver                     intentionally future work
universal parts taxonomy                        intentionally absent
```

---

# FINAL DEFINITION OF DONE

AIXEM 0.5.2 is complete when a fresh Agent can execute this chain without repository-wide guessing:

```text
task intent
    -> bounded guide retrieval
    -> source-backed or explicitly generic/placeholder component identity
    -> stable component ports
    -> electrical port.type
    -> optional source-reviewed pinSemantics
    -> symbol sizing and presentation binding
    -> semantic net closure
    -> evidence-based component placement
    -> grid-legal routing
    -> deterministic render
    -> structural validation
    -> part semantic review
    -> bounded electrical compatibility result
    -> circuit-intent review
```

and when an existing valid schematic can be modified through the smallest necessary authority region without silent global redraw.

The release quality bar is:

> **AIXEM 0.5.2 must make reusable part authoring, pin semantics, placement decisions, routing preparation, and validation claims deterministic enough for an AI Agent to operate without inventing paths, component identities, electrical meaning, functional relationships, or correctness claims. It must preserve the distinction between semantic authority and presentation, between advisory placement and authoritative layout, and between structural validity, part correctness, bounded electrical compatibility, and future simulation capability.**
