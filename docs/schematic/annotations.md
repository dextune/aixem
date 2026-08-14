---
id: AIXEM-SCHEM-ANNOTATION-001
title: Annotations and Fields
status: normative
version: '1.0'
language: en
domain: schematic
kind: guide
summary: Defines reference, value, pin name, pin number, net label, note, and test-point presentation.
authority:
- schematic-annotation
aliases:
- annotations
- reference designator
- pin labels
- schematic text
agent:
  priority: critical
  estimated_tokens: 856
  intents:
  - create-schematic
  - create-symbol
depends_on:
- AIXEM-CONCEPT-SYMBOL-001
related:
- AIXEM-SYMBOL-FIELDS-001
- AIXEM-SCHEM-VISUAL-001
navigation:
  group: schematic
  order: 50
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SCHEM-0009
  title: Pin text distinction
  level: MUST
  statement: Pin name and pin number MUST be visually distinguishable by position, role, or style.
  validator: schematic.annotation
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0009.json
- id: AIXEM-REQ-SCHEM-0010
  title: Readable annotation
  level: MUST
  statement: Required annotation text MUST not overlap symbol bodies, pins, or route segments in the reference output.
  validator: schematic.annotation
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0010.json
---

# Annotations and Fields

Defines reference, value, pin name, pin number, net label, note, and test-point presentation.

> **Document ID:** `AIXEM-SCHEM-ANNOTATION-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

These rules prioritize a compact, grid-aligned engineering drawing that remains unambiguous when printed or viewed without color.

The declared authority scopes are `schematic-annotation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Reference and value fields have separate anchors.
- Net labels expose semantic names.
- Notes are informative and never create connectivity.

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

<a id="AIXEM-REQ-SCHEM-0009"></a>

### AIXEM-REQ-SCHEM-0009 — Pin text distinction

**MUST.** Pin name and pin number MUST be visually distinguishable by position, role, or style.

- Verification mode: `automated`
- Validator: `schematic.annotation`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0009.json`

<a id="AIXEM-REQ-SCHEM-0010"></a>

### AIXEM-REQ-SCHEM-0010 — Readable annotation

**MUST.** Required annotation text MUST not overlap symbol bodies, pins, or route segments in the reference output.

- Verification mode: `automated`
- Validator: `schematic.annotation`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0010.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Symbol Presentation Model](../concepts/symbol-model.md) — `AIXEM-CONCEPT-SYMBOL-001`
- [Field Layout](../symbols/field-layout.md) — `AIXEM-SYMBOL-FIELDS-001`
- [Grid-First Visual Language](visual-language.md) — `AIXEM-SCHEM-VISUAL-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
