# AIXEM 0.5.2 — Symbol Expressiveness Conformance & Conservative CAD Compatibility Plan

**Target release:** AIXEM 0.5.2 candidate  
**Plan status:** Implementation-ready  
**Baseline:** AIXEM 0.5.1 (2026-08-11)  
**Primary objective:** Prove, with executable evidence, that the current AIXEM symbol model can represent a broad and practically useful range of EDA schematic symbols, while introducing only narrowly justified, backward-compatible extensions when a real corpus case demonstrates a modeling gap.  
**Secondary objective:** Define a separate, deliberately limited Static 2D Block Compatibility Profile for non-interactive CAD-style blocks without claiming DWG/DXF-native compatibility or AutoCAD Dynamic Block behavior.  
**Documentation language:** English only.

---

## 1. Executive Summary

AIXEM 0.5.1 already provides the essential foundation for AI-oriented symbol authoring:

- a route-first agent workflow;
- a documented renderer contract;
- a measurable symbol design profile;
- deterministic `.aixsym → renderer → SVG / resolved-scene` behavior;
- semantic component-to-symbol binding through `portMap` and `fieldMap`;
- parameters, variants, reusable definitions, predicates, and deterministic placement transforms;
- the graphic primitives `group`, `use`, `line`, `polyline`, `polygon`, `rect`, `circle`, `ellipse`, `arc`, `path`, `text`, `image`, and `dimension`;
- executable authoring examples and visual-repair evidence.

The next weakness is therefore not a lack of primitive breadth. It is an **evidence gap**.

AIXEM can plausibly express most conventional schematic symbol shapes, but a strong engineering claim should not be based only on schema inspection or renderer design. It should be based on a controlled, repeatable corpus that exercises the difficult cases and records exactly what passed, what failed, and why.

AIXEM 0.5.2 should therefore be an **expressiveness-conformance release**, not a broad feature-expansion release.

The preferred workflow is:

```text
Freeze 0.5.1 behavior
        ↓
Define conformance claims and exclusions
        ↓
Build representative symbol corpus
        ↓
Generate minimal test projects through existing production pipeline
        ↓
Validate schema / ports / fields / geometry / deterministic render
        ↓
Inspect visual evidence
        ↓
Classify failures
        ↓
Fix authoring/documentation first
        ↓
Extend core format only when a genuine modeling gap is proven
        ↓
Re-run corpus and legacy regression
        ↓
Publish evidence-backed capability matrix
```

The release should explicitly avoid the following failure mode:

```text
A difficult reference symbol appears
→ add a new primitive immediately
→ renderer and schema grow
→ authoring surface becomes harder for agents
→ long-term compatibility burden increases
```

Instead:

```text
A difficult reference symbol appears
→ attempt composition with existing primitives
→ verify path/group/use/parameter/variant solutions
→ classify whether the issue is documentation, authoring, renderer, or model semantics
→ add a new core capability only if the current model cannot represent the required meaning cleanly
```

This preserves AIXEM's current advantage: a relatively small, deterministic, AI-authorable graphics model.

---

## 2. Baseline Assessment

### 2.1 What 0.5.1 already proves

The 0.5.1 baseline already demonstrates several important capabilities:

1. **Basic schematic geometry** through lines, rectangles, circles, arcs, polygons, ellipses, and paths.
2. **Complex vector geometry** through compound path commands.
3. **Reusable geometry** through definitions and `use`.
4. **Deterministic presentation alternatives** through variants.
5. **Parameterized geometry** through typed parameter values and numeric expressions.
6. **Conditional presentation** through `visibleWhen`.
7. **Semantic-to-graphic binding** through a total component-port-to-symbol-port `portMap`.
8. **Field binding and overrides** through `fieldMap`, semantic attributes, and placement overrides.
9. **Electrical attachment independent from visible geometry** through symbol ports and visible lead geometry.
10. **Deterministic output evidence** through SVG, workbench output, and `resolved-scene.json`.

This means 0.5.2 should not redesign the core authoring model unless the corpus demonstrates a specific deficiency.

### 2.2 What 0.5.1 does not yet prove

The current examples are useful authoring examples, but they are not yet a systematic expressiveness conformance suite.

The unresolved questions include:

- Can the current model represent both IEC-style and ANSI-style passive symbols without special cases?
- Can complex transistor, transformer, relay, switch, and vacuum-tube shapes be authored without renderer-specific code?
- Can high-pin-count symbols remain manageable and deterministic at 64–100+ ports?
- Can dense field and pin-label layouts be validated consistently?
- Can irregular curves and compound path geometry be authored without introducing a new primitive?
- Can reusable subgeometry reduce complexity for repeated structures?
- Can declarative parameters and variants cover legitimate static graphical alternatives without changing endpoint identity?
- Does the current component model support a true independently placeable multi-unit device, or would that require a semantic extension?
- Which AutoCAD-like static 2D block features can be supported honestly without implying Dynamic Block or native DWG compatibility?

### 2.3 Important distinction: graphics expressiveness versus EDA semantics

The corpus must distinguish two different questions:

```text
Can AIXEM draw the shape?
```

and:

```text
Can AIXEM model the electrical/component semantics of that device correctly?
```

A symbol may be graphically reproducible while exposing a semantic gap. Multi-unit FPGA/gate packages are the most important anticipated example.

This distinction must remain visible in all conformance results.

---

## 3. Conservative Engineering Principles

### 3.1 Evidence before expansion

No new primitive, top-level symbol field, or renderer behavior should be added merely because another CAD/EDA package exposes a similar feature.

