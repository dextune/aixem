---
id: AIXEM-FORMAT-AIXLIB-001
title: .aixlib.json Component Library
status: normative
version: '1.0'
language: en
domain: file-formats
kind: reference
summary: Documents component type definitions, endpoint contracts, properties, symbol bindings, versions, and asset
  digests.
authority:
- aixlib-format
aliases:
- .aixlib
- component library JSON
- library format
agent:
  priority: critical
  estimated_tokens: 1869
  intents:
  - create-schematic
  - create-symbol
  - inspect-artifact
depends_on:
- AIXEM-CONCEPT-COMPONENT-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-FORMAT-AIXSYM-001
- AIXEM-SPEC-SYMBOL-001
navigation:
  group: file-formats
  order: 30
artifacts:
  owns:
  - '*.aixlib.json'
  consumes: []
requirements:
- id: AIXEM-REQ-FORMAT-0010
  title: Library schema
  level: MUST
  statement: A component library MUST validate against the declared library schema.
  validator: schematic.library_schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-FORMAT-0010.json
- id: AIXEM-REQ-FORMAT-0011
  title: Locked symbol references
  level: MUST
  statement: Every symbol asset referenced by a component library MUST be locally resolvable and digest-locked.
  validator: schematic.digest_lock
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-FORMAT-0011.json
---

# .aixlib.json Component Library

Documents component type definitions, endpoint contracts, properties, symbol bindings, versions, and asset digests.

> **Document ID:** `AIXEM-FORMAT-AIXLIB-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The format is interpreted together with its declared schema, feature set, and project lock.

The declared authority scopes are `aixlib-format`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Library IDs and versions identify contracts.
- Component endpoints precede graphic ports.
- Presentation bindings select symbol assets and variants.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `*.aixlib.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-FORMAT-0010"></a>

### AIXEM-REQ-FORMAT-0010 — Library schema

**MUST.** A component library MUST validate against the declared library schema.

- Verification mode: `automated`
- Validator: `schematic.library_schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-FORMAT-0010.json`

<a id="AIXEM-REQ-FORMAT-0011"></a>

### AIXEM-REQ-FORMAT-0011 — Locked symbol references

**MUST.** Every symbol asset referenced by a component library MUST be locally resolvable and digest-locked.

- Verification mode: `automated`
- Validator: `schematic.digest_lock`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-FORMAT-0011.json`

## Component-Level Authoring Profiles

File-level `provenance` continues to describe authorship, origin, and licensing of the library artifact. It does not prove datasheet truth for every component ID in a multi-component library. New component authoring uses the bounded profiles defined by the [Library Layout Contract](../specifications/components/library-layout-contract.md) and [Pin Electrical Semantics Profile](../specifications/components/pin-electrical-semantics-profile.md).

A component that claims a concrete orderable part records `metadata.partProvenance.status = "datasheet-backed"` together with `manufacturer`, `partNumber`, and `sourceUri`. An uncertain concrete identity is `placeholder` with a reason and cannot be `semanticReady`. An intentionally generic class is `generic-template` and must not claim an exact manufacturer product.

Each port retains `type` as its basic electrical-behavior axis. Optional `metadata.pinSemantics` adds source-reviewable signal class, function, polarity, differential membership, power-domain hints, capabilities, and alternate functions. Presentation geometry cannot override these component-port semantics.

A structurally valid or deterministically rendered library is not automatically a source-verified part library. Structural, part-semantic, bounded compatibility, and circuit-intent outcomes are reported separately.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Component Model](../concepts/component-model.md) — `AIXEM-CONCEPT-COMPONENT-001`
- [.aixsym.json Symbol Asset](aixsym.md) — `AIXEM-FORMAT-AIXSYM-001`
- [Symbol Asset Contract 1](../specifications/symbols/symbol-contract.md) — `AIXEM-SPEC-SYMBOL-001`

<a id="0-5-1-component-presentation-example"></a>
## Component Presentation Example

`.aixlib.json` owns reusable component definitions and their presentation bindings. It bridges semantic ports/properties to one or more locked symbol assets.

<!-- aixem-snippet: examples/authoring/05-field-and-port-binding/library/electronics/authoring/authoring-components.aixlib.json#/library/components/0 -->
```json
{
  "classification": [],
  "description": "Bound sensor",
  "displayName": "Bound sensor",
  "id": "authoring:sensor",
  "kind": "sensor",
  "metadata": {
    "partProvenance": {
      "status": "generic-template"
    },
    "semanticReady": true
  },
  "ports": [
    {
      "id": "in",
      "metadata": {
        "pinSemantics": {
          "capabilities": [],
          "functionalTags": [],
          "polarity": "unspecified",
          "profile": "aixem-pin-semantics-1",
          "signalClass": "digital"
        }
      },
      "name": "Input",
      "required": false,
      "terminal": "in",
      "type": "input"
    },
    {
      "id": "out",
      "metadata": {
        "pinSemantics": {
          "capabilities": [],
          "functionalTags": [],
          "polarity": "unspecified",
          "profile": "aixem-pin-semantics-1",
          "signalClass": "digital"
        }
      },
      "name": "Output",
      "required": false,
      "terminal": "out",
      "type": "output"
    }
  ],
  "presentations": [
    {
      "asset": {
        "digest": "sha256:334056e981bd1741e42f034fbbeb3547dc5f7b1025b8d8c05d449d86da0e2e71",
        "path": "library/electronics/authoring/sensor.aixsym.json",
        "revision": "1.0.0",
        "symbolId": "authoring:sensor"
      },
      "fieldMap": {
        "deviceLabel": "label",
        "reference": "refdes",
        "value": "rating"
      },
      "portMap": {
        "in": "p-left",
        "out": "p-right"
      },
      "purpose": "primary-diagram"
    }
  ],
  "properties": [
    {
      "id": "refdes",
      "required": false,
      "type": "string"
    },
    {
      "id": "rating",
      "required": false,
      "type": "string"
    },
    {
      "id": "label",
      "required": false,
      "type": "string"
    }
  ]
}
```
<!-- /aixem-snippet -->

### Presentation Rules

- `purpose` selects a presentation class such as schematic.
- `asset.path`, `asset.digest`, `asset.symbolId`, and `asset.revision` form one locked asset reference.
- `portMap` direction is semantic component port ID → symbol port ID and must be total.
- `fieldMap` direction is symbol text field name → component property/entity attribute name.
- `defaultVariant` is used only when a placement does not explicitly select a variant.
- `parameterMap` is structurally reserved; 0.5.1 authoring must not depend on behavior absent from the renderer contract.
- multiple presentations may exist when each has an unambiguous purpose and independently valid lock/mapping.

### Component Property and Port Contract

A component port declares stable `id`, displayed `name`, electrical `type`, and optional `description`, `terminal`, `required`, and `metadata`. A component property declares stable `id`, `type`, and optional `default`, `description`, `required`, `unit`, and `values`.

Changing an endpoint set or meaning is a component compatibility change. Changing body graphics without changing the endpoint contract is normally a presentation revision.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
