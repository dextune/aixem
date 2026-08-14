# AIXEM 0.5.8 — Pre-Live Agent Readiness Hardening Plan

**Proposed release:** 0.5.8  
**Baseline:** AIXEM 0.5.7 (2026-08-12)  
**Scope:** deterministic authoring harness reliability, cold-start stage integrity, executor process hygiene, evidence provenance, evaluator fairness, route readiness, and pre-live conformance closure  
**Circuit-format impact:** none intended  
**Renderer / Viewer impact:** none intended  
**External AI execution:** explicitly out of scope for this release  
**Primary goal:** remove deterministic platform-side ambiguity before connecting a real AI agent, so the first Tier B failures can be attributed to the agent or task rather than to an unproven execution harness.

---

## 1. Executive Summary

AIXEM 0.5.7 is already a strong pre-live baseline. The repository has a route-bounded authoring loop, structured diagnostics, write-scope enforcement, deterministic closure, cold-start stage construction, hidden-invariant scoring, live-run evidence contracts, L001-L012 cold-start tasks, and a cleaned documentation information architecture. The final 0.5.7 release reports 119/119 repository tests, Agent Evaluation 3 Tier A 12/12, historical Agent Evaluation 2 12/12, symbol/static corpus 36/36, hierarchical corpus 30/30, Reference Viewer corpus 18/18, and five complete clean verification cycles.

The remaining live claim is intentionally false. That is correct and must remain false throughout 0.5.8.

The next useful work is therefore **not to add more schematic capability** and **not to anticipate model weaknesses with speculative AI features**. It is to harden the deterministic boundary immediately below a future external agent.

The current implementation is structurally sound, but package-level review identified several issues that should be closed before the first real Tier B run:

1. the Agent Evaluation 3 runner is not fully output-location independent;
2. live evidence provenance is still tied to a 0.5.6 release constant and a fixed 2026-08-12 timestamp;
3. Tier A proves all twelve cold-start stages but the subprocess protocol fixture exercises an expected-failure path rather than a complete successful subprocess authoring path;
4. `task/`, `reference/`, and the stage manifest are declared read-only but are not postflight-verified after an executor runs;
5. timeout handling kills the immediate process but does not explicitly terminate a spawned process group;
6. stdout/stderr secret redaction exists, but the observation log can still retain unsanitized result/details strings;
7. observation coverage and actual Change-Set truth are not reconciled;
8. hidden invariants are schema-valid but do not carry machine-checkable provenance proving that each case-specific expectation comes from the task or canonical specification;
9. live-corpus tasks cover the principal mutating routes, but there is no compact route-readiness matrix proving the complete authoring route graph is executable before AI integration;
10. platform overhead metrics are not yet separated cleanly from future agent wall time.

0.5.8 should close exactly those gaps and then stop.

The result should be a **Pre-Live Readiness Gate** that says:

> AIXEM has not run an external AI agent yet, but every deterministic boundary that the external agent will depend on has been exercised through successful, failing, timeout, tamper, and evidence-retention paths using non-AI fixtures, with truthful provenance and no new circuit-authoring authority.

---

## 2. Baseline to Preserve

### 2.1 0.5.7 release baseline

Preserve the verified 0.5.7 baseline:

```text
repository tests                         119 / 119 PASS
Agent Evaluation 3 Tier A               12 / 12 PASS
Agent Evaluation 2                      12 / 12 PASS
symbol/static corpus                    36 / 36 PASS
hierarchical corpus                     30 / 30 PASS
Reference Viewer corpus                 18 / 18 PASS
clean release verification cycles        5 / 5 PASS
external Tier B executed                false
live claim authorized                   false
```

### 2.2 Existing authority model

Do not alter:

```text
.aixem            semantic authority
.aixlayout.json   placement/routing geometry authority
.aixsym.json      symbol graphics and electrical-port authority
.aixlib.json      reusable component/presentation binding authority
.aixproj.json     project composition and project-net authority
```

Generated render, Viewer, evidence, index, manifest, and report artifacts remain derived.

### 2.3 Existing authoring loop

Preserve:

```text
Task
  -> Route / Task Packet
  -> prepare
  -> authoritative source edit
  -> check
  -> structured diagnostics
  -> authority-local repair
  -> deterministic regeneration
  -> close
  -> Authoring Run Record
```

0.5.8 hardens this pipeline. It does not replace it.

### 2.4 Existing live boundary

Preserve:

```text
Agent Task Contract 1
Cold-Start Stage Contract 1
Live Executor Protocol 1
Observation Event Contract 1
Evaluation Invariant Contract 1
Live Run Evidence 1
Attempt-Set Contract 1
```

Prefer compatible amendments and stronger validators over creating new top-level contracts.

---

## 3. Deep Findings From the 0.5.7 Package

## 3.1 Agent Evaluation 3 runner has a real path-portability defect

The CLI exposes a custom results directory:

```bash
python tools/run_agent_evals_3.py --tier-a-only --results <path>
```

The default repository-local path passes. However, a package-level reproduction with a results directory outside `validation/agent-evals-3/` fails because the protocol fixture attempts:

```python
retained["path"].relative_to(CORPUS)
```

This is not a model issue. It is a harness assumption.

A real Tier B campaign will often write retained evidence to a dedicated external or temporary results root. The runner must therefore be location-independent before external execution.

