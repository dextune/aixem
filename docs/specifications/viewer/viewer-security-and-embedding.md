---
id: AIXEM-SPEC-VIEWER-SECURITY-001
title: Viewer Security and Embedding 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines the self-contained static HTML threat boundary, restrictive CSP, inert authored text, safe Viewer
  Model embedding, network denial, and no-write behavior.
authority:
- viewer-security-contract
- viewer-embedding-contract
aliases:
- Viewer security
- offline viewer
- CSP
agent:
  priority: critical
  estimated_tokens: 1074
  intents:
  - inspect-viewer
  - render-review
  - validate-project
  - publish-release
depends_on:
- AIXEM-SPEC-VIEWER-001
related:
- AIXEM-SPEC-VIEWER-A11Y-001
- AIXEM-CONF-REFERENCE-VIEWER-001
navigation:
  group: viewer
  order: 50
artifacts:
  owns:
  - implementation/schematic/viewer/templates/base.html.j2
  consumes:
  - viewer-model.json
requirements:
- id: AIXEM-REQ-VIEWER-0011
  title: Offline self-containment
  level: MUST
  statement: P0 viewer.html MUST load and operate without required network access or remote assets.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_viewer_security.py::ViewerSecurityConformanceTests.test_v013_offline_network_denial_and_csp
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0011.json
- id: AIXEM-REQ-VIEWER-0013
  title: No network side effects
  level: MUST
  statement: Reference Viewer runtime MUST make zero external network requests during normal operation.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_viewer_security.py::ViewerSecurityConformanceTests.test_v013_offline_network_denial_and_csp
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0013.json
- id: AIXEM-REQ-VIEWER-0012
  title: Untrusted text escaping
  level: MUST
  statement: Authored text MUST be rendered as inert text and MUST NOT create executable HTML or JavaScript.
  validator: schematic.reference_viewer
  verification_mode: automated
  test: tests/conformance/test_viewer_security.py::ViewerSecurityConformanceTests.test_v014_hostile_authored_text_is_inert
  evidence: validation/evidence/requirements/AIXEM-REQ-VIEWER-0012.json
---

# Viewer Security and Embedding 1

The generated Viewer is a static local document that treats every project-provided string as untrusted display data. Its security profile denies external dependencies, runtime network effects, dynamic code construction, browser persistence, and semantic write-back.

## Offline Package Boundary

The P0 HTML embeds its required CSS, Viewer Model JSON, SVG canvases, and JavaScript. It does not require remote fonts, stylesheets, scripts, images, JSON, analytics, or telemetry. The same document remains functional when browser networking is blocked.

<a id="AIXEM-REQ-VIEWER-0011"></a>

### AIXEM-REQ-VIEWER-0011 — Offline self-containment

**MUST.** P0 viewer.html MUST load and operate without required network access or remote assets.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_viewer_security.py::ViewerSecurityConformanceTests.test_v013_offline_network_denial_and_csp`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0011.json`

## Network Denial

Normal Viewer behavior contains no `fetch`, `XMLHttpRequest`, WebSocket, EventSource, beacon, form submission, or service-worker registration. Browser conformance blocks network and records every request; the expected count is zero. File-local navigation is not needed for P0 because required products are embedded.

<a id="AIXEM-REQ-VIEWER-0013"></a>

### AIXEM-REQ-VIEWER-0013 — No network side effects

**MUST.** Reference Viewer runtime MUST make zero external network requests during normal operation.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_viewer_security.py::ViewerSecurityConformanceTests.test_v013_offline_network_denial_and_csp`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0013.json`

## Authored Text and JSON Embedding

Project IDs, titles, sheet titles, references, values, labels, net/port IDs, properties, and diagnostic messages are data. HTML template insertion escapes them. Runtime insertion uses text nodes or equivalent inert operations rather than raw authored HTML.

Serialized Viewer Model JSON escapes `<`, `>`, `&`, and script-closing sequences so an authored `</script>` cannot terminate the JSON script element. Parsing the embedded bytes must reconstruct the same model data.

<a id="AIXEM-REQ-VIEWER-0012"></a>

### AIXEM-REQ-VIEWER-0012 — Untrusted text escaping

**MUST.** Authored text MUST be rendered as inert text and MUST NOT create executable HTML or JavaScript.

- Verification mode: `automated`
- Validator: `schematic.reference_viewer`
- Test reference: `tests/conformance/test_viewer_security.py::ViewerSecurityConformanceTests.test_v014_hostile_authored_text_is_inert`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-VIEWER-0012.json`

## Content Security Policy

The generated document includes a restrictive static CSP compatible with its self-contained inline resources. Default access is denied; network connection, frames, objects, media, manifests, workers, and base-URI changes are not permitted. Dynamic code construction through `eval` or `new Function` is prohibited.

## Structural Fail-Closed Behavior

Viewer Model construction and validation reject duplicate QIDs, unresolved related QIDs, absent required view records, invalid active-sheet derivation, unsupported required model schemas, and project-net references missing from the object index. The Viewer does not silently omit inconsistent required objects.

## No Write-Back or Persistence

The Viewer does not expose filesystem writes, save/download-as-authority operations, browser persistence of authoritative data, or a network API. Highlighting, layer visibility, and viewport transforms remain in memory only.

## Embedding Boundary

A host may place the static Viewer in a controlled browser surface, but the host does not gain permission to reinterpret QIDs or bypass the read-only contract. Future external embedding APIs require a versioned DOM/message contract and separate security review.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
