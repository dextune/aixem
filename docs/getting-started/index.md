---
id: AIXEM-START-INDEX-001
title: Getting Started
status: informative
version: '1.0'
language: en
domain: getting-started
kind: index
summary: A short learning path from the AIXEM model to a rendered and validated schematic.
authority:
- onboarding
aliases:
- getting started
- onboarding
- start AIXEM
agent:
  priority: normal
  estimated_tokens: 741
  intents:
  - learn-aixem
  - create-schematic
depends_on: []
related:
- AIXEM-START-INTRO-001
- AIXEM-START-QUICK-001
- AIXEM-START-FIRST-001
navigation:
  group: getting-started
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Getting Started

A short learning path from the AIXEM model to a rendered and validated schematic.

> **Document ID:** `AIXEM-START-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

This page is part of the shortest supported learning path and intentionally points to deeper normative material rather than duplicating it.

The declared authority scopes are `onboarding`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Read only the minimum concepts needed for a first project.
- Keep semantics, graphics, and layout separate.
- Validate before publishing.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Read Introduction
2. Run Quick Start
3. Build the First Schematic

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve read only the minimum concepts needed for a first project as an explicit, reviewable part of the task.
- Preserve keep semantics, graphics, and layout separate as an explicit, reviewable part of the task.
- Preserve validate before publishing as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Introduction to AIXEM](introduction.md) — `AIXEM-START-INTRO-001`
- [Quick Start](quick-start.md) — `AIXEM-START-QUICK-001`
- [Create Your First Schematic](first-schematic.md) — `AIXEM-START-FIRST-001`

## Complete Section Map

This list is the complete authored link surface for the `getting-started` navigation section. The navigation registry remains the machine-readable membership owner.

- [Introduction to AIXEM](introduction.md) — `AIXEM-START-INTRO-001`
- [Quick Start](quick-start.md) — `AIXEM-START-QUICK-001`
- [Create Your First Schematic](first-schematic.md) — `AIXEM-START-FIRST-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
