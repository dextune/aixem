# AIXEM 0.5.6 — Live-Agent Cold-Start Authoring Plan

**Target release:** AIXEM 0.5.6  
**Baseline:** AIXEM 0.5.5 (2026-08-11)  
**Plan status:** Implementation-ready; actual external-agent evidence is an explicit release gate  
**Primary objective:** Prove, with truthful retained evidence, how a real external AI agent uses the existing route-bounded AIXEM authoring loop from a fresh incomplete workspace without seeing a completed target or becoming a second circuit authority.  
**Documentation language:** English only.

---

## 1. Executive Summary

AIXEM 0.5.5 proves that the authoring loop itself is deterministic and authority-aware. It provides stable diagnostics, objective before/after change sets, route-owned write scopes, `prepare/check/close`, deterministic rendering, Viewer evidence, and Agent Evaluation 2 Tier A replay.

The remaining evidence gap is **live cold-start execution**. AIXEM must prove what an external agent was given, what process actually ran, what observable actions occurred, which authoritative files changed, whether the existing closure pipeline passed, whether task-specific semantic intent was satisfied, and how every attempt contributed to the reported denominator.

The 0.5.6 quality bar is:

> AIXEM no longer proves only that an idealized repair harness can close a schematic. It proves, under a controlled cold-start stage, what a real external AI agent was given, what it actually changed, which AIXEM routes and diagnostics governed the work, whether the final design truly closed, and exactly how often that live agent succeeded—without exposing a completed answer or inventing a second circuit authority.

## 2. Baseline Assessment

The 0.5.5 baseline already supplies:

- canonical route-first agent retrieval;
- authoritative `.aixem`, `.aixsym.json`, `.aixlib.json`, `.aixlayout.json`, and `.aixproj.json` formats;
- Diagnostic Contract 1;
- Authoring Change-Set Contract 1;
- Authoring Execution Contract 1;
- Authoring Run Record 1;
- deterministic render, resolved evidence, SVG, Viewer Model, Reference Viewer, and Workbench outputs;
- A001-A012 deterministic Agent Evaluation 2 evidence;
- a truthful `liveExternalAgentExecuted=false` boundary when no external executor ran.

The missing pieces are a reusable task envelope, deterministic agent-visible stage, provider-neutral external process protocol, normalized observable-action evidence, evaluator-only semantic invariants, live-run evidence binding, and a genuine cold-start corpus.

## 3. Conservative Design Principles

1. Prove the current authoring surface before expanding circuit features.
2. Preserve all existing authoritative formats and renderer/Viewer contracts.
3. Treat every new live-agent artifact as non-authoritative evidence.
4. Enforce `task request != write permission`; route scope is permission.
5. Exclude completed targets, evaluator acceptance data, and prior successful attempts from the executor-visible stage.
6. Record observable behavior only; never require private chain-of-thought.
7. Score semantic invariants rather than hidden byte-identical source copies unless bytes are normatively fixed.
8. Keep provider-specific integration outside the normative core.
9. Separate stochastic live attempts from deterministic AIXEM build products.
10. Do not make a third-party model or cloud API a mandatory platform dependency.

## 4. Target Architecture

```text
Agent Task Contract 1
        ↓
Cold-Start Stage Contract 1
  task + route references + incomplete workspace
  no target solution / evaluator oracle
        ↓
Live Executor Protocol 1
        ↓
External AI agent process
        ├── observable action events
        └── authoritative workspace edits
        ↓
AIXEM 0.5.5 prepare/check/repair/close
        ↓
Authoring Run Record 1
        ↓
Evaluation Invariant Contract 1
        ↓
Live Run Evidence 1
        ↓
Agent Evaluation 3
  Tier A protocol proof / Tier B live execution
```

## 5. Normative Terminology

