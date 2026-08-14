# AIXEM 0.5.7 — Document Information Architecture and Governance Plan

**Proposed release:** 0.5.7  
**Baseline:** AIXEM 0.5.6 (2026-08-12)  
**Scope:** repository documentation naming, hierarchy, lifecycle, discoverability, governance, and agent-facing documentation discipline  
**Circuit-format impact:** none intended  
**Renderer / Viewer impact:** none intended  
**Primary goal:** make every authored document intentionally placed, uniquely classifiable, discoverable through an official path, and governed by rules that prevent future documentation sprawl.

---

## 1. Executive Summary

AIXEM 0.5.6 already has a strong canonical documentation system under `docs/`: stable document IDs, front matter, navigation coverage, dependency relationships, generated indexes, route-first retrieval, conformance mapping, and deterministic publication all validate successfully.

The principal weakness is now **outside and around that canonical core**.

Historical plans remain at repository root, release/status information is repeated across several surfaces, validation reports have accumulated in flat or generation-oriented directories, and release-specific amendments have often been appended to canonical documents instead of being integrated into their semantic structure. `AGENTS.md` has followed the same append-by-release pattern and has become a historical ledger as well as an operational instruction file.

0.5.7 should therefore **not redesign the technical documentation model from scratch**. It should preserve the good 0.5.x canonical model and add a repository-wide information architecture above it:

1. classify every Markdown document by role and lifecycle;
2. reduce the repository root to a deliberate, small set of entrypoint files;
3. move historical plans and human-readable verification reports into version-scoped homes;
4. normalize canonical-document filenames where ambiguity materially harms retrieval;
5. integrate patch-style appended content into the proper document sections;
6. replace release-accumulating `AGENTS.md` content with stable, version-neutral rules plus compact current-release pointers;
7. define explicit rules for creating, naming, moving, deprecating, archiving, and deleting documents;
8. add automated repository-wide documentation inventory, orphan detection, naming checks, lifecycle checks, and path-migration support;
9. keep stable IDs and evidence truth intact while paths are normalized;
10. verify the migration three times before release.

The result should make AIXEM easier for both humans and AI agents to navigate while **reducing**, rather than increasing, the amount of documentation that must be read for ordinary work.

---

## 2. Baseline Audit of AIXEM 0.5.6

### 2.1 Repository-wide Markdown inventory

The 0.5.6 package contains **224 Markdown files**.

| Area | Markdown files | Current role |
|---|---:|---|
| `docs/` | 139 | canonical authored documentation |
| `validation/` | 58 | reports, reviews, evaluation tasks, evidence narratives |
| `examples/` | 10 | example-local instructions |
| repository root | 16 | entrypoints, governance files, release/status files, historical plans |
| `legacy/` | 1 | legacy-area explanation |

The canonical `docs/` layer is healthy:

- 139 / 139 documents contain valid canonical metadata;
- 139 / 139 are present exactly once in `docs/_meta/navigation.yaml`;
- 95 are normative and 44 informative;
- document IDs are unique;
- document titles are unique;
- internal canonical Markdown links are valid;
- current documentation validation reports no errors or warnings.

This strong baseline MUST be preserved.

### 2.2 Root-directory accumulation

The repository root currently contains:

- `README.md`
- `START_HERE.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `RELEASE_NOTES.md`
- `IMPLEMENTATION_STATUS.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `NOTICE.md`
- seven historical/current `PLAN-*.md` files

The seven plan files alone occupy roughly **322 KiB** and more than **10,000 lines** at repository root.

The root therefore mixes four different lifecycles:

1. permanent repository entrypoints;
2. current-release summaries;
3. historical implementation plans;
4. current operational agent instructions.

These should not share one flat namespace.

### 2.3 Release/status information has multiple owners

0.5.6 release state is represented in multiple places:

- `CHANGELOG.md`
- `RELEASE_NOTES.md`
- `IMPLEMENTATION_STATUS.md`
- `docs/releases/0.5.6.md`
- `validation/final-validation-report.md`
- `validation/reports/plan-implementation-matrix-0.5.6.md`
- release JSON metadata/evidence

Not all of these are duplicates in purpose, but the repository does not currently declare which surface owns which statement.

This creates a future drift risk. A release note, implementation state, validation result, and changelog entry should have clearly separated responsibilities.

### 2.4 `AGENTS.md` has become release-accumulative

`AGENTS.md` is approximately **574 lines / 23 KiB** in 0.5.6.

Its lower half contains dedicated historical sections for:

- 0.5.1 authoring and drawing;
- 0.5.2 symbol expressiveness;
- 0.5.3 hierarchical composition;
- 0.5.4 Reference Viewer;
- 0.5.5 closed-loop authoring;
- 0.5.6 live-agent cold-start operation.

This causes two problems:

1. operational instructions become progressively larger every release;
2. historical state can remain stale inside a file that agents treat as authoritative preflight guidance.

A concrete 0.5.6 example exists: the `Current implementation state` section still states that **0.5.4 is the active Reference Viewer normalization release**, even though the package itself is 0.5.6.

`AGENTS.md` should be an **operational constitution**, not a changelog.

### 2.5 Patch-by-append debt exists inside canonical docs