A new core capability is justified only when:

1. a controlled corpus case cannot be represented correctly with the current model;
2. the failure is not caused by insufficient documentation or a poor authoring recipe;
3. existing primitives cannot represent the geometry without an unreasonable or semantically misleading workaround;
4. at least one real engineering use case is blocked;
5. the proposed capability is vendor-neutral;
6. backward compatibility can be preserved;
7. deterministic rendering and validation remain straightforward.

### 3.2 Prefer composition over primitive growth

The expected preference order is:

```text
existing primitive
→ primitive composition
→ group / definition / use
→ path
→ parameter / visibleWhen
→ variant
→ only then consider schema or renderer extension
```

### 3.3 Do not confuse variants with semantic units

A variant is a graphical/presentation alternative whose endpoint identity remains invariant.

A multi-unit device may expose independently placeable subparts with different port subsets. If this requirement cannot be represented without violating endpoint identity, the corpus must report a model gap rather than forcing the behavior into `variant`.

### 3.4 No vendor-native compatibility claim

0.5.2 must not claim:

- KiCad native file compatibility;
- OrCAD native library compatibility;
- DWG/DXF round-trip compatibility;
- AutoCAD Dynamic Block compatibility;
- exact visual identity with a vendor's default library;
- support for every vendor-specific edge case.

The release may claim only what the AIXEM corpus demonstrates.

### 3.5 No proprietary reference asset dependency

The corpus must use self-authored, vendor-neutral reference geometry.

Do not ship:

- copied vendor library files;
- proprietary symbol assets;
- vendor screenshots as pixel baselines;
- reverse-engineered native-format fixtures unless separately licensed and explicitly in scope.

Reference categories may correspond to common industry symbol families, but the corpus itself should remain AIXEM-authored.

### 3.6 Critical conformance is pass/fail, not averaged

Do not hide a critical semantic failure behind an aggregate score.

A Core case passes only when all mandatory gates pass.

---

## 4. Release Scope

### 4.1 P0 — Required release scope

1. Define Symbol Expressiveness Conformance Profile 1.
2. Build a 24-case Core corpus.
3. Add a corpus manifest and case metadata schema outside the core AIXEM format.
4. Add a batch harness that uses the existing production renderer.
5. Validate schema, bindings, ports, field resolution, design-profile rules, deterministic rendering, and visual review evidence.
6. Generate a machine-readable capability matrix.
7. Publish exact claim language and exclusions.
8. Run all 0.5.1 regression tests unchanged.

### 4.2 P1 — Conservative extended scope

1. Add five complex/edge symbol cases.
2. Add one multi-unit capability probe.
3. Define Static 2D Block Compatibility Profile 1.
4. Add a small 5–6 case static-block corpus.
5. Improve authoring documentation only where corpus failures show a repeatable need.

### 4.3 P2 — Conditional scope only

P2 is not pre-authorized implementation work.

It may begin only when P0/P1 evidence proves a real gap.

Potential examples:

- minimal multi-unit component semantics;
- a narrowly scoped text capability required by multiple corpus cases;
- a missing transform/style behavior that cannot be expressed by current structures.

P2 must not include speculative CAD feature accumulation.

---

## 5. Non-Goals

The following remain explicitly outside 0.5.2:

- AutoCAD Dynamic Block action graphs;
- interactive stretch/move/flip/lookup action chains;
- grip editing semantics;
- general geometric or parametric constraint solver;
- 3D solid, mesh, B-rep, surface, or BIM object representation;
- DWG/DXF import/export;
- KiCad/OrCAD native import/export;
- SPICE model compatibility work;
- PCB footprint representation;
- automatic symbol recognition from screenshots;
- vendor-specific default library cloning;
- broad font engine replacement;
- visual AI scoring in CI;
- automatic symbol synthesis from arbitrary CAD files.

These exclusions are deliberate. They keep the release focused on evidence-backed 2D schematic expressiveness.

---

## 6. Conformance Claim Model

AIXEM should publish distinct capability levels instead of one broad compatibility statement.

### 6.1 Level S-Core — Schematic Symbol Expressiveness Core

Requirements:

- all 24 Core corpus cases pass;
- zero schema errors;
- zero unresolved component-port mappings;
- zero mapped hidden ports;
- all required lead/port coincidence rules pass;
- deterministic render digests pass;
- no unsupported required graphic feature is used;
- required visual-review checklist passes for every case.

Permitted claim:

> AIXEM demonstrates conformance against its representative Core schematic-symbol expressiveness corpus using the production `.aixsym` and renderer pipeline.

Not permitted:

> AIXEM is fully KiCad compatible.

or:

> AIXEM supports every OrCAD symbol.

### 6.2 Level S-Extended — Extended Symbol Expressiveness

Requirements:

- S-Core passes;
- all five complex/edge cases pass;
- complex path and repeated-geometry cases remain deterministic;
- no core schema extension is required solely for visual mimicry.

This level demonstrates broader graphical range, not vendor-native compatibility.

### 6.3 Level MU — Multi-Unit Device Capability

Multi-unit support should receive a separate result:

```text
PASS
PARTIAL
NOT SUPPORTED
```

It must not be implied by S-Core or S-Extended.

A true PASS requires independently placeable units that share one component identity without corrupting semantic endpoint ownership.

### 6.4 Level B2D — Static 2D Block Profile

This is a separate profile for non-interactive 2D block geometry.

It must explicitly exclude Dynamic Block runtime behavior and native DWG semantics.

---

## 7. Symbol Expressiveness Corpus

