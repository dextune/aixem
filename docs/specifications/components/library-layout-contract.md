---
id: AIXEM-SPEC-LIBRARY-LAYOUT-001
title: Library Layout and Part Integrity Contract
status: normative
version: '1.0'
language: en
domain: specifications
kind: contract
summary: Defines canonical project-library placement, reusable naming, component provenance, semantic identity, and validation-claim boundaries for new AIXEM authoring.
authority:
- component-library-layout-and-integrity
aliases:
- library layout contract
- reusable part integrity
- project library root
agent:
  priority: critical
  estimated_tokens: 2555
  intents:
  - create-symbol
  - create-schematic
  - validate-project
depends_on:
- AIXEM-FORMAT-AIXLIB-001
- AIXEM-FORMAT-AIXSYM-001
- AIXEM-SYMBOL-BINDING-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-SYMBOL-DESIGN-001
- AIXEM-CONF-VALIDATION-001
navigation:
  group: specifications
  order: 76
artifacts:
  owns:
  - implementation/schematic/authoring_integrity.py
  - tools/validate_authoring_integrity.py
  - library/README.md
  consumes:
  - docs/_meta/routes/create-symbol.yaml
requirements:
- id: AIXEM-REQ-LIBRARY-0001
  title: Canonical new-artifact path
  level: MUST
  statement: Newly authored reusable component libraries and symbol assets MUST use a safe project-relative path below library/electronics or library/architecture with lower-kebab namespace segments and filenames.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::LibraryPathTests.test_lby001_new_electronics_path
  evidence: validation/evidence/requirements/AIXEM-REQ-LIBRARY-0001.json
- id: AIXEM-REQ-LIBRARY-0002
  title: Source or truthful placeholder provenance
  level: MUST
  statement: A component claiming a concrete real-world part identity MUST provide manufacturer, part number, and source URI or be explicitly declared as a non-semantic-ready placeholder with a reason.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::PartProvenanceTests.test_prt002_concrete_part_without_source
  evidence: validation/evidence/requirements/AIXEM-REQ-LIBRARY-0002.json
- id: AIXEM-REQ-LIBRARY-0003
  title: Semantic component identity
  level: MUST
  statement: Every component ID MUST own a reviewable identity, port inventory, minimum property contract, provenance status, and presentation binding, and geometry-only ID multiplication MUST be rejected.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::SemanticIdentityTests.test_prt005_geometry_only_id_multiplication
  evidence: validation/evidence/requirements/AIXEM-REQ-LIBRARY-0003.json
- id: AIXEM-REQ-LIBRARY-0004
  title: Separated validation claims
  level: MUST
  statement: Structural render, part semantic review, placeholder status, bounded compatibility, and circuit-intent review results MUST be reported separately and MUST NOT be collapsed into one ambiguous pass claim.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::ReviewAndClaimsTests.test_full_claim_separation
  evidence: validation/evidence/requirements/AIXEM-REQ-LIBRARY-0004.json
- id: AIXEM-REQ-LIBRARY-0005
  title: Source-bound review evidence
  level: MUST
  statement: Datasheet-backed semantic-ready status MUST require review evidence bound to the exact component identity, source URI, library digest, and applicable symbol digest set.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::ReviewAndClaimsTests.test_prt008_review_wrong_source
  evidence: validation/evidence/requirements/AIXEM-REQ-LIBRARY-0005.json
---

# Library Layout and Part Integrity Contract

This contract governs where a newly authored reusable part belongs and what evidence is required before that part may be described as semantically ready. It does not change the identity rules or schema URIs of `.aixlib.json`, `.aixsym.json`, or `.aixproj.json`.

## Authority Split

```text
.aixlib.json component
    -> stable reusable component identity, ports, properties,
       component-level provenance, and presentation binding

.aixsym.json
    -> reusable graphic presentation and symbol-local ports

portMap
    -> component endpoint to symbol endpoint mapping

project manifest
    -> safe project-relative path and digest locks
```

