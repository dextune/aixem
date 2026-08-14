# AIXEM 0.5 Plan — Documentation Architecture & Agent Reference System

> Status: **Implemented in 0.5.0**  
> Baseline: AIXEM Schematic Reference Platform 0.4  
> Target release: 0.5  
> Theme: **One canonical documentation root, two optimized consumers — humans and AI agents**

## 0. Executive summary

AIXEM 0.5 is a documentation-system release, not a feature-expansion release. Its primary objective is to turn the current set of documents, specifications, reference indexes, examples, and validation artifacts into a coherent documentation platform comparable to an official SDK/standard documentation site.

The central rule is:

```text
Canonical authored docs
        |
        +--> Official static documentation site for humans
        +--> Compiled task routes / indexes / cards for AI agents
        +--> Requirement traceability / conformance data
        +--> Release manifest / integrity evidence
```

AIXEM 0.5 SHALL eliminate the need to maintain the same rule separately in prose documentation and agent-reference JSON. Markdown under `docs/` becomes the canonical human-authored knowledge source; machine indexes are generated from document metadata.

---

## 1. Goals

### 1.1 Primary goals

1. Establish `docs/` as the **single canonical documentation root**.
2. Reorganize documentation into a stable information architecture suitable for an official public site.
3. Add structured metadata to every canonical document.
4. Compile agent-optimized indexes, task routes, dependency graphs, aliases, and manifests from canonical docs.
5. Preserve route-first bounded retrieval so an agent does not search or read the whole repository for ordinary tasks.
6. Introduce normative requirement IDs and end-to-end traceability from specification to validator/test/evidence.
7. Build a fully static documentation site from the same source documents.
8. Add release gates that prevent missing files, stale indexes, broken links, orphaned docs, conflicting authority, or non-deterministic generated output.
9. Keep AIXEM graphics and schematic conventions vendor-neutral and independent.
10. Provide a root `AGENTS.md` that tells coding/authoring agents exactly how to enter, navigate, modify, validate, and report work.

### 1.2 Non-goals for 0.5

- Redesigning the core semantic circuit model without a documentation-driven need.
- Replacing the orthogonal router or schematic renderer architecture solely for performance.
- Adding a server-side documentation backend.
- Requiring an external search service to navigate docs.
- Copying UI assets, icons, nomenclature, or proprietary library content from OrCAD, KiCad, or another EDA vendor.

---

## 2. Architecture principles

### P1 — One source of truth

A rule is authored once. Machine-oriented reference artifacts are generated, not manually duplicated.

### P2 — Stable identity over file location

Every canonical document has a stable `id`. File paths may move without changing the document identity.

### P3 — Route first, search second

Known agent intents resolve to a bounded route before full-text or repository-wide search is allowed.

### P4 — Normative and informative content are explicit

Documents and sections must distinguish requirements from explanations/examples.

### P5 — Generated files are disposable

Anything reproducible from canonical sources is treated as generated output and MUST NOT become a second authority.

### P6 — Deterministic release

Same source + same toolchain = byte-stable generated metadata where practical, with reproducible digests and manifests.

### P7 — Human navigation and agent navigation share the same graph

Sidebar, related links, agent routes, dependency graphs, and requirement traceability derive from the same metadata model.

### P8 — Bounded context is a design constraint

Default agent retrieval budget remains at most **7 documents / 96 KiB / depth 3** unless a task route explicitly grants more.

---

## 3. Target repository documentation structure

