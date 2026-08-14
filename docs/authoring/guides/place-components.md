---
id: AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001
title: Agent Component Placement Strategy
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Defines an evidence-ranked deterministic Agent strategy for component placement that preserves existing valid authority and prioritizes semantic readability over compactness.
authority:
- authoring-guide-place-components
aliases:
- place components guide
- agent placement strategy
- schematic placement workflow
agent:
  priority: critical
  estimated_tokens: 1416
  intents:
  - create-schematic
  - author-component-circuit
depends_on:
- AIXEM-SCHEM-PLACEMENT-001
- AIXEM-SCHEM-GRID-001
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
related:
- AIXEM-CONCEPT-NET-001
- AIXEM-FORMAT-AIXLAYOUT-001
navigation:
  group: authoring-guides
  order: 4
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/create-schematic.yaml
  - docs/_meta/generated/task-packets/create-schematic.json
  - tools/placement_assist.py
requirements: []
---

# Agent Component Placement Strategy

## 1. Task

Transform already closed circuit semantics into readable deterministic component positions while preserving authority, grid legality, existing valid anchors, and routing feasibility.

## 2. Use This Guide When / Do Not Use It When

Use it after component identities and semantic nets are known and before route geometry is committed. Do not use placement to infer connectivity, active alternate functions, power domains, differential pairs, or component roles.

## 3. Primary Route ID

`create-schematic`

## 4. Authored Route and Generated Task Packet

- Authored route: `docs/_meta/routes/create-schematic.yaml`
- Generated task packet: `docs/_meta/generated/task-packets/create-schematic.json`

## 5. Required Inputs

Closed entities and net memberships, resolved bounds and endpoint maps, explicit user-fixed positions, active `G/P/M` style profile, existing valid placement for edits, and source-reviewed pin semantics where available.

## 6. Authority Allowed to Change

Only `.aixlayout.json` placement authority changes during placement. The strategy may rank geometry but cannot create or change semantic net membership, component endpoint identity, library semantics, or generated render evidence.

## 7. Canonical Output Location

Write placements only in the project-owned `.aixlayout.json`. The placement-assist tool is advisory and never writes authority.

## 8. Important Default Profile Values

Use `G=2.5 mm` for legal origins, `P=5 mm` for ordinary spacing rhythm, and `M=10 mm` for major alignment where practical. The bounded magnetic acquisition window is one `G` and considers at most base, X, Y, and XY candidates.

## 9. Short Execution Sequence

1. Close semantics and resolve bounds/endpoints before geometry.
2. For an existing drawing, freeze every unaffected valid placement by default.
3. Establish page flow and explicit boundaries; prefer left-to-right primary signal flow when applicable.
4. Form functional regions only from explicit net, component, property, pin-semantic, interface, or user evidence.
5. Place anchors in order: user-fixed items, interfaces/connectors, power boundaries, principal high-connectivity devices, explicit clocks/references, then repeated-stage primaries.
6. Orient principal devices so incoming/outgoing endpoint groups remain readable without violating symbol conventions.
7. Place support components only when their role is explicit; do not infer every capacitor as decoupling or every resistor as a pull-up.
8. Align semantic pin groups and orthogonal exits rather than blindly aligning body centers.
9. Reserve channels based on pin density, fanout, branches, pair preferences, and multi-pin edge congestion.
10. Review likely bends, crossings, escape congestion, blockage, detours, and junction density.
11. Refine locally in this order: collision, grid, whitespace, crossings, endpoint alignment, repeated rhythm, area.
12. Write the selected legal placements, then render and validate.

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Component Placement](../../schematic/placement.md) | `AIXEM-SCHEM-PLACEMENT-001` | canonical legality and composition rules | informative owner |
| [Grid and Snap System](../../schematic/grid-system.md) | `AIXEM-SCHEM-GRID-001` | active grid authority | informative owner |
| [Grid-First Visual Language](../../schematic/visual-language.md) | `AIXEM-SCHEM-VISUAL-001` | readable flow and whitespace | informative |
| [Pin Electrical Semantics Profile](../../specifications/components/pin-electrical-semantics-profile.md) | `AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001` | explicit placement evidence | normative |
| [Component Model](../../concepts/component-model.md) | `AIXEM-CONCEPT-COMPONENT-001` | reusable identity | informative |
| [Net Model](../../concepts/net-model.md) | `AIXEM-CONCEPT-NET-001` | explicit connectivity | informative |
| [`.aixlayout.json` Layout](../../file-formats/aixlayout.md) | `AIXEM-FORMAT-AIXLAYOUT-001` | placement authority | normative |

## 11. Validators and Tools

Use `tools/placement_assist.py suggest` for deterministic read-only candidates. Run placement closure, grid coherence, collision/field review, route-feasibility review, Change-Set scope, and deterministic render validation.

## 12. Completion Criteria

Every entity has one legal position; existing unaffected coordinates remain unchanged during a local edit; explicit regions and pin groups are readable; routes have usable channels; no semantic facts were inferred or changed; deterministic tie-breaking explains the selected coordinates.

## 13. Stop / Fail-Closed Conditions

Stop when semantics are incomplete, a desired relationship exists only in a name heuristic, every legal local candidate causes a hard collision, or a local request would require broad redraw. Report scope expansion rather than silently rearranging the sheet.

## 14. Common Mistakes

Do not optimize compactness first, move valid neighbors automatically, infer decoupling from capacitance alone, treat capability as active function, create pair semantics from `D+`/`D-` names alone, or use JSON/filesystem order as a tie-break.

## 15. Evidence / Outputs

Retain original and final coordinates, protected-anchor list, explicit evidence for functional groups/support relationships, placement-assist payloads, selected tie-break rationale, placement/grid validation, and before/after render review.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
