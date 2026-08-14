---
id: AIXEM-SPEC-DOC-GOVERNANCE-001
title: Repository Document Governance Contract 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: contract
summary: Defines repository-wide roles, naming, lifecycle, discoverability, migration, and validation rules for every authored Markdown document.
authority:
- repository-document-governance
- documentation-information-architecture
aliases:
- document governance contract
- repository documentation policy
- documentation information architecture contract
agent:
  priority: critical
  estimated_tokens: 4249
  intents:
  - build-documentation
  - publish-release
depends_on:
- AIXEM-SPEC-DOCUMENT-001
- AIXEM-SPEC-METADATA-001
- AIXEM-SPEC-RELEASE-001
related:
- AIXEM-GOV-DOC-AUTHORING-001
- AIXEM-AGENT-ROUTES-001
- AIXEM-GOV-RELEASE-001
navigation:
  group: specifications
  order: 115
artifacts:
  owns:
  - docs/_meta/repository-document-policy.yaml
  - docs/_meta/path-migrations.yaml
  - docs/_meta/schema/repository-document-policy.schema.json
  - docs/_meta/schema/path-migrations.schema.json
  - docs/_meta/generated/repository-document-inventory.json
  - docs/_meta/generated/path-migration-index.json
  - docs/_meta/generated/document-relationship-audit.json
  consumes:
  - planning/index.yaml
requirements:
- id: AIXEM-REQ-DOC-GOV-0001
  title: Exact repository document role
  level: MUST
  statement: Every authored Markdown file MUST resolve to exactly one declared repository document role.
  validator: docs.repository_inventory
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_every_markdown_has_exactly_one_role
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0001.json
- id: AIXEM-REQ-DOC-GOV-0002
  title: Root hygiene and reserved names
  level: MUST
  statement: Root Markdown and reserved special filenames MUST be limited to the explicit policy allowlists.
  validator: docs.document_naming
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_root_hygiene_and_reserved_names
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0002.json
- id: AIXEM-REQ-DOC-GOV-0003
  title: Role-aware discoverability
  level: MUST
  statement: Every human-authored document MUST be discoverable through the official mechanism declared for its role.
  validator: docs.document_discoverability
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_role_aware_discoverability_has_no_orphans
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0003.json
- id: AIXEM-REQ-DOC-GOV-0004
  title: Canonical current-state structure
  level: MUST
  statement: Canonical documents MUST end at the canonical footer and MUST NOT contain release patch append markers.
  validator: docs.canonical_structure
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_canonical_structure_has_terminal_footer_and_no_patch_blocks
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0004.json
- id: AIXEM-REQ-DOC-GOV-0005
  title: Stable identity across path migration
  level: MUST
  statement: A canonical path migration MUST preserve document identity and produce a validated prior-path redirect.
  validator: docs.path_migrations
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_path_migrations_preserve_identity_and_redirects
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0005.json
- id: AIXEM-REQ-DOC-GOV-0006
  title: Controlled metadata vocabulary
  level: MUST
  statement: Canonical domain and kind values MUST use the controlled metadata vocabulary and size estimates MUST be machine checked.
  validator: docs.metadata_vocabulary
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_metadata_vocabularies_and_token_estimates
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0006.json
- id: AIXEM-REQ-DOC-GOV-0007
  title: Deterministic repository inventory
  level: MUST
  statement: Identical authored inputs MUST produce a byte-identical repository document inventory and path migration index.
  validator: docs.repository_inventory
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_repository_inventory_is_deterministic
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0007.json
- id: AIXEM-REQ-DOC-GOV-0008
  title: Version-scoped plan and report lifecycle
  level: MUST
  statement: Implementation plans and human validation reports MUST be version scoped and registered by their lifecycle owner.
  validator: docs.document_lifecycle
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_planning_and_validation_lifecycles
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0008.json
- id: AIXEM-REQ-DOC-GOV-0009
  title: Agent document creation gate
  level: MUST
  statement: Repository agent instructions MUST require role, owner, discovery, lifecycle, naming, and validation decisions before creating a document.
  validator: docs.agent_document_rules
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_agents_document_creation_gate
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0009.json
- id: AIXEM-REQ-DOC-GOV-0010
  title: Unknown Markdown fails closed
  level: MUST
  statement: A Markdown path that matches no declared role MUST fail repository documentation validation.
  validator: docs.repository_inventory
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_unknown_markdown_fails_closed
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0010.json
- id: AIXEM-REQ-DOC-GOV-0011
  title: Root reference-chain integrity
  level: MUST
  statement: Every approved root Markdown link MUST resolve safely, the root reference map MUST link every policy-required repository area and build control, and every human-authored Markdown document MUST be reachable from the primary root entrypoint.
  validator: docs.root_reference_chain
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_root_reference_chain_reaches_all_human_documents
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0011.json
- id: AIXEM-REQ-DOC-GOV-0012
  title: Complete category-index coverage
  level: MUST
  statement: Every canonical category index MUST link every document registered in its navigation section.
  validator: docs.section_index_coverage
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_section_indexes_cover_navigation_members
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0012.json
- id: AIXEM-REQ-DOC-GOV-0013
  title: Current-release coherence
  level: MUST
  statement: Operational root entrypoints, current release navigation, planning, validation, route paths, and release metadata MUST agree with VERSION.
  validator: docs.release_coherence
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_current_release_pointers_are_coherent
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0013.json
- id: AIXEM-REQ-DOC-GOV-0014
  title: Unambiguous normative authority scope
  level: MUST
  statement: A normative authority scope MUST have exactly one owner unless the repository document policy explicitly declares that scope shareable.
  validator: docs.authority_scope
  verification_mode: automated
  test: tests/docs/test_document_governance.py::DocumentGovernanceTests.test_normative_authority_scopes_are_unambiguous
  evidence: validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0014.json
