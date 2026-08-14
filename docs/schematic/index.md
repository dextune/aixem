---
id: AIXEM-SCHEM-INDEX-001
title: Schematic Authoring
status: informative
version: '1.0'
language: en
domain: schematic
kind: index
summary: A task-oriented guide to grid-first placement, explicit connectivity cues, annotation, and sheet organization.
authority:
- schematic-guide-navigation
aliases:
- schematic guide
- draw schematic
- schematic authoring
agent:
  priority: normal
  estimated_tokens: 898
  intents:
  - create-schematic
  - route-nets
depends_on: []
related:
- AIXEM-SCHEM-GRID-001
- AIXEM-SCHEM-VISUAL-001
- AIXEM-ROUTE-INDEX-001
navigation:
  group: schematic
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Schematic Authoring

A task-oriented guide to grid-first placement, explicit connectivity cues, annotation, and sheet organization.

> **Document ID:** `AIXEM-SCHEM-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

These rules prioritize a compact, grid-aligned engineering drawing that remains unambiguous when printed or viewed without color.

The declared authority scopes are `schematic-guide-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Grid before detail.
- Readable left-to-right signal flow.
- Explicit junction and no-connect cues.
- Compact and deterministic symbols.

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

- Preserve grid before detail as an explicit, reviewable part of the task.
- Preserve readable left-to-right signal flow as an explicit, reviewable part of the task.
- Preserve explicit junction and no-connect cues as an explicit, reviewable part of the task.
- Preserve compact and deterministic symbols as an explicit, reviewable part of the task.
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

- [Grid and Snap System](grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Grid-First Visual Language](visual-language.md) — `AIXEM-SCHEM-VISUAL-001`
- [Net Routing](../routing/index.md) — `AIXEM-ROUTE-INDEX-001`

## Complete Section Map

This list is the complete authored link surface for the `schematic` navigation section. The navigation registry remains the machine-readable membership owner.

- [Grid and Snap System](grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Component Placement](placement.md) — `AIXEM-SCHEM-PLACEMENT-001`
- [Junctions and Connectivity Cues](junctions.md) — `AIXEM-SCHEM-JUNCTION-001`
- [Annotations and Fields](annotations.md) — `AIXEM-SCHEM-ANNOTATION-001`
- [Grid-First Visual Language](visual-language.md) — `AIXEM-SCHEM-VISUAL-001`
- [Sheet Organization](sheet-organization.md) — `AIXEM-SCHEM-SHEET-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