**0.5.8 action:** remove implicit corpus-parent assumptions and make every emitted path relative to an explicit results/evidence root or represented as a safe normalized path object.

---

## 3.2 Live execution provenance is not yet ready for a future run

`tools/run_agent_evals_3.py` currently retains:

```text
RELEASE = AIXEM-SRP-0.5.6-2026-08-12
FIXED_TIME = 2026-08-12T00:00:00Z
```

This is acceptable for frozen deterministic 0.5.6 Tier A evidence, but it is not acceptable for a real external run performed against a later repository release.

A future Tier B attempt must distinguish at least:

```text
repositoryRelease
corpusId / corpusRevision
protocolVersion
executorDescriptorDigest
actual attempt generatedAt / startedAt / finishedAt
```

Deterministic Tier A products may retain fixed timestamps when byte reproducibility requires them. Live attempt evidence must not use a fabricated historical timestamp.

**0.5.8 action:** separate deterministic-build time from live-evidence time and separate corpus origin from current repository release identity.

---

## 3.3 Tier A does not yet prove a complete successful subprocess authoring attempt

Agent Evaluation 3 currently provides strong deterministic evidence for:

- all L001-L012 cold-start stage builds;
- stage determinism;
- task/stage/executor/evaluator/evidence schemas;
- isolated invariant scoring;
- failure retention;
- claim truthfulness.

The observable subprocess fixture runs against L008 but intentionally performs no repair. Its expected terminal status is `FAIL`.

Individual unit tests prove successful pieces, including manual semantic repair and successful `prepare/check/close`. What is missing is one deterministic non-AI subprocess flowing through the **entire live-shaped pipeline** and ending in `PASS`:

```text
fresh stage
 -> subprocess starts
 -> route is resolved
 -> authoritative edit occurs
 -> check / close run
 -> run record is produced
 -> actual final workspace is scored
 -> retained live-shaped evidence validates
 -> terminalStatus = PASS
 -> liveExternalAgentExecuted = false
```

This is a platform plumbing gap, not a reason to claim AI capability.

**0.5.8 action:** add a small deterministic scripted-fixture success matrix using `agentClass=test-fixture`.

Do not label these fixtures Tier B. Do not let them authorize a live claim.

---

## 3.4 Stage read-only roots are declared, not postflight-proven

A cold-start manifest declares:

```text
writableRoots = workspace, state
readOnlyRoots = task, reference
```

The stage is validated before execution. After execution, the runner scores the workspace and retains evidence, but it does not independently prove that the executor left these immutable inputs unchanged:

```text
task/**
reference/**
stage-manifest.json
```

A buggy coding agent could accidentally edit a reference document, task envelope, or stage manifest. Even if the final workspace is valid, that attempt must not be considered trustworthy.

**0.5.8 action:** add deterministic pre/post digests for executor-immutable stage inputs and fail the attempt when they change.

This is intentionally postflight detection, not a new filesystem sandbox.

---

## 3.5 Timeout handling should terminate the process tree, not only the parent

The live executor currently calls `process.kill()` on timeout.

Real coding agents routinely spawn child processes such as:

```text
shell
python
node
renderer
validator
git helper
model client helper
```

Killing only the parent can leave children running against the staged workspace or state directory.

**0.5.8 action:** on supported POSIX systems, launch the executor in a dedicated process session/group and terminate the complete group on timeout, with a short terminate -> kill escalation. Keep a conservative fallback on platforms without process-group support.

Do not add a general job scheduler, container runtime, cgroup manager, or distributed execution layer.

---

## 3.6 Observation evidence needs the same secret hygiene as stdout/stderr

The current live executor redacts explicit inherited secret values and common credential-like patterns from captured stdout/stderr.

Observation JSONL is validated for schema, sequence, path safety, and prohibited private-reasoning fields, but `result` and `details` may still contain sensitive strings and the retained attempt copies the observation log.

A future adapter can accidentally report CLI output or an error containing a token.

**0.5.8 action:** sanitize observation events before retention using the same explicit secret set and conservative generic secret pattern policy used for process output. Retain only the sanitized log in official evidence and record whether redaction was applied.

Do not capture full environment dumps, prompts, or private model reasoning.

---

## 3.7 Observation coverage is not reconciled with actual mutation truth

AIXEM correctly treats Change-Set 1 as the source of truth for file mutations. Observation events are supplementary.

The prior live-agent design explicitly anticipated two important conditions:

```text
observation says a file-write occurred but Change-Set has no corresponding mutation
Change-Set records a mutation but a writes-capable adapter reports no file-write event
```

The current implementation validates the observation stream independently but does not reconcile it against Change-Set evidence.

**0.5.8 action:** add a small observation-consistency audit:

- Change-Set remains authoritative;
- observation never rewrites mutation truth;
- if `writes=false`, no completeness claim is made;
- if `writes=true`, missing observed write/delete events produce an explicit observation-consistency failure or degraded-coverage status;
- observed write events with no corresponding Change-Set mutation are retained as a discrepancy;
- path normalization uses workspace-relative safe paths.

Do not build a general event-sourcing engine.

---

## 3.8 Hidden invariant legitimacy is currently review-driven rather than machine-linked

The invariant scorer intentionally uses a small predicate vocabulary and rejects hidden completed-source equality. This is correct.

However, case-specific invariant manifests do not currently carry an explicit machine-readable basis linking each hidden expectation to one of:

