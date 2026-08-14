---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 1039
  intents:
  - validate-project
navigation:
  group: specifications
  order: 194
artifacts:
  owns:
  - docs/specifications/schemas/agent/aixem-agent-evaluation-invariant-1.schema.json
  consumes:
  - validation/agent-evals-3/cases/*/evaluator/invariants.json
id: AIXEM-SPEC-AGENT-EVAL-INVARIANT-001
title: Evaluation Invariant Contract 1
kind: contract
summary: Defines a small evaluator-only semantic predicate vocabulary that scores the actual final workspace without staging or restoring a completed answer.
authority:
- agent-evaluation-invariant-contract
aliases:
- hidden semantic invariants
- cold-start scorer
- evaluator-only predicates
depends_on:
- AIXEM-SPEC-AGENT-STAGE-001
- AIXEM-SPEC-AGENT-EXECUTION-001
related:
- AIXEM-SPEC-AGENT-LIVE-RUN-001
- AIXEM-CONF-AGENT-LIVE-001
requirements:
- id: AIXEM-REQ-AGENT-LIVE-0012
  title: Constrained semantic predicate vocabulary
  level: MUST
  statement: Evaluator-only acceptance data MUST use the declared small predicate vocabulary and MUST reject exact hidden source equality, golden-source restoration, completed-solution payloads, and arbitrary oracle file comparisons.
  validator: agent.evaluation_invariants
  verification_mode: automated
  test: tests/agent/test_invariant_scorer.py::EvaluationInvariantContractTests.test_exact_completed_source_oracle_is_prohibited
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0012.json
- id: AIXEM-REQ-AGENT-LIVE-0013
  title: Score actual final workspace without repair
  level: MUST
  statement: The evaluator MUST score the agent's actual final workspace, MUST retain failed predicates, and MUST NOT patch, restore, or replace authoritative source before scoring.
  validator: agent.evaluation_invariants
  verification_mode: automated
  test: tests/agent/test_invariant_scorer.py::EvaluationInvariantContractTests.test_scorer_checks_actual_incomplete_workspace_without_self_repair
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0013.json
- id: AIXEM-REQ-AGENT-LIVE-0014
  title: Evaluator cannot mutate authority
  level: MUST
  statement: Invariant evaluation and deterministic rendering MAY create derived outputs but MUST leave the authoritative workspace digest unchanged and MUST fail if evaluator code mutates authority.
  validator: agent.evaluation_invariants
  verification_mode: automated
  test: tests/agent/test_invariant_scorer.py::EvaluationInvariantContractTests.test_semantically_repaired_workspace_passes_hidden_invariants
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0014.json
- id: AIXEM-REQ-AGENT-LIVE-0024
  title: Agent-visible invariant basis
  level: MUST
  statement: Every required official invariant MUST declare a machine-checkable basis resolving to an agent-visible task pointer, staged canonical requirement, or staged active profile; an unresolved or non-staged basis MUST fail the fairness audit.
  validator: agent.evaluation_invariants
  verification_mode: automated
  test: tests/agent/test_pre_live_readiness.py::PreLiveReadinessHardeningTests.test_invariant_basis_rejects_missing_task_and_nonstaged_document
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0024.json
---

# Evaluation Invariant Contract 1

Evaluation Invariant Contract 1 separates task intent from staged information. The agent sees the user task and ordinary AIXEM references; the evaluator later checks a small set of semantic and conformance properties against the actual final workspace.

> **Document ID:** `AIXEM-SPEC-AGENT-EVAL-INVARIANT-001`  
> **Schema:** `docs/specifications/schemas/agent/aixem-agent-evaluation-invariant-1.schema.json`  
> **Implementation:** `implementation/agent/invariant_scorer.py`

## Allowed Predicates

- `validator-pass` — no blocking diagnostics under a declared route;
- `diagnostic-absent` — one expected defect class is gone;
- `artifact-present` — required artifact pattern exists;
- `authority-digest-unchanged` — selected baseline authorities or paths remain unchanged;
- `symbol-port-set` — exact or subset symbol endpoint identity;
- `entity-present` — semantic entity and optional component type exist;
- `local-net-members` — exact or subset local semantic net closure;
- `project-net-members` — exact or subset project-level net closure;
- `interface-binding` — leaf port/local net/project member closure;
- `render-deterministic` — production rendering is byte-stable for the declared repeats.

## Prohibited Hidden Answers

The evaluator rejects arguments such as `exactSource`, `sourceEquality`, `expectedSource`, `goldenSource`, `completedSolution`, `oracleFile`, `sourceDigestEquality`, and `byteEquality`. A predicate must express the user/spec invariant, not a concealed completed implementation.

A known-good fixture may exist elsewhere in repository history for regression, but it is not staged and is never copied over the agent's output by the evaluator.

## Scoring

Each invariant produces `PASS` or `FAIL`, evidence, and any evaluator error. Required predicates determine the attempt score; optional predicates remain visible. The evaluator snapshots the workspace before and after scoring and raises a contract error if any authoritative digest changes.

Derived `render/**` and `evidence/**` output may be regenerated for deterministic checks. These outputs are never treated as authoring authority.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-LIVE-0012"></a>

### AIXEM-REQ-AGENT-LIVE-0012 — Constrained semantic predicate vocabulary

**MUST.** Evaluator-only acceptance data MUST use the declared small predicate vocabulary and MUST reject exact hidden source equality, golden-source restoration, completed-solution payloads, and arbitrary oracle file comparisons.

<a id="AIXEM-REQ-AGENT-LIVE-0013"></a>

### AIXEM-REQ-AGENT-LIVE-0013 — Score actual final workspace without repair

**MUST.** The evaluator MUST score the agent's actual final workspace, MUST retain failed predicates, and MUST NOT patch, restore, or replace authoritative source before scoring.

<a id="AIXEM-REQ-AGENT-LIVE-0014"></a>

### AIXEM-REQ-AGENT-LIVE-0014 — Evaluator cannot mutate authority

**MUST.** Invariant evaluation and deterministic rendering MAY create derived outputs but MUST leave the authoritative workspace digest unchanged and MUST fail if evaluator code mutates authority.


## Invariant Basis

Every official L001-L012 invariant carries one or more basis records. A basis resolves to an agent-visible JSON pointer in `agent-task.json`, a requirement in a canonical document included in the staged reference pack, or a staged profile path. The fairness auditor rejects missing task pointers, non-staged documents, absent requirement IDs, and unavailable profiles. This proves legitimacy of the expectation without exposing a completed answer.

<a id="AIXEM-REQ-AGENT-LIVE-0024"></a>

### AIXEM-REQ-AGENT-LIVE-0024 — Agent-visible invariant basis

**MUST.** Every required official invariant MUST declare a machine-checkable basis resolving to an agent-visible task pointer, staged canonical requirement, or staged active profile; an unresolved or non-staged basis MUST fail the fairness audit.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
