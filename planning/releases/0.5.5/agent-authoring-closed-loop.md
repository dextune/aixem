# AIXEM 0.5.5 — Agent Authoring Closed-Loop Contract Plan

**Proposed target release:** AIXEM 0.5.5 candidate  
**Plan status:** Implementation-ready  
**Baseline:** AIXEM 0.5.4 (2026-08-11)  
**Primary objective:** Convert the existing route-first AI authoring guidance, validators, renderer evidence, and Reference Viewer into a machine-readable closed authoring loop in which an agent can author or repair a schematic, receive stable diagnostics, identify the correct authority owner, make a bounded edit, and prove closure without repository-wide search or generated-output patching.  
**Compatibility objective:** Preserve all valid AIXEM 0.5.4 semantic, symbol, library, layout, project, resolved-scene, Viewer Model, SVG, Viewer, and Workbench contracts.  
**Documentation language:** English only.

---

## 1. Executive Summary

AIXEM 0.5.4 successfully closes the viewing side of the platform:

```text
Authoritative AIXEM inputs
        ↓
Production Renderer
        ↓
Resolved evidence / SVG
        ↓
Viewer Model 1
        ↓
Reference Viewer 1 / Review Workbench 1
        ↓
Browser conformance
```

The repository also already contains a strong agent-authoring knowledge system:

```text
Natural-language task
        ↓
route-index / task packet
        ↓
create-symbol
        ↓
create-schematic
        ↓
route-nets
        ↓
render-review
        ↓
validate-project
```

That architecture is correct and should not be replaced.

The next weakness is **execution closure**.

Today, an agent can be told where to read and what the correct workflow is, but validator and repair feedback is not yet normalized into a stable machine contract. Existing agent evaluations also prove route sufficiency using fixture-backed simulation; they do not yet prove that a cold-start agent can receive a task, create or repair authoritative artifacts, interpret structured failures, and converge to a valid schematic.

AIXEM 0.5.5 should therefore add a narrow machine-facing layer:

```text
                    AGENT AUTHORING TASK
                            │
                            ▼
                     Task Packet / Route
                            │
                            ▼
                 Authoritative Source Edit
                            │
                            ▼
                 Authoring Validation Runner
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
       PASS / closure              Diagnostic Set 1
                                          │
                                          ▼
                                Authority + Scope Decision
                                          │
                                          ▼
                                  Minimal Source Repair
                                          │
                                          └───────┐
                                                  ▼
                                             Revalidate
                                                  │
                                                  ▼
                                         Deterministic Render
                                                  │
                                                  ▼
                                         Authoring Run Record 1
```

The key principle is:

> **AIXEM 0.5.5 must make authoring failures machine-actionable without introducing a second circuit language, an editor, or an autonomous circuit-design engine.**

---

## 2. Review of AIXEM 0.5.4

### 2.1 What is now strong

The 0.5.4 repository contains the expected Viewer normalization architecture:

```text
implementation/schematic/viewer/
├── model.py
├── core.py
├── reference_viewer.py
├── review_workbench.py
└── templates/
```

and the corresponding normative specification family:

```text
docs/specifications/viewer/
├── reference-viewer-contract.md
├── review-workbench-contract.md
├── viewer-state-and-interaction.md
├── viewer-security-and-embedding.md
└── viewer-accessibility-profile.md
```

The derived Viewer Model schema is also present:

```text
docs/specifications/schemas/viewer/aixem-viewer-model-1.schema.json
```

The release additionally includes:

- Viewer/Workbench separation;
- V001-V018 behavioral corpus;
- Playwright browser conformance;
- qualified object identity;
- deterministic Viewer artifacts;
- offline and hostile-text security gates;
- `inspect-viewer` route;
- updated `render-review` route;
- three-pass release evidence.

This is the correct foundation for an agent platform because an agent now has a deterministic inspection surface after authoring.

### 2.2 Existing authoring route architecture is also strong

The current composite authoring path is already well chosen:

```text
author-component-circuit
  → create-symbol
  → create-schematic
  → route-nets
  → render-review
  → validate-project
```

The route system has bounded context budgets, explicit stage exits, canonical authority ownership, and generated task packets.

Do not replace this route architecture with a large orchestration framework.

### 2.3 Current authoring evaluation is not yet an actual agent-generation proof

The current `tools/docs/run_agent_evals.py` explicitly reports:

```text
executionMode = fixture-backed-route-simulation
liveExternalAgentExecuted = false
```

The eight existing evaluations are useful and should remain, but they currently validate:

- route selection;
- document budget;
- fixture conformance;
- known authority diagnosis;
- deterministic render evidence.

They do **not** yet prove:

```text
prompt
→ cold-start agent edit
→ validation failure
→ diagnostic interpretation
→ authority-local repair
→ rerender
→ final closure
```

This is the most important remaining gap for the stated product direction.

### 2.4 Diagnostics are useful but not normalized for agent repair

Existing validators commonly emit records shaped approximately as:

```json
{
  "code": "lead-port-mismatch",
  "path": "...",
  "message": "...",
  "severity": "error"
}
```

This is human-readable and testable, but a general agent still has to infer:

- which authority layer owns the defect;
- which exact object is affected;
- which JSON pointer or semantic identifier is relevant;
- which task route should be re-entered;
- which files are allowed to change;
- which generated files must not be hand-edited;
- which validators must pass after repair.

Those facts should become explicit machine-readable data.

