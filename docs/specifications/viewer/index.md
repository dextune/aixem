---
id: AIXEM-SPEC-VIEWER-INDEX-001
title: Viewer Specifications
status: informative
version: '1.0'
language: en
domain: specifications
kind: index
summary: Routes implementers and reviewers to the canonical AIXEM Reference Viewer, Workbench, state, security,
  accessibility, and model contracts.
authority:
- viewer-specification-index
aliases:
- viewer specifications
- Reference Viewer index
agent:
  priority: high
  estimated_tokens: 643
  intents:
  - inspect-viewer
  - render-review
  - validate-project
depends_on: []
related:
- AIXEM-SPEC-VIEWER-001
- AIXEM-SPEC-WORKBENCH-001
- AIXEM-SPEC-VIEWER-STATE-001
- AIXEM-SPEC-VIEWER-SECURITY-001
- AIXEM-SPEC-VIEWER-A11Y-001
navigation:
  group: viewer
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Viewer Specifications

The AIXEM viewer family is a derived, deterministic, read-only consumption layer over production renderer evidence. It never becomes circuit, layout, or project-composition authority.

## Canonical Retrieval Order

1. **Reference Viewer Contract 1** defines the product boundary, required capabilities, qualified identity, Viewer Model, and output compatibility.
2. **Viewer State and Interaction 1** defines deterministic startup state, view transitions, selection, search, layers, and viewport behavior.
3. **Viewer Security and Embedding 1** defines offline operation, inert authored text, CSP, and the no-network/no-persistence boundary.
4. **Viewer Accessibility Profile 1** defines keyboard access, semantic control state, visible focus, and narrow-viewport operability.
5. **Review Workbench Contract 1** extends the same Viewer Core with diagnostics, evidence, and provenance.

## Product Vocabulary

- **Reference Viewer:** `viewer.html`, the canonical read-only design-inspection surface.
- **Review Workbench:** `workbench.html`, the read-only engineering-review extension.
- **Viewer Core:** shared runtime state and interaction behavior.
- **Viewer Model:** schema-validated derived data reproducible from resolved renderer evidence.
- **Editor:** a separate future product capable of changing authoritative AIXEM files; it is outside Viewer Contract 1.

## Authority Boundary

```text
.aixem / .aixlayout / .aixproj
          | authoritative
          v
Production Renderer
          | derived evidence
          v
resolved scene(s) + SVG
          | deterministic adapter
          v
Viewer Model 1
          | ephemeral state only
          v
Reference Viewer 1 / Review Workbench 1
```

## Complete Section Map

This list is the complete authored link surface for the `viewer` navigation section. The navigation registry remains the machine-readable membership owner.

- [Reference Viewer Contract 1](reference-viewer-contract.md) — `AIXEM-SPEC-VIEWER-001`
- [Review Workbench Contract 1](review-workbench-contract.md) — `AIXEM-SPEC-WORKBENCH-001`
- [Viewer State and Interaction 1](viewer-state-and-interaction.md) — `AIXEM-SPEC-VIEWER-STATE-001`
- [Viewer Security and Embedding 1](viewer-security-and-embedding.md) — `AIXEM-SPEC-VIEWER-SECURITY-001`
- [Viewer Accessibility Profile 1](viewer-accessibility-profile.md) — `AIXEM-SPEC-VIEWER-A11Y-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