```text
docs/
├── index.md
├── getting-started/
│   ├── index.md
│   ├── introduction.md
│   ├── quick-start.md
│   └── first-schematic.md
├── concepts/
│   ├── index.md
│   ├── semantic-model.md
│   ├── authority-model.md
│   ├── component-model.md
│   ├── net-model.md
│   ├── symbol-model.md
│   └── layout-model.md
├── schematic/
│   ├── index.md
│   ├── grid-system.md
│   ├── placement.md
│   ├── junctions.md
│   ├── annotations.md
│   └── visual-language.md
├── symbols/
│   ├── index.md
│   ├── symbol-anatomy.md
│   ├── pins-and-ports.md
│   ├── primitives.md
│   ├── authoring-guide.md
│   └── symbol-lint.md
├── routing/
│   ├── index.md
│   ├── net-routing.md
│   ├── orthogonal-routing.md
│   ├── route-constraints.md
│   └── router-behavior.md
├── specifications/
│   ├── index.md
│   ├── core/
│   ├── schematic/
│   ├── symbols/
│   ├── layout/
│   ├── project/
│   ├── agent/
│   └── schemas/
├── file-formats/
│   ├── index.md
│   ├── aixem.md
│   ├── aixlib.md
│   ├── aixsym.md
│   ├── aixlayout.md
│   └── aixproj.md
├── agent/
│   ├── index.md
│   ├── architecture.md
│   ├── retrieval.md
│   ├── task-routing.md
│   ├── schematic-authoring.md
│   ├── symbol-generation.md
│   ├── routing-agent.md
│   └── validation-loop.md
├── architecture/
│   ├── index.md
│   ├── system-overview.md
│   ├── pipeline.md
│   ├── artifact-store.md
│   ├── cache.md
│   ├── security.md
│   └── adr/
├── conformance/
│   ├── index.md
│   ├── requirements.md
│   ├── validation.md
│   ├── test-suite.md
│   └── compatibility.md
├── examples/
│   ├── index.md
│   ├── basic/
│   ├── controller/
│   └── advanced/
├── governance/
│   ├── versioning.md
│   ├── compatibility.md
│   ├── deprecation.md
│   ├── release-process.md
│   └── terminology.md
├── releases/
│   ├── index.md
│   ├── 0.4.md
│   └── 0.5.md
└── _meta/
    ├── schema/
    │   └── document-metadata.schema.json
    ├── navigation.yaml
    ├── aliases.yaml
    ├── glossary.yaml
    ├── routes/
    │   ├── create-schematic.yaml
    │   ├── create-symbol.yaml
    │   ├── route-nets.yaml
    │   ├── validate-project.yaml
    │   └── change-architecture.yaml
    └── generated/
        ├── document-index.json
        ├── route-index.json
        ├── inverted-index.json
        ├── dependency-graph.json
        ├── artifact-map.json
        ├── requirement-traceability.json
        └── manifest.json
```

### Authored vs generated boundary

**Authored:** Markdown documents, YAML route declarations, navigation metadata, aliases, glossary, schemas.  
**Generated:** indexes, dependency graph, traceability graph, manifests, compatibility reference output, search index, static site output.

The existing `reference/` tree becomes a **compatibility build target** during 0.5 rather than the long-term canonical source.

---

## 4. Canonical document metadata contract

Every canonical Markdown file MUST carry front matter. Minimum target contract:

```yaml
---
id: AIXEM-SCHEM-GRID-001
title: Grid and Snap System
status: normative
version: 1.0
domain: schematic

summary: Defines schematic grid, snap, and coordinate rules.

authority:
  - layout
  - rendering

aliases:
  - grid
  - snap grid
  - coordinate grid
  - alignment grid

agent:
  priority: high
  estimated_tokens: 850
  intents:
    - create-schematic
    - place-component
    - route-net

depends_on:
  - AIXEM-CORE-COORD-001

related:
  - AIXEM-SCHEM-ROUTE-001
---
```

### Required metadata fields

- `id`
- `title`
- `status`: `normative | informative | draft | deprecated`
- `version`
- `domain`
- `summary`
- `authority`
- `aliases`
- `agent.intents`
- `depends_on`
- `related`

### Rules

- IDs are immutable after publication.
- Titles and paths may change.
- A document can be deprecated only with a replacement pointer or an explicit terminal reason.
- Two active normative documents MUST NOT claim conflicting authority for the same rule without an explicit precedence declaration.
- Generated indexes SHALL reference stable IDs, not rely solely on paths.

---

## 5. Requirement and conformance model

Normative requirements receive stable IDs such as:

```text
AIXEM-REQ-CORE-0001
AIXEM-REQ-SCHEM-0012
AIXEM-REQ-SYMBOL-0024
AIXEM-REQ-ROUTE-0031
AIXEM-REQ-AGENT-0040
```

Target traceability chain:

```text
Requirement
   -> Canonical specification section
   -> Schema / constraint
   -> Validator rule
   -> Test case
   -> Evidence artifact
   -> Release conformance report
```

Each release MUST be able to answer:

- Where is this rule defined?
- Which validator enforces it?
- Which test proves it?
- Which release evidence shows it passed?

---

## 6. Agent reference compiler

### 6.1 Input

- canonical Markdown front matter
- section anchors
- `_meta/routes/*.yaml`
- aliases and glossary
- artifact ownership metadata
- requirement IDs