### 2.5 There is no stable authoring change-scope evidence

AIXEM has excellent authority rules in documentation, but the execution layer does not yet emit a canonical record proving:

```text
what the agent changed
why that file was allowed to change
which authority layer owned it
whether generated outputs were touched directly
which validators were rerun
whether the repair reduced diagnostics
```

For agentic authoring this is high-value evidence.

### 2.6 Minor 0.5.4 cleanup item

`implementation/schematic/component_core.py` still contains the older standalone HTML `build_viewer()` path, while the official 0.5.4 production entrypoint is `render_project.py` with Viewer Model 1 and the normalized Viewer/Workbench renderers.

This does not invalidate the 0.5.4 release because the documented production path uses `render_project.py`, but the legacy helper creates avoidable ambiguity for future agents and maintainers.

0.5.5 should either:

1. make the legacy path explicitly internal/non-reference; or
2. route it through the normalized Viewer adapter without changing protected circuit rendering behavior.

This is cleanup only, not the main 0.5.5 objective.

---

## 3. 0.5.5 Design Principles

### 3.1 Close the loop before adding new circuit features

Do not add new symbol primitives, project features, buses, global nets, simulation, PCB, or import/export merely to make 0.5.5 appear larger.

The target is reliability of the existing authoring surface.

### 3.2 Keep authoritative formats unchanged

The following remain authoritative exactly as before:

```text
.aixem
.aixsym.json
.aixlib.json
.aixlayout.json
.aixproj.json
```

No new authoring language replaces them.

### 3.3 New agent artifacts are evidence, not circuit authority

0.5.5 may introduce derived machine-readable artifacts such as:

```text
authoring-diagnostics.json
authoring-change-set.json
authoring-run-record.json
```

These MUST NOT define circuit meaning.

They only explain and prove an authoring operation over existing authority.

### 3.4 Prefer diagnosis over automatic patch generation

P0 diagnostics should say:

```text
what failed
where it failed
who owns it
what route owns repair
what scope is allowed
what must be revalidated
```

P0 should **not** require the platform to synthesize source patches automatically.

The AI agent remains the author.

### 3.5 Every repair must be authority-local

A render defect must not be fixed by changing semantics unless semantics actually own the defect.

A semantic defect must not be hidden by moving geometry.

A generated artifact must never be hand-patched as the final fix.

### 3.6 Evaluation must test the process, not merely the final file

A valid final schematic is necessary but insufficient for agent-platform conformance.

AIXEM should also detect:

- repository-wide discovery when a route was sufficient;
- edits outside route-authorized authority;
- direct edits to generated evidence;
- unnecessary renderer source inspection;
- repeated non-improving repair loops;
- semantic changes made to repair presentation-only defects.

---

## 4. Target Architecture

```text
                         USER / AGENT TASK
                                │
                                ▼
                      Route Resolution Layer
                 route-index + task packet + budgets
                                │
                                ▼
                     Authoring Execution Contract 1
                target authority + stage + checkpoints
                                │
                                ▼
                    Existing AIXEM Authoritative Files
       .aixem / .aixsym / .aixlib / .aixlayout / .aixproj
                                │
                                ▼
                         Narrow Validators
                                │
                                ▼
                     Agent Diagnostic Contract 1
       code + authority + object + location + remediation route
                                │
                       ┌────────┴────────┐
                       │                 │
                    no errors          errors
                       │                 │
                       │                 ▼
                       │        Agent performs minimal edit
                       │                 │
                       │                 ▼
                       │          Change-Scope Check
                       │                 │
                       └────────┬────────┘
                                ▼
                       Production Renderer
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
      resolved evidence        SVG           Viewer Model 1
                                                    │
                                                    ▼
                                            Reference Viewer 1
                                │
                                ▼
                      Authoring Run Record 1
                  deterministic execution evidence
                                │
                                ▼
                    Agent Authoring Conformance
```

---

## 5. Agent Diagnostic Contract 1

Create:

```text
docs/specifications/agent/diagnostic-contract.md
```

Recommended ID:

```text
AIXEM-SPEC-AGENT-DIAGNOSTIC-001
```

### 5.1 Purpose

Normalize authoring-related validation failures into one machine-readable envelope.

### 5.2 Schema

Create:

```text
docs/specifications/schemas/agent/aixem-agent-diagnostic-1.schema.json
```

Recommended schema URI:

```text
https://schemas.aixem.org/agent/diagnostic/1
```

### 5.3 Minimum diagnostic record

Recommended shape:

```json
{
  "id": "diag-0001",
  "code": "AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH",
  "severity": "error",
  "authority": "symbol",
  "artifact": "symbols/switch.aixsym.json",
  "location": {
    "jsonPointer": "/symbol/ports/0",
    "objectKind": "symbol-port",
    "objectId": "in"
  },
  "requirement": "AIXEM-REQ-SYMBOL-DESIGN-0002",
  "remediationRoute": "create-symbol",
  "repairClass": "authoritative-source",
  "message": "Visible lead endpoint does not coincide with the electrical port.",
  "evidence": {}
}
```

### 5.4 Required fields

Every error diagnostic MUST identify, where applicable:

```text
stable code
authority owner
artifact path
structured location
requirement or rule owner
remediation route
repair class
human-readable message
```

### 5.5 Authority vocabulary

Use a controlled vocabulary such as:

```text
semantic
component-library
symbol
layout
project
project-routing
renderer
viewer
workbench
documentation
```

