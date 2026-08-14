---
id: AIXEM-FORMAT-STYLE-001
title: Schematic Style Profile
status: normative
version: '1.0'
language: en
domain: file-formats
kind: reference
summary: Documents the style profile for grid spacing, strokes, colors, fonts, markers, selection states, and workbench
  presentation.
authority:
- style-profile-format
aliases:
- style profile
- aixstyle
- schematic theme
agent:
  priority: critical
  estimated_tokens: 855
  intents:
  - create-schematic
  - inspect-artifact
  - change-architecture
depends_on:
- AIXEM-SPEC-GRID-PROFILE-001
- AIXEM-SPEC-VISUAL-PROFILE-001
related:
- AIXEM-SCHEM-VISUAL-001
navigation:
  group: file-formats
  order: 70
artifacts:
  owns:
  - profiles/aixem-grid-schematic-style-1.aixstyle.json
  consumes: []
requirements:
- id: AIXEM-REQ-FORMAT-0020
  title: Profile identity
  level: MUST
  statement: A style profile MUST declare a stable ID, version, unit, grid policy, and visual token groups.
  validator: schematic.style_profile
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-FORMAT-0020.json
- id: AIXEM-REQ-FORMAT-0021
  title: Presentation non-authority
  level: MUST
  statement: A style profile MUST NOT alter semantic endpoint identity or net membership.
  validator: schematic.geometry_isolation
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-FORMAT-0021.json
---

# Schematic Style Profile

Documents the style profile for grid spacing, strokes, colors, fonts, markers, selection states, and workbench presentation.

> **Document ID:** `AIXEM-FORMAT-STYLE-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The format is interpreted together with its declared schema, feature set, and project lock.

The declared authority scopes are `style-profile-format`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Presentation tokens are replaceable.
- Grid tokens are profile constraints.
- System fallback fonts keep the reference build self-contained.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `profiles/aixem-grid-schematic-style-1.aixstyle.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-FORMAT-0020"></a>

### AIXEM-REQ-FORMAT-0020 — Profile identity

**MUST.** A style profile MUST declare a stable ID, version, unit, grid policy, and visual token groups.

- Verification mode: `automated`
- Validator: `schematic.style_profile`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-FORMAT-0020.json`

<a id="AIXEM-REQ-FORMAT-0021"></a>

### AIXEM-REQ-FORMAT-0021 — Presentation non-authority

**MUST.** A style profile MUST NOT alter semantic endpoint identity or net membership.

- Verification mode: `automated`
- Validator: `schematic.geometry_isolation`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-FORMAT-0021.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Grid Schematic Profile 1](../specifications/schematic/grid-profile.md) — `AIXEM-SPEC-GRID-PROFILE-001`
- [Workbench Visual Profile 1](../specifications/schematic/visual-profile.md) — `AIXEM-SPEC-VISUAL-PROFILE-001`
- [Grid-First Visual Language](../schematic/visual-language.md) — `AIXEM-SCHEM-VISUAL-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
