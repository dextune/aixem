---
id: AIXEM-ARCH-ADR-0002
title: 'ADR-0002: Route-First Agent Retrieval'
status: normative
version: '1.0'
language: en
domain: architecture
kind: adr
summary: Records the decision to resolve known work through bounded task routes before full-text or repository-wide
  search.
authority:
- architecture-decision
aliases:
- route first ADR
- bounded retrieval ADR
- ADR 0002
agent:
  priority: high
  estimated_tokens: 743
  intents:
  - build-documentation
  - change-architecture
depends_on:
- AIXEM-SPEC-AGENT-RETRIEVAL-001
related:
- AIXEM-AGENT-ROUTES-001
navigation:
  group: architecture
  order: 90
artifacts:
  owns: []
  consumes: []
requirements: []
---

# ADR-0002: Route-First Agent Retrieval

Records the decision to resolve known work through bounded task routes before full-text or repository-wide search.

> **Document ID:** `AIXEM-ARCH-ADR-0002`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The architecture separates authored authority, generated products, validation evidence, and static consumption surfaces.

The declared authority scopes are `architecture-decision`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Accepted decision.
- Exact intent and alias lookup comes first.
- Default budget is seven documents and 96 KiB.
- Search remains a controlled fallback.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve accepted decision as an explicit, reviewable part of the task.
- Preserve exact intent and alias lookup comes first as an explicit, reviewable part of the task.
- Preserve default budget is seven documents and 96 kib as an explicit, reviewable part of the task.
- Preserve search remains a controlled fallback as an explicit, reviewable part of the task.
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

- [Agent Retrieval Profile 1](../../specifications/agent/retrieval-profile.md) — `AIXEM-SPEC-AGENT-RETRIEVAL-001`
- [Task Routes](../../agent/task-routing.md) — `AIXEM-AGENT-ROUTES-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
