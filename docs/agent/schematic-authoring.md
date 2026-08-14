---
id: AIXEM-AGENT-SCHEMATIC-001
title: Schematic Authoring Agent
status: informative
version: '1.0'
language: en
domain: agent
kind: guide
summary: Provides an authority-safe agent sequence for creating or modifying semantic circuits, placements, routes,
  and project locks.
authority:
- agent-schematic-workflow
aliases:
- schematic agent
- AI schematic authoring
- agent draw circuit
agent:
  priority: normal
  estimated_tokens: 895
  intents:
  - create-schematic
depends_on:
- AIXEM-CONCEPT-AUTHORITY-001
- AIXEM-SCHEM-GRID-001
- AIXEM-ROUTE-NETS-001
related:
- AIXEM-AUTHORING-GUIDE-MODIFY-SCHEMATIC-001
- AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001
- AIXEM-START-FIRST-001
- AIXEM-AGENT-VALIDATION-001
navigation:
  group: agent
  order: 50
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Schematic Authoring Agent

Provides an authority-safe agent sequence for creating or modifying semantic circuits, placements, routes, and project locks.

> **Document ID:** `AIXEM-AGENT-SCHEMATIC-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

The procedure is designed to minimize context while preserving authority, traceability, and fail-closed behavior.

The declared authority scopes are `agent-schematic-workflow`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Agent schematic workflow.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve the create-schematic route
2. Read semantic and authority requirements
3. Create or update .aixem semantics
4. Resolve component and symbol assets
5. Place entities on the grid
6. Route semantic nets
7. Update the project lock
8. Render and validate
9. Inspect the workbench

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve agent schematic workflow as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- The agent must not infer a missing electrical connection from visual proximity.

## Placement and Existing-Edit Handoffs

After component selection and semantic closure, use the [Agent Component Placement Strategy](../authoring/guides/place-components.md) before routing. For an existing circuit, use [Modify Existing Schematic](../authoring/guides/modify-existing-schematic.md): preserve unaffected coordinates and route geometry, limit edits to the smallest affected authority region, and report any required wide redraw as a scope expansion.

Naming heuristics may rank otherwise equivalent geometry, but only explicit component, net, port, pin-semantics, interface, user-constraint, and existing-authority evidence may establish facts.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Authority Model](../concepts/authority-model.md) — `AIXEM-CONCEPT-AUTHORITY-001`
- [Grid and Snap System](../schematic/grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Semantic Net Routing](../routing/net-routing.md) — `AIXEM-ROUTE-NETS-001`
- [Create Your First Schematic](../getting-started/first-schematic.md) — `AIXEM-START-FIRST-001`
- [Three-Stage Validation Loop](validation-loop.md) — `AIXEM-AGENT-VALIDATION-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