Authoring P0 primarily covers the first six.

### 5.6 Repair classes

Recommended controlled values:

```text
authoritative-source
binding
placement
routing
project-composition
renderer-defect
unsupported-capability
manual-review
```

### 5.7 No generated-output repair target

The diagnostic contract MUST NOT recommend direct edits to:

```text
render/*.svg
resolved-scene.json
resolved-project-scene.json
viewer-model.json
viewer.html
workbench.html
release evidence
```

If those artifacts expose a defect, the diagnostic must point upstream to the owning source or implementation layer.

---

## 6. Diagnostic Code Registry

Create:

```text
docs/conformance/agent-diagnostics.md
```

Recommended ID:

```text
AIXEM-CONF-AGENT-DIAGNOSTICS-001
```

P0 should normalize the existing high-value authoring failures first.

Recommended initial registry:

```text
AIXEM-DIAG-SCHEMA-INVALID
AIXEM-DIAG-SEMANTIC-PORT-UNKNOWN
AIXEM-DIAG-SEMANTIC-NET-ENDPOINT-UNKNOWN
AIXEM-DIAG-SEMANTIC-NET-CLOSURE
AIXEM-DIAG-COMPONENT-TYPE-UNKNOWN
AIXEM-DIAG-BINDING-PORTMAP-INCOMPLETE
AIXEM-DIAG-BINDING-PORTMAP-TARGET-UNKNOWN
AIXEM-DIAG-BINDING-ASSET-MISSING
AIXEM-DIAG-BINDING-ASSET-DIGEST
AIXEM-DIAG-SYMBOL-PORT-EXPRESSION
AIXEM-DIAG-SYMBOL-PORT-OFF-GRID
AIXEM-DIAG-SYMBOL-PORT-ORIENTATION
AIXEM-DIAG-SYMBOL-LEAD-MISSING
AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH
AIXEM-DIAG-SYMBOL-PIN-PITCH
AIXEM-DIAG-SYMBOL-FIELD-BODY-OVERLAP
AIXEM-DIAG-LAYOUT-PLACEMENT-MISSING
AIXEM-DIAG-LAYOUT-PLACEMENT-OFF-GRID
AIXEM-DIAG-ROUTE-ENDPOINT-CLOSURE
AIXEM-DIAG-ROUTE-NON-ORTHOGONAL
AIXEM-DIAG-ROUTE-VIA-OFF-GRID
AIXEM-DIAG-ROUTE-ZERO-LENGTH
AIXEM-DIAG-JUNCTION-AMBIGUOUS
AIXEM-DIAG-PROJECT-SHEET-UNKNOWN
AIXEM-DIAG-PROJECT-INTERFACE-UNKNOWN
AIXEM-DIAG-PROJECT-NET-DUPLICATE-MEMBER
AIXEM-DIAG-PROJECT-NET-MULTIPLE-OWNERSHIP
AIXEM-DIAG-PROJECT-ROUTE-NON-ORTHOGONAL
AIXEM-DIAG-RENDERER-DETERMINISM
AIXEM-DIAG-UNSUPPORTED-CAPABILITY
```

Do not attempt to normalize every possible low-level exception in the first release.

---

## 7. Authoring Change-Set Contract 1

Create:

```text
docs/specifications/agent/authoring-change-set-contract.md
```

Recommended ID:

```text
AIXEM-SPEC-AGENT-CHANGESET-001
```

Schema:

```text
docs/specifications/schemas/agent/aixem-agent-change-set-1.schema.json
```

### 7.1 Purpose

Record the actual file-level effect of one agent iteration.

This artifact is derived from before/after snapshots.

The agent does not get to declare that an edit was valid merely by naming it valid.

### 7.2 Minimum fields

```json
{
  "iteration": 2,
  "route": "route-nets",
  "changed": [
    {
      "path": "control.aixlayout.json",
      "authority": "layout",
      "beforeDigest": "...",
      "afterDigest": "...",
      "allowed": true
    }
  ],
  "generatedOutputEdits": [],
  "scopeViolations": [],
  "requiredValidators": [
    "schematic.route_closure",
    "schematic.orthogonal"
  ]
}
```

### 7.3 Route write-scope declaration

Extend task routes with machine-readable write scope.

Recommended fields:

```yaml
writes:
  authority:
    - layout
  patterns:
    - "**/*.aixlayout.json"
  derived:
    - "render/**"
    - "evidence/**"
  prohibited:
    - "render/**/*.svg"
    - "**/viewer.html"
```

The exact schema may instead use artifact roles rather than glob patterns if that is cleaner.

### 7.4 Scope rules

Examples:

```text
create-symbol
  may edit symbol + component-library presentation binding

create-schematic
  may edit semantic source + placement/layout records

route-nets
  may edit layout connections only

compose-project
  may edit project composition + required sheet interface declarations

route-project-nets
  may edit project presentation/routing authority only

render-review
  does not itself grant unrestricted write authority;
  remediation follows the diagnostic owner route
```

### 7.5 Generated artifacts are never authoritative edits

A route may regenerate derived artifacts after a valid source change.

A hand-edit to a generated output must be reported as a scope violation.

---

## 8. Authoring Run Record 1

Create:

```text
docs/specifications/agent/authoring-run-record.md
```

Recommended ID:

```text
AIXEM-SPEC-AGENT-RUN-001
```

Schema:

```text
docs/specifications/schemas/agent/aixem-agent-run-record-1.schema.json
```

### 8.1 Purpose

Provide deterministic evidence for one complete authoring or repair task.

### 8.2 Required top-level data

```text
run ID
entry route
task packet digest
baseline artifact digests
route chain
iterations
final authoritative artifact digests
final render/evidence digests
final diagnostic count
final conformance status
```

### 8.3 Iteration record

Each iteration should record:

```text
route/stage
diagnostics before edit
change-set digest
diagnostics after edit
validators executed
rendered evidence produced
whether diagnostic count improved
```

### 8.4 Optional executor metadata

Permit but do not require:

```text
executor type
model/provider name
tool name
configuration identifier
```

These fields are evaluation metadata only.

AIXEM conformance must remain vendor-neutral.

### 8.5 Determinism

For the same recorded authoritative before/after artifacts and validator versions, the run record serialization must be deterministic.

The AI's reasoning text is not part of the deterministic contract.

---

## 9. Authoring Execution Contract 1

Create:

```text
docs/specifications/agent/authoring-execution-contract.md
```

Recommended ID:

```text
AIXEM-SPEC-AGENT-EXECUTION-001
```

This document should bind together existing route architecture and the new diagnostic/change/run evidence.

### 9.1 Canonical stage state machine

```text
PREPARED
  ↓
EDITED
  ↓
VALIDATED
  ├─ PASS → RENDERED → CLOSED
  └─ FAIL → DIAGNOSED → REPAIR → VALIDATED
```

### 9.2 Required preflight

Before editing, the agent/harness must know:

```text
entry route
allowed authority layers
required inputs
baseline digests
required validators
stage exit conditions
```

### 9.3 Required repair loop

For every failed iteration:

1. normalize diagnostics;
2. select the highest-severity blocking diagnostic set;
3. group diagnostics by authority owner;
4. choose the smallest owning route;
5. edit only allowed authority;
6. recompute change set;
7. rerun narrow validators first;
8. rerender only when structurally valid;
9. run full closure at the end.

### 9.4 Non-improving loop detection

The harness should flag when the same blocking diagnostic set survives unchanged across consecutive iterations.

It should also flag oscillation such as:

```text
A → B → A
```

for the same authoritative digest/diagnostic state pair.

P0 does not need an autonomous solver; it only needs to expose the stalled state clearly.

---

## 10. Authoring Harness

Add a small vendor-neutral CLI rather than a large daemon or framework.

Recommended entrypoint:

```text
tools/agent_authoring.py
```

Recommended subcommands:

```text
prepare
check
close
```

### 10.1 `prepare`

Inputs:

```text
project/workspace root
entry route
task identifier
```

Outputs:

```text
resolved task packet
baseline digest manifest
allowed write scope
required validator list
initial diagnostics
```

### 10.2 Agent edit boundary

The agent edits authoritative files using its normal file tools.

AIXEM does not need to proxy every write in P0.

### 10.3 `check`

`check` computes:

```text
changed authoritative files
changed derived files
scope violations
normalized diagnostics
narrow validation result
next remediation route(s)
```

### 10.4 `close`

`close` runs:

```text
full validators
production render
Viewer Model validation
required browser/render checks when applicable
determinism check
final run record
```

### 10.5 No background service

P0 must remain usable as ordinary files + CLI tools.

Do not introduce a server, database, queue, plugin host, or agent daemon.

---

## 11. Validator Normalization

### 11.1 Keep existing validators

Do not rewrite working validators merely for architecture purity.

Wrap existing outputs into the new diagnostic contract.

### 11.2 Normalize at adapter boundaries

Recommended implementation:

```text
implementation/agent/
├── diagnostics.py
├── change_scope.py
├── run_record.py
└── validator_adapter.py
```

or an equivalently small structure.

### 11.3 Stable code before prose

Agents should branch on:

```text
code
authority
remediationRoute
location
```

not by parsing English error messages.

### 11.4 JSON Schema errors

Schema failures should expose:

```text
AIXEM-DIAG-SCHEMA-INVALID
artifact
JSON Pointer
schema pointer when available
```

Do not create a unique diagnostic code for every raw jsonschema sentence.

---

## 12. Authority-Aware Repair Routing

Each normalized diagnostic should resolve to one of the existing task routes whenever possible.

Example mapping:

| Diagnostic class | Authority | Remediation route |
|---|---|---|
| unknown semantic endpoint | semantic | `create-schematic` |
| incomplete port map | component-library binding | `create-symbol` |
| lead/port mismatch | symbol | `create-symbol` |
| placement off-grid | layout placement | `create-schematic` |
| route non-orthogonal | local layout routing | `route-nets` |
| duplicate project-net member | project composition | `compose-project` |
| project route geometry defect | project presentation routing | `route-project-nets` |
| renderer output contradicts valid resolved data | renderer implementation | `change-architecture` or explicit renderer maintenance path |

Do not create a new route when an existing route already owns the repair.

---

## 13. Agent Evaluation 2

Create a new evaluation family rather than deleting the current fixture-backed evaluations.

Recommended path:

```text
validation/agent-evals-2/
```

### 13.1 Two-tier evaluation model

#### Tier A — Deterministic harness conformance

Required in CI.

Tests:

- diagnostic schema;
- route write scope;
- before/after change detection;
- generated-output edit detection;
- run-record closure;
- known repair replay;
- determinism.

#### Tier B — Live agent execution

