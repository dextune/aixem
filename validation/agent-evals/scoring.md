# Agent Evaluation Scoring

Each task is scored against release gates rather than an opaque aggregate benchmark.

| Dimension | Gate |
|---|---:|
| Route resolves and declared stage order is preserved | 100% |
| Simple-stage document count ≤ 7 | 100% |
| Simple-stage documentation bytes ≤ 96 KiB | 100% |
| Route depth ≤ 3 | 100% |
| Repository-wide search during route simulation | 0 |
| Renderer implementation paths loaded during route simulation | 0 |
| Schema validity | 100% |
| Semantic/component/port closure | 100% |
| Renderer success | 100% |
| Deterministic rerender | 100% |
| Required authority diagnosis | exact owner |
| Visual/profile checks | at least 95%, with no release-critical defect |

The fixture-backed simulator does not score model prose quality. A live-agent trial should additionally record tool calls, documents actually opened, edits, retry count, visual-review findings, and any source-code inspection.
