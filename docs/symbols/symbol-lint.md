---
id: AIXEM-SYMBOL-LINT-001
title: Symbol Lint
status: normative
version: '1.0'
language: en
domain: symbols
kind: guide
summary: Defines structural, geometric, mapping, readability, and vendor-independence checks for symbol assets.
authority:
- symbol-validation
aliases:
- symbol lint
- validate symbol
- symbol checker
agent:
  priority: critical
  estimated_tokens: 1887
  intents:
  - create-symbol
  - validate-project
depends_on:
- AIXEM-SYMBOL-ANATOMY-001
- AIXEM-SYMBOL-PORTS-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-CONF-VALIDATION-001
navigation:
  group: symbols
  order: 60
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SYMBOL-0010
  title: Schema validation
  level: MUST
  statement: Every symbol asset MUST validate against the active AIXEM symbol schema before use.
  validator: schematic.symbol_schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0010.json
- id: AIXEM-REQ-SYMBOL-0011
  title: Mapping validation
  level: MUST
  statement: Symbol lint MUST reject duplicate, missing, or unresolved endpoint mappings.
  validator: schematic.port_mapping
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0011.json
- id: AIXEM-REQ-SYMBOL-0012
  title: Readable geometry
  level: MUST
  statement: Symbol lint MUST detect zero-length port stubs and text that violates declared bounds or required clearances.
  validator: schematic.symbol_geometry
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0012.json
---

# Symbol Lint

Defines structural, geometric, mapping, readability, and vendor-independence checks for symbol assets.

> **Document ID:** `AIXEM-SYMBOL-LINT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Symbol graphics are presentation assets. Endpoint identity remains owned by the component and semantic layers.

The declared authority scopes are `symbol-validation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Symbol validation.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Validate schema
2. Resolve features
3. Check bounds and grid
4. Check port IDs and mappings
5. Check fields and clearances
6. Record evidence

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-SYMBOL-0010"></a>

### AIXEM-REQ-SYMBOL-0010 — Schema validation

**MUST.** Every symbol asset MUST validate against the active AIXEM symbol schema before use.

- Verification mode: `automated`
- Validator: `schematic.symbol_schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0010.json`

<a id="AIXEM-REQ-SYMBOL-0011"></a>

### AIXEM-REQ-SYMBOL-0011 — Mapping validation

**MUST.** Symbol lint MUST reject duplicate, missing, or unresolved endpoint mappings.

- Verification mode: `automated`
- Validator: `schematic.port_mapping`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0011.json`

<a id="AIXEM-REQ-SYMBOL-0012"></a>

### AIXEM-REQ-SYMBOL-0012 — Readable geometry

**MUST.** Symbol lint MUST detect zero-length port stubs and text that violates declared bounds or required clearances.

- Verification mode: `automated`
- Validator: `schematic.symbol_geometry`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0012.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Symbol Anatomy](symbol-anatomy.md) — `AIXEM-SYMBOL-ANATOMY-001`
- [Pins, Ports, and Endpoint Mapping](pins-and-ports.md) — `AIXEM-SYMBOL-PORTS-001`
- [Validation Architecture](../conformance/validation.md) — `AIXEM-CONF-VALIDATION-001`

<a id="0-5-1-authoring-lint-profile"></a>
## Authoring Lint Profile

The authoring validator supplements JSON Schema with measurable graphic and binding checks. Run it before project-level release validation:

```bash
python tools/docs/authoring_validation.py
```

### Automated Checks

- every authoring symbol, library, layout, and project validates against its active schema;
- every symbol port resolves numerically and lies on the 2.5 mm profile grid;
- standard port orientations are orthogonal;
- every standard `pin-lead` names its associated port through `metadata.port`;
- `metadata.portEndpoint` selects `start` or `end`, and that exact endpoint coincides with the port;
- repeated standard pin groups use consistent 5 mm pitch;
- required reference/value anchors do not lie inside ordinary rectangular body geometry;
- library `portMap` keys close exactly over component semantic ports;
- every map target exists and the locked symbol digest matches;
- `fieldMap` sources refer to declared component properties;
- authoring examples rerender byte-for-byte identically;
- the deliberately broken lead/port fixture is rejected, proving the check is active.

### Review-Mode Checks

Automation does not replace engineering visual review. Inspect:

- functional pin grouping and signal-flow readability;
- body proportion and visual density;
- field, name, and number clearance after actual value substitution;
- ambiguity between decorative graphics and electrical marks;
- junction/crossing readability in the complete schematic;
- usefulness at normal workbench zoom and narrow viewport sizes.

### Failure Repair Map

| Diagnostic | Owning repair layer |
|---|---|
| `symbol-grid` | symbol port expression/default |
| `lead-port-mismatch` | symbol lead geometry or symbol port coordinate |
| `portmap-total` | component presentation in `.aixlib.json` |
| `portmap-target` | component presentation or symbol port ID |
| `fieldmap-source` | component property declaration or `fieldMap` |
| `field-body-overlap` | symbol field anchor/body dimensions |
| `render-drift` | authoritative input or renderer determinism defect; never patch the golden output directly |

Rerun the narrow validator after repair, then render, inspect evidence, and run release validation when the change is release-scoped.
<a id="0-5-2-corpus-conformance-checks"></a>
## Authoring-Integrity Claim Boundary

Symbol lint and deterministic rendering establish structural conformance: schema, graphic bounds, port geometry, lead coincidence, grid, binding, and repeatability. They do not independently verify a manufacturer part number or datasheet pinout.

New-authoring validation additionally checks canonical paths, provenance class, minimum semantic contract, semantic-clone batches, pin-semantics consistency, and source-bound review evidence. Those results remain separately named; `STRUCTURAL_PASS` must not be promoted to `PART_SEMANTIC_PASS` or `CIRCUIT_INTENT_REVIEW_PASS` without the corresponding evidence.

## Corpus Conformance Checks

For corpus-backed symbol validation, apply these additional checks after the 0.5.1 authoring lint profile:

1. validate `case.json` and the referenced `.aixsym` source;
2. confirm expected port, visible-port, parameter, variant, primitive, and field-role inventories;
3. confirm generated `portMap` closure and visible targets;
4. verify declared grid policy and metadata-annotated lead/port coincidence;
5. reject unintended degenerate line, rectangle, circle, or ellipse geometry;
6. render through `GridProjectRenderer`, not a corpus-specific renderer;
7. compare canonical SVG, resolved scene, and geometry signature with explicitly approved digests;
8. require digest-bound structured visual review with no critical readability or connectivity defect;
9. publish MU separately from graphics tiers.

Failures are classified F1 through F6 before implementation changes. Only a reproduced F4 or F5 may open a core contract review.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