Release evidence when an external agent is available.

Must record:

```text
executor metadata
documents actually opened
route/task packet used
files changed
repair iterations
diagnostics before/after
source-code inspections
repository-wide searches
final conformance
```

A release must never claim live-agent success when only Tier A or fixture replay was executed.

### 13.2 Cold-start staging

Live evaluation must run in an isolated staged copy that does not expose the expected completed fixture as an easy answer source.

The agent should receive:

```text
task prompt
AIXEM repository docs/routes/tools
starting project state
```

It should not receive the hidden target solution.

### 13.3 Evaluate outcome equivalence, not exact source bytes

Two correct schematics may serialize different but valid deterministic choices where the contract permits freedom.

Score primarily on:

```text
schema/semantic validity
authority correctness
route correctness
required geometry constraints
render success
visual/conformance gates
scope discipline
repair convergence
```

Use exact bytes only where determinism or locked baseline explicitly requires them.

---

## 14. Agent Evaluation Corpus A001-A012

Recommended P0 cases:

| ID | Case | Main proof |
|---|---|---|
| A001 | New two-pin passive from task intent | full symbol→schematic→route closure |
| A002 | Six-pin connector | pin pitch, numbering, total port map |
| A003 | Twelve-pin controller | functional grouping and field/layout discipline |
| A004 | Parameter/variant use | precedence without renderer archaeology |
| A005 | Three-terminal net | junction and crossing correctness |
| A006 | Hierarchical two-sheet composition | interface ports + project net |
| A007 | Same-name local nets | namespace isolation |
| A008 | Broken lead/port | symbol-authority repair |
| A009 | Correct-looking wire on wrong net | semantic-authority repair |
| A010 | Off-grid/non-orthogonal route | layout-authority repair |
| A011 | Duplicate project-net member | project-authority repair |
| A012 | Field/body overlap | symbol visual-rule repair |

For each case retain:

```text
start state
prompt
evaluation policy
hidden expected invariants
required exit conditions
allowed write scope
required validators
```

---

## 15. Evaluation Metrics

Record at minimum:

```text
route compliance
route budget compliance
documents opened
repository-wide searches
renderer source inspections
authoritative files changed
derived files hand-edited
scope violations
initial blocking diagnostics
repair iterations
non-improving iterations
final blocking diagnostics
schema validity
semantic closure
binding closure
placement closure
routing closure
project closure
render success
Viewer Model success
deterministic rerender
```

Recommended P0 release targets:

```text
Tier A deterministic harness tests                 100%
Normalized blocking diagnostics                    100% for P0 registry
Route write-scope enforcement                      100%
Generated-output hand-edit detection               100%
Final schema/semantic closure                      100% corpus
Final renderer success                             100% corpus
Final deterministic rerender                       100% corpus
Repository-wide search                             0 normal successful Tier-B tasks
Renderer source inspection                         0 normal successful Tier-B tasks
Authority-scope violations                         0 successful tasks
```

Do not set a universal token-count threshold in P0; record it when the agent runtime exposes it reliably.

---

## 16. Reference Viewer Role in 0.5.5

Do not substantially expand Viewer features.

The 0.5.4 Viewer should serve as the deterministic observation surface for authoring closure.

Useful 0.5.5 integration is limited to:

- linking Workbench diagnostics to stable diagnostic codes when already available;
- displaying affected QID/object where the diagnostic refers to a rendered object;
- exposing run-record provenance in Workbench evidence if low-risk.

Do **not** prioritize:

- mini-map;
- deep-link state;
- print/export UI;
- endpoint-level interactive editing;
- session persistence;
- authoring buttons.

These are lower leverage than closing the agent repair loop.

---

## 17. Documentation Plan

### 17.1 New normative documents

| Path | Role |
|---|---|
| `docs/specifications/agent/authoring-execution-contract.md` | canonical authoring stage/repair state machine |
| `docs/specifications/agent/diagnostic-contract.md` | stable machine-readable diagnostic contract |
| `docs/specifications/agent/authoring-change-set-contract.md` | route-authorized write-scope and actual change evidence |
| `docs/specifications/agent/authoring-run-record.md` | deterministic end-to-end run evidence |
| `docs/conformance/agent-authoring.md` | P0 authoring closed-loop conformance |
| `docs/conformance/agent-diagnostics.md` | diagnostic code registry and ownership |

### 17.2 New schemas

```text
docs/specifications/schemas/agent/
├── aixem-agent-diagnostic-1.schema.json
├── aixem-agent-change-set-1.schema.json
└── aixem-agent-run-record-1.schema.json
```

### 17.3 Existing docs to update

| Path | Change |
|---|---|
| `AGENTS.md` | require diagnostic-code/authority/scope discipline and run closure |
| `docs/agent/authoring-orchestration.md` | add machine execution checkpoints |
| `docs/agent/failure-policy.md` | define normalized diagnostic and stalled-loop policy |
| `docs/agent/validation-loop.md` | use diagnostics→owner→repair→closure state machine |
| `docs/agent/visual-qa-loop.md` | bind visual defects to stable diagnostic/authority records |
| `docs/agent/task-routing.md` | define remediation-route use |
| `docs/specifications/agent/retrieval-profile.md` | permit diagnostic-driven narrow retrieval |
| `docs/concepts/authority-model.md` | add derived run/change/diagnostic evidence as non-authority |
| `docs/concepts/deterministic-builds.md` | include deterministic authoring run evidence |
| `docs/conformance/release-gates.md` | add agent-authoring closed-loop gate |
| `docs/conformance/validation.md` | normalize authoring validator outputs |
| `docs/getting-started/quick-start.md` | show prepare/edit/check/close workflow |
| `docs/_meta/conformance.yaml` | add agent diagnostic/run validators |
| `docs/_meta/navigation.yaml` | add Authoring Execution/Diagnostics entries |