```text
user task fact / completion criterion
canonical normative requirement
active profile rule
```

Before a real model is judged, AIXEM should prove that the evaluator does not secretly demand a fact the agent could never infer.

**0.5.8 action:** add a lightweight evaluator-basis map for official L001-L012 invariants.

Recommended shape:

```json
{
  "invariant": "L005-NET",
  "basis": [
    {"type": "task", "pointer": "/facts/..."},
    {"type": "document", "documentId": "...", "requirementId": "..."}
  ]
}
```

The exact field layout can remain compact. The important gate is:

> Every required non-generic invariant is traceable to agent-visible task information or an agent-visible canonical rule.

Do not create a general theorem/proof system.

---

## 3.9 Reference-pack sufficiency should be proven from the staged copy itself

The reference pack intentionally contains:

- `AGENTS.md`;
- `VERSION`;
- `START_HERE.md`;
- route index and selected task packets;
- route-selected canonical documents;
- schemas;
- profiles;
- deterministic authoring/schematic implementation;
- required authoring/query tools.

The non-AI protocol fixture already exercises tools from the reference pack, which is good. 0.5.8 should strengthen this into an explicit closure test:

```text
with source-repository PYTHONPATH removed
with CWD inside the staged reference pack
using only staged task/reference/workspace/state paths
prepare/check/close can execute for the supported readiness fixtures
```

This catches accidental imports or file reads back into the source repository.

Do not duplicate the repository into the stage or over-sanitize the documentation.

---

## 3.10 Existing live cases cover the main mutating routes, not the complete authoring route graph

L001-L012 exercise:

```text
create-symbol       5 cases
create-schematic    2 cases
route-nets          2 cases
compose-project     3 cases
```

These are the major mutation authorities and are appropriate for live evaluation.

Other authoring workflow routes include:

```text
author-component-circuit   composite
route-project-nets         derived/non-authoritative stage
render-review              derived/review stage
validate-project           validation/closure stage
```

0.5.8 should **not add more L-cases simply to make a coverage percentage larger**. Instead, add a route-readiness audit proving that every authoring route is one of:

- directly represented by an existing L-case;
- a composite whose child transitions are tested;
- a non-authoritative generation/review/validation stage exercised by deterministic harness fixtures.

This keeps the live corpus focused and avoids artificial expansion.

---

## 3.11 Platform overhead should be baselined before model time is introduced

The prior live-agent plan recommended recording stage materialization, reference size, validator/render/close durations, event counts, and changed-file counts. Current results retain some execution duration and structural counts but do not provide a clean platform-only baseline for the complete future live path.

Before an external AI is connected, measure only deterministic infrastructure overhead:

```text
stage build duration
stage validation duration
reference-pack files / bytes
workspace files / bytes
prepare duration
check duration
close duration
render duration inside closure
evaluator duration
evidence-retention duration
observation events / bytes
changed authoritative files
```

The purpose is diagnosis, not optimization.

Do not change algorithms merely to improve these numbers unless a clear pathological regression is found.

---

## 3.12 Some isolation remains intentionally environmental

AIXEM's current stage model is a fresh-copy data-isolation model. `networkPolicy` can be descriptor-only, adapter-enforced, or external-sandbox. The generic executor is not a container sandbox.

0.5.8 must not create a container orchestration or OS sandbox subsystem just because external agents may eventually need one.

Instead:

- make the enforcement level explicit in readiness/evidence;
- prohibit claims stronger than the actual enforcement mode;
- detect mutation of AIXEM-declared immutable stage inputs;
- terminate the process tree on timeout;
- leave whole-host filesystem/network confinement to the eventual executor environment unless real evidence later proves AIXEM must own more.

---

## 4. Design Principles for 0.5.8

### P1 — No new circuit capability

No new symbol primitive, schema field, routing behavior, hierarchy concept, component model, renderer feature, or Viewer feature is introduced.

### P2 — Harden only boundaries a real agent will immediately depend on

Every change must answer:

> Could this deterministic defect make the first external-agent result misleading, unreproducible, unsafe, or impossible to attribute?

If not, defer it.

### P3 — Test fixtures are not AI evidence

Scripted subprocess fixtures remain `agentClass=test-fixture` and can never set `liveExternalAgentExecuted=true`.

### P4 — Successful and failing plumbing must both be proven

A trustworthy harness must prove:

```text
PASS
FAIL
TIMEOUT
EXECUTOR_ERROR
INVALID_STAGE / integrity failure
```

without fabricating any live claim.

### P5 — Change-Set is mutation truth

Observation is useful telemetry, never authority.

### P6 — Live evidence uses real provenance

Deterministic generated products may use a fixed build timestamp. Actual external execution evidence may not.

### P7 — Do not pre-optimize the agent experience

Repair hints, semantic diffs, context reduction, adapter UX, and prompt specialization remain evidence-gated until real Tier B data exists.

### P8 — Prefer amendments over new abstraction layers

Extend existing runner, executor, stage, evidence, and conformance code where practical. Avoid new framework layers.

---

## 5. Explicit Non-Goals

0.5.8 MUST NOT:

