---
id: AIXEM-AUTHORING-GUIDE-RENDER-REVIEW-001
title: Render and Review
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Guides read-only deterministic rendering and evidence-backed classification of source, symbol, layout, Viewer, and Workbench defects.
authority:
- authoring-guide-render-review
aliases:
- render review guide
- visual qa guide
- inspect schematic render
agent:
  priority: critical
  estimated_tokens: 1081
  intents:
  - render-review
  - author-component-circuit
depends_on:
- AIXEM-SPEC-RENDERER-001
- AIXEM-AGENT-VISUAL-QA-001
related:
- AIXEM-SPEC-VIEWER-001
- AIXEM-CONF-VALIDATION-001
navigation:
  group: authoring-guides
  order: 9
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/render-review.yaml
  - docs/_meta/generated/task-packets/render-review.json
requirements: []
---

# Render and Review

## 1. Task

Generate deterministic derived renderer and Viewer evidence, inspect it, classify every defect by owning authority, and repair only the authoritative source through the appropriate write route.

## 2. Use This Guide When / Do Not Use It When

Use it after source validation and after any source repair. Do not use it to hand-edit SVG, HTML, resolved scene, Viewer Model, render manifest, or validation output.

## 3. Primary Route ID

`render-review`

## 4. Authored Route and Generated Task Packet

- Authored route: `docs/_meta/routes/render-review.yaml`
- Generated task packet: `docs/_meta/generated/task-packets/render-review.json`

## 5. Required Inputs

Locked project inputs, active renderer/style profile, narrow validator results, previous evidence when comparing a repair, and the declared Viewer/Workbench profile.

## 6. Authority Allowed to Change

This route is read-only. A discovered defect is assigned to semantic, component-library, symbol, layout, project, renderer, Viewer, or Workbench authority and repaired through the owning task route.

## 7. Canonical Output Location

Use the declared generated render/evidence tree. Generated files are disposable derivatives and cannot be repaired directly.

## 8. Important Default Profile Values

`render PASS` means structural/binding/geometry/determinism success. It does not mean datasheet correctness, pinout review, semantic-ready part status, bounded compatibility PASS, circuit-intent approval, electrical safety, or simulation correctness.

## 9. Short Execution Sequence

1. Validate and lock all authoritative inputs.
2. Run the deterministic renderer to create resolved scene, SVG, Viewer Model, Viewer/Workbench files, manifest, and validation output.
3. Inspect machine-readable diagnostics before visual output.
4. Inspect resolved geometry and then the SVG/Viewer/Workbench presentation.
5. Classify each defect by the smallest owning authority.
6. Open the corresponding write route, repair the owner, and regenerate all derivatives.
7. Compare evidence and verify byte-identical output for equivalent locked inputs.
8. Record visual/browser review and unresolved limitations.

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Renderer Contract](../../specifications/renderer/renderer-contract.md) | `AIXEM-SPEC-RENDERER-001` | deterministic source-to-scene boundary | normative |
| [Reference Viewer Contract](../../specifications/viewer/reference-viewer-contract.md) | `AIXEM-SPEC-VIEWER-001` | Viewer authority boundary | normative |
| [Visual QA and Repair Loop](../../agent/visual-qa-loop.md) | `AIXEM-AGENT-VISUAL-QA-001` | defect classification and repair | informative |
| [Workbench Visual Profile](../../specifications/schematic/visual-profile.md) | `AIXEM-SPEC-VISUAL-PROFILE-001` | drawing vs application chrome | normative |
| [Conformance Validation](../../conformance/validation.md) | `AIXEM-CONF-VALIDATION-001` | evidence interpretation | conformance |

## 11. Validators and Tools

Use renderer-contract, deterministic digest, schema/binding, visual review, Reference Viewer browser, CSP/security, accessibility, and route-scope validators as applicable.

## 12. Completion Criteria

Renderer completes fail closed, resolved evidence is inspected, every defect has one owner, repairs occur only in authority, regenerated output is deterministic, and visual/browser review has no release-critical defect.

## 13. Stop / Fail-Closed Conditions

Stop on unresolved source or digest locks, unsupported required capability, renderer nondeterminism, unsafe external content, or a defect whose authority owner cannot be established.

## 14. Common Mistakes

Do not edit derivatives, infer semantic correctness from visual appearance, repair Viewer chrome by changing circuit geometry, or promote structural render success into part or circuit certification.

## 15. Evidence / Outputs

Retain resolved scene/project scene, SVG, Viewer Model, Viewer/Workbench files, render manifest, project validation, deterministic digest comparison, and visual/browser review record.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
