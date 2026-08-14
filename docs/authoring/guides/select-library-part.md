---
id: AIXEM-AUTHORING-GUIDE-SELECT-LIBRARY-PART-001
title: Select a Library Part
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Guides semantic and provenance-based selection of an existing reusable component without relying on filename, symbol appearance, or a render-only claim.
authority:
- authoring-guide-select-library-part
aliases:
- select library part
- reuse component
- choose existing part
agent:
  priority: critical
  estimated_tokens: 1178
  intents:
  - create-schematic
  - author-component-circuit
depends_on:
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-CONCEPT-COMPONENT-001
related:
- AIXEM-FORMAT-AIXLIB-001
- AIXEM-SYMBOL-BINDING-001
navigation:
  group: authoring-guides
  order: 2
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/create-schematic.yaml
  - docs/_meta/generated/task-packets/create-schematic.json
requirements: []
---

# Select a Library Part

## 1. Task

Choose an existing component ID and presentation that satisfy the requested circuit role, endpoint contract, required properties, provenance status, and project lock requirements.

## 2. Use This Guide When / Do Not Use It When

Use it before placing an existing reusable part. Use [Create a Library Part](create-library-part.md) only when no suitable semantic component exists or the task explicitly owns a new reusable definition. Do not select by visual similarity alone.

## 3. Primary Route ID

`create-schematic`

## 4. Authored Route and Generated Task Packet

- Authored route: `docs/_meta/routes/create-schematic.yaml`
- Generated task packet: `docs/_meta/generated/task-packets/create-schematic.json`

## 5. Required Inputs

Requested functional role, required physical endpoints, required component properties, provenance expectation, active project library inventory, available presentations, and project digest state.

## 6. Authority Allowed to Change

Selection changes schematic entity references and, when required, project digest locks. It does not redefine the selected library component or symbol asset. Library repair is a separate `create-symbol` operation.

## 7. Canonical Output Location

The selected identity is recorded as the component/library reference in `.aixem`; locked library paths remain safe and project-relative in `.aixproj.json`. No new reusable file is created by normal selection.

## 8. Important Default Profile Values

Selection is semantic, not geometric. The reference `G/P/M = 2.5/5/10 mm` rhythm affects subsequent placement and rendering but does not determine component identity.

## 9. Short Execution Sequence

1. Convert the requested role into required endpoints, behavior types, semantic facets, and properties.
2. Search component IDs and metadata inside the authorized library set; use paths only as retrieval hints.
3. Prefer an exact datasheet-backed part when exact identity is requested. For generic intent, prefer a complete generic template.
4. Exclude placeholders from semantic-ready or production-ready claims.
5. Verify the complete terminal inventory, required properties, provenance status, and detailed pin semantics.
6. Verify that the selected presentation has a total endpoint map and suitable variant.
7. Lock or verify the library digest in the project manifest.
8. Create the schematic entity by component ID and retain the selection rationale in review evidence.

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Library Layout and Part Integrity Contract](../../specifications/components/library-layout-contract.md) | `AIXEM-SPEC-LIBRARY-LAYOUT-001` | provenance and semantic-ready meanings | normative |
| [Pin Electrical Semantics Profile](../../specifications/components/pin-electrical-semantics-profile.md) | `AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001` | endpoint behavior and function review | normative |
| [Component Model](../../concepts/component-model.md) | `AIXEM-CONCEPT-COMPONENT-001` | stable reusable identity | informative |
| [`.aixlib.json` Component Library](../../file-formats/aixlib.md) | `AIXEM-FORMAT-AIXLIB-001` | component and presentation fields | normative |
| [Component to Symbol Binding](../../symbols/component-symbol-binding.md) | `AIXEM-SYMBOL-BINDING-001` | endpoint-preserving presentation | informative |

## 11. Validators and Tools

Use the library schema, authoring-integrity validator, project digest-lock validator, component-type closure, and presentation-binding checks exposed by the route packet.

## 12. Completion Criteria

The selected component has the requested semantic role, complete endpoints and properties, an acceptable provenance status, a total presentation binding, and a project-locked library digest.

## 13. Stop / Fail-Closed Conditions

Stop when no candidate matches the requested terminal contract, the exact part is unsupported by source evidence, required properties are absent, the only candidate is a placeholder, or the project digest does not match the reviewed library.

## 14. Common Mistakes

Do not select by filename, symbol outline, displayed pin order, or render success. Do not silently substitute a generic template for an exact requested part or a placeholder for a reviewed component.

## 15. Evidence / Outputs

Retain selected component ID, library path and digest, presentation/variant choice, verified endpoint/property summary, provenance result, and any unresolved limitation.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
