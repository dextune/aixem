# AIXEM 0.4 to 0.5 Migration Report

Status: **PASS**

## Scope

The exact 0.4 baseline archive was inventoried before canonical restructuring. Every baseline file is represented by one digest-bearing inventory record and one migration disposition.

## Results

- Baseline files inventoried: **589**
- Baseline bytes inventoried: **17462531**
- Migration mappings: **589**
- Historical declared-but-missing artifacts: **3**
- Historical omissions resolved in 0.5: **3**
- Unresolved target omissions: **0**

## Dispositions

| Disposition | Files |
|---|---:|
| `archived-by-inventory` | 474 |
| `canonicalized` | 28 |
| `discarded-build-cache` | 1 |
| `generated` | 48 |
| `regenerated` | 6 |
| `retained` | 22 |
| `retained-compatibility-schema` | 8 |
| `superseded` | 2 |

## Authority outcome

Canonical 0.5 rules reside under `docs/`. The `reference/` tree is regenerated as compatibility output. Nested legacy baselines are retained by inventory digest and migration rationale rather than copied into the canonical source tree.
