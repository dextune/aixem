---
id: AIXEM-SPEC-VIEWER-A11Y-001
title: Viewer Accessibility Profile 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines keyboard access, visible focus, semantic control state, non-color cues, qualified navigation, and
  narrow-viewport access for Viewer Contract 1.
authority:
- viewer-accessibility-profile
aliases:
- Viewer accessibility
- keyboard viewer
- narrow viewport
agent:
  priority: high
  estimated_tokens: 746
  intents:
  - inspect-viewer
  - render-review
  - validate-project
depends_on:
- AIXEM-SPEC-VIEWER-001
- AIXEM-SPEC-VIEWER-STATE-001
related:
- AIXEM-SPEC-VIEWER-SECURITY-001
- AIXEM-CONF-REFERENCE-VIEWER-001
navigation:
  group: viewer
  order: 60
artifacts:
  owns: []
  consumes:
  - implementation/schematic/viewer/templates/base.html.j2
  - implementation/schematic/viewer/core.py
requirements:
- id: AIXEM-REQ-VIEWER-0014
  title: Responsive inspection
  level: MUST
  statement: Required navigation and inspection capabilities MUST remain reachable in the declared narrow-viewport
    profile.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_viewer_accessibility.py::ViewerAccessibilityConformanceTests.test_v012_narrow_viewport_retains_navigation_and_inspection
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0014.json
---

# Viewer Accessibility Profile 1

Viewer Contract 1 provides an operable semantic path that does not depend on precise canvas pointing. The qualified navigator and search surface are the primary accessible alternative to thousands of SVG primitives.

## Keyboard and Focus

Every required command is reachable through normal focus traversal. Keyboard shortcuts supplement but do not replace focusable controls. Interactive controls display a focus-visible outline distinct from hover and selection. Focus order follows title bar, toolbar, navigator/search/layers, canvas, inspector, and review regions where present.

## Programmatic State

Mode buttons expose pressed state. Navigator category tabs expose selected state. Object rows expose selected state. Responsive panel buttons expose expanded state and identify their controlled panel. Hierarchy and inspector labels remain associated with their content. Status updates use a non-disruptive live region.

## Semantic Alternative to Canvas Hit Targets

SVG objects may remain outside the page tab sequence. Every inspectable sheet, entity, local net, interface, and project net is reachable through the qualified navigator or search, and those paths resolve to the same inspector identity as pointer selection.

## Non-Color Meaning

Selection uses outlines, halos, weight, and inspector/state text in addition to color. Junctions, crossings, errors, direction, and connectivity retain shape, label, or structural cues. Color is not the sole carrier of semantic meaning.

## Narrow Viewport

At widths below the desktop three-column layout, navigator and inspector become explicit keyboard-operable drawers. Required controls and data are not simply removed. Diagnostics may reflow or collapse by section, but the core navigator, canvas, and inspector remain reachable.

<a id="AIXEM-REQ-VIEWER-0014"></a>

### AIXEM-REQ-VIEWER-0014 — Responsive inspection

**MUST.** Required navigation and inspection capabilities MUST remain reachable in the declared narrow-viewport profile.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_viewer_accessibility.py::ViewerAccessibilityConformanceTests.test_v012_narrow_viewport_retains_navigation_and_inspection`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0014.json`

## Conformance Viewports

The browser corpus exercises desktop and narrow widths. Narrow conformance verifies access to the navigator, search, view controls, canvas, inspector, and close/toggle controls with visible focus. A visually compact layout that makes semantic inspection impossible is non-conforming.

This profile is a reference-platform contract and evidence baseline; it is not a claim of certification against an external accessibility standard.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
