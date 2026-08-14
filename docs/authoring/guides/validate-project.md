---
id: AIXEM-AUTHORING-GUIDE-VALIDATE-PROJECT-001
title: Validate a Project
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Guides final closure of schema, lock, semantic, placement, routing, part provenance, pin semantics, bounded compatibility, intent, render, and evidence results.
authority:
- authoring-guide-validate-project
aliases:
- validate project guide
- project conformance guide
- close authoring evidence
agent:
  priority: critical
  estimated_tokens: 1364
  intents:
  - validate-project
  - author-component-circuit
depends_on:
- AIXEM-CONF-VALIDATION-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
related:
- AIXEM-CONF-TESTS-001
- AIXEM-SPEC-RELEASE-001
navigation:
  group: authoring-guides
  order: 10
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/validate-project.yaml
  - docs/_meta/generated/task-packets/validate-project.json
requirements: []
---

# Validate a Project

## 1. Task

Close all applicable source, binding, geometry, project-lock, provenance, pin-semantic, compatibility, circuit-intent, deterministic render, and evidence gates without collapsing distinct meanings into one PASS.

## 2. Use This Guide When / Do Not Use It When

Use it at each narrow repair boundary and for final project/release closure. Do not use a later-layer review result to bypass an earlier structural failure, or a render result to bypass semantic review.

## 3. Primary Route ID

`validate-project`

## 4. Authored Route and Generated Task Packet

- Authored route: `docs/_meta/routes/validate-project.yaml`
- Generated task packet: `docs/_meta/generated/task-packets/validate-project.json`

## 5. Required Inputs

Final authoritative sources, locked project manifest, component/source review records, intended circuit-use review records, route/review evidence, active profiles, and generated renderer/Viewer outputs.

## 6. Authority Allowed to Change

Validation is read-only. Failures reopen the smallest owning authoring route. Evidence records are derived and cannot redefine source authority.

## 7. Canonical Output Location

Machine-readable validation and release evidence belongs under declared `validation/evidence/...` paths. It references authoritative sources and digests but does not replace them.

## 8. Important Default Profile Values

Publish these separately where applicable:

```text
STRUCTURAL_PASS | STRUCTURAL_FAIL
PART_SEMANTIC_PASS | GENERIC_TEMPLATE_PASS | PLACEHOLDER | INCOMPLETE
PASS | WARN | ERROR | NOT_EVALUATED   (bounded compatibility)
CIRCUIT_INTENT_REVIEW_PASS | INCOMPLETE | NOT_REVIEWED
```

No compatibility result claims voltage, timing, simulation, safety, or production readiness.

## 9. Short Execution Sequence

1. Validate JSON schemas, safe paths, profile declarations, project references, and digests.
2. Validate component/library identity, total presentation binding, symbol design, semantic endpoints, placement closure, active-grid coherence, route closure, junctions, and deterministic serialization.
3. Validate component `partProvenance`, minimum semantic contract, semantic-clone protection, and placeholder truthfulness.
4. Validate Pin Electrical Semantics shape, consistency, differential closure, no-connect behavior, and source-review coverage.
5. Run the bounded compatibility precheck and retain uncertainty as `WARN` or `NOT_EVALUATED`.
6. Validate exact source/library/symbol-bound part review and, when claimed, circuit-intent review.
7. Render and inspect deterministic scene/SVG/Viewer evidence.
8. Run applicable focused and inherited regression suites, traceability, documentation relationship, and release-manifest checks.
9. Publish the separate result matrix and exact unresolved limitations.

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Conformance Validation](../../conformance/validation.md) | `AIXEM-CONF-VALIDATION-001` | ordered validation layers | conformance |
| [Conformance Tests](../../conformance/test-suite.md) | `AIXEM-CONF-TESTS-001` | executable inventory | conformance |
| [Library Layout and Part Integrity Contract](../../specifications/components/library-layout-contract.md) | `AIXEM-SPEC-LIBRARY-LAYOUT-001` | provenance, identity, claims | normative |
| [Pin Electrical Semantics Profile](../../specifications/components/pin-electrical-semantics-profile.md) | `AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001` | pin and compatibility validation | normative |
| [Renderer Contract](../../specifications/renderer/renderer-contract.md) | `AIXEM-SPEC-RENDERER-001` | deterministic output gate | normative |
| [Release Integrity](../../specifications/documentation/release-integrity.md) | `AIXEM-SPEC-RELEASE-001` | manifest and evidence closure | normative |

## 11. Validators and Tools

Use `tools/validate_authoring_integrity.py`, the focused schematic tests, project/schema/digest/binding/grid/route validators, renderer and Viewer suites, documentation compiler/audit, requirement traceability, and release verification/package tools.

## 12. Completion Criteria

All required lower layers pass; every warning/unevaluated outcome is explicit; source and intent evidence binds exact reviewed state; generated outputs are deterministic; documentation and traceability have no silent gap; release metadata and manifest match the verified tree.

## 13. Stop / Fail-Closed Conditions

Stop on a schema or lock failure, unresolved endpoint or placement, noncanonical new library path, unsupported concrete part, missing source-bound review, semantic clone, compatibility `ERROR`, renderer nondeterminism, documentation authority conflict, or stale release evidence.

## 14. Common Mistakes

Do not report one generic PASS, mark a placeholder semantic-ready, treat an input-only or tri-state topology as proven, reuse review evidence after source/digest change, or package a tree that changed after the final clean pass.

## 15. Evidence / Outputs

Retain focused and full regression reports, per-requirement records, pass-by-pass verification evidence, claim matrix, deterministic render/manifest digests, final validation report, release metadata, package verification, and SHA-256 checksum.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
