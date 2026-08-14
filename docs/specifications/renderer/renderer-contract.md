---
id: AIXEM-SPEC-RENDERER-001
title: Renderer Contract 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines deterministic component presentation selection, field and variant precedence, port transforms, route
  binding, and renderer evidence.
authority:
- renderer-resolution-contract
aliases:
- renderer contract
- field precedence
- variant precedence
agent:
  priority: critical
  estimated_tokens: 1970
  intents:
  - create-symbol
  - create-schematic
  - render-review
  - validate-project
depends_on:
- AIXEM-SPEC-SYMBOL-001
- AIXEM-SPEC-LAYOUT-001
- AIXEM-SPEC-PROJECT-LOCK-001
related:
- AIXEM-SYMBOL-BINDING-001
- AIXEM-AGENT-VISUAL-QA-001
- AIXEM-SPEC-VIEWER-001
- AIXEM-SPEC-WORKBENCH-001
navigation:
  group: specifications
  order: 75
artifacts:
  owns:
  - implementation/schematic/component_core.py
  - implementation/schematic/render_project.py
  consumes:
  - profiles/aixem-grid-schematic-style-1.aixstyle.json
requirements:
- id: AIXEM-REQ-RENDERER-0001
  title: Deterministic variant selection
  level: MUST
  statement: The renderer MUST select variants in placement, presentation default, then symbol default precedence order.
  validator: schematic.renderer_contract
  verification_mode: automated
  test: tests/docs/test_renderer_contract.py::RendererContractTests.test_variant_and_parameter_precedence
  evidence: validation/evidence/requirements/AIXEM-REQ-RENDERER-0001.json
- id: AIXEM-REQ-RENDERER-0002
  title: Deterministic parameter resolution
  level: MUST
  statement: The renderer MUST resolve parameters from symbol defaults, selected variant defaults, and placement overrides
    in that order.
  validator: schematic.renderer_contract
  verification_mode: automated
  test: tests/docs/test_renderer_contract.py::RendererContractTests.test_variant_and_parameter_precedence
  evidence: validation/evidence/requirements/AIXEM-REQ-RENDERER-0002.json
- id: AIXEM-REQ-RENDERER-0003
  title: Deterministic field resolution
  level: MUST
  statement: The renderer MUST resolve fields from identity defaults, presentation mappings, semantic entity attributes,
    and placement field overrides in that order.
  validator: schematic.renderer_contract
  verification_mode: automated
  test: tests/docs/test_renderer_contract.py::RendererContractTests.test_field_precedence
  evidence: validation/evidence/requirements/AIXEM-REQ-RENDERER-0003.json
- id: AIXEM-REQ-RENDERER-0004
  title: Semantic port transform
  level: MUST
  statement: The renderer MUST expose routed port positions under semantic component port IDs after symbol-port mapping
    and placement transformation.
  validator: schematic.renderer_contract
  verification_mode: automated
  test: tests/docs/test_renderer_contract.py::RendererContractTests.test_port_map_direction_totality_and_visibility
  evidence: validation/evidence/requirements/AIXEM-REQ-RENDERER-0004.json
- id: AIXEM-REQ-RENDERER-0005
  title: Fail-closed input and feature resolution
  level: MUST
  statement: The renderer MUST reject missing or mismatched locked assets, unresolved mappings, hidden mapped ports,
    and unsupported required features.
  validator: schematic.renderer_contract
  verification_mode: automated
  test: tests/docs/test_renderer_contract.py::RendererContractTests.test_fail_closed_binding_cases
  evidence: validation/evidence/requirements/AIXEM-REQ-RENDERER-0005.json
- id: AIXEM-REQ-RENDERER-0006
  title: Deterministic evidence output
  level: MUST
  statement: Equivalent locked inputs MUST produce byte-stable SVG, resolved-scene, Viewer Model, viewer, workbench,
    and render-manifest outputs.
  validator: schematic.authoring_examples
  verification_mode: automated
  test: tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_authoring_golden_examples
  evidence: validation/evidence/requirements/AIXEM-REQ-RENDERER-0006.json
---

# Renderer Contract 1

The reference renderer resolves locked semantics, component presentations, symbol assets, placements, and explicit routes into deterministic evidence. Renderer output is derived and may not become an independent semantic authority.

## Inputs

The renderer consumes one `.aixproj.json` manifest, its digest-locked `.aixem` source, `.aixlayout.json`, all referenced `.aixlib.json` libraries, all selected `.aixsym.json` assets, the active style profile, and local digest-locked raster assets when permitted.

Remote assets are denied. Unsafe paths, missing files, digest mismatches, symbol identity mismatches, and unsupported required features fail closed.

## Presentation Selection

For each semantic entity, the renderer resolves its component type, selects presentations whose `purpose` matches project `renderPolicy.purpose`, and otherwise uses the first declared presentation. It then loads and verifies the presentation asset.

## Variant Selection

<a id="AIXEM-REQ-RENDERER-0001"></a>

### AIXEM-REQ-RENDERER-0001 — Deterministic variant selection

**MUST.** The renderer MUST select variants in placement, presentation default, then symbol default precedence order.

- Verification mode: `automated`
- Validator: `schematic.renderer_contract`
- Test reference: `tests/docs/test_renderer_contract.py::RendererContractTests.test_variant_and_parameter_precedence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-RENDERER-0001.json`

```text
placement.variant
→ presentation.defaultVariant
→ symbol.defaultVariant
```

An explicitly selected but unknown variant is an error.