---
# Repository Document Governance Contract 1

Defines repository-wide roles, naming, lifecycle, discoverability, migration, and validation rules for every authored Markdown document.

> **Document ID:** `AIXEM-SPEC-DOC-GOVERNANCE-001`  
> **Status:** Normative  
> **Version:** 1.0

## 1. Authority Boundary

`docs/` remains the only canonical authored technical-documentation root. Repository entrypoints, implementation plans, release validation reports, evidence narratives, fixture tasks, and legacy explanations are intentionally noncanonical. Moving a file into `docs/` does not make its claims authoritative unless it also receives canonical identity, metadata, navigation, requirement, and validation treatment.

The policy distinguishes four questions that must not be conflated:

1. **What is true now?** Canonical documentation owns current technical truth.
2. **Why was a change proposed?** A version-scoped implementation plan owns intent and rationale.
3. **What changed in a release?** `CHANGELOG.md` and `docs/releases/<version>.md` own release history.
4. **What was actually verified?** `validation/releases/<version>/` and machine evidence own observed results.

## 2. Repository Document Roles

Every Markdown file is classified by `docs/_meta/repository-document-policy.yaml`. Classification is fail-closed and exact: zero matches and multiple matches are both errors.

The supported roles are:

| Role | Authority and lifecycle |
|---|---|
| Repository entrypoint or policy | Permanent, conventional root guidance; never a substitute for canonical technical rules. |
| Canonical documentation | Current technical authority under `docs/`, with stable ID and navigation registration. |
| Implementation plan | Version-scoped historical intent under `planning/releases/`. |
| Validation release index/report | Version-scoped immutable human evidence under `validation/releases/`. |
| Machine-bound evidence narrative | Retained under `validation/evidence/` because paths may be schema-, test-, or digest-bound. |
| Evaluation or corpus instruction | Local `README.md`, scoring guide, result summary, or `TASK.md` owned by a registered suite/case. |
| Example-local instruction | Local guidance owned by a self-contained example directory. |
| Legacy explanation | Historical compatibility context under `legacy/`. |
| Generated documentation product | A deterministic pointer or inventory generated from an authoritative input. |