### 6.2 Generated output

```text
docs/_meta/generated/
  document-index.json
  route-index.json
  inverted-index.json
  dependency-graph.json
  artifact-map.json
  requirement-traceability.json
  manifest.json
```

Optional 0.4 compatibility output:

```text
reference/index.aixref.json
reference/routes/*.aixroute.json
reference/cards/**/*.aixcard.json
reference/indexes/*.json
```

### 6.3 Resolver policy

```text
1. Normalize user task -> intent
2. Exact intent / alias lookup
3. Load task route
4. Load required docs/sections in order
5. Evaluate conditional reads
6. Stop when route completion condition is met
7. Use inverted index only if no valid route exists
8. Never exceed route/context budget without explicit justification
```

### 6.4 Compiler invariants

- duplicate document ID = build failure
- unresolved dependency = build failure
- missing route target = build failure
- route cycle = build failure unless explicitly marked iterative
- normative authority conflict = build failure
- stale generated index = release failure
- non-deterministic manifest for identical source = test failure

---

## 7. Official documentation site

The site is a static build product generated from `docs/`; no database or runtime backend is required.

### Required UX

- hierarchical left navigation
- top search
- breadcrumb
- section table of contents
- Previous / Next navigation
- document version and status badge
- Normative / Informative / Draft / Deprecated state
- stable document ID display
- Related Documents
- Used By / Depends On graph links
- schema viewer
- requirement backlinks
- example schematic viewer
- responsive layout
- print-friendly specification pages
- canonical anchors for every requirement

### AIXEM visual direction

The docs site should be restrained and engineering-oriented:

- square or low-radius controls
- compact typography and spacing
- high information density without visual clutter
- grid-aware diagrams
- schematic examples rendered from AIXEM artifacts where possible
- no copied vendor icons, toolbar art, logos, or proprietary component artwork

### Build recommendation

Use a static documentation framework as a presentation layer only. The source of truth remains framework-neutral Markdown + metadata. The build layer may be replaced without migrating the canonical content model.

---

## 8. AGENTS.md contract

The project root contains `AGENTS.md` and every coding/authoring agent reads it first.

It defines:

- repository purpose
- source-of-truth hierarchy
- route-first reading rules
- context budget
- artifact authority boundaries
- schematic/grid/routing invariants
- document editing rules
- generated-file policy
- validation obligations
- release integrity requirements
- final work-report format

Nested `AGENTS.md` files MAY be introduced later only when a subtree needs stricter local rules. Local rules can narrow behavior but must not silently contradict root normative requirements.

---

## 9. Implementation plan — three refinement passes

AIXEM 0.5 is implemented in three deliberate passes. Each pass finishes with a self-validation gate before the next begins.

# PASS 1 — Canonicalize and normalize

### Work

1. Inventory all 0.4 documents/specifications/reference entries/examples.
2. Build `legacy-path -> canonical-document-id -> new-path` migration map.
3. Detect duplicates, contradictions, stale references, and declared-but-missing artifacts.
4. Create target `docs/` hierarchy.
5. Move/rewrite content into canonical documents without losing provenance.
6. Add front matter metadata to 100% of canonical docs.
7. Create glossary and terminology policy.
8. Create governance/version/deprecation rules.
9. Keep legacy paths as generated compatibility outputs or explicit redirects where required.

### Self-validation 1

- 100% canonical docs have unique IDs.
- 0 unresolved internal links.
- 0 unclassified authored docs.
- 0 duplicate active normative authorities.
- 100% legacy source files are mapped to `migrated / deprecated / generated / retained`.
- No document claims the existence of an absent release artifact.

### Deliverable

`0.5-alpha1 — Canonical Documentation Tree`

---

# PASS 2 — Compile and route for agents

### Work

1. Implement document metadata parser.
2. Implement metadata schema validation.
3. Implement document index compiler.
4. Implement alias/intent resolver.
5. Implement route compiler.
6. Implement dependency graph and artifact ownership graph.
7. Implement requirement traceability generator.
8. Implement deterministic manifest/digest generation.
9. Generate 0.4-compatible `reference/` artifacts where needed.
10. Add retrieval test corpus covering schematic creation, symbol creation, routing, validation, architecture change, artifact inspection, and migration.

### Self-validation 2