## Parameter Resolution

<a id="AIXEM-REQ-RENDERER-0002"></a>

### AIXEM-REQ-RENDERER-0002 — Deterministic parameter resolution

**MUST.** The renderer MUST resolve parameters from symbol defaults, selected variant defaults, and placement overrides in that order.

- Verification mode: `automated`
- Validator: `schematic.renderer_contract`
- Test reference: `tests/docs/test_renderer_contract.py::RendererContractTests.test_variant_and_parameter_precedence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-RENDERER-0002.json`

```text
symbol.parameters[*].default
→ selectedVariant.parameterDefaults
→ placement.parameters
```

The renderer validates known parameter names, types, enum values, and numeric bounds after precedence resolves.

## Field Resolution

<a id="AIXEM-REQ-RENDERER-0003"></a>

### AIXEM-REQ-RENDERER-0003 — Deterministic field resolution

**MUST.** The renderer MUST resolve fields from identity defaults, presentation mappings, semantic entity attributes, and placement field overrides in that order.

- Verification mode: `automated`
- Validator: `schematic.renderer_contract`
- Test reference: `tests/docs/test_renderer_contract.py::RendererContractTests.test_field_precedence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-RENDERER-0003.json`

```text
base identity fields: entity, reference, value, type, title
→ presentation.fieldMap-derived values
→ semantic entity attributes
→ placement.fields overrides
```

A text node with `field` reads the final field map. A literal `text` value is used only when no `field` is declared.

## Port Resolution and Placement Transform

The renderer requires total semantic port mapping, applies selected-variant `portOverrides`, evaluates `visibleWhen`, resolves local numeric coordinates, and transforms each point by axis adaptation, scale/mirror, rotation, and translation.

<a id="AIXEM-REQ-RENDERER-0004"></a>

### AIXEM-REQ-RENDERER-0004 — Semantic port transform

**MUST.** The renderer MUST expose routed port positions under semantic component port IDs after symbol-port mapping and placement transformation.

- Verification mode: `automated`
- Validator: `schematic.renderer_contract`
- Test reference: `tests/docs/test_renderer_contract.py::RendererContractTests.test_port_map_direction_totality_and_visibility`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-RENDERER-0004.json`

This rule is why route endpoints use `entity.semanticPort`, not raw symbol port IDs.

## Predicates, Definitions, and Graphics

`visibleWhen` evaluates against resolved parameters and fields. A hidden mapped port causes rejection. `use` expands a named definition with local value expressions. Named variant `suppress` entries remove matching graphics by ID. Base graphics render before selected-variant graphics.

The renderer supports `group`, `use`, `line`, `polyline`, `polygon`, `rect`, `circle`, `ellipse`, `arc`, `path`, `text`, `image`, and `dimension`, subject to required-feature negotiation.

## Style Resolution

Symbol-local styles are deterministic fallbacks. The grid renderer applies the active project visual profile to approved presentation roles. Style resolution must not move ports, change endpoint identity, change net membership, or alter semantic closure. The architecture decision is recorded in ADR 0004.

## Route Binding

Every layout connection must name an existing semantic net. Each endpoint route side must belong to that net. Every semantic net must have one layout connection record, and every semantic endpoint must be referenced by route geometry. Point endpoints and `via` points remain geometric only.

## Fail-Closed Conditions

<a id="AIXEM-REQ-RENDERER-0005"></a>

### AIXEM-REQ-RENDERER-0005 — Fail-closed input and feature resolution

**MUST.** The renderer MUST reject missing or mismatched locked assets, unresolved mappings, hidden mapped ports, and unsupported required features.

- Verification mode: `automated`
- Validator: `schematic.renderer_contract`
- Test reference: `tests/docs/test_renderer_contract.py::RendererContractTests.test_fail_closed_binding_cases`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-RENDERER-0005.json`

## Output Contract

The renderer emits:

- `drawing.svg` — deterministic drawing;
- `resolved-scene.json` — resolved entities, parameters, transformed semantic port positions, nets, routes, junctions, and statistics;
- `viewer.html` — standalone SVG viewer;
- `workbench.html` — engineering review interface;
- `render-manifest.json` — renderer identity, locked input digests, output digests, and status;
- `project-validation.json` — closure checks, grid metrics, features, hashes, and diagnostics.

<a id="AIXEM-REQ-RENDERER-0006"></a>

### AIXEM-REQ-RENDERER-0006 — Deterministic evidence output

**MUST.** Equivalent locked inputs MUST produce byte-stable SVG, resolved-scene, Viewer Model, viewer, workbench, and render-manifest outputs.

- Verification mode: `automated`
- Validator: `schematic.authoring_examples`
- Test reference: `tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_authoring_golden_examples`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-RENDERER-0006.json`

## Renderer-to-Viewer Boundary

The production renderer owns deterministic SVG, resolved-scene, resolved-project-scene, validation, and render-manifest evidence. After those products close, `ViewerModelBuilder` derives capability flags, qualified object/search indexes, inspector projections, views, layers, diagnostics, and provenance without inventing circuit meaning.

```text
resolved scene(s) + drawing/project SVG
                ↓
        Viewer Model 1
                ↓
ReferenceViewerRenderer / ReviewWorkbenchRenderer
```

`render_project.py` orchestrates this boundary but does not embed a second semantic renderer in HTML. `viewer.html` is the primary read-only viewing surface; `workbench.html` is the distinct diagnostics/provenance extension. Their contracts are owned by the Viewer specification family.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