- execute Codex, Claude Code, OpenCode, Ollama agents, or any other real AI agent;
- claim Tier B success;
- add provider-specific SDK integration;
- add provider-specific agent adapters beyond existing non-executable templates;
- add an AIXEM editor DSL or transaction language;
- add GUI editing or AI chat to Viewer/Workbench;
- add new schematic or project format capability;
- redesign renderer or Viewer architecture;
- add automatic repair hints based on guessed LLM behavior;
- add semantic diff UI;
- add diagnostic-to-Viewer overlays;
- optimize task context based on hypothetical model usage;
- expand L001-L012 merely for numerical coverage;
- add multi-agent orchestration;
- add a database, queue, service mesh, container platform, or job scheduler;
- add a mandatory OS sandbox implementation;
- benchmark model quality;
- perform electrical-design synthesis from datasheets or physics.

These remain outside the pre-live boundary.

---

## 6. Target State

After 0.5.8, the path immediately before a real agent should be:

```text
                    AIXEM 0.5.8 PRE-LIVE GATE
                              |
                              v
                   Agent Task Contract 1
                              |
                              v
                    Fresh Cold-Start Stage
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
     immutable input digest              workspace baseline
     task/reference/manifest             authoritative digest
             |                                 |
             +----------------+----------------+
                              |
                              v
                 Deterministic Fixture Process
                    (never an AI claim)
                              |
                              v
             process-group lifecycle control
                              |
                              v
                   observable event stream
                    + secret sanitation
                              |
                              v
                  authoritative Change-Set
                              |
                              v
                    prepare/check/close
                              |
                              v
                 hidden invariant scoring
                 + invariant basis audit
                              |
                              v
                 postflight stage integrity
                              |
                              v
                   retained run evidence
                              |
                              v
                PRE-LIVE READINESS = PASS
                              |
                              v
              external AI integration may begin
```

---

## 7. Phase 0 — Freeze the Exact 0.5.7 Baseline

1. Start from the released 0.5.7 archive.
2. Verify archive SHA-256 and release manifest.
3. Record 0.5.7 protected technical hashes.
4. Record all agent contract/schema digests.
5. Record current L001-L012 task, stage, and invariant digests.
6. Record 119/119 repository tests and all inherited corpus results.
7. Record five 0.5.7 verification passes.
8. Record:

```text
externalTierBExecuted = false
liveExternalAgentExecuted = false
liveClaimAuthorized = false
```

9. Reproduce and retain the custom-`--results` path failure as a 0.5.8 regression fixture before fixing it.
10. Record current default Tier A result as a protected behavioral baseline.

**Exit criterion:** 0.5.8 has exact evidence of the healthy 0.5.7 baseline and the specific pre-live defects it intends to close.

---

## 8. Phase 1 — Fix Runner Portability and Evidence Provenance

### 8.1 Results-root independence

Refactor `tools/run_agent_evals_3.py` so:

- `--results` may point to any writable safe directory;
- `--work` may point to any writable safe directory;
- emitted retained-evidence paths are relative to the declared results root, not an implicit corpus root;
- no output path relies on `relative_to(CORPUS)` unless the path has first been proven to belong there;
- default paths remain backward compatible.

Add tests for:

```text
default repository results root
external temporary results root
external temporary work root
both external simultaneously
paths containing spaces
non-writable / invalid destination -> clear fail-closed error
```

### 8.2 Separate identities

Distinguish:

```text
repositoryRelease
corpusId
corpusRevision / baselineRelease
protocolVersion
```

Do not rewrite historical 0.5.6 evidence.

### 8.3 Deterministic clock versus live clock

Use:

- fixed timestamp only for deterministic Tier A generated artifacts;
- actual UTC timestamp for any future Tier B attempt/evidence;
- monotonic clock for durations.

The runner must be testable with an injected clock so unit tests remain deterministic.

### 8.4 No fabricated live time

A Tier B path invoked in the future must never publish `2026-08-12T00:00:00Z` merely because the harness was introduced on that date.

**Exit criterion:** the evaluation runner is relocatable and provenance-correct before any external agent is launched.

---

## 9. Phase 2 — Add Stage Postflight Integrity

### 9.1 Immutable-stage baseline

At stage build time retain digests for:

```text
task/**
reference/**
stage-manifest.json
```

The manifest already has sufficient information for much of this; avoid duplicating large inventories unnecessarily.

### 9.2 Post-execution verification

After the executor terminates and before a PASS can be built:

- recalculate task/reference/manifest integrity;
- detect add/modify/delete under immutable roots;
- detect symlink introduction;
- detect manifest replacement;
- report a stable integrity result.

### 9.3 State remains writable

Do not reject expected executor output under:

```text
state/**
```

as long as it conforms to retained evidence contracts.

### 9.4 Workspace mutation remains governed by Change-Set

Postflight integrity does not replace route scope or Change-Set validation.

### 9.5 Failure semantics

If immutable input changes:

```text
terminal result cannot be PASS
live claim cannot be authorized
tamper/integrity evidence must be retained
workspace may still be scored for diagnostic purposes
```

Avoid creating a new terminal-status explosion. Prefer a structured integrity failure inside existing `FAIL` or `INVALID_STAGE` semantics unless a contract review proves a new status is necessary.

**Exit criterion:** an executor cannot silently change the task or its reference authority and still obtain a successful retained attempt.

---

## 10. Phase 3 — Harden Subprocess Lifecycle and Evidence Secret Hygiene

### 10.1 Process-group lifecycle

On POSIX:

1. start the executor in a new session/process group;
2. on timeout, send a graceful termination to the group;
3. wait a short bounded grace interval;
4. kill the full group if still alive;
5. retain timeout status and exit evidence.