### 7.1 Corpus architecture

Recommended structure:

```text
validation/corpus/
└── symbol-expressiveness-1/
    ├── README.md
    ├── manifest.json
    ├── schema/
    │   └── corpus-case-1.schema.json
    ├── cases/
    │   ├── S001-resistor-iec/
    │   │   ├── case.json
    │   │   └── symbol.aixsym.json
    │   ├── S002-resistor-ansi/
    │   └── ...
    ├── expected/
    │   ├── geometry-signatures/
    │   └── approved-render-digests.json
    └── results/
        ├── corpus-results.json
        ├── capability-matrix.json
        ├── render-digests.json
        └── visual-review.json
```

Do not store redundant hand-maintained `.aixem`, `.aixlib`, and `.aixlayout` projects for every symbol unless a case genuinely requires custom semantics.

Instead, the harness should generate a minimal synthetic project wrapper from `case.json` and feed that wrapper to the existing production validation/rendering path.

This minimizes fixture duplication while testing the real renderer.

### 7.2 Core corpus — 24 mandatory cases

#### Group A — Passive geometry

| ID | Case | Primary purpose |
|---|---|---|
| S001 | IEC resistor | rectangular body, straight leads, basic fields |
| S002 | ANSI resistor | repeated zig-zag geometry, polyline/path economy |
| S003 | non-polar capacitor | parallel plates, symmetric ports |
| S004 | polarized capacitor | arc/curved plate plus polarity marking |
| S005 | inductor | repeated curved coil geometry, definition/use or path |

#### Group B — Semiconductor geometry

| ID | Case | Primary purpose |
|---|---|---|
| S006 | standard diode | polygon/line composition and two-port alignment |
| S007 | LED | diode body plus repeated emission arrows |
| S008 | Zener/TVS | non-trivial terminal edge geometry and variant suitability |
| S009 | NPN BJT | multi-lead transistor geometry, arrow orientation |
| S010 | N-channel MOSFET | internal multi-line geometry, gate separation, arrow/body detail |

#### Group C — Analog and electromechanical

| ID | Case | Primary purpose |
|---|---|---|
| S011 | op-amp | triangular body, grouped input/output/power ports |
| S012 | comparator | op-amp-like body with different field/port policy |
| S013 | transformer | repeated windings, optional core lines, four or more ports |
| S014 | SPDT relay | coil plus mechanically associated contact geometry |
| S015 | normally-open push switch | simple movable-contact geometry |
| S016 | 1P4T rotary switch | arc/circle plus radial contact arrangement |

#### Group D — Digital logic

| ID | Case | Primary purpose |
|---|---|---|
| S017 | NAND gate | curved logic body plus inversion bubble |
| S018 | Schmitt inverter | inversion bubble plus internal hysteresis marking |

#### Group E — Scale and pin density

| ID | Case | Primary purpose |
|---|---|---|
| S019 | 2-pin connector | minimal connector baseline |
| S020 | 20-pin connector | repeated pins, deterministic numbering and pitch |
| S021 | 100-pin connector | high port count and repeated geometry stress |
| S022 | 32-pin MCU | functional port grouping and field layout |
| S023 | 64-pin MCU | medium-high density and body scaling |
| S024 | 100-pin MCU | high density, label layout, renderer scalability |

### 7.3 Extended corpus — five complex cases

| ID | Case | Purpose |
|---|---|---|
| S025 | JFET | additional transistor topology and arrow/detail handling |
| S026 | crystal / oscillator | mixed rectangular/parallel-line timing symbol geometry |
| S027 | optocoupler | multi-body internal relationship without semantic ambiguity |
| S028 | vacuum tube triode/pentode class | complex curves and internal electrodes |
| S029 | irregular custom company symbol | compound path, reusable geometry, unusual silhouette |

### 7.4 Multi-unit probe — one isolated case

| ID | Case | Purpose |
|---|---|---|
| S030 | FPGA / large multi-unit package | determine whether independently placeable units sharing one semantic component identity are representable correctly |

S030 is deliberately not an ordinary graphical pass/fail case.

It must answer:

1. Can units be placed separately?
2. Do all units share one component identity/reference correctly?
3. Can each unit expose a declared subset of ports?
4. Can units have distinct graphics without abusing variants?
5. Are net endpoints unambiguous?
6. Does the resolved scene preserve the shared identity?
7. Can validation detect duplicate or omitted unit ports?

If the answer is no, record a capability gap. Do not fake a pass with duplicated component entities unless the model explicitly defines that as valid behavior.

---

## 8. Case Contract

Every corpus case should define a compact, machine-readable contract.

Suggested `case.json` fields:

```text
id
category
tier
purpose
symbolPath
componentPorts
expectedPortCount
expectedVisiblePortCount
requiredCapabilities
optionalCapabilities
expectedFieldRoles
expectedBoundsClass
expectedGridPolicy
expectedVariantIds
expectedParameterIds
expectedPrimitiveFamilies
manualReviewChecks
knownExclusions
```

The corpus case schema is a **validation-fixture schema**, not a new AIXEM production format.

### 8.1 Required capabilities vocabulary

Use a small fixed vocabulary such as:

```text
geometry.line
geometry.polyline
geometry.polygon
geometry.rect
geometry.circle
geometry.ellipse
geometry.arc
geometry.path
structure.group
structure.use
parameter.numeric
variant.graphics
visibility.predicate
text.field
port.mapping
port.transform
style.named
scale.high-port-count
```

Do not create vendor-specific capability names.

