---
id: AIXEM-SCHEM-PLACEMENT-001
title: Component Placement
status: normative
version: '1.0'
language: en
domain: schematic
kind: guide
summary: Defines grid-aligned placement, orientation, spacing, flow, grouping, and collision avoidance.
authority:
- component-placement
aliases:
- placement
- place components
- schematic layout
agent:
  priority: critical
  estimated_tokens: 1079
  intents:
  - create-schematic
  - place-component
depends_on:
- AIXEM-SCHEM-GRID-001
- AIXEM-CONCEPT-LAYOUT-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001
- AIXEM-SCHEM-VISUAL-001
- AIXEM-FORMAT-AIXLAYOUT-001
navigation:
  group: schematic
  order: 30
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SCHEM-0004
  title: Grid-aligned origins
  level: MUST
  statement: Every component placement origin MUST align to the active snap grid unless the profile declares a documented
    exception.
  validator: schematic.grid
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0004.json
- id: AIXEM-REQ-SCHEM-0005
  title: Placement closure
  level: MUST
  statement: The placement set MUST resolve every presented semantic entity exactly once.
  validator: schematic.placement_closure
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0005.json
---

# Component Placement

Defines grid-aligned placement, orientation, spacing, flow, grouping, and collision avoidance.

> **Document ID:** `AIXEM-SCHEM-PLACEMENT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

These rules prioritize a compact, grid-aligned engineering drawing that remains unambiguous when printed or viewed without color.

The declared authority scopes are `component-placement`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Component placement.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Establish page zones and signal flow
2. Place connectors and power boundaries
3. Place functional blocks
4. Align related pin rows
5. Reserve routing channels
6. Run collision and grid checks

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-SCHEM-0004"></a>

### AIXEM-REQ-SCHEM-0004 — Grid-aligned origins

**MUST.** Every component placement origin MUST align to the active snap grid unless the profile declares a documented exception.

- Verification mode: `automated`
- Validator: `schematic.grid`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0004.json`

<a id="AIXEM-REQ-SCHEM-0005"></a>

### AIXEM-REQ-SCHEM-0005 — Placement closure

**MUST.** The placement set MUST resolve every presented semantic entity exactly once.

- Verification mode: `automated`
- Validator: `schematic.placement_closure`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0005.json`

### Implementation notes

- Prefer additional whitespace over diagonal routes or compressed labels. Dense pages remain readable when alignment and channels are consistent.
- Treat component resize as an instance presentation transform, not as a new component or a semantic edit. Under the grid circuit-schematic renderer use the same finite positive value for `scaleX` and `scaleY`; use mirror flags for reflection.
- A resized component recomputes mapped semantic-port coordinates. Endpoint-bound route sides follow those ports, while explicit route vias stay authored and must be locally rerouted if grid or orthogonality validation no longer passes.

### Instance resize boundary

Resizing preserves the placement `entity`, component type, selected presentation, semantic ports, and net membership. It may change symbol footprint, field positions carried by the symbol, and transformed pin anchors. Scaling is therefore reviewed together with collision, whitespace, endpoint escape, and route feasibility rather than as a cosmetic-only edit.

## Agent Placement Strategy Boundary

The informative [Agent Component Placement Strategy](../authoring/guides/place-components.md) turns these requirements into a repeatable decision sequence: close semantics, preserve existing valid anchors, establish flow and boundaries, form evidence-backed functional regions, place anchors and principal devices, place explicitly related support parts, align pin groups, reserve routing channels, review route feasibility, refine locally on `G/P/M`, then render and validate.

Placement never invents connectivity. Explicit semantic nets, component/port identity, pin semantics, project interfaces, user constraints, and existing valid placement outrank names or visual heuristics. Semantic correctness, minimal movement, legality, readability, and route feasibility all outrank compactness.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Grid and Snap System](grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Explicit Layout Model](../concepts/layout-model.md) — `AIXEM-CONCEPT-LAYOUT-001`
- [Grid-First Visual Language](visual-language.md) — `AIXEM-SCHEM-VISUAL-001`
- [.aixlayout.json Explicit Layout](../file-formats/aixlayout.md) — `AIXEM-FORMAT-AIXLAYOUT-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
