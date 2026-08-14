---
id: AIXEM-ARCH-ADR-0004
title: ADR 0004 — Symbol Style and Renderer Precedence
status: normative
version: '1.0'
language: en
domain: architecture
kind: adr
summary: Decides that symbol assets own geometry and fallback style while active profiles may override approved presentation roles without changing semantics.
authority:
- style-precedence-decision
aliases:
- adr 0004
- symbol style precedence
- renderer style authority
agent:
  priority: high
  estimated_tokens: 620
  intents:
  - create-symbol
  - change-architecture
  - render-review
depends_on:
- AIXEM-CONCEPT-AUTHORITY-001
- AIXEM-SPEC-RENDERER-001
related:
- AIXEM-SPEC-VISUAL-PROFILE-001
- AIXEM-FORMAT-STYLE-001
navigation:
  group: architecture
  order: 94
artifacts:
  owns: []
  consumes:
  - profiles/aixem-grid-schematic-style-1.aixstyle.json
requirements: []
---

# ADR 0004 — Symbol Style and Renderer Precedence

## Status

Accepted for AIXEM 0.5.1.

## Context

A symbol asset contains geometry and local named styles, while the schematic style profile defines project-wide visual tokens. Without a declared precedence, agents may encode project theme choices into every symbol or a renderer may override details that affect connectivity cues.

## Decision

```text
symbol asset
  owns intrinsic geometry, port coordinates, graphic roles/classes, text anchors,
  and a deterministic fallback style

active schematic style profile
  owns project-level palette, approved role-based stroke/font presentation,
  grid appearance, wire appearance, junction appearance, and workbench presentation

renderer
  resolves the two layers deterministically according to Renderer Contract 1
```

A profile may override approved visual properties such as color, stroke width, line cap/join, font family/size/weight, opacity, and visibility of non-semantic review overlays. It may not move a port, move a graphic node, change endpoint identity, change component identity, change semantic net membership, create a junction, or suppress a mapped semantic port.

## Intrinsic Geometry

Intrinsic geometry includes all numeric node coordinates, symbol bounds, insertion anchors, port coordinates/orientations, text anchor positions, parameterized dimension expressions, and variant graphics. These remain in `.aixsym.json`.

## Fallback Style

A symbol must render deterministically without a vendor-specific external theme. Its `styles` therefore provide local fallback values. Profiles should target semantic graphic roles/classes rather than depend on arbitrary node IDs.

## Compatibility

A 0.5.0 symbol that uses only existing fields continues to render under 0.5.1. The 0.5.1 renderer preserves symbol geometry and applies the existing grid-light profile's role-based presentation. No migration is required for ordinary assets.

## Consequences

- Authors can inspect geometry independently of theme.
- A project can apply a consistent visual language without rewriting symbols.
- Style changes remain incapable of changing circuit meaning.
- Renderer behavior is testable through deterministic golden output.
- Future style-profile evolution must retain the same semantic prohibition.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
