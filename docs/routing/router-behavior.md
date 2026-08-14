---
id: AIXEM-ROUTE-BEHAVIOR-001
title: Router Behavior
status: informative
version: '1.0'
language: en
domain: routing
kind: guide
summary: Describes a deterministic route-agent workflow, cost model, fallback sequence, and evidence output.
authority:
- routing-agent-guidance
aliases:
- router behavior
- auto router
- routing algorithm
agent:
  priority: normal
  estimated_tokens: 661
  intents:
  - route-nets
  - change-architecture
depends_on:
- AIXEM-ROUTE-CONSTRAINT-001
related:
- AIXEM-AGENT-ROUTING-001
- AIXEM-ARCH-PIPELINE-001
navigation:
  group: routing
  order: 50
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Router Behavior

Describes a deterministic route-agent workflow, cost model, fallback sequence, and evidence output.

> **Document ID:** `AIXEM-ROUTE-BEHAVIOR-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Routing records present semantic nets; they never create net membership through geometry.

The declared authority scopes are `routing-agent-guidance`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Routing agent guidance.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Build the obstacle and channel map
2. Resolve net terminal order
3. Generate orthogonal candidates
4. Score bends, length, crossings, congestion, and label clearance
5. Commit the best valid path
6. Validate and locally repair
7. Emit route evidence

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve routing agent guidance as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- The reference profile favors predictable readability over aggressive geometric compaction.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Route Constraints](route-constraints.md) — `AIXEM-ROUTE-CONSTRAINT-001`
- [Routing Agent](../agent/routing-agent.md) — `AIXEM-AGENT-ROUTING-001`
- [Build and Authoring Pipeline](../architecture/pipeline.md) — `AIXEM-ARCH-PIPELINE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