A path assists retrieval. It never replaces the IDs and digests inside the authoritative files. Symbol provenance describes the graphic asset; it does not independently prove the pinout of each component that uses that asset.

## Canonical Authoring Root

<a id="AIXEM-REQ-LIBRARY-0001"></a>

### AIXEM-REQ-LIBRARY-0001 — Canonical new-artifact path

**MUST.** Newly authored reusable component libraries and symbol assets MUST use a safe project-relative path below `library/electronics` or `library/architecture` with lower-kebab namespace segments and filenames.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::LibraryPathTests.test_lby001_new_electronics_path`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LIBRARY-0001.json`

The canonical shape is:

```text
<project-root>/
└── library/
    ├── electronics/
    │   └── <semantic-namespace...>/
    │       ├── <collection>.aixlib.json
    │       └── <presentation>.aixsym.json
    └── architecture/
        └── <semantic-namespace...>/
            ├── <collection>.aixlib.json
            └── <presentation>.aixsym.json
```

Only the first-level domain vocabulary is closed in this profile. Everything below the domain remains extensible. Each segment and filename stem uses lower-kebab-case. The authoring process reuses an accurate existing namespace before creating a synonym and uses the shallowest hierarchy that preserves semantic clarity.

Ordinary reusable-part authoring does not create new assets under `examples/`, `validation/`, `render/`, `evidence/`, `docs/`, `libraries/`, a standalone `symbols/`, or another competing root. A task that explicitly owns an example or conformance fixture may write within that fixture's authority, but it does not redefine the canonical project-library root.

Existing safe historical artifacts remain readable and may be repaired in place. The canonical path gate applies to an added reusable artifact. Moving a legacy artifact is an explicit migration that updates all project paths, presentation paths, and digest locks.

## Component Provenance Status

Every newly authored component declares `metadata.partProvenance.status` as one of:

```text
datasheet-backed
generic-template
placeholder
```

<a id="AIXEM-REQ-LIBRARY-0002"></a>

### AIXEM-REQ-LIBRARY-0002 — Source or truthful placeholder provenance

**MUST.** A component claiming a concrete real-world part identity MUST provide manufacturer, part number, and source URI or be explicitly declared as a non-semantic-ready placeholder with a reason.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::PartProvenanceTests.test_prt002_concrete_part_without_source`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LIBRARY-0002.json`

A `datasheet-backed` component identifies the manufacturer, exact part number or stable product identifier, `sourceKind=manufacturer-datasheet`, and a syntactically valid `sourceUri`. A captured source digest should be retained when the exact reviewed artifact is available.

A `generic-template` intentionally represents a generic class and does not claim a concrete manufacturer part number. A `placeholder` records why the concrete identity cannot yet be supported and remains `semanticReady=false`. A source URI is an evidence identity; normal deterministic validation does not fetch the network resource.

## Semantic Component Contract

<a id="AIXEM-REQ-LIBRARY-0003"></a>

### AIXEM-REQ-LIBRARY-0003 — Semantic component identity

**MUST.** Every component ID MUST own a reviewable identity, port inventory, minimum property contract, provenance status, and presentation binding, and geometry-only ID multiplication MUST be rejected.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::SemanticIdentityTests.test_prt005_geometry_only_id_multiplication`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LIBRARY-0003.json`

Authoring begins with component semantics and then selects or creates presentation geometry:

```text
provenance class
-> component identity
-> complete physical endpoint inventory
-> minimum distinguishing properties
-> reusable presentation selection or creation
-> total portMap
-> locked asset digest
```

Several valid component IDs may share one symbol asset. Shared geometry is not itself a defect. A new ID is invalid when it differs only by ID or display text and has no distinct pin, property, or provenance basis. Deterministic semantic signatures may identify suspicious batches but never replace component identity.

## Review and Claim Boundaries

<a id="AIXEM-REQ-LIBRARY-0004"></a>

