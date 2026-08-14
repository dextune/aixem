---
id: AIXEM-AUTHORING-GUIDE-CREATE-LIBRARY-PART-001
title: Create a Library Part
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Guides a fresh Agent from provenance classification and semantic component definition through grid-proportional symbol creation, binding, and separated review claims.
authority:
- authoring-guide-create-library-part
aliases:
- create library part
- new reusable component
- author component symbol
agent:
  priority: critical
  estimated_tokens: 1607
  intents:
  - create-symbol
  - author-component-circuit
  - validate-project
depends_on:
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-SYMBOL-DESIGN-001
related:
- AIXEM-FORMAT-AIXLIB-001
- AIXEM-FORMAT-AIXSYM-001
- AIXEM-SYMBOL-BINDING-001
navigation:
  group: authoring-guides
  order: 1
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/create-symbol.yaml
  - docs/_meta/generated/task-packets/create-symbol.json
requirements: []
---

# Create a Library Part

## 1. Task

Create or deliberately repair a reusable semantic component definition and its required graphic presentation asset. A normal new part produces at least one `.aixlib.json` component definition and one selected or newly authored `.aixsym.json` presentation.

## 2. Use This Guide When / Do Not Use It When

Use it for a new resistor class, sourced MCU, connector family, architectural symbol, or reusable component presentation. Use [Select a Library Part](select-library-part.md) when a suitable component already exists. Do not use this guide to edit generated SVG, Viewer, evidence, or corpus output directly.

## 3. Primary Route ID

`create-symbol`

## 4. Authored Route and Generated Task Packet

- Authored route: `docs/_meta/routes/create-symbol.yaml`
- Generated task packet: `docs/_meta/generated/task-packets/create-symbol.json`

## 5. Required Inputs

- active project or authoring root;
- requested functional identity and domain;
- source evidence for any concrete real part;
- complete physical terminal inventory and intended reusable properties;
- active symbol/style profile and existing asset inventory.

## 6. Authority Allowed to Change

The route may change component-library authority, symbol authority, and project digest locks within its declared Change-Set scope. Component semantics are authored before graphic presentation. Generated render and evidence artifacts remain read-only outputs.

## 7. Canonical Output Location

For a new reusable artifact:

```text
<project-root>/library/electronics/<semantic-namespace...>/<name>.aixlib.json
<project-root>/library/electronics/<semantic-namespace...>/<name>.aixsym.json
```

or the equivalent `library/architecture/...` tree. Use lower-kebab segments and semantically scoped filenames. Existing safe legacy assets may be repaired in place; moving them requires an explicit migration.

## 8. Important Default Profile Values

```text
G = 2.5 mm   body and port quantization
P = 5.0 mm   standard repeated pin pitch
M = 10 mm    major rhythm
L = 5.0 mm   standard visible lead
minimum repeated-group body span = (N - 1)P + 2G
```

Required content dimensions are rounded outward to `G`. Resolve collisions by enlarging at `G` increments, not by compressing `P` or the standard lead.

## 9. Short Execution Sequence

1. Resolve the project root and inspect the selected domain subtree for an existing accurate namespace.
2. Classify the component as `datasheet-backed`, `generic-template`, or `placeholder`.
3. For a concrete part, capture manufacturer, exact part number, and `sourceUri` before inventing terminals or geometry.
4. Author component ID, display name, kind, description, complete ports, minimum properties, and component-level provenance.
5. Author `port.type`; add Pin Electrical Semantics facets only when justified by source or explicit generic intent.
6. Reuse a locked symbol asset when it fits. Otherwise choose the nearest validated recipe, compute pin spans, reserve text channels, and quantize body dimensions outward to `G`.
7. Create a total component-port to symbol-port map, field map, variant selection, and digest-locked asset reference.
8. Run schema, path, provenance, pin-semantic, binding, symbol-design, render, and deterministic checks.
9. Record part semantic review separately from structural render. A placeholder remains non-semantic-ready.

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Library Layout and Part Integrity Contract](../../specifications/components/library-layout-contract.md) | `AIXEM-SPEC-LIBRARY-LAYOUT-001` | path, naming, provenance, identity, claims | normative |
| [Pin Electrical Semantics Profile](../../specifications/components/pin-electrical-semantics-profile.md) | `AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001` | electrical behavior and semantic facets | normative |
| [Symbol Design Profile](../../specifications/symbols/symbol-design-profile.md) | `AIXEM-SPEC-SYMBOL-DESIGN-001` | `G/P/M` dimensions and fields | normative |
| [`.aixlib.json` Component Library](../../file-formats/aixlib.md) | `AIXEM-FORMAT-AIXLIB-001` | semantic serialization | normative |
| [`.aixsym.json` Symbol Asset](../../file-formats/aixsym.md) | `AIXEM-FORMAT-AIXSYM-001` | graphic serialization | normative |
| [Component to Symbol Binding](../../symbols/component-symbol-binding.md) | `AIXEM-SYMBOL-BINDING-001` | total endpoint and field mapping | informative |
| [Symbol Authoring Cookbook](../../symbols/symbol-authoring-cookbook.md) | `AIXEM-SYMBOL-COOKBOOK-001` | closest validated construction recipe | informative |
| [Symbol Lint](../../symbols/symbol-lint.md) | `AIXEM-SYMBOL-LINT-001` | structural and render checks | informative |

## 11. Validators and Tools

- `python tools/validate_authoring_integrity.py <library-file> --artifact-path <project-relative-path> --operation added`
- `python -m unittest tests.schematic.test_authoring_integrity`
- existing symbol schema, binding, design-profile, and deterministic renderer validators from the route packet.

## 12. Completion Criteria

The new files are canonical and digest-locked; the component has a complete semantic contract; all required ports map to visible symbol endpoints; the symbol follows the active sizing rhythm; structural result and part semantic result are explicit; any placeholder remains `semanticReady=false`.

## 13. Stop / Fail-Closed Conditions

Stop rather than guess when a concrete part lacks a reliable source, terminal identity is uncertain, a required endpoint cannot be mapped, the requested namespace conflicts with established vocabulary, or review evidence does not bind the exact component/source/digest state.

## 14. Common Mistakes

Do not create reusable assets under `examples/`, use symbol appearance as component identity, mint IDs by copying geometry, turn a pin name into invented electrical truth, or describe `render PASS` as datasheet verification.

## 15. Evidence / Outputs

Retain authoritative library and symbol files, digest changes, validator outputs, deterministic render evidence, source-bound part review, placeholder state where applicable, and circuit-intent review only when the part is actually used in a schematic.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
