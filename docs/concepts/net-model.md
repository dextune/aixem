---
id: AIXEM-CONCEPT-NET-001
title: Net Model
status: normative
version: '1.0'
language: en
domain: concepts
kind: concept
summary: Defines net membership, endpoint closure, labels, and the separation between logical nets and route paths.
authority:
- net-semantics
aliases:
- net model
- logical net
- network connectivity
agent:
  priority: critical
  estimated_tokens: 919
  intents:
  - create-schematic
  - route-nets
  - validate-project
  - compose-project
depends_on:
- AIXEM-CONCEPT-SEMANTIC-001
related:
- AIXEM-ROUTE-NETS-001
- AIXEM-SCHEM-JUNCTION-001
- AIXEM-CONCEPT-PROJECT-NET-001
navigation:
  group: concepts
  order: 50
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-CORE-0013
  title: Explicit membership
  level: MUST
  statement: Net membership MUST be declared as endpoint references in semantic source data.
  validator: schematic.semantic
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0013.json
- id: AIXEM-REQ-CORE-0014
  title: No contradictory intent
  level: MUST
  statement: An endpoint MUST NOT be both a member of a net and explicitly marked no-connect.
  validator: schematic.no_connect
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0014.json
---

# Net Model

Defines net membership, endpoint closure, labels, and the separation between logical nets and route paths.

> **Document ID:** `AIXEM-CONCEPT-NET-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The model described here is independent from any particular renderer or workbench implementation.

The declared authority scopes are `net-semantics`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- A net can have multiple routed paths.
- A label can expose a net name without changing membership.
- Route topology is validated against semantic membership.

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

<a id="AIXEM-REQ-CORE-0013"></a>

### AIXEM-REQ-CORE-0013 — Explicit membership

**MUST.** Net membership MUST be declared as endpoint references in semantic source data.

- Verification mode: `automated`
- Validator: `schematic.semantic`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0013.json`

<a id="AIXEM-REQ-CORE-0014"></a>

### AIXEM-REQ-CORE-0014 — No contradictory intent

**MUST.** An endpoint MUST NOT be both a member of a net and explicitly marked no-connect.

- Verification mode: `automated`
- Validator: `schematic.no_connect`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0014.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Semantic Circuit Model](semantic-model.md) — `AIXEM-CONCEPT-SEMANTIC-001`
- [Semantic Net Routing](../routing/net-routing.md) — `AIXEM-ROUTE-NETS-001`
- [Junctions and Connectivity Cues](../schematic/junctions.md) — `AIXEM-SCHEM-JUNCTION-001`

## Local Nets and Project Nets

A local net is owned by one `.aixem` leaf. A project net is owned by `aixproj/2` and connects declared interface ports from independent leaves. The resolver computes transitive equivalence while preserving both scopes and rejects two project-net IDs that collapse through one local net. Matching names are never authority. See [Project Net Model](project-net-model.md).

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
