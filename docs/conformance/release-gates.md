---
id: AIXEM-CONF-RELEASE-001
title: Release Gates
status: normative
version: '1.0'
language: en
domain: conformance
kind: policy
summary: Defines the final conditions for documentation, examples, conformance evidence, generated freshness, manifests, and archive integrity.
authority:
- release-gate
aliases:
- release gates
- release validation
- ship criteria
agent:
  priority: critical
  estimated_tokens: 2002
  intents:
  - publish-release
  - validate-project
  - compose-project
depends_on:
- AIXEM-SPEC-RELEASE-001
- AIXEM-CONF-TESTS-001
related:
- AIXEM-GOV-RELEASE-001
- AIXEM-ARCH-PIPELINE-001
- AIXEM-CONF-HIERARCHICAL-PROJECT-001
- AIXEM-CONF-REFERENCE-VIEWER-001
navigation:
  group: conformance
  order: 60
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-CONF-0040
  title: Minimum repeated verification
  level: MUST
  statement: Every published release MUST record the release-declared number of completed independent refinement and validation passes, never fewer than three.
  validator: docs.three_passes
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0040.json
- id: AIXEM-REQ-CONF-0041
  title: All checks pass
  level: MUST
  statement: Every release-critical automated check MUST pass before the release manifest is finalized.
  validator: docs.release_gate
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0041.json
- id: AIXEM-REQ-CONF-0042
  title: Archive verification
  level: MUST
  statement: The distributed ZIP archive MUST pass integrity, traversal-safety, and checksum verification.
  validator: docs.archive_safety
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0042.json
---
# Release Gates

Defines the final conditions for documentation, examples, conformance evidence, generated freshness, manifests, and archive integrity.

> **Document ID:** `AIXEM-CONF-RELEASE-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Conformance is demonstrated by observed evidence from a specific release build, not by a prose claim alone.

The declared authority scopes are `release-gate`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Release gate.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Verify canonical sources
2. Verify generated freshness
3. Run repository tests
4. Render the example
5. Inspect site and workbench screenshots
6. Verify requirement evidence
7. Create and verify manifest
8. Create and verify ZIP

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-CONF-0040"></a>

### AIXEM-REQ-CONF-0040 — Minimum repeated verification

**MUST.** Every published release MUST record the release-declared number of completed independent refinement and validation passes, never fewer than three.

- Verification mode: `automated`
- Validator: `docs.three_passes`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0040.json`

<a id="AIXEM-REQ-CONF-0041"></a>

### AIXEM-REQ-CONF-0041 — All checks pass

**MUST.** Every release-critical automated check MUST pass before the release manifest is finalized.

- Verification mode: `automated`
- Validator: `docs.release_gate`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0041.json`

<a id="AIXEM-REQ-CONF-0042"></a>

### AIXEM-REQ-CONF-0042 — Archive verification

**MUST.** The distributed ZIP archive MUST pass integrity, traversal-safety, and checksum verification.

- Verification mode: `automated`
- Validator: `docs.archive_safety`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0042.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Documentation Release Integrity 1](../specifications/documentation/release-integrity.md) — `AIXEM-SPEC-RELEASE-001`
- [Test Suite](test-suite.md) — `AIXEM-CONF-TESTS-001`
- [Release Process](../governance/release-process.md) — `AIXEM-GOV-RELEASE-001`
- [Build and Authoring Pipeline](../architecture/pipeline.md) — `AIXEM-ARCH-PIPELINE-001`

## 0.5.8.1 Documentation and Reference-Chain Gate

The 0.5.8.1 release requires five complete clean verification cycles. Each cycle must validate root-link safety, complete `README.md` reachability for every human-authored Markdown document, full category-index coverage, current-release coherence, unique normative authority-scope ownership, canonical documentation and route integrity, inherited pre-live readiness, protected technical regressions, generated-output determinism, and release evidence.

External Tier B remains unexecuted and cannot be authorized by documentation closure.

<a id="0-5-4-reference-viewer-gate"></a>
## Reference Viewer Gate

A Reference Viewer release requires V001-V018, controlled-Chromium behavior, zero external requests, inert hostile text, keyboard and narrow-viewport operation, unique DOM IDs, complete qualified identity closure, distinct Viewer/Workbench profiles, and three-run byte identity for Viewer Model and both HTML products.

Pass 3 also re-runs every protected 0.5.3 hierarchy, symbol, Static 2D Block, authoring, and repository gate; compares protected circuit-render evidence; regenerates documentation/reference/site outputs; verifies traceability and manifest closure; and records all three release passes. See [Reference Viewer Conformance](reference-viewer.md).

<a id="0-5-3-hierarchical-project-gate"></a>
## Hierarchical Project Gate

A hierarchical release requires all H001–H015 cases and N001–N015 fixtures to match their expected outcomes, the ten-sheet case to complete, all legacy 0.5.2 corpora to pass, and three complete hierarchical render cycles to produce identical per-sheet, Overview, Composite, and resolved-project-scene digests.

The release also requires data-driven Workbench hierarchy, dedicated composition/project-routing agent routes, regenerated documentation indexes/site, and three recorded verification passes. See [Hierarchical Project Conformance](hierarchical-project.md).
## Agent Authoring Closed-Loop Gate

A 0.5.5 release must pass Agent Diagnostic, Change-Set, Execution, and Run Record schemas; complete P0 code-to-owner/route coverage; active child-stage write-scope enforcement; generated-output edit and unsafe-path rejection; stalled/oscillating loop detection; A001-A012 Tier A closure; protected renderer regression; and three-pass release verification.

The release claim must identify the actual evaluation tier. Tier A is mandatory deterministic harness/replay evidence. Tier B is optional live external-agent evidence and may be claimed only when the isolated cold-start executor, configuration, observed retrieval/actions, changes, and final record are retained.

<a id="0-5-2-expressiveness-release-gates"></a>
## Expressiveness Release Gates

The 0.5.2 release publishes four independent results:

| Result | Gate |
|---|---|
| S-Core | S001-S024 all pass automated, digest, determinism, and visual gates. |
| S-Extended | S-Core plus S025-S029 pass. |
| MU | S030 shared-identity independent-placement result is explicitly `PASS`, `PARTIAL`, or `NOT_SUPPORTED`. |
| B2D | B001-B006 all pass the limited Static 2D Block Profile. |

Release closure requires three verification cycles. Each cycle contains:

1. representability and coverage;
2. visual quality, scale, and agent usability;
3. regression, repeat determinism, compatibility, package, and claim integrity.

A failed cycle is repaired at the smallest owning layer and rerun in full. P2 remains `NOT_TRIGGERED` unless a reproduced F4 or approved F5 design justifies a contract extension.
<a id="0-5-6-live-agent-release-gate"></a>
## Live-agent release gate

AIXEM 0.5.6 engineering conformance requires all new contracts/schemas/tests, L001-L012 Tier A protocol evidence, Agent Evaluation 2 regression, protected renderer/Viewer hashes, documentation/traceability, and three complete release verification cycles. A public live-executor result additionally requires actual retained Tier B evidence. When no external runtime was available, the release must publish zero attempts, `liveExternalAgentExecuted=false`, `liveClaimAuthorized=false`, and a pending external-evidence gate.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