### 8.2 Geometry signature

For each rendered case, derive a normalized geometry signature from the resolved scene and SVG:

- symbol bounds;
- transformed port coordinates;
- primitive counts by family;
- field anchors;
- variant/parameter resolution;
- number of definitions/use expansions;
- required feature set;
- canonical SVG digest.

The signature should be stable enough to detect accidental renderer drift without requiring raster pixel comparison.

---

## 9. Validation Harness

### 9.1 Reuse the production pipeline

The harness must not introduce a second simplified symbol renderer.

For each case:

```text
case.json + symbol.aixsym.json
        ↓
synthetic component/library wrapper
        ↓
synthetic semantic entity
        ↓
synthetic placement/layout
        ↓
existing project validator
        ↓
existing renderer
        ↓
SVG + resolved-scene
        ↓
corpus-specific assertions
```

This is critical. A corpus rendered by a special test renderer would prove the test renderer, not the AIXEM production path.

### 9.2 Recommended tooling

Add thin orchestration only:

```text
tools/validate_symbol_corpus.py
tests/conformance/test_symbol_expressiveness_corpus.py
```

Avoid adding multiple overlapping CLIs unless needed.

The tool should support:

```text
--case S014
--tier core
--all
--update-approved-digests
--emit-report
```

Updating approved digests must be an explicit operation, never an automatic side effect of normal tests.

### 9.3 Validation stages

Each case passes through the following stages:

#### Stage A — Static validity

- JSON parses;
- symbol validates against the active schema;
- all required features are declared;
- no remote/unlocked asset dependency exists;
- case metadata validates.

#### Stage B — Binding validity

- component ports are unique;
- `portMap` is total for required component ports;
- every target symbol port exists;
- mapped required ports resolve visible;
- field bindings resolve;
- selected variants and parameters are valid.

#### Stage C — Geometry validity

- required grid rules pass;
- visible pin lead endpoints coincide with electrical port coordinates where applicable;
- body and port bounds are sane;
- no unsupported transform is required;
- no obviously invalid zero-length or degenerate geometry occurs unless intentional.

#### Stage D — Renderer validity

- project resolves without error;
- SVG is produced;
- `resolved-scene.json` is produced;
- expected port count matches;
- expected fields appear;
- expected primitive families are present.

#### Stage E — Determinism

Render the same case repeatedly under the controlled environment.

Required:

```text
resolved-scene digest: identical
canonical SVG digest: identical
```

At least three repeated renders should be used in release verification.

#### Stage F — Visual review

Human review remains required for symbol-specific legibility that mechanical rules cannot reliably judge.

The review should be structured, not subjective free-form commentary.

---

## 10. Visual Review Checklist

Every case should record explicit visual review items.

Minimum checklist:

- [ ] silhouette is recognizable for the intended device class;
- [ ] ports are visually attached to the expected leads;
- [ ] pin numbers do not collide with pin names;
- [ ] reference/value fields do not obscure the body;
- [ ] polarity, arrow, inversion, or switch state marks are unambiguous;
- [ ] repeated geometry is evenly spaced;
- [ ] high-pin-count bodies remain readable at normal schematic scale;
- [ ] no decorative detail suggests false connectivity;
- [ ] variant differences are graphical and do not silently change endpoint identity;
- [ ] unusual path geometry does not produce self-intersection/fill artifacts.

Visual review evidence should identify the reviewer, case, source digest, render digest, date, and result.

Do not use a 95% average to pass the release. A required case with a critical readability or connectivity defect fails until corrected.

---

## 11. Performance and Scale Policy

High-pin-count corpus cases should record performance, but 0.5.2 should avoid arbitrary absolute performance promises before a baseline is measured.

Record per case:

- source symbol size;
- primitive count;
- visible port count;
- resolved primitive count;
- render duration;
- validation duration;
- resolved-scene size;
- SVG size.

For the first 0.5.2 baseline, publish observed values.

For subsequent releases, enforce regression thresholds relative to the approved baseline, for example:

```text
no unexplained >25% regression in corpus batch render time
no unexplained >25% regression in resolved output size
```

Exact thresholds should be confirmed after measuring the first corpus on the controlled CI environment.

Do not optimize prematurely merely because the 100-pin cases are larger than the existing authoring examples.

---

## 12. Failure Classification

Every corpus failure must be assigned one primary class before any implementation change.

### F1 — Authoring/documentation gap

Example:

- symbol is representable, but the correct use of path or `use` is unclear.

Action:

- improve cookbook/reference;
- add a focused example;
- no schema change.

### F2 — Validator gap

Example:

- invalid lead/port relation is visually wrong but not detected.

Action:

- strengthen lint/conformance check;
- no format change unless necessary.

### F3 — Renderer defect

Example:

- valid path or transform is declared by the schema but rendered incorrectly.

Action:

- fix renderer to match existing contract;
- add regression test.

### F4 — Expressiveness gap

Example:

- the shape cannot be represented cleanly with existing primitives and path semantics.

Action:

- perform extension review under Section 13.

### F5 — Semantic model gap

Example:

- a multi-unit package requires independently placeable units sharing one component identity and current semantics cannot express it.

Action:

- do not treat as a graphics failure;
- open a semantic ADR and compatibility analysis.

### F6 — Out-of-scope vendor behavior

Example:

- an AutoCAD Dynamic Block requires interactive stretch actions.

Action:

- document exclusion;
- no implementation work in 0.5.2.

---

## 13. Core Extension Gate

A new core symbol feature may be added only if all of the following are true:

