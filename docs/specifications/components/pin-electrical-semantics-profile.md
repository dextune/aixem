---
id: AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
title: Pin Electrical Semantics Profile 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: profile
summary: Defines orthogonal source-reviewable component pin semantics and a conservative static compatibility precheck without claiming full ERC or simulation correctness.
authority:
- component-pin-electrical-semantics
aliases:
- pin electrical semantics
- pin semantics profile
- bounded electrical compatibility
agent:
  priority: critical
  estimated_tokens: 2024
  intents:
  - create-symbol
  - create-schematic
  - validate-project
depends_on:
- AIXEM-CONCEPT-COMPONENT-001
- AIXEM-FORMAT-AIXLIB-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
related:
- AIXEM-SYMBOL-PORTS-001
- AIXEM-CONCEPT-NET-001
- AIXEM-CONF-VALIDATION-001
navigation:
  group: specifications
  order: 77
artifacts:
  owns: []
  consumes:
  - implementation/schematic/authoring_integrity.py
requirements:
- id: AIXEM-REQ-PIN-0001
  title: Electrical behavior remains port type authority
  level: MUST
  statement: Stable component port IDs and port.type MUST remain the endpoint and basic electrical-behavior authority, while metadata.pinSemantics MUST use the explicit aixem-pin-semantics-1 profile when present.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::PinSemanticsTests.test_pin001_active_low_reset
  evidence: validation/evidence/requirements/AIXEM-REQ-PIN-0001.json
- id: AIXEM-REQ-PIN-0002
  title: Orthogonal semantic facets
  level: MUST
  statement: Signal class, functional tags, polarity, differential membership, power-domain hints, capabilities, and alternate functions MUST remain orthogonal facets and MUST NOT create additional physical endpoints.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::PinSemanticsTests.test_pin005_alternate_functions
  evidence: validation/evidence/requirements/AIXEM-REQ-PIN-0002.json
- id: AIXEM-REQ-PIN-0003
  title: Pin semantic consistency
  level: MUST
  statement: Pin semantic profiles MUST reject invalid tokens, contradictory no-connect obligations, duplicate differential members, and malformed alternate-function declarations.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::PinSemanticsTests.test_pin003_duplicate_differential_member
  evidence: validation/evidence/requirements/AIXEM-REQ-PIN-0003.json
- id: AIXEM-REQ-PIN-0004
  title: Source-reviewed detailed pin semantics
  level: MUST
  statement: Detailed source-dependent pin semantics on a datasheet-backed component MUST be covered by review evidence bound to the cited source and exact component state before semantic-ready status is granted.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::ReviewAndClaimsTests.test_prt007_render_pass_does_not_bypass_review
  evidence: validation/evidence/requirements/AIXEM-REQ-PIN-0004.json
- id: AIXEM-REQ-PIN-0005
  title: Conservative compatibility outcomes
  level: MUST
  statement: The bounded static compatibility precheck MUST report PASS, WARN, ERROR, or NOT_EVALUATED conservatively and MUST NOT claim voltage safety, timing correctness, simulation correctness, or production readiness.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::CompatibilityTests.test_compatibility_never_claims_safety
  evidence: validation/evidence/requirements/AIXEM-REQ-PIN-0005.json
---

# Pin Electrical Semantics Profile 1

This profile adds reviewable meaning to a stable component endpoint without overloading one field or introducing solver-specific semantics. It is a component-library profile. Symbol location, symbol labels, and graphic metadata cannot override it.

## Endpoint and Behavior Authority

<a id="AIXEM-REQ-PIN-0001"></a>

### AIXEM-REQ-PIN-0001 — Electrical behavior remains port type authority

**MUST.** Stable component port IDs and `port.type` MUST remain the endpoint and basic electrical-behavior authority, while `metadata.pinSemantics` MUST use the explicit `aixem-pin-semantics-1` profile when present.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::PinSemanticsTests.test_pin001_active_low_reset`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-PIN-0001.json`

The electrical behavior vocabulary remains:

```text
input
output
bidirectional
passive
power-input
power-output
open-collector
open-emitter
tri-state
no-connect
unspecified
```

This axis answers how an endpoint participates in basic electrical drive or connection behavior. It does not encode functional purpose, waveform, voltage, timing, or active device configuration.

## Profile Shape

```json
{
  "id": "reset-n",
  "name": "RESET_N",
  "terminal": "14",
  "type": "input",
  "required": true,
  "metadata": {
    "pinSemantics": {
      "profile": "aixem-pin-semantics-1",
      "signalClass": "digital",
      "functionalTags": ["reset"],
      "polarity": "active-low",
      "powerDomain": "vddio",
      "capabilities": []
    }
  }
}
```

<a id="AIXEM-REQ-PIN-0002"></a>

### AIXEM-REQ-PIN-0002 — Orthogonal semantic facets

**MUST.** Signal class, functional tags, polarity, differential membership, power-domain hints, capabilities, and alternate functions MUST remain orthogonal facets and MUST NOT create additional physical endpoints.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::PinSemanticsTests.test_pin005_alternate_functions`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-PIN-0002.json`

