---
id: AIXEM-EXAMPLE-BASIC-001
title: 'Example: Passive Divider'
status: informative
version: '1.0'
language: en
domain: examples
kind: example
summary: Walks through the semantic, symbol, placement, and routing decisions for a two-resistor divider with an output
  test point.
authority:
- example
aliases:
- passive divider
- resistor divider example
- basic schematic
agent:
  priority: normal
  estimated_tokens: 767
  intents:
  - create-schematic
  - learn-aixem
depends_on:
- AIXEM-START-FIRST-001
related:
- AIXEM-SCHEM-GRID-001
- AIXEM-ROUTE-NETS-001
- AIXEM-SPEC-VIEWER-001
navigation:
  group: examples
  order: 20
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Example: Passive Divider

Walks through the semantic, symbol, placement, and routing decisions for a two-resistor divider with an output test point.

> **Document ID:** `AIXEM-EXAMPLE-BASIC-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Examples demonstrate the normative model but do not supersede specifications.

The declared authority scopes are `example`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Example.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Declare VIN, VOUT, and GND nets
2. Instantiate two resistor components and a test point
3. Place components on the 2.5 mm grid
4. Route three orthogonal nets
5. Declare references and values
6. Lock and validate the project

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve example as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- This narrative example intentionally omits a second executable project so the release has one authoritative renderer fixture.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Create Your First Schematic](../getting-started/first-schematic.md) — `AIXEM-START-FIRST-001`
- [Grid and Snap System](../schematic/grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Semantic Net Routing](../routing/net-routing.md) — `AIXEM-ROUTE-NETS-001`


## Reference Viewer Inspection

Open the generated `viewer.html` for normal inspection. It provides qualified selection, search, layer visibility, and viewport controls without authoring affordances. Open `workbench.html` only when validation diagnostics and provenance are part of the review. The Viewer Model and both HTML outputs are derived and do not replace source, layout, project, SVG, or resolved-scene authority.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
