---
id: AIXEM-AUTHORING-GUIDE-AUTHOR-COMPONENT-CIRCUIT-001
title: Author a Component Circuit
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Provides the stable end-to-end chain from reusable component identity through semantic schematic, placement, routing, rendering, and separated validation claims.
authority:
- authoring-guide-author-component-circuit
aliases:
- author component circuit guide
- end-to-end circuit authoring
- new part and schematic
agent:
  priority: critical
  estimated_tokens: 1184
  intents:
  - author-component-circuit
depends_on:
- AIXEM-AUTHORING-GUIDES-INDEX-001
- AIXEM-AGENT-AUTHORING-001
related:
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-CONF-VALIDATION-001
navigation:
  group: authoring-guides
  order: 8
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/author-component-circuit.yaml
  - docs/_meta/generated/task-packets/author-component-circuit.json
requirements: []
---

# Author a Component Circuit

## 1. Task

Execute the complete bounded chain for creating or selecting a reusable component, using it in a semantic schematic, placing and routing it, reviewing deterministic output, and closing each validation claim separately.

## 2. Use This Guide When / Do Not Use It When

Use it when one request spans multiple authoring authorities. For a single operation, use the matching child guide. For local work on a validated circuit, begin with [Modify an Existing Schematic](modify-existing-schematic.md).

## 3. Primary Route ID

`author-component-circuit`

## 4. Authored Route and Generated Task Packet

- Composite authored route: `docs/_meta/routes/author-component-circuit.yaml`
- Composite generated task packet: `docs/_meta/generated/task-packets/author-component-circuit.json`

## 5. Required Inputs

Requested part/circuit intent, provenance expectations, selected project root, active profiles, existing library inventory, project boundaries, and completion/evidence requirements.

## 6. Authority Allowed to Change

Each child route changes only its declared authority. The composite route does not broaden child write scopes. Generated output remains derived and validation evidence does not become circuit authority.

## 7. Canonical Output Location

Reusable assets go under `library/<electronics|architecture>/...`; semantic and layout files remain project-owned; project composition remains in `.aixproj.json`; render and evidence remain generated under their declared output trees.

## 8. Important Default Profile Values

Use `G/P/M = 2.5/5/10 mm` for the reference profile. Treat source-or-placeholder provenance and structural/semantic/compatibility/intent claim separation as release gates.

## 9. Short Execution Sequence

```text
create-library-part or select-library-part
-> create-schematic
-> place-components
-> route-nets
-> render-review
-> validate-project
```

At every boundary, close the child route before opening the next. A new concrete part resolves provenance before pins/geometry. Semantic connectivity closes before placement. Placement closes before routing. Render review repairs the owning source, never the generated output. Final validation publishes separate claim results.

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Create a Library Part](create-library-part.md) | `AIXEM-AUTHORING-GUIDE-CREATE-LIBRARY-PART-001` | new reusable identity | informative |
| [Select a Library Part](select-library-part.md) | `AIXEM-AUTHORING-GUIDE-SELECT-LIBRARY-PART-001` | existing component reuse | informative |
| [Create a Schematic](create-schematic.md) | `AIXEM-AUTHORING-GUIDE-CREATE-SCHEMATIC-001` | semantic and placement sources | informative |
| [Place Components](place-components.md) | `AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001` | evidence-based layout | informative |
| [Route Nets](route-nets.md) | `AIXEM-AUTHORING-GUIDE-ROUTE-NETS-001` | explicit route geometry | informative |
| [Render and Review](render-review.md) | `AIXEM-AUTHORING-GUIDE-RENDER-REVIEW-001` | deterministic visual QA | informative |
| [Validate a Project](validate-project.md) | `AIXEM-AUTHORING-GUIDE-VALIDATE-PROJECT-001` | evidence closure | informative |

## 11. Validators and Tools

Run every validator named by the active child route, preserve Change-Set evidence at each write boundary, regenerate derived output, and finish with the full project and release-relevant regression gates.

## 12. Completion Criteria

Every child route exits successfully; no authority is written outside scope; reusable identity and provenance are truthful; semantics, placement, and routes close; render is deterministic; structural, part semantic, compatibility, placeholder, and circuit-intent results are explicit.

## 13. Stop / Fail-Closed Conditions

Stop when a child route cannot close, provenance is uncertain, semantic facts are being inferred from geometry, a local change expands globally, a required capability is outside AIXEM, or a higher-level claim lacks its own evidence.

## 14. Common Mistakes

Do not load every guide at once, bypass route order, let presentation redefine semantics, treat compatibility precheck as simulation, or report one generic PASS for all validation layers.

## 15. Evidence / Outputs

Retain final authoritative sources, all route Change-Sets, project locks, deterministic renderer/Viewer evidence, source-bound part review, bounded compatibility outcomes, circuit-intent review, and final validation summary.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