On unsupported platforms, retain a documented conservative fallback.

### 10.2 Child-process regression fixture

Add a deterministic fixture that:

- spawns a child process;
- waits beyond the timeout;
- writes a canary only if it survives;
- proves no child remains after timeout handling.

Keep the fixture local to tests.

### 10.3 Observation sanitization

Before official retention:

- sanitize `result` and nested `details` strings;
- replace explicit inherited secret values;
- replace conservative generic credential patterns;
- preserve schema shape and sequence;
- record redaction count / applied flag;
- never retain the unsanitized copy in official evidence output.

### 10.4 Evidence scans

Add a final evidence-secret scan across:

```text
live-run-evidence.json
observation-log.jsonl
retained stdout/stderr fields
executor descriptor copy
attempt-set summary
```

Do not scan arbitrary binary circuit files for generic strings unless a concrete risk justifies it.

### 10.5 Output limit semantics

Clarify that `outputBytes` is the maximum **retained/captured evidence bytes** per stream unless implementation is upgraded to enforce emitted-process quota.

Do not silently claim disk-output enforcement that does not exist.

If a bounded streaming implementation can be added with small complexity, it may be used; otherwise correct the contract language and retain strict evidence-size truncation.

**Exit criterion:** timeouts do not leave executor children active, and retained executor/observation evidence is credential-safe under the declared policy.

---

## 11. Phase 4 — Reconcile Observation With Change-Set Truth

### 11.1 Add consistency evaluation

For adapters declaring `writes=true`:

- compare normalized observed `file-write` / `file-delete` targets with Change-Set paths;
- categorize exact match, missing observation, extra observation, and unsupported path.

For `writes=false`:

- do not treat absent write events as a failure;
- state that write observation is unavailable.

### 11.2 Change-Set wins

Never alter the Change-Set based on observation events.

### 11.3 Consistency result

Retain a compact result such as:

```text
coverageDeclared
changedPaths
observedWritePaths
missingObservedWrites
unmatchedObservedWrites
consistent
```

### 11.4 Negative fixtures

Add cases where:

1. event says write, workspace unchanged;
2. workspace changes, no write event despite `writes=true`;
3. workspace changes, `writes=false`;
4. delete event targets unsafe path;
5. duplicate write events occur;
6. write then revert results in no final Change-Set mutation.

The last case should not be treated as an authoritative final mutation merely because an event existed.

**Exit criterion:** observation completeness is measured honestly without turning telemetry into authority.

---

## 12. Phase 5 — Add a Deterministic Subprocess Readiness Matrix

This is the most important pre-live addition.

### 12.1 Purpose

Prove that the live-shaped subprocess boundary can successfully execute the existing authoring loop before an AI is introduced.

### 12.2 Do not create fake AI

Every fixture descriptor uses:

```text
agentClass = test-fixture
liveExternalAgentExecuted = false
claimEligible = false for live-agent claims
```

### 12.3 Small representative success matrix

Use a minimal authority-complete set rather than twelve scripted solutions solely for coverage.

Recommended four success fixtures:

| Fixture | Existing route | Authority exercised | Purpose |
|---|---|---|---|
| R001 | `create-symbol` | symbol / library | subprocess performs a valid symbol-local repair and closes |
| R002 | `create-schematic` | semantic | subprocess performs a valid semantic repair and closes |
| R003 | `route-nets` | layout | subprocess performs a valid orthogonal/grid repair and closes |
| R004 | `compose-project` | project | subprocess performs a valid project-net repair and closes |

Prefer reuse/adaptation of L008-L011 start states because they already isolate one authority defect each.

### 12.4 Scripted repair source remains evaluator/test-only

The repair script or known patch:

- lives outside the staged reference pack;
- is never copied into `task/`, `reference/`, or `workspace/`;
- is never visible to a future external agent;
- exists only to prove protocol plumbing.

### 12.5 End-to-end PASS requirements

Each success fixture must prove:

```text
fresh stage valid
subprocess started
observation valid
prepare executed
one authority-local repair applied
Change-Set valid
check valid
close conformant
Authoring Run Record present
hidden invariants pass
postflight immutable roots unchanged
retained evidence validates
terminalStatus PASS
liveExternalAgentExecuted false
```

### 12.6 Fault matrix

Add a compact deterministic failure set for:

```text
no executable -> EXECUTOR_ERROR
nonzero exit -> FAIL/EXECUTOR failure behavior as defined
timeout after workspace edit -> TIMEOUT with retained changed workspace evidence
immutable task/reference edit -> integrity failure
wrong-authority edit -> FAIL
hand-edited generated output -> FAIL
zero exit but invariants fail -> FAIL
close says blocked despite executor completion -> FAIL
malformed observation -> no live claim / retained failure
secret in observation -> sanitized or rejected per policy
```

Do not duplicate every existing unit test. The matrix exists to exercise **integrated boundaries**.

### 12.7 No L-corpus expansion

Do not introduce L013-L024 for these plumbing cases. Keep L001-L012 as the live-authoring corpus.

**Exit criterion:** AIXEM proves successful and failing live-shaped subprocess flows without involving an AI model or creating false Tier B evidence.

---

## 13. Phase 6 — Prove Evaluator Fairness and Reference-Pack Sufficiency

### 13.1 Invariant basis registry

Add compact provenance for every required L001-L012 invariant.

