# AIXEM Agent Evaluation 2

This corpus separates two evidence tiers.

- **Tier A** is the deterministic, vendor-neutral harness and known-repair replay required by CI. It proves route scope, diagnostic ownership, repair closure, production rendering, and run-record determinism. It is not a live-agent-generation claim.
- **Tier B** is optional live external-agent execution in an isolated cold-start stage that does not expose a completed expected solution. No Tier B execution is claimed by the bundled release unless `tier-b-status.json` records an actually executed executor and retained evidence.

Cases A001-A012 preserve the plan's authoring and repair categories. The completed reference fixtures are used only by Tier A deterministic replay. A live executor must receive a separately staged incomplete start state.

- [Retained result summary](results/summary.md)

