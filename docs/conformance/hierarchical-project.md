---
id: AIXEM-CONF-HIERARCHICAL-PROJECT-001
title: Hierarchical Project Conformance
status: normative
version: '1.0'
language: en
domain: conformance
kind: conformance
summary: Defines the executable H001-H015 and N001-N015 profile, deterministic render evidence, compatibility gates,
  and public claim boundary for AIXEM 0.5.3.
authority:
- hierarchical-conformance
- hierarchical-public-claims
aliases:
- hierarchical corpus
- multisheet conformance
- H001 H015
agent:
  priority: critical
  estimated_tokens: 1670
  intents:
  - validate-project
  - publish-release
  - compose-project
depends_on:
- AIXEM-SPEC-PROJECT-COMPOSITION-001
- AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001
related:
- AIXEM-CONF-RELEASE-001
- AIXEM-CONF-COMPAT-001
- AIXEM-CONF-REFERENCE-VIEWER-001
navigation:
  group: conformance
  order: 55
artifacts:
  owns:
  - validation/corpus/hierarchical-project-1/manifest.json
  - validation/corpus/hierarchical-project-1/results/validation-report.json
  - validation/corpus/hierarchical-project-1/results/determinism-report.json
  - validation/corpus/hierarchical-project-1/results/capability-matrix.json
  consumes: []
requirements:
- id: AIXEM-REQ-HIER-0011
  title: Independent leaf rendering
  level: MUST
  statement: Every valid aixproj/2 sheet MUST resolve and render through the production leaf pipeline as an independent
    SVG and resolved scene.
  validator: schematic.renderer_contract
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_multi_view_render_outputs_and_workbench_are_data_driven
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0011.json
- id: AIXEM-REQ-HIER-0012
  title: Three data-driven project views
  level: MUST
  statement: A conforming hierarchical render MUST provide Sheet, Overview, and Composite views using resolved project
    data and sheet-qualified identity.
  validator: schematic.workbench
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_multi_view_render_outputs_and_workbench_are_data_driven
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0012.json
- id: AIXEM-REQ-HIER-0013
  title: Hierarchical render determinism
  level: MUST
  statement: Three complete render runs from identical staged inputs MUST produce identical per-sheet, overview, composite,
    and resolved-project-scene digests.
  validator: schematic.deterministic
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_ten_sheet_project_and_three_run_determinism
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0013.json
- id: AIXEM-REQ-HIER-0014
  title: Legacy v1 preservation
  level: MUST
  statement: Valid aixproj/1 and aixlayout/1 projects MUST remain valid and preserve their production drawing and resolved-scene
    bytes.
  validator: schematic.renderer_contract
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_legacy_production_outputs_remain_byte_identical
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0014.json
- id: AIXEM-REQ-HIER-0015
  title: Three-pass hierarchical release gate
  level: MUST
  statement: Release evidence MUST record three completed verification passes covering semantic structure, rendering
    and agent usability, and regression and claim integrity.
  validator: docs.three_passes
  verification_mode: automated
  test: tests/docs/test_hierarchical_authoring_routes.py::HierarchicalAuthoringRouteTests.test_three_pass_release_evidence
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0015.json
---

# Hierarchical Project Conformance

AIXEM 0.5.3 hierarchical capability is releaseable only when executable evidence demonstrates the authority model, negative behavior, deterministic rendering, legacy preservation, and bounded public claim.

## Corpus Inventory

The canonical corpus is `validation/corpus/hierarchical-project-1`.

| Case | Purpose |
|---|---|
| H001 | base two-sheet interface and project-net closure |
| H002 | one component endpoint plus one semantic interface endpoint |
| H003 | three-sheet VCC/GND fanout |
| H004 | same-name local nets remain isolated |
| H005 | three-level hierarchy and traversal |
| H006 | local route closure to `@PORT` |
| H007 | deterministic overview |
| H008 | full composite workspace |
| H009 | unknown project interface fails closed |
| H010 | duplicate project-net ownership fails closed |
| H011 | complete digest lock |
| H012 | legacy v1 compatibility |
| H013 | ten-sheet scale baseline |
| H014 | crossing versus junction semantics |
| H015 | local/project equivalence collision rejection |

N001–N015 provide focused negative fixtures for parser, layout, project, hierarchy, and digest failures.

## Required Outputs

A valid v2 project render emits:

