---
id: AIXEM-START-QUICK-001
title: Quick Start
status: informative
version: '1.0'
language: en
domain: getting-started
kind: guide
summary: Builds the bundled grid-controller example, opens the Reference Viewer as the primary inspection surface, and
  verifies Workbench and renderer evidence.
authority:
- onboarding
- build-workflow
aliases:
- quick start
- build example
- run AIXEM
agent:
  priority: normal
  estimated_tokens: 1238
  intents:
  - create-schematic
  - validate-project
  - build-documentation
depends_on:
- AIXEM-START-INTRO-001
related:
- AIXEM-EXAMPLE-CONTROLLER-001
- AIXEM-CONF-VALIDATION-001
- AIXEM-SPEC-VIEWER-001
navigation:
  group: getting-started
  order: 30
artifacts:
  owns: []
  consumes:
  - examples/electronics-grid-controller/project.aixproj.json
  - implementation/schematic/render_project.py
requirements: []
---

# Quick Start

Build the bundled grid-controller example, publish the static documentation, run the conformance suite, and inspect the resulting evidence.

> **Document ID:** `AIXEM-START-QUICK-001`  
> **Status:** Informative  
> **Version:** 1.0

## Prerequisites

- Python 3.11 or newer
- A POSIX-compatible shell for the command examples
- A modern browser for the generated Reference Viewer, Review Workbench, and documentation site

The release has no database, server-side documentation runtime, remote font, or remote search dependency.

## 1. Install the pinned Python dependencies

From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Build canonical documentation products

```bash
python tools/docs/build_all.py
```

This command validates the canonical Markdown and authored metadata, then generates:

- `docs/_meta/generated/`
- `reference/`
- `site/`

Open `site/index.html` to browse the static documentation release.

## 3. Render the schematic example

```bash
python implementation/schematic/render_project.py \
  examples/electronics-grid-controller/project.aixproj.json
```

Open:

```text
examples/electronics-grid-controller/render/viewer.html
```

Use `viewer.html` for normal read-only design inspection. Open the following only when diagnostics and provenance are needed:

```text
examples/electronics-grid-controller/render/workbench.html
```

The example should report grid-aligned placement, orthogonal route geometry, explicit junction semantics, no required remote assets, and deterministic output digests.

## 4. Run repository conformance tests

```bash
python tools/docs/run_tests.py
```

The suite covers canonical metadata, links, navigation, task routes, bounded retrieval, the schematic renderer, requirement evidence, review evidence, English-only release text, and the release manifest when present.

## 5. Execute all three release passes

```bash
python tools/docs/release_pipeline.py --package
```

The release pipeline performs, records, and retries the following gates:

1. canonicalization and 0.4 migration coverage;
2. agent compiler, route corpus, and reproducibility checks;
3. static publication, screenshots, conformance evidence, manifest verification, and deterministic ZIP packaging.

## Expected outputs

| Output | Purpose |
|---|---|
| `site/index.html` | Official static documentation entrypoint |
| `site/reference-explorer.html` | Human-readable agent route catalog |
| `docs/_meta/generated/route-index.json` | Machine route-first resolver input |
| `validation/releases/<version>/final-validation.md` | Release-level validation summary |
| `release/manifest.json` | SHA-256 coverage for shipped files |
| sibling `.zip` file | Deterministic release bundle |

## Next steps

- [Create the first schematic](first-schematic.md)
- [Understand the semantic model](../concepts/semantic-model.md)
- [Read the agent retrieval rules](../agent/retrieval.md)
- [Inspect the release gates](../conformance/release-gates.md)
## Route-Bounded Agent Authoring

Use a staged workspace and an existing route/task packet. For a composite task, name the active child stage explicitly:

```bash
python tools/docs/build_all.py
python tools/agent_authoring.py prepare \
  --workspace /path/to/staged-project \
  --route author-component-circuit \
  --stage-route create-schematic \
  --task-id task-001 \
  --project project.aixproj.json

# Edit only authoritative files allowed by the emitted execution packet.
python tools/agent_authoring.py check --state-dir /path/to/staged-project/.aixem-agent/task-001
python tools/agent_authoring.py close --state-dir /path/to/staged-project/.aixem-agent/task-001
```

`check` returns normalized diagnostics, changed-file evidence, and remediation routes. `close` succeeds only after full validation and three deterministic renders, then writes the final Authoring Run Record 1. Do not edit generated render or Viewer products between prepare and close.

## Viewer Output Roles

- `viewer-model.json` is deterministic derived inspection data.
- `viewer.html` is the canonical read-only design surface.
- `workbench.html` extends the same Viewer Core with diagnostics and provenance.
- `drawing.svg` and `resolved-scene.json` remain renderer evidence.

Neither HTML product authors or saves AIXEM source files.
<a id="0-5-6-cold-start-live-agent-evaluation"></a>
## Cold-start live-agent evaluation

Use `tools/live_agent_authoring.py` to build and validate one fresh stage. Use `tools/run_agent_evals_3.py --tier-a-only` for deterministic protocol conformance. Supply `--external-executor` only for actual Tier B execution. A Tier A result never authorizes `liveExternalAgentExecuted=true`.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
