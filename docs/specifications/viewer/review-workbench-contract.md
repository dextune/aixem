---
id: AIXEM-SPEC-WORKBENCH-001
title: Review Workbench Contract 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines the read-only engineering-review profile that extends Reference Viewer 1 with deterministic diagnostics,
  provenance, and evidence regions.
authority:
- review-workbench-contract
aliases:
- Review Workbench
- workbench.html
- engineering review surface
agent:
  priority: critical
  estimated_tokens: 563
  intents:
  - inspect-viewer
  - render-review
  - validate-project
depends_on:
- AIXEM-SPEC-VIEWER-001
related:
- AIXEM-SPEC-VIEWER-SECURITY-001
- AIXEM-CONF-REFERENCE-VIEWER-001
navigation:
  group: viewer
  order: 30
artifacts:
  owns:
  - implementation/schematic/viewer/review_workbench.py
  - implementation/schematic/viewer/templates/review-workbench.html.j2
  consumes:
  - viewer-model.json
  - viewer.html
  - project-validation.json
  - render-manifest.json
requirements: []
---

# Review Workbench Contract 1

The Review Workbench is a distinct product profile over the same Viewer Core used by the Reference Viewer. It inherits every read-only, identity, view, state, security, accessibility, and determinism requirement of Reference Viewer Contract 1.

## Product Role

`workbench.html` is an engineering-review surface, not an editor. It may add validation diagnostics, conformance status, renderer evidence, input/output digests, routing metrics, release information, and artifact provenance. It may not add authoring commands or write paths merely to resemble a CAD application.

The generated root declares `data-aixem-profile="review-workbench"`. The normal Viewer declares `reference-viewer`. These products may share templates, scripts, styles, and Viewer Model data, but their rendered regions and declared roles are distinguishable.

## Required Review Regions

When evidence is available, the Workbench presents:

- diagnostics with stable code, severity, status, and inert message text;
- provenance identifying the Viewer Model schema, viewer contract, release, project, model digest, and source/render digests;
- the same qualified navigator, search, layer, view, viewport, selection, and inspector behavior as the Reference Viewer.

Missing optional diagnostics do not permit fabricated results. A Workbench may state that a category is unavailable, but it must not imply that an unexecuted validator passed.

## Shared-Core Rule

Mode switching, active sheet, selection, search, layers, viewport transforms, keyboard commands, and inspector projection are implemented once in Viewer Core. The Workbench does not fork semantic viewing behavior. A defect common to both profiles is repaired in the shared owner.

## Prohibited Implications

The Workbench does not provide Place Wire, Place Symbol, Place Label, Place Junction, Place No-Connect, Rotate Selection, Save, Undo, Redo, or equivalent authoring affordances. A future Editor requires a separate architecture decision, command model, authority/write-back contract, and conformance family.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