---

## 18. Task Route Schema Extension

Extend the existing task-route schema conservatively.

Recommended optional fields:

```yaml
writes:
  authority: []
  artifacts: []
  derived: []

remediation:
  acceptsDiagnostics: []
```

### 18.1 Backward compatibility

Existing routes without the fields must remain valid during migration.

0.5.5 canonical authoring routes should populate them.

### 18.2 Composite route inheritance

`author-component-circuit` should not receive one broad union write scope that permits every file at every stage.

The active stage's child route controls the current edit scope.

This prevents an agent from using a composite task as permission for unrestricted repository mutation.

---

## 19. Generated Task Packet Upgrade

Generated task packets should include compact execution metadata:

```text
allowed authority writes
required validators
stage exit conditions
diagnostic remediation mapping
prohibited generated-output edits
```

The packet remains derived navigation/execution data, not authority.

A cold-start agent should be able to begin a routine task from:

```text
AGENTS.md
→ route index
→ one task packet
→ route-selected canonical sections
```

without broad repository inspection.

---

## 20. Implementation Plan

### 20.1 Minimal new implementation

Recommended:

```text
implementation/agent/
├── __init__.py
├── diagnostics.py
├── change_scope.py
├── run_record.py
└── validator_adapter.py
```

and:

```text
tools/agent_authoring.py
```

Avoid introducing a generic workflow engine.

### 20.2 Existing implementation remains primary

Do not rewrite:

```text
component_core.py
project_composition.py
project_routing.py
render_project.py
viewer/*
```

except for small integration points needed to expose stable diagnostic metadata or retire the ambiguous legacy Viewer helper path.

### 20.3 No hidden semantic mutations

The harness may validate, snapshot, diff, and render.

It must not silently rewrite authoritative files to make them pass.

---

## 21. Validation Pipeline

Recommended execution:

```text
1. resolve route/task packet
2. snapshot authoritative digests
3. run narrow preflight validation
4. agent edits authoritative source
5. compute change set
6. reject/flag scope violations
7. run route-local validators
8. normalize diagnostics
9. if errors: return remediation routes
10. if structurally valid: render
11. inspect resolved evidence / Viewer Model
12. run required conformance
13. rerender for determinism
14. emit authoring-run-record.json
```

---

## 22. Structural Negative Cases

Add tests for:

```text
unknown diagnostic code
missing diagnostic authority owner
missing artifact location
invalid remediation route
change set claims unchanged digest as edit
changed file outside route write scope
generated SVG hand-edited
viewer.html hand-edited
agent edits project semantics during route-nets
agent edits layout to repair wrong semantic net
agent edits symbol to repair project-net membership
run record omits a failed iteration
run record closes with blocking diagnostics
stalled loop not detected
```

Fail closed for the contract violations above.

---

## 23. Compatibility Policy

### 23.1 Circuit formats

No required changes to:

```text
.aixem
.aixsym.json
.aixlib.json
aixlayout/1
aixlayout/2
aixproj/1
aixproj/2
```

### 23.2 Renderer and Viewer

Protected 0.5.4 rendering semantics remain unchanged.

Where equivalent locked inputs are used, existing protected SVG/resolved-scene/resolved-project-scene baselines must remain identical.

Viewer Model 1 remains derived and read-only.

### 23.3 Agent contracts are independently versioned

Recommended contract IDs:

```text
aixem.agent-diagnostic@1
aixem.agent-change-set@1
aixem.agent-run-record@1
```

These versions must not be tied mechanically to `aixproj` or Viewer contract versions.

---

## 24. Security and Safety Boundary

0.5.5 does not grant the agent broader file-system authority.

The harness should make mutations more observable, not less controlled.

Required protections:

```text
path must remain inside staged project/repository root
symlink/path traversal must fail closed
route write scope must be checked after edit
derived-output hand edits must be detected
external network remains unnecessary for AIXEM validation/rendering
run record must not embed secrets or environment dumps
```

Live-agent executor credentials are outside AIXEM artifact evidence.

---

## 25. Performance Policy

The P0 authoring harness should record rather than aggressively optimize:

```text
prepare duration
narrow validation duration
render duration
full close duration
change-set file count
diagnostic count per iteration
run-record bytes
```

The harness itself should not become the performance bottleneck relative to rendering.

Do not add databases or caches unless measurement proves a need.

---

## 26. P0 Implementation Sequence

### Phase 0 — Freeze 0.5.4 Agent/Renderer Baseline

1. Record authoring route/task-packet digests.
2. Record existing 8/8 fixture-backed agent eval status.
3. Record `liveExternalAgentExecuted=false` as current limitation.
4. Record authoring example render digests.
5. Record hierarchical and Viewer protected hashes.
6. Classify the legacy `component_core.py` Viewer helper as internal or normalize it through the Viewer adapter.

**Exit criterion:** exact proof of what 0.5.5 may change without weakening 0.5.4.

### Phase 1 — Diagnostic Contract

