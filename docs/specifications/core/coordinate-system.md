---
id: AIXEM-SPEC-COORD-001
title: Coordinate and Unit System
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines millimetre units, local symbol coordinates, global sheet coordinates, precision, orientation, and
  transform ordering.
authority:
- coordinate-system
aliases:
- coordinates
- units
- millimetres
- transform order
agent:
  priority: critical
  estimated_tokens: 966
  intents:
  - create-symbol
  - create-schematic
  - route-nets
depends_on: []
related:
- AIXEM-SCHEM-GRID-001
- AIXEM-SYMBOL-ANATOMY-001
- AIXEM-FORMAT-AIXLAYOUT-001
navigation:
  group: specifications
  order: 30
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-LAYOUT-0001
  title: Millimetre units
  level: MUST
  statement: Reference-profile symbol and schematic coordinates MUST be interpreted in millimetres.
  validator: schematic.coordinate_units
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0001.json
- id: AIXEM-REQ-LAYOUT-0002
  title: Finite coordinates
  level: MUST
  statement: Serialized coordinates MUST be finite numeric values.
  validator: schematic.schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0002.json
- id: AIXEM-REQ-LAYOUT-0003
  title: Deterministic transforms
  level: MUST
  statement: Translation, rotation, mirroring, and local-to-global transforms MUST be applied in the declared deterministic
    order.
  validator: schematic.deterministic
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0003.json
---

# Coordinate and Unit System

Defines millimetre units, local symbol coordinates, global sheet coordinates, precision, orientation, and transform ordering.

> **Document ID:** `AIXEM-SPEC-COORD-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `coordinate-system`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Symbol assets use local coordinates.
- Placements map local geometry into sheet space.
- Route points are stored in sheet space.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-LAYOUT-0001"></a>

### AIXEM-REQ-LAYOUT-0001 — Millimetre units

**MUST.** Reference-profile symbol and schematic coordinates MUST be interpreted in millimetres.

- Verification mode: `automated`
- Validator: `schematic.coordinate_units`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0001.json`

<a id="AIXEM-REQ-LAYOUT-0002"></a>

### AIXEM-REQ-LAYOUT-0002 — Finite coordinates

**MUST.** Serialized coordinates MUST be finite numeric values.

- Verification mode: `automated`
- Validator: `schematic.schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0002.json`

<a id="AIXEM-REQ-LAYOUT-0003"></a>

### AIXEM-REQ-LAYOUT-0003 — Deterministic transforms

**MUST.** Translation, rotation, mirroring, and local-to-global transforms MUST be applied in the declared deterministic order.

- Verification mode: `automated`
- Validator: `schematic.deterministic`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0003.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Grid and Snap System](../../schematic/grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Symbol Anatomy](../../symbols/symbol-anatomy.md) — `AIXEM-SYMBOL-ANATOMY-001`
- [.aixlayout.json Explicit Layout](../../file-formats/aixlayout.md) — `AIXEM-FORMAT-AIXLAYOUT-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
