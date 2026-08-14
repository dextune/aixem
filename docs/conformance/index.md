---
id: AIXEM-CONF-INDEX-001
title: Conformance
status: informative
version: '1.0'
language: en
domain: conformance
kind: index
summary: Explains how requirements, validators, tests, evidence, compatibility, and release gates establish conformance.
authority:
- conformance-navigation
aliases:
- conformance
- compliance
- validation evidence
agent:
  priority: normal
  estimated_tokens: 1097
  intents:
  - validate-project
  - publish-release
depends_on: []
related:
- AIXEM-CONF-REQUIREMENTS-001
- AIXEM-CONF-VALIDATION-001
- AIXEM-CONF-RELEASE-001
navigation:
  group: conformance
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Conformance

Explains how requirements, validators, tests, evidence, compatibility, and release gates establish conformance.

> **Document ID:** `AIXEM-CONF-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Conformance is demonstrated by observed evidence from a specific release build, not by a prose claim alone.

The declared authority scopes are `conformance-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Requirement IDs are traceable.
- Validation modes are explicit.
- Evidence is release-specific.
- A release gate verifies the final package.

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

- Preserve requirement ids are traceable as an explicit, reviewable part of the task.
- Preserve validation modes are explicit as an explicit, reviewable part of the task.
- Preserve evidence is release-specific as an explicit, reviewable part of the task.
- Preserve a release gate verifies the final package as an explicit, reviewable part of the task.
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

- [Requirement Model](requirements.md) — `AIXEM-CONF-REQUIREMENTS-001`
- [Validation Architecture](validation.md) — `AIXEM-CONF-VALIDATION-001`
- [Release Gates](release-gates.md) — `AIXEM-CONF-RELEASE-001`

## Hierarchical Project Profile

- [Hierarchical Project Conformance](hierarchical-project.md) defines H001–H015, N001–N015, deterministic render evidence, and the public claim boundary.

## Complete Section Map

This list is the complete authored link surface for the `conformance` navigation section. The navigation registry remains the machine-readable membership owner.

- [Requirement Model](requirements.md) — `AIXEM-CONF-REQUIREMENTS-001`
- [Validation Architecture](validation.md) — `AIXEM-CONF-VALIDATION-001`
- [Test Suite](test-suite.md) — `AIXEM-CONF-TESTS-001`
- [Symbol Expressiveness Conformance Profile 1](symbol-expressiveness.md) — `AIXEM-CONF-SYMBOL-EXP-001`
- [Static 2D Block Compatibility Profile 1](static-2d-block-profile.md) — `AIXEM-CONF-B2D-001`
- [Compatibility and Migration Conformance](compatibility-conformance.md) — `AIXEM-CONF-COMPAT-001`
- [Release Gates](release-gates.md) — `AIXEM-CONF-RELEASE-001`
- [Hierarchical Project Conformance](hierarchical-project.md) — `AIXEM-CONF-HIERARCHICAL-PROJECT-001`
- [Reference Viewer Conformance](reference-viewer.md) — `AIXEM-CONF-REFERENCE-VIEWER-001`
- [Agent Diagnostic Registry and Conformance](agent-diagnostics.md) — `AIXEM-CONF-AGENT-DIAGNOSTICS-001`
- [Agent Authoring Closed-Loop Conformance](agent-authoring.md) — `AIXEM-CONF-AGENT-AUTHORING-001`
- [Live-Agent Cold-Start Conformance](live-agent-cold-start.md) — `AIXEM-CONF-AGENT-LIVE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
