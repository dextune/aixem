---
id: AIXEM-GOV-DOC-AUTHORING-001
title: Documentation Authoring and Lifecycle Guide
status: informative
version: '1.0'
language: en
domain: governance
kind: guide
summary: Provides a practical decision path for creating, extending, moving, deprecating, archiving, and deleting AIXEM documents.
authority:
- documentation-authoring-guidance
aliases:
- documentation authoring guide
- document placement guide
- document lifecycle guide
agent:
  priority: high
  estimated_tokens: 1511
  intents:
  - build-documentation
  - publish-release
depends_on:
- AIXEM-SPEC-DOC-GOVERNANCE-001
related:
- AIXEM-SPEC-METADATA-001
- AIXEM-GOV-RELEASE-001
- AIXEM-AGENT-ROUTES-001
navigation:
  group: governance
  order: 55
artifacts:
  owns: []
  consumes:
  - docs/_meta/repository-document-policy.yaml
  - planning/index.yaml
requirements: []
---

# Documentation Authoring and Lifecycle Guide

Provides a practical decision path for creating, extending, moving, deprecating, archiving, and deleting AIXEM documents.

> **Document ID:** `AIXEM-GOV-DOC-AUTHORING-001`  
> **Status:** Informative  
> **Version:** 1.0

## Start With the Document Role

Before editing or creating Markdown, identify what the reader needs:

| Need | Correct owner |
|---|---|
| Current technical truth | Existing canonical owner under `docs/`, or a justified new canonical document |
| Repository operating rules | `AGENTS.md`, `CONTRIBUTING.md`, or another approved root policy |
| Why and how a release was proposed | `planning/releases/<version>/` |
| What changed | concise `CHANGELOG.md` entry and `docs/releases/<version>.md` |
| What passed or failed | `validation/releases/<version>/` and machine evidence |
| How to execute a fixture | local `README.md` or `TASK.md` in a registered suite/case |
| Historical compatibility context | `legacy/` or the canonical path-migration registry |
| Generated navigation or report | generator input; never hand-edit the generated product |

## Prefer an Existing Owner

Add to an existing document when the proposed material has the same:

- authority;
- audience;
- lifecycle;
- retrieval intent;
- release and compatibility obligations.

Create a new document only when at least one of those boundaries is genuinely independent and the new file has a durable discovery path. Length alone is not a split criterion.

## Pre-Create Gate

Record answers to all eight questions before creating a file:

1. What repository document role will it have?
2. Which existing document was considered as the owner?
3. Why is a new file more precise than extending that owner?
4. What official index, navigation section, suite descriptor, or policy will expose it?
5. What is its lifecycle and who may change it later?
6. Does its path and filename satisfy the role rule?
7. Does it need a stable canonical ID, or is it noncanonical history/evidence?
8. Which validator proves it is classified and discoverable?

An unresolved answer means the file must not be created.

## Canonical Document Workflow

1. Resolve the owning task route before broad search.
2. Confirm that no current canonical document already owns the authority.
3. Assign a stable ID and controlled `domain` and `kind`.
4. Add exact navigation placement and relationships.
5. Define normative requirements only when release-gating behavior is intended.
6. Add validator, test, conformance mapping, and evidence for each requirement.
7. Keep current rules in semantic sections; never append a release patch block.
8. Keep the canonical footer as the final content.
9. Regenerate indexes, routes, task packets, reference products, site, inventory, and manifest.

## Plan Workflow

Place plans at:

```text
planning/releases/<version>/<purpose>.md
```

Register them in `planning/index.yaml` and link them from `planning/README.md`. Plans may be `proposed`, `active`, `completed`, `superseded`, or `abandoned`. A completed plan is historical intent and cannot override a later canonical rule or observed validation result.

## Validation Report Workflow

Place human-readable reports at:

```text
validation/releases/<version>/<purpose>.md
```

Link each report from that release's `README.md`. Keep machine-bound evidence at its existing contract path unless every schema, test, digest, and retained consumer is deliberately migrated.

A report should identify scope, command or validator, result, evidence paths, and any truth boundary. It should not restate technical specifications as a second source of truth.

## Move Workflow

For a noncanonical move:

1. update the role registry or lifecycle owner;
2. update current authored links and machine consumers;
3. preserve historical evidence references when they are provenance;
4. rerun the repository document audit.

For a canonical move, additionally:

1. preserve the document ID;
2. add an append-only record to `docs/_meta/path-migrations.yaml`;
3. update current links;
4. regenerate old-site-path redirects;
5. validate identity, old-path uniqueness, cycles, and redirect targets.

## Deprecate, Archive, or Delete

Deprecate when the information remains necessary for compatibility but is no longer current. Archive plans and evidence through their lifecycle owner, not by creating an unindexed `archive/` pile.

Delete only when:

- there is no current authority or evidence obligation;
- replacements and migration are documented;
- all current references are removed;
- historical provenance remains available where required;
- the repository audit reports no unknown path or orphan.

## Naming Examples

Good:

```text
docs/governance/documentation-authoring-guide.md
planning/releases/0.5.7/document-information-architecture-governance.md
validation/releases/0.5.7/implementation-matrix.md
validation/agent-evals-3/cases/L008/TASK.md
```

Reject:

```text
notes.md
FINAL-v2.md
PLAN-0.5.8-SOMETHING.md
validation/reports/report-new.md
docs/governance/misc.md
```

## Final Review Checklist

- The document has exactly one role.
- Its owner and authority do not conflict with another file.
- Its official discovery path resolves.
- Its lifecycle is explicit.
- Its filename follows policy.
- Current technical prose is version-neutral unless version behavior is itself the subject.
- Generated products were regenerated rather than hand-edited.
- Repository audit, canonical validation, tests, and release gates pass.

## Related Documents

- [Repository Document Governance Contract 1](../specifications/documentation/document-governance-contract.md) — `AIXEM-SPEC-DOC-GOVERNANCE-001`
- [Documentation Metadata Contract 1](../specifications/documentation/metadata-contract.md) — `AIXEM-SPEC-METADATA-001`
- [Release Process](release-process.md) — `AIXEM-GOV-RELEASE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
