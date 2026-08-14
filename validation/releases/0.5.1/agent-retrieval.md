# AIXEM 0.5.1 Agent Retrieval Validation Report

Status: **PASS**

- Retrieval corpus cases: **12**
- Pass rate: **100.0%**
- Normal-task repository-wide searches in fixture-backed evaluations: **0**
- Normal-task renderer-source inspections in fixture-backed evaluations: **0**

| Route | Documents | Bytes | Depth |
|---|---:|---:|---:|
| `author-component-circuit` | composite / 5 stages | per-stage | 3 |
| `build-documentation` | 5 | 29924 | 3 |
| `change-architecture` | 6 | 29568 | 3 |
| `create-schematic` | 7 | 43565 | 3 |
| `create-symbol` | 7 | 66775 | 3 |
| `inspect-artifact` | 4 | 19371 | 3 |
| `migrate-baseline` | 4 | 19668 | 3 |
| `publish-release` | 5 | 28014 | 3 |
| `render-review` | 5 | 38333 | 3 |
| `route-nets` | 7 | 43995 | 3 |
| `validate-project` | 7 | 49104 | 3 |

Composite-route budgets apply per child stage. No normal evaluation task exceeded seven documents, 96 KiB, or depth three in any stage.