- **Authoring Task:** non-authoritative create/modify/repair request.
- **Cold-Start Stage:** freshly materialized agent-visible task/reference/workspace/state filesystem.
- **Reference Pack:** route-selected AIXEM documents, schemas, profiles, metadata, and tools; never a task solution.
- **Evaluator Oracle:** evaluator-private semantic acceptance data.
- **Live Executor:** declared external AI-agent subprocess.
- **Observation Event:** normalized externally observable action.
- **Live Attempt:** one task, one fresh stage, one executor invocation.
- **Live Run Evidence:** immutable object binding task, stage, executor, observations, closure record, scoring, and terminal state.
- **Platform Conformance:** correctness of AIXEM protocol mechanics.
- **Executor Result:** measured behavior of a named external runtime/configuration; it does not redefine circuit conformance.

## 6. Agent Task Contract 1

Define one schema-valid request envelope containing task identity, mode, route resolution policy, target project, supplied facts, preserved constraints, expected outputs, requested scope constraints, and completion evidence.

The resolver must:

- select a canonical route before staging;
- intersect requested writes with route-owned authority/artifact patterns;
- reject route or authority widening;
- preserve canonical validators, prohibitions, and constraints;
- emit a stable effective-scope digest.

## 7. Cold-Start Stage Contract 1

A stage contains:

```text
task/       normalized task and human-readable task text
reference/  sanitized route-selected AIXEM reference pack
workspace/  incomplete starting project only
state/      empty runtime/evidence state at materialization
```

The stage manifest records every visible/writable file, starting digests, excluded classes, route pack digest, isolation profile, bytes, and deterministic stage digest.

The builder must reject:

- unsafe relative paths or traversal;
- symlinks and external filesystem aliases;
- evaluator directories or invariant manifests;
- completed targets and completed target renders;
- prior attempt state/results;
- credentials or complete environment dumps;
- non-empty initial state roots.

Equivalent inputs must produce identical stage trees and digests.

## 8. Live Executor Protocol 1

Use a generic argv subprocess descriptor rather than a provider SDK. The descriptor declares:

- stable executor ID and label;
- `agentClass` (`external-ai` or test fixture);
- executable and argv template;
- executor/model/config identity metadata;
- working-directory and stage placeholders;
- wall-time, output-byte, and observation-event limits;
- network policy declaration;
- observation coverage capabilities;
- environment-variable names allowed for inheritance.

Execution proof must distinguish unavailable, started, completed, failed, timeout, output-limit, invalid observation, and executor error. Exit code zero never proves authoring success.

`liveExternalAgentExecuted=true` requires a real `external-ai` process, task-open evidence, at least one observable action, valid retained observation, and actual process-start proof.

## 9. Credential and Secret Boundary

Secret values must never be serialized into executor descriptors, observations, run evidence, manifests, release metadata, or reports. Only approved environment-variable names may be recorded. Captured output must redact bearer tokens, API-key patterns, JWTs, and inherited secret values without corrupting ordinary SHA-256 digests.

## 10. Observation Event Contract 1

Use canonical ordered JSONL events. P0 kinds:

```text
task-open, route-resolve, document-open, file-read, search,
command, validator, render, file-write, file-delete,
completion, executor-error
```

Require contiguous sequence numbers, safe stage-relative targets, declared kinds, normalized status, capability counts, and a canonical stream digest. The schema must reject private reasoning, chain-of-thought, scratchpad, internal monologue, and full prompt-transcript fields.

Observation coverage claims are valid only for capabilities the adapter declares complete. Actual before/after Change-Set 1 remains mutation truth even when the observation log is incomplete.

## 11. Evaluation Invariant Contract 1

Use a small deterministic predicate vocabulary, including:

- validator pass;
- diagnostic absence;
- artifact presence;
- unrelated authority digest unchanged;
- symbol port set;
- entity presence;
- local/project net membership;
- interface binding;
- deterministic final rendering.

Reject exact completed-source equality, golden-source restoration, hidden completed solution payloads, arbitrary scripts, and requirements not implied by the task or canonical specification. Score the actual final workspace. The evaluator must not mutate authority.

