---
id: AIXEM-CONF-SYMBOL-EXP-001
title: Symbol Expressiveness Conformance Profile 1
status: normative
version: '1.0'
language: en
domain: conformance
kind: profile
summary: Defines evidence-backed schematic-symbol expressiveness tiers, corpus gates, extension controls, and public claim boundaries.
authority:
- symbol-expressiveness-conformance
aliases:
- symbol expressiveness
- symbol conformance corpus
- schematic symbol corpus
agent:
  priority: critical
  estimated_tokens: 2085
  intents:
  - validate-symbol-expressiveness
  - create-symbol
  - publish-release
depends_on:
- AIXEM-SPEC-RENDERER-001
- AIXEM-SPEC-SYMBOL-DESIGN-001
- AIXEM-CONF-VALIDATION-001
related:
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-EXAMPLE-SYMBOL-CORPUS-001
- AIXEM-CONF-B2D-001
- AIXEM-CONF-RELEASE-001
navigation:
  group: conformance
  order: 45
artifacts:
  owns:
  - validation/corpus/symbol-expressiveness-1/
  - validation/reports/symbol-expressiveness-0.5.2.json
  - validation/releases/0.5.2/symbol-expressiveness.md
  - validation/reports/multi-unit-capability-0.5.2.json
  consumes:
  - implementation/schematic/render_project.py
  - docs/specifications/schemas/component-graphics-1/aixem-symbol-asset-1.schema.json
requirements: []
---

# Symbol Expressiveness Conformance Profile 1

> **Document ID:** `AIXEM-CONF-SYMBOL-EXP-001`  
> **Status:** Normative  
> **Version:** 1.0

## Purpose

This profile proves a bounded engineering claim with executable evidence. It determines whether the current AIXEM symbol model can represent a representative set of schematic-symbol classes through the production `.aixsym` validation, binding, resolution, and rendering path.

The corpus is evidence. It does not replace the symbol schema, renderer contract, component semantics, or symbol design profile.

## Claim Levels

### S-Core

S-Core contains cases `S001` through `S024`: passive devices, semiconductor devices, analog and electromechanical devices, logic symbols, connectors, and 32-, 64-, and 100-pin IC-scale symbols.

S-Core passes only when every case satisfies all mandatory gates. Results are pass/fail; a critical defect cannot be hidden by an average score.

Permitted claim:

> AIXEM demonstrates conformance against its representative Core schematic-symbol expressiveness corpus using the production `.aixsym` and renderer pipeline.

### S-Extended

S-Extended adds cases `S025` through `S029`: JFET, timing-device, optocoupler, vacuum-tube, and irregular compound-path constructions. It demonstrates broader graphical range and does not imply vendor-native compatibility.

### MU

Case `S030` is an isolated semantic capability probe. Its result is one of `PASS`, `PARTIAL`, or `NOT_SUPPORTED` and is published independently from S-Core and S-Extended.

A MU `PASS` requires independently placeable units that share one semantic component identity, expose declared port subsets, retain unambiguous endpoint ownership, and do not misuse variants as semantic units.

## Corpus Contract

The canonical fixture root is `validation/corpus/symbol-expressiveness-1/`.

Each case contains:

- `case.json`, validated against `schema/corpus-case-1.schema.json`;
- one self-authored, vendor-neutral `symbol.aixsym.json`;
- a declared purpose, tier, expected port inventory, capability vocabulary, primitive families, fields, parameters, variants, grid policy, and review checks.

The harness generates minimal `.aixem`, `.aixlib.json`, `.aixlayout.json`, and `.aixproj.json` wrappers in a temporary directory. Hand-maintained duplicate projects are not authoritative fixtures.

## Production-Pipeline Requirement

`tools/validate_symbol_corpus.py` MUST invoke `GridProjectRenderer` from the production renderer implementation. A corpus-only renderer, alternate geometry resolver, or special-case rendering path is prohibited.

The required flow is:

```text
case contract + .aixsym source
→ synthetic semantic/library/layout wrapper
→ existing schema and project validation
→ existing production renderer
→ drawing.svg + resolved-scene.json
→ conformance assertions and review evidence
```

## Mandatory Gates

Every required case MUST pass all applicable stages:

