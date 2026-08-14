# AIXEM Repository Reference Map

This root document is the stable navigation map for AIXEM. It routes readers and agents to the correct owner without duplicating technical rules. Current technical authority remains in canonical documents under `docs/`; generated indexes, plans, release reports, examples, and evidence remain subordinate to their declared owners.

## 1. Choose the Correct Entry Point

| Need | Start here | Continue through |
|---|---|---|
| AI or automated repository work | [`AGENTS.md`](AGENTS.md) | route index, task packet, canonical owner |
| Fast independent evaluation | [`START_HERE.md`](START_HERE.md) | current release note and validation index |
| General product orientation | [`README.md`](README.md) | canonical documentation home |
| Human contribution workflow | [`CONTRIBUTING.md`](CONTRIBUTING.md) | documentation governance and release process |
| Security reporting or trust boundary | [`SECURITY.md`](SECURITY.md) | canonical security architecture |
| Chronological release history | [`CHANGELOG.md`](CHANGELOG.md) | canonical release notes |
| Legal and attribution notice | [`NOTICE.md`](NOTICE.md) | repository package contents |

## 2. Canonical Documentation Categories

Resolve broad subject matter through these category indexes. Each category index links every canonical member registered in its navigation section.

| Category | Canonical index | Primary purpose |
|---|---|---|
| Documentation home | [`docs/index.md`](docs/index.md) | platform overview and authority model |
| Getting started | [`docs/getting-started/index.md`](docs/getting-started/index.md) | installation, quick start, first schematic |
| End-to-end authoring | [`docs/authoring/index.md`](docs/authoring/index.md) | shortest path from component to validated circuit |
| Task-oriented authoring | [`docs/authoring/guides/index.md`](docs/authoring/guides/index.md) | one-hop create/select/place/route/review/validate procedures |
| Reusable project library | [`library/README.md`](library/README.md) | canonical new part root and normative contract links |
| Core concepts | [`docs/concepts/index.md`](docs/concepts/index.md) | semantics, authority, nets, symbols, layout, projects |
| Schematic authoring | [`docs/schematic/index.md`](docs/schematic/index.md) | grid, placement, annotation, junction, sheet organization |
| Symbol authoring | [`docs/symbols/index.md`](docs/symbols/index.md) | symbol geometry, ports, fields, variants, lint |
| Net routing | [`docs/routing/index.md`](docs/routing/index.md) | orthogonal geometry, constraints, crossings, cookbooks |
| File formats | [`docs/file-formats/index.md`](docs/file-formats/index.md) | `.aixem`, symbol, library, layout, project, style files |
| Normative specifications | [`docs/specifications/index.md`](docs/specifications/index.md) | contracts, profiles, schemas, agent protocols |
| Viewer specifications | [`docs/specifications/viewer/index.md`](docs/specifications/viewer/index.md) | Reference Viewer, Workbench, state, security, accessibility |
| AI agent operations | [`docs/agent/index.md`](docs/agent/index.md) | bounded retrieval, task routes, repair, closure, live boundary |
| System architecture | [`docs/architecture/index.md`](docs/architecture/index.md) | pipeline, storage, cache, security, ADRs |
| Conformance | [`docs/conformance/index.md`](docs/conformance/index.md) | requirements, validators, corpora, release gates |
| Examples | [`docs/examples/index.md`](docs/examples/index.md) | executable reference projects and corpus guidance |
| Governance | [`docs/governance/index.md`](docs/governance/index.md) | versioning, compatibility, deprecation, release, terminology |
| Release notes | [`docs/releases/index.md`](docs/releases/index.md) | durable version-scoped release narratives |

Repository examples are indexed by the canonical examples section and have local build instructions at [`examples/authoring/README.md`](examples/authoring/README.md) and [`examples/electronics-grid-controller/README.md`](examples/electronics-grid-controller/README.md).

## 3. Task and Agent Retrieval

Use route-first retrieval rather than broad repository search.

1. Query intent with [`tools/docs/query_route.py`](tools/docs/query_route.py).
2. Resolve the generated [`route-index.json`](docs/_meta/generated/route-index.json).
3. Load the matching packet from [`task-packets/`](docs/_meta/generated/task-packets/).
4. Read only the canonical document IDs and sections named by that packet.
5. Confirm route write authority before editing.
6. Complete `prepare -> edit -> check -> close` and retain required evidence.

The authored route definitions are under [`docs/_meta/routes/`](docs/_meta/routes/). The route index and task packets are derived navigation products and never technical authority.

For common authoring work, select exactly one guide from [`docs/authoring/guides/index.md`](docs/authoring/guides/index.md). New reusable component and symbol artifacts start through [`library/README.md`](library/README.md) and the canonical [Library Layout and Part Integrity Contract](docs/specifications/components/library-layout-contract.md).

## 4. Artifact and Specification Ownership

