---
id: AIXEM-AGENT-AUTHORING-001
title: Agent Authoring Orchestration
status: normative
version: '1.0'
language: en
domain: agent
kind: policy
summary: Defines bounded route chaining, stage inputs and outputs, authority checkpoints, and stop conditions for
  composite drawing tasks.
authority:
- agent-authoring-orchestration
aliases:
- author component circuit
- composite authoring route
- drawing task orchestration
agent:
  priority: critical
  estimated_tokens: 1998
  intents:
  - author-component-circuit
  - create-symbol
  - create-schematic
  - compose-project
  - route-project-nets
depends_on:
- AIXEM-AGENT-ROUTES-001
- AIXEM-CONCEPT-AUTHORITY-001
related:
- AIXEM-AUTHORING-GUIDE-MODIFY-SCHEMATIC-001
- AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-AGENT-VISUAL-QA-001
- AIXEM-SYMBOL-BINDING-001
- AIXEM-SPEC-PROJECT-COMPOSITION-001
navigation:
  group: agent
  order: 35
artifacts:
  owns:
  - docs/_meta/routes/author-component-circuit.yaml
  consumes:
  - docs/_meta/generated/task-packets/
requirements:
- id: AIXEM-REQ-AGENT-AUTHORING-0001
  title: Ordered route chaining
  level: MUST
  statement: A composite authoring task MUST execute declared child routes in order and satisfy each stage exit
    condition before advancing.
  validator: agent.authoring_routes
  verification_mode: automated
  test: tests/docs/test_authoring_routes.py::AuthoringRouteTests.test_composite_route_chain
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-AUTHORING-0001.json
- id: AIXEM-REQ-AGENT-AUTHORING-0002
  title: Bounded stage retrieval
  level: MUST
  statement: Each child route in a composite authoring task MUST remain within the configured seven-document, ninety-six-KiB,
    depth-three retrieval budget.
  validator: agent.authoring_routes
  verification_mode: automated
  test: tests/docs/test_authoring_routes.py::AuthoringRouteTests.test_authoring_route_budgets
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-AUTHORING-0002.json
- id: AIXEM-REQ-AGENT-AUTHORING-0003
  title: Documentation before implementation archaeology
  level: MUST
  statement: An agent MUST read the route-selected format and renderer contracts before inspecting renderer implementation
    for ordinary authoring behavior.
  validator: agent.authoring_routes
  verification_mode: automated
  test: tests/docs/test_authoring_routes.py::AuthoringRouteTests.test_agents_policy_contains_source_inspection_gate
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-AUTHORING-0003.json
---

# Agent Authoring Orchestration

Composite drawing work is a sequence of bounded authority stages, not one unlimited search task.

## Canonical Workflow

```text
create or modify component/symbol
→ bind component presentation
→ create semantic schematic and placements
→ route semantic nets
→ render and review
→ validate project
```

The compiled `author-component-circuit` route represents this sequence as child routes. Generated task packets are navigation products, not normative authority.

<a id="AIXEM-REQ-AGENT-AUTHORING-0001"></a>

### AIXEM-REQ-AGENT-AUTHORING-0001 — Ordered route chaining

**MUST.** A composite authoring task MUST execute declared child routes in order and satisfy each stage exit condition before advancing.

- Verification mode: `automated`
- Validator: `agent.authoring_routes`
- Test reference: `tests/docs/test_authoring_routes.py::AuthoringRouteTests.test_composite_route_chain`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-AUTHORING-0001.json`

## Stage Contracts

| Stage | Inputs | Outputs | Exit condition |
|---|---|---|---|
| `create-symbol` | component endpoint contract, desired fields, design profile | valid `.aixsym.json`, valid presentation binding | schema, mapping, lead/port, and visual checks pass |
| `create-schematic` | component library and semantic intent | closed `.aixem`, placements in `.aixlayout.json` | entities, endpoint intent, and placements close |
| `route-nets` | semantic nets and resolved placements | connection paths, bends, junctions, labels | every endpoint routed; orthogonal and unambiguous |
| `render-review` | locked project inputs | SVG/workbench, resolved scene, visual result | no unresolved visual defect |
| `validate-project` | final authoritative sources and derived evidence | release-valid report | schemas, digests, closure, determinism pass |

## Route Entry Decisions

- Use `create-symbol` for symbol-only graphics or field changes.
- Use `create-schematic` when component types already exist and the task changes entities, nets, or placement.
- Use `route-nets` when endpoint membership is already correct and only wire geometry changes.
- Use `render-review` for evidence generation and defect classification.
- Use `author-component-circuit` when a new component asset must be created and then used in a circuit.

<a id="AIXEM-REQ-AGENT-AUTHORING-0002"></a>

### AIXEM-REQ-AGENT-AUTHORING-0002 — Bounded stage retrieval

**MUST.** Each child route in a composite authoring task MUST remain within the configured seven-document, ninety-six-KiB, depth-three retrieval budget.

- Verification mode: `automated`
- Validator: `agent.authoring_routes`
- Test reference: `tests/docs/test_authoring_routes.py::AuthoringRouteTests.test_authoring_route_budgets`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-AUTHORING-0002.json`

