---
id: AIXEM-AUTHORING-GUIDE-ROUTE-NETS-001
title: Route Nets
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Guides conversion of closed semantic nets into explicit orthogonal grid-aligned route geometry with unambiguous branches, junctions, and crossings.
authority:
- authoring-guide-route-nets
aliases:
- route nets guide
- connect wires guide
- orthogonal routing workflow
agent:
  priority: critical
  estimated_tokens: 1160
  intents:
  - route-nets
  - author-component-circuit
depends_on:
- AIXEM-CONCEPT-NET-001
- AIXEM-ROUTE-CONSTRAINT-001
- AIXEM-FORMAT-AIXLAYOUT-001
related:
- AIXEM-SCHEM-GRID-001
- AIXEM-ROUTE-CROSSING-001
navigation:
  group: authoring-guides
  order: 5
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/route-nets.yaml
  - docs/_meta/generated/task-packets/route-nets.json
requirements: []
---

# Route Nets

## 1. Task

Materialize existing semantic net membership as explicit orthogonal route paths in `.aixlayout.json` without changing connectivity.

## 2. Use This Guide When / Do Not Use It When

Use it only after semantic endpoint and placement closure. Return to [Create a Schematic](create-schematic.md) if a net or endpoint is missing, and to [Place Components](place-components.md) if legal routing channels do not exist. Do not use route geometry to invent a semantic connection.

## 3. Primary Route ID

`route-nets`

## 4. Authored Route and Generated Task Packet

- Authored route: `docs/_meta/routes/route-nets.yaml`
- Generated task packet: `docs/_meta/generated/task-packets/route-nets.json`

## 5. Required Inputs

Closed semantic nets, resolved component/sheet endpoints, grid-legal placements, symbol bounds/ports, active style profile, explicit pair or signal-class semantics where available, and route constraints.

## 6. Authority Allowed to Change

The route changes layout connection and path geometry plus necessary project digest locks. Semantic nets, component ports, symbols, and generated render evidence remain unchanged.

## 7. Canonical Output Location

Write connection records, paths, bends, labels, and explicit junctions only in the owning `.aixlayout.json`.

## 8. Important Default Profile Values

Free bends use `G=2.5 mm`; ordinary paths are orthogonal. Pair/signal-class metadata may rank equally legal geometry only when explicitly declared. It never creates connectivity or PCB-level electrical claims.

## 9. Short Execution Sequence

1. Confirm every connection names an existing semantic net and every intended endpoint resolves.
2. Select the straight, bent, multi-terminal, branch, or crossing recipe that matches topology.
3. Resolve electrical endpoints from the component-to-symbol mapping and placement transform.
4. Choose orthogonal `G`-aligned exits and preserve reserved channels.
5. Add explicit junction records for branch joins; preserve no-connect crossing semantics.
6. Avoid zero-length segments, illegal diagonal geometry, body/field obstacles, and ambiguous overlaps.
7. Use differential or signal-class semantics as conservative geometric preferences only.
8. Validate endpoint closure, grid alignment, orthogonality, branch/junction semantics, and deterministic render.

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Net Model](../../concepts/net-model.md) | `AIXEM-CONCEPT-NET-001` | semantic membership authority | informative |
| [Semantic Net Routing](../../routing/net-routing.md) | `AIXEM-ROUTE-NETS-001` | endpoint-to-path model | informative |
| [Routing Cookbook](../../routing/routing-cookbook.md) | `AIXEM-ROUTE-COOKBOOK-001` | topology recipes | informative |
| [Grid and Snap System](../../schematic/grid-system.md) | `AIXEM-SCHEM-GRID-001` | route grid | informative |
| [Route Constraints](../../routing/route-constraints.md) | `AIXEM-ROUTE-CONSTRAINT-001` | obstacles and clearances | informative |
| [Crossings and Junctions](../../routing/crossings-and-junctions.md) | `AIXEM-ROUTE-CROSSING-001` | explicit connectivity cues | informative |
| [`.aixlayout.json` Layout](../../file-formats/aixlayout.md) | `AIXEM-FORMAT-AIXLAYOUT-001` | route serialization | normative |

## 11. Validators and Tools

Run semantic route closure, orthogonality, free-bend grid, zero-length, junction, obstacle/clearance, Change-Set, and deterministic renderer validators from the route packet.

## 12. Completion Criteria

Every semantic endpoint is represented exactly as required, every free segment is orthogonal and legal, every branch join is explicit, crossings remain unambiguous, and rerendering locked sources is deterministic.

## 13. Stop / Fail-Closed Conditions

Stop when semantic closure is incomplete, an endpoint cannot resolve, available channels require an unapproved placement rewrite, pair semantics are only inferred from labels, or an ambiguous crossing cannot be represented explicitly.

## 14. Common Mistakes

Do not connect by visual proximity, turn wire crossings into implicit junctions, route from displayed text rather than stable endpoints, alter semantic nets to simplify geometry, or edit rendered SVG wires.

## 15. Evidence / Outputs

Retain updated `.aixlayout.json`, route-closure diagnostics, grid/orthogonality/junction results, scope-valid Change-Set, and deterministic routed render evidence.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