```text
sheets/<id>.svg
sheets/<id>.resolved-scene.json
interface-summaries/<id>.json
project-overview.svg
project-composite.svg
resolved-project-scene.json
viewer-model.json
viewer.html
workbench.html
render-manifest.json
```

The Reference Viewer hierarchy is generated from project records. It provides explicit Sheet, Overview, and Composite modes, sheet-scoped layer controls, qualified search, project-net selection, and interface inspection. The Review Workbench uses the same Viewer Core and adds diagnostics/provenance.

## Three-Pass Gate

### Pass 1 — Semantic and Structural Correctness

Verify v1 immutability, feature-gated interface grammar, local endpoint closure, layout presentation closure, hierarchy validity, project-net closure, name isolation, and expected negative diagnostics.

### Pass 2 — Rendering, Routing, Scale, and Agent Usability

Verify independent leaf rendering, interface attachment, orthogonal overview/composite routes, qualified identity, data-driven Workbench hierarchy, dedicated agent routes, and the H013 ten-sheet baseline.

### Pass 3 — Regression, Determinism, and Claim Integrity

Run the full repository suite, legacy symbol and Static 2D Block corpora, all hierarchical cases, three repeated complete renders, documentation/site generation, release manifest verification, and claim audit.

A release-critical correction restarts the affected pass from clean inputs.

## Public Claim Boundary

When all gates pass, the release may state:

> AIXEM supports deterministic composition of multiple digest-locked schematic source/layout pairs into an explicit hierarchical project, using semantic sheet interface ports and explicit project nets, with independent sheet rendering, project overview rendering, and composite project visualization.

The release must not claim full KiCad hierarchical compatibility, full OrCAD multi-page compatibility, or reusable hierarchical module instancing.

## Failure Classification

- H-F1: leaf semantic source;
- H-F2: leaf layout;
- H-F3: project composition;
- H-F4: project-net semantics;
- H-F5: project presentation/routing;
- H-F6: renderer defect;
- H-F7: proven architecture gap requiring a dedicated ADR.

## Evidence Files

- `results/validation-report.json` records all 30 expected outcomes;
- `results/determinism-report.json` records canonical repeat digests;
- `results/capability-matrix.json` maps claims to cases;
- `validation/evidence/pass-01`, `pass-02`, and `pass-03` retain release-cycle evidence.


## Normative Requirements

<a id="AIXEM-REQ-HIER-0011"></a>

### AIXEM-REQ-HIER-0011 — Independent leaf rendering

**MUST.** Every valid aixproj/2 sheet MUST resolve and render through the production leaf pipeline as an independent SVG and resolved scene.

- Verification mode: `automated`
- Validator: `schematic.renderer_contract`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_multi_view_render_outputs_and_workbench_are_data_driven`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0011.json`

<a id="AIXEM-REQ-HIER-0012"></a>

### AIXEM-REQ-HIER-0012 — Three data-driven project views

**MUST.** A conforming hierarchical render MUST provide Sheet, Overview, and Composite views using resolved project data and sheet-qualified identity.

- Verification mode: `automated`
- Validator: `schematic.workbench`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_multi_view_render_outputs_and_workbench_are_data_driven`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0012.json`

<a id="AIXEM-REQ-HIER-0013"></a>

### AIXEM-REQ-HIER-0013 — Hierarchical render determinism

**MUST.** Three complete render runs from identical staged inputs MUST produce identical per-sheet, overview, composite, and resolved-project-scene digests.

- Verification mode: `automated`
- Validator: `schematic.deterministic`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_ten_sheet_project_and_three_run_determinism`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0013.json`

<a id="AIXEM-REQ-HIER-0014"></a>

### AIXEM-REQ-HIER-0014 — Legacy v1 preservation

**MUST.** Valid aixproj/1 and aixlayout/1 projects MUST remain valid and preserve their production drawing and resolved-scene bytes.

- Verification mode: `automated`
- Validator: `schematic.renderer_contract`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_legacy_production_outputs_remain_byte_identical`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0014.json`

<a id="AIXEM-REQ-HIER-0015"></a>

### AIXEM-REQ-HIER-0015 — Three-pass hierarchical release gate

**MUST.** Release evidence MUST record three completed verification passes covering semantic structure, rendering and agent usability, and regression and claim integrity.

- Verification mode: `automated`
- Validator: `docs.three_passes`
- Test reference: `tests/docs/test_hierarchical_authoring_routes.py::HierarchicalAuthoringRouteTests.test_three_pass_release_evidence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0015.json`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
