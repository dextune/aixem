---
id: AIXEM-EXAMPLE-HIERARCHY-001
title: 'Example: Hierarchical Reference Pattern'
status: informative
version: '1.0'
language: en
domain: examples
kind: example
summary: Shows how to partition power, sensing, control, and external I/O across sheets while retaining explicit semantic
  net continuity.
authority:
- example
aliases:
- hierarchical example
- multi sheet schematic
- sheet hierarchy
agent:
  priority: normal
  estimated_tokens: 911
  intents:
  - create-schematic
  - compose-project
depends_on:
- AIXEM-SCHEM-SHEET-001
related:
- AIXEM-CONCEPT-NET-001
- AIXEM-SCHEM-ANNOTATION-001
- AIXEM-CONF-HIERARCHICAL-PROJECT-001
- AIXEM-SPEC-VIEWER-001
navigation:
  group: examples
  order: 40
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Example: Hierarchical Reference Pattern

Shows how to partition power, sensing, control, and external I/O across sheets while retaining explicit semantic net continuity.

> **Document ID:** `AIXEM-EXAMPLE-HIERARCHY-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Examples demonstrate the normative model but do not supersede specifications.

The declared authority scopes are `example`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Example.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Define stable block and port IDs
2. Assign one functional purpose per sheet
3. Expose boundary nets through explicit ports
4. Keep power domains and resets visible
5. Resolve cross-sheet labels to semantic net IDs
6. Validate complete endpoint closure

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve example as an explicit, reviewable part of the task.
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

- [Sheet Organization](../schematic/sheet-organization.md) — `AIXEM-SCHEM-SHEET-001`
- [Net Model](../concepts/net-model.md) — `AIXEM-CONCEPT-NET-001`
- [Annotations and Fields](../schematic/annotations.md) — `AIXEM-SCHEM-ANNOTATION-001`

## Executable Reference Cases

This pattern is implemented and validated in the hierarchical corpus rather than remaining an illustrative hierarchy only.

- `validation/corpus/hierarchical-project-1/cases/H001-two-sheet-power-+-control` demonstrates two independent leaf circuits, semantic ports, explicit project nets, and all three views.
- `validation/corpus/hierarchical-project-1/cases/H005-three-level-sheet-hierarchy` demonstrates deterministic three-level organization.
- `validation/corpus/hierarchical-project-1/cases/H013-ten-sheet-scale-baseline` establishes the initial scale baseline.

The examples do not claim reusable module instancing or native vendor hierarchy interchange.


## Reference Viewer Inspection

Open the generated `viewer.html` for normal inspection. It provides qualified selection, search, layer visibility, and viewport controls without authoring affordances. Open `workbench.html` only when validation diagnostics and provenance are part of the review. The Viewer Model and both HTML outputs are derived and do not replace source, layout, project, SVG, or resolved-scene authority.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
