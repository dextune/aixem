# Hierarchical Project Conformance Corpus 1

This executable corpus covers AIXEM 0.5.3 hierarchical interface ports, immutable `aixlayout/2` and `aixproj/2` contracts, explicit project nets, hierarchy validation, deterministic overview/composite routing, legacy v1 compatibility, and negative fail-closed behavior.

- `cases/H001` through `H015` map directly to the release plan.
- `negative/N001` through `N015` exercise focused validation failures.
- Every project is self-contained and digest locked.
- Generated render/evidence outputs are produced by `tools/validate_hierarchical_corpus.py`.

Connectivity is never inferred from geometry or matching names. Structural ownership is always Project → Sheet → Layer.