1. **Static validity:** JSON and schemas validate; required capabilities are declared; locked local inputs are available.
2. **Binding validity:** component port IDs are unique; the generated `portMap` is total; mapped symbol ports exist and are visible; field bindings resolve.
3. **Geometry validity:** required ports are on the declared grid; annotated lead endpoints coincide with electrical ports; bounds and primitive geometry are non-degenerate.
4. **Renderer validity:** production rendering succeeds; SVG and resolved scene are emitted; expected fields, ports, and primitive families are present.
5. **Determinism:** repeated canonical SVG and resolved-scene digests are identical.
6. **Approved baseline:** the source, geometry signature, SVG, and scene match an explicitly approved digest record.
7. **Structured visual review:** all required case checks pass against the exact reviewed source and render digests.

## Visual Review Evidence

Visual review records MUST be digest-bound and identify the case, reviewer mode, review date, source digest, SVG digest, check results, and unresolved defects.

The minimum checks cover recognizability, lead-to-port attachment, label collisions, body-field clearance, polarity or state markings, repeated-geometry spacing, high-pin-count readability, false-connectivity risk, variant endpoint invariance, and compound-path artifacts.

AI-assisted review is valid as internal release-candidate evidence only when it is disclosed as such. It is not represented as independent certification or third-party human approval.

## Failure Classification

Every failure MUST be assigned one primary class before changing the implementation:

| Class | Meaning | Default action |
|---|---|---|
| F1 | Authoring or documentation gap | Improve recipe/reference; keep the format unchanged. |
| F2 | Validator gap | Strengthen mechanical checks. |
| F3 | Renderer defect against an existing contract | Repair the renderer and add regression coverage. |
| F4 | Proven graphical expressiveness gap | Apply the Core Extension Gate. |
| F5 | Semantic model gap | Open a semantic ADR; do not disguise it as graphics. |
| F6 | Out-of-scope vendor behavior | Record the exclusion. |

## Core Extension Gate

A new primitive, top-level symbol field, or renderer contract may be introduced only when all of the following are true:

1. an identified corpus case is blocked;
2. an automated reproduction exists;
3. existing primitive composition, `group`, `use`, `path`, parameters, predicates, and variants are insufficient or semantically misleading;
4. the capability is useful beyond one vendor artifact;
5. syntax and semantics remain small, declarative, deterministic, and mechanically validatable;
6. existing 0.5.1 sources remain valid;
7. authoring burden remains suitable for an AI agent;
8. an ADR records alternatives, compatibility impact, and rejection rationale.

`path` remains the generic escape hatch for unusual vector geometry. One visually difficult symbol is not sufficient justification for primitive proliferation.

## Multi-Unit Boundary

A graphically complete FPGA-shaped symbol does not prove true multi-unit semantics. The MU probe MUST test shared identity and independent placement separately from drawing expressiveness.

When the current model rejects duplicate placements of one entity and has no unit-subset placement construct, the correct result is `NOT_SUPPORTED`. Duplicating semantic component entities or treating variants as units is not an acceptable simulated pass.

## Capability and Performance Outputs

The harness emits:

- `corpus-results.json`;
- `capability-matrix.json`;
- `primitive-usage-matrix.json`;
- `performance-baseline.json`;
- normalized geometry signatures;
- approved render digests;
- per-case production SVG, resolved scene, render manifest, and workbench output.

Performance values are observations, not unconditional service-level claims. Future releases may apply reviewed relative-regression thresholds to the approved baseline.

## Datasheet-Truth Boundary

S-Core and S-Extended results prove that AIXEM can serialize, bind, render, and review the tested graphic constructions. They do not prove that a corpus item is a real manufacturer part, that its pinout matches a cited datasheet, or that it is suitable for a circuit. Generic and synthetic conformance artifacts must be identified as such. Datasheet-backed readiness is governed by separate component provenance and part-semantic review evidence.

## Public Claim Boundary

The profile does not claim:

- KiCad or OrCAD native-library compatibility;
- exact identity with a vendor default library;
- DWG or DXF import, export, or round trip;
- AutoCAD Dynamic Block behavior;
- PCB footprint, SPICE-model, 3D, B-rep, BIM, or parametric-constraint compatibility.

Tool-family names may be used in informative comparisons. Conformance is defined only by AIXEM-owned cases and published gates.

## Release Evidence

The release result is authoritative only for the source and renderer digests recorded in:

- `validation/reports/symbol-expressiveness-0.5.2.json`;
- `validation/reports/multi-unit-capability-0.5.2.json`;
- `validation/evidence/0.5.2/`;
- `release/manifest.json`.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
