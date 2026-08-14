---
id: AIXEM-SCHEM-SHEET-001
title: Sheet Organization
status: informative
version: '1.0'
language: en
domain: schematic
kind: guide
summary: Organizes blocks, hierarchy, ports, title information, and cross-sheet references for scalable schematics.
authority:
- sheet-organization-guide
aliases:
- sheet organization
- schematic pages
- hierarchical schematic
agent:
  priority: normal
  estimated_tokens: 854
  intents:
  - create-schematic
  - compose-project
depends_on:
- AIXEM-SCHEM-PLACEMENT-001
related:
- AIXEM-EXAMPLE-HIERARCHY-001
- AIXEM-SCHEM-ANNOTATION-001
- AIXEM-SPEC-PROJECT-COMPOSITION-001
navigation:
  group: schematic
  order: 70
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Sheet Organization

Organizes blocks, hierarchy, ports, title information, and cross-sheet references for scalable schematics.

> **Document ID:** `AIXEM-SCHEM-SHEET-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

These rules prioritize a compact, grid-aligned engineering drawing that remains unambiguous when printed or viewed without color.

The declared authority scopes are `sheet-organization-guide`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Sheet organization guide.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Assign one purpose per sheet
2. Place inputs at the left and outputs at the right where practical
3. Keep power and clock boundaries explicit
4. Use stable hierarchical port names
5. Reserve a title and revision region

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve sheet organization guide as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- A sheet boundary is an organizational device. Net continuity across sheets remains explicit semantic data.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Component Placement](placement.md) — `AIXEM-SCHEM-PLACEMENT-001`
- [Example: Hierarchical Reference Pattern](../examples/hierarchical-reference.md) — `AIXEM-EXAMPLE-HIERARCHY-001`
- [Annotations and Fields](annotations.md) — `AIXEM-SCHEM-ANNOTATION-001`

## Executable 0.5.3 Hierarchy

The normative structural order is:

```text
Project
└── Sheet
    └── Layer
```

A sheet is an independent semantic/layout unit registered in `aixproj/2`. A layer is only a presentation subdivision inside one sheet and must never simulate a page. Optional parent relations organize real sheets and do not connect them electrically. Executable evidence is H001–H015 in `validation/corpus/hierarchical-project-1`.

Use [Project Composition Contract 2](../specifications/project/project-composition-contract.md) for project authority and [Hierarchical Sheet-Port Layout Contract 2](../specifications/layout/hierarchical-sheet-port-contract.md) for boundary presentation.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
