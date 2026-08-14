---
id: AIXEM-SPEC-INTERFACE-PORT-001
title: Interface Port Contract 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines feature-gated semantic sheet interface ports and the @PORT endpoint syntax used by hierarchical projects.
authority:
- leaf-interface-semantics
aliases:
- interface port
- sheet port semantics
- hierarchical interface
- off-sheet semantic endpoint
agent:
  priority: critical
  estimated_tokens: 1537
  intents:
  - create-schematic
  - compose-project
  - validate-project
depends_on:
- AIXEM-CONCEPT-SEMANTIC-001
- AIXEM-CONCEPT-NET-001
related:
- AIXEM-SPEC-PROJECT-COMPOSITION-001
- AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001
- AIXEM-FORMAT-AIXEM-001
navigation:
  group: specifications
  order: 45
artifacts:
  owns: []
  consumes:
  - validation/corpus/hierarchical-project-1/manifest.json
requirements:
- id: AIXEM-REQ-HIER-0001
  title: Feature-gated interface declarations
  level: MUST
  statement: A semantic source that declares interface ports or uses @PORT endpoints MUST declare hierarchical.interface@1 as a required feature.
  validator: schematic.feature_support
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_interface_endpoint_is_a_real_leaf_semantic_endpoint
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0001.json
- id: AIXEM-REQ-HIER-0002
  title: Real semantic interface endpoint
  level: MUST
  statement: Every @PORT token in a net or no-connect statement MUST resolve to one unique top-level port declaration in the same leaf semantic source.
  validator: schematic.endpoint_closure
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_interface_endpoint_is_a_real_leaf_semantic_endpoint
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0002.json
- id: AIXEM-REQ-HIER-0003
  title: Interface ownership closure
  level: MUST
  statement: An interface port MUST occur in at most one local semantic net and MUST NOT be both net-connected and explicitly no-connect.
  validator: schematic.no_connect
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_complete_corpus_runner
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0003.json
---

# Interface Port Contract 1

This contract introduces the only new leaf-level semantic concept required by the AIXEM 0.5.3 hierarchical profile: the **interface port**. An interface port is a semantic endpoint owned by one leaf `.aixem` model. It exposes a local net at the sheet boundary without moving connectivity authority into layout geometry or the project manifest.

> **Document ID:** `AIXEM-SPEC-INTERFACE-PORT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Authority Boundary

A leaf semantic source owns:

- component entities and component endpoints;
- top-level interface port declarations;
- local net membership, including interface endpoints;
- explicit no-connect intent.

The project manifest may connect an interface port to ports on other sheets, but it cannot change the local net that owns the port. Layout may place and draw the port, but it cannot create or change the connection.

## Grammar

A source opts into this contract with:

```aixem
feature hierarchical.interface@1 required=true
```

The normative declaration form is:

```text
port <id> [direction=<direction>] [role=<role>] [label=<text>]
```

The normative endpoint token is:

```text
@<port-id>
```

Example:

```aixem
aixem 1.0
model control title="Controller"
feature component.graphics@1 required=true
feature explicit.layout@2 required=true
feature hierarchical.interface@1 required=true

port VCC direction=input role=power
port STATUS direction=output role=signal

component U1 type=example:controller refdes=U1
net vcc = U1.VCC @VCC
net status = U1.STATUS @STATUS
```

The `@` prefix is part of endpoint syntax and is not part of the port ID. The IDs `VCC` and `@VCC` therefore refer to the same declared interface object in declaration and endpoint contexts respectively.

## Direction and Role Vocabulary

The 0.5.3 profile accepts these directions:

```text
input
output
bidirectional
passive
```

It accepts these roles:

```text
signal
power
clock
reset
control
analog
```

Direction and role support diagnostics, inspection, and presentation. They do not constitute a complete electrical-rule-checking type system in this release.

## Local Net Closure

An interface port is a first-class semantic endpoint. This means a local off-sheet connection can satisfy the existing minimum-two-endpoint net rule without fabricating a component or weakening parser closure:

```aixem
port ENABLE direction=input role=control
net enable = U1.EN @ENABLE
```

The local net has two explicit endpoints: `U1.EN` and `@ENABLE`.

Every interface port obeys the same contradiction rules as component endpoints:

- an undeclared `@PORT` is invalid;
- one interface endpoint cannot occur in two local nets;
- one interface endpoint cannot be both connected and no-connect;
- duplicate port declarations are invalid;
- a project-connected interface port must be owned by exactly one local net.

## Stability and Provenance

Port identity is stable across layout changes. Moving a sheet-port glyph, changing its side, changing its visible label, or changing the active layer never changes semantic ownership.

Resolved outputs qualify interface identity as:

```text
interface:<sheet-id>:<port-id>
```

The resolver retains the owning source path and digest so repair tools can modify the smallest authoritative file.

## Prohibited Inferences

The following are never sufficient to create cross-sheet connectivity:

- matching interface port names;
- matching local net names;
- matching visible labels;
- touching or crossing route geometry;
- parent-child hierarchy relationships.

Only explicit `projectNets[]` membership in `aixproj/2` connects leaf interfaces.

## Validation Profile

The executable evidence is in `validation/corpus/hierarchical-project-1`:

- H002 proves the component-endpoint plus interface-endpoint local-net pattern;
- H006 proves local route closure to `@PORT`;
- N001 through N004 prove duplicate, unknown, multi-net, and net/no-connect failures.

## Normative Requirements

<a id="AIXEM-REQ-HIER-0001"></a>

### AIXEM-REQ-HIER-0001 — Feature-gated interface declarations

**MUST.** A semantic source that declares interface ports or uses @PORT endpoints MUST declare hierarchical.interface@1 as a required feature.

- Verification mode: `automated`
- Validator: `schematic.feature_support`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_interface_endpoint_is_a_real_leaf_semantic_endpoint`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0001.json`

<a id="AIXEM-REQ-HIER-0002"></a>

### AIXEM-REQ-HIER-0002 — Real semantic interface endpoint

**MUST.** Every @PORT token in a net or no-connect statement MUST resolve to one unique top-level port declaration in the same leaf semantic source.

- Verification mode: `automated`
- Validator: `schematic.endpoint_closure`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_interface_endpoint_is_a_real_leaf_semantic_endpoint`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0002.json`

<a id="AIXEM-REQ-HIER-0003"></a>

### AIXEM-REQ-HIER-0003 — Interface ownership closure

**MUST.** An interface port MUST occur in at most one local semantic net and MUST NOT be both net-connected and explicitly no-connect.

- Verification mode: `automated`
- Validator: `schematic.no_connect`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_complete_corpus_runner`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0003.json`

## Related Documents

- [Semantic Circuit Model](../../concepts/semantic-model.md)
- [Net Model](../../concepts/net-model.md)
- [Project Composition Contract 2](../project/project-composition-contract.md)
- [Hierarchical Sheet-Port Layout Contract 2](../layout/hierarchical-sheet-port-contract.md)
- [.aixem Semantic Source](../../file-formats/aixem.md)

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