1. A corpus case is blocked.
2. The blocker is reproduced by an automated test.
3. Existing composition/path/parameter/variant mechanisms are insufficient or materially misleading.
4. The capability is useful beyond one vendor-specific artifact.
5. The proposed syntax is small and declarative.
6. Existing 0.5.1 files remain valid.
7. The renderer can implement the capability deterministically.
8. The capability can be validated mechanically.
9. Documentation and authoring burden remain acceptable for an AI agent.
10. An ADR records the alternatives and rejection rationale.

### 13.1 Primitive addition policy

A new primitive should be especially difficult to justify because `path` is already the generic escape hatch for unusual vector geometry.

A new primitive is reasonable only when it provides at least one of:

- materially safer semantics than a path;
- substantially simpler parameterization for a repeated engineering operation;
- unambiguous validation that a generic path cannot provide;
- significant reduction in authoring complexity across multiple corpus cases.

Otherwise, keep the primitive set unchanged.

---

## 14. Multi-Unit Device Probe and Conditional Minimal Extension

### 14.1 Why multi-unit is special

Multi-unit devices are not simply alternative body styles.

A typical multi-unit component may require:

```text
one physical/semantic component identity
        ↓
unit A placed at location 1 → subset of ports
unit B placed at location 2 → different subset of ports
unit P placed at location 3 → power ports
```

Using `variant` for this would be incorrect if variants are defined to preserve the same endpoint identity and represent alternative presentation states.

### 14.2 0.5.2 default action

Do **not** add multi-unit syntax before running S030.

First determine whether the current component/entity/placement model already supports the requirement without duplication or semantic ambiguity.

### 14.3 If a gap is proven

Open a dedicated ADR before implementation.

The minimal target semantics should satisfy only these requirements:

- one shared semantic component identity;
- one shared reference/value identity;
- independently placeable unit presentations;
- each unit declares the component-port subset it exposes;
- no port may disappear silently;
- duplicate ownership of the same exposed port is either prohibited or explicitly modeled;
- unit selection is not a variant;
- existing single-unit components require no migration.

A likely design family to evaluate is a presentation-level `unit`/`part` selection associated with a placement, but the plan should not commit to field names until the ADR compares alternatives.

### 14.4 Multi-unit acceptance tests if implemented

- dual op-amp package;
- quad NAND package;
- FPGA bank/power split example;
- shared reference/value across units;
- disjoint port subset closure;
- deterministic resolved-scene identity;
- migration-free rendering of all existing 0.5.1 fixtures.

This extension should be released only if it remains small and vendor-neutral.

---

## 15. Static 2D Block Compatibility Profile 1

### 15.1 Purpose

The Static 2D Block Profile provides a precise answer to:

> Which non-interactive CAD-style 2D block characteristics can AIXEM represent using its current graphics model?

It is not a DWG profile.

### 15.2 Included capabilities

Subject to corpus evidence, the profile may include:

- line/polyline/polygon outlines;
- rectangles, circles, ellipses, and arcs;
- compound path geometry;
- reusable definitions and instances;
- affine placement transforms and mirroring supported by the renderer;
- named styles;
- text;
- dimensions;
- supported paint/pattern behavior already present in the format;
- digest-locked local images;
- declarative parameters resolved before rendering;
- declarative variants/visibility states that do not require interactive runtime actions.

### 15.3 Explicit exclusions

The profile must state:

- no Dynamic Block action graph;
- no interactive grip semantics;
- no stretch action;
- no lookup/action dependency engine;
- no general geometric constraints;
- no associative dimension solver;
- no native DWG object identity;
- no native AutoCAD layer/block table round trip;
- no 3D CAD semantics.

### 15.4 Small static-block corpus

Keep this corpus limited to approximately six cases:

| ID | Case | Purpose |
|---|---|---|
| B001 | mechanical mounting plate outline | circle/arc/rect/hole geometry |
| B002 | repeated-hole panel block | definition/use and repeated transforms |
| B003 | architectural/electrical fixture block | mixed line/path geometry at plan scale |
| B004 | annotation/title block | text, line structure, field-like labels |
| B005 | dimensioned 2D outline | dimension primitive and static annotation |
| B006 | irregular logo/mark block | compound path / optional locked raster fallback |

The Static 2D Block Profile should be P1 and must not delay the S-Core schematic-symbol release gate.

---

## 16. Agent Authoring Integration

The corpus should improve AI authoring, not become a separate repository island.

### 16.1 Add a corpus lookup route

Add one route:

```text
validate-symbol-expressiveness
```

Purpose:

- find the nearest representative symbol case;
- inspect its canonical `.aixsym` construction;
- author a new symbol using the current design profile;
- run focused corpus-style validation.

Do not add 30 separate task routes.

### 16.2 Cookbook integration

Extend `docs/symbols/authoring-cookbook.md` with a concise table:

```text
symbol class
→ nearest corpus case
→ preferred construction pattern
→ common failure mode
```

The cookbook should link to corpus cases rather than duplicate their full JSON.

### 16.3 Agent rule: nearest proven pattern first

Add to `AGENTS.md`:

> When authoring a non-trivial symbol, prefer the nearest validated corpus construction pattern before inventing a new graphics structure. Do not add a new primitive or renderer behavior merely to reproduce a familiar vendor-library appearance.

### 16.4 Corpus is evidence, not authority over semantics

Corpus cases remain conformance fixtures. They must not redefine component semantics, renderer precedence, or symbol schema contracts.

Normative authority remains in the existing specification and conformance documents.

---

## 17. Documentation Plan

