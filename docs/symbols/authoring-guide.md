---
id: AIXEM-SYMBOL-AUTHORING-001
title: Symbol Authoring Guide
status: informative
version: '1.0'
language: en
domain: symbols
kind: guide
summary: Provides a repeatable sequence for deriving a compact symbol from a component endpoint contract.
authority:
- symbol-authoring-workflow
aliases:
- create symbol
- draw symbol
- symbol guide
agent:
  priority: normal
  estimated_tokens: 2054
  intents:
  - create-symbol
depends_on:
- AIXEM-SYMBOL-PORTS-001
- AIXEM-SYMBOL-PRIMITIVES-001
related:
- AIXEM-AUTHORING-GUIDE-CREATE-LIBRARY-PART-001
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-AGENT-SYMBOL-001
- AIXEM-SYMBOL-LINT-001
navigation:
  group: symbols
  order: 50
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Symbol Authoring Guide

Provides a repeatable sequence for deriving a compact symbol from a component endpoint contract.

> **Document ID:** `AIXEM-SYMBOL-AUTHORING-001`  
> **Status:** Informative  
> **Version:** 1.0

## Overview

Symbol graphics are presentation assets. Endpoint identity remains owned by the component and semantic layers.

The declared authority scopes are `symbol-authoring-workflow`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Symbol authoring workflow.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Read the component endpoint contract
2. Group endpoints by function and direction
3. Choose body dimensions on the grid
4. Place ports and text anchors
5. Add only necessary graphic detail
6. Define variants without changing endpoint identity
7. Run schema and symbol lint

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

- Preserve symbol authoring workflow as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

### Implementation notes

- Do not trace a vendor screenshot or import a proprietary library symbol. Reconstruct the engineering function from public endpoint and package information using original geometry.

## New Reusable-Part Decision Flow

For a new reusable part, resolve the active project or authoring root first and create the `.aixlib.json` and required `.aixsym.json` assets below `library/<electronics|architecture>/<semantic-namespace...>/`. Reuse an existing lower-kebab namespace before creating a synonym. Editing an explicitly referenced legacy artifact remains an in-place repair unless a migration task was requested.

Author in this order: provenance class, component identity, complete terminal inventory, minimum properties, optional source-reviewed pin semantics, symbol reuse or construction, total `portMap`, digest lock, structural validation, then part-semantic review. A concrete part without reliable primary-source evidence is a placeholder; it is never made semantic-ready by a successful render.

Choose symbol dimensions from the active `G/P/M` rhythm: compute pin-group and text requirements, add clearance, round outward to `G`, preserve standard `P` and lead length, then render and enlarge in `G` increments when needed. Start from the nearest validated corpus recipe rather than an arbitrary freehand size.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Pins, Ports, and Endpoint Mapping](pins-and-ports.md) — `AIXEM-SYMBOL-PORTS-001`
- [Graphic Primitives](primitives.md) — `AIXEM-SYMBOL-PRIMITIVES-001`
- [Symbol Generation Agent](../agent/symbol-generation.md) — `AIXEM-AGENT-SYMBOL-001`
- [Symbol Lint](symbol-lint.md) — `AIXEM-SYMBOL-LINT-001`

<a id="0-5-1-agent-executable-workflow"></a>
## Agent-Executable Workflow

This section is the route-sized execution sequence. Use the [Symbol Authoring Cookbook](symbol-authoring-cookbook.md) for the matching device recipe and the [AIXSYM Field Reference](aixsym-field-reference.md) only for fields required by that recipe.

### Inputs

- semantic component ID and complete endpoint contract;
- port IDs, names, numbers, electrical types, and required visibility;
- displayed semantic properties and their intended symbol fields;
- active symbol-design profile and style profile;
- existing compatible symbol asset, when one can be reused;
- optional parameters and recognized graphical variants.

### Outputs

- one schema-valid `.aixsym.json` asset;
- one `.aixlib.json` presentation binding or an update to an existing binding;
- rendered SVG and `resolved-scene.json` evidence;
- symbol-design lint and binding-validation results;
- updated asset digest/revision in every consuming project lock.

### Execution Sequence

1. **Freeze the endpoint contract.** Do not draw until the semantic component ports are known and stable.
2. **Select a recipe.** Choose two-pin passive, connector, multi-pin IC, analog block, parameterized symbol, or variant symbol.
3. **Choose origin and body dimensions.** Use the 2.5 mm grid, 5 mm pin pitch, and 5 mm standard lead unless a declared profile overrides them.
4. **Draw body and visible leads.** A visible lead is a graphic node. It is not an electrical attachment by itself.
5. **Declare electrical symbol ports.** Make each associated lead endpoint coincide with the port `x`/`y` coordinate. Record `metadata.port` and `metadata.portEndpoint` on standard recipe leads so lint can prove the relationship.
6. **Add field nodes.** Bind identity and value text through a text node `field`; do not hard-code instance values into reusable symbol graphics.
7. **Add parameters or variants only when needed.** Preserve endpoint IDs and apply the documented parameter/variant precedence.
8. **Bind the component presentation.** `portMap` maps semantic component port ID to symbol port ID; `fieldMap` maps symbol field name to semantic property/attribute name.
9. **Validate narrowly.** Run schema, symbol-design, and binding checks before rendering.
10. **Render and inspect.** Review body proportions, pin grouping, label/number visibility, field clearance, and actual routed port positions.
11. **Repair the owning source only.** Geometry defects belong to the symbol; semantic endpoint defects belong to the component/model; placement and wire geometry belong to layout.
12. **Relock and revalidate.** Update digests and rerun deterministic rendering after every authoritative asset change.

### Pin Construction Checkpoint

```text
symbol body ───── visible lead line ───── ● electrical symbol port
                                            ↑
                                  routed attachment coordinate
```

The lead owns visible geometry. The symbol port owns electrical attachment. A renderer may overlay port names or numbers from port metadata, but those overlays do not replace the lead.

### Stage Exit Criteria

- [ ] The endpoint contract is known and has not been inferred from drawing geometry.
- [ ] The symbol validates against the active schema.
- [ ] Every semantic component port has exactly one `portMap` entry.
- [ ] Every mapped target exists and remains visible after variant/parameter resolution.
- [ ] Every standard visible lead endpoint coincides with its electrical port.
- [ ] Reference, value, and custom fields resolve through the renderer contract.
- [ ] Grid, pitch, body, and field-clearance checks pass.
- [ ] SVG and `resolved-scene.json` have been inspected.
- [ ] All affected digests are current and deterministic rerender passes.

### Source-Inspection Gate

For normal symbol authoring, do not inspect `implementation/schematic/component_core.py` to discover routine serialization or precedence. Read the route-selected [Renderer Contract](../specifications/renderer/renderer-contract.md), format reference, and cookbook first. Source inspection is reserved for a demonstrated documentation/implementation discrepancy.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
