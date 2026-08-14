---
id: AIXEM-AUTHORING-GUIDE-MODIFY-SCHEMATIC-001
title: Modify an Existing Schematic
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Guides minimal-diff changes to an existing validated schematic while freezing unaffected semantic, placement, and routing authority.
authority:
- authoring-guide-modify-schematic
aliases:
- modify existing schematic
- minimal schematic edit
- local circuit repair
agent:
  priority: critical
  estimated_tokens: 1187
  intents:
  - create-schematic
  - route-nets
  - author-component-circuit
depends_on:
- AIXEM-CONCEPT-AUTHORITY-001
- AIXEM-SCHEM-PLACEMENT-001
related:
- AIXEM-AGENT-AUTHORING-001
- AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001
navigation:
  group: authoring-guides
  order: 7
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/create-schematic.yaml
  - docs/_meta/generated/task-packets/create-schematic.json
requirements: []
---

# Modify an Existing Schematic

## 1. Task

Apply the smallest requested semantic and geometric delta to an existing validated schematic while preserving every unaffected authoritative coordinate, route, identity, and digest relationship.

## 2. Use This Guide When / Do Not Use It When

Use it for adding or replacing a local part, changing one net, repairing one collision, or extending one functional region. Use the new-schematic guide when the page is intentionally being rebuilt. Do not silently convert a local request into global redraw.

## 3. Primary Route ID

`create-schematic` followed by `route-nets` only for the affected region.

## 4. Authored Route and Generated Task Packet

- Create-schematic route: `docs/_meta/routes/create-schematic.yaml`
- Create-schematic task packet: `docs/_meta/generated/task-packets/create-schematic.json`
- Route-nets route: `docs/_meta/routes/route-nets.yaml`

## 5. Required Inputs

Validated baseline sources and evidence, exact requested delta, active route scope, affected entity/net/placement map, and protected unaffected authority set.

## 6. Authority Allowed to Change

Only the smallest semantic, layout, project-lock, or library region justified by the request. Existing valid authority is evidence and remains frozen unless the task or a concrete hard defect requires movement.

## 7. Canonical Output Location

Modify the existing owning files at their declared safe paths. A legacy library asset may be repaired in place; moving it into the canonical library tree is a separate explicit migration.

## 8. Important Default Profile Values

All new or moved geometry remains legal under the active `G/P/M` profile. Unaffected coordinates and route points are byte-stable where serialization permits.

## 9. Short Execution Sequence

1. Snapshot and validate the baseline.
2. Translate the request into an exact semantic delta and identify the smallest affected authority graph.
3. Freeze unaffected component IDs, net memberships, coordinates, route geometry, and digest locks.
4. Update semantics first when connectivity or component identity changes.
5. Select/create any required library part through the corresponding guide.
6. Place only new or directly affected entities; preserve valid anchors.
7. Reroute only affected connections and shared branch segments.
8. Regenerate all derived outputs from authoritative sources.
9. Compare before/after authoritative digests and coordinates; investigate any unrelated change.
10. Run narrow validators, full affected-route validation, render review, and final project closure.

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Authority Model](../../concepts/authority-model.md) | `AIXEM-CONCEPT-AUTHORITY-001` | identify the smallest owner | informative |
| [Component Placement](../../schematic/placement.md) | `AIXEM-SCHEM-PLACEMENT-001` | preserve and locally refine layout | informative owner |
| [Authoring Orchestration](../../agent/authoring-orchestration.md) | `AIXEM-AGENT-AUTHORING-001` | route-bounded change loop | informative |
| [Place Components](place-components.md) | `AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001` | protected-anchor strategy | informative |
| [Route Nets](route-nets.md) | `AIXEM-AUTHORING-GUIDE-ROUTE-NETS-001` | affected-route repair | informative |

## 11. Validators and Tools

Use workspace snapshots and Change-Set evidence, semantic and placement closure, route closure, digest-lock validation, deterministic render, and an explicit before/after unaffected-authority comparison.

## 12. Completion Criteria

The requested delta is complete; unaffected authority is unchanged; new/moved geometry is legal; only affected routes changed; derived artifacts were regenerated; before/after evidence explains every changed authoritative file.

## 13. Stop / Fail-Closed Conditions

Stop and report scope expansion when the change requires broad component movement, shared-route reconstruction beyond the affected region, unresolved component migration, or a new global page strategy. Do not proceed as though it were still a local edit.

## 14. Common Mistakes

Do not normalize the entire file, reorder unrelated objects, re-place a valid page, reroute every net, migrate legacy paths opportunistically, or edit generated output to hide a source defect.

## 15. Evidence / Outputs

Retain baseline and final snapshots, changed-authority list, protected set, exact semantic/layout delta, route-scope results, before/after render comparison, and any reported scope expansion.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
