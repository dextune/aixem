---
id: AIXEM-ARCH-ADR-0003
title: 'ADR-0003: Vendor-Neutral Engineering Surfaces'
status: normative
version: '1.0'
language: en
domain: architecture
kind: adr
summary: Records the decision to use conventional engineering inspection patterns with original AIXEM assets while separating
  the read-only Viewer, Review Workbench, and any future Editor.
authority:
- architecture-decision
aliases:
- vendor neutral UI ADR
- independent CAD UI
- ADR 0003
agent:
  priority: high
  estimated_tokens: 1003
  intents:
  - change-architecture
  - inspect-artifact
depends_on:
- AIXEM-SCHEM-VISUAL-001
related:
- AIXEM-SPEC-VISUAL-PROFILE-001
- AIXEM-SPEC-VIEWER-001
- AIXEM-SPEC-WORKBENCH-001
navigation:
  group: architecture
  order: 100
artifacts:
  owns: []
  consumes: []
requirements: []
---

# ADR-0003: Vendor-Neutral Engineering Surfaces

Records the decision to use conventional engineering inspection patterns with original AIXEM assets while separating the read-only Viewer, Review Workbench, and any future Editor.

> **Document ID:** `AIXEM-ARCH-ADR-0003`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The architecture separates authored authority, generated products, validation evidence, and static consumption surfaces.

The declared authority scopes are `architecture-decision`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Accepted decision.
- Functional regions are permitted.
- Vendor logos, icons, fonts, screenshots, libraries, and pixel-level replicas are excluded.
- AIXEM terminology and tokens remain original.

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
- Preserve functional regions are permitted as an explicit, reviewable part of the task.
- Preserve vendor logos, icons, fonts, screenshots, libraries, and pixel-level replicas are excluded as an explicit, reviewable part of the task.
- Preserve aixem terminology and tokens remain original as an explicit, reviewable part of the task.
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

- [Grid-First Visual Language](../../schematic/visual-language.md) — `AIXEM-SCHEM-VISUAL-001`
- [Schematic Presentation Profile 1](../../specifications/schematic/visual-profile.md) — `AIXEM-SPEC-VISUAL-PROFILE-001`


<a id="0-5-4-product-separation"></a>
## Product Separation

The accepted architecture distinguishes three product classes:

```text
Reference Viewer 1  = read-only design inspection
Review Workbench 1  = Viewer + diagnostics/provenance
Future Editor       = authoritative changes and write-back under a separate contract
```

The Viewer and Workbench may use conventional navigation, canvas, inspector, toolbar, and status arrangements, but they use original AIXEM code, icons, tokens, and terminology. They do not reproduce a vendor product pixel-for-pixel and do not expose unsupported editing controls.

- [Reference Viewer Contract 1](../../specifications/viewer/reference-viewer-contract.md) — `AIXEM-SPEC-VIEWER-001`
- [Review Workbench Contract 1](../../specifications/viewer/review-workbench-contract.md) — `AIXEM-SPEC-WORKBENCH-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
