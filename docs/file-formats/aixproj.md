---
id: AIXEM-FORMAT-AIXPROJ-001
title: .aixproj.json Project Lock
status: normative
version: '1.0'
language: en
domain: file-formats
kind: reference
summary: Documents the project manifest that binds all locked inputs, active profiles, render policy, provenance,
  and outputs.
authority:
- aixproj-format
aliases:
- .aixproj
- project lock JSON
- project manifest file
agent:
  priority: high
  estimated_tokens: 1004
  intents:
  - validate-project
  - publish-release
  - inspect-artifact
  - compose-project
depends_on:
- AIXEM-SPEC-PROJECT-LOCK-001
related:
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-CONCEPT-DETERMINISM-001
- AIXEM-SPEC-PROJECT-COMPOSITION-001
- AIXEM-CONCEPT-PROJECT-NET-001
navigation:
  group: file-formats
  order: 60
artifacts:
  owns:
  - '*.aixproj.json'
  consumes: []
requirements: []
---

# .aixproj.json Project Lock

Documents the project manifest that binds all locked inputs, active profiles, render policy, provenance, and outputs.

> **Document ID:** `AIXEM-FORMAT-AIXPROJ-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The format is interpreted together with its declared schema, feature set, and project lock.

The declared authority scopes are `aixproj-format`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- The manifest is the renderer entrypoint.
- Input digests prevent silent drift.
- Output roles make publication checks possible.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `*.aixproj.json`

## Operational Rules

- Preserve the manifest is the renderer entrypoint as an explicit, reviewable part of the task.
- Preserve input digests prevent silent drift as an explicit, reviewable part of the task.
- Preserve output roles make publication checks possible as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

## Canonical Library Path Guidance

New project-owned reusable component and symbol assets are stored below the project-local `library/electronics/...` or `library/architecture/...` tree and referenced with safe project-relative paths and digests. Existing safe legacy references remain compatible and repairable in place. Moving them is an explicit migration, not a side effect of validation or symbol repair.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Project Lock Contract 1](../specifications/project/project-lock-contract.md) — `AIXEM-SPEC-PROJECT-LOCK-001`
- [Deterministic Builds](../concepts/deterministic-builds.md) — `AIXEM-CONCEPT-DETERMINISM-001`

<a id="0-5-3-multi-sheet-form-aixproj-2"></a>
## Multi-Sheet Form (`aixproj/2`)

`aixproj/1` remains the immutable single-sheet lock. `aixproj/2` adds `sheets[]`, optional `parent`/`order`, and explicit `projectNets[]`. Each sheet references one independent source/layout pair, and every required digest is verified before composition.

```json
{
  "schema": "https://schemas.aixem.org/component-graphics/aixproj/2",
  "formatVersion": "2.0",
  "project": {
    "sheets": [{"id": "control", "title": "Control", "source": {}, "layout": {}}],
    "projectNets": [{"id": "vcc", "members": [{"sheet": "power", "port": "VOUT"}, {"sheet": "control", "port": "VCC"}]}]
  }
}
```

The complete contract is [Project Composition Contract 2](../specifications/project/project-composition-contract.md). Parent-child organization never implies electrical connectivity.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
