---
id: AIXEM-AGENT-VISUAL-QA-001
title: Visual QA and Repair Loop
status: normative
version: '1.0'
language: en
domain: agent
kind: guide
summary: Defines the render-inspect-classify-repair loop and defect-to-authority mapping for symbols and schematics.
authority:
- visual-qa-workflow
aliases:
- render review
- visual repair loop
- inspect schematic output
agent:
  priority: critical
  estimated_tokens: 1157
  intents:
  - render-review
  - create-symbol
  - create-schematic
depends_on:
- AIXEM-SPEC-RENDERER-001
- AIXEM-CONF-VALIDATION-001
related:
- AIXEM-AGENT-AUTHORING-001
- AIXEM-SYMBOL-DESIGN-RULES-001
navigation:
  group: agent
  order: 45
artifacts:
  owns:
  - docs/_meta/routes/render-review.yaml
  consumes:
  - examples/authoring/08-visual-repair/
requirements:
- id: AIXEM-REQ-AGENT-VISUAL-QA-0001
  title: Evidence-backed visual review
  level: MUST
  statement: Visual review MUST inspect validation evidence, resolved-scene data, and rendered output before a drawing task is declared complete.
  validator: agent.visual_qa
  verification_mode: automated
  test: tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_visual_repair_fixture
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-VISUAL-QA-0001.json
- id: AIXEM-REQ-AGENT-VISUAL-QA-0002
  title: Authority-local repair
  level: MUST
  statement: A detected drawing defect MUST be repaired in the authoritative source that owns the defective fact before derived artifacts are regenerated.
  validator: agent.visual_qa
  verification_mode: automated
  test: tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_visual_repair_fixture
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-VISUAL-QA-0002.json
---

# Visual QA and Repair Loop

Schema-valid data can still produce an unreadable or misleading drawing. Visual QA therefore combines machine-readable evidence with rendered inspection.

## Required Loop

```text
author source artifact
→ run schema and narrow lint
→ render
→ inspect project-validation.json
→ inspect resolved-scene.json
→ inspect SVG/workbench visually
→ classify defect by authority layer
→ repair authoritative source only
→ rerender and compare deterministic output
→ run final validation
```

<a id="AIXEM-REQ-AGENT-VISUAL-QA-0001"></a>

### AIXEM-REQ-AGENT-VISUAL-QA-0001 — Evidence-backed visual review

**MUST.** Visual review MUST inspect validation evidence, resolved-scene data, and rendered output before a drawing task is declared complete.

- Verification mode: `automated`
- Validator: `agent.visual_qa`
- Test reference: `tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_visual_repair_fixture`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-VISUAL-QA-0001.json`

## Inspection Order

1. Confirm `project-validation.json` reports valid schemas, digest locks, semantic closure, placement closure, route endpoint closure, grid validation, and no release-critical diagnostics.
2. Confirm `resolved-scene.json` contains expected component types, variants, resolved parameters, transformed semantic port coordinates, nets, paths, and junctions.
3. Inspect SVG/workbench for lead/port coincidence, field clearance, pin grouping, route readability, junction visibility, crossings, and label placement.
4. Compare output digests after a no-change rerender.

## Defect-to-Authority Matrix

| Symptom | Likely owner |
|---|---|
| Wire stops short of a visible pin lead | `.aixsym` lead or port geometry; possibly route endpoint transform |
| Correct wire shape belongs to wrong net | `.aixem` semantic membership |
| Text overlaps body | `.aixsym` field layout or design profile |
| Component is in the wrong location | `.aixlayout` placement |
| Crossing appears connected unexpectedly | semantic net membership and/or layout junction data |
| Color, stroke, or font is wrong | symbol fallback style or active style profile |
| Pin name or number is missing | symbol port metadata and visibility |
| Displayed value is wrong | `fieldMap`, semantic attributes, or placement `fields` precedence |
| Correct source renders inconsistently | renderer implementation/determinism contract |

<a id="AIXEM-REQ-AGENT-VISUAL-QA-0002"></a>

### AIXEM-REQ-AGENT-VISUAL-QA-0002 — Authority-local repair

**MUST.** A detected drawing defect MUST be repaired in the authoritative source that owns the defective fact before derived artifacts are regenerated.

- Verification mode: `automated`
- Validator: `agent.visual_qa`
- Test reference: `tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_visual_repair_fixture`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-VISUAL-QA-0002.json`

## Visual Repair Fixture

`examples/authoring/08-visual-repair/fixtures/broken-lead-port.aixsym.json` is intentionally schema-valid but has a lead endpoint that differs from port `1`. The repair changes only symbol geometry; it does not move the placement, reroute a net, or alter semantics. The corrected asset and repair evidence demonstrate the required discipline.

## Completion Record

A review record should name the source inputs, renderer/version, output digests, checks performed, defects found, authority classification, files repaired, and final status. Do not claim a visual pass from JSON Schema alone.
## Diagnostic-Bound Visual Repair

A visual finding must be converted to an owner before repair. Wrong connectivity routes to semantic authority; a lead/port or field/body defect routes to symbol authority; placement and local route defects route to layout authority; project membership routes to project authority; and a contradiction between valid resolved data and generated presentation is an implementation defect. Viewer and Workbench output remain read-only evidence.

The affected artifact and QID or JSON Pointer should be retained in the normalized diagnostic where available. The resulting change set must show that only the owning route changed authoritative files. A visually improved screenshot does not close the task unless structural validation, production render, Viewer Model validation, and deterministic run-record closure also pass.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
