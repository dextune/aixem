---
id: AIXEM-SCHEM-JUNCTION-001
title: Junctions and Connectivity Cues
status: normative
version: '1.0'
language: en
domain: schematic
kind: guide
summary: Defines explicit junction dots, non-connecting crossings, endpoint joins, and no-connect marks.
authority:
- junction-presentation
aliases:
- junctions
- wire crossing
- connection dot
- no connect mark
agent:
  priority: critical
  estimated_tokens: 972
  intents:
  - create-schematic
  - route-nets
  - validate-project
depends_on:
- AIXEM-CONCEPT-NET-001
related:
- AIXEM-ROUTE-CROSSING-001
- AIXEM-FORMAT-AIXLAYOUT-001
navigation:
  group: schematic
  order: 40
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SCHEM-0006
  title: Explicit junction
  level: MUST
  statement: A multi-segment electrical join MUST have an explicit junction declaration when required by the active
    profile.
  validator: schematic.junction
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0006.json
- id: AIXEM-REQ-SCHEM-0007
  title: Crossing isolation
  level: MUST
  statement: A route crossing without an explicit junction MUST render and validate as not connected.
  validator: schematic.junction
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0007.json
- id: AIXEM-REQ-SCHEM-0008
  title: Semantic no-connect
  level: MUST
  statement: A no-connect mark MUST correspond to an explicit semantic no-connect declaration.
  validator: schematic.no_connect
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0008.json
---

# Junctions and Connectivity Cues

Defines explicit junction dots, non-connecting crossings, endpoint joins, and no-connect marks.

> **Document ID:** `AIXEM-SCHEM-JUNCTION-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

These rules prioritize a compact, grid-aligned engineering drawing that remains unambiguous when printed or viewed without color.

The declared authority scopes are `junction-presentation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- The dot is evidence of a declared join.
- A crossing is not a join by geometry.
- No-connect marks close intent and prevent silent omissions.

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

<a id="AIXEM-REQ-SCHEM-0006"></a>

### AIXEM-REQ-SCHEM-0006 — Explicit junction

**MUST.** A multi-segment electrical join MUST have an explicit junction declaration when required by the active profile.

- Verification mode: `automated`
- Validator: `schematic.junction`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0006.json`

<a id="AIXEM-REQ-SCHEM-0007"></a>

### AIXEM-REQ-SCHEM-0007 — Crossing isolation

**MUST.** A route crossing without an explicit junction MUST render and validate as not connected.

- Verification mode: `automated`
- Validator: `schematic.junction`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0007.json`

<a id="AIXEM-REQ-SCHEM-0008"></a>

### AIXEM-REQ-SCHEM-0008 — Semantic no-connect

**MUST.** A no-connect mark MUST correspond to an explicit semantic no-connect declaration.

- Verification mode: `automated`
- Validator: `schematic.no_connect`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0008.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Net Model](../concepts/net-model.md) — `AIXEM-CONCEPT-NET-001`
- [Crossings and Junctions](../routing/crossings-and-junctions.md) — `AIXEM-ROUTE-CROSSING-001`
- [.aixlayout.json Explicit Layout](../file-formats/aixlayout.md) — `AIXEM-FORMAT-AIXLAYOUT-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