### 17.1 New canonical documents

Keep new documentation small.

| Path | Role |
|---|---|
| `docs/conformance/symbol-expressiveness.md` | normative conformance levels, corpus rules, claim boundaries |
| `docs/conformance/static-2d-block-profile.md` | normative limited static CAD block profile |
| `docs/examples/symbol-expressiveness-corpus.md` | informative case index and construction notes |

Do not create one documentation page per corpus case unless a case requires significant explanation.

### 17.2 Existing documents to update

| Path | Change |
|---|---|
| `AGENTS.md` | nearest-corpus-pattern rule and expressiveness validation route |
| `docs/symbols/authoring-cookbook.md` | corpus cross-reference table |
| `docs/symbols/primitives.md` | only correct actual gaps discovered by corpus |
| `docs/symbols/symbol-lint.md` | corpus-relevant validation checks |
| `docs/conformance/validation.md` | corpus harness and evidence outputs |
| `docs/conformance/test-suite.md` | new conformance suite |
| `docs/conformance/release-gates.md` | S-Core/S-Extended/MU/B2D gates |
| `docs/conformance/compatibility.md` | precise claim wording and exclusions |
| `docs/_meta/navigation.yaml` | one corpus/conformance entry, not case-level clutter |
| `docs/_meta/routes/validate-project.yaml` | reference symbol corpus where appropriate |

### 17.3 Claim wording policy

Official docs should prefer:

> representative EDA schematic symbol expressiveness corpus

instead of:

> OrCAD-compatible symbol engine

or:

> KiCad-compatible symbol engine

Tool-family names may appear in informative comparison sections, but conformance must be defined by AIXEM's own published corpus and requirements.

---

## 18. File-Level Change Matrix

### P0 additions

```text
validation/corpus/symbol-expressiveness-1/
validation/corpus/symbol-expressiveness-1/schema/corpus-case-1.schema.json
validation/corpus/symbol-expressiveness-1/manifest.json
validation/corpus/symbol-expressiveness-1/cases/S001...S024/
validation/corpus/symbol-expressiveness-1/results/

tools/validate_symbol_corpus.py
tests/conformance/test_symbol_expressiveness_corpus.py

docs/conformance/symbol-expressiveness.md
docs/examples/symbol-expressiveness-corpus.md
docs/_meta/routes/validate-symbol-expressiveness.yaml
```

### P1 additions

```text
validation/corpus/symbol-expressiveness-1/cases/S025...S030/
validation/corpus/static-2d-block-1/
docs/conformance/static-2d-block-profile.md
```

### Conditional P2 additions

Only after an approved ADR:

```text
docs/architecture/adr/0005-<proven-gap>.md
schema/renderer changes strictly required by that ADR
focused migration/compatibility tests
```

No placeholder core feature should be merged merely because it is listed as a possible future gap.

---

## 19. Implementation Sequence

### Phase 0 — Freeze and Baseline

1. Freeze the 0.5.1 symbol schema, renderer contract, symbol design profile, authoring examples, and renderer regression output.
2. Record current schema and renderer digests.
3. Run the full 0.5.1 test suite before corpus work.
4. Inventory which primitive/parameter/variant capabilities are already exercised by existing examples.
5. Create a matrix of capability → existing evidence → missing evidence.

**Exit criterion:** no proposed 0.5.2 feature is justified merely by failing to notice existing 0.5.1 capability.

### Phase 1 — Define Conformance Before Cases

1. Write `symbol-expressiveness.md`.
2. Define S-Core, S-Extended, and MU result rules.
3. Define the case schema.
4. Define allowed and prohibited public claim language.
5. Define manual review evidence format.

**Exit criterion:** the release knows what constitutes a pass before symbols are authored.

### Phase 2 — Build Core Corpus

Implement S001–S024 using current 0.5.1 features only.

For each case:

1. author the symbol;
2. declare required capabilities;
3. create synthetic binding metadata;
4. run existing schema/lint checks;
5. render through production renderer;
6. inspect resolved ports/fields;
7. record geometry signature;
8. perform structured visual review;
9. fix authoring or documentation defects;
10. do not change the core schema during the first attempt.

**Exit criterion:** every Core failure has a classified root cause.

### Phase 3 — Build Corpus Harness

1. Implement batch generation of minimal projects.
2. Reuse existing renderer entry points.
3. Add normalized render digests.
4. Emit per-case and aggregate reports.
5. Add CI test integration.
6. Add explicit approved-digest update workflow.

**Exit criterion:** all Core cases can be regenerated from clean source in one command.

### Phase 4 — Close Core Gaps Conservatively

Process failures in priority order:

```text
F1 documentation/authoring
→ F2 validator
→ F3 renderer defect
→ F4 expressiveness gap
→ F5 semantic gap
→ F6 out of scope
```

Only F4/F5 may open a core extension discussion.

Any proposed change must include:

- blocked cases;
- alternative constructions attempted;
- compatibility analysis;
- authoring complexity impact;
- tests;
- ADR if contract changes.

**Exit criterion:** S-Core either passes or the release explicitly documents a remaining unsupported capability. Do not hide failures.

### Phase 5 — Extended and Multi-Unit Probe

1. Implement S025–S029.
2. Run S030 as a semantic capability probe.
3. Separate graphical expressiveness results from multi-unit semantic results.
4. If S030 fails, create a gap report first.
5. Implement a multi-unit extension only if the gap is important enough and the design remains small.

**Exit criterion:** S-Extended and MU have independent, evidence-backed results.