At least **31 canonical documents** contain material after the standard canonical-document footer. At least **28 canonical documents** contain explicit release patch markers such as:

- `AIXEM-0.5.1-AUTHORING-EXPANSION`
- `aixem-0.5.5-agent-authoring`
- `aixem-0.5.6-live-agent`

Affected areas include agent guidance, concepts, conformance, file formats, routing, schematic guidance, schemas, symbol documentation, and getting-started material.

The appended material is often valid and important. The defect is **structural**, not semantic: current rules are being added as release patches instead of being merged into the document's normal information hierarchy.

If repeated, this produces documents that read like a chronological patch log rather than a current authoritative reference.

### 2.6 Canonical metadata vocabulary is broader than necessary

The 139 canonical documents currently use:

- **15 `domain` values**;
- **27 `kind` values**.

`domain` and `kind` are currently free-form strings in the metadata schema. The 27 `kind` values include closely related terms such as:

- `guide`
- `architecture-guide`
- `specification-guide`
- `contract-guide`
- `validation-guide`
- `tutorial`
- `workflow`
- `process`
- `policy`
- `execution-policy`

The metadata is valid, but the vocabulary can drift indefinitely because the schema does not constrain it.

### 2.7 Filename ambiguity exists in a few canonical areas

Most canonical filenames are already lower-kebab-case and appropriately scoped by directory.

The notable same-basename collisions are:

- `docs/conformance/compatibility.md`
- `docs/governance/compatibility.md`
- `docs/schematic/authoring-cookbook.md`
- `docs/symbols/authoring-cookbook.md`

These are not inherently incorrect because their directories provide context. However, AI tools, grep output, editor tabs, and copied references often lose parent-directory context. Canonical filename uniqueness should therefore be preferred where a rename is low-risk.

`index.md` is an intentional exception. `README.md` and `TASK.md` are also legitimate special names in self-contained noncanonical directories.

### 2.8 Noncanonical Markdown is outside the strong canonical validator

`tools/docs/aixem_docs.py::load_documents()` loads canonical Markdown under `docs/` only.

As a consequence, the strong checks for:

- metadata;
- canonical links;
- navigation coverage;
- dependency integrity;
- document identity;

correctly apply to canonical docs but do not classify or govern repository-root plans, validation reports, fixture READMEs, or legacy guidance.

A raw link-graph audit finds **81 noncanonical Markdown files with no inbound Markdown link**. This number MUST NOT be interpreted as 81 deletable files: many are intentionally terminal fixture `TASK.md` files or machine-referenced evidence. It does prove that **Markdown-link reachability alone is insufficient** and that the repository lacks a formal repository-wide document-role registry.

### 2.9 Path-move policy is declared but not implemented as a general facility

Current agent guidance states that when a canonical document path moves, identity and migration/redirect metadata should be preserved.

However, the current canonical metadata schema has no general `previous_paths`, `moved_from`, or redirect field, and the documentation builder does not expose a general current-version canonical path-redirect registry.

Before performing broad canonical renames, 0.5.7 must implement an explicit path-migration mechanism.

### 2.10 Declared token estimates can become stale after appended edits

Several expanded canonical documents have grown substantially while retaining relatively small manually authored `agent.estimated_tokens` values. This is especially visible in files that received large 0.5.1 append blocks.

The route budget itself is byte-bounded, so this is not currently a release failure. It is nevertheless a metadata-maintenance smell. A derived estimate is safer than a manually maintained size estimate.

---

## 3. Design Principles for 0.5.7

### P1 — Preserve one canonical documentation authority

`docs/` remains the **only canonical authored technical-documentation root**.

Do not move validation evidence, implementation plans, fixture tasks, or repository contribution files into `docs/` merely to make the tree visually uniform.

### P2 — Every Markdown file must have exactly one role

A document must be classifiable as one of:

- repository entrypoint / policy;
- canonical documentation;
- implementation plan;
- release history;
- validation report / review;
- machine-bound evidence narrative;
- example-local instruction;
- evaluation task;
- legacy/archive explanation;
- generated documentation product.

Unknown-role Markdown is a validation failure.

### P3 — Semantic ownership beats visual tidiness

A move or rename must never create a second source of truth or weaken evidence traceability.

### P4 — Current docs describe the current system

Release-specific history belongs in release notes, plans, changelog entries, and validation records.

Canonical contracts and guides should describe the active rule directly unless version-specific behavior is itself part of the contract.

### P5 — Stable IDs survive path changes

Renaming or moving a canonical document MUST preserve its `id`.

### P6 — Generated navigation is derived; authored structure is intentional

Do not manually create parallel indexes that compete with generated indexes. Human entrypoints may summarize, but generated products remain derived from authoritative metadata.

### P7 — Agent instructions must stay bounded

`AGENTS.md` should contain only high-frequency repository-wide rules and routing instructions. Domain-specific details should be loaded through task routes.

### P8 — A document should exist only when it has a distinct purpose

Before creating a new document, extend an existing owner when the proposed content has the same authority, audience, lifecycle, and retrieval intent.

### P9 — Deletion is a lifecycle operation

A document is deleted only after references, ownership, replacement, evidence retention, and release-history obligations are resolved.

### P10 — Documentation architecture is testable

