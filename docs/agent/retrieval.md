---
id: AIXEM-AGENT-RETRIEVAL-001
title: Bounded Retrieval
status: normative
version: '1.0'
language: en
domain: agent
kind: guide
summary: Defines intent normalization, exact route resolution, section-level loading, dependency expansion, fallback
  search, and context accounting.
authority:
- agent-retrieval-workflow
aliases:
- bounded retrieval
- agent search
- document lookup
agent:
  priority: high
  estimated_tokens: 695
  intents:
  - build-documentation
  - change-architecture
  - inspect-artifact
depends_on:
- AIXEM-SPEC-AGENT-RETRIEVAL-001
related:
- AIXEM-AGENT-ROUTES-001
- AIXEM-ARCH-CACHE-001
navigation:
  group: agent
  order: 30
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Bounded Retrieval

Defines intent normalization, exact route resolution, section-level loading, dependency expansion, fallback search, and context accounting.

> **Document ID:** `AIXEM-AGENT-RETRIEVAL-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The procedure is designed to minimize context while preserving authority, traceability, and fail-closed behavior.

The declared authority scopes are `agent-retrieval-workflow`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Agent retrieval workflow.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Normalize the task phrase
2. Resolve an exact intent or alias
3. Load the route in declared order
4. Load only named sections
5. Follow conditional dependencies only when triggered
6. Stop at completion conditions
7. Use the inverted index only when no route resolves

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve agent retrieval workflow as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- A repository-wide search is a controlled fallback for migrations, route defects, or inherently exhaustive audits.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Agent Retrieval Profile 1](../specifications/agent/retrieval-profile.md) — `AIXEM-SPEC-AGENT-RETRIEVAL-001`
- [Task Routes](task-routing.md) — `AIXEM-AGENT-ROUTES-001`
- [Cache and Incremental Compilation](../architecture/cache.md) — `AIXEM-ARCH-CACHE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