### Phase 6 — Static 2D Block Profile

1. Define the profile scope.
2. Reuse existing primitives and renderer.
3. Implement B001–B006.
4. Confirm dimensions, transforms, repeated definitions, text, and path behavior.
5. Publish explicit exclusions.

**Exit criterion:** the B2D claim is precise and cannot be misread as Dynamic Block or DWG compatibility.

### Phase 7 — Agent and Documentation Integration

1. Add the corpus validation route.
2. Update authoring cookbook cross-references.
3. Add the nearest-proven-pattern rule to `AGENTS.md`.
4. Add capability matrix to the documentation site.
5. Avoid expanding ordinary `create-symbol` route beyond its context budget.

**Exit criterion:** an agent can locate a relevant proven pattern without loading the full corpus.

### Phase 8 — Release Closure

1. Run corpus from clean checkout.
2. Run all 0.5.1 regressions.
3. Render corpus three times and compare digests.
4. Perform final visual sign-off.
5. Regenerate documentation metadata/site/manifests.
6. Verify no generated result is treated as independent normative authority.
7. Publish a release-specific expressiveness report.

---

## 20. Three-Pass Verification and Error-Improvement Loop

### PASS 1 — Representability and Coverage

Focus:

> Can the current model represent the selected engineering symbol classes without speculative expansion?

Checks:

- Core case count complete;
- every case validates;
- capability tags resolve;
- port mapping complete;
- lead/port geometry valid;
- primitive coverage known;
- all failures classified.

Gate:

```text
Core case inventory                 24/24
Case metadata validity              100%
Schema-valid symbols                100% or documented blocker
Unclassified failures               0
Unsupported required feature drift  0
```

If this pass reveals a problem, fix the smallest owning layer and repeat PASS 1.

### PASS 2 — Visual Quality, Scale, and Agent Usability

Focus:

> Are the symbols not only legal, but useful and maintainable for AI authoring?

Checks:

- visual-review checklist for every Core case;
- 20/100-pin connector readability;
- 32/64/100-pin MCU readability;
- repeated geometry uses reasonable construction patterns;
- complex symbols do not require pathological path data where reusable primitives are clearer;
- agent can reach nearest corpus case through the route system;
- no repository-wide search is needed for ordinary corpus-pattern authoring.

Gate:

```text
Core visual critical defects        0
Mapped-port critical defects        0
Deterministic field resolution      100%
Agent route budget violations       0
Unnecessary renderer source lookup  0 for normal pattern use
```

### PASS 3 — Regression, Determinism, and Claim Integrity

Focus:

> Can AIXEM publish the capability claim without weakening compatibility or overstating scope?

Checks:

- full repository regression;
- repeated corpus render digest comparison;
- approved baseline changes reviewed;
- claim text matches actual passed tiers;
- 0.5.1 fixtures remain valid;
- static 2D block exclusions are present;
- multi-unit result is stated separately;
- package and manifest integrity pass.

Gate:

```text
Full regression                     PASS
Core corpus critical gates          100%
Repeated render determinism          PASS
0.5.1 compatibility                  PASS
Unreviewed golden digest changes    0
Unsupported compatibility claims    0
Release-critical diagnostics        0
```

---

## 21. Acceptance Criteria

### 21.1 S-Core acceptance

- [ ] S001–S024 exist.
- [ ] Every case metadata file validates.
- [ ] Every symbol validates against the active AIXEM symbol schema.
- [ ] Every required semantic port maps to an existing visible symbol port.
- [ ] Applicable visible lead endpoints coincide with electrical ports.
- [ ] Required fields render correctly.
- [ ] Every case renders through the production renderer.
- [ ] Every case emits deterministic `resolved-scene.json`.
- [ ] Every case emits deterministic canonical SVG.
- [ ] Every case has structured visual-review evidence.
- [ ] Zero critical visual/connectivity defects remain.

### 21.2 S-Extended acceptance

- [ ] S025–S029 exist.
- [ ] Complex path/curve geometry renders deterministically.
- [ ] Vacuum-tube/custom-path cases do not require undocumented renderer behavior.
- [ ] No new primitive is introduced unless it passed the Core Extension Gate.

### 21.3 MU acceptance

- [ ] S030 result is published independently.
- [ ] A PASS is claimed only for true shared-identity independently placeable units.
- [ ] Variants are not misused as semantic units.
- [ ] If unsupported, the limitation is documented without weakening other expressiveness claims.

### 21.4 B2D acceptance

- [ ] B001–B006 pass the declared Static 2D Block Profile.
- [ ] Dynamic Block and native DWG behavior remain explicitly excluded.
- [ ] No vendor-specific action semantics are introduced into the core renderer.

---

## 22. Recommended Release Evidence

Generate a dedicated report:

```text
validation/reports/symbol-expressiveness-0.5.2.json
validation/reports/symbol-expressiveness-0.5.2.md
```

Minimum contents:

- release digest;
- active symbol schema digest;
- renderer version/digest;
- corpus version;
- passed/failed case list;
- failure classes;
- capability coverage matrix;
- primitive usage matrix;
- high-port-count metrics;
- deterministic render results;
- visual-review completion;
- S-Core result;
- S-Extended result;
- MU result;
- B2D result;
- explicit exclusions;
- any approved extensions introduced during the release.

The report should allow an external reviewer to see exactly what AIXEM has proven without reading renderer source.

---

## 23. Capability Matrix Output

Generate a concise matrix such as:

```text
Capability                         Evidence cases        Result
-----------------------------------------------------------------
straight/vector primitives         S001-S024             PASS
curved/arc geometry                S004,S005,S016-S018   PASS
compound path geometry             S028,S029             PASS/PENDING
reusable repeated geometry         S005,S007,S020,S021   PASS
parameterized static geometry      selected cases        PASS
variant graphical alternatives     selected cases        PASS
high port count 100                S021,S024             PASS
field/port binding                 all Core              PASS
true independently placed units    S030                  PASS/PARTIAL/NO
static 2D block profile            B001-B006             PASS/PARTIAL
Dynamic Block actions              excluded              NOT IN SCOPE
3D/B-rep                           excluded              NOT IN SCOPE
```

This matrix is more credible than a broad prose compatibility claim.

---

## 24. Risk Analysis

### Risk 1 — Corpus becomes a second standard

Mitigation:

- corpus cases are fixtures;
- normative rules remain in specification/conformance docs;
- case metadata references canonical requirement IDs.

### Risk 2 — Too many examples increase maintenance cost

Mitigation:

- 24 Core + 5 Extended + 1 Probe only;
- synthetic project wrappers instead of duplicated full projects;
- one shared harness;
- generated aggregate reports.

### Risk 3 — Golden SVG digests become brittle

Mitigation:

- canonicalize output before digest;
- require explicit baseline update command;
- pair digest checks with geometry signatures;
- visual approval required only when baseline intentionally changes.

### Risk 4 — Multi-unit work expands the semantic model excessively

Mitigation:

- S030 is a probe, not a pre-approved feature;
- separate ADR required;
- minimal shared-identity requirement only;
- postpone if the design cannot remain small.

### Risk 5 — Vendor comparison turns into compatibility overclaim

Mitigation:

- publish AIXEM-owned conformance levels;
- keep tool-family comparison informative;
- explicitly state no native-format round trip.

### Risk 6 — Primitive proliferation

Mitigation:

- path remains generic complex-shape escape hatch;
- new primitive must satisfy the Core Extension Gate;
- one difficult symbol alone is insufficient justification.

---

## 25. Definition of Done

AIXEM 0.5.2 Symbol Expressiveness work is complete only when:

### Core evidence

- [ ] 24 Core corpus cases are implemented.
- [ ] All Core critical conformance gates pass.
- [ ] Corpus harness uses the production renderer.
- [ ] Capability and primitive-usage matrices are generated.
- [ ] Deterministic rendering is proven through repeated runs.
- [ ] Visual review evidence is complete.

### Conservative extension control

- [ ] No speculative primitive was added.
- [ ] Every core format/renderer extension, if any, is tied to a blocked corpus case.
- [ ] Every contract change has an ADR and compatibility test.
- [ ] Existing 0.5.1 fixtures remain valid.

### Extended evidence

- [ ] Five complex cases have explicit results.
- [ ] Multi-unit capability has an independent result.
- [ ] Unsupported behavior is documented instead of simulated through semantic misuse.

### Static 2D block profile

- [ ] Profile scope is documented.
- [ ] Small B2D corpus is implemented.
- [ ] Dynamic Block, constraints, native DWG, and 3D exclusions are explicit.

### Agent readiness

- [ ] Agent can resolve the nearest proven corpus pattern without repository-wide discovery.
- [ ] Corpus links are integrated into the authoring cookbook.
- [ ] No unnecessary growth of the normal `create-symbol` context route occurs.

### Release integrity

- [ ] Full repository tests pass.
- [ ] Generated reports are deterministic.
- [ ] Manifests include the new corpus and evidence.
- [ ] Public claim text matches only the tiers that actually passed.
- [ ] Final release package contains no proprietary vendor assets.

---

## 26. Recommended Priority

### P0 — Do now

1. conformance profile;
2. 24 Core cases;
3. one production-pipeline corpus harness;
4. geometry/binding/determinism assertions;
5. structured visual review;
6. capability matrix;
7. release claim boundaries;
8. full 0.5.1 regression.

### P1 — Do after Core is stable

1. five complex cases;
2. S030 multi-unit probe;
3. six-case Static 2D Block Profile;
4. small documentation/route integration.

### P2 — Only if proven necessary

1. multi-unit semantic extension;
2. narrowly justified text/geometry capability;
3. additional corpus categories that expose a real uncovered engineering need.

Do not begin P2 merely to increase feature count.

---

## 27. Final Target State

The desired AIXEM relationship after this work is:

```text
                 existing AIXEM 0.5.1 contracts
                            │
                            ▼
                  Symbol Conformance Profile
                            │
             ┌──────────────┼──────────────┐
             │              │              │
          S-Core        S-Extended         MU probe
        24 cases          5 cases          1 case
             │              │              │
             └──────────────┴──────┬───────┘
                                   │
                         production renderer
                                   │
                         resolved-scene + SVG
                                   │
                    automated invariants + review
                                   │
                         capability matrix
                                   │
             ┌─────────────────────┴─────────────────────┐
             │                                           │
   proven schematic-symbol claim             explicit unsupported gaps
             │                                           │
             └─────────────────────┬─────────────────────┘
                                   │
                       conservative extension gate
                                   │
                     only if evidence requires it
```

The key 0.5.2 quality bar is:

> **Do not make AIXEM larger in order to look more capable. Make the existing model prove what it can already do, identify the few places where it genuinely cannot, and extend only those places with the smallest vendor-neutral contract possible.**

This approach gives AIXEM a stronger technical basis for claiming broad schematic-symbol expressiveness while preserving deterministic rendering, AI authoring simplicity, and long-term compatibility.