Naming, placement, lifecycle, reachability, path migration, metadata vocabulary, and root hygiene must be machine-validated.

---

## 4. Proposed Repository Document Taxonomy

### 4.1 Repository root

The repository root should contain only conventional, high-value entrypoints and non-Markdown build files.

Target Markdown whitelist:

```text
/
├── AGENTS.md
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── NOTICE.md
```

`START_HERE.md` should normally be absorbed into `README.md` or replaced by a short generated/maintained pointer only if an external evaluation workflow demonstrably requires a dedicated file.

`RELEASE_NOTES.md` should not independently restate the current release when `docs/releases/<version>.md` is the canonical release narrative.

`IMPLEMENTATION_STATUS.md` should not remain a mutable root-level second owner of release validation state.

Historical `PLAN-*.md` files should leave the root.

### 4.2 Canonical documentation

Keep:

```text
docs/
├── index.md
├── _meta/
├── agent/
├── architecture/
├── authoring/
├── concepts/
├── conformance/
├── examples/
├── file-formats/
├── getting-started/
├── governance/
├── releases/
├── routing/
├── schematic/
├── specifications/
└── symbols/
```

Do not reorganize these domains merely for aesthetic symmetry. Physical movement should be justified by retrieval or authority problems.

### 4.3 Implementation plans

Create a dedicated noncanonical planning root:

```text
planning/
├── README.md
└── releases/
    ├── 0.5.0/
    │   └── documentation-platform.md
    ├── 0.5.1/
    │   └── agent-authoring-drawing.md
    ├── 0.5.2/
    │   └── symbol-expressiveness-conformance.md
    ├── 0.5.3/
    │   └── hierarchical-multisheet-composition.md
    ├── 0.5.4/
    │   └── reference-viewer-contract.md
    ├── 0.5.5/
    │   └── agent-authoring-closed-loop.md
    ├── 0.5.6/
    │   └── live-agent-cold-start-authoring.md
    └── 0.5.7/
        └── document-information-architecture-governance.md
```

Rules:

- plans are historical design/implementation intent, not current normative authority;
- completed plans become read-only historical records except for explicit errata metadata;
- plan filenames do not repeat `PLAN-` or the version because directory context already supplies lifecycle and version;
- a planning index records status: `proposed`, `active`, `completed`, `superseded`, or `abandoned`;
- canonical docs may cite plans for provenance, but implementation agents must not treat plans as higher authority than current normative docs.

### 4.4 Validation documentation

Human-readable validation material should be grouped by release and purpose, while machine-bound evidence paths remain stable unless a deliberate evidence migration is implemented.

Proposed shape:

```text
validation/
├── README.md
├── releases/
│   ├── 0.5.2/
│   │   ├── implementation-matrix.md
│   │   ├── symbol-expressiveness.md
│   │   ├── static-2d-block.md
│   │   └── multi-unit-capability.md
│   ├── 0.5.3/
│   │   ├── implementation-matrix.md
│   │   └── verification/
│   ├── 0.5.4/
│   │   ├── implementation-matrix.md
│   │   └── verification/
│   ├── 0.5.5/
│   │   ├── implementation-matrix.md
│   │   └── verification/
│   └── 0.5.6/
│       ├── implementation-matrix.md
│       ├── final-validation.md
│       └── verification/
├── evidence/
├── evaluations/
├── corpus/
└── generated-or-machine-results/   # only if needed; avoid gratuitous movement
```

The exact physical migration of existing machine evidence must be conservative. Paths embedded in requirement metadata, tests, release manifests, or retained evidence should remain unchanged unless all consumers and digests are migrated together.

### 4.5 Evaluation suites

Normalize generation-style names such as:

```text
validation/agent-evals/
validation/agent-evals-2/
validation/agent-evals-3/
```

into a semantically explicit hierarchy only if references can be migrated safely, for example:

```text
validation/evaluations/agent-authoring/v1/
validation/evaluations/agent-authoring/v2/
validation/evaluations/live-cold-start/v1/
```

Do not perform this rename merely for cosmetic consistency. First calculate reference count, schema bindings, test paths, release metadata dependencies, and archived-evidence expectations.

### 4.6 Examples and fixtures

Keep local `README.md` and `TASK.md` names where the directory is a self-contained unit.

Examples:

```text
examples/authoring/03-multi-pin-ic/README.md
validation/.../cases/L003/TASK.md
```

These are valid special names because the parent directory is the identity boundary.

---

## 5. Naming Rules

### 5.1 Default filename rule

All newly authored Markdown files except explicit special files MUST use:

```text
lowercase-kebab-case.md
```

Allowed characters:

```text
[a-z0-9-]
```

No spaces, underscores, mixed case, timestamps, or arbitrary sequence suffixes.

### 5.2 Reserved special filenames

Allowed only for their conventional roles:

