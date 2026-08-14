# AIXEM Implementation Plans

This directory preserves noncanonical planning state. Release-scoped implementation plans explain why and how a change was proposed; operational authoring queues coordinate future work. Neither class overrides current canonical technical documentation under `docs/` or authoritative production artifacts.

The machine-readable lifecycle owner for release plans is [`index.yaml`](index.yaml). Completed release plans are read-only except for explicit errata that preserve the original decision record. Operational queue lifecycle and discoverability are owned by their local workspace.

## Operational Authoring Queue

- [Library Part Authoring Backlog](library-parts/README.md) — isolated Markdown queue for bounded AI part creation, dated generation history, and independent review. Its checkboxes and logs are workflow state only; actual `.aixlib.json` / `.aixsym.json` content and canonical review evidence remain authoritative.

| Release | Plan | Lifecycle |
|---|---|---|
| 0.5.0 | [Documentation Platform](releases/0.5.0/documentation-platform.md) | Completed |
| 0.5.1 | [Agent Authoring and Drawing](releases/0.5.1/agent-authoring-drawing.md) | Completed |
| 0.5.2 | [Symbol Expressiveness and Conformance](releases/0.5.2/symbol-expressiveness-conformance.md) | Completed |
| 0.5.3 | [Hierarchical Multi-Sheet Composition](releases/0.5.3/hierarchical-multisheet-composition.md) | Completed |
| 0.5.4 | [Reference Viewer Contract](releases/0.5.4/reference-viewer-contract.md) | Completed |
| 0.5.5 | [Agent Authoring Closed Loop](releases/0.5.5/agent-authoring-closed-loop.md) | Completed |
| 0.5.6 | [Live-Agent Cold-Start Authoring](releases/0.5.6/live-agent-cold-start-authoring.md) | Completed; external Tier B claim evidence remains separate |
| 0.5.7 | [Document Information Architecture and Governance](releases/0.5.7/document-information-architecture-governance.md) | Completed |
| 0.5.8 | [Pre-Live Agent Readiness Hardening](releases/0.5.8/pre-live-agent-readiness-hardening.md) | Completed; external Tier B remains unexecuted |

| 0.5.8.1 | [Final Documentation, Specification, and Reference-Chain Closure](releases/0.5.8.1/final-document-specification-reference-chain-closure.md) | Completed; external Tier B remains unexecuted |

| 0.5.9 | [Integrated Authoring, Library, Pin Semantics, and Agent Placement Hardening](releases/0.5.9/integrated-authoring-library-pin-semantics-and-agent-placement-hardening.md) | Completed; full ERC/simulation/auto-layout and external Tier B remain outside scope |

For current rules, resolve a task route and read the canonical document IDs it names. For observed release results, use `validation/releases/<version>/`.