1. Publish Agent Diagnostic Contract 1.
2. Publish JSON schema.
3. Create P0 diagnostic registry.
4. Map existing validator issues into stable codes.
5. Attach authority and remediation route.
6. Add structural negative tests.

**Exit criterion:** every P0 blocking authoring error is machine-routable without parsing English prose.

### Phase 2 — Route Write Scope

1. Publish Authoring Change-Set Contract 1.
2. Extend task-route schema backward-compatibly.
3. Add write-scope data to authoring routes.
4. Regenerate task packets.
5. Implement before/after digest diff.
6. Detect generated-output hand edits.

**Exit criterion:** the harness can prove whether an agent changed only files allowed by the active route.

### Phase 3 — Execution and Run Record

1. Publish Authoring Execution Contract 1.
2. Publish Authoring Run Record 1 and schema.
3. Implement `prepare`, `check`, and `close` CLI flow.
4. Record iteration diagnostics and change sets.
5. Add stalled-loop detection.
6. Add deterministic run-record serialization.

**Exit criterion:** a complete authoring task produces one verifiable run record from baseline to closure.

### Phase 4 — Existing Workflow Integration

1. Update `AGENTS.md`.
2. Update authoring orchestration.
3. Update validation and visual QA loops.
4. Update failure policy.
5. Integrate normalized diagnostics with Workbench evidence only where low-risk.
6. Keep Viewer read-only.

**Exit criterion:** agent documentation and machine contracts describe one identical repair loop.

### Phase 5 — Agent Evaluation 2 Corpus

1. Add A001-A012 start states and policies.
2. Hide expected completed solutions from staged live runs.
3. Add deterministic harness replay cases.
4. Add cold-start live-agent runner interface.
5. Score authority/scope/process as well as final correctness.
6. Preserve original EVAL-01-EVAL-08 as legacy route-sufficiency evidence.

**Exit criterion:** AIXEM can distinguish fixture simulation, deterministic harness proof, and actual live-agent execution.

### Phase 6 — Conformance and Release Integration

1. Add `docs/conformance/agent-authoring.md`.
2. Add new conformance map entries.
3. Add release-gate checks.
4. Add traceability from diagnostic codes to requirements/tests.
5. Regenerate documentation, routes, task packets, site, and manifests.
6. Run three-pass verification.

**Exit criterion:** every new public claim is backed by executable evidence.

---

## 27. Three-Pass Verification Loop

### PASS 1 — Contract and Authority Closure

Focus:

> Can every authoring failure be routed to one authoritative owner without inventing a second circuit authority?

Gate:

```text
Agent Diagnostic Contract published                 PASS
Diagnostic schema                                   PASS
Change-Set Contract                                 PASS
Run Record Contract                                 PASS
Execution Contract                                  PASS
P0 diagnostic registry mapping                      100%
Authoring route write scopes                        100%
Unknown remediation routes                          0
Generated artifact as repair owner                  0
Normative ownership conflicts                       0
```

### PASS 2 — Repair Loop and Scope Behavior

Focus:

> Can the platform catch bad agent edits and guide bounded repair deterministically?

Gate:

```text
prepare/check/close harness                          PASS
route scope violation detection                     PASS
generated-output hand-edit detection                PASS
semantic-vs-layout wrong-owner negative case        PASS
symbol-vs-binding wrong-owner negative case         PASS
project-vs-project-routing wrong-owner case         PASS
stalled loop detection                              PASS
narrow validator rerun                              PASS
final production render                             PASS
run record schema                                   PASS
run record determinism                              PASS
```

### PASS 3 — Regression, Agent Evals, and Claims

Focus:

> Does the new agent execution layer improve authoring reliability without changing established schematic capability or overstating live-agent evidence?

Gate:

```text
full repository tests                               PASS
0.5.4 Reference Viewer corpus                       PASS
0.5.3 hierarchical corpus                           PASS
0.5.2 symbol/static corpus                          PASS
0.5.1 authoring examples                            PASS
legacy EVAL-01-EVAL-08                              PASS
Agent Evaluation 2 Tier A                           PASS
Tier B claim matches actual execution evidence      PASS
protected render hashes                             PASS
three-run deterministic release evidence            PASS
document dependency graph                           PASS
route/task packet compilation                       PASS
release manifest/integrity                          PASS
false live-agent claim                              0
```

---

## 28. Acceptance Criteria

### 28.1 Diagnostic closure

- [ ] Blocking authoring diagnostics use stable codes.
- [ ] Each P0 diagnostic identifies an authority owner.
- [ ] Each P0 diagnostic identifies a remediation route.
- [ ] Structured location data is present where available.
- [ ] Agents do not need to parse prose to choose the owning route.

### 28.2 Change-scope closure

- [ ] Authoring routes declare allowed write authority.
- [ ] Actual changed files are computed from digests.
- [ ] Generated-output hand edits are detected.
- [ ] Scope violations fail the authoring run or require explicit override evidence.
- [ ] Composite routes enforce active child-stage scope, not broad union scope.

### 28.3 Execution closure

- [ ] `prepare` emits a deterministic task execution packet.
- [ ] `check` emits normalized diagnostics and scope evidence.
- [ ] `close` emits full conformance and run record.
- [ ] Repeated unchanged failures are detected.
- [ ] Final run cannot close with blocking diagnostics.

### 28.4 Agent evaluation