### AIXEM-REQ-LIBRARY-0004 — Separated validation claims

**MUST.** Structural render, part semantic review, placeholder status, bounded compatibility, and circuit-intent review results MUST be reported separately and MUST NOT be collapsed into one ambiguous pass claim.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::ReviewAndClaimsTests.test_full_claim_separation`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LIBRARY-0004.json`

| Result | Proven scope | Explicitly outside the claim |
|---|---|---|
| `STRUCTURAL_PASS` | schema, binding, geometry, grid, lint, deterministic render | datasheet truth, part selection, electrical safety |
| `PART_SEMANTIC_PASS` | provenance policy, source-bound pinout review, minimum semantic attributes | complete electrical-design or regulatory correctness |
| `GENERIC_TEMPLATE_PASS` | coherent generic contract without a false concrete identity | existence of a manufacturer product |
| `PLACEHOLDER` | unresolved concrete intent is explicit | semantic or production readiness |
| bounded compatibility result | a small static port-type rule set | voltage, timing, simulation, or production safety |
| `CIRCUIT_INTENT_REVIEW_PASS` | stated role and endpoint/property use were reviewed | absolute-maximum, thermal, regulatory, or simulation correctness |

A successful SVG render is always a structural result. It cannot authorize `semanticReady=true` by itself.

<a id="AIXEM-REQ-LIBRARY-0005"></a>

### AIXEM-REQ-LIBRARY-0005 — Source-bound review evidence

**MUST.** Datasheet-backed semantic-ready status MUST require review evidence bound to the exact component identity, source URI, library digest, and applicable symbol digest set.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::ReviewAndClaimsTests.test_prt008_review_wrong_source`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LIBRARY-0005.json`

The review records pin numbers, canonical names, electrical behavior types, applicable pin-semantics facets, minimum properties, presentation mapping, reviewer mode, timestamp, and result. Circuit-intent evidence additionally records the intended role, required pins, deliberate no-connects, task-relevant property use, and endpoint-preserving presentation.

Review evidence is derived and release-scoped. It does not become component authority and cannot be edited to redefine source truth.

## Authoring and Validation Procedure

1. Resolve the active project or authoring root.
2. Determine whether the task adds a reusable asset, repairs an existing asset, or explicitly migrates a legacy asset.
3. For a new part, choose `electronics` or `architecture`, reuse the established namespace, and select semantic lower-kebab filenames.
4. Resolve `datasheet-backed`, `generic-template`, or `placeholder` before inventing pins or geometry.
5. Author the semantic component contract and Pin Electrical Semantics Profile where justified.
6. Reuse or create the graphic presentation using the active symbol-design profile.
7. Bind every required component endpoint and update digest locks.
8. Run structural validation, component semantic validation, bounded compatibility where applicable, and circuit-intent review as separate layers.
9. Publish the exact result matrix; never promote a lower-layer pass into a higher-layer claim.

## Compatibility and Non-Goals

This contract deliberately does not introduce a universal component taxonomy, package registry, catalog crawler, datasheet parser, automatic electrical-safety checker, global library service, fuzzy deduplication system, or core file-format version bump. Historical safe paths remain compatible; only new ordinary authoring is canonicalized.

## Related Documents

- [`.aixlib.json` Component Library](../../file-formats/aixlib.md) — `AIXEM-FORMAT-AIXLIB-001`
- [`.aixsym.json` Symbol Asset](../../file-formats/aixsym.md) — `AIXEM-FORMAT-AIXSYM-001`
- [Component to Symbol Binding](../../symbols/component-symbol-binding.md) — `AIXEM-SYMBOL-BINDING-001`
- [Pin Electrical Semantics Profile](pin-electrical-semantics-profile.md) — `AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001`
- [Create a Library Part](../../authoring/guides/create-library-part.md) — `AIXEM-AUTHORING-GUIDE-CREATE-LIBRARY-PART-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
