---
id: AIXEM-CONCEPT-AUTHORITY-001
title: Authority Model
status: normative
version: '1.0'
language: en
domain: concepts
kind: concept
summary: Defines which artifact class owns semantics, component definitions, symbol graphics, layout, project locks, presentation, and documentation.
authority:
- authority-layer-model
aliases:
- authority model
- source of truth
- ownership layers
agent:
  priority: critical
  estimated_tokens: 1307
  intents:
  - create-schematic
  - create-symbol
  - route-nets
  - change-architecture
  - inspect-artifact
depends_on: []
related:
- AIXEM-SPEC-AUTHORITY-001
- AIXEM-ARCH-PIPELINE-001
- AIXEM-SPEC-VIEWER-001
- AIXEM-SPEC-VIEWER-STATE-001
navigation:
  group: concepts
  order: 30
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-CORE-0004
  title: Single owning layer
  level: MUST
  statement: Each behavior or data field MUST have one declared authority layer.
  validator: docs.artifact_ownership
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0004.json
- id: AIXEM-REQ-CORE-0005
  title: Derived artifact discipline
  level: MUST
  statement: A generated artifact MUST NOT supersede the canonical source from which it was derived.
  validator: docs.generated_freshness
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0005.json
---
# Authority Model

Defines which artifact class owns semantics, component definitions, symbol graphics, layout, project locks, presentation, and documentation.

> **Document ID:** `AIXEM-CONCEPT-AUTHORITY-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The model described here is independent from any particular renderer or workbench implementation.

The declared authority scope is `authority-layer-model`. The normative conflict-resolution order is owned separately by the Authority and Precedence contract. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Change the highest-authority source.
- Regenerate downstream artifacts.
- Fail closed when active normative authorities conflict.

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

<a id="AIXEM-REQ-CORE-0004"></a>

### AIXEM-REQ-CORE-0004 — Single owning layer

**MUST.** Each behavior or data field MUST have one declared authority layer.

- Verification mode: `automated`
- Validator: `docs.artifact_ownership`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0004.json`

<a id="AIXEM-REQ-CORE-0005"></a>

### AIXEM-REQ-CORE-0005 — Derived artifact discipline

**MUST.** A generated artifact MUST NOT supersede the canonical source from which it was derived.

- Verification mode: `automated`
- Validator: `docs.generated_freshness`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0005.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Authority and Precedence](../specifications/core/authority-precedence.md) — `AIXEM-SPEC-AUTHORITY-001`
- [Build and Authoring Pipeline](../architecture/pipeline.md) — `AIXEM-ARCH-PIPELINE-001`
## Agent Execution Evidence Is Non-Authority

`authoring-diagnostics.json`, Authoring Change-Set 1, execution packets, and Authoring Run Record 1 are deterministic derived evidence. They describe an operation over `.aixem`, symbol/library assets, layout, and project authority; they never define endpoints, connectivity, placement, route geometry, hierarchy, or project-net membership.

A diagnostic points to the smallest owner. A change set proves whether the active route respected that owner. A run record proves closure. None may be edited to conceal an unresolved defect, and generated presentation artifacts remain invalid repair targets.

## Viewer Runtime State Is Not Authority

AIXEM 0.5.4 adds a derived consumption layer without adding an authored authority format. The authority chain is:

```text
.aixem       semantic authority
.aixlayout   local presentation authority
.aixproj     project composition authority
resolved scene / SVG    deterministic evidence
Viewer Model 1          derived inspection index
Viewer runtime state    ephemeral presentation state
```

Mode, active sheet, QID selection, search text, layer visibility, viewport transform, and panel state cannot supersede semantic, layout, project, or renderer evidence. A Viewer defect must be repaired in Viewer ownership unless the evidence itself proves an upstream authority defect.
<a id="0-5-6-task-stage-and-live-evidence-authority"></a>
## Task, stage, and live-evidence authority

`agent-task.json`, `stage-manifest.json`, executor descriptors, observation logs, invariant manifests, evaluator results, live-run evidence, and attempt sets are non-authoritative control/evidence artifacts. They may request, constrain, execute, observe, or evaluate work, but they never define circuit semantics. The active canonical route owns write permission; a task may only narrow it.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
