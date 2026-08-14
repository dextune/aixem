---
id: AIXEM-CONCEPT-INDEX-001
title: Core Concepts
status: informative
version: '1.0'
language: en
domain: concepts
kind: index
summary: Explains the authority layers and data model that keep circuit meaning independent from drawing geometry.
authority:
- concept-navigation
aliases:
- concepts
- core concepts
- data model
agent:
  priority: normal
  estimated_tokens: 958
  intents:
  - learn-aixem
  - change-architecture
depends_on: []
related:
- AIXEM-CONCEPT-SEMANTIC-001
- AIXEM-CONCEPT-AUTHORITY-001
- AIXEM-CONCEPT-DETERMINISM-001
navigation:
  group: concepts
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Core Concepts

Explains the authority layers and data model that keep circuit meaning independent from drawing geometry.

> **Document ID:** `AIXEM-CONCEPT-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

The model described here is independent from any particular renderer or workbench implementation.

The declared authority scopes are `concept-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Semantic circuit model.
- Component and endpoint identity.
- Symbol presentation.
- Explicit layout.
- Locked deterministic build.

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

- Preserve semantic circuit model as an explicit, reviewable part of the task.
- Preserve component and endpoint identity as an explicit, reviewable part of the task.
- Preserve symbol presentation as an explicit, reviewable part of the task.
- Preserve explicit layout as an explicit, reviewable part of the task.
- Preserve locked deterministic build as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Semantic Circuit Model](semantic-model.md) — `AIXEM-CONCEPT-SEMANTIC-001`
- [Authority Model](authority-model.md) — `AIXEM-CONCEPT-AUTHORITY-001`
- [Deterministic Builds](deterministic-builds.md) — `AIXEM-CONCEPT-DETERMINISM-001`

## Hierarchical Composition Concept

- [Project Net Model](project-net-model.md) explains local-net/project-net scope, transitive closure, and routing separation.

## Complete Section Map

This list is the complete authored link surface for the `concepts` navigation section. The navigation registry remains the machine-readable membership owner.

- [Semantic Circuit Model](semantic-model.md) — `AIXEM-CONCEPT-SEMANTIC-001`
- [Authority Model](authority-model.md) — `AIXEM-CONCEPT-AUTHORITY-001`
- [Component Model](component-model.md) — `AIXEM-CONCEPT-COMPONENT-001`
- [Net Model](net-model.md) — `AIXEM-CONCEPT-NET-001`
- [Symbol Presentation Model](symbol-model.md) — `AIXEM-CONCEPT-SYMBOL-001`
- [Explicit Layout Model](layout-model.md) — `AIXEM-CONCEPT-LAYOUT-001`
- [Deterministic Builds](deterministic-builds.md) — `AIXEM-CONCEPT-DETERMINISM-001`
- [Project Net Model](project-net-model.md) — `AIXEM-CONCEPT-PROJECT-NET-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
