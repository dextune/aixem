---
id: AIXEM-GOV-INDEX-001
title: Governance
status: informative
version: '1.0'
language: en
domain: governance
kind: index
summary: Policies for versioning, compatibility, deprecation, release execution, and shared terminology.
authority:
- governance-navigation
aliases:
- governance
- project policy
- standards governance
agent:
  priority: normal
  estimated_tokens: 923
  intents:
  - change-architecture
  - publish-release
depends_on: []
related:
- AIXEM-GOV-VERSIONING-001
- AIXEM-GOV-COMPAT-001
- AIXEM-GOV-RELEASE-001
- AIXEM-GOV-DOC-AUTHORING-001
navigation:
  group: governance
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Governance

Policies for versioning, compatibility, deprecation, release execution, and shared terminology.

> **Document ID:** `AIXEM-GOV-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

This policy controls long-lived identity and release behavior across documentation, schemas, and implementations.

The declared authority scopes are `governance-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Stable IDs outlive paths.
- Breaking changes require migration.
- Deprecated material remains discoverable.
- Release claims are evidence-backed.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Identify the reader or agent task before selecting a document.
2. Read the minimum linked concept or guide required for that task.
3. Use the normative specification when a rule affects compatibility or conformance.
4. Finish with the relevant validation and evidence page.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve stable ids outlive paths as an explicit, reviewable part of the task.
- Preserve breaking changes require migration as an explicit, reviewable part of the task.
- Preserve deprecated material remains discoverable as an explicit, reviewable part of the task.
- Preserve release claims are evidence-backed as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Versioning Policy](versioning.md) — `AIXEM-GOV-VERSIONING-001`
- [Compatibility Policy](compatibility-policy.md) — `AIXEM-GOV-COMPAT-001`
- [Release Process](release-process.md) — `AIXEM-GOV-RELEASE-001`
- [Documentation Authoring and Lifecycle Guide](documentation-authoring-guide.md) — `AIXEM-GOV-DOC-AUTHORING-001`

## Complete Section Map

This list is the complete authored link surface for the `governance` navigation section. The navigation registry remains the machine-readable membership owner.

- [Versioning Policy](versioning.md) — `AIXEM-GOV-VERSIONING-001`
- [Compatibility Policy](compatibility-policy.md) — `AIXEM-GOV-COMPAT-001`
- [Deprecation Policy](deprecation.md) — `AIXEM-GOV-DEPRECATION-001`
- [Release Process](release-process.md) — `AIXEM-GOV-RELEASE-001`
- [Terminology](terminology.md) — `AIXEM-GOV-TERMS-001`
- [Documentation Authoring and Lifecycle Guide](documentation-authoring-guide.md) — `AIXEM-GOV-DOC-AUTHORING-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
