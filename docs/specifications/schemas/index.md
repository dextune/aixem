---
id: AIXEM-SPEC-SCHEMAS-001
title: JSON Schema Catalog
status: informative
version: '1.0'
language: en
domain: specifications
kind: index
summary: Catalogs the machine-readable project, library, symbol, layout, and documentation metadata schemas distributed
  with AIXEM 0.5.
authority:
- schema-catalog
aliases:
- schema catalog
- JSON schemas
- machine readable contracts
agent:
  priority: normal
  estimated_tokens: 1124
  intents:
  - inspect-artifact
  - validate-project
  - build-documentation
depends_on: []
related:
- AIXEM-SPEC-METADATA-001
- AIXEM-SPEC-SYMBOL-001
- AIXEM-SPEC-LAYOUT-001
- AIXEM-SPEC-PROJECT-LOCK-001
navigation:
  group: specifications
  order: 130
artifacts:
  owns:
  - docs/specifications/schemas/
  consumes: []
requirements: []
---

# JSON Schema Catalog

Catalogs the machine-readable project, library, symbol, layout, and documentation metadata schemas distributed with AIXEM 0.5.

> **Document ID:** `AIXEM-SPEC-SCHEMAS-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `schema-catalog`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Schemas constrain serialized structure.
- Normative prose defines semantics and precedence.
- Generated schema pages link to the exact raw JSON files.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Identify the reader or agent task before selecting a document.
2. Read the minimum linked concept or guide required for that task.
3. Use the normative specification when a rule affects compatibility or conformance.
4. Finish with the relevant validation and evidence page.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `docs/specifications/schemas/`

## Operational Rules

- Preserve schemas constrain serialized structure as an explicit, reviewable part of the task.
- Preserve normative prose defines semantics and precedence as an explicit, reviewable part of the task.
- Preserve generated schema pages link to the exact raw json files as an explicit, reviewable part of the task.
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

- [Documentation Metadata Contract 1](../documentation/metadata-contract.md) — `AIXEM-SPEC-METADATA-001`
- [Symbol Asset Contract 1](../symbols/symbol-contract.md) — `AIXEM-SPEC-SYMBOL-001`
- [Explicit Layout Contract 1](../layout/layout-contract.md) — `AIXEM-SPEC-LAYOUT-001`
- [Project Lock Contract 1](../project/project-lock-contract.md) — `AIXEM-SPEC-PROJECT-LOCK-001`

## Component Graphics 2 Schemas

The 0.5.3 hierarchical profile adds two immutable schema URIs without modifying released v1 files:

- `component-graphics-2/aixem-project-manifest-2.schema.json` — `https://schemas.aixem.org/component-graphics/aixproj/2`
- `component-graphics-2/aixem-explicit-layout-2.schema.json` — `https://schemas.aixem.org/component-graphics/aixlayout/2`

The line-oriented `.aixem` interface extension is governed by [Interface Port Contract 1](../core/interface-port-contract.md) and feature negotiation rather than a JSON schema.
## Agent Authoring 1 Schemas

AIXEM 0.5.5 adds derived, independently versioned execution-evidence schemas without changing circuit formats:

- `agent/aixem-agent-diagnostic-1.schema.json` — `https://schemas.aixem.org/agent/diagnostic/1`
- `agent/aixem-agent-change-set-1.schema.json` — `https://schemas.aixem.org/agent/change-set/1`
- `agent/aixem-agent-run-record-1.schema.json` — `https://schemas.aixem.org/agent/run-record/1`

These schemas explain and prove an authoring operation. They do not become circuit authority.
<a id="aixem-0-5-6-live-agent-evidence-schemas"></a>
## Live-agent evidence schemas

AIXEM 0.5.6 adds `aixem-agent-task-1`, `aixem-agent-stage-manifest-1`, `aixem-agent-executor-1`, `aixem-agent-observation-event-1`, `aixem-agent-evaluation-invariant-1`, `aixem-agent-live-run-1`, and `aixem-agent-attempt-set-1`. These schemas govern non-authoritative execution/evidence artifacts and do not revise circuit formats.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
