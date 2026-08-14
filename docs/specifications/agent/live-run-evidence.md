---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 1091
  intents:
  - validate-project
navigation:
  group: specifications
  order: 195
artifacts:
  owns:
  - docs/specifications/schemas/agent/aixem-agent-live-run-1.schema.json
  - docs/specifications/schemas/agent/aixem-agent-attempt-set-1.schema.json
  consumes:
  - docs/specifications/schemas/agent/aixem-agent-run-record-1.schema.json
id: AIXEM-SPEC-AGENT-LIVE-RUN-001
title: Live Run Evidence 1
kind: contract
summary: Binds task, stage, executor, observation, authoring record, evaluator result, terminal status, and attempt-set denominator into truthful retained evidence.
authority:
- agent-live-run-evidence
aliases:
- live attempt evidence
- retained attempt set
- denominator integrity
depends_on:
- AIXEM-SPEC-AGENT-EXECUTOR-LIVE-001
- AIXEM-SPEC-AGENT-EVAL-INVARIANT-001
- AIXEM-SPEC-AGENT-RUN-001
related:
- AIXEM-CONF-AGENT-LIVE-001
requirements:
- id: AIXEM-REQ-AGENT-LIVE-0015
  title: Digest-bound terminal evidence
  level: MUST
  statement: One live attempt MUST bind task, stage, executor, observation, authoring run record, evaluator result, stage validation, terminal status, and self-digest in an immutable evidence object.
  validator: agent.live_run
  verification_mode: automated
  test: tests/agent/test_live_run_evidence.py::LiveRunEvidenceContractTests.test_evidence_digest_tampering_is_detected
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0015.json
- id: AIXEM-REQ-AGENT-LIVE-0016
  title: Denominator integrity
  level: MUST
  statement: Attempt aggregation MUST require the exact declared attempt IDs, reject duplicates or omissions, and retain PASS, FAIL, TIMEOUT, EXECUTOR_ERROR, and INVALID_STAGE results in the denominator.
  validator: agent.live_run
  verification_mode: automated
  test: tests/agent/test_live_run_evidence.py::LiveRunEvidenceContractTests.test_failed_or_non_live_attempt_remains_in_denominator
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0016.json
- id: AIXEM-REQ-AGENT-LIVE-0017
  title: Truthful live claim gate
  level: MUST
  statement: A live-agent claim MUST require actual external-AI process proof, valid observation evidence, retained terminal evidence, and denominator integrity; deterministic fixtures and protocol-only runs MUST NOT authorize the claim.
  validator: agent.live_run
  verification_mode: automated
  test: tests/agent/test_live_run_evidence.py::LiveRunEvidenceContractTests.test_live_pass_requires_evaluation_and_conformant_authoring_record
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0017.json
- id: AIXEM-REQ-AGENT-LIVE-0026
  title: Portable and truthful execution provenance
  level: MUST
  statement: Retained attempt evidence MUST separate current repository release, corpus identity and revision, corpus baseline release, and protocol version; deterministic Tier A may use a fixed clock while actual Tier B evidence MUST use actual UTC execution time and results paths MUST be independent of the corpus location.
  validator: agent.live_run
  verification_mode: automated
  test: tests/agent/test_pre_live_readiness.py::PreLiveReadinessHardeningTests.test_repository_corpus_protocol_identity_and_clock_modes_are_separate
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0026.json
---

# Live Run Evidence 1

Live Run Evidence 1 is the immutable, digest-addressed record for one cold-start attempt. It does not claim that the model is correct; it records exactly what was launched, observed, retained, and scored.

> **Document ID:** `AIXEM-SPEC-AGENT-LIVE-RUN-001`  
> **Schemas:** `aixem-agent-live-run-1.schema.json`, `aixem-agent-attempt-set-1.schema.json`  
> **Implementation:** `implementation/agent/live_run.py`

## Terminal Status

```text
INVALID_STAGE    stage contract failed before launch
EXECUTOR_ERROR   process unavailable or failed to start
TIMEOUT          wall-time limit reached
FAIL             process ran, but final workspace or closed-loop evidence failed
PASS             evaluator passed and Authoring Run Record 1 closed conformantly
```

A zero executor return code is not enough for `PASS`. A `PASS` requires both hidden invariant success and a conformant closed authoring record. The evaluator does not repair a failed attempt.

## Bound Evidence

The evidence records content digests and identities for:

- task and stage manifest;
- executor descriptor and executable proof;
- observation stream and declared coverage;
- Authoring Run Record 1 when produced;
- evaluator result and invariant summary;
- stage validation;
- exact terminal state and claim eligibility.

The self-digest covers every field except the digest itself. Tampering invalidates the evidence.

## Claim Eligibility

`liveExternalAgentExecuted` comes from Live Executor Protocol 1. `claimEligible` additionally requires a retained terminal live attempt. Protocol fixtures always remain false. The attempt set authorizes an aggregate claim only when at least one live attempt exists and the exact expected denominator is present.

A failure or timeout remains reportable evidence. It is not discarded to improve a score.

## Attempt Set

Attempt Set 1 requires exact expected attempt IDs. It rejects missing IDs, unexpected IDs, and duplicate IDs. Its summary counts live attempts, passes, failures, timeouts, executor errors, and invalid stages.

The claim text names the executor profile and exact numerator/denominator. It does not generalize to arbitrary circuits, arbitrary models, or untested configurations.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-LIVE-0015"></a>

### AIXEM-REQ-AGENT-LIVE-0015 — Digest-bound terminal evidence

**MUST.** One live attempt MUST bind task, stage, executor, observation, authoring run record, evaluator result, stage validation, terminal status, and self-digest in an immutable evidence object.

<a id="AIXEM-REQ-AGENT-LIVE-0016"></a>

### AIXEM-REQ-AGENT-LIVE-0016 — Denominator integrity

**MUST.** Attempt aggregation MUST require the exact declared attempt IDs, reject duplicates or omissions, and retain PASS, FAIL, TIMEOUT, EXECUTOR_ERROR, and INVALID_STAGE results in the denominator.

<a id="AIXEM-REQ-AGENT-LIVE-0017"></a>

### AIXEM-REQ-AGENT-LIVE-0017 — Truthful live claim gate

**MUST.** A live-agent claim MUST require actual external-AI process proof, valid observation evidence, retained terminal evidence, and denominator integrity; deterministic fixtures and protocol-only runs MUST NOT authorize the claim.


## Provenance and Clock Modes

Attempt evidence separates the current repository release from the Agent Evaluation corpus ID, corpus revision, historical baseline release, and protocol version. Deterministic Tier A generation may retain the fixed build clock needed for reproducibility. Any future external Tier B path uses actual UTC attempt timestamps and monotonic duration measurement. Results and work roots are explicit, writable destinations and retained paths are normalized relative to the declared results root rather than the corpus directory.

<a id="AIXEM-REQ-AGENT-LIVE-0026"></a>

### AIXEM-REQ-AGENT-LIVE-0026 — Portable and truthful execution provenance

**MUST.** Retained attempt evidence MUST separate current repository release, corpus identity and revision, corpus baseline release, and protocol version; deterministic Tier A MAY use a fixed clock while actual Tier B evidence MUST use actual UTC execution time and results paths MUST be independent of the corpus location.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