The aggregate composite may exceed one route's document count because the budget is enforced per stage. Do not widen one stage to absorb all later work.

## Authority Checkpoint Before Every Edit

```text
component identity/endpoints      → .aixlib and semantic model
visible body/pin graphics         → .aixsym.json
net membership/no-connect         → .aixem
instance position/rotation        → .aixlayout.json placement
wire geometry/junction positions  → .aixlayout.json connections
field source                      → fieldMap, semantic attributes, placement fields
stroke/color/font                 → symbol fallback style / active profile by renderer contract
```

## Existing Asset Reuse

Reuse an existing symbol when its endpoint contract, mapped visibility, required fields, and design profile already match. A new cosmetic variant is preferred over duplicating an equivalent component contract.

<a id="AIXEM-REQ-AGENT-AUTHORING-0003"></a>

### AIXEM-REQ-AGENT-AUTHORING-0003 — Documentation before implementation archaeology

**MUST.** An agent MUST read the route-selected format and renderer contracts before inspecting renderer implementation for ordinary authoring behavior.

- Verification mode: `automated`
- Validator: `agent.authoring_routes`
- Test reference: `tests/docs/test_authoring_routes.py::AuthoringRouteTests.test_agents_policy_contains_source_inspection_gate`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-AUTHORING-0003.json`

Implementation inspection is a fallback for a specific documented discrepancy, not normal discovery.

## New Creation, Existing Repair, and Placement Boundary

Classify each library mutation before writing. A newly added reusable `.aixlib.json` or `.aixsym.json` goes below `library/electronics/...` or `library/architecture/...`. An explicitly referenced legacy file may be repaired in place; moving it is a separate migration that must update paths, digests, generators, and dependent evidence.

Placement strategy may rank legal geometry using explicit semantic evidence, but it cannot create or change net membership. For modifications, freeze unaffected valid authority and edit the smallest semantic/layout region. A requested local change that would require a wide redraw is reported as scope expansion rather than performed silently.

## Stop Conditions

Stop and report a contract conflict when a normative source disagrees with active schema behavior, a locked asset cannot be verified, a required map cannot be made total without changing component identity, or the requested visual behavior would change semantic connectivity. Record the exact stage, authority layer, and evidence.
## Hierarchical Authoring Stages

Multi-sheet work adds two bounded stages without widening the existing leaf routes:

```text
create-schematic (per affected leaf)
→ route-nets (per affected leaf)
→ compose-project (interfaces, hierarchy, project nets)
→ route-project-nets (overview/composite geometry)
→ validate-project
```

Agents should load compact interface summaries before unrelated full leaf bodies. A local edit should not require opening every sheet. The `compose-project` route owns semantic composition; `route-project-nets` owns derived project geometry only.
## Machine Execution Closure

A composite route is orchestration, not a broad mutation grant. Before each stage, `tools/agent_authoring.py prepare` resolves the active child route, task-packet digest, baseline digests, allowed authority and artifact patterns, required validators, and stage exits. After an agent edit, `check` derives the change set from before/after snapshots, normalizes validator failures, and returns the smallest remediation route. `close` performs full validation, three deterministic renders, and Authoring Run Record 1 closure.

The canonical state sequence is `PREPARED -> EDITED -> VALIDATED`, followed by either `RENDERED -> CLOSED` or `DIAGNOSED -> REPAIR -> VALIDATED`. Every repair remains local to the diagnostic owner. Repeated unchanged blocking states and A -> B -> A digest/diagnostic oscillation are blocking execution evidence, not reasons to widen the search or patch generated outputs.

See [Authoring Execution Contract 1](../specifications/agent/authoring-execution-contract.md), [Agent Diagnostic Contract 1](../specifications/agent/diagnostic-contract.md), and [Authoring Run Record 1](../specifications/agent/authoring-run-record.md).
<a id="0-5-6-external-agent-orchestration-boundary"></a>
## External-agent orchestration boundary

Agent Task Contract 1 resolves one executable canonical route before stage construction. The live harness must not introduce evaluation-specific authoring shortcuts. Composite authoring continues to execute child routes in order, with only the active child route's write scope in force. `validate-live-agent-authoring` operates the harness; it does not grant circuit-authoring authority.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