Generic invariants may use a shared basis:

```text
validator-pass -> canonical conformance/validation authority
render-deterministic -> deterministic rendering contract
```

Case-specific invariants must identify task facts and/or canonical requirements.

### 13.2 Agent-visible basis check

For every basis:

- task pointer must exist in `agent-task.json`; or
- canonical document/requirement must resolve through the active route reference pack.

If an invariant depends on a rule not visible through the route, either:

1. correct the route/reference pack; or
2. remove/replace the unfair invariant.

Do not add a special hidden instruction file for the agent.

### 13.3 Exact-source leakage remains prohibited

Continue rejecting completed target source equality as the normal oracle.

### 13.4 Isolated reference execution

Add a test mode that executes staged authoring tools with:

```text
source repository removed from PYTHONPATH
working directory inside reference/
only stage paths supplied
```

At least the four readiness success fixtures must close in this mode.

### 13.5 Reference-pack budget audit

For each live case record:

```text
files
bytes
canonical documents
task packets
schemas/profiles/tools bytes
```

Fail only on existing route budget violations or missing dependencies. Do not optimize content merely because it can be made smaller.

**Exit criterion:** every official hidden expectation is fair, and the staged reference pack is sufficient without secretly reaching back into the source repository.

---

## 14. Phase 7 — Add Authoring Route Readiness Coverage

### 14.1 Create one generated readiness matrix

For the existing authoring workflow routes:

```text
create-symbol
create-schematic
route-nets
compose-project
route-project-nets
render-review
validate-project
author-component-circuit
```

record:

```text
route kind
write authority
existing live case coverage
readiness fixture coverage
prepare/check/close support
reference-pack closure
validator availability
expected mutation mode
status
```

### 14.2 Composite route

For `author-component-circuit` prove:

- each declared child route resolves;
- child order remains stable;
- active child scope never widens parent intent;
- non-mutating child stages do not accidentally grant source authority.

Do not create an autonomous multi-stage planner.

### 14.3 Non-authoritative stages

For `route-project-nets`, `render-review`, and `validate-project`:

- prove they can be entered through the current harness;
- prove source edits are prohibited where authority is empty;
- prove deterministic generation/review/closure behavior remains intact.

### 14.4 No route explosion

Do not create new routes for readiness fixtures.

**Exit criterion:** every existing authoring route has an explicit, defensible pre-live readiness status without expanding the task-routing model.

---

## 15. Phase 8 — Establish a Platform-Only Readiness Report

### 15.1 Add one generated report

Recommended location:

```text
validation/agent-evals-3/readiness/readiness-report.json
```

Optionally provide one human-readable version under the release validation directory.

### 15.2 Required sections

```text
repository release
corpus revision
protocol/schema digests
runner portability
stage integrity
process lifecycle
secret hygiene
observation consistency
subprocess success matrix
subprocess fault matrix
invariant fairness
reference-pack closure
route readiness
platform timing baseline
Tier B status
```

### 15.3 Platform timing baseline

Report measurements, not performance promises.

For each readiness fixture retain:

```text
stageBuildMs
stageValidateMs
prepareMs
checkMs
closeMs
evaluatorMs
evidenceRetainMs
referenceBytes
workspaceBytes
observationBytes
observationEvents
changedAuthoritativeFiles
```

### 15.4 No optimization gate unless pathological

Timing is informational unless:

- a deterministic operation hangs;
- a known bounded step exceeds an existing contractual limit;
- a new change creates an obvious order-of-magnitude regression.

Do not delay Tier B merely to chase micro-optimizations.

**Exit criterion:** before a model is added, AIXEM can quantify its own deterministic overhead and report all pre-live gates in one place.

---

## 16. Phase 9 — Documentation and AGENTS Alignment

0.5.7 already fixed documentation sprawl. 0.5.8 must preserve that discipline.

### 16.1 Do not create many new canonical docs

Preferred documentation changes:

- amend `docs/specifications/agent/live-executor-protocol.md`;
- amend `docs/specifications/agent/cold-start-stage-contract.md`;
- amend `docs/specifications/agent/live-run-evidence.md` or its existing owner;
- amend `docs/specifications/agent/observation-event-contract.md`;
- amend `docs/specifications/agent/evaluation-invariant-contract.md`;
- amend `docs/conformance/live-agent-cold-start.md`;
- amend `docs/agent/live-agent-cold-start-authoring.md`;
- add the 0.5.8 release note;
- add the version-scoped 0.5.8 implementation plan/history entry.

Create a new canonical document only if no existing owner can express the new normative rule without authority confusion.

### 16.2 AGENTS.md

Keep `AGENTS.md` bounded.

Only add concise stable rules if needed, such as:

```text
A future external executor must pass the generated pre-live readiness gate.
Immutable stage inputs are never writable authority.
Test-fixture PASS results never authorize a live-agent claim.
```

Do not append a long `0.5.8` historical section.

### 16.3 Planning location

When incorporated into the repository, store this plan as:

```text
planning/releases/0.5.8/pre-live-agent-readiness-hardening.md
```

The external handoff filename `PLAN-0.5.8-PRE-LIVE-AGENT-READINESS-HARDENING.md` is only a transfer convenience and should not return as a root repository plan file.

**Exit criterion:** canonical documentation, tooling, tests, and AGENTS describe the same pre-live boundary without reintroducing documentation duplication.

