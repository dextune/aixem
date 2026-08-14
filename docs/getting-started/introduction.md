---
id: AIXEM-START-INTRO-001
title: Introduction to AIXEM
status: informative
version: '1.0'
language: en
domain: getting-started
kind: concept
summary: Introduces AIXEM as a vendor-neutral, machine-authorable schematic system with explicit authority boundaries.
authority:
- onboarding
- product-definition
aliases:
- introduction
- what is AIXEM
- AIXEM overview
agent:
  priority: normal
  estimated_tokens: 756
  intents:
  - learn-aixem
  - discover-documentation
depends_on: []
related:
- AIXEM-CONCEPT-AUTHORITY-001
- AIXEM-ARCH-SYSTEM-001
navigation:
  group: getting-started
  order: 20
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Introduction to AIXEM

Introduces AIXEM as a vendor-neutral, machine-authorable schematic system with explicit authority boundaries.

> **Document ID:** `AIXEM-START-INTRO-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

This page is part of the shortest supported learning path and intentionally points to deeper normative material rather than duplicating it.

The declared authority scopes are `onboarding`, `product-definition`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Semantic connectivity is authoritative.
- Symbol graphics are independent assets.
- Explicit layout is presentation geometry.
- Project locks make rendering reproducible.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Confirm the goal and the owning authority layer.
2. Follow the task sequence described on this page.
3. Open related normative documents only when a binding rule is required.
4. Validate the resulting authoritative and generated artifacts.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve semantic connectivity is authoritative as an explicit, reviewable part of the task.
- Preserve symbol graphics are independent assets as an explicit, reviewable part of the task.
- Preserve explicit layout is presentation geometry as an explicit, reviewable part of the task.
- Preserve project locks make rendering reproducible as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- AIXEM uses familiar engineering-CAD interaction patterns while retaining original AIXEM assets, names, and implementation.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Authority Model](../concepts/authority-model.md) — `AIXEM-CONCEPT-AUTHORITY-001`
- [System Overview](../architecture/system-overview.md) — `AIXEM-ARCH-SYSTEM-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
