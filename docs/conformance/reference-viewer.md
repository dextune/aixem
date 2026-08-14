---
id: AIXEM-CONF-REFERENCE-VIEWER-001
title: Reference Viewer Conformance
status: normative
version: '1.0'
language: en
domain: conformance
kind: conformance
summary: Defines V001-V018 browser, security, accessibility, scale, separation, and three-run deterministic evidence
  for Reference Viewer Contract 1.
authority:
- reference-viewer-conformance
- viewer-public-claims
aliases:
- viewer corpus
- V001 V018
- browser conformance
agent:
  priority: critical
  estimated_tokens: 1112
  intents:
  - inspect-viewer
  - render-review
  - validate-project
  - publish-release
depends_on:
- AIXEM-SPEC-VIEWER-001
- AIXEM-SPEC-VIEWER-STATE-001
- AIXEM-SPEC-VIEWER-SECURITY-001
- AIXEM-SPEC-VIEWER-A11Y-001
related:
- AIXEM-CONF-HIERARCHICAL-PROJECT-001
- AIXEM-CONF-RELEASE-001
navigation:
  group: conformance
  order: 58
artifacts:
  owns:
  - validation/corpus/reference-viewer-1/manifest.json
  - validation/corpus/reference-viewer-1/results/validation-report.json
  - validation/corpus/reference-viewer-1/results/determinism-report.json
  - validation/corpus/reference-viewer-1/results/capability-matrix.json
  - validation/corpus/reference-viewer-1/results/performance-baseline.json
  consumes:
  - validation/corpus/hierarchical-project-1/
  - validation/corpus/symbol-expressiveness-1/
requirements: []
---

# Reference Viewer Conformance

Reference Viewer Contract 1 is releaseable only when executable browser evidence proves required behavior, security, accessibility, qualified identity, deterministic artifacts, and preservation of existing circuit rendering authority.

## Corpus Inventory

The canonical corpus is `validation/corpus/reference-viewer-1`.

| ID | Case | Required evidence |
|---|---|---|
| V001 | legacy single-sheet Viewer | Sheet-only capabilities and no authoring controls |
| V002 | three-mode hierarchical Viewer | Sheet, Overview, and Composite |
| V003 | data-driven hierarchy | active-sheet navigation |
| V004 | same-name local nets | qualified isolation |
| V005 | project-net selection | declared route/interface highlight closure |
| V006 | interface inspection | local/project relationship |
| V007 | sheet-scoped layers | no cross-sheet leakage |
| V008 | cross-view continuity | project-net selection survives Overview/Composite |
| V009 | component search | owning sheet opens |
| V010 | pan, zoom, fit | independent per-view transforms |
| V011 | keyboard-only workflow | required operations without pointer |
| V012 | narrow viewport | navigator and inspector remain reachable |
| V013 | offline/network denial | zero runtime requests and restrictive CSP |
| V014 | hostile authored text | inert display, no executable nodes |
| V015 | DOM/QID closure | unique IDs and all QIDs resolve |
| V016 | ten-sheet project | load, search, switching, and highlight baseline |
| V017 | profile separation | distinct Viewer and Workbench over shared core |
| V018 | three-run determinism | byte-identical model and HTML artifacts |

## Browser Gate

Controlled Chromium loads generated HTML with JavaScript enabled and networking blocked. Tests fail on console error, page error, external request, duplicate DOM ID, unresolved QID, incorrect mode/selection/layer transition, inaccessible required controls, or executable hostile text. Screenshots are evidence supplements, not behavioral substitutes.

## Required Evidence Products

```text
validation/corpus/reference-viewer-1/results/validation-report.json
validation/corpus/reference-viewer-1/results/determinism-report.json
validation/corpus/reference-viewer-1/results/capability-matrix.json
validation/corpus/reference-viewer-1/results/performance-baseline.json
validation/corpus/reference-viewer-1/results/browser-test.log
validation/corpus/reference-viewer-1/results/screenshot-evidence.json
```

The V016 baseline records Viewer Model bytes, Viewer/Workbench bytes, DOM and SVG counts, search index size, startup duration, mode-switch duration, search/highlight/fit duration where measured, and browser memory when available. Measurements establish a baseline; they do not justify unmeasured complexity.

## Three-Pass Release Gate

### Pass 1 — Contract, Authority, and Structure

Verify canonical documents, Viewer/Workbench/Editor terminology, non-authoritative state, Viewer Model schema closure, qualified identity, project-type capability mapping, removal of fake controls, and absence of normative ownership conflicts.

### Pass 2 — Browser Behavior, Security, and Operability

Run V001-V017 with networking blocked. Verify every required view and action, qualified search, selection closure, layer isolation, keyboard-only flow, narrow inspection, zero network requests, zero injection executions, and zero console errors.

### Pass 3 — Regression, Determinism, Documentation, and Claims

Run V001-V018 plus the full repository, hierarchical, symbol, Static 2D Block, and authoring corpora; compare protected renderer evidence; perform three complete Viewer renders; regenerate documentation/reference/site products; verify routes, traceability, manifest, package, and public claims.

## Public Claim Boundary

A passing release may claim a deterministic, self-contained, read-only HTML Reference Viewer for single-sheet and hierarchical multi-sheet projects with qualified semantic inspection, Sheet/Overview/Composite views, hierarchy navigation, project-net highlighting, sheet-scoped layers, offline operation, and browser-level conformance evidence.

It may not claim schematic editing, write-back, vendor UI compatibility, collaboration, PCB/Gerber viewing, or simulation viewing.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
