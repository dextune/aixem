# AIXEM 0.5.1 Agent Authoring Evaluation Harness

This directory stores the cold-start authoring task set, expected outcomes, deterministic route-simulation results, and scoring policy for AIXEM 0.5.1.

The checked-in result is **fixture-backed route simulation**, not a claim that an external stochastic agent was run. The simulator begins from the declared entry route, loads only compiled task packets and their canonical document targets, validates the associated golden fixture, and records that no repository-wide discovery or renderer source path was used. The task prompts and rubrics are also suitable for later human-triggered live-agent trials.

Run:

```bash
python tools/docs/run_agent_evals.py
```

Inputs:

- `tasks/*.json` — eight plan-defined authoring tasks;
- `expected/*.json` — route, budget, closure, determinism, and diagnosis expectations;
- `docs/_meta/generated/task-packets/` — derived bounded execution maps;
- `examples/authoring/` — executable golden fixtures.

Output:

- `results/0.5.1-fixture-results.json` — deterministic route-simulation result;
- `results/summary.md` — human-readable release summary.

A later live-agent run must write a separate timestamped result and must not overwrite the fixture-backed baseline.

Documentation:

- [Scoring policy](scoring.md)
- [Fixture result summary](results/summary.md)

