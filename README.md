<div align="center">

# AIXEM

### AI-Native Schematic Authoring Reference Platform

**Semantic authority · deterministic authoring · source-bound parts · Agent-first workflows**

[![Version](https://img.shields.io/badge/version-0.5.9-111827?style=for-the-badge)](docs/releases/0.5.9.md)
[![AI Native](https://img.shields.io/badge/AI-Native-2563eb?style=for-the-badge)](AGENTS.md)
[![Docs](https://img.shields.io/badge/docs-reference-7c3aed?style=for-the-badge)](docs/index.md)

<br/>

**AIXEM defines a machine-readable authority model for schematics that an AI Agent can author, place, route, render, and review without inventing connectivity or semantic truth.**

</div>

---

## Why AIXEM?

Most schematic automation starts from graphics. AIXEM starts from **authority**.

| Principle | What it means |
|---|---|
| **Semantic-first** | Connectivity comes from explicit semantic nets and stable endpoint IDs — never visual proximity. |
| **Deterministic** | The same authoritative inputs produce reproducible authoring and rendering behavior. |
| **Source-bound** | Concrete real-world parts are tied to provenance; unresolved identities remain explicit placeholders. |
| **Agent-native** | AI Agents move from task intent to bounded guides, routes, canonical specifications, and tools. |

> **A render is not electrical truth.** AIXEM keeps structural representation, component semantics, electrical compatibility, and circuit intent as separate concerns.

---

## Architecture at a Glance

```mermaid
flowchart LR
    LIB[".aixlib.json\nComponent semantics"] --> BIND["Presentation binding"]
    SYM[".aixsym.json\nSymbol graphics"] --> BIND
    BIND --> SCH[".aixem\nEntities + semantic nets"]
    PROJ[".aixproj.json\nProject composition"] --> SCH
    SCH --> LAY[".aixlayout.json\nPlacement + routing"]
    SCH --> RENDER["Deterministic renderer"]
    LAY --> RENDER
    RENDER --> VIEW["SVG / Reference Viewer"]
    SCH --> REVIEW["Review + diagnostics"]
    LAY --> REVIEW
```

### Authority Model

| Artifact | Responsibility |
|---|---|
| `.aixlib.json` | Component identity, ports, properties, provenance, presentations |
| `.aixsym.json` | Reusable symbol geometry and visual endpoint presentation |
| `.aixem` | Schematic entities and semantic net membership |
| `.aixlayout.json` | Component placement and route geometry |
| `.aixproj.json` | Multi-sheet/project composition and digest closure |

Rendered SVG, Viewer state, task packets, diagnostics, placement suggestions, audits, and review artifacts are **derived**. They do not redefine source authority.

---

## Agent Authoring Loop

```text
Task intent
    ↓
AGENTS.md / REFERENCE.md
    ↓
docs/authoring/guides/index.md
    ↓
task-specific guide + bounded route
    ↓
canonical specification
    ↓
authoritative source edit
    ↓
render → review → refine
```

The Agent-facing guide layer covers:

`create-library-part` · `select-library-part` · `create-schematic` · `place-components` · `route-nets` · `compose-project` · `modify-existing-schematic` · `author-component-circuit` · `render-review` · `validate-project`

---

## 0.5.9 — Authoring Hardening

AIXEM 0.5.9 focuses on making AI-authored schematics **less ambiguous, more reviewable, and more deterministic** without expanding into a simulator or global auto-layout system.

- canonical `library/electronics/...` and `library/architecture/...` authoring structure;
- `datasheet-backed`, `generic-template`, and `placeholder` provenance states;
- source-bound concrete-part identity and pinout review;
- semantic component contracts with geometry-only ID clone rejection;
- deterministic `G / P / M = 2.5 / 5 / 10 mm` symbol and placement rhythm;
- read-only snap and X/Y/XY placement assistance;
- versioned `metadata.pinSemantics` for signal class, function, polarity, differential pairing, power domains, capabilities, and alternate functions;
- conservative electrical compatibility precheck;
- evidence-ranked component placement and minimal-diff modification guidance;
- bounded Agent retrieval paths across guides, routes, specifications, and tooling.

---

## Semantic Review Boundaries

AIXEM intentionally separates several different kinds of confidence rather than treating every successful render as proof of circuit correctness.

| Layer | Meaning |
|---|---|
| **Structural** | Schema, binding, geometry, grid, and deterministic rendering |
| **Part semantics** | Provenance, concrete identity, pinout/source relationship, and minimum component semantics |
| **Generic / placeholder** | Explicit generic intent or unresolved concrete identity without false certainty |
| **Circuit intent** | Whether the selected component and pins match the intended circuit role |

Electrical compatibility guidance is deliberately bounded. It does not claim voltage safety, timing correctness, simulation correctness, regulatory compliance, or production readiness.

---

## Start Here

| You are... | Start with |
|---|---|
| **AI Agent / automated contributor** | [`AGENTS.md`](AGENTS.md) → [`REFERENCE.md`](REFERENCE.md) → [`docs/authoring/guides/index.md`](docs/authoring/guides/index.md) |
| **Human evaluator** | [`START_HERE.md`](START_HERE.md) |
| **Human contributor** | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| **Reading the specification** | [`docs/index.md`](docs/index.md) |
| **Authoring reusable parts** | [`library/README.md`](library/README.md) |
| **Reading the current release** | [`docs/releases/0.5.9.md`](docs/releases/0.5.9.md) |

---

## Repository Map

```text
AIXEM/
├── AGENTS.md                 # AI Agent entrypoint
├── REFERENCE.md              # canonical repository reference map
├── docs/                     # specifications, contracts, guides, releases
├── library/                  # reusable authored component/symbol assets
├── implementation/           # reference implementation
├── tools/                    # authoring, rendering, diagnostics, release tooling
├── examples/                 # current authoring examples and fixtures
├── validation/               # conformance and engineering evidence
├── planning/                 # historical and release plans
├── release/                  # machine-readable release metadata
└── site/                     # generated documentation site
```

---

## Deliberate Boundaries

AIXEM 0.5.9 intentionally stops before:

- full ERC;
- simulation binding or solver execution;
- global automatic component placement;
- datasheet crawling or manufacturer catalog ingestion;
- universal lower-level parts taxonomy;
- Viewer editing;
- live external Agent claims.

These are explicit architectural boundaries rather than implied features.

---

<div align="center">

### AIXEM

**A deterministic schematic authority model built for AI Agents.**

<sub>Current release: 0.5.9 · 2026-08-12</sub>

</div>
