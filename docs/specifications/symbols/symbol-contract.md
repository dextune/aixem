---
id: AIXEM-SPEC-SYMBOL-001
title: Symbol Asset Contract 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines the serialized symbol asset contract, feature declaration, port mapping, deterministic geometry,
  and variant compatibility.
authority:
- symbol-serialization-contract
aliases:
- symbol contract
- aixsym contract
- symbol specification
agent:
  priority: critical
  estimated_tokens: 1397
  intents:
  - create-symbol
  - validate-project
depends_on:
- AIXEM-SYMBOL-ANATOMY-001
- AIXEM-SYMBOL-PRIMITIVES-001
related:
- AIXEM-FORMAT-AIXSYM-001
navigation:
  group: specifications
  order: 70
artifacts:
  owns:
  - docs/specifications/schemas/component-graphics-1/aixem-symbol-asset-1.schema.json
  consumes: []
requirements:
- id: AIXEM-REQ-SYMBOL-0020
  title: Schema-conforming asset
  level: MUST
  statement: A symbol asset MUST validate against the declared symbol schema version.
  validator: schematic.symbol_schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0020.json
- id: AIXEM-REQ-SYMBOL-0021
  title: Required feature rejection
  level: MUST
  statement: A renderer MUST reject a symbol that requires an unsupported graphic feature.
  validator: schematic.feature_support
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0021.json
- id: AIXEM-REQ-SYMBOL-0022
  title: Local deterministic content
  level: MUST
  statement: All content required to render a symbol MUST be local, locked, and deterministic.
  validator: schematic.remote_assets
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0022.json
---

# Symbol Asset Contract 1

Defines the serialized symbol asset contract, feature declaration, port mapping, deterministic geometry, and variant compatibility.

> **Document ID:** `AIXEM-SPEC-SYMBOL-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `symbol-serialization-contract`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- The JSON schema constrains structure.
- Feature negotiation protects portability.
- Port maps preserve circuit meaning.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `docs/specifications/schemas/component-graphics-1/aixem-symbol-asset-1.schema.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-SYMBOL-0020"></a>

### AIXEM-REQ-SYMBOL-0020 — Schema-conforming asset

**MUST.** A symbol asset MUST validate against the declared symbol schema version.

- Verification mode: `automated`
- Validator: `schematic.symbol_schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0020.json`

<a id="AIXEM-REQ-SYMBOL-0021"></a>

### AIXEM-REQ-SYMBOL-0021 — Required feature rejection

**MUST.** A renderer MUST reject a symbol that requires an unsupported graphic feature.

- Verification mode: `automated`
- Validator: `schematic.feature_support`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0021.json`

<a id="AIXEM-REQ-SYMBOL-0022"></a>

### AIXEM-REQ-SYMBOL-0022 — Local deterministic content

**MUST.** All content required to render a symbol MUST be local, locked, and deterministic.

- Verification mode: `automated`
- Validator: `schematic.remote_assets`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0022.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Symbol Anatomy](../../symbols/symbol-anatomy.md) — `AIXEM-SYMBOL-ANATOMY-001`
- [Graphic Primitives](../../symbols/primitives.md) — `AIXEM-SYMBOL-PRIMITIVES-001`
- [.aixsym.json Symbol Asset](../../file-formats/aixsym.md) — `AIXEM-FORMAT-AIXSYM-001`

<a id="0-5-1-binding-and-rendering-requirements"></a>
## Binding and Rendering Requirements

The schema contract is necessary but not sufficient for a usable component presentation. A conforming project also satisfies these linked contracts:

- the component presentation `portMap` closes exactly over semantic component ports;
- each target identifies an existing symbol port;
- each required mapped port remains visible after variant and parameter resolution;
- symbol numeric expressions resolve deterministically and within declared parameter constraints;
- selected variants preserve endpoint identity;
- all image and symbol dependencies are project-local and digest-locked;
- the renderer exposes transformed route coordinates under semantic component port IDs;
- visible lead geometry meets its associated symbol port under the active design profile;
- styles affect presentation only and never alter connectivity.

### Total Mapping

The direction is component semantic port → symbol port. The component library is the binding authority; neither the symbol nor layout may infer or reverse the map.

### Feature and Dependency Closure

`requiredFeatures` declares symbol-side capabilities that must be supported. Unsupported required features fail closed. Reusable definitions, paint servers, image sources, and asset references must resolve locally and deterministically.

### Contract Layers

| Layer | Contract owner |
|---|---|
| serialization shape | AIXSYM JSON Schema |
| endpoint/presentation mapping | component-symbol binding contract |
| grid, lead, pitch, and field geometry | symbol design profile |
| field/variant/parameter/style precedence | renderer contract |
| final instance transform and wire geometry | explicit layout contract |

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
