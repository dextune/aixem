---
id: AIXEM-ROUTE-NETS-001
title: Semantic Net Routing
status: normative
version: '1.0'
language: en
domain: routing
kind: guide
summary: Defines how route records bind semantic nets to one or more explicit endpoint-to-endpoint paths.
authority:
- route-binding
aliases:
- semantic routing
- route net
- connect components
agent:
  priority: critical
  estimated_tokens: 1562
  intents:
  - route-nets
  - create-schematic
  - route-project-nets
depends_on:
- AIXEM-CONCEPT-NET-001
- AIXEM-CONCEPT-LAYOUT-001
related:
- AIXEM-FORMAT-AIXLAYOUT-001
- AIXEM-ROUTE-BEHAVIOR-001
- AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001
navigation:
  group: routing
  order: 20
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-ROUTE-0001
  title: Net-bound paths
  level: MUST
  statement: Every route connection MUST name an existing semantic net.
  validator: schematic.route_closure
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0001.json
- id: AIXEM-REQ-ROUTE-0002
  title: Endpoint-bound terminals
  level: MUST
  statement: Every route path terminal MUST resolve to an endpoint that belongs to the named semantic net.
  validator: schematic.route_closure
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0002.json
- id: AIXEM-REQ-ROUTE-0003
  title: No inferred membership
  level: MUST
  statement: Route geometry MUST NOT add an endpoint to a semantic net.
  validator: schematic.geometry_isolation
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0003.json
---

# Semantic Net Routing

Defines how route records bind semantic nets to one or more explicit endpoint-to-endpoint paths.

> **Document ID:** `AIXEM-ROUTE-NETS-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Routing records present semantic nets; they never create net membership through geometry.

The declared authority scopes are `route-binding`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Route binding.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Load semantic net membership
2. Resolve placed port coordinates
3. Partition multi-terminal topology
4. Route explicit paths
5. Insert declared junctions
6. Validate closure and geometry

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-ROUTE-0001"></a>

### AIXEM-REQ-ROUTE-0001 — Net-bound paths

**MUST.** Every route connection MUST name an existing semantic net.

- Verification mode: `automated`
- Validator: `schematic.route_closure`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0001.json`

<a id="AIXEM-REQ-ROUTE-0002"></a>

### AIXEM-REQ-ROUTE-0002 — Endpoint-bound terminals

**MUST.** Every route path terminal MUST resolve to an endpoint that belongs to the named semantic net.

- Verification mode: `automated`
- Validator: `schematic.route_closure`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0002.json`

<a id="AIXEM-REQ-ROUTE-0003"></a>

### AIXEM-REQ-ROUTE-0003 — No inferred membership

**MUST.** Route geometry MUST NOT add an endpoint to a semantic net.

- Verification mode: `automated`
- Validator: `schematic.geometry_isolation`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0003.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Net Model](../concepts/net-model.md) — `AIXEM-CONCEPT-NET-001`
- [Explicit Layout Model](../concepts/layout-model.md) — `AIXEM-CONCEPT-LAYOUT-001`
- [.aixlayout.json Explicit Layout](../file-formats/aixlayout.md) — `AIXEM-FORMAT-AIXLAYOUT-001`
- [Router Behavior](router-behavior.md) — `AIXEM-ROUTE-BEHAVIOR-001`

## Routing to an Interface Endpoint

In `aixlayout/2`, local routes may terminate at an interface endpoint exactly as they terminate at a component endpoint:

```json
{"net":"enable","paths":[{"from":{"endpoint":"U1.EN"},"to":{"endpoint":"@ENABLE"}}]}
```

The endpoint must already belong to the named local semantic net. This route is handled by `route-nets`. Cross-sheet geometry is a separate `route-project-nets` operation and must not edit semantic project-net membership.

<a id="0-5-1-serialization-and-closure-example"></a>
## Serialization and Closure Example

A layout connection names one existing semantic `net` and supplies one or more geometric `paths`. Every semantic endpoint in the net must appear at least once as a path `from` or `to`; point sides and `via` coordinates do not add endpoint membership.

<!-- aixem-snippet: examples/authoring/06-two-terminal-route/two_terminal_route.aixlayout.json#/layout/connections/0 -->
```json
{
  "labels": [
    {
      "text": "SIGNAL",
      "x": 82.5,
      "y": 32.5
    }
  ],
  "layer": "connections",
  "net": "signal",
  "paths": [
    {
      "from": {
        "endpoint": "T1.1"
      },
      "to": {
        "endpoint": "T2.1"
      },
      "via": [
        [
          80,
          35
        ],
        [
          80,
          60
        ]
      ]
    }
  ],
  "style": "signal"
}
```
<!-- /aixem-snippet -->

### Endpoint Resolution

1. Parse the semantic `entity.port` token.
2. Resolve entity component type through the loaded library.
3. Use presentation `portMap` to select the symbol port.
4. Resolve symbol parameters/variant and confirm the port is visible.
5. Apply placement scale, mirrors, rotation, and translation.
6. Connect route geometry to the resulting world coordinate.

### Route Construction Rules

- Use endpoint-to-endpoint direct paths when aligned.
- Add the minimum number of grid-aligned `via` points required for orthogonality and clearance.
- Reject diagonal and zero-length free segments.
- Keep every free route segment at least 2.5 mm under the baseline profile.
- For multi-terminal nets, make branches meet at an explicit point and list that point in `junctions`.
- Preserve semantic source while cleaning geometry; edit semantic membership only when the circuit meaning itself is wrong.

### Handoff and Evidence

A completed route stage produces updated `.aixlayout.json`, deterministic SVG, `resolved-scene.json`, and validation evidence proving net closure, endpoint closure, orthogonality, grid alignment, and junction semantics. See the [Routing Cookbook](routing-cookbook.md) for topology-specific recipes.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
