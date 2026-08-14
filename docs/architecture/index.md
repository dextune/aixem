---
id: AIXEM-ARCH-INDEX-001
title: System Architecture
status: informative
version: '1.0'
language: en
domain: architecture
kind: index
summary: A component and data-flow view of the canonical documentation compiler, agent reference layer, schematic
  pipeline, validators, and static publication outputs.
authority:
- architecture-navigation
aliases:
- architecture
- system design
- platform architecture
agent:
  priority: normal
  estimated_tokens: 1015
  intents:
  - change-architecture
  - inspect-artifact
depends_on: []
related:
- AIXEM-ARCH-SYSTEM-001
- AIXEM-ARCH-PIPELINE-001
- AIXEM-ARCH-ADR-INDEX-001
navigation:
  group: architecture
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# System Architecture

A component and data-flow view of the canonical documentation compiler, agent reference layer, schematic pipeline, validators, and static publication outputs.

> **Document ID:** `AIXEM-ARCH-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

The architecture separates authored authority, generated products, validation evidence, and static consumption surfaces.

The declared authority scopes are `architecture-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Canonical source plane.
- Compilation and validation plane.
- Static consumption plane.
- Evidence and release plane.

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

- Preserve canonical source plane as an explicit, reviewable part of the task.
- Preserve compilation and validation plane as an explicit, reviewable part of the task.
- Preserve static consumption plane as an explicit, reviewable part of the task.
- Preserve evidence and release plane as an explicit, reviewable part of the task.
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

- [System Overview](system-overview.md) — `AIXEM-ARCH-SYSTEM-001`
- [Build and Authoring Pipeline](pipeline.md) — `AIXEM-ARCH-PIPELINE-001`
- [Architecture Decision Records](adr/index.md) — `AIXEM-ARCH-ADR-INDEX-001`

## Complete Section Map

This list is the complete authored link surface for the `architecture` navigation section. The navigation registry remains the machine-readable membership owner.

- [System Overview](system-overview.md) — `AIXEM-ARCH-SYSTEM-001`
- [Build and Authoring Pipeline](pipeline.md) — `AIXEM-ARCH-PIPELINE-001`
- [Artifact Ownership and Storage](artifact-store.md) — `AIXEM-ARCH-ARTIFACT-001`
- [Cache and Incremental Compilation](cache.md) — `AIXEM-ARCH-CACHE-001`
- [Security and Trust Boundaries](security.md) — `AIXEM-ARCH-SECURITY-001`
- [Architecture Decision Records](adr/index.md) — `AIXEM-ARCH-ADR-INDEX-001`
- [ADR-0001: One Canonical Documentation Root](adr/0001-canonical-doc-root.md) — `AIXEM-ARCH-ADR-0001`
- [ADR-0002: Route-First Agent Retrieval](adr/0002-route-first-retrieval.md) — `AIXEM-ARCH-ADR-0002`
- [ADR-0003: Vendor-Neutral Engineering Surfaces](adr/0003-vendor-neutral-ui.md) — `AIXEM-ARCH-ADR-0003`
- [ADR 0004 — Symbol Style and Renderer Precedence](adr/0004-symbol-style-and-renderer-precedence.md) — `AIXEM-ARCH-ADR-0004`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
