---
id: AIXEM-SYMBOL-INDEX-001
title: Symbol Authoring
status: informative
version: '1.0'
language: en
domain: symbols
kind: index
summary: Guidance for compact, grid-aligned, endpoint-safe, independently authored schematic symbols.
authority:
- symbol-guide-navigation
aliases:
- symbols
- symbol authoring
- symbol library
agent:
  priority: normal
  estimated_tokens: 900
  intents:
  - create-symbol
  - create-schematic
depends_on: []
related:
- AIXEM-SYMBOL-ANATOMY-001
- AIXEM-SYMBOL-AUTHORING-001
- AIXEM-SPEC-SYMBOL-001
navigation:
  group: symbols
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Symbol Authoring

Guidance for compact, grid-aligned, endpoint-safe, independently authored schematic symbols.

> **Document ID:** `AIXEM-SYMBOL-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Symbol graphics are presentation assets. Endpoint identity remains owned by the component and semantic layers.

The declared authority scopes are `symbol-guide-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Stable endpoint identity.
- Body and port separation.
- Deterministic field anchors.
- Lintable geometry.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Identify the reader or agent task before selecting a document.
2. Read the minimum linked concept or guide required for that task.
3. Use the normative specification when a rule affects compatibility or conformance.
4. Finish with the relevant validation and evidence page.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve stable endpoint identity as an explicit, reviewable part of the task.
- Preserve body and port separation as an explicit, reviewable part of the task.
- Preserve deterministic field anchors as an explicit, reviewable part of the task.
- Preserve lintable geometry as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Symbol Anatomy](symbol-anatomy.md) — `AIXEM-SYMBOL-ANATOMY-001`
- [Symbol Authoring Guide](authoring-guide.md) — `AIXEM-SYMBOL-AUTHORING-001`
- [Symbol Asset Contract 1](../specifications/symbols/symbol-contract.md) — `AIXEM-SPEC-SYMBOL-001`

## Complete Section Map

This list is the complete authored link surface for the `symbols` navigation section. The navigation registry remains the machine-readable membership owner.

- [Symbol Anatomy](symbol-anatomy.md) — `AIXEM-SYMBOL-ANATOMY-001`
- [Pins, Ports, and Endpoint Mapping](pins-and-ports.md) — `AIXEM-SYMBOL-PORTS-001`
- [Graphic Primitives](primitives.md) — `AIXEM-SYMBOL-PRIMITIVES-001`
- [Symbol Authoring Guide](authoring-guide.md) — `AIXEM-SYMBOL-AUTHORING-001`
- [Symbol Variants](variants.md) — `AIXEM-SYMBOL-VARIANTS-001`
- [Field Layout](field-layout.md) — `AIXEM-SYMBOL-FIELDS-001`
- [Symbol Design Rules Entry Point](design-rules.md) — `AIXEM-SYMBOL-DESIGN-RULES-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