- [ ] Legacy fixture-backed evals remain available.
- [ ] New Tier A harness evals pass.
- [ ] Live-agent runs are explicitly distinguished from fixture/replay runs.
- [ ] Live eval staging hides the completed expected solution.
- [ ] Evaluation scores edit discipline, not only final render appearance.

### 28.5 Regression

- [ ] Existing AIXEM authoritative file formats remain compatible.
- [ ] Existing symbol expressiveness remains unchanged.
- [ ] Existing hierarchical composition remains unchanged.
- [ ] Reference Viewer remains read-only.
- [ ] Protected render evidence remains byte-identical where required.

---

## 29. Explicit Non-Goals for 0.5.5

Do not add:

- graphical schematic editing;
- Viewer authoring controls;
- drag-and-drop placement UI;
- automatic source patch generation as a normative feature;
- a new schematic language;
- a new symbol primitive system;
- a new router algorithm;
- SPICE simulation;
- PCB/Gerber generation;
- vendor import/export;
- cloud collaboration;
- agent server/daemon;
- message queues;
- database-backed workspace state;
- autonomous electrical design synthesis;
- component datasheet crawling;
- LLM-provider-specific APIs;
- plugin marketplace/runtime.

These broaden the product before the core agent authoring loop is proven.

---

## 30. P1 Candidates After 0.5.5 Stability

Only after P0 evidence:

1. optional machine-generated repair hints for selected deterministic diagnostics;
2. optional patch preview/dry-run representation;
3. richer object/QID linkage from diagnostics into Workbench;
4. endpoint-level diagnostic visualization;
5. route-specific context minimization based on diagnostic code;
6. optional live-agent adapter examples for common agent tools;
7. semantic-diff presentation between authoring iterations.

These should remain derived and vendor-neutral.

---

## 31. P2 Gate

A true AIXEM Editor or structured command/mutation language remains a separate architecture program.

Open that program only when evidence shows that direct authoritative-file editing by agents is the main remaining reliability bottleneck after Diagnostic Contract 1 and Change-Scope Contract 1 are stable.

Do not preemptively build an editor command model in 0.5.5.

---

## 32. Recommended Public Claim After P0

If every P0 gate passes, AIXEM may state:

> **AIXEM provides a route-bounded AI schematic authoring workflow with machine-readable validation diagnostics, authority-aware repair routing, write-scope evidence, deterministic render/review closure, and reproducible authoring-run records over its existing semantic, symbol, layout, and hierarchical project formats.**

If Tier B live-agent evidence is executed and retained, AIXEM may additionally state the exact tested tasks and executor configuration.

Do not state generically:

> AIXEM autonomously designs arbitrary electronic circuits.

Do not state:

> AIXEM provides a schematic editor.

Do not state live-agent success when only fixture-backed simulation or deterministic replay was executed.

---

## 33. Recommended Priority

### P0 — Implement now

1. freeze 0.5.4 authoring/viewer baseline;
2. resolve the legacy Viewer helper ambiguity;
3. publish Agent Diagnostic Contract 1;
4. publish diagnostic schema and stable P0 code registry;
5. normalize existing authoring validator outputs;
6. attach authority owner and remediation route;
7. publish Authoring Change-Set Contract 1;
8. add route write-scope metadata;
9. detect generated-output hand edits and authority-scope violations;
10. publish Authoring Execution Contract 1;
11. publish Authoring Run Record 1;
12. implement `prepare/check/close` harness;
13. record per-iteration diagnostics and changed files;
14. detect stalled/non-improving loops;
15. integrate with existing route/task-packet compiler;
16. update AGENTS and authoring/validation/visual-QA docs;
17. add Agent Evaluation 2 Tier A corpus;
18. add optional but rigorous Tier B live-agent execution mode;
19. preserve all existing renderer/Viewer/hierarchical/symbol regressions;
20. run three complete verification passes.

### P1 — Evidence-driven only

1. deterministic repair hints;
2. semantic diff display;
3. diagnostic-to-Viewer object linkage;
4. optional agent-tool adapters.

### P2 — Separate architecture decision

Structured editor command language / GUI Editor / authoritative transaction engine.

---

## 34. Definition of Done

AIXEM 0.5.5 is complete only when an agent-authoring task can be represented as this evidence-backed loop:

```text
Task
  ↓
Route + Task Packet
  ↓
Allowed Authority Scope
  ↓
Agent Source Edit
  ↓
Change Set
  ↓
Narrow Validation
  ↓
Structured Diagnostics
  ↓
Authority + Remediation Route
  ↓
Minimal Repair
  ↓
Full Validation
  ↓
Production Render
  ↓
Reference Viewer / Workbench Review
  ↓
Determinism Check
  ↓
Authoring Run Record
  ↓
CLOSED
```

and when all of the following are true:

- no new circuit authority was introduced;
- no generated artifact was used as the final repair target;
- every blocking P0 diagnostic is machine-routable;
- every agent iteration has objective before/after evidence;
- route write scope is enforceable;
- existing AIXEM rendering and hierarchy behavior is preserved;
- fixture simulation and actual live-agent execution are never conflated;
- the repository can prove not only that a final schematic is valid, but that the agent reached it through the correct authority layers.

The 0.5.5 quality bar should be:

> **AIXEM does not merely give an AI enough documentation to draw a circuit. It gives the AI a deterministic, authority-aware feedback loop that tells it exactly what class of fact is wrong, where that fact lives, what it is allowed to change, what it must not patch, and how to prove that the repair actually closed the design.**