## 3. Naming and Placement

The default filename is lowercase kebab case:

```text
[a-z0-9]+(?:-[a-z0-9]+)*.md
```

The only reserved special names are `README.md`, `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `NOTICE.md`, `START_HERE.md`, `TASK.md`, and canonical `index.md`. A special name is valid only in the role and path declared by policy.

Versions belong in directory context for plans and validation reports:

```text
planning/releases/0.5.7/document-information-architecture-governance.md
validation/releases/0.5.7/implementation-matrix.md
```

Canonical release notes intentionally use `docs/releases/0.5.7.md` because the filename is the series identity.

## 4. Discoverability and Orphan Semantics

A document is orphaned when it lacks the official discovery mechanism for its role, not merely when it has no Markdown hyperlink.

- canonical documents are discovered through `docs/_meta/navigation.yaml`;
- root entrypoints are discovered through the root whitelist;
- plans are registered in `planning/index.yaml` and linked from `planning/README.md`;
- human validation reports are linked from their release `README.md`;
- suite and corpus instructions are owned by their local registered directory;
- evaluation `TASK.md` files are owned by the case descriptor in the same case directory;
- machine-bound evidence narratives are owned by evidence policy and machine references;
- generated documentation products are owned by their generator and generated manifest.

The generated inventory records both inbound Markdown references and textual machine references, but neither count alone defines authority.

## 5. Canonical Current-State Discipline

Canonical documents describe the active system directly. Release patch comments such as `AIXEM-0.5.x-...:START`, `:END`, `:begin`, or `:end` are prohibited. Valid rules introduced by an earlier release must be integrated into the semantic section that owns them.

The standard canonical footer is terminal:

```text
---

