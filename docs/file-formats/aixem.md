---
id: AIXEM-FORMAT-AIXEM-001
title: .aixem Semantic Source
status: normative
version: '1.0'
language: en
domain: file-formats
kind: reference
summary: Documents the line-oriented semantic source format for model headers, features, library use, entities,
  nets, and no-connect declarations.
authority:
- aixem-format
aliases:
- .aixem
- semantic source
- AIXEM source file
agent:
  priority: critical
  estimated_tokens: 1389
  intents:
  - create-schematic
  - inspect-artifact
  - validate-project
  - compose-project
depends_on:
- AIXEM-CONCEPT-SEMANTIC-001
related:
- AIXEM-FORMAT-AIXLIB-001
- AIXEM-FORMAT-AIXPROJ-001
- AIXEM-SPEC-INTERFACE-PORT-001
navigation:
  group: file-formats
  order: 20
artifacts:
  owns:
  - '*.aixem'
  consumes: []
requirements:
- id: AIXEM-REQ-FORMAT-0001
  title: Semantic parse closure
  level: MUST
  statement: An .aixem source MUST parse without duplicate entity IDs, duplicate net IDs, or unresolved endpoint
    references.
  validator: schematic.semantic
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-FORMAT-0001.json
- id: AIXEM-REQ-FORMAT-0002
  title: Declared features
  level: MUST
  statement: Required semantic features MUST be declared before use.
  validator: schematic.feature_support
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-FORMAT-0002.json
---

# .aixem Semantic Source

Documents the line-oriented semantic source format for model headers, features, library use, entities, nets, and no-connect declarations.

> **Document ID:** `AIXEM-FORMAT-AIXEM-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The format is interpreted together with its declared schema, feature set, and project lock.

The declared authority scopes are `aixem-format`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- The source is intentionally geometry-free.
- Attributes use explicit key-value tokens.
- Endpoint references remain stable across layout changes.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `*.aixem`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-FORMAT-0001"></a>

### AIXEM-REQ-FORMAT-0001 — Semantic parse closure

**MUST.** An .aixem source MUST parse without duplicate entity IDs, duplicate net IDs, or unresolved endpoint references.

- Verification mode: `automated`
- Validator: `schematic.semantic`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-FORMAT-0001.json`

<a id="AIXEM-REQ-FORMAT-0002"></a>

### AIXEM-REQ-FORMAT-0002 — Declared features

**MUST.** Required semantic features MUST be declared before use.

- Verification mode: `automated`
- Validator: `schematic.feature_support`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-FORMAT-0002.json`

### Implementation notes

- The bundled example is the executable reference for the currently implemented grammar.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Semantic Circuit Model](../concepts/semantic-model.md) — `AIXEM-CONCEPT-SEMANTIC-001`
- [.aixlib.json Component Library](aixlib.md) — `AIXEM-FORMAT-AIXLIB-001`
- [.aixproj.json Project Lock](aixproj.md) — `AIXEM-FORMAT-AIXPROJ-001`

<a id="0-5-3-hierarchical-interface-extension"></a>
## Hierarchical Interface Extension

A leaf source opts into hierarchical boundaries with `feature hierarchical.interface@1 required=true`, declares top-level `port` records, and uses `@PORT` as a real semantic endpoint. The leaf source remains the authority for the local net that owns each interface port. See [Interface Port Contract 1](../specifications/core/interface-port-contract.md).

```aixem
port VCC direction=input role=power
net vcc = U1.VCC @VCC
```

Matching port or local-net names in other files do not create connectivity. Cross-sheet equivalence is declared only in `aixproj/2`.

<a id="0-5-1-complete-minimal-semantic-model"></a>
## Complete Minimal Semantic Model

```aixem
aixem 1.0
model two_pin_passive title="Two-pin passive"
feature component.graphics@1 required=true
feature explicit.layout@1 required=true

component R1 type=authoring:resistor refdes=R1 value=10k
component R2 type=authoring:resistor refdes=R2 value=22k

net link = R1.2 R2.1

noconn R1.1
noconn R2.2
```

### Semantic Ownership

The file owns:

- model identity and declared required features;
- entity/component instance keys and component type references;
- entity attributes used by field binding;
- explicit net names and endpoint membership;
- explicit no-connect intent.

It never stores component X/Y position, rotation, symbol variant selection, wire bends, route labels, junction drawing coordinates, colors, or line widths. Those facts belong to layout or presentation.

### Closure Rules

- Every endpoint token is `entity.port` and must resolve through the referenced component type.
- An endpoint may not belong to multiple semantic nets unless a future normative feature explicitly permits it.
- An endpoint may not be both net-connected and declared `noconn`.
- Coincident rendered coordinates never create a semantic net.
- Layout may materialize but may not redefine the membership declared here.

Entity attributes are ordinary semantic data. Field display precedence is governed by the renderer contract; a placement field override changes presentation, not the semantic source.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
