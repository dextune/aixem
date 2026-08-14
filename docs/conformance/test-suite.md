---
id: AIXEM-CONF-TESTS-001
title: Test Suite
status: normative
version: '1.0'
language: en
domain: conformance
kind: reference
summary: Defines unit, integration, retrieval-corpus, deterministic rebuild, static-site, schematic, and archive
  tests.
authority:
- test-suite-contract
aliases:
- test suite
- repository tests
- conformance tests
agent:
  priority: critical
  estimated_tokens: 1596
  intents:
  - validate-project
  - publish-release
depends_on:
- AIXEM-CONF-VALIDATION-001
related:
- AIXEM-CONF-RELEASE-001
navigation:
  group: conformance
  order: 40
artifacts:
  owns:
  - tests/docs/test_repository.py
  - tests/docs/retrieval-corpus.json
  consumes: []
requirements:
- id: AIXEM-REQ-CONF-0020
  title: Retrieval corpus
  level: MUST
  statement: Every authored task route MUST have at least one successful corpus phrase that resolves to that route.
  validator: route.corpus
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0020.json
- id: AIXEM-REQ-CONF-0021
  title: Example integration test
  level: MUST
  statement: The release test suite MUST render and validate the bundled grid-controller project.
  validator: schematic.example
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0021.json
- id: AIXEM-REQ-CONF-0022
  title: Deterministic core outputs
  level: MUST
  statement: The test suite MUST compare deterministic core generated digests across consecutive unchanged builds.
  validator: docs.reproducibility
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0022.json
---

# Test Suite

Defines unit, integration, retrieval-corpus, deterministic rebuild, static-site, schematic, and archive tests.

> **Document ID:** `AIXEM-CONF-TESTS-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Conformance is demonstrated by observed evidence from a specific release build, not by a prose claim alone.

The declared authority scopes are `test-suite-contract`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Narrow tests run quickly.
- Integration tests exercise real artifacts.
- Corpus tests measure route precision.
- Manifest tests run on final output.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `tests/docs/test_repository.py`
- `tests/docs/retrieval-corpus.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-CONF-0020"></a>

### AIXEM-REQ-CONF-0020 — Retrieval corpus

**MUST.** Every authored task route MUST have at least one successful corpus phrase that resolves to that route.

- Verification mode: `automated`
- Validator: `route.corpus`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0020.json`

<a id="AIXEM-REQ-CONF-0021"></a>

### AIXEM-REQ-CONF-0021 — Example integration test

**MUST.** The release test suite MUST render and validate the bundled grid-controller project.

- Verification mode: `automated`
- Validator: `schematic.example`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0021.json`

<a id="AIXEM-REQ-CONF-0022"></a>

### AIXEM-REQ-CONF-0022 — Deterministic core outputs

**MUST.** The test suite MUST compare deterministic core generated digests across consecutive unchanged builds.

- Verification mode: `automated`
- Validator: `docs.reproducibility`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0022.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Validation Architecture](validation.md) — `AIXEM-CONF-VALIDATION-001`
- [Release Gates](release-gates.md) — `AIXEM-CONF-RELEASE-001`

<a id="0-5-1-authoring-test-inventory"></a>
## Authoring Test Inventory

The documentation test discovery includes:

- `tests/docs/test_authoring_reference.py` — schema/reference coverage and source-backed snippet integrity;
- `tests/docs/test_authoring_examples.py` — design profile, all golden examples, deterministic rendering, and broken-fixture detection;
- `tests/docs/test_renderer_contract.py` — variant, parameter, field, port-map, and fail-closed binding behavior;
- `tests/docs/test_authoring_routes.py` — route budgets, composite child chain, task packets, source-inspection policy, and agent evaluation fixtures;
- existing repository tests — metadata, requirements, links, routes, examples, generated outputs, site, manifests, and archive integrity.

### Golden Example Coverage

| Fixture | Contract proven |
|---|---|
| `01-two-pin-passive` | body/leads, lead-port coincidence, reference/value fields, basic binding |
| `02-connector` | repeated 5 mm pitch, numbering/naming, many total mappings |
| `03-multi-pin-ic` | four-side functional grouping, power/return placement, body sizing |
| `04-parameterized-variant` | variant and parameter precedence |
| `05-field-and-port-binding` | field direction/precedence and semantic port-keyed positions |
| `06-two-terminal-route` | direct/bent orthogonal two-terminal routing |
| `07-multi-terminal-junction` | explicit branch junction and unrelated crossing |
| `08-visual-repair` | active rejection and repair of lead-port mismatch |

### Release Thresholds

Schema validity, semantic/port closure, route-budget compliance, renderer success, and deterministic rerender are all 100% gates. Review-mode visual checks target at least 95% and may not conceal any release-critical diagnostic. Normal successful evaluation tasks record zero repository-wide discovery searches and zero renderer-source inspections.
<a id="0-5-2-symbol-expressiveness-test-inventory"></a>
## Symbol Expressiveness Test Inventory

The released suite adds:

- S001-S024 Core fixture validation;
- S025-S029 Extended fixture validation;
- S030 graphics pass plus negative shared-identity placement probe;
- B001-B006 Static 2D Block validation;
- exact corpus inventory and case-schema tests;
- current symbol-schema digest preservation;
- production-renderer identification and repeat-determinism tests;
- approved-digest and visual-review integrity tests;
- dimension-label regression coverage;
- plan implementation and three-cycle release evidence checks.

Release verification renders every case three times in the determinism pass. The complete three-perspective verification is then repeated for three independent cycles before packaging.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