<canonical-footer-sentence>
```

No heading, requirement, example, or comment may follow it.

## 6. Canonical Path Migration

A canonical move preserves the stable document ID and records the old and new paths in `docs/_meta/path-migrations.yaml`. Migration records are append-only after release. Validation rejects missing targets, reused old paths, identity mismatch, cycles, duplicate sources, or a migration whose old path remains an active canonical document.

The compiler publishes `path-migration-index.json`, annotates the current document-index entry with previous paths, and emits an offline HTML redirect at the old site path. Internal authored links must use the current path; historical evidence may retain the old path as provenance.

## 7. Metadata Vocabulary and Size Estimates

`domain` and `kind` are controlled enumerations in the canonical metadata schema. A new value requires an information-architecture change rather than an ad hoc string.

The authored `agent.estimated_tokens` value is checked against a deterministic body-size estimate. Byte limits remain the hard route budget. The estimate exists only to help bounded retrieval planning and must not be treated as a tokenizer-specific guarantee.

## 8. Lifecycle Operations

### Create

Create a document only after identifying its role, unique owner, audience, lifecycle, official discovery mechanism, filename, and validator. Extend the existing owner when authority, audience, lifecycle, and retrieval intent are the same.

### Move

Update every current authored consumer. Canonical moves additionally require stable-ID migration records and generated redirects. Historical evidence is not rewritten merely to make paths look current.

### Deprecate or supersede

Keep the replacement and lifecycle visible. Canonical deprecation uses canonical metadata; plans use `planning/index.yaml`; validation reports remain immutable evidence.

### Delete

Delete only after references, replacement, ownership, evidence retention, and release-history obligations are resolved. A deletion is a reviewed lifecycle event, not cleanup by intuition.

## 9. Generated Inventory

`docs/_meta/generated/repository-document-inventory.json` contains, for every Markdown file:

```text
path, role, lifecycle, canonicalDocumentId, release, sourceOwner,
discoverabilityOwner, inboundDocumentRefs, machineRefs, status, bytes, digest
```

The inventory is derived and non-authoritative. `docs/_meta/repository-document-policy.yaml`, canonical metadata, planning lifecycle data, release indexes, and registered fixture structure remain the authored inputs.

## 10. Root Reference and Relationship Closure

`README.md` is the primary repository entrypoint. `REFERENCE.md` owns the stable root category, artifact, validation, and history map. `AGENTS.md` remains a bounded operating contract and links to that map instead of duplicating category content.

The repository relationship audit must prove:

1. every approved root-local link and Markdown anchor resolves without escaping the repository;
2. `REFERENCE.md` links every policy-required repository area and root build control;
3. every human-authored Markdown file is reachable from `README.md` through explicit links;
4. every category index links every navigation member registered beneath it;
5. current operational pointers agree with `VERSION`;
6. active routes contain no stale release-scoped evidence path;
7. normative authority scopes have one owner unless explicitly declared shareable.

The generated audit is evidence, not technical authority. Its inputs remain the root documents, canonical metadata, navigation, route definitions, planning registry, release indexes, repository-document policy, and release metadata.

## Normative Requirements

<a id="AIXEM-REQ-DOC-GOV-0001"></a>

### AIXEM-REQ-DOC-GOV-0001 — Exact repository document role

**MUST.** Every authored Markdown file MUST resolve to exactly one declared repository document role.

- Verification mode: `automated`
- Validator: `docs.repository_inventory`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_every_markdown_has_exactly_one_role`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0001.json`

<a id="AIXEM-REQ-DOC-GOV-0002"></a>

### AIXEM-REQ-DOC-GOV-0002 — Root hygiene and reserved names

**MUST.** Root Markdown and reserved special filenames MUST be limited to the explicit policy allowlists.

- Verification mode: `automated`
- Validator: `docs.document_naming`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_root_hygiene_and_reserved_names`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0002.json`

<a id="AIXEM-REQ-DOC-GOV-0003"></a>

### AIXEM-REQ-DOC-GOV-0003 — Role-aware discoverability

**MUST.** Every human-authored document MUST be discoverable through the official mechanism declared for its role.

- Verification mode: `automated`
- Validator: `docs.document_discoverability`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_role_aware_discoverability_has_no_orphans`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0003.json`

<a id="AIXEM-REQ-DOC-GOV-0004"></a>

### AIXEM-REQ-DOC-GOV-0004 — Canonical current-state structure

**MUST.** Canonical documents MUST end at the canonical footer and MUST NOT contain release patch append markers.

- Verification mode: `automated`
- Validator: `docs.canonical_structure`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_canonical_structure_has_terminal_footer_and_no_patch_blocks`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0004.json`

<a id="AIXEM-REQ-DOC-GOV-0005"></a>

### AIXEM-REQ-DOC-GOV-0005 — Stable identity across path migration

**MUST.** A canonical path migration MUST preserve document identity and produce a validated prior-path redirect.

- Verification mode: `automated`
- Validator: `docs.path_migrations`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_path_migrations_preserve_identity_and_redirects`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0005.json`

<a id="AIXEM-REQ-DOC-GOV-0006"></a>

### AIXEM-REQ-DOC-GOV-0006 — Controlled metadata vocabulary

**MUST.** Canonical domain and kind values MUST use the controlled metadata vocabulary and size estimates MUST be machine checked.

- Verification mode: `automated`
- Validator: `docs.metadata_vocabulary`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_metadata_vocabularies_and_token_estimates`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0006.json`

<a id="AIXEM-REQ-DOC-GOV-0007"></a>

### AIXEM-REQ-DOC-GOV-0007 — Deterministic repository inventory

**MUST.** Identical authored inputs MUST produce a byte-identical repository document inventory and path migration index.

- Verification mode: `automated`
- Validator: `docs.repository_inventory`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_repository_inventory_is_deterministic`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0007.json`

<a id="AIXEM-REQ-DOC-GOV-0008"></a>

### AIXEM-REQ-DOC-GOV-0008 — Version-scoped plan and report lifecycle

**MUST.** Implementation plans and human validation reports MUST be version scoped and registered by their lifecycle owner.

- Verification mode: `automated`
- Validator: `docs.document_lifecycle`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_planning_and_validation_lifecycles`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0008.json`

<a id="AIXEM-REQ-DOC-GOV-0009"></a>

### AIXEM-REQ-DOC-GOV-0009 — Agent document creation gate

**MUST.** Repository agent instructions MUST require role, owner, discovery, lifecycle, naming, and validation decisions before creating a document.

- Verification mode: `automated`
- Validator: `docs.agent_document_rules`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_agents_document_creation_gate`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0009.json`

<a id="AIXEM-REQ-DOC-GOV-0010"></a>

### AIXEM-REQ-DOC-GOV-0010 — Unknown Markdown fails closed

**MUST.** A Markdown path that matches no declared role MUST fail repository documentation validation.

- Verification mode: `automated`
- Validator: `docs.repository_inventory`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_unknown_markdown_fails_closed`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0010.json`

<a id="AIXEM-REQ-DOC-GOV-0011"></a>

### AIXEM-REQ-DOC-GOV-0011 — Root reference-chain integrity

**MUST.** Every approved root Markdown link MUST resolve safely, the root reference map MUST link every policy-required repository area and build control, and every human-authored Markdown document MUST be reachable from the primary root entrypoint.

- Verification mode: `automated`
- Validator: `docs.root_reference_chain`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_root_reference_chain_reaches_all_human_documents`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0011.json`

<a id="AIXEM-REQ-DOC-GOV-0012"></a>

### AIXEM-REQ-DOC-GOV-0012 — Complete category-index coverage

**MUST.** Every canonical category index MUST link every document registered in its navigation section.

- Verification mode: `automated`
- Validator: `docs.section_index_coverage`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_section_indexes_cover_navigation_members`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0012.json`

<a id="AIXEM-REQ-DOC-GOV-0013"></a>

### AIXEM-REQ-DOC-GOV-0013 — Current-release coherence

**MUST.** Operational root entrypoints, current release navigation, planning, validation, route paths, and release metadata MUST agree with VERSION.

- Verification mode: `automated`
- Validator: `docs.release_coherence`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_current_release_pointers_are_coherent`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0013.json`

<a id="AIXEM-REQ-DOC-GOV-0014"></a>

### AIXEM-REQ-DOC-GOV-0014 — Unambiguous normative authority scope

**MUST.** A normative authority scope MUST have exactly one owner unless the repository document policy explicitly declares that scope shareable.

- Verification mode: `automated`
- Validator: `docs.authority_scope`
- Test reference: `tests/docs/test_document_governance.py::DocumentGovernanceTests.test_normative_authority_scopes_are_unambiguous`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOC-GOV-0014.json`

## 11. Validation and Release Closure

Repository documentation validation must cover:

1. exact role classification;
2. root whitelist and naming rules;
3. canonical metadata, links, navigation, requirements, and dependencies;
4. role-aware discoverability and zero orphans;
5. canonical footer and patch-marker prohibition;
6. path-migration identity and redirect integrity;
7. controlled metadata vocabulary and size-estimate bounds;
8. deterministic inventory and generated products;
9. current-release consistency in operational entrypoints;
10. root-link safety and complete root reachability;
11. category-index coverage;
12. current-release coherence;
13. normative authority-scope ownership;
14. release manifest and archive closure.

A documentation-only release must still prove that protected circuit formats, renderer output, Viewer output, and agent execution contracts did not change unintentionally.

## Related Documents

- [Canonical Document Model](../core/document-model.md) — `AIXEM-SPEC-DOCUMENT-001`
- [Documentation Metadata Contract 1](metadata-contract.md) — `AIXEM-SPEC-METADATA-001`
- [Documentation Authoring and Lifecycle Guide](../../governance/documentation-authoring-guide.md) — `AIXEM-GOV-DOC-AUTHORING-001`
- [Release Integrity Contract](release-integrity.md) — `AIXEM-SPEC-RELEASE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