- exact known intents resolve without repository-wide search.
- common task routes stay within 7 docs / 96 KiB / depth 3.
- 0 unresolved route targets.
- 0 dependency cycles except explicitly approved iterative loops.
- 100% generated outputs trace to canonical source IDs.
- second compiler run with unchanged inputs produces no semantic diff.
- stale generated output is detected by `--check` mode.

### Deliverable

`0.5-beta1 — Agent Reference Compiler & Bounded Retrieval`

---

# PASS 3 — Publish, conform, and harden

### Work

1. Build official static documentation site.
2. Add navigation/search/breadcrumb/status/related/dependency UI.
3. Add embedded schematic and schema examples.
4. Introduce normative requirement IDs across specifications.
5. Bind validator/test/evidence records to requirement IDs.
6. Add release integrity gate.
7. Add broken-link/orphan/authority-conflict/stale-index checks.
8. Add documentation build reproducibility test.
9. Generate release conformance report.
10. Perform visual review for desktop and narrow layouts.

### Self-validation 3

- static site builds with zero errors and zero broken internal links.
- every normative requirement has a canonical anchor.
- required validator/test/evidence coverage is reported with no silent gaps.
- all release-manifest paths exist and hashes match.
- no generated file is hand-authored or divergent from source.
- representative agent tasks complete using route-first retrieval.
- representative human tasks reach the target content in <= 3 navigation hops.
- release ZIP passes integrity and manifest verification.

### Deliverable

`0.5-rc1 -> 0.5.0 — Official Documentation & Conformance Release`

---

## 10. Work breakdown structure

| ID | Work package | Priority | Depends on |
|---|---|---:|---|
| D0 | 0.4 baseline inventory | P0 | - |
| D1 | Canonical information architecture | P0 | D0 |
| D2 | Legacy-to-canonical migration map | P0 | D0 |
| D3 | Document metadata schema | P0 | D1 |
| D4 | Canonical content migration | P0 | D1,D2,D3 |
| D5 | Glossary/governance/version policy | P1 | D1 |
| A1 | Metadata parser + validator | P0 | D3 |
| A2 | Document/alias index compiler | P0 | A1,D4 |
| A3 | Route compiler/resolver | P0 | A2 |
| A4 | Dependency/artifact graph | P0 | A2 |
| A5 | Requirement traceability compiler | P1 | A1 |
| A6 | 0.4 reference compatibility output | P1 | A2,A3 |
| S1 | Static docs site shell | P1 | D1 |
| S2 | Generated navigation/search | P1 | A2,S1 |
| S3 | Schema/schematic viewers | P2 | S1 |
| C1 | Requirement ID migration | P0 | D4 |
| C2 | Validator/test/evidence mapping | P0 | C1,A5 |
| C3 | Release integrity gate | P0 | A2,A4,C2 |
| C4 | Reproducible build checks | P1 | C3 |
| R1 | Migration report | P1 | D4 |
| R2 | 0.5 conformance report | P0 | C3,C4 |
| R3 | 0.5 release bundle | P0 | all P0 |

---

## 11. Target tooling layout

The exact implementation language may follow the main project toolchain, but responsibilities should be separated as follows:

```text
tools/docs/
├── parse_metadata.*
├── validate_docs.*
├── build_index.*
├── build_routes.*
├── build_graphs.*
├── build_traceability.*
├── build_manifest.*
├── build_legacy_reference.*
└── check_release.*

tests/docs/
├── metadata/
├── routes/
├── graphs/
├── requirements/
├── release/
└── retrieval-corpus/
```

The tooling MUST support at least:

```text
build   : regenerate derived documentation artifacts
check   : fail if generated artifacts are stale or invalid
verify  : validate a release bundle and manifest
```

---

## 12. Migration rules from 0.4

### 12.1 Current canonical candidates

Current 0.4 content should be migrated approximately as follows:

| 0.4 path | 0.5 target |
|---|---|
| `START_HERE.md` | `docs/getting-started/index.md` + root README entrypoint |
| `docs/05-reference-navigation-architecture.md` | `docs/agent/retrieval.md` |
| `docs/06-agent-task-execution-protocol.md` | `docs/agent/architecture.md` / `task-routing.md` |
| `docs/07-system-architecture-and-services.md` | `docs/architecture/system-overview.md` |
| `docs/08-cache-digest-and-incremental-loading.md` | `docs/architecture/cache.md` |
| `specifications/aixem-grid-schematic-style-1.aixstyle.json` | `docs/specifications/schematic/` + schema/example asset |
| `reference/index.aixref.json` | generated compatibility artifact |
| `examples/.../drawing.svg` | `docs/examples/...` referenced build asset |
| `examples/.../workbench.html` | docs example viewer/build asset |
| `validation/...` | release/conformance evidence |

