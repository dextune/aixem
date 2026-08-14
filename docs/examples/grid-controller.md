---
id: AIXEM-EXAMPLE-CONTROLLER-001
title: 'Example: Grid Controller and Sensor Interface'
status: informative
version: '1.0'
language: en
domain: examples
kind: example
summary: Documents the bundled executable project with 17 entities, 20 semantic nets, 12 symbol assets, and explicit
  orthogonal routing.
authority:
- reference-example
aliases:
- grid controller
- controller example
- reference workbench
agent:
  priority: normal
  estimated_tokens: 820
  intents:
  - create-schematic
  - route-nets
  - validate-project
  - inspect-artifact
depends_on:
- AIXEM-SPEC-GRID-PROFILE-001
- AIXEM-SPEC-PROJECT-LOCK-001
related:
- AIXEM-START-QUICK-001
- AIXEM-SCHEM-VISUAL-001
- AIXEM-SPEC-VIEWER-001
navigation:
  group: examples
  order: 30
artifacts:
  owns:
  - examples/electronics-grid-controller/project.aixproj.json
  - examples/electronics-grid-controller/render/workbench.html
  consumes: []
requirements: []
---

# Example: Grid Controller and Sensor Interface

Documents the bundled executable project with 17 entities, 20 semantic nets, 12 symbol assets, and explicit orthogonal routing.

> **Document ID:** `AIXEM-EXAMPLE-CONTROLLER-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Examples demonstrate the normative model but do not supersede specifications.

The declared authority scopes are `reference-example`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Reference example.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Inspect project.aixproj.json
2. Read grid-controller.aixem
3. Inspect library and symbol bindings
4. Inspect explicit placements and routes
5. Run the renderer
6. Review project-validation.json and workbench.html

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `examples/electronics-grid-controller/project.aixproj.json`
- `examples/electronics-grid-controller/render/workbench.html`

## Operational Rules

- Preserve reference example as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- The renderer verifies schema closure, locked digests, endpoint mapping, grid placement, orthogonal routing, no-connect intent, and remote-asset denial.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Grid Schematic Profile 1](../specifications/schematic/grid-profile.md) — `AIXEM-SPEC-GRID-PROFILE-001`
- [Project Lock Contract 1](../specifications/project/project-lock-contract.md) — `AIXEM-SPEC-PROJECT-LOCK-001`
- [Quick Start](../getting-started/quick-start.md) — `AIXEM-START-QUICK-001`
- [Grid-First Visual Language](../schematic/visual-language.md) — `AIXEM-SCHEM-VISUAL-001`


## Reference Viewer Inspection

Open the generated `viewer.html` for normal inspection. It provides qualified selection, search, layer visibility, and viewport controls without authoring affordances. Open `workbench.html` only when validation diagnostics and provenance are part of the review. The Viewer Model and both HTML outputs are derived and do not replace source, layout, project, SVG, or resolved-scene authority.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
