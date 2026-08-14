---
id: AIXEM-ARCH-ADR-INDEX-001
title: Architecture Decision Records
status: informative
version: '1.0'
language: en
domain: architecture
kind: index
summary: Index of durable decisions that constrain the AIXEM 0.5 documentation and reference architecture.
authority:
- adr-navigation
aliases:
- ADR
- architecture decisions
- decision records
agent:
  priority: normal
  estimated_tokens: 730
  intents:
  - change-architecture
depends_on: []
related:
- AIXEM-ARCH-ADR-0001
- AIXEM-ARCH-ADR-0002
- AIXEM-ARCH-ADR-0003
navigation:
  group: architecture
  order: 70
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Architecture Decision Records

Index of durable decisions that constrain the AIXEM 0.5 documentation and reference architecture.

> **Document ID:** `AIXEM-ARCH-ADR-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

The architecture separates authored authority, generated products, validation evidence, and static consumption surfaces.

The declared authority scopes are `adr-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Decisions state context, choice, consequences, and supersession policy.
- Normative specifications remain the enforceable rule source.

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

- Preserve decisions state context, choice, consequences, and supersession policy as an explicit, reviewable part of the task.
- Preserve normative specifications remain the enforceable rule source as an explicit, reviewable part of the task.
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

- [ADR-0001: One Canonical Documentation Root](0001-canonical-doc-root.md) — `AIXEM-ARCH-ADR-0001`
- [ADR-0002: Route-First Agent Retrieval](0002-route-first-retrieval.md) — `AIXEM-ARCH-ADR-0002`
- [ADR-0003: Vendor-Neutral Engineering Workbench](0003-vendor-neutral-ui.md) — `AIXEM-ARCH-ADR-0003`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
