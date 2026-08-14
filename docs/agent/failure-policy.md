---
id: AIXEM-AGENT-FAILURE-001
title: Fail-Closed Policy
status: normative
version: '1.0'
language: en
domain: agent
kind: policy
summary: Defines conditions under which an agent or build must stop instead of guessing, repairing downstream output,
  or suppressing evidence.
authority:
- agent-failure-policy
aliases:
- fail closed
- agent failure
- stop conditions
agent:
  priority: critical
  estimated_tokens: 1300
  intents:
  - validate-project
  - change-architecture
  - publish-release
depends_on:
- AIXEM-SPEC-AUTHORITY-001
related:
- AIXEM-CONF-RELEASE-001
navigation:
  group: agent
  order: 90
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-AGENT-0030
  title: Digest mismatch stop
  level: MUST
  statement: An agent or build MUST stop when a required locked digest does not match.
  validator: schematic.digest_lock
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0030.json
- id: AIXEM-REQ-AGENT-0031
  title: Missing canonical source stop
  level: MUST
  statement: An agent MUST stop when a required canonical source or route target is absent.
  validator: route.targets
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0031.json
- id: AIXEM-REQ-AGENT-0032
  title: Unsupported required feature stop
  level: MUST
  statement: A renderer MUST stop when a required project or symbol feature is unsupported.
  validator: schematic.feature_support
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0032.json
---

# Fail-Closed Policy

Defines conditions under which an agent or build must stop instead of guessing, repairing downstream output, or suppressing evidence.

> **Document ID:** `AIXEM-AGENT-FAILURE-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The procedure is designed to minimize context while preserving authority, traceability, and fail-closed behavior.

The declared authority scopes are `agent-failure-policy`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Do not invent absent rules.
- Do not patch generated output as the final fix.
- Report the failed invariant with the observed evidence.

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

<a id="AIXEM-REQ-AGENT-0030"></a>

### AIXEM-REQ-AGENT-0030 — Digest mismatch stop

**MUST.** An agent or build MUST stop when a required locked digest does not match.

- Verification mode: `automated`
- Validator: `schematic.digest_lock`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0030.json`

<a id="AIXEM-REQ-AGENT-0031"></a>

### AIXEM-REQ-AGENT-0031 — Missing canonical source stop

**MUST.** An agent MUST stop when a required canonical source or route target is absent.

- Verification mode: `automated`
- Validator: `route.targets`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0031.json`

<a id="AIXEM-REQ-AGENT-0032"></a>

### AIXEM-REQ-AGENT-0032 — Unsupported required feature stop

**MUST.** A renderer MUST stop when a required project or symbol feature is unsupported.

- Verification mode: `automated`
- Validator: `schematic.feature_support`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0032.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Authority and Precedence](../specifications/core/authority-precedence.md) — `AIXEM-SPEC-AUTHORITY-001`
- [Release Gates](../conformance/release-gates.md) — `AIXEM-CONF-RELEASE-001`
## Closed-Loop Blocking Conditions

An authoring run fails closed when a blocking diagnostic has no registered authority owner or remediation route, a file changes outside the active child route scope, a generated output is hand-edited, a path escapes the staged root, a project lock changes beyond an allowed digest update, a failure state stalls or oscillates, rendering is nondeterministic, or closure is requested with remaining errors.

The machine response preserves the diagnostic code, artifact, structured location, owner, route, change-set evidence, and iteration state. Agents must repair the upstream authoritative source or escalate a true implementation defect; they must not suppress evidence or reclassify generated output as authority.

Tier A replay evidence and Tier B live-agent evidence are also fail-closed claims: a release must record `liveExternalAgentExecuted=false` when no external executor actually ran.
<a id="0-5-6-live-attempt-failure-retention"></a>
## Live-attempt failure retention

`FAIL`, `TIMEOUT`, `EXECUTOR_ERROR`, and `INVALID_STAGE` are retained evidence, not disposable noise. A zero process exit with failed closure or invariants is `FAIL`. A timeout after edits remains `TIMEOUT` and the workspace is scored/retained when safe. An unavailable process is `EXECUTOR_ERROR`. Never repair the workspace in the evaluator or omit a failed attempt from the denominator.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