---

## 17. Phase 10 — Verification and Release Closure

Run three complete clean verification passes after all targeted hardening is complete.

### PASS 1 — Pre-Live Boundary Integrity

Focus:

> Can the harness prove its own inputs, process behavior, telemetry, and evidence without an AI model?

Required:

```text
runner external results root                     PASS
runner external work root                        PASS
repository/corpus/protocol identity              PASS
live-time provenance semantics                   PASS
cold-start determinism                           12 / 12
immutable task/reference/manifest postflight     PASS
process-group timeout cleanup                    PASS
secret sanitation                                PASS
observation schema/sequence/path validation      PASS
observation <-> Change-Set consistency           PASS
invariant-basis audit                            PASS
reference-pack isolated execution                PASS
liveExternalAgentExecuted                        false
liveClaimAuthorized                              false
```

### PASS 2 — Integrated Success and Fault Behavior

Focus:

> Does every important terminal path retain correct evidence through the real subprocess boundary?

Required:

```text
R001 create-symbol scripted success              PASS
R002 create-schematic scripted success           PASS
R003 route-nets scripted success                 PASS
R004 compose-project scripted success            PASS
expected subprocess PASS evidence                valid
EXECUTOR_ERROR fixture                           retained
FAIL fixture                                     retained
TIMEOUT fixture                                  retained
immutable-input tamper fixture                   retained + blocked
wrong-authority fixture                          retained + blocked
generated-output edit fixture                    retained + blocked
zero-exit/invariant-fail fixture                 retained + FAIL
malformed observation fixture                    retained + no live claim
all fixture liveExternalAgentExecuted            false
```

### PASS 3 — Full Regression and Packaging

Focus:

> Did pre-live hardening avoid changing AIXEM technical behavior?

Required:

```text
all repository tests                             PASS
Agent Evaluation 3 Tier A                        PASS
Agent Evaluation 2                               12 / 12
symbol/static corpus                             36 / 36
hierarchical corpus                              30 / 30
Reference Viewer corpus                          18 / 18
protected circuit/render/Viewer hashes           unchanged
route/task packet budgets                        PASS
document governance / orphan audit               PASS
requirement traceability                         PASS
site/reference deterministic build               PASS
release manifest                                 PASS
deterministic package double-build               identical
archive safety / digest audit                    PASS
external Tier B                                  NOT EXECUTED
```

Any failure must be repaired at the smallest owning layer and the affected complete pass rerun from a clean generated state.

---

## 18. Required Regression Tests to Add

At minimum add deterministic tests for:

```text
custom --results outside corpus
custom --work outside corpus
results path containing spaces
current repository release separated from corpus baseline release
actual-time provider injected for live evidence path
fixed-time provider retained for Tier A reproducibility
executor child process terminated on timeout
task file modified by executor
reference file modified by executor
stage-manifest modified by executor
symlink introduced after stage build
secret in observation result
secret nested in observation details
observed write absent from Change-Set
Change-Set write absent from writes-capable observation
write observation unavailable when writes=false
scripted subprocess success for symbol authority
scripted subprocess success for semantic authority
scripted subprocess success for layout authority
scripted subprocess success for project authority
successful fixture still liveExternalAgentExecuted=false
successful fixture cannot authorize Tier B claim
zero exit + failed invariant -> FAIL
close blocked + executor completion -> FAIL
timeout after mutation retains the actual final workspace state
invariant basis points to missing task pointer -> fail
invariant basis points to non-staged document -> fail
reference pack tool execution without source repository PYTHONPATH
all authoring routes appear exactly once in readiness matrix
```

Do not add duplicate tests when an existing unit test can be extended cleanly.

---

## 19. Acceptance Criteria

### Runner and provenance

- [ ] Agent Evaluation 3 runs successfully with results/work roots outside the repository.
- [ ] No retained path assumes membership in `validation/agent-evals-3/` unless explicitly configured there.
- [ ] Current repository release is derived from authoritative release metadata or `VERSION`.
- [ ] Corpus identity is separate from repository release identity.
- [ ] Tier A can remain deterministically timestamped.
- [ ] Future Tier B evidence uses real execution time rather than the historical fixed timestamp.

### Stage integrity

- [ ] `task/**` is postflight immutable.
- [ ] `reference/**` is postflight immutable.
- [ ] `stage-manifest.json` is postflight immutable.
- [ ] executor-introduced symlinks are detected.
- [ ] immutable-input mutation blocks PASS.
- [ ] Change-Set remains workspace mutation authority.

### Process safety

- [ ] timeout terminates the executor process group on supported POSIX systems.
- [ ] a spawned-child fixture proves no child survives timeout.
- [ ] unsupported-platform fallback behavior is explicit and tested where practical.

### Evidence hygiene

- [ ] stdout/stderr redaction remains valid.
- [ ] observation result/details are sanitized before retention.
- [ ] final retained evidence contains no fixture secret values.
- [ ] redaction application is recorded without serializing the original secret.

### Observation truth

- [ ] observed writes are reconciled with Change-Set when writes coverage is declared.
- [ ] Change-Set remains authoritative on mismatch.
- [ ] missing observation capability is reported as unavailable coverage, not fabricated completeness.

### Deterministic subprocess readiness

