---
id: AIXEM-FORMAT-INDEX-001
title: File Formats
status: informative
version: '1.0'
language: en
domain: file-formats
kind: index
summary: A practical map of semantic source, component libraries, symbol assets, explicit layout, project locks,
  and style profiles.
authority:
- format-navigation
aliases:
- file formats
- AIXEM files
- extensions
agent:
  priority: normal
  estimated_tokens: 908
  intents:
  - inspect-artifact
  - create-schematic
  - create-symbol
depends_on: []
related:
- AIXEM-FORMAT-AIXEM-001
- AIXEM-FORMAT-AIXPROJ-001
navigation:
  group: file-formats
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# File Formats

A practical map of semantic source, component libraries, symbol assets, explicit layout, project locks, and style profiles.

> **Document ID:** `AIXEM-FORMAT-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

The format is interpreted together with its declared schema, feature set, and project lock.

The declared authority scopes are `format-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Each format has one authority role.
- References use stable IDs and locked digests.
- Schemas validate JSON formats.

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

- Preserve each format has one authority role as an explicit, reviewable part of the task.
- Preserve references use stable ids and locked digests as an explicit, reviewable part of the task.
- Preserve schemas validate json formats as an explicit, reviewable part of the task.
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

- [.aixem Semantic Source](aixem.md) — `AIXEM-FORMAT-AIXEM-001`
- [.aixproj.json Project Lock](aixproj.md) — `AIXEM-FORMAT-AIXPROJ-001`

## Hierarchical Versioned Forms

The 0.5.3 profile keeps `.aixem` at language version 1.0 with feature negotiation, adds `aixlayout/2` for interface presentation, and adds `aixproj/2` for multi-sheet composition. Existing v1 files remain valid.

## Complete Section Map

This list is the complete authored link surface for the `file-formats` navigation section. The navigation registry remains the machine-readable membership owner.

- [.aixem Semantic Source](aixem.md) — `AIXEM-FORMAT-AIXEM-001`
- [.aixlib.json Component Library](aixlib.md) — `AIXEM-FORMAT-AIXLIB-001`
- [.aixsym.json Symbol Asset](aixsym.md) — `AIXEM-FORMAT-AIXSYM-001`
- [.aixlayout.json Explicit Layout](aixlayout.md) — `AIXEM-FORMAT-AIXLAYOUT-001`
- [.aixproj.json Project Lock](aixproj.md) — `AIXEM-FORMAT-AIXPROJ-001`
- [Schematic Style Profile](style-profile.md) — `AIXEM-FORMAT-STYLE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