- `README.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `NOTICE.md`
- `TASK.md`
- `index.md`

A new uppercase special filename requires a governance change, not ad hoc creation.

### 5.3 Version placement

Prefer version in the **directory**, not repeated in every filename:

Good:

```text
planning/releases/0.5.6/live-agent-cold-start-authoring.md
validation/releases/0.5.6/implementation-matrix.md
```

Avoid:

```text
PLAN-0.5.6-LIVE-AGENT-COLD-START-AUTHORING.md
validation/reports/plan-implementation-matrix-0.5.6.md
```

Canonical release notes remain the intentional exception:

```text
docs/releases/0.5.6.md
```

because the filename itself is the release identity in the release-note series.

### 5.4 Canonical basename uniqueness

For canonical docs, non-`index.md` basenames SHOULD be globally unique when practical.

Proposed low-risk ambiguity cleanup candidates:

```text
docs/governance/compatibility.md
    -> docs/governance/compatibility-policy.md

docs/conformance/compatibility.md
    -> docs/conformance/compatibility-conformance.md

docs/symbols/authoring-cookbook.md
    -> docs/symbols/symbol-authoring-cookbook.md

docs/schematic/authoring-cookbook.md
    -> docs/schematic/schematic-authoring-cookbook.md
```

These renames MUST preserve document IDs and MUST be preceded by path-migration support.

### 5.5 Names must express purpose, not implementation chronology

Avoid generic filenames such as:

- `notes.md`
- `misc.md`
- `new.md`
- `final.md`
- `final2.md`
- `temp.md`
- `pass-01.md` outside an explicitly versioned verification directory
- `report.md` when parent context does not uniquely identify the report

### 5.6 Document title and filename alignment

The filename does not need to duplicate the full title, but it must identify the same topic without relying on undocumented abbreviations.

---

## 6. Canonical Document Content Rules

### 6.1 No release-patch append blocks in current canonical docs

Current canonical documentation MUST NOT accumulate sections purely through markers such as:

```text
<!-- AIXEM-0.5.x-...:START -->
...
<!-- ...:END -->
```

During 0.5.7, valid content inside existing blocks must be integrated into the natural sections of each document.

Version history belongs in:

- `docs/releases/`;
- `CHANGELOG.md`;
- `planning/releases/`;
- `validation/releases/`.

### 6.2 The canonical footer is terminal

If the standard canonical footer is retained, it MUST be the final authored content in the document.

No headings, requirements, examples, or patch blocks may appear after it.

### 6.3 One rule, one owner

Normative statements MUST have one canonical owner. Other docs link to that requirement or explain it informatively rather than restating a competing MUST.

### 6.4 Separate current behavior from provenance

A current specification says what AIXEM does now.

A release note says what changed.

A plan says why/how a change was intended.

A validation report says what was actually verified.

These four roles must not be merged.

### 6.5 Split only on real authority/retrieval boundaries

Do not split a document merely because it is long.

Split when at least one condition is true:

- it owns multiple independent authority scopes;
- agents routinely need only one independent half;
- requirements form clearly separable contracts;
- the document has become a chronological collection of unrelated extensions;
- a split measurably improves route budgets or retrieval precision.

### 6.6 Do not create thin documents without a navigation purpose

A short landing/index document is valid when it is an intentional navigation node. A standalone content document with only a few sentences should normally be merged into its owner.

---

## 7. Metadata Governance

### 7.1 Constrain `domain`

Add an explicit allowed domain vocabulary to the metadata schema.

A new domain requires:

- an information-architecture justification;
- navigation integration;
- an owner;
- at least one durable content category, not a one-off file.

Existing intentional virtual domains such as `authoring` or `documentation` may remain if their landing-page function is documented.

### 7.2 Normalize `kind`

Reduce the current 27-value free-form vocabulary to a controlled set such as:

```text
index
specification
contract
profile
policy
reference
guide
cookbook
concept
architecture
adr
conformance
release-note
example
```

Map legacy variants deliberately. Example mappings:

```text
architecture-guide    -> architecture or guide
specification-guide   -> guide
contract-guide        -> guide
validation-guide      -> guide
execution-policy      -> policy
tutorial              -> guide
workflow              -> guide or policy, based on authority
process               -> policy or guide, based on authority
```

Do not bulk-map by string alone; review each document's semantic role.

### 7.3 Derive size estimates

Make `agent.estimated_tokens` a derived or machine-checked value rather than an indefinitely manual estimate.

Preferred approach:

1. keep byte count as the hard retrieval-budget metric;
2. calculate a deterministic approximate token count during compilation;
3. publish the calculated value in generated indexes/task packets;
4. either remove authored `estimated_tokens` in a schema revision or validate it against a bounded deterministic estimate.

### 7.4 Add lifecycle/path metadata outside canonical authority

Do not overload canonical front matter with plan/evidence lifecycle fields.

Introduce a lightweight repository-document policy/registry for noncanonical document classes.

---

## 8. Repository-Wide Document Registry and Inventory

### 8.1 Authored policy

Add an authored policy file, for example:

```text
docs/_meta/repository-document-policy.yaml
```

It defines:

- Markdown roots;
- role by path pattern;
- allowed special filenames;
- naming regexes;
- lifecycle requirements;
- discoverability rules;
- immutable evidence exceptions;
- root whitelist;
- archive rules.

### 8.2 Generated inventory

Generate:

```text
docs/_meta/generated/repository-document-inventory.json
```

Each Markdown file should have at minimum:

```text
path
role
lifecycle
canonicalDocumentId? 
release? 
sourceOwner? 
discoverabilityOwner
inboundDocumentRefs
machineRefs
status
```

### 8.3 Orphan definition

An orphan is a human-authored document that is not reachable through the official discovery mechanism for its role.

Examples of valid discovery mechanisms:

- canonical doc -> `navigation.yaml`;
- repository entrypoint -> root whitelist;
- plan -> planning index;
- validation report -> release validation index/final report;
- fixture README/TASK -> parent suite manifest or registered case;
- legacy README -> legacy inventory root;
- generated output -> generator manifest.

A document is **not** declared orphan merely because no Markdown hyperlink points to it.

### 8.4 Unknown-document fail-closed rule

Any new `.md` file that matches no declared role/path pattern MUST fail documentation validation.

This is the key preventive control against future stray files.

---

## 9. Canonical Path Migration Support

Before renaming canonical files, add a general migration registry:

```text
docs/_meta/path-migrations.yaml
```

Suggested record:

```yaml
migrations:
  - document: AIXEM-GOV-COMPAT-001
    from: docs/governance/compatibility.md
    to: docs/governance/compatibility-policy.md
    since: 0.5.7
    reason: disambiguate canonical basename