## 12. Live Run Evidence 1 and Attempt Set 1

One attempt binds digests for:

- task;
- stage manifest;
- executor descriptor and executable proof;
- observation stream;
- Authoring Run Record 1;
- evaluator result;
- stage validation;
- terminal status;
- evidence object itself.

Terminal statuses are `PASS`, `FAIL`, `TIMEOUT`, `EXECUTOR_ERROR`, and `INVALID_STAGE`.

Attempt aggregation must require the exact declared attempt IDs, reject duplicates/omissions, retain every terminal result, and report the complete denominator. No cherry-picking is permitted.

## 13. Agent Evaluation 3

Tier A is deterministic protocol/evaluator conformance. It proves schemas, freshness, target/oracle isolation, process mechanics, observations, scorer behavior, failed-attempt retention, and claim truthfulness. It is never live-agent success.

Tier B executes a real external AI agent against fresh cold-start stages and scores the agent's actual final workspaces. The evaluator must not restore known-good fixtures before check/close/scoring.

## 14. Live Corpus L001-L012

| ID | Case | Primary proof |
|---|---|---|
| L001 | New two-pin passive | complete route-first creation |
| L002 | Six-pin connector | pin count, pitch, total mapping |
| L003 | Twelve-pin controller | multi-pin symbol/binding discipline |
| L004 | Parameter/variant instance | documented precedence path |
| L005 | Three-terminal semantic net | junction/crossing correctness |
| L006 | Two-sheet composition | interface/project-net authoring |
| L007 | Same-name local nets | namespace isolation |
| L008 | Broken lead/port | diagnostic-driven symbol repair |
| L009 | Wrong semantic net | semantic-authority repair |
| L010 | Off-grid/non-orthogonal route | layout-authority repair |
| L011 | Duplicate project-net member | project-authority repair |
| L012 | Field/body overlap | visual-profile repair without semantic drift |

L001-L007 are creation cases; L008-L012 are repair cases. Values, IDs, nets, and placements must not be byte-identical to completed bundled examples. Tasks supply required connectivity intent; they do not test autonomous electrical invention.

## 15. Route Resolution Policy

Normal live tasks continue to use existing authoring routes. Add at most one maintenance route, `validate-live-agent-authoring`, for operating the conformance harness. Do not create one route per corpus case or an evaluation shortcut around canonical authoring routes.

## 16. Existing Closure Authority

A live result succeeds only when the existing 0.5.5 pipeline succeeds:

```text
prepare -> authoritative edits -> check -> local repairs -> close
```

Change-Set 1 remains write truth. Diagnostics remain ownership/remediation truth. Run Record 1 remains closure truth. Generated SVG, Viewer Model, HTML, manifests, and evidence must never be patched as final repairs.

## 17. Structural Negative Cases

Tests must cover invalid task/stage/executor schemas, authority widening, target/evaluator/prior-attempt leakage, serialized credentials, forged live flags, missing observation coverage, invalid sequence, output/time/event limits, path traversal, generated-output edits, hidden arbitrary requirements, evaluator mutation, zero-exit invariant failure, failed-attempt omission, duplicate/cherry-picked attempt sets, Tier A mislabeled as Tier B, and fixture restoration before live scoring.

## 18. Compatibility Policy

No changes are required to authoritative circuit schemas. Preserve Agent Diagnostic, Change-Set, Execution, and Run Record contracts, historical A001-A012 evidence, and protected renderer/Viewer/hierarchy/symbol hashes. New task/stage/executor/observation/evaluation artifacts are independently versioned evidence.

## 19. Resource Policy

Record stage/reference/workspace bytes, materialization duration, executor wall duration, captured output bytes, event count, validator/render/close durations, changed files, and repair iterations. Never reuse modified live workspaces between attempts. P0 remains file-backed and requires no database.

