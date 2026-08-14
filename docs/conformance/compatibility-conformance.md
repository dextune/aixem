---
id: AIXEM-CONF-COMPAT-001
title: Compatibility and Migration Conformance
status: normative
version: '1.0'
language: en
domain: conformance
kind: policy
summary: Defines version compatibility claims, migration maps, deprecated paths, and 0.4 reference-output compatibility.
authority:
- compatibility-conformance
aliases:
- compatibility conformance
- migration validation
- compatibility evidence
agent:
  priority: critical
  estimated_tokens: 1440
  intents:
  - migrate-baseline
  - publish-release
  - compose-project
depends_on: []
related:
- AIXEM-GOV-COMPAT-001
- AIXEM-RELEASE-040-001
- AIXEM-RELEASE-050-001
- AIXEM-CONF-HIERARCHICAL-PROJECT-001
- AIXEM-SPEC-VIEWER-001
navigation:
  group: conformance
  order: 50
artifacts:
  owns:
  - legacy/0.4-migration-map.json
  consumes: []
requirements:
- id: AIXEM-REQ-CONF-0030
  title: Complete baseline inventory
  level: MUST
  statement: The 0.5 release MUST inventory every file in the shipped 0.4 baseline used for migration analysis.
  validator: docs.legacy_inventory
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0030.json
- id: AIXEM-REQ-CONF-0031
  title: Migration disposition
  level: MUST
  statement: Every baseline inventory entry MUST have a migration disposition and target or rationale.
  validator: docs.legacy_inventory
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0031.json
- id: AIXEM-REQ-CONF-0032
  title: Compatibility reference build
  level: MUST
  statement: The 0.5 build MUST generate a route-and-card compatibility reference tree from canonical documentation.
  validator: docs.compatibility_reference
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0032.json
---

# Compatibility and Migration Conformance

Defines version compatibility claims, migration maps, deprecated paths, and 0.4 reference-output compatibility.

> **Document ID:** `AIXEM-CONF-COMPAT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Conformance is demonstrated by observed evidence from a specific release build, not by a prose claim alone.

The declared authority scopes are `compatibility-conformance`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Compatibility is explicit rather than implied.
- Generated compatibility JSON is not canonical.
- Migration maps preserve auditability.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `legacy/0.4-migration-map.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-CONF-0030"></a>

### AIXEM-REQ-CONF-0030 — Complete baseline inventory

**MUST.** The 0.5 release MUST inventory every file in the shipped 0.4 baseline used for migration analysis.

- Verification mode: `automated`
- Validator: `docs.legacy_inventory`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0030.json`

<a id="AIXEM-REQ-CONF-0031"></a>

### AIXEM-REQ-CONF-0031 — Migration disposition

**MUST.** Every baseline inventory entry MUST have a migration disposition and target or rationale.

- Verification mode: `automated`
- Validator: `docs.legacy_inventory`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0031.json`

<a id="AIXEM-REQ-CONF-0032"></a>

### AIXEM-REQ-CONF-0032 — Compatibility reference build

**MUST.** The 0.5 build MUST generate a route-and-card compatibility reference tree from canonical documentation.

- Verification mode: `automated`
- Validator: `docs.compatibility_reference`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0032.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Compatibility Policy](../governance/compatibility-policy.md) — `AIXEM-GOV-COMPAT-001`
- [AIXEM 0.4 Baseline](../releases/0.4.md) — `AIXEM-RELEASE-040-001`
- [AIXEM 0.5.0](../releases/0.5.md) — `AIXEM-RELEASE-050-001`

## Hierarchical Capability Claim Boundary

AIXEM 0.5.3 preserves valid `aixproj/1`, `aixlayout/1`, `.aixsym`, and `.aixlib` behavior while adding opt-in v2 project/layout contracts. The supported claim is deterministic composition of digest-locked independent sheets through semantic interface ports and explicit project nets, with Sheet, Overview, and Composite visualization.

This release does not claim full KiCad hierarchy compatibility, full OrCAD multi-page compatibility, reusable module instancing, buses, or implicit global nets.


<a id="0-5-2-symbol-claim-boundaries"></a>
## Symbol Claim Boundaries

The 0.5.2 release may claim only the AIXEM-owned tiers that actually pass against the recorded source and renderer digests.

Preferred wording:

> representative EDA schematic-symbol expressiveness corpus

Prohibited wording includes unqualified claims of KiCad compatibility, OrCAD compatibility, DWG/DXF round trip, AutoCAD Dynamic Block behavior, or support for every vendor-library edge case.

S-Core and S-Extended are graphical/binding conformance results. MU is a separate semantic result. B2D covers deterministic static vector blocks only.

## Viewer Contract Compatibility

Viewer contract versions are independent from circuit and project schema versions. Reference Viewer Contract 1 can consume valid `aixproj/1` and `aixproj/2` renderer evidence. A compatible Viewer 1 implementation may change non-semantic spacing, chrome styling, CSS class names, or internal JavaScript organization while preserving required capabilities, QID semantics, deterministic startup state, DOM contract markers, security, and browser behavior.

A change to required view modes, QID meaning, Viewer Model schema, DOM automation markers, selection semantics, or startup-state semantics requires Viewer Contract 2. Viewer normalization does not revise `.aixem`, `.aixsym`, `.aixlib`, `aixlayout/1`, `aixlayout/2`, `aixproj/1`, or `aixproj/2`.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
