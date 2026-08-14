---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 1105
  intents:
  - author-component-circuit
  - validate-project
navigation:
  group: specifications
  order: 191
artifacts:
  owns:
  - docs/specifications/schemas/agent/aixem-agent-stage-manifest-1.schema.json
  consumes:
  - validation/agent-evals-3/cases/*/start/**
id: AIXEM-SPEC-AGENT-STAGE-001
title: Cold-Start Stage Contract 1
kind: contract
summary: Defines deterministic, fresh, target-isolated task, reference, workspace, and state roots for one live authoring attempt.
authority:
- cold-start-stage-contract
aliases:
- cold-start stage
- isolated agent workspace
- sanitized reference pack
depends_on:
- AIXEM-SPEC-AGENT-TASK-001
- AIXEM-SPEC-AGENT-RETRIEVAL-001
related:
- AIXEM-SPEC-AGENT-EXECUTOR-LIVE-001
- AIXEM-SPEC-AGENT-EVAL-INVARIANT-001
requirements:
- id: AIXEM-REQ-AGENT-LIVE-0004
  title: Deterministic fresh stage
  level: MUST
  statement: Equivalent task, route pack, incomplete start state, and attempt ID MUST produce the same task, reference-pack, start-workspace, and stage digests in a fresh stage.
  validator: agent.cold_start_stage
  verification_mode: automated
  test: tests/agent/test_cold_start_stage.py::ColdStartStageContractTests.test_all_l001_l012_stages_are_deterministic_valid_and_oracle_free
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0004.json
- id: AIXEM-REQ-AGENT-LIVE-0005
  title: Evaluator and completed target isolation
  level: MUST
  statement: A cold-start stage MUST exclude evaluator invariants, scoring metadata, prior attempts, completed target sources, and completed target renders while permitting only general route-selected reference material.
  validator: agent.cold_start_stage
  verification_mode: automated
  test: tests/agent/test_agent_evals_3.py::AgentEvaluation3CorpusTests.test_tasks_and_evaluator_manifests_are_schema_valid_and_separated
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0005.json
- id: AIXEM-REQ-AGENT-LIVE-0006
  title: Fresh filesystem isolation
  level: MUST
  statement: Stage construction MUST require an empty destination, copy without following symlinks, keep task and reference roots read-only by contract, and fail closed on traversal or symlink input.
  validator: agent.cold_start_stage
  verification_mode: automated
  test: tests/agent/test_cold_start_stage.py::ColdStartStageContractTests.test_symlinks_in_start_state_fail_closed
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0006.json
- id: AIXEM-REQ-AGENT-LIVE-0020
  title: Postflight immutable stage integrity
  level: MUST
  statement: The harness MUST digest task, reference, and stage-manifest inputs before launch, recompute them after execution, detect additions, modifications, deletions, replacements, and symlinks, and block PASS when any immutable input changed.
  validator: agent.cold_start_stage
  verification_mode: automated
  test: tests/agent/test_pre_live_readiness.py::PreLiveReadinessHardeningTests.test_task_reference_manifest_and_symlink_tampering_fail_postflight
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0020.json
---

# Cold-Start Stage Contract 1

A cold-start stage is the complete visible filesystem boundary for one retained attempt. It is derived execution material, not a new authoring authority.

> **Document ID:** `AIXEM-SPEC-AGENT-STAGE-001`  
> **Schema:** `docs/specifications/schemas/agent/aixem-agent-stage-manifest-1.schema.json`  
> **Implementation:** `implementation/agent/cold_start_stage.py`

## Directory Contract

```text
stage/
├── stage-manifest.json      derived, immutable after launch
├── task/                    visible, read-only contract
│   ├── agent-task.json
│   └── TASK.md
├── reference/               sanitized route-selected reference pack
├── workspace/               incomplete authoritative start state; writable by scope
└── state/                   initially empty; executor evidence and harness state
```

Only `workspace/` and `state/` are writable. The external agent must not modify `task/`, `reference/`, or `stage-manifest.json`.

## Reference Pack Policy

The builder includes `AGENTS.md`, route packets, route-selected canonical documents, active schemas, profiles, implementation required by the existing authoring loop, and compact route tooling. It does not copy repository-wide validation corpora, evaluator files, release evidence, previous attempts, completed solutions, credentials, or generated target render output.

General examples selected by the ordinary route are allowed. An example becomes prohibited only when it is the exact completed answer or an equivalent answer leak for the staged task.

## Target Leakage Check

Leakage detection uses path/name classes and known completed-output digests. It rejects evaluator/oracle/solution naming and any forbidden completed render digest listed by the case metadata. A valid stage records the scanned file count, zero matches, and the check result in the manifest.

## Freshness and Determinism

Each attempt is copied from the immutable corpus start state into a new empty directory. `state/` must be empty before launch. Stage validation recomputes task resolution, start-workspace digests, reference-pack digests, target leakage, and the manifest self-digest.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-LIVE-0004"></a>

### AIXEM-REQ-AGENT-LIVE-0004 — Deterministic fresh stage

**MUST.** Equivalent task, route pack, incomplete start state, and attempt ID MUST produce the same task, reference-pack, start-workspace, and stage digests in a fresh stage.

<a id="AIXEM-REQ-AGENT-LIVE-0005"></a>

### AIXEM-REQ-AGENT-LIVE-0005 — Evaluator and completed target isolation

**MUST.** A cold-start stage MUST exclude evaluator invariants, scoring metadata, prior attempts, completed target sources, and completed target renders while permitting only general route-selected reference material.

<a id="AIXEM-REQ-AGENT-LIVE-0006"></a>

### AIXEM-REQ-AGENT-LIVE-0006 — Fresh filesystem isolation

**MUST.** Stage construction MUST require an empty destination, copy without following symlinks, keep task and reference roots read-only by contract, and fail closed on traversal or symlink input.

## Validation

```bash
python tools/live_agent_authoring.py validate-stage --stage /tmp/aixem-L008
```

Validation is performed before process launch. An invalid stage is retained as `INVALID_STAGE`; it is never repaired by the executor or evaluator.


## Postflight Integrity

The preflight stage validator proves construction-time freshness. The executor additionally captures an immutable baseline for `task/**`, `reference/**`, and `stage-manifest.json` immediately before launch and compares it after process termination. Additions, modifications, deletions, manifest replacement, and newly introduced symlinks are retained as integrity errors. `state/**` remains writable evidence space and workspace changes remain governed by Change-Set 1.

<a id="AIXEM-REQ-AGENT-LIVE-0020"></a>

### AIXEM-REQ-AGENT-LIVE-0020 — Postflight immutable stage integrity

**MUST.** The harness MUST digest task, reference, and stage-manifest inputs before launch, recompute them after execution, detect additions, modifications, deletions, replacements, and symlinks, and block `PASS` when any immutable input changed.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
