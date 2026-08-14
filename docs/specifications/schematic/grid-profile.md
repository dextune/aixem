---
id: AIXEM-SPEC-GRID-PROFILE-001
title: Grid Schematic Profile 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: profile
summary: Binds the default grid, orthogonal routing, explicit junction, annotation, and workbench presentation requirements
  into a named application profile.
authority:
- schematic-profile
aliases:
- grid profile
- grid schematic profile
- schematic profile 1
agent:
  priority: critical
  estimated_tokens: 1389
  intents:
  - create-schematic
  - validate-project
depends_on:
- AIXEM-SCHEM-GRID-001
- AIXEM-ROUTE-ORTHO-001
- AIXEM-SCHEM-JUNCTION-001
related:
- AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001
- AIXEM-SPEC-VISUAL-PROFILE-001
- AIXEM-FORMAT-STYLE-001
navigation:
  group: specifications
  order: 50
artifacts:
  owns:
  - aixem.schematic.grid-light@1
  consumes: []
requirements:
- id: AIXEM-REQ-LAYOUT-0004
  title: Profile declaration
  level: MUST
  statement: A conforming project MUST declare the active schematic profile and required features.
  validator: schematic.project_schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0004.json
- id: AIXEM-REQ-LAYOUT-0005
  title: Grid profile enforcement
  level: MUST
  statement: A renderer claiming this profile MUST enforce its grid, routing, junction, and remote-asset policies.
  validator: schematic.profile_checks
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0005.json
- id: AIXEM-REQ-LAYOUT-0006
  title: Active grid coherence
  level: MUST
  statement: The serialized layout grid MUST agree with the active style-profile snap grid and the reference profile ratios MUST remain integral.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::SizingAndGridTests.test_g005_grid_profile_mismatch
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0006.json
- id: AIXEM-REQ-LAYOUT-0007
  title: Read-only deterministic placement assistance
  level: MUST
  statement: Placement assistance MUST produce deterministic legal suggestions without mutating authoritative schematic, layout, project, library, or symbol files.
  validator: schematic.placement_assist
  verification_mode: automated
  test: tests/schematic/test_placement_assist.py::PlacementAssistTests.test_cli_emits_read_only_payload
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0007.json
---

# Grid Schematic Profile 1

Binds the default grid, orthogonal routing, explicit junction, annotation, and workbench presentation requirements into a named application profile.

> **Document ID:** `AIXEM-SPEC-GRID-PROFILE-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `schematic-profile`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- The profile is a bundle of existing requirements.
- Projects may define other profiles but must declare them.
- Unsupported required profile features are rejected.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `aixem.schematic.grid-light@1`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-LAYOUT-0004"></a>

### AIXEM-REQ-LAYOUT-0004 — Profile declaration

**MUST.** A conforming project MUST declare the active schematic profile and required features.

- Verification mode: `automated`
- Validator: `schematic.project_schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0004.json`

<a id="AIXEM-REQ-LAYOUT-0005"></a>

### AIXEM-REQ-LAYOUT-0005 — Grid profile enforcement

**MUST.** A renderer claiming this profile MUST enforce its grid, routing, junction, and remote-asset policies.

- Verification mode: `automated`
- Validator: `schematic.profile_checks`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0005.json`

## Grid Authority and Placement Assistance

The active style profile owns schematic placement and routing snap authority:

```text
styleProfile.grid.snap       -> authoritative G
layout.coordinateSystem.grid -> serialized declaration that must agree with G
symbol coordinate grid       -> symbol-local authoring metadata only
```

For Grid Schematic Profile 1, `grid.minor` equals `grid.snap`, while `grid.major / grid.snap` and `symbol.pinPitch / grid.snap` are integral. A symbol-local grid cannot override schematic placement or route-bend legality.

<a id="AIXEM-REQ-LAYOUT-0006"></a>

### AIXEM-REQ-LAYOUT-0006 — Active grid coherence

**MUST.** The serialized layout grid MUST agree with the active style-profile snap grid and the reference profile ratios MUST remain integral.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::SizingAndGridTests.test_g005_grid_profile_mismatch`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0006.json`

A mismatch fails closed with `AIXEM-DIAG-LAYOUT-GRID-PROFILE-MISMATCH`.

<a id="AIXEM-REQ-LAYOUT-0007"></a>

### AIXEM-REQ-LAYOUT-0007 — Read-only deterministic placement assistance

**MUST.** Placement assistance MUST produce deterministic legal suggestions without mutating authoritative schematic, layout, project, library, or symbol files.

- Verification mode: `automated`
- Validator: `schematic.placement_assist`
- Test reference: `tests/schematic/test_placement_assist.py::PlacementAssistTests.test_cli_emits_read_only_payload`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0007.json`

The reference helper uses round-half-away-from-zero snapping, a one-`G` acquisition window, at most base/X/Y/XY candidates, stable ranking, and an explicit `mutated=false` result. An Agent must make and validate any authoritative `.aixlayout.json` edit separately.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Grid and Snap System](../../schematic/grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Orthogonal Routing](../../routing/orthogonal-routing.md) — `AIXEM-ROUTE-ORTHO-001`
- [Junctions and Connectivity Cues](../../schematic/junctions.md) — `AIXEM-SCHEM-JUNCTION-001`
- [Workbench Visual Profile 1](visual-profile.md) — `AIXEM-SPEC-VISUAL-PROFILE-001`
- [Schematic Style Profile](../../file-formats/style-profile.md) — `AIXEM-FORMAT-STYLE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