| Question | Canonical owner |
|---|---|
| Which artifact owns a fact? | [`Authority Model`](docs/concepts/authority-model.md) and [`Authority and Precedence`](docs/specifications/core/authority-precedence.md) |
| Semantic circuit structure | [`.aixem Semantic Source`](docs/file-formats/aixem.md) |
| Component library binding | [`.aixlib.json Component Library`](docs/file-formats/aixlib.md) |
| New reusable library location and part integrity | [`Library Layout and Part Integrity Contract`](docs/specifications/components/library-layout-contract.md) |
| Component pin electrical semantics | [`Pin Electrical Semantics Profile 1`](docs/specifications/components/pin-electrical-semantics-profile.md) |
| Symbol graphics and electrical ports | [`.aixsym.json Symbol Asset`](docs/file-formats/aixsym.md) |
| Placement and route geometry | [`.aixlayout.json Explicit Layout`](docs/file-formats/aixlayout.md) |
| Project composition and project nets | [`.aixproj.json Project Lock`](docs/file-formats/aixproj.md) |
| Grid and visual profile | [`Grid Schematic Profile 1`](docs/specifications/schematic/grid-profile.md) and [`Schematic Presentation Profile 1`](docs/specifications/schematic/visual-profile.md) |
| Renderer behavior | [`Renderer Contract 1`](docs/specifications/renderer/renderer-contract.md) |
| Viewer behavior | [`Viewer Specifications`](docs/specifications/viewer/index.md) |
| Agent task, execution, observation, and evidence | [`AI Agent Operations`](docs/agent/index.md) and agent contracts under [`docs/specifications/agent/`](docs/specifications/agent/) |

## 5. Machine-Readable Reference Indexes

| Index | Purpose |
|---|---|
| [`document-index.json`](docs/_meta/generated/document-index.json) | stable document identity, metadata, headings, requirements |
| [`route-index.json`](docs/_meta/generated/route-index.json) | intent-to-route resolution and bounded document selection |
| [`task-packet-index.json`](docs/_meta/generated/task-packet-index.json) | generated task-packet inventory |
| [`requirement-traceability.json`](docs/_meta/generated/requirement-traceability.json) | requirement-to-validator/test/evidence closure |
| [`dependency-graph.json`](docs/_meta/generated/dependency-graph.json) | canonical dependency and related-document graph |
| [`artifact-map.json`](docs/_meta/generated/artifact-map.json) | authored and generated artifact ownership |
| [`repository-document-inventory.json`](docs/_meta/generated/repository-document-inventory.json) | repository-wide document role and lifecycle inventory |
| [`document-relationship-audit.json`](docs/_meta/generated/document-relationship-audit.json) | root reachability, section-index coverage, release coherence, authority-scope review |
| [`path-migration-index.json`](docs/_meta/generated/path-migration-index.json) | stable identity across canonical path changes |
| [`Schema Catalog`](docs/specifications/schemas/index.md) | governed schema inventory and validation entrypoint |

## 6. Validation, Evidence, and Release Chain

```text
canonical requirement
    -> validator and test mapping
    -> generated traceability
    -> release-specific evidence
    -> repeated verification summary
    -> release manifest
    -> independently verified ZIP
```

Start at [`validation/README.md`](validation/README.md). Current release narratives are under [`validation/releases/`](validation/releases/README.md), retained machine evidence is under [`validation/evidence/`](validation/evidence/README.md), and the deterministic pre-live readiness result remains at [`validation/agent-evals-3/results/readiness/readiness-report.json`](validation/agent-evals-3/results/readiness/readiness-report.json).

For the active release, read [`docs/releases/0.5.9.md`](docs/releases/0.5.9.md), [`validation/releases/0.5.9/README.md`](validation/releases/0.5.9/README.md), [`release/release-metadata.json`](release/release-metadata.json), and [`release/manifest.json`](release/manifest.json).

## 7. Plans, History, and Compatibility

- Implementation intent: [`planning/README.md`](planning/README.md)
- Historical plan registry: [`planning/index.yaml`](planning/index.yaml)
- Legacy migration context: [`legacy/README.md`](legacy/README.md)
- Canonical path migrations: [`docs/_meta/path-migrations.yaml`](docs/_meta/path-migrations.yaml)
- Compatibility policy: [`docs/governance/compatibility-policy.md`](docs/governance/compatibility-policy.md)
- Compatibility conformance: [`docs/conformance/compatibility-conformance.md`](docs/conformance/compatibility-conformance.md)

Plans and historical reports explain intent or observed results. They never override current canonical specifications.

## 8. Repository Structure and Build Controls

Every governed top-level area is reachable from this root map. Directories under `reference/` and `site/` are generated; edit their owners rather than their contents.

| Repository area | Role and authority |
|---|---|
| [`docs/`](docs/) | Canonical authored technical documentation and metadata inputs |
| [`examples/`](examples/) | Executable reference projects and local authoring instructions |
| [`implementation/`](implementation/) | Deterministic implementation inspected only after the owning contract |
| [`legacy/`](legacy/) | Retained compatibility and migration context |
| [`planning/`](planning/) | Version-scoped implementation intent and lifecycle history |
| [`profiles/`](profiles/) | Governed machine-readable schematic, style, and execution profiles |
| [`reference/`](reference/) | Generated agent cards, routes, indexes, and reference products |
| [`release/`](release/) | Current release metadata, manifest, and archive-verification records |
| [`site/`](site/) | Generated static documentation site and compatibility redirects |
| [`tests/`](tests/) | Automated contract, governance, conformance, and regression tests |
| [`tools/`](tools/) | Build, query, authoring, validation, evaluation, and packaging commands |
| [`validation/`](validation/) | Human validation narratives, corpora, evaluations, and retained evidence |

Root build and environment controls are [`VERSION`](VERSION), [`Makefile`](Makefile), [`requirements.txt`](requirements.txt), and [`requirements-release.txt`](requirements-release.txt). Their roles are operational; they do not override canonical technical specifications.

## 9. Reference-Chain Rule

A repository reader must be able to begin at an approved root document and reach every human-authored document through explicit Markdown links or the official registry for that document role. Category indexes must link every canonical member registered in their navigation section. Root links, current-version pointers, route paths, and authority-scope ownership are validated during documentation and release checks.
