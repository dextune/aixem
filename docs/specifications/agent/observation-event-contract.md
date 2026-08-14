---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 1118
  intents:
  - author-component-circuit
  - validate-project
navigation:
  group: specifications
  order: 193
artifacts:
  owns:
  - docs/specifications/schemas/agent/aixem-agent-observation-event-1.schema.json
  consumes: []
id: AIXEM-SPEC-AGENT-OBSERVATION-001
title: Observation Event Contract 1
kind: contract
summary: Defines ordered JSONL evidence for externally observable agent actions while rejecting private model reasoning and chain-of-thought fields.
authority:
- agent-observation-contract
aliases:
- observable agent events
- agent action log
- no chain of thought evidence
depends_on:
- AIXEM-SPEC-AGENT-TASK-001
related:
- AIXEM-SPEC-AGENT-EXECUTOR-LIVE-001
- AIXEM-SPEC-AGENT-LIVE-RUN-001
requirements:
- id: AIXEM-REQ-AGENT-LIVE-0010
  title: Observable actions only
  level: MUST
  statement: Retained agent observation evidence MUST contain only externally observable actions and MUST reject chain-of-thought, private reasoning, scratchpad, internal monologue, and prompt-transcript fields.
  validator: agent.observation
  verification_mode: automated
  test: tests/agent/test_observation.py::ObservationEventContractTests.test_private_reasoning_fields_are_rejected
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0010.json
- id: AIXEM-REQ-AGENT-LIVE-0011
  title: Ordered digest-addressed event stream
  level: MUST
  statement: Observation events MUST use contiguous sequence numbers, safe stage-relative targets, declared event kinds, normalized capability counts, and a digest of canonical JSONL serialization.
  validator: agent.observation
  verification_mode: automated
  test: tests/agent/test_observation.py::ObservationEventContractTests.test_observable_stream_is_sequence_checked_and_digest_addressed
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0011.json
- id: AIXEM-REQ-AGENT-LIVE-0022
  title: Observation secret sanitation
  level: MUST
  statement: Observation result and nested details strings MUST be sanitized before official retention using explicit inherited-secret values and conservative credential patterns; malformed raw streams MUST NOT be retained as official evidence.
  validator: agent.observation
  verification_mode: automated
  test: tests/agent/test_pre_live_readiness.py::PreLiveReadinessHardeningTests.test_nested_observation_secrets_are_sanitized_before_retention
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0022.json
- id: AIXEM-REQ-AGENT-LIVE-0023
  title: Observation and Change-Set consistency
  level: MUST
  statement: When write coverage is declared, observed write and delete paths MUST be reconciled with Change-Set paths while Change-Set remains authoritative; unavailable coverage and discrepancies MUST be reported without inventing mutation truth.
  validator: agent.observation
  verification_mode: automated
  test: tests/agent/test_pre_live_readiness.py::PreLiveReadinessHardeningTests.test_observation_consistency_preserves_change_set_authority
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0023.json
---

# Observation Event Contract 1

Observation Event Contract 1 records what an external process visibly did, not why a model internally chose to do it.

> **Document ID:** `AIXEM-SPEC-AGENT-OBSERVATION-001`  
> **Schema:** `docs/specifications/schemas/agent/aixem-agent-observation-event-1.schema.json`  
> **Implementation:** `implementation/agent/observation.py`

## Event Stream

Events are canonical JSON objects written one per line. Sequence numbers start at one and increase without gaps. Supported kinds are:

```text
task-open       route-resolve   document-open   file-read
search          command         validator       render
file-write      file-delete     completion      executor-error
```

Optional fields identify a safe stage-relative target, route, tool, result, elapsed milliseconds, and structured observable details.

## No Private Reasoning Requirement

The schema and validator reject fields such as `chainOfThought`, `reasoning`, `privateReasoning`, `thoughts`, `scratchpad`, `internalMonologue`, and `promptTranscript`, including nested occurrences. Natural-language summaries may be retained only when they describe an observable command/result and do not expose private model reasoning.

This contract does not require an AI provider to reveal hidden reasoning. It deliberately avoids that dependency.

## Capability Coverage

An executor descriptor declares whether its adapter can observe file reads, searches, commands, writes, and route actions. The retained result records the declaration separately from observed event counts. A capability declaration does not invent an event that did not occur.

`Change-Set 1` remains the authoritative source of actual workspace mutation truth. Observation `file-write` events are useful behavioral evidence but do not replace before/after authoritative snapshots.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-LIVE-0010"></a>

### AIXEM-REQ-AGENT-LIVE-0010 — Observable actions only

**MUST.** Retained agent observation evidence MUST contain only externally observable actions and MUST reject chain-of-thought, private reasoning, scratchpad, internal monologue, and prompt-transcript fields.

<a id="AIXEM-REQ-AGENT-LIVE-0011"></a>

### AIXEM-REQ-AGENT-LIVE-0011 — Ordered digest-addressed event stream

**MUST.** Observation events MUST use contiguous sequence numbers, safe stage-relative targets, declared event kinds, normalized capability counts, and a digest of canonical JSONL serialization.

## Evidence Relationship

```text
observation-log.jsonl  behavioral evidence
Change-Set 1           mutation truth
Authoring Run Record 1 closed-loop evidence
Live Run Evidence 1    immutable attempt envelope
```


## Retention Sanitation

Observation `result` and recursively nested `details` strings are sanitized before schema validation and official retention. The sanitizer applies explicit inherited-secret values and conservative token patterns while preserving event shape and sequence. If raw JSONL is malformed, the official observation file is replaced with a safe empty stream and the parse failure remains explicit; the malformed raw secret-bearing stream is not copied into retained evidence.

## Change-Set Consistency

For adapters declaring write coverage, normalized `file-write` and `file-delete` targets are compared with final Change-Set paths. Missing observations, unmatched observations, and unsafe targets are retained as discrepancies. When write coverage is unavailable, the result says `UNAVAILABLE`; it does not claim completeness. In every case Change-Set 1 remains mutation authority.

<a id="AIXEM-REQ-AGENT-LIVE-0022"></a>

### AIXEM-REQ-AGENT-LIVE-0022 — Observation secret sanitation

**MUST.** Observation result and nested details strings MUST be sanitized before official retention using explicit inherited-secret values and conservative credential patterns; malformed raw streams MUST NOT be retained as official evidence.

<a id="AIXEM-REQ-AGENT-LIVE-0023"></a>

### AIXEM-REQ-AGENT-LIVE-0023 — Observation and Change-Set consistency

**MUST.** When write coverage is declared, observed write and delete paths MUST be reconciled with Change-Set paths while Change-Set remains authoritative; unavailable coverage and discrepancies MUST be reported without inventing mutation truth.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