```

Requirements:

1. `document` resolves to the same stable canonical ID at the new path;
2. `from` cannot be reused by another active canonical doc;
3. migration records are immutable once released, except explicit correction;
4. generated site builds redirect/stub pages for prior published site paths where applicable;
5. internal links are rewritten to the new canonical path;
6. generated indexes use the new path only;
7. legacy references can resolve old path -> stable ID -> new path;
8. validation detects migration cycles and conflicting old paths.

This closes the current gap between the declared "paths may move" policy and actual tooling.

---

## 10. `AGENTS.md` Redesign

### 10.1 Objective

Reduce `AGENTS.md` from a release-accumulating handbook into a concise, stable repository operating contract.

### 10.2 Keep in `AGENTS.md`

Only repository-wide, high-frequency rules:

1. mission;
2. route-first retrieval order;
3. context budget;
4. authority precedence;
5. artifact authority boundaries;
6. invariant schematic rules;
7. generated-file rules;
8. documentation creation/move/delete rules;
9. documentation naming and placement table;
10. task workflow;
11. validation expectations;
12. fail-closed behavior;
13. compatibility/path migration;
14. current release pointer;
15. final-change reporting requirements.

### 10.3 Remove from `AGENTS.md`

Move or replace detailed release-specific sections that are already owned by canonical docs:

- 0.5.1 authoring operational detail;
- 0.5.2 symbol corpus detail;
- 0.5.3 hierarchy detail;
- 0.5.4 Viewer detail;
- 0.5.5 closed-loop detail;
- 0.5.6 live-agent detail.

Their durable rules already have task routes and canonical documents. `AGENTS.md` should link to the route or document ID rather than embedding a historical copy.

### 10.4 Add a documentation decision table

`AGENTS.md` should explicitly answer:

| Need | Correct action |
|---|---|
| Change an existing technical rule | edit the current canonical owner |
| Add a new technical authority | create canonical doc only after owner/route analysis |
| Record release change | update `docs/releases/<version>.md` and concise `CHANGELOG.md` |
| Record implementation plan | `planning/releases/<version>/...` |
| Record verification result | `validation/releases/<version>/...` or machine evidence area |
| Add fixture instructions | local `README.md`/`TASK.md` in registered fixture |
| Preserve obsolete information | archive/deprecate; do not leave an unclassified root file |
| Move canonical doc | preserve ID + add path migration record |
| Add generated index/report | change generator input; never hand-maintain output |

### 10.5 Add a “before creating a document” gate

Agents MUST answer:

1. What role will this document have?
2. Is there already an owner with the same authority and audience?
3. Why is a new document better than extending that owner?
4. What official index/registry will make it discoverable?
5. What is its lifecycle?
6. Does its filename obey the role's naming rule?
7. Does it need a stable canonical ID or is it noncanonical history/evidence?
8. What validator proves it is not orphaned?

If these cannot be answered, do not create the file.

### 10.6 Current release handling

`AGENTS.md` should not contain prose that must be manually rewritten in many places each release.

Use a compact version-neutral statement such as:

```text
Current release identity is read from VERSION and release metadata.
Use docs/releases/<VERSION>.md for release-specific narrative.
```

If a current-release capability requires special agent handling, route it through canonical task packets rather than appending another historical section.

---

## 11. New Canonical Governance Documents

0.5.7 should add or expand canonical documentation for the documentation system itself.

Preferred approach: add one normative owner plus one concise informative guide, rather than many overlapping documents.

### 11.1 Normative

Proposed:

```text
docs/specifications/documentation/document-governance-contract.md
```

Possible ID:

```text
AIXEM-SPEC-DOC-GOVERNANCE-001
```

Owns requirements for:

- role classification;
- path/naming rules;
- canonical vs noncanonical authority;
- discoverability;
- lifecycle;
- path migrations;
- root whitelist;
- generated-document boundaries;
- orphan detection.

### 11.2 Informative

Proposed:

```text
docs/governance/documentation-authoring-guide.md
```

Possible ID:

```text
AIXEM-GOV-DOC-AUTHORING-001
```

Contains:

- decision tree;
- naming examples;
- create/move/deprecate/delete workflow;
- examples of good/bad placement;
- checklist for agents and human contributors.

### 11.3 Existing metadata contract

Update `docs/specifications/documentation/metadata-contract.md` only for metadata-schema concerns. Do not turn it into a catch-all documentation style guide.

---

## 12. Root Document Consolidation Decisions

### 12.1 `README.md`

Keep.

Responsibilities:

- product identity;
- minimal quickstart;
- links to canonical docs;
- link to `AGENTS.md` for agents;
- link to current release note and validation entrypoint.

It must not duplicate detailed architecture/specification text.

### 12.2 `START_HERE.md`

Evaluate consumers first.

Preferred outcome: merge its high-value evaluation path into `README.md` and/or a canonical getting-started page, then remove it.

Retain only if a concrete external workflow depends on the filename.

### 12.3 `CHANGELOG.md`

Keep.

Responsibilities:

- concise chronological change list;
- no full release narrative;
- link to canonical release note for details.

### 12.4 `RELEASE_NOTES.md`

Preferred outcome: remove as an independent root narrative.

`docs/releases/<version>.md` remains the durable release note owner.

If ecosystem distribution requires root `RELEASE_NOTES.md`, generate it as a small pointer or copy from the canonical current-release source rather than hand-authoring both.

### 12.5 `IMPLEMENTATION_STATUS.md`

Preferred outcome: remove from root.

Current implementation/verification truth should be derived from:

- `VERSION`;
- release metadata;
- current release note;
- current final validation report.

If a human summary remains useful, place it under the version-scoped validation release directory and make its authority explicitly evidentiary, not normative.

### 12.6 `CONTRIBUTING.md`

Keep, but make documentation rules link to the new canonical documentation-governance contract and authoring guide.

### 12.7 `SECURITY.md`

Keep as the conventional repository security-reporting entrypoint.

It is distinct from `docs/architecture/security.md`, which owns technical trust-boundary architecture. Add an explicit link to prevent perceived duplication.

### 12.8 `NOTICE.md`

Keep if release/legal packaging expects it. Treat it as a root policy/legal special file, not canonical technical documentation.

---

## 13. Cleanup of Existing Canonical Documents

### 13.1 Build an append-block inventory

For every canonical file containing release patch markers or content after the canonical footer, classify every appended section as:

- integrate into existing section;
- move to another canonical owner;
- move to release history;
- move to example/cookbook;
- obsolete duplicate;
- retained version-specific compatibility rule.

### 13.2 No blind deletion

Patch markers may surround essential current requirements and executable examples. Remove markers only after content is preserved in its correct semantic location.

### 13.3 Priority cleanup group

Prioritize documents with the largest appended blocks and agent retrieval impact, including:

- `docs/file-formats/aixsym.md`
- `docs/symbols/primitives.md`
- `docs/symbols/pins-and-ports.md`
- `docs/symbols/variants.md`
- `docs/file-formats/aixlayout.md`
- `docs/conformance/validation.md`
- `docs/conformance/test-suite.md`
- `docs/routing/crossings-and-junctions.md`
- `docs/routing/net-routing.md`
- `docs/symbols/authoring-guide.md`
- agent documents containing 0.5.5/0.5.6 appended blocks.

### 13.4 Preserve requirement identity

Moving a normative requirement within the same document MUST preserve its requirement ID and stable anchor where feasible.

Moving a requirement to a different canonical owner requires an explicit migration review and traceability update; avoid such moves unless authority is genuinely wrong.

---

## 14. Automated Validation to Add

Create a repository-wide documentation auditor, preferably integrated into the existing docs toolchain.

Suggested command:

```bash
python tools/docs/audit_repository_docs.py
```

or an equivalent subcommand in `aixem_docs.py`.

### 14.1 Root hygiene

Fail when an unapproved Markdown file exists at repository root.

### 14.2 Path-role classification

Fail when a Markdown path matches no document role.

### 14.3 Naming validation

Validate:

- lowercase-kebab default;
- allowed special names;
- version-scoped conventions;
- no unknown uppercase document names;
- canonical basename collision policy.

### 14.4 Canonical footer validation

Fail if content appears after the terminal canonical footer.

### 14.5 Release patch-marker validation

Fail new canonical docs/changes that introduce historical append markers. Existing markers must reach zero before 0.5.7 release closure unless explicitly allowlisted with rationale.

### 14.6 Role-aware orphan validation

Validate discoverability using the registry rules described above.

### 14.7 Path migration validation

Validate old/new path uniqueness, stable ID preservation, no cycles, generated redirects, and updated internal links.

### 14.8 Metadata vocabulary validation

Validate controlled `domain` and `kind` values.

### 14.9 Stale current-version prose validation

At minimum, detect hard-coded `active release` or `current implementation` claims in `AGENTS.md` and root entrypoints that disagree with `VERSION`.

Do not attempt to infer every semantic version statement in historical release docs.

### 14.10 Documentation inventory determinism

Identical authored inputs must produce byte-identical repository-document inventory and migration products.

---

## 15. Proposed Migration Phases

### Phase 0 — Freeze and inventory

1. Unpack/checkout the exact 0.5.6 baseline.
2. Record all Markdown paths, sizes, hashes, roles, references, and machine consumers.
3. Record canonical IDs and requirement IDs.
4. Record release-manifest hashes and protected non-document outputs.
5. Run the existing documentation and repository suites before modification.

**Exit condition:** baseline inventory is reproducible and all pre-existing tests are green.

### Phase 1 — Publish documentation governance contract

1. Add the normative document-governance contract.
2. Add the informative documentation-authoring guide.
3. Update metadata schema vocabularies conservatively.
4. Add repository-document policy schema/policy.
5. Add path-migration schema/registry.
6. Add requirement IDs, conformance mappings, tests, and evidence.

**Exit condition:** new governance rules are themselves canonical, traceable, and release-gated.

### Phase 2 — Implement repository-wide documentation auditor

Implement:

- document role classification;
- root whitelist;
- naming checks;
- orphan/discoverability checks;
- canonical-footer checks;
- patch-marker checks;
- lifecycle checks;
- path migration checks;
- generated inventory.

Initially run in report mode to generate the migration backlog. Then convert required rules to fail-closed gates.

**Exit condition:** every existing Markdown file has an explicit role/classification.

### Phase 3 — Clean repository root

1. Create `planning/releases/`.
2. Move all `PLAN-*.md` files into version-scoped paths.
3. Add planning index/lifecycle records.
4. Resolve `START_HERE.md` by merge-or-justified-retain decision.
5. Eliminate manually duplicated root release narrative.
6. Move/remove `IMPLEMENTATION_STATUS.md` as a root owner.
7. Update README/CONTRIBUTING/SECURITY cross-links.

**Exit condition:** repository root matches the approved Markdown whitelist.

### Phase 4 — Normalize validation-document hierarchy

1. Classify every human-readable validation Markdown file by release and purpose.
2. Move implementation matrices into version-scoped validation release directories.
3. Move human verification reports into the owning version subtree.
4. Keep machine-bound evidence paths stable unless migration is fully supported.
5. Add one `validation/README.md` entrypoint describing evidence versus human reports.
6. Ensure historical reports remain immutable and discoverable.

**Exit condition:** no human validation report is ambiguously floating in a flat mixed-release directory.

### Phase 5 — Integrate canonical patch blocks

For all affected canonical docs:

1. capture pre-change semantic/requirement inventory;
2. integrate appended current rules into normal sections;
3. remove release patch markers;
4. move historical commentary to release/planning records where appropriate;
5. place footer at true end of document;
6. refresh related links and metadata;
7. re-run targeted routes/tests after each domain batch.

Recommended batches:

```text
A. agent + concepts
B. specifications + file formats
C. symbols + routing + schematic
D. conformance + getting-started + examples
```

**Exit condition:** zero unjustified release patch markers and zero content after canonical footer.

### Phase 6 — Normalize canonical filenames where justified

1. Implement path-migration support first.
2. Rename only the approved collision/ambiguity candidates.
3. Preserve IDs.
4. Update links, routes, navigation-derived products, site output, and migration records.
5. Validate prior site paths/compatibility behavior.

**Exit condition:** approved filename ambiguities are removed without identity loss.

### Phase 7 — Normalize metadata vocabulary and size estimates

1. Review all 27 current `kind` values.
2. Map them to the approved controlled vocabulary.
3. Constrain `domain` values.
4. derive/check token estimates automatically.
5. rebuild document/route/task-packet indexes.

**Exit condition:** metadata classification cannot drift through arbitrary new strings.

### Phase 8 — Rewrite `AGENTS.md`

1. Preserve high-value repository-wide rules.
2. add the document placement/naming/lifecycle decision table.
3. add the pre-create document gate.
4. remove historical per-release operational copies.
5. replace stale current-release prose with `VERSION`/route-driven pointers.
6. keep route-first context budget and authority rules intact.
7. verify that ordinary authoring tasks still resolve through bounded task packets without needing historical sections from `AGENTS.md`.

**Exit condition:** `AGENTS.md` is version-stable, shorter, and sufficient as an entrypoint without becoming a second technical manual.

### Phase 9 — Regenerate and repair all downstream products

Regenerate:

- canonical document index;
- route index;
- inverted index;
- dependency graph;
- artifact map;
- requirement traceability;
- task packets;
- repository-document inventory;
- site;
- compatibility reference output;
- release manifest.

Repair all path consumers and tests.

**Exit condition:** no stale path, ID, link, route, or manifest reference remains.

### Phase 10 — Three complete verification passes

Run the complete documentation/repository/release verification **three independent times** from a clean generated-output state.

Each pass must include:

1. repository-document audit;
2. canonical metadata/link/dependency validation;
3. navigation coverage;
4. route integrity and budgets;
5. path-migration integrity;
6. orphan/discoverability validation;
7. generated-output determinism;
8. static site build and link validation;
9. existing repository tests;
10. protected circuit/render/Viewer regression checks;
11. requirement traceability;
12. release manifest/package integrity.

Retain pass-specific evidence.

---

## 16. Required Regression Protections

0.5.7 is a documentation architecture release. It MUST NOT accidentally mutate technical behavior.

Protect at minimum:

- `.aixem` schemas/semantics;
- `.aixsym.json` schemas/semantics;
- `.aixlayout.json` schemas/semantics;
- `.aixproj.json` schemas/semantics;
- renderer output hashes where currently protected;
- Viewer/Workbench contracts and output hashes where protected;
- agent diagnostic/change-set/execution/run-record contracts;
- live-agent cold-start protocol contracts;
- existing route intent behavior unless a documentation-specific route change is intentionally required.

Documentation path changes may alter documentation/site/reference manifests, but they must not alter circuit/render outputs.

---

## 17. Acceptance Criteria

0.5.7 is complete only if all of the following are true.

### Repository structure

- [ ] Repository root contains only approved Markdown entrypoints.
- [ ] Historical plans are version-scoped under `planning/releases/`.
- [ ] Human validation reports are release/purpose scoped.
- [ ] Every Markdown file is assigned exactly one role.
- [ ] No unknown-role Markdown exists.

### Canonical docs

- [ ] 100% of canonical docs retain unique stable IDs.
- [ ] 100% remain present exactly once in navigation.
- [ ] No broken canonical internal links or anchors.
- [ ] No dependency cycles.
- [ ] No content exists after canonical footer.
- [ ] No unjustified release patch markers remain.
- [ ] Controlled `domain` and `kind` vocabularies validate.
- [ ] Canonical filename migration records validate.

### Discoverability

- [ ] Every plan is reachable from the planning index.
- [ ] Every human validation report is reachable from a validation release index/owner.
- [ ] Every fixture `README.md` / `TASK.md` is bound to a registered example/evaluation unit.
- [ ] Every root Markdown file is explicitly whitelisted.
- [ ] Role-aware orphan count is zero.

### AGENTS

- [ ] `AGENTS.md` contains the new documentation rules.
- [ ] `AGENTS.md` no longer acts as a historical release ledger.
- [ ] No stale active-release prose contradicts `VERSION`.
- [ ] Route-first retrieval and existing context budgets remain intact.
- [ ] An agent can determine where a new document belongs without repository-wide guessing.

### Tooling

- [ ] Repository-wide document audit is automated.
- [ ] Path migration is automated and validated.
- [ ] Generated repository-document inventory is deterministic.
- [ ] New stray Markdown fails CI/release validation.

### Verification

- [ ] Three complete clean verification passes succeed.
- [ ] All existing technical regressions pass.
- [ ] Release manifest verifies.
- [ ] Final ZIP/archive verifies with no path traversal, missing members, or digest mismatch.

---

## 18. Explicit Non-Goals

0.5.7 should NOT:

- redesign schematic semantics;
- add new renderer features;
- change Viewer behavior;
- broaden agent write authority;
- rewrite all technical prose merely for stylistic uniformity;
- move every noncanonical file into `docs/`;
- delete historical plans or verification evidence just because they are old;
- introduce a heavyweight external documentation framework;
- create many new governance documents when one owner and one guide are sufficient;
- rename stable canonical IDs for cosmetic consistency;
- reorganize machine evidence paths without a concrete benefit and complete migration proof.

---

## 19. Recommended Implementation Priority

### P0 — Required

1. repository-wide document taxonomy;
2. canonical documentation-governance contract;
3. repository-document policy + generated inventory;
4. role-aware orphan validation;
5. root Markdown whitelist;
6. planning release hierarchy and root-plan migration;
7. validation report release hierarchy;
8. path-migration facility before canonical renames;
9. canonical footer/post-footer cleanup;
10. removal/integration of release patch blocks;
11. AGENTS documentation rules and historical-section compaction;
12. stale active-version elimination;
13. three-pass verification and package integrity.

### P1 — Strongly recommended

1. controlled `kind` vocabulary;
2. controlled `domain` vocabulary;
3. global canonical basename ambiguity cleanup;
4. derived token estimates;
5. generated root/current-release pointers where useful;
6. evaluation-suite naming normalization if migration cost is acceptable.

### P2 — Defer unless justified

1. broad canonical domain reshuffling;
2. rewriting all historical evidence paths;
3. major documentation-site visual redesign;
4. new documentation runtime/search infrastructure;
5. splitting documents solely based on length.

---

## 20. Expected Result

After 0.5.7, an agent should be able to infer the following without a repository-wide search:

```text
Need technical truth?
    -> docs/ canonical route

Need repository operating rules?
    -> AGENTS.md / CONTRIBUTING.md

Need why a release was planned?
    -> planning/releases/<version>/

Need what changed?
    -> CHANGELOG.md -> docs/releases/<version>.md

Need proof of what passed?
    -> validation/releases/<version>/ -> machine evidence

Need a fixture task?
    -> registered example/evaluation directory

Need old compatibility context?
    -> legacy/ or path-migration registry
```

The important architectural outcome is not fewer files by itself. It is **zero ambiguous ownership**:

- one place for current normative truth;
- one place for plans;
- one place for release history;
- one place for validation narratives/evidence;
- one stable agent entrypoint;
- one automated rule set that prevents documentation from becoming disorganized again.

That is the appropriate documentation foundation for AIXEM to continue evolving as an AI-native schematic authoring platform without making future agents read an ever-growing historical pile before they can draw or modify a circuit.
