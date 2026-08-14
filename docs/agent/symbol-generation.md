---
id: AIXEM-AGENT-SYMBOL-001
title: Symbol Generation Agent
status: informative
version: '1.0'
language: en
domain: agent
kind: guide
summary: Provides an agent sequence for turning a component endpoint contract into an original, compact, linted
  symbol asset.
authority:
- agent-symbol-workflow
aliases:
- symbol generation agent
- AI symbol authoring
- generate symbol
agent:
  priority: normal
  estimated_tokens: 844
  intents:
  - create-symbol
depends_on:
- AIXEM-SYMBOL-AUTHORING-001
- AIXEM-SYMBOL-LINT-001
related:
- AIXEM-AUTHORING-GUIDE-CREATE-LIBRARY-PART-001
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-AGENT-VALIDATION-001
navigation:
  group: agent
  order: 60
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Symbol Generation Agent

Provides an agent sequence for turning a component endpoint contract into an original, compact, linted symbol asset.

> **Document ID:** `AIXEM-AGENT-SYMBOL-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

The procedure is designed to minimize context while preserving authority, traceability, and fail-closed behavior.

The declared authority scopes are `agent-symbol-workflow`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Agent symbol workflow.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve the endpoint contract
2. Classify pins by function and direction
3. Choose grid-compatible body dimensions
4. Author original primitives and ports
5. Bind every port to an endpoint
6. Define fields and variants
7. Run schema, mapping, geometry, and independence checks

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve agent symbol workflow as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- Datasheets may inform endpoint names and functions; proprietary symbol graphics may not be copied into the AIXEM library.

## Explicit Pin Axis Model

Classify each endpoint on separate axes:

```text
component port ID          -> stable endpoint identity
port.type                  -> electrical behavior
metadata.pinSemantics      -> function, class, polarity, pair, capabilities
symbol port                -> graphic position and orientation
portMap                    -> component endpoint to symbol endpoint
```

For datasheet-backed parts, source-dependent pin semantics and alternate functions require review against the cited source. Do not infer capabilities from a familiar pin name, and do not mint component IDs by duplicating graphics.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Symbol Authoring Guide](../symbols/authoring-guide.md) — `AIXEM-SYMBOL-AUTHORING-001`
- [Symbol Lint](../symbols/symbol-lint.md) — `AIXEM-SYMBOL-LINT-001`
- [Three-Stage Validation Loop](validation-loop.md) — `AIXEM-AGENT-VALIDATION-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
