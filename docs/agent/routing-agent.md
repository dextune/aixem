---
id: AIXEM-AGENT-ROUTING-001
title: Routing Agent
status: informative
version: '1.0'
language: en
domain: agent
kind: guide
summary: Provides an agent sequence for deterministic orthogonal routing with explicit crossings, junctions, and
  local repair.
authority:
- agent-routing-workflow
aliases:
- routing agent
- AI wire routing
- automatic routing
agent:
  priority: normal
  estimated_tokens: 925
  intents:
  - route-nets
  - route-project-nets
depends_on:
- AIXEM-ROUTE-BEHAVIOR-001
- AIXEM-ROUTE-CONSTRAINT-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-AGENT-VALIDATION-001
- AIXEM-CONCEPT-PROJECT-NET-001
navigation:
  group: agent
  order: 70
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Routing Agent

Provides an agent sequence for deterministic orthogonal routing with explicit crossings, junctions, and local repair.

> **Document ID:** `AIXEM-AGENT-ROUTING-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

The procedure is designed to minimize context while preserving authority, traceability, and fail-closed behavior.

The declared authority scopes are `agent-routing-workflow`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Agent routing workflow.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Read net membership
2. Resolve all placed terminal coordinates
3. Build obstacles and preferred channels
4. Route highest-constraint nets first
5. Minimize bends and ambiguous crossings
6. Declare intended junctions
7. Validate closure and grid alignment
8. Repair only the failing local route

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve agent routing workflow as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

## Explicit Semantic Preference Boundary

Signal class, power-domain, functional tags, and differential-pair metadata may guide route ordering or geometric preference only when explicitly declared by component authority. Names such as `D+`, `RESET_N`, or `CLK` are weak hints and cannot create pair membership, polarity, connectivity, or a new net.

Differential metadata in this release supports coherent departure and arrival geometry; it does not claim PCB impedance, length matching, timing, or signal-integrity correctness.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Router Behavior](../routing/router-behavior.md) — `AIXEM-ROUTE-BEHAVIOR-001`
- [Route Constraints](../routing/route-constraints.md) — `AIXEM-ROUTE-CONSTRAINT-001`
- [Three-Stage Validation Loop](validation-loop.md) — `AIXEM-AGENT-VALIDATION-001`

## Local Versus Project Routing Discipline

`route-nets` remains leaf-scoped and may edit only local `.aixlayout.json` connection geometry. `route-project-nets` reads closed project-net membership and resolved interface anchors to create Overview/Composite geometry. It must never add, remove, or rename project-net members merely to improve a drawing.

When a project route fails, classify the owner first: missing port semantics, missing leaf presentation, invalid project membership, or project-router geometry. Repair the smallest owning layer.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
