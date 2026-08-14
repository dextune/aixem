---
id: AIXEM-AGENT-INDEX-001
title: AI Agent Operations
status: informative
version: '1.0'
language: en
domain: agent
kind: index
summary: The operational entrypoint for bounded retrieval, authority-aware modification, schematic authoring, validation,
  and release work by AI agents.
authority:
- agent-guide-navigation
aliases:
- AI agent
- agent operations
- agent docs
agent:
  priority: normal
  estimated_tokens: 1030
  intents:
  - change-architecture
  - create-schematic
  - create-symbol
  - route-nets
depends_on: []
related:
- AIXEM-AGENT-ARCH-001
- AIXEM-AGENT-RETRIEVAL-001
- AIXEM-AGENT-VALIDATION-001
navigation:
  group: agent
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# AI Agent Operations

The operational entrypoint for bounded retrieval, authority-aware modification, schematic authoring, validation, and release work by AI agents.

> **Document ID:** `AIXEM-AGENT-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

The procedure is designed to minimize context while preserving authority, traceability, and fail-closed behavior.

The declared authority scopes are `agent-guide-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Route first.
- Read within a declared budget.
- Modify the owning authority.
- Regenerate and prove the result.

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

- Preserve route first as an explicit, reviewable part of the task.
- Preserve read within a declared budget as an explicit, reviewable part of the task.
- Preserve modify the owning authority as an explicit, reviewable part of the task.
- Preserve regenerate and prove the result as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Agent Architecture](architecture.md) — `AIXEM-AGENT-ARCH-001`
- [Bounded Retrieval](retrieval.md) — `AIXEM-AGENT-RETRIEVAL-001`
- [Three-Stage Validation Loop](validation-loop.md) — `AIXEM-AGENT-VALIDATION-001`

## Hierarchical Task Routes

Use `compose-project` to close sheet registration, hierarchy, and project-net membership. Use `route-project-nets` only for deterministic Overview/Composite geometry after semantic closure.

## Complete Section Map

This list is the complete authored link surface for the `agent` navigation section. The navigation registry remains the machine-readable membership owner.

- [Agent Architecture](architecture.md) — `AIXEM-AGENT-ARCH-001`
- [Bounded Retrieval](retrieval.md) — `AIXEM-AGENT-RETRIEVAL-001`
- [Task Routes](task-routing.md) — `AIXEM-AGENT-ROUTES-001`
- [Schematic Authoring Agent](schematic-authoring.md) — `AIXEM-AGENT-SCHEMATIC-001`
- [Symbol Generation Agent](symbol-generation.md) — `AIXEM-AGENT-SYMBOL-001`
- [Routing Agent](routing-agent.md) — `AIXEM-AGENT-ROUTING-001`
- [Three-Stage Validation Loop](validation-loop.md) — `AIXEM-AGENT-VALIDATION-001`
- [Fail-Closed Policy](failure-policy.md) — `AIXEM-AGENT-FAILURE-001`
- [Agent Authoring Orchestration](authoring-orchestration.md) — `AIXEM-AGENT-AUTHORING-001`
- [Live-Agent Cold-Start Authoring](live-agent-cold-start-authoring.md) — `AIXEM-AGENT-LIVE-COLD-START-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