## 20. P0 Implementation Sequence

1. Freeze 0.5.5 truth and protected hashes.
2. Publish Agent Task Contract 1.
3. Publish Cold-Start Stage Contract 1.
4. Publish Live Executor Protocol 1.
5. Publish Observation Event Contract 1.
6. Publish Evaluation Invariant Contract 1.
7. Publish Live Run Evidence 1 and Attempt Set 1.
8. Implement deterministic stage builder and sanitized reference packs.
9. Implement generic bounded subprocess execution and secret policy.
10. Implement normalized observations and Change-Set relationship.
11. Implement constrained invariant scorer.
12. Build L001-L012.
13. Implement Tier A protocol tests.
14. Implement explicit-descriptor-only Tier B execution.
15. Retain all terminal attempts and exact denominator.
16. Execute at least one real external agent when a runtime is available.
17. Update AGENTS, retrieval, failure, validation, orchestration, schemas, routes, site, and traceability.
18. Run existing Agent Evaluation 2 and all repository/corpus regressions.
19. Execute three complete release verification cycles.
20. Package deterministically and independently verify the archive.

## 21. Three-Pass Verification Loop

### PASS 1 — Contract, Stage, and Evidence Integrity

Require schema validity, route scope precedence, deterministic fresh stages, zero completed-target/evaluator/prior-attempt leakage, safe filesystem isolation, valid evidence digests, and complete requirement ownership.

### PASS 2 — Executor, Observation, Scoring, and Claim Truth

Require bounded process behavior, secret non-serialization/redaction, no-CoT evidence, valid observation coverage, actual-workspace scoring, evaluator non-mutation, failed/timeout/error retention, exact denominator, and strict Tier A/Tier B claim separation.

### PASS 3 — Regression, Determinism, Documentation, and Packaging

Require Agent Evaluation 2 regression, all repository tests, authoring examples, symbol corpus, hierarchy corpus, Reference Viewer corpus, protected hashes, deterministic docs/site/reference generation, requirement traceability, release manifest, ZIP determinism, CRC, safe members, and one top-level directory.

Repeat the complete loop three times. Failed checks must be repaired and rerun; no unexecuted pass may be reported as complete.

## 22. Public Claim Policy

Only after actual retained Tier B execution may AIXEM state that a named executor completed a specific numerator/denominator across specific cases and attempts. Never claim arbitrary autonomous circuit design, guarantee that any LLM can author valid schematics, or describe Tier A protocol mechanics as Tier B success.

## 23. P1 Candidates After Live Evidence

Use measured live failures—not speculation—to consider repair hints, semantic diffs, diagnostic-to-Viewer links, route-context reduction, optional CLI adapter examples, better task templates, endpoint overlays, minimal-change scoring, or corpus expansion.

## 24. P2 Gate

A structured Editor/transaction-command architecture is a separate ADR. Open it only if retained live evidence proves direct file mutation is the dominant reliability bottleneck through repeated syntax, multi-file atomicity, interruption, or structural recovery failures.

## 25. Definition of Done

Full plan completion requires retained evidence for this exact chain:

```text
natural-language task
-> non-authoritative task contract
-> fresh isolated stage without target/evaluator leakage
-> actual external AI process
-> canonical route use
-> authoritative edits only
-> 0.5.5 diagnostics/change-set/repair loop
-> actual final workspace
-> check + close + deterministic render/Viewer evidence
-> hidden semantic invariant scoring
-> immutable live-run evidence
-> retained PASS/FAIL/TIMEOUT/ERROR result
```

All deterministic implementation and regression gates may pass without an available external runtime, but the full live Tier B Definition of Done remains pending until `liveExternalAgentExecuted=true` is backed by actual retained execution evidence.

## 26. Final Target State

```text
0.5.5: AIXEM deterministically proves the authoring loop itself.
0.5.6: AIXEM truthfully proves how a named real AI executor performs inside that loop from a cold start.
```
