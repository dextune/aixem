---
id: AIXEM-ROUTE-CROSSING-001
title: Crossings and Junctions
status: normative
version: '1.0'
language: en
domain: routing
kind: guide
summary: Applies the explicit-junction model to T joins, four-way joins, non-connected crossings, and dense buses.
authority:
- route-crossing-policy
aliases:
- crossings
- junction routing
- wire intersection
agent:
  priority: critical
  estimated_tokens: 1474
  intents:
  - route-nets
  - validate-project
depends_on:
- AIXEM-SCHEM-JUNCTION-001
- AIXEM-ROUTE-ORTHO-001
related:
- AIXEM-ROUTE-CONSTRAINT-001
navigation:
  group: routing
  order: 60
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-ROUTE-0010
  title: Declared joins
  level: MUST
  statement: Every routed join between two or more path branches MUST be represented by a junction record when required
    by profile policy.
  validator: schematic.junction
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0010.json
- id: AIXEM-REQ-ROUTE-0011
  title: Non-join crossings
  level: MUST
  statement: A crossing of different semantic nets MUST remain non-connected and MUST NOT share a junction record.
  validator: schematic.junction
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0011.json
---

# Crossings and Junctions

Applies the explicit-junction model to T joins, four-way joins, non-connected crossings, and dense buses.

> **Document ID:** `AIXEM-ROUTE-CROSSING-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Routing records present semantic nets; they never create net membership through geometry.

The declared authority scopes are `route-crossing-policy`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- T joins are explicit.
- Four-way joins are allowed only when intentional.
- Dense buses should use separated channels or labels to reduce ambiguous crossings.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-ROUTE-0010"></a>

### AIXEM-REQ-ROUTE-0010 — Declared joins

**MUST.** Every routed join between two or more path branches MUST be represented by a junction record when required by profile policy.

- Verification mode: `automated`
- Validator: `schematic.junction`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0010.json`

<a id="AIXEM-REQ-ROUTE-0011"></a>

### AIXEM-REQ-ROUTE-0011 — Non-join crossings

**MUST.** A crossing of different semantic nets MUST remain non-connected and MUST NOT share a junction record.

- Verification mode: `automated`
- Validator: `schematic.junction`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0011.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Junctions and Connectivity Cues](../schematic/junctions.md) — `AIXEM-SCHEM-JUNCTION-001`
- [Orthogonal Routing](orthogonal-routing.md) — `AIXEM-ROUTE-ORTHO-001`
- [Route Constraints](route-constraints.md) — `AIXEM-ROUTE-CONSTRAINT-001`

<a id="0-5-1-complete-branch-and-crossing-pattern"></a>
## Complete Branch and Crossing Pattern

<!-- aixem-snippet: examples/authoring/07-multi-terminal-junction/multi_terminal_junction.aixlayout.json#/layout/connections -->
```json
[
  {
    "junctions": [
      [
        75,
        50
      ]
    ],
    "labels": [
      {
        "text": "BUS",
        "x": 77.5,
        "y": 47.5
      }
    ],
    "layer": "connections",
    "net": "bus",
    "paths": [
      {
        "from": {
          "endpoint": "T1.1"
        },
        "to": {
          "point": [
            75,
            50
          ]
        }
      },
      {
        "from": {
          "endpoint": "T2.1"
        },
        "to": {
          "point": [
            75,
            50
          ]
        },
        "via": [
          [
            75,
            25
          ]
        ]
      },
      {
        "from": {
          "endpoint": "T3.1"
        },
        "to": {
          "point": [
            75,
            50
          ]
        }
      }
    ],
    "style": "signal"
  },
  {
    "labels": [
      {
        "text": "CROSS / NO JUNCTION",
        "x": 95,
        "y": 42.5
      }
    ],
    "layer": "connections",
    "net": "cross",
    "paths": [
      {
        "from": {
          "endpoint": "T4.1"
        },
        "to": {
          "endpoint": "T5.1"
        }
      }
    ],
    "style": "signal"
  }
]
```
<!-- /aixem-snippet -->

### Three-Terminal Branch

The `bus` semantic net contains three endpoints. Its layout uses three paths that terminate at the common point `[75, 50]` and records that point in `junctions`. Both semantic membership and explicit geometric join are present.

### Unrelated Crossing

The `cross` net is a separate semantic net. Its route may geometrically cross the `bus` trunk. The lines remain electrically separate because their semantic memberships differ and no shared-net junction creates a branch relationship.

### Review Rules

- A junction dot without same-net semantic membership is invalid and visually misleading.
- Same-net branch geometry without an explicit junction is incomplete under the baseline profile.
- Do not merge different connection records merely to simplify drawing.
- Do not split one semantic branch into separate net names merely to avoid a routing problem.
- Move or reroute a crossing when ordinary viewing makes the non-join ambiguous, even when semantic validation passes.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
