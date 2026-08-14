---
id: AIXEM-EXAMPLE-SYMBOL-CORPUS-001
title: Symbol Expressiveness Corpus Construction Index
status: informative
version: '1.0'
language: en
domain: examples
kind: index
summary: Maps common symbol classes to the nearest validated corpus construction pattern and its primary authoring risks.
authority:
- symbol-corpus-example-navigation
aliases:
- symbol corpus examples
- nearest symbol pattern
- conformance symbol recipes
agent:
  priority: high
  estimated_tokens: 1029
  intents:
  - validate-symbol-expressiveness
  - create-symbol
depends_on:
- AIXEM-CONF-SYMBOL-EXP-001
- AIXEM-SYMBOL-COOKBOOK-001
related:
- AIXEM-SYMBOL-AIXSYM-REF-001
- AIXEM-SYMBOL-LINT-001
- AIXEM-CONF-B2D-001
navigation:
  group: examples
  order: 45
artifacts:
  owns: []
  consumes:
  - validation/corpus/symbol-expressiveness-1/
  - validation/corpus/static-2d-block-1/
requirements: []
---

# Symbol Expressiveness Corpus Construction Index

> **Document ID:** `AIXEM-EXAMPLE-SYMBOL-CORPUS-001`  
> **Status:** Informative  
> **Version:** 1.0

## Nearest-Proven-Pattern Rule

Before inventing a non-trivial graphics structure, select the nearest validated corpus case and inspect only that case's `case.json` and `symbol.aixsym.json`. Preserve the target component's actual endpoint semantics; a visual resemblance does not authorize copying another case's port inventory.

The fixtures demonstrate construction patterns but do not supersede the normative symbol schema, design profile, renderer contract, or component semantics.

## Core Pattern Index

| Symbol class | Nearest cases | Preferred construction | Frequent failure |
|---|---|---|---|
| IEC/ANSI passive | S001-S005 | Straight primitives first; `use` or compact path for repeated coils/zig-zags. | Decorative endpoint differs from electrical port. |
| Diode family | S006-S008 | Shared body composition; variants only when endpoint identity is invariant. | Arrow or terminal mark implies false connectivity. |
| Transistor family | S009, S010, S025 | Group internal geometry; keep gate/base separation explicit. | Arrow orientation or lead attachment is ambiguous. |
| Op-amp/comparator | S011, S012 | Polygonal body with grouped inputs, output, and supply ports. | Field and pin labels collide at the apex. |
| Transformer | S013 | Reused winding geometry plus independent ports. | Core lines or curves appear electrically connected. |
| Relay/switch/rotary | S014-S016 | Separate conductive leads from mechanical association marks. | Mechanical line is mistaken for a net. |
| Logic gate | S017, S018 | Path body plus explicit bubble and internal marks. | Bubble moves the electrical attachment point incorrectly. |
| Connector | S019-S021 | Parameterized/repeated leads, deterministic numbering, fixed pitch. | Off-grid pins or unreadable 100-pin labels. |
| MCU/high-pin IC | S022-S024 | Functional side grouping, scalable body, stable field zones. | Labels become denser than the declared pitch supports. |
| Timing/opto/tube/custom | S026-S029 | Compose first; use compound path only for genuinely irregular contours. | Path self-intersection or undocumented renderer behavior. |
| FPGA multi-unit | S030 | Treat as a semantic probe, not a variant recipe. | Duplicated entities falsely simulate shared identity. |

## Static Block Pattern Index

| Static block class | Nearest cases | Preferred construction |
|---|---|---|
| Mechanical outline | B001 | Rect/circle/arc composition. |
| Repeated panel | B002 | Definitions and `use` transforms. |
| Plan fixture | B003 | Lines plus bounded path details. |
| Title or annotation block | B004 | Static text with explicit anchors and line hierarchy. |
| Dimensioned outline | B005 | Existing `dimension` primitive with deterministic label styling. |
| Irregular mark | B006 | Compound path with explicit fill/stroke intent. |

## Focused Validation

Run one case while authoring:

```bash
python tools/validate_symbol_corpus.py --case S014
```

Run a tier:

```bash
python tools/validate_symbol_corpus.py --tier core --repeat 3
```

Run all released profiles and emit evidence:

```bash
python tools/validate_symbol_corpus.py --all --repeat 3 --emit-report
```

Approved digests are updated only by an explicit reviewed operation:

```bash
python tools/validate_symbol_corpus.py --all --repeat 3 --update-approved-digests
```

Never update approved digests merely to make a changed render pass.

## Evidence Interpretation

A case result separates:

- source/schema and binding assertions;
- geometry signature;
- production-render output;
- repeat determinism;
- approved digest status;
- digest-bound structured visual review.

S030 may draw successfully while MU remains `NOT_SUPPORTED`. That is an intentional distinction between graphics expressiveness and independently placeable shared-identity device semantics.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
