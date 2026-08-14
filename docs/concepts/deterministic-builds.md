---
id: AIXEM-CONCEPT-DETERMINISM-001
title: Deterministic Builds
status: normative
version: '1.0'
language: en
domain: concepts
kind: concept
summary: Defines digest locks, fixed generation metadata, stable ordering, and reproducible derived artifacts.
authority:
- build-reproducibility
aliases:
- deterministic build
- reproducible output
- digest locking
agent:
  priority: critical
  estimated_tokens: 1369
  intents:
  - validate-project
  - publish-release
  - build-documentation
depends_on: []
related:
- AIXEM-SPEC-PROJECT-LOCK-001
- AIXEM-CONF-RELEASE-001
- AIXEM-SPEC-VIEWER-001
- AIXEM-CONF-REFERENCE-VIEWER-001
navigation:
  group: concepts
  order: 80
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-CORE-0030
  title: Locked inputs
  level: MUST
  statement: A project build MUST verify the digest of every locked source, library, symbol, layout, and style input
    before rendering.
  validator: schematic.digest_lock
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0030.json
- id: AIXEM-REQ-CORE-0031
  title: Stable generated metadata
  level: MUST
  statement: Generated indexes and manifests MUST use stable ordering and controlled generation metadata.
  validator: docs.deterministic
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0031.json
- id: AIXEM-REQ-CORE-0032
  title: Rebuild equivalence
  level: MUST
  statement: An unchanged canonical source tree MUST reproduce equivalent generated documentation and reference indexes.
  validator: docs.reproducibility
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0032.json
---

# Deterministic Builds

Defines digest locks, fixed generation metadata, stable ordering, and reproducible derived artifacts.

> **Document ID:** `AIXEM-CONCEPT-DETERMINISM-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The model described here is independent from any particular renderer or workbench implementation.

The declared authority scopes are `build-reproducibility`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Digest mismatch is fail-closed.
- Generated timestamps are controlled.
- Manifests exclude self-referential digest fields.

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

<a id="AIXEM-REQ-CORE-0030"></a>

### AIXEM-REQ-CORE-0030 — Locked inputs

**MUST.** A project build MUST verify the digest of every locked source, library, symbol, layout, and style input before rendering.

- Verification mode: `automated`
- Validator: `schematic.digest_lock`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0030.json`

<a id="AIXEM-REQ-CORE-0031"></a>

### AIXEM-REQ-CORE-0031 — Stable generated metadata

**MUST.** Generated indexes and manifests MUST use stable ordering and controlled generation metadata.

- Verification mode: `automated`
- Validator: `docs.deterministic`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0031.json`

<a id="AIXEM-REQ-CORE-0032"></a>

### AIXEM-REQ-CORE-0032 — Rebuild equivalence

**MUST.** An unchanged canonical source tree MUST reproduce equivalent generated documentation and reference indexes.

- Verification mode: `automated`
- Validator: `docs.reproducibility`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0032.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Project Lock Contract 1](../specifications/project/project-lock-contract.md) — `AIXEM-SPEC-PROJECT-LOCK-001`
- [Release Gates](../conformance/release-gates.md) — `AIXEM-CONF-RELEASE-001`
## Deterministic Authoring Evidence

Equivalent baseline/final artifact snapshots and validator versions must yield byte-stable diagnostic ordering, change-set serialization, state digests, and Authoring Run Record 1. Wall-clock timestamps, random IDs, model reasoning text, credentials, and environment dumps are excluded from the deterministic contract.

Closure repeats production rendering three times and compares artifact digests. The external agent's prose or token path may vary; the retained authority, diagnostics, changes, validation results, and render evidence remain reproducible.

## Viewer Artifact Determinism

Viewer Model 1, `viewer.html`, and `workbench.html` join SVG and resolved-scene products in the deterministic render boundary. Stable serialization uses ordered project/hierarchy data, sorted model keys, controlled release metadata, fixed templates, no random DOM IDs, and no wall-clock values. Three complete renders from identical staged inputs must produce identical bytes for all three Viewer artifacts.

Ephemeral interaction state is not serialized in P0. For the same model and action sequence, state transitions remain deterministic even though a user's in-memory session is not itself a release artifact.
<a id="0-5-6-deterministic-stages-versus-stochastic-attempts"></a>
## Deterministic stages versus stochastic attempts

Equivalent task, route pack, incomplete start state, and attempt ID produce an identical cold-start stage. Independent external-agent attempts may produce different valid authoritative edits and are therefore immutable/digest-addressed rather than required to be byte-identical. Once one final authoritative state is locked, the existing deterministic renderer and Viewer obligations still apply.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