### Signal class

The initial closed vocabulary is:

```text
analog
digital
mixed-signal
power
ground
reference
rf
unspecified
```

Signal class is a placement, review, and future-adapter hint. It is not a voltage or waveform declaration.

### Functional tags

`functionalTags` are stable lower-kebab tokens. Core examples include `clock`, `reset`, `enable`, `power`, `ground`, `reference`, `oscillator`, `communication`, `programming`, `debug`, `test`, `chip-select`, `interrupt`, `sense`, `feedback`, `shield`, and `chassis`. Source-backed protocol tags such as `i2c-data`, `spi-clock`, or `uart-tx` are allowed without turning the standard into a universal function taxonomy.

### Polarity

The closed vocabulary is `unspecified`, `active-high`, `active-low`, `positive`, and `negative`. Logic/control polarity remains distinct from differential or physical polarity and does not replace `port.type`.

### Differential pair

```json
{
  "id": "usb2-data",
  "member": "positive"
}
```

Within one component, a basic pair has at most one positive and one negative physical member. Pair identity assists review, placement, and routing preference. It does not itself establish impedance or PCB-length matching.

### Power domain

A lower-kebab token such as `vdd`, `vddio`, `avdd`, `dvdd`, `vcore`, or `vbat` may group related pins. It is not a voltage value, net identity, or safety constraint.

### Capabilities and alternate functions

Capabilities describe source-backed potential such as `adc-capable` or `open-drain-capable`; they are not active configuration. Alternate functions remain descriptions of one physical terminal and do not mint additional endpoints. Runtime mux selection is outside this profile.

## Consistency Rules

<a id="AIXEM-REQ-PIN-0003"></a>

### AIXEM-REQ-PIN-0003 — Pin semantic consistency

**MUST.** Pin semantic profiles MUST reject invalid tokens, contradictory no-connect obligations, duplicate differential members, and malformed alternate-function declarations.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::PinSemanticsTests.test_pin003_duplicate_differential_member`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-PIN-0003.json`

Hard failures include an unsupported profile version, an invalid signal class, non-lower-kebab semantic tokens, `type=no-connect` combined with `required=true`, duplicate pair members, or alternate functions without stable names. Unspecified semantics on an otherwise complex semantic-ready part may remain a review warning rather than invented truth.

## Source Review

<a id="AIXEM-REQ-PIN-0004"></a>

### AIXEM-REQ-PIN-0004 — Source-reviewed detailed pin semantics

**MUST.** Detailed source-dependent pin semantics on a datasheet-backed component MUST be covered by review evidence bound to the cited source and exact component state before semantic-ready status is granted.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::ReviewAndClaimsTests.test_prt007_render_pass_does_not_bypass_review`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-PIN-0004.json`

The review covers terminal number, canonical pin name, `port.type`, signal class, polarity, differential membership, power-domain hint, capabilities, and alternate functions where applicable. Pin naming conventions and symbol-side labels remain weak hints; they cannot replace source-bound review.

## Bounded Compatibility Precheck

<a id="AIXEM-REQ-PIN-0005"></a>

### AIXEM-REQ-PIN-0005 — Conservative compatibility outcomes

**MUST.** The bounded static compatibility precheck MUST report `PASS`, `WARN`, `ERROR`, or `NOT_EVALUATED` conservatively and MUST NOT claim voltage safety, timing correctness, simulation correctness, or production readiness.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::CompatibilityTests.test_compatibility_never_claims_safety`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-PIN-0005.json`

| Topology | Outcome |
|---|---|
| one ordinary `output` with one or more `input` endpoints | normally `PASS` |
| multiple ordinary `output` drivers | `ERROR` |
| one `power-output` with one or more `power-input` endpoints | normally `PASS` |
| multiple local `power-output` sources | `ERROR` |
| connected `no-connect` | `ERROR` |
| input-only closed local net | `WARN` |
| multiple open or tri-state drivers | `WARN` |
| multiple bidirectional endpoints | `WARN` or `NOT_EVALUATED` |
| `unspecified` behavior | `NOT_EVALUATED` or `WARN` |

This layer is deliberately smaller than a complete ERC engine. Unknown enable exclusivity, pull networks, hierarchy sources, analog behavior, ratings, and protocol state remain explicit uncertainty.

## Simulation Boundary

Stable component port IDs are suitable future source endpoints for a separate simulation binding contract. This profile does not define SPICE/IBIS/Verilog-A terminal order, model equations, parameters, stimulus, analyses, or result formats. No solver capability is implied.

## Related Documents

- [Library Layout and Part Integrity Contract](library-layout-contract.md) — `AIXEM-SPEC-LIBRARY-LAYOUT-001`
- [Component Model](../../concepts/component-model.md) — `AIXEM-CONCEPT-COMPONENT-001`
- [Pins, Ports, and Endpoint Mapping](../../symbols/pins-and-ports.md) — `AIXEM-SYMBOL-PORTS-001`
- [Validate a Project](../../authoring/guides/validate-project.md) — `AIXEM-AUTHORING-GUIDE-VALIDATE-PROJECT-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
