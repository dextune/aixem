---
id: AIXEM-START-FIRST-001
title: Create Your First Schematic
status: informative
version: '1.0'
language: en
domain: getting-started
kind: guide
summary: Shows the minimum authoring sequence for semantic source, library binding, symbol assets, layout, project
  lock, render, and validation.
authority:
- schematic-authoring-workflow
aliases:
- first schematic
- new schematic tutorial
- create circuit
agent:
  priority: normal
  estimated_tokens: 698
  intents:
  - create-schematic
depends_on:
- AIXEM-CONCEPT-AUTHORITY-001
- AIXEM-FORMAT-AIXEM-001
- AIXEM-FORMAT-AIXPROJ-001
related:
- AIXEM-AGENT-SCHEMATIC-001
- AIXEM-SCHEM-GRID-001
- AIXEM-ROUTE-ORTHO-001
navigation:
  group: getting-started
  order: 40
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Create Your First Schematic

Shows the minimum authoring sequence for semantic source, library binding, symbol assets, layout, project lock, render, and validation.

> **Document ID:** `AIXEM-START-FIRST-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

This page is part of the shortest supported learning path and intentionally points to deeper normative material rather than duplicating it.

The declared authority scopes are `schematic-authoring-workflow`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Schematic authoring workflow.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Declare semantic entities and nets
2. Bind component definitions
3. Select or author symbol assets
4. Place components on the snap grid
5. Route each semantic net orthogonally
6. Lock all input digests
7. Render and validate

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve schematic authoring workflow as an explicit, reviewable part of the task.
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

- [Authority Model](../concepts/authority-model.md) — `AIXEM-CONCEPT-AUTHORITY-001`
- [.aixem Semantic Source](../file-formats/aixem.md) — `AIXEM-FORMAT-AIXEM-001`
- [.aixproj.json Project Lock](../file-formats/aixproj.md) — `AIXEM-FORMAT-AIXPROJ-001`
- [Schematic Authoring Agent](../agent/schematic-authoring.md) — `AIXEM-AGENT-SCHEMATIC-001`
- [Grid and Snap System](../schematic/grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Orthogonal Routing](../routing/orthogonal-routing.md) — `AIXEM-ROUTE-ORTHO-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
