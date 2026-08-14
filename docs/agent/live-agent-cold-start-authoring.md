---
status: normative
version: '1.0'
language: en
domain: agent
agent:
  priority: critical
  estimated_tokens: 1234
  intents:
  - author-component-circuit
  - create-symbol
  - create-schematic
  - route-nets
  - compose-project
  - validate-project
navigation:
  group: agent
  order: 120
artifacts:
  owns: []
  consumes:
  - validation/agent-evals-3/**
id: AIXEM-AGENT-LIVE-COLD-START-001
title: Live-Agent Cold-Start Authoring
kind: guide
summary: Defines the operator and adapter workflow for staging, executing, observing, closing, scoring, and retaining one real external-agent authoring attempt.
authority:
- agent-live-authoring-workflow
aliases:
- live agent authoring
- cold-start authoring run
- external agent evaluation
depends_on:
- AIXEM-SPEC-AGENT-TASK-001
- AIXEM-SPEC-AGENT-STAGE-001
- AIXEM-SPEC-AGENT-EXECUTOR-LIVE-001
- AIXEM-SPEC-AGENT-OBSERVATION-001
- AIXEM-SPEC-AGENT-EVAL-INVARIANT-001
- AIXEM-SPEC-AGENT-LIVE-RUN-001
related:
- AIXEM-AGENT-AUTHORING-001
- AIXEM-CONF-AGENT-LIVE-001
requirements: []
---

# Live-Agent Cold-Start Authoring

This workflow evaluates whether an external AI agent can use the existing AIXEM route-bounded authoring loop from an incomplete state. It does not introduce a second authoring API, a hidden patcher, or a structured editor transaction language.

## End-to-End Chain

```text
natural-language task
  → Agent Task Contract 1
  → deterministic fresh stage
  → external AI subprocess
  → observable route/files/commands
  → authoritative edits only
  → agent_authoring prepare/check/repair/close
  → Authoring Run Record 1
  → evaluator-only semantic invariants
  → Live Run Evidence 1
  → exact retained attempt set
```

## Adapter Obligations

An external adapter must:

1. read `task/agent-task.json` and `task/TASK.md`;
2. begin with `reference/AGENTS.md` and the compiled active route packet;
3. write only within `workspace/` and `state/`;
4. emit ordered Observation Event Contract 1 JSONL;
5. use `tools/agent_authoring.py prepare`, `check`, and `close`, or provide equivalent observable invocation of the same contract;
6. leave failed work as-is rather than asking the evaluator to restore a fixture;
7. exit within declared limits.

The adapter may use a provider CLI, a local model runner, or another agent process. Core remains provider-neutral.

## Operator Procedure

### 1. Copy and edit the executor template

Start from `validation/agent-evals-3/executors/external-ai-template.json`. Replace command and identity fields. Keep `agentClass: external-ai` only for a genuine AI executor. Add names such as `OPENAI_API_KEY` to `inheritEnvironment` only when the adapter actually needs them; values are never placed in the descriptor.

### 2. Run Tier A first

```bash
python tools/run_agent_evals_3.py --tier-a-only
```

Tier A validates task, stage, subprocess, observation, evaluator, live-run, corpus, and deterministic stage mechanics. Its non-AI fixture intentionally does no repair and therefore produces a retained task `FAIL`; protocol conformance still passes. Tier A never authorizes a live claim.

### 3. Run actual Tier B

```bash
python tools/run_agent_evals_3.py \
  --external-executor /secure/path/executor.json \
  --attempts-per-case 3
```

The runner creates a fresh stage for every L001-L012 attempt, retains all terminal outcomes, scores the actual final workspace, and builds an exact attempt set. Do not delete failed attempts or rerun only difficult cases without declaring a new complete attempt set.

## Event Example

```json
{"schema":"https://schemas.aixem.org/agent/observation-event/1","formatVersion":"1.0","sequence":1,"kind":"task-open","target":"task/agent-task.json","result":"opened"}
{"schema":"https://schemas.aixem.org/agent/observation-event/1","formatVersion":"1.0","sequence":2,"kind":"route-resolve","route":"create-symbol","target":"reference/docs/_meta/generated/task-packets/create-symbol.json","result":"resolved"}
{"schema":"https://schemas.aixem.org/agent/observation-event/1","formatVersion":"1.0","sequence":3,"kind":"command","tool":"agent_authoring.prepare","result":"started"}
```

Do not emit private chain of thought.

## Repair Ownership

The live agent must follow diagnostics back to the owning route. A visual symptom does not grant semantic authority. `Change-Set 1` determines actual writes, and `close` blocks generated-output hand edits, scope violations, unresolved diagnostics, loop stalls, and nondeterministic render output.

## Truthful Reporting

Allowed result language names the exact executor, attempt count, cases, policy, and numerator/denominator. Do not claim arbitrary circuit autonomy, universal model reliability, or Tier B passage when only Tier A ran.

When no external executor is available, retain `tier-b-status.json` with:

```text
executed=false
attempts=0
liveExternalAgentExecuted=false
claimAuthorized=false
```


## Pre-Live Readiness Boundary

Before attaching an external AI executor, run the deterministic pre-live gate. Four `test-fixture` subprocesses must close the existing symbol, semantic, layout, and project authority paths, and the integrated fault matrix must retain executor error, failure, timeout, immutable-input tamper, wrong-authority, generated-output, invariant, close, malformed-observation, and secret cases.

A readiness PASS proves the AIXEM harness, not an AI model. The required state is:

```text
preLiveReadiness=true
externalTierBExecuted=false
liveExternalAgentExecuted=false
liveClaimAuthorized=false
```

Reference-pack fixtures execute `prepare`, `check`, and `close` from the staged `reference/` root with source-repository `PYTHONPATH` removed. Change-Set remains mutation truth, and postflight integrity must prove `task/`, `reference/`, and `stage-manifest.json` unchanged.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
