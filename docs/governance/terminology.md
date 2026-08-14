---
id: AIXEM-GOV-TERMS-001
title: Terminology
status: normative
version: '1.0'
language: en
domain: governance
kind: reference
summary: Defines consistent meanings for entity, endpoint, net, component type, symbol port, placement, path, junction,
  project lock, canonical document, route, and evidence.
authority:
- terminology
aliases:
- terminology
- glossary
- definitions
agent:
  priority: high
  estimated_tokens: 825
  intents:
  - learn-aixem
  - change-architecture
  - inspect-artifact
depends_on: []
related:
- AIXEM-CONCEPT-INDEX-001
- AIXEM-FORMAT-INDEX-001
navigation:
  group: governance
  order: 60
artifacts:
  owns:
  - docs/_meta/glossary.yaml
  consumes: []
requirements: []
---

# Terminology

Defines consistent meanings for entity, endpoint, net, component type, symbol port, placement, path, junction, project lock, canonical document, route, and evidence.

> **Document ID:** `AIXEM-GOV-TERMS-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

This policy controls long-lived identity and release behavior across documentation, schemas, and implementations.

The declared authority scopes are `terminology`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Entity: a semantic instance.
- Endpoint: a connectable semantic interface.
- Net: an explicit set of endpoint references.
- Port: a symbol presentation of an endpoint.
- Route: explicit geometry bound to a net.
- Canonical document: an authored rule source.
- Task route: a bounded ordered reading plan.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `docs/_meta/glossary.yaml`

## Operational Rules

- Preserve entity: a semantic instance as an explicit, reviewable part of the task.
- Preserve endpoint: a connectable semantic interface as an explicit, reviewable part of the task.
- Preserve net: an explicit set of endpoint references as an explicit, reviewable part of the task.
- Preserve port: a symbol presentation of an endpoint as an explicit, reviewable part of the task.
- Preserve route: explicit geometry bound to a net as an explicit, reviewable part of the task.
- Preserve canonical document: an authored rule source as an explicit, reviewable part of the task.
- Preserve task route: a bounded ordered reading plan as an explicit, reviewable part of the task.
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

- [Core Concepts](../concepts/index.md) — `AIXEM-CONCEPT-INDEX-001`
- [File Formats](../file-formats/index.md) — `AIXEM-FORMAT-INDEX-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
