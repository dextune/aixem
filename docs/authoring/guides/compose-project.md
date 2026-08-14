---
id: AIXEM-AUTHORING-GUIDE-COMPOSE-PROJECT-001
title: Compose a Project
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Guides deterministic registration of independent sheets, explicit interface ports, hierarchy, project nets, and digest-locked project composition.
authority:
- authoring-guide-compose-project
aliases:
- compose project guide
- multi-sheet project guide
- connect sheets guide
agent:
  priority: critical
  estimated_tokens: 1062
  intents:
  - compose-project
depends_on:
- AIXEM-SPEC-PROJECT-COMPOSITION-001
- AIXEM-FORMAT-AIXPROJ-001
related:
- AIXEM-CONCEPT-PROJECT-NET-001
- AIXEM-CONF-HIERARCHICAL-PROJECT-001
navigation:
  group: authoring-guides
  order: 6
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/compose-project.yaml
  - docs/_meta/generated/task-packets/compose-project.json
requirements: []
---

# Compose a Project

## 1. Task

Register validated leaf sheets, define organizational hierarchy, connect explicit sheet interface ports through project nets, and lock every referenced source/library/layout by safe path and digest.

## 2. Use This Guide When / Do Not Use It When

Use it for multi-sheet composition. Use [Create a Schematic](create-schematic.md) to author leaf semantics and [Route Nets](route-nets.md) for local leaf routing. Do not infer project connectivity from names, page proximity, or generated Overview geometry.

## 3. Primary Route ID

`compose-project`

## 4. Authored Route and Generated Task Packet

- Authored route: `docs/_meta/routes/compose-project.yaml`
- Generated task packet: `docs/_meta/generated/task-packets/compose-project.json`

## 5. Required Inputs

Independently valid leaf projects/sheets, explicit semantic interface ports, desired hierarchy, project-net membership intent, safe project-relative source paths, and current digests.

## 6. Authority Allowed to Change

Project composition authority in `.aixproj.json` may change. Leaf semantic and layout sources remain owned by their respective tasks. Overview/Composite scenes and routes remain derived.

## 7. Canonical Output Location

Write the project manifest at the selected project root. References remain safe project-root-relative and cannot escape through `..`.

## 8. Important Default Profile Values

Project composition has no global placement solver. Leaf `G/P/M` geometry remains local authority; generated project scenes may display multiple sheets but do not become connectivity authority.

## 9. Short Execution Sequence

1. Validate every leaf independently and record source/layout/library digests.
2. Register deterministic sheet IDs and safe paths.
3. Declare hierarchy with no cycles and stable ordering.
4. Resolve every project-net member to an explicit qualified sheet interface port.
5. Reject duplicate membership and multiple project-net ownership.
6. Lock all relevant assets and regenerate the resolved project graph.
7. Validate composition, interface closure, digest locks, derived overview/composite generation, and deterministic output.

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Project Composition Contract](../../specifications/project/project-composition-contract.md) | `AIXEM-SPEC-PROJECT-COMPOSITION-001` | hierarchy and project-net authority | normative |
| [`.aixproj.json` Project Manifest](../../file-formats/aixproj.md) | `AIXEM-FORMAT-AIXPROJ-001` | serialization and locks | normative |
| [Project-Net Semantics](../../concepts/project-net-model.md) | `AIXEM-CONCEPT-PROJECT-NET-001` | qualified interface membership | informative |
| [Hierarchical Project Conformance](../../conformance/hierarchical-project.md) | `AIXEM-CONF-HIERARCHICAL-PROJECT-001` | positive and fail-closed corpus | conformance |

## 11. Validators and Tools

Run project schema, safe-path/digest lock, hierarchy acyclicity, interface resolution, duplicate-member, multiple-ownership, geometry-isolation, and deterministic project render validators.

## 12. Completion Criteria

Every leaf validates independently; hierarchy is acyclic and deterministic; every project-net member resolves exactly; no membership is duplicated or multiply owned; all locks match; derived outputs regenerate without becoming authority.

## 13. Stop / Fail-Closed Conditions

Stop on an unresolved sheet/interface, unsafe path, digest mismatch, cycle, duplicate member, ambiguous project-net ownership, or an attempt to use Overview geometry as semantic truth.

## 14. Common Mistakes

Do not connect similarly named ports automatically, reach upward from a nested self-contained project via path escape, duplicate local routing in project-net authority, or hand-edit derived project scenes.

## 15. Evidence / Outputs

Retain the locked project manifest, resolved semantic graph, per-sheet interface summaries, composition diagnostics, deterministic project scene/render evidence, and route-bounded Change-Set.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