### 12.2 Important 0.4 cleanup

The 0.4 root index currently declares route/domain/index paths that are not all present in the active extracted baseline. The 0.5 migration begins by treating this as an integrity defect, not by synthesizing assumed content. Each declared artifact must be recovered from an authoritative source, regenerated from canonical docs, or removed/deprecated with an explicit migration record.

---

## 13. Schematic/graphics invariants preserved in 0.5

Documentation reorganization MUST NOT weaken the existing visual/semantic rules:

- 2.5 mm snap grid baseline.
- orthogonal routing using 0/90/180/270-degree segments.
- explicit junction semantics; a visual crossing alone does not create connectivity.
- semantic connectivity, symbol representation, placement/routing, and rendering style remain separate authority layers.
- compact grid-first schematic presentation.
- independent AIXEM visual assets and naming.
- no copied vendor graphics or proprietary libraries.

Any changes to these invariants require a normative specification change, compatibility impact note, and conformance test update.

---

## 14. Release gates

0.5.0 MUST NOT be released if any of the following is true:

- missing file referenced by canonical docs or manifest
- duplicate stable document ID
- duplicate requirement ID
- unresolved internal document link
- unresolved dependency or route target
- unapproved dependency cycle
- stale generated index
- conflicting normative authority without explicit precedence
- generated artifact edited independently of canonical source
- manifest hash mismatch
- release ZIP verification failure
- required conformance evidence missing
- official docs site build failure

---

## 15. Acceptance metrics

| Metric | 0.5 target |
|---|---:|
| Canonical docs with valid metadata | 100% |
| Duplicate active document IDs | 0 |
| Broken internal links | 0 |
| Unresolved route targets | 0 |
| Orphan canonical docs | 0, except explicitly exempted |
| Known task exact-route resolution | >= 95% test corpus |
| Common route read budget | <= 7 docs / 96 KiB / depth 3 |
| Normative requirements with stable IDs | 100% |
| Release manifest missing paths | 0 |
| Unchanged-input generated semantic diff | 0 |
| Human core-task navigation depth | <= 3 hops |
| Static site runtime backend dependency | 0 |

---

## 16. Expected 0.5 release artifacts

```text
AGENTS.md
README.md
CHANGELOG.md

docs/                         # canonical authored documentation
site/ or dist/docs/           # generated static official documentation

docs/_meta/generated/         # compiled agent/document indexes
reference/                     # optional 0.4 compatibility build output

tools/docs/                    # compiler, validators, release checks
tests/docs/                    # documentation and retrieval tests

validation/
├── migration-report.md
├── documentation-validation-report.md
├── agent-retrieval-report.md
├── requirement-traceability-report.md
├── release-integrity-report.md
└── evidence/
```

Release bundle:

```text
AIXEM-SRP-0.5.0.zip
```

---

## 17. Definition of Done

AIXEM 0.5 is complete only when:

1. A new human reader can start at one official documentation entrypoint and navigate the project without knowing repository paths.
2. An AI agent can start at `AGENTS.md`, resolve a known task route, and load only the minimum authoritative documents needed for the task.
3. Canonical documentation and agent reference data cannot silently drift because the latter is compiled from the former.
4. A requirement can be traced from specification to validation evidence.
5. The official site is generated statically from the same canonical source.
6. The release process rejects missing, stale, contradictory, or non-reproducible documentation artifacts.
7. The entire release ZIP and manifest verify successfully.

---

## 18. Execution order

```text
0. Baseline inventory/freeze
        ↓
1. Canonical docs tree + migration map
        ↓
2. Metadata schema + front matter migration
        ↓
3. PASS 1 validation
        ↓
4. Agent reference compiler + route tests
        ↓
5. PASS 2 validation
        ↓
6. Requirement/conformance migration
        ↓
7. Official static docs site
        ↓
8. Release integrity/reproducibility gates
        ↓
9. PASS 3 validation
        ↓
10. 0.5.0 release bundle
```

The first implementation task after approving this plan is **D0: generate the 0.4 baseline inventory and legacy-to-canonical migration map**. No bulk file move should occur before that inventory is complete.
