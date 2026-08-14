---
id: AIXEM-EXAMPLE-INDEX-001
title: Examples
status: informative
version: '1.0'
language: en
domain: examples
kind: index
summary: A progression from a minimal passive circuit to the complete grid-controller reference and a hierarchical
  design pattern.
authority:
- example-navigation
aliases:
- examples
- sample schematics
- demo projects
agent:
  priority: normal
  estimated_tokens: 930
  intents:
  - create-schematic
  - learn-aixem
depends_on: []
related:
- AIXEM-EXAMPLE-BASIC-001
- AIXEM-EXAMPLE-CONTROLLER-001
- AIXEM-EXAMPLE-HIERARCHY-001
navigation:
  group: examples
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Examples

A progression from a minimal passive circuit to the complete grid-controller reference and a hierarchical design pattern.

> **Document ID:** `AIXEM-EXAMPLE-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Examples demonstrate the normative model but do not supersede specifications.

The declared authority scopes are `example-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Examples demonstrate rather than redefine requirements.
- The grid-controller project is executable.
- Smaller examples focus on authoring decisions.

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

- Preserve examples demonstrate rather than redefine requirements as an explicit, reviewable part of the task.
- Preserve the grid-controller project is executable as an explicit, reviewable part of the task.
- Preserve smaller examples focus on authoring decisions as an explicit, reviewable part of the task.
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

- [Example: Passive Divider](passive-divider.md) — `AIXEM-EXAMPLE-BASIC-001`
- [Example: Grid Controller and Sensor Interface](grid-controller.md) — `AIXEM-EXAMPLE-CONTROLLER-001`
- [Example: Hierarchical Reference Pattern](hierarchical-reference.md) — `AIXEM-EXAMPLE-HIERARCHY-001`

## Hierarchical Corpus Examples

The executable H001–H015 cases under `validation/corpus/hierarchical-project-1` are the conformance-backed multi-sheet examples for 0.5.3.

## Complete Section Map

This list is the complete authored link surface for the `examples` navigation section. The navigation registry remains the machine-readable membership owner.

- [Example: Passive Divider](passive-divider.md) — `AIXEM-EXAMPLE-BASIC-001`
- [Example: Grid Controller and Sensor Interface](grid-controller.md) — `AIXEM-EXAMPLE-CONTROLLER-001`
- [Example: Hierarchical Reference Pattern](hierarchical-reference.md) — `AIXEM-EXAMPLE-HIERARCHY-001`
- [Symbol Expressiveness Corpus Construction Index](symbol-expressiveness-corpus.md) — `AIXEM-EXAMPLE-SYMBOL-CORPUS-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