- [ ] at least four authority-representative scripted subprocess attempts end in valid `PASS` evidence.
- [ ] all scripted fixtures remain `test-fixture`.
- [ ] every scripted fixture keeps `liveExternalAgentExecuted=false`.
- [ ] PASS/FAIL/TIMEOUT/EXECUTOR_ERROR and integrity-failure paths are integrated and retained.

### Evaluator fairness

- [ ] every required L001-L012 case-specific invariant has a task/spec/profile basis.
- [ ] every document/requirement basis is available through the agent-visible reference pack.
- [ ] no completed target source is added.
- [ ] evaluator cannot silently repair the workspace.

### Reference pack

- [ ] representative prepare/check/close flows execute using staged reference files without source-repository import fallback.
- [ ] route budgets remain within existing limits.
- [ ] no special simplified agent-only rulebook bypasses normal AIXEM routing.

### Route readiness

- [ ] all existing authoring routes have one explicit readiness status.
- [ ] mutating routes map to live cases and/or success fixtures.
- [ ] non-authoritative routes do not grant source write authority.
- [ ] composite child-route resolution is verified.
- [ ] no new route is created solely for readiness tests.

### Regression and release

- [ ] all 0.5.7 technical regressions remain green.
- [ ] protected circuit/render/Viewer hashes remain unchanged.
- [ ] document governance remains green.
- [ ] three complete clean verification passes succeed.
- [ ] final archive is deterministic and independently verified.
- [ ] external Tier B remains explicitly unexecuted.
- [ ] live-agent success remains explicitly unclaimed.

---

## 20. Priorities

## P0 — Implement in 0.5.8

1. runner output/work-root portability;
2. repository/corpus/protocol provenance separation;
3. real-time semantics for future live evidence;
4. immutable task/reference/manifest postflight verification;
5. process-group timeout cleanup;
6. observation secret sanitation;
7. observation/Change-Set consistency audit;
8. four-route deterministic subprocess success matrix;
9. integrated failure/timeout/tamper matrix;
10. invariant basis/provenance audit;
11. isolated reference-pack execution proof;
12. authoring route readiness matrix;
13. platform-only readiness/timing report;
14. documentation/traceability updates;
15. three complete verification passes and deterministic packaging.

## P1 — Defer until actual Tier B data exists

Do **not** implement in 0.5.8:

1. deterministic repair hints for agents;
2. semantic diff summaries for model consumption;
3. diagnostic-to-Viewer object links;
4. route-context reduction/optimization;
5. provider-specific adapter examples beyond what is strictly necessary to connect the first real executor later;
6. new task prompt templates based on hypothetical failures;
7. visual diagnostic overlays;
8. minimal-change scoring;
9. live corpus expansion.

These should be selected from measured Tier B failures, not prediction.

## P2 — Separate architecture decision

Keep outside 0.5.8:

```text
structured editor / transaction command language
GUI editor
agent session manager
multi-agent planner
container execution platform
remote execution service
database-backed evidence service
```

Open these only if real evidence proves the current file-based authoring model is the dominant bottleneck.

---

## 21. Definition of Done

AIXEM 0.5.8 is complete when the repository can prove, **without executing a real AI agent**, the following chain:

```text
AIXEM 0.5.7 baseline preserved
        ↓
portable Agent Evaluation 3 runner
        ↓
truthful repository/corpus/protocol provenance
        ↓
fresh deterministic cold-start stage
        ↓
agent-visible task/reference frozen by postflight digest
        ↓
non-AI subprocess fixture executes
        ↓
process tree bounded and cleaned on timeout
        ↓
observable events validated and sanitized
        ↓
actual Change-Set remains mutation truth
        ↓
prepare/check/close completes or fails truthfully
        ↓
hidden invariants are fair and traceable
        ↓
actual final workspace is scored
        ↓
retained evidence validates
        ↓
PASS/FAIL/TIMEOUT/ERROR/tamper paths proven
        ↓
all fixture live-agent flags remain false
        ↓
full 0.5.7 regression remains unchanged
        ↓
PRE-LIVE READINESS GATE = PASS
```

and when:

```text
externalTierBExecuted = false
liveExternalAgentExecuted = false
liveClaimAuthorized = false
preLiveReadiness = true
```

The 0.5.8 quality bar is:

> **Before AIXEM asks whether an AI agent can author a circuit correctly, AIXEM must first prove that its own cold-start stage, route authority, subprocess lifecycle, evidence capture, evaluator, and closure pipeline behave correctly on both successful and failing executions. 0.5.8 makes that deterministic platform-side proof complete without predicting model behavior or expanding the circuit product.**

---

## 22. Handoff to the First Real AI Agent

Only after 0.5.8 passes should the first Tier B integration begin.

The first external-agent experiment should then be deliberately boring:

```text
one named executor profile
one explicit descriptor
one or a few representative L-cases first
fresh stage every attempt
all attempts retained
no prompt/harness tuning during the declared attempt set
```

After those first real results exist, classify failures into:

```text
agent reasoning/retrieval failure
task ambiguity
route/document insufficiency
diagnostic insufficiency
direct-file editing failure
executor integration failure
platform defect
```

Only then should AIXEM decide whether any previously deferred P1 feature is justified.

This preserves the correct engineering order:

```text
0.5.7  documentation/governance stability
   ↓
0.5.8  deterministic pre-live platform readiness
   ↓
Tier B  first real external-agent evidence
   ↓
measured failure analysis
   ↓
only evidence-justified reliability improvements
```
