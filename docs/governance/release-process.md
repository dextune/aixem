---
id: AIXEM-GOV-RELEASE-001
title: Release Process
status: normative
version: '1.0'
language: en
domain: governance
kind: policy
summary: Defines release preparation, release-declared repeated clean verification, deterministic build, validation, visual review, manifest creation, archive creation, and checksum publication.
authority:
- release-process
aliases:
- release process
- publish release
- release checklist
agent:
  priority: high
  estimated_tokens: 782
  intents:
  - publish-release
depends_on:
- AIXEM-CONF-RELEASE-001
- AIXEM-ARCH-PIPELINE-001
related:
- AIXEM-GOV-VERSIONING-001
- AIXEM-SPEC-RELEASE-001
navigation:
  group: governance
  order: 50
artifacts:
  owns: []
  consumes: []
requirements: []
---
# Release Process

Defines release preparation, three refinement passes, deterministic build, validation, visual review, manifest creation, archive creation, and checksum publication.

> **Document ID:** `AIXEM-GOV-RELEASE-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

This policy controls long-lived identity and release behavior across documentation, schemas, and implementations.

The declared authority scopes are `release-process`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Release process.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Freeze canonical inputs
2. Complete the release-declared number of independent clean verification cycles; never fewer than three.
3. In every cycle, validate canonical content, agent retrieval, conformance, publication, and protected technical regressions.
4. Repair the smallest owning layer and restart the affected complete cycle.
5. Verify deterministic rebuilds.
6. Finalize evidence and manifest only after all required cycles pass.
7. Create the ZIP.
8. Verify ZIP checksum, complete membership, and safe paths independently.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve release process as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- A failed gate returns the release to the owning source layer; generated output is never hand-patched to force a pass.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Release Gates](../conformance/release-gates.md) — `AIXEM-CONF-RELEASE-001`
- [Build and Authoring Pipeline](../architecture/pipeline.md) — `AIXEM-ARCH-PIPELINE-001`
- [Versioning Policy](versioning.md) — `AIXEM-GOV-VERSIONING-001`
- [Release Integrity Contract](../specifications/documentation/release-integrity.md) — `AIXEM-SPEC-RELEASE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
