---
id: AIXEM-ROUTE-INDEX-001
title: Net Routing
status: informative
version: '1.0'
language: en
domain: routing
kind: index
summary: Guidance for explicit, orthogonal, grid-aligned route geometry bound to semantic nets.
authority:
- routing-guide-navigation
aliases:
- routing
- net routing
- wire routing
agent:
  priority: normal
  estimated_tokens: 920
  intents:
  - route-nets
  - create-schematic
depends_on: []
related:
- AIXEM-ROUTE-NETS-001
- AIXEM-ROUTE-ORTHO-001
- AIXEM-ROUTE-CONSTRAINT-001
navigation:
  group: routing
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Net Routing

Guidance for explicit, orthogonal, grid-aligned route geometry bound to semantic nets.

> **Document ID:** `AIXEM-ROUTE-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Routing records present semantic nets; they never create net membership through geometry.

The declared authority scopes are `routing-guide-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Route by semantic net.
- Use horizontal and vertical segments.
- Declare junctions explicitly.
- Optimize readability rather than geometric shortest path alone.

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

- Preserve route by semantic net as an explicit, reviewable part of the task.
- Preserve use horizontal and vertical segments as an explicit, reviewable part of the task.
- Preserve declare junctions explicitly as an explicit, reviewable part of the task.
- Preserve optimize readability rather than geometric shortest path alone as an explicit, reviewable part of the task.
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

- [Semantic Net Routing](net-routing.md) — `AIXEM-ROUTE-NETS-001`
- [Orthogonal Routing](orthogonal-routing.md) — `AIXEM-ROUTE-ORTHO-001`
- [Route Constraints](route-constraints.md) — `AIXEM-ROUTE-CONSTRAINT-001`

## Project Routing Boundary

Local routing remains owned by `route-nets`; project-level sheet-to-sheet routing is a separate derived operation selected through `route-project-nets`.

## Complete Section Map

This list is the complete authored link surface for the `routing` navigation section. The navigation registry remains the machine-readable membership owner.

- [Semantic Net Routing](net-routing.md) — `AIXEM-ROUTE-NETS-001`
- [Orthogonal Routing](orthogonal-routing.md) — `AIXEM-ROUTE-ORTHO-001`
- [Route Constraints](route-constraints.md) — `AIXEM-ROUTE-CONSTRAINT-001`
- [Router Behavior](router-behavior.md) — `AIXEM-ROUTE-BEHAVIOR-001`
- [Crossings and Junctions](crossings-and-junctions.md) — `AIXEM-ROUTE-CROSSING-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
