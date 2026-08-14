# Agent Evaluation 3 — Cold-Start Corpus

L001-L012 are incomplete, fresh-start authoring tasks. `agent-task.json`, `TASK.md`, and `start/` are agent-visible inputs. `evaluator/invariants.json` and `case.json` remain evaluator-only and are never copied into a cold-start stage.

The corpus contains no completed target workspace or completed target render. Creation tasks are L001-L007; repair tasks are L008-L012. Agent Evaluation 2 remains historical deterministic Tier A replay and is not reused as live evidence.

## Registered Cases

- [L001 — New two-pin passive](cases/L001/TASK.md)
- [L002 — Six-pin connector](cases/L002/TASK.md)
- [L003 — Twelve-pin controller](cases/L003/TASK.md)
- [L004 — Parameterized variant instance](cases/L004/TASK.md)
- [L005 — Three-terminal semantic net](cases/L005/TASK.md)
- [L006 — Two-sheet hierarchical composition](cases/L006/TASK.md)
- [L007 — Same-name local nets](cases/L007/TASK.md)
- [L008 — Broken lead and port](cases/L008/TASK.md)
- [L009 — Correct-looking route on wrong semantic net](cases/L009/TASK.md)
- [L010 — Off-grid non-orthogonal route](cases/L010/TASK.md)
- [L011 — Duplicate project-net member](cases/L011/TASK.md)
- [L012 — Field and body overlap](cases/L012/TASK.md)

The links above are part of the repository root reference chain. The corpus builder MUST reproduce them so rebuilding the suite cannot isolate any human-authored `TASK.md`.
