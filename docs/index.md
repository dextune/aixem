---
id: AIXEM-DOCS-HOME-001
title: AIXEM Documentation
status: informative
version: '1.0'
language: en
domain: documentation
kind: index
summary: The canonical entrypoint for the AIXEM schematic platform, its specifications, workflows, agent routes, and conformance evidence.
authority:
- documentation-navigation
aliases:
- documentation home
- AIXEM docs
- documentation index
agent:
  priority: normal
  estimated_tokens: 1213
  intents:
  - discover-documentation
  - create-schematic
  - create-symbol
  - route-nets
  - validate-project
  - compose-project
  - route-project-nets
depends_on: []
related:
- AIXEM-START-INTRO-001
- AIXEM-ARCH-SYSTEM-001
- AIXEM-CONF-REQUIREMENTS-001
- AIXEM-SPEC-PROJECT-COMPOSITION-001
- AIXEM-RELEASE-0581-001
navigation:
  group: home
  order: 10
artifacts:
  owns:
  - docs/index.md
  consumes: []
requirements: []
---
# AIXEM Documentation

AIXEM is a vendor-neutral, machine-authorable schematic platform built around explicit circuit semantics, grid-aligned graphics, orthogonal routing, deterministic rendering, and bounded AI-agent retrieval.

> **Document ID:** `AIXEM-DOCS-HOME-001`  
> **Status:** Informative  
> **Version:** 1.0

## Choose an entrypoint

<div class="home-grid">
<a class="home-card" href="getting-started/index.html"><b>Get started</b><span>Install the toolchain, render the bundled project, and verify the release.</span></a>
<a class="home-card" href="concepts/index.html"><b>Understand the model</b><span>Learn the authority layers for semantics, symbols, layout, routing, and presentation.</span></a>
<a class="home-card" href="schematic/index.html"><b>Author schematics</b><span>Apply the grid, placement, annotation, junction, and visual-language rules.</span></a>
<a class="home-card" href="symbols/index.html"><b>Build symbols</b><span>Create deterministic symbol geometry, pins, fields, variants, and lintable assets.</span></a>
<a class="home-card" href="routing/index.html"><b>Route nets</b><span>Use orthogonal route geometry without confusing visual crossings with connectivity.</span></a>
<a class="home-card" href="agent/index.html"><b>Operate AI agents</b><span>Resolve a bounded task route before using full-text or repository-wide search.</span></a>
<a class="home-card" href="specifications/index.html"><b>Read specifications</b><span>Open the normative contracts, requirement anchors, and machine-readable schemas.</span></a>
<a class="home-card" href="conformance/index.html"><b>Verify conformance</b><span>Trace requirements to validators, tests, release evidence, manifests, and gates.</span></a>
</div>

## Documentation architecture

`docs/` is the only canonical documentation root. The compiler derives every machine-facing and publication-facing product from canonical Markdown and authored metadata.

```text
Canonical Markdown + authored metadata
        |
        +-- static official documentation site
        +-- document, route, alias, and search indexes
        +-- dependency and artifact ownership graphs
        +-- requirement traceability and evidence paths
        +-- generated 0.4 compatibility reference
        +-- deterministic release manifest
```

Generated products are disposable. A rule must be changed in the canonical source that owns its authority scope and then regenerated.

## Core invariants

- The baseline schematic snap grid is **2.5 mm** with a **10 mm** major grid.
- Routes are orthogonal and use only horizontal or vertical segments.
- A visual crossing is not a semantic junction.
- No-connect intent exists in source semantics rather than only in presentation.
- Semantic connectivity, symbol graphics, placement/routing, and visual style remain separate authority layers.
- Required remote documentation and rendering assets are denied by default.
- Known AI-agent tasks resolve through authored routes before broad search.
- Project composition is explicit: Project -> Sheet -> Layer, with cross-sheet connectivity declared only by project nets.

## Fast evaluation

1. Follow the [Quick Start](getting-started/quick-start.md).
2. Open the [grid-controller example](examples/grid-controller.md) and its generated workbench.
3. Review the [task-routing model](agent/task-routing.md) and generated route index.
4. Review the [requirement catalog](conformance/requirements.md).
5. Read the [current 0.5.8.1 release record](releases/0.5.8.1.md), [Release Gates](conformance/release-gates.md), and release-scoped validation report.

## Authority and status

A page marked **Normative** contains binding requirements. Informative pages explain workflows or examples and cannot override a normative contract. Stable document IDs survive path and title changes; published requirement IDs are immutable.

## Related documents

- [Introduction to AIXEM](getting-started/introduction.md) — `AIXEM-START-INTRO-001`
- [System Overview](architecture/system-overview.md) — `AIXEM-ARCH-SYSTEM-001`
- [Requirement Model](conformance/requirements.md) — `AIXEM-CONF-REQUIREMENTS-001`
- [Project Composition Contract 2](specifications/project/project-composition-contract.md) — `AIXEM-SPEC-PROJECT-COMPOSITION-001`
- [AIXEM 0.5.8.1](releases/0.5.8.1.md) — `AIXEM-RELEASE-0581-001`
- [Release Gates](conformance/release-gates.md) — `AIXEM-CONF-RELEASE-001`

## Complete Section Map

This list is the complete authored link surface for the `home` navigation section. The navigation registry remains the machine-readable membership owner.

_This section has no child documents; this page is the canonical entrypoint._

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
