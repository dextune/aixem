---
id: AIXEM-CONF-VALIDATION-001
title: Validation Architecture
status: normative
version: '1.0'
language: en
domain: conformance
kind: guide
summary: Defines validator scopes, result severity, fail-closed behavior, diagnostic structure, and evidence recording.
authority:
- validation-architecture
aliases:
- validation
- validators
- validation architecture
agent:
  priority: critical
  estimated_tokens: 2097
  intents:
  - validate-project
  - publish-release
  - build-documentation
depends_on:
- AIXEM-CONF-REQUIREMENTS-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-CONF-TESTS-001
- AIXEM-AGENT-VALIDATION-001
navigation:
  group: conformance
  order: 30
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-CONF-0010
  title: Machine-readable result
  level: MUST
  statement: A release-critical validator MUST emit a machine-readable result with check IDs, status, diagnostics,
    and observed metrics.
  validator: docs.evidence
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0010.json
- id: AIXEM-REQ-CONF-0011
  title: Error severity
  level: MUST
  statement: A failed MUST requirement MUST produce an error and prevent release completion.
  validator: docs.release_gate
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0011.json
- id: AIXEM-REQ-CONF-0012
  title: Observed evidence
  level: MUST
  statement: Evidence MUST record the actual observed value or artifact digest used to reach its status.
  validator: docs.evidence
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0012.json
---

# Validation Architecture

Defines validator scopes, result severity, fail-closed behavior, diagnostic structure, and evidence recording.

> **Document ID:** `AIXEM-CONF-VALIDATION-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Conformance is demonstrated by observed evidence from a specific release build, not by a prose claim alone.

The declared authority scopes are `validation-architecture`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Schema checks validate shape.
- Cross-artifact checks validate closure.
- Visual review validates human usability.
- Release checks validate packaging.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-CONF-0010"></a>

### AIXEM-REQ-CONF-0010 — Machine-readable result

**MUST.** A release-critical validator MUST emit a machine-readable result with check IDs, status, diagnostics, and observed metrics.

- Verification mode: `automated`
- Validator: `docs.evidence`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0010.json`

<a id="AIXEM-REQ-CONF-0011"></a>

### AIXEM-REQ-CONF-0011 — Error severity

**MUST.** A failed MUST requirement MUST produce an error and prevent release completion.

- Verification mode: `automated`
- Validator: `docs.release_gate`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0011.json`

<a id="AIXEM-REQ-CONF-0012"></a>

### AIXEM-REQ-CONF-0012 — Observed evidence

**MUST.** Evidence MUST record the actual observed value or artifact digest used to reach its status.

- Verification mode: `automated`
- Validator: `docs.evidence`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0012.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Requirement Model](requirements.md) — `AIXEM-CONF-REQUIREMENTS-001`
- [Test Suite](test-suite.md) — `AIXEM-CONF-TESTS-001`
- [Three-Stage Validation Loop](../agent/validation-loop.md) — `AIXEM-AGENT-VALIDATION-001`
## Agent Authoring Validation Order

For a route-bounded authoring operation, validate in this order:

1. resolve task packet, active child route, write scope, and baseline digests;
2. run schema and route-local preflight validators;
3. compute the before/after change set and reject scope or generated-output violations;
4. normalize failures to stable diagnostics and repair the smallest owner;
5. repeat narrow validation until blocking diagnostics close without stall or oscillation;
6. run full source/project validation, production render, Viewer Model validation, and three-run determinism;
7. validate and retain Authoring Run Record 1.

A final valid-looking SVG cannot bypass any earlier step.
<a id="0-5-1-authoring-validation-layers"></a>
## Authoring Validation Layers

The authoring release adds these validator responsibilities:

| Validator | Scope |
|---|---|
| `docs.authoring_reference` | active schema fields and primitive types are covered by canonical agent-readable docs |
| `docs.authoring_snippets` | source-backed Markdown JSON snippets parse and equal their canonical example sources |
| `schematic.symbol_design` | grid, orientation, lead/port coincidence, pitch, field/body checks |
| `schematic.authoring_binding` | asset lock, total `portMap`, existing targets, declared field sources |
| `schematic.renderer_contract` | field, variant, parameter, port mapping, and fail-closed resolution behavior |
| `schematic.authoring_examples` | all golden examples validate and rerender deterministically |
| `agent.authoring_routes` | simple/composite route chain, budgets, section targets, task-packet digests |
| `agent.visual_qa` | evidence and defect-to-authority repair workflow coverage |
| `manual.symbol_visual_review` | functional grouping, legibility, ambiguity, and normal-zoom usefulness |

### Required Validation Order

```text
parse/schema
→ feature and asset lock
→ semantic/component/port closure
→ symbol design and binding
→ layout route closure
→ renderer contract and deterministic render
→ visual QA review
→ release integrity
```

A later pass cannot legitimize an earlier contract failure. Generated SVG, task packets, site pages, and evidence are regenerated from authoritative inputs and are never hand-patched as the final repair.
<a id="0-5-2-expressiveness-validation-order"></a>
## Expressiveness Validation Order

Execute symbol expressiveness validation in this order:

```text
case contract and symbol schema
→ required capability and inventory checks
→ component-port / symbol-port closure
→ grid, lead coincidence, and non-degenerate geometry
→ production project validation and rendering
→ canonical SVG and resolved-scene determinism
→ approved digest comparison
→ digest-bound structured visual review
→ tier summary and independent MU result
```

`tools/validate_symbol_corpus.py` is thin orchestration around the production renderer. A passing alternate test renderer is not valid conformance evidence.

Use `--update-approved-digests` only after a deliberate source or renderer change has been reviewed. Normal tests fail closed on changed approved output.
<a id="0-5-6-live-agent-validation-order"></a>
## Authoring Integrity Result Hierarchy

AIXEM reports authoring results without collapsing their meaning:

```text
STRUCTURAL_PASS
  schema, binding, geometry, grid, lint, deterministic render

PART_SEMANTIC_PASS | GENERIC_TEMPLATE_PASS | PLACEHOLDER
  component provenance, identity, pinout-source review, minimum semantic contract

PIN_SEMANTIC / COMPATIBILITY RESULT
  profile consistency plus bounded PASS/WARN/ERROR/NOT_EVALUATED checks

CIRCUIT_INTENT_REVIEW_PASS
  component role, intended pin use, required pins/no-connects, task-relevant properties
```

The compatibility layer is intentionally conservative. It detects clear output, power-output, and connected-no-connect conflicts, while tri-state, open-driver, bidirectional, input-only, and unspecified cases remain warnings or unevaluated where higher-level evidence is absent. It does not claim voltage, timing, safety, simulation, or production correctness.

## Live-agent validation order

Validate in this order: task resolution; stage isolation/determinism; executor descriptor and bounds; observation stream; existing authoring `check/close`; actual-workspace invariant scoring; live-run evidence digest; exact attempt-set denominator; Tier A/Tier B claim gate. Failure at an earlier structural boundary blocks a success claim even when later files appear valid.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
