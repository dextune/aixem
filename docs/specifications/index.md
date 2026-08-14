---
id: AIXEM-SPEC-INDEX-001
title: Specifications
status: informative
version: '1.0'
language: en
domain: specifications
kind: index
summary: The normative contract set for document metadata, semantic authority, coordinates, graphics, layout, project
  locks, agent retrieval, and release integrity.
authority:
- specification-navigation
aliases:
- specifications
- standard
- normative documents
agent:
  priority: normal
  estimated_tokens: 1667
  intents:
  - inspect-artifact
  - change-architecture
  - validate-project
depends_on: []
related:
- AIXEM-SPEC-DOCUMENT-001
- AIXEM-SPEC-AUTHORITY-001
- AIXEM-SPEC-RELEASE-001
- AIXEM-SPEC-DOC-GOVERNANCE-001
navigation:
  group: specifications
  order: 10
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Specifications

The normative contract set for document metadata, semantic authority, coordinates, graphics, layout, project locks, agent retrieval, and release integrity.

> **Document ID:** `AIXEM-SPEC-INDEX-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `specification-navigation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Requirements use stable IDs.
- Schemas constrain serialized artifacts.
- Validators and evidence close the conformance chain.

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

- Preserve requirements use stable ids as an explicit, reviewable part of the task.
- Preserve schemas constrain serialized artifacts as an explicit, reviewable part of the task.
- Preserve validators and evidence close the conformance chain as an explicit, reviewable part of the task.
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

- [Canonical Document Model](core/document-model.md) — `AIXEM-SPEC-DOCUMENT-001`
- [Authority and Precedence](core/authority-precedence.md) — `AIXEM-SPEC-AUTHORITY-001`
- [Documentation Release Integrity 1](documentation/release-integrity.md) — `AIXEM-SPEC-RELEASE-001`
- [Repository Document Governance Contract 1](documentation/document-governance-contract.md) — `AIXEM-SPEC-DOC-GOVERNANCE-001`

## Hierarchical Composition Specifications

- [Interface Port Contract 1](core/interface-port-contract.md)
- [Hierarchical Sheet-Port Layout Contract 2](layout/hierarchical-sheet-port-contract.md)
- [Project Composition Contract 2](project/project-composition-contract.md)

These contracts extend, rather than replace, the immutable v1 project and layout contracts.

## Complete Section Map

This list is the complete authored link surface for the `specifications` navigation section. The navigation registry remains the machine-readable membership owner.

- [Canonical Document Model](core/document-model.md) — `AIXEM-SPEC-DOCUMENT-001`
- [Coordinate and Unit System](core/coordinate-system.md) — `AIXEM-SPEC-COORD-001`
- [Authority and Precedence](core/authority-precedence.md) — `AIXEM-SPEC-AUTHORITY-001`
- [Grid Schematic Profile 1](schematic/grid-profile.md) — `AIXEM-SPEC-GRID-PROFILE-001`
- [Schematic Presentation Profile 1](schematic/visual-profile.md) — `AIXEM-SPEC-VISUAL-PROFILE-001`
- [Symbol Asset Contract 1](symbols/symbol-contract.md) — `AIXEM-SPEC-SYMBOL-001`
- [Explicit Layout Contract 1](layout/layout-contract.md) — `AIXEM-SPEC-LAYOUT-001`
- [Project Lock Contract 1](project/project-lock-contract.md) — `AIXEM-SPEC-PROJECT-LOCK-001`
- [Agent Retrieval Profile 1](agent/retrieval-profile.md) — `AIXEM-SPEC-AGENT-RETRIEVAL-001`
- [Documentation Metadata Contract 1](documentation/metadata-contract.md) — `AIXEM-SPEC-METADATA-001`
- [Repository Document Governance Contract 1](documentation/document-governance-contract.md) — `AIXEM-SPEC-DOC-GOVERNANCE-001`
- [Documentation Release Integrity 1](documentation/release-integrity.md) — `AIXEM-SPEC-RELEASE-001`
- [JSON Schema Catalog](schemas/index.md) — `AIXEM-SPEC-SCHEMAS-001`
- [Symbol Design Profile 1](symbols/symbol-design-profile.md) — `AIXEM-SPEC-SYMBOL-DESIGN-001`
- [Renderer Contract 1](renderer/renderer-contract.md) — `AIXEM-SPEC-RENDERER-001`
- [Interface Port Contract 1](core/interface-port-contract.md) — `AIXEM-SPEC-INTERFACE-PORT-001`
- [Hierarchical Sheet-Port Layout Contract 2](layout/hierarchical-sheet-port-contract.md) — `AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001`
- [Project Composition Contract 2](project/project-composition-contract.md) — `AIXEM-SPEC-PROJECT-COMPOSITION-001`
- [Agent Diagnostic Contract 1](agent/diagnostic-contract.md) — `AIXEM-SPEC-AGENT-DIAGNOSTIC-001`
- [Authoring Change-Set Contract 1](agent/authoring-change-set-contract.md) — `AIXEM-SPEC-AGENT-CHANGESET-001`
- [Authoring Execution Contract 1](agent/authoring-execution-contract.md) — `AIXEM-SPEC-AGENT-EXECUTION-001`
- [Authoring Run Record 1](agent/authoring-run-record.md) — `AIXEM-SPEC-AGENT-RUN-001`
- [Agent Task Contract 1](agent/agent-task-contract.md) — `AIXEM-SPEC-AGENT-TASK-001`
- [Cold-Start Stage Contract 1](agent/cold-start-stage-contract.md) — `AIXEM-SPEC-AGENT-STAGE-001`
- [Live Executor Protocol 1](agent/live-executor-protocol.md) — `AIXEM-SPEC-AGENT-EXECUTOR-LIVE-001`
- [Observation Event Contract 1](agent/observation-event-contract.md) — `AIXEM-SPEC-AGENT-OBSERVATION-001`
- [Evaluation Invariant Contract 1](agent/evaluation-invariant-contract.md) — `AIXEM-SPEC-AGENT-EVAL-INVARIANT-001`
- [Live Run Evidence 1](agent/live-run-evidence.md) — `AIXEM-SPEC-AGENT-LIVE-RUN-001`
- [Library Layout and Part Integrity Contract](components/library-layout-contract.md) — `AIXEM-SPEC-LIBRARY-LAYOUT-001`
- [Pin Electrical Semantics Profile 1](components/pin-electrical-semantics-profile.md) — `AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
