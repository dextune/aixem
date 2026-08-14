# AGENTS.md — AIXEM Repository Operating Contract

This is the mandatory preflight for AI agents and automated contributors. It defines only repository-wide rules. Use [`REFERENCE.md`](REFERENCE.md) for category navigation and follow the selected canonical route for technical detail.

## 1. Startup Sequence

1. Read this file and `VERSION`.
2. Open [`REFERENCE.md`](REFERENCE.md) and choose the relevant category.
3. Resolve the task with `python tools/docs/query_route.py "<intent>"` or `docs/_meta/generated/route-index.json`.
4. Load the matching generated task packet.
5. Read only the canonical documents and sections named by the route.
6. Confirm authoritative source, route write scope, and prohibited derived paths.
7. Run the narrow validator first; run release validation before publication.

maximum documents: **7**; maximum bytes: **96 KiB**; maximum reference depth: **3** per simple route or composite child stage. Load packets from [`docs/_meta/generated/task-packets/`](docs/_meta/generated/task-packets/). Escalate only for an unresolved dependency, authority conflict, or validator-directed owner, and record the reason.

## 2. Category Router

| Task area | Follow this reference chain |
|---|---|
| Schematic, symbol, routing, or project authoring | [`Canonical Documentation Categories`](REFERENCE.md#2-canonical-documentation-categories) -> selected task route |
| File format, authority, schema, or protocol | [`Artifact and Specification Ownership`](REFERENCE.md#4-artifact-and-specification-ownership) -> [`Machine-Readable Reference Indexes`](REFERENCE.md#5-machine-readable-reference-indexes) |
| Agent execution, retrieval, repair, or evaluation | [`Task and Agent Retrieval`](REFERENCE.md#3-task-and-agent-retrieval) -> agent category and task packet |
| Validation, evidence, or publication | [`Validation, Evidence, and Release Chain`](REFERENCE.md#6-validation-evidence-and-release-chain) |
| Governance, planning, compatibility, or history | [`Plans, History, and Compatibility`](REFERENCE.md#7-plans-history-and-compatibility) |
| Repository structure, tools, tests, or generated areas | [`Repository Structure and Build Controls`](REFERENCE.md#8-repository-structure-and-build-controls) |

## 3. Authority and Claim Precedence

When sources disagree:

1. normative canonical specification or contract;
2. governed machine schema;
3. canonical architecture, concept, or policy;
4. agent guide, cookbook, or conformance guide;
5. example or fixture;
6. generated output or evidence;
7. implementation plan or historical report.

Plans describe intent, release notes describe change, and validation reports describe observed results. Current technical truth comes from canonical documents under `docs/`.

Artifact owners are summarized in [`REFERENCE.md#4-artifact-and-specification-ownership`](REFERENCE.md#4-artifact-and-specification-ownership). Never repair a source defect by editing SVG, HTML, Viewer output, generated indexes, reports, manifests, screenshots, or other derived artifacts.

## 4. Invariants That Apply Across Authoring Routes

- Baseline snap grid: `2.5 mm`, unless a normative profile says otherwise.
- Placement and routing remain grid aligned; signal routes are orthogonal unless explicitly excepted.
- Geometry never creates connectivity. A crossing is not a junction without semantic junction intent.
- Wire endpoints resolve to semantic ports, junctions, or declared sheet interfaces.
- Symbol lead endpoints coincide with declared electrical ports.
- Stable IDs survive presentation and canonical path changes.
- Hierarchy is `Project -> Sheet -> Layer`; a layer is not a schematic sheet.
- Same names never imply cross-sheet electrical connectivity; use declared interface summaries and explicit project-net membership.
- Project-net membership is explicit in `.aixproj.json`; `route-project-nets` cannot redefine it.

## 5. Authoring and Repair Loop

For common authoring operations, start at [`docs/authoring/guides/index.md`](docs/authoring/guides/index.md), select one task guide, and then follow its authored route and canonical references. New reusable component/symbol artifacts belong below `project-root/library/<electronics|architecture>/`; do not create ordinary reusable parts under `examples/`.

Use the active route. `author-component-circuit` is the governed composite chain for symbol, semantic, layout, review, and validation stages:

```text
prepare -> authoritative edit -> narrow check -> authority-local repair -> deterministic regenerate -> close
```

- Requested scope may narrow route authority, never widen it.
- Change-Set remains mutation truth; observation is telemetry only.
- Diagnose with stable code, authority, location, and remediation route.
- Stop on unchanged repeated failure or `A -> B -> A` oscillation and retain evidence.
- Close only after blocking diagnostics, scope violations, nondeterminism, and missing evidence are resolved.
- Viewer and Workbench remain read-only review surfaces.

Do not inspect renderer implementation code before reading the selected canonical contracts and task packet. Inspect renderer or harness source only for a reproducible implementation defect, validator-directed investigation, or an explicit implementation task, and report the escalation.

## 6. Live-Agent Evaluation Truth

A cold-start stage excludes evaluator invariants, completed targets, prior attempts, and completed renders. Retain externally observable actions only; never request or store private chain-of-thought or hidden scratchpads. Score the actual final workspace without evaluator repair.

Before an external executor is connected, `validation/agent-evals-3/results/readiness/readiness-report.json` must report `preLiveReadiness=true`. A `test-fixture` PASS proves plumbing only. A live Tier B claim requires a named external AI process and a complete valid retained attempt set. Until then, these remain false:

```text
externalTierBExecuted
liveExternalAgentExecuted
liveClaimAuthorized
```

## 7. Documentation and Reference Rules

Use [`REFERENCE.md#2-canonical-documentation-categories`](REFERENCE.md#2-canonical-documentation-categories) for category ownership and [`docs/specifications/documentation/document-governance-contract.md`](docs/specifications/documentation/document-governance-contract.md) for normative rules.

### Before Creating a Document

Answer all eight questions:

1. What repository document role will it have?
2. Which existing owner was considered?
3. Why is a new file better than extending that owner?
4. Which official navigation, index, suite descriptor, or registry will expose it?
5. What is its lifecycle and release scope?
6. Does its path and filename satisfy the role rule?
7. Does it need canonical identity, or is it noncanonical history/evidence?
8. Which validator proves it is classified, linked, and discoverable?

Do not invent document roles, authority, requirements, identifiers, or release claims. Unknown-role Markdown fails closed. Canonical path moves preserve document ID and require the path-migration registry. Category indexes must link every registered member. Root entrypoints and current-release pointers must remain coherent with `VERSION`.

## 8. Generated Files and Validation

Do not hand-maintain:

```text
docs/_meta/generated/
reference/
site/
render output
Viewer bundles
release manifests
verification summaries
```

Change the owner or generator, rebuild, and verify deterministic output.

Core documentation checks:

```bash
python tools/docs/audit_repository_docs.py
python tools/docs/validate_docs.py
python tools/docs/build_all.py
python tools/docs/run_tests.py
```

Release-bound changes also run the versioned repository test, complete repeated verification, manifest verification, deterministic packaging, and independent archive audit.

## 9. Final Change Report

Report:

- selected route and canonical owners;
- authoritative files changed;
- generated products rebuilt;
- validators and exact commands run;
- migrations or compatibility effects;
- unresolved diagnostics or explicitly unexecuted capability claims.
