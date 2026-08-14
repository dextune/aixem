# AIXEM Schematic Reference Platform 0.5.9

AIXEM 0.5.9 hardens AI-driven schematic authoring around canonical reusable-library placement, source-or-placeholder part integrity, versioned pin semantics, bounded electrical compatibility, deterministic placement assistance, and task-oriented Agent retrieval. It preserves the verified 0.5.8.1 file-format, Renderer, Reference Viewer, hierarchy, execution-harness, and pre-live claim boundaries.

## Root Entry Points

| Role | Entry point |
|---|---|
| Complete repository reference map | [`REFERENCE.md`](REFERENCE.md) |
| AI or automated contributor | [`AGENTS.md`](AGENTS.md) |
| Fast evaluator | [`START_HERE.md`](START_HERE.md) |
| Human contributor | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Security reporter | [`SECURITY.md`](SECURITY.md) |
| Canonical documentation | [`docs/index.md`](docs/index.md) |
| Task-oriented authoring guides | [`docs/authoring/guides/index.md`](docs/authoring/guides/index.md) |
| Reusable project library | [`library/README.md`](library/README.md) |
| Historical plans | [`planning/README.md`](planning/README.md) |
| Validation and evidence | [`validation/README.md`](validation/README.md) |
| Current release note | [`docs/releases/0.5.9.md`](docs/releases/0.5.9.md) |
| Current release verification | [`validation/releases/0.5.9/README.md`](validation/releases/0.5.9/README.md) |

## Authoring Chain

```text
README / START_HERE / AGENTS
          -> REFERENCE.md
          -> docs/authoring/guides/index.md
          -> task-specific guide and bounded route
          -> canonical specification
          -> validator, render review, and evidence
```

New reusable assets belong below `library/electronics/` or `library/architecture/`. Concrete real-world parts require source-bound provenance; otherwise unresolved concrete identity remains an explicit placeholder. Existing safe legacy library paths remain readable and repairable when explicitly referenced.

## Authority Boundary

`.aixem`, `.aixsym.json`, `.aixlib.json`, `.aixlayout.json`, and `.aixproj.json` remain authoritative in their declared layers. Documentation indexes, task packets, placement suggestions, diagnostics, render output, Viewer artifacts, review records, relationship audits, and validation evidence remain derived or evidentiary.

A render PASS is structural only. Part semantic review, pin-semantic validation, bounded compatibility, and circuit-intent review are separate results.

## Core Documentation Commands

```bash
python tools/docs/audit_repository_docs.py --require-redirects
python tools/docs/validate_docs.py
python tools/docs/build_all.py
python tools/docs/run_tests.py
```

## Full 0.5.9 Validation

```bash
python tools/run_tests_059.py
python tools/run_agent_evals_2.py
python tools/run_agent_evals_3.py --tier-a-only
python tools/validate_symbol_corpus.py --all --repeat 3 --emit-report
python tools/validate_hierarchical_corpus.py --repeats 3
python tools/validate_reference_viewer_corpus.py --repeats 3 --screenshots
python tools/verify_release_059.py --all-passes
python tools/package_release_059.py
```

## 0.5.9 Hardening Scope

- canonical singular `library/<electronics|architecture>/...` new-artifact structure;
- lower-kebab namespace and reusable library/symbol naming;
- datasheet-backed, generic-template, and placeholder provenance;
- semantic component contracts and geometry-only ID-clone rejection;
- `G/P/M = 2.5/5/10 mm` sizing and grid authority closure;
- deterministic, read-only placement snap and alignment assistance;
- versioned pin semantics and source-bound semantic review;
- conservative `PASS/WARN/ERROR/NOT_EVALUATED` compatibility precheck;
- task-oriented guides for creation, selection, placement, modification, routing, rendering, and validation;
- five consecutive clean verification passes and deterministic archive closure.

## Deliberate Non-Goals and Claim Boundary

0.5.9 does not add a full ERC engine, simulation binding or solver, global auto-layout, datasheet crawler, universal lower-level taxonomy, or Viewer editing. `externalTierBExecuted`, `liveExternalAgentExecuted`, and `liveClaimAuthorized` remain false until a named external process produces complete valid evidence.
