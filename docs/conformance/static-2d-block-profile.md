---
id: AIXEM-CONF-B2D-001
title: Static 2D Block Compatibility Profile 1
status: normative
version: '1.0'
language: en
domain: conformance
kind: profile
summary: Defines a deliberately limited deterministic vector-block profile without native DWG or interactive Dynamic Block claims.
authority:
- static-2d-block-conformance
aliases:
- static 2d block profile
- static cad block
- b2d profile
agent:
  priority: high
  estimated_tokens: 720
  intents:
  - validate-symbol-expressiveness
  - publish-release
depends_on:
- AIXEM-CONF-SYMBOL-EXP-001
- AIXEM-SPEC-RENDERER-001
related:
- AIXEM-EXAMPLE-SYMBOL-CORPUS-001
- AIXEM-CONF-COMPAT-001
navigation:
  group: conformance
  order: 46
artifacts:
  owns:
  - validation/corpus/static-2d-block-1/
  - validation/reports/static-2d-block-0.5.2.json
  - validation/releases/0.5.2/static-2d-block.md
  consumes:
  - implementation/schematic/render_project.py
requirements: []
---

# Static 2D Block Compatibility Profile 1

> **Document ID:** `AIXEM-CONF-B2D-001`  
> **Status:** Normative  
> **Version:** 1.0

## Purpose

This profile states which non-interactive 2D CAD-style block characteristics AIXEM demonstrates through its current vector graphics model. It is separate from schematic-symbol semantics and is not a DWG profile.

## Included Capabilities

Subject to passing corpus evidence, B2D includes:

- line, polyline, polygon, rectangle, circle, ellipse, arc, and compound-path geometry;
- reusable definitions and `use` instances;
- supported deterministic placement transforms and mirroring;
- named styles, static text, and static dimensions;
- existing paint and digest-locked local-image behavior;
- declarative parameters, variants, and visibility states resolved before rendering.

## Required Corpus

The canonical fixture root is `validation/corpus/static-2d-block-1/`.

| ID | Case | Evidence target |
|---|---|---|
| B001 | Mechanical mounting plate | Rectangular, circular, arc, and hole geometry. |
| B002 | Repeated-hole panel | Definition reuse and repeated transforms. |
| B003 | Plan fixture | Mixed line and path geometry. |
| B004 | Annotation/title block | Structured lines and static text. |
| B005 | Dimensioned outline | Deterministic dimension geometry and readable labels. |
| B006 | Irregular mark | Compound path and static mark composition. |

Each case uses the same production-pipeline, determinism, approved-digest, and structured-review gates defined by `AIXEM-CONF-SYMBOL-EXP-001`.

## Explicit Exclusions

B2D excludes:

- Dynamic Block action graphs;
- interactive grips, stretch, move, flip, and lookup actions;
- general geometric or parametric constraints;
- associative dimension solving;
- native DWG object identity, layer tables, block tables, import, export, or round trip;
- 3D solids, surfaces, meshes, B-rep, BIM, or manufacturing semantics.

A declarative AIXEM variant is not an AutoCAD Dynamic Block action.

## Pass Rule

B2D passes only when `B001` through `B006` all pass automated assertions, repeat determinism, approved digest comparison, and structured visual review. A critical static-text, dimension, geometry, or false-connectivity defect fails the profile.

## Public Claim Boundary

Permitted claim:

> AIXEM demonstrates its Static 2D Block Profile 1 against six self-authored deterministic vector fixtures.

Prohibited claim:

> AIXEM is DWG compatible or implements AutoCAD Dynamic Blocks.

## Release Evidence

Evidence is published in:

- `validation/reports/static-2d-block-0.5.2.json`;
- `validation/releases/0.5.2/static-2d-block.md`;
- `validation/corpus/static-2d-block-1/results/`;
- `release/manifest.json`.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
