# Contributing to AIXEM

Read [`REFERENCE.md`](REFERENCE.md) for the repository category and ownership map. Read `AGENTS.md` before changing code, documentation, schemas, examples, evidence, or generated products.

## Required Workflow

1. Resolve the relevant task route and task packet.
2. Identify the highest-authority source that owns the behavior.
3. Confirm the route's declared write scope.
4. Edit authored authority rather than generated products.
5. Regenerate affected indexes, site, reference output, redirects, inventory, or schematic render.
6. Run the narrow validator and repository tests.
7. Run release checks for publication-bound changes.
8. Report exact commands, migrations, generated effects, and remaining claim boundaries.

## Documentation Policy

The normative rules are in [`docs/specifications/documentation/document-governance-contract.md`](docs/specifications/documentation/document-governance-contract.md). The practical workflow is in [`docs/governance/documentation-authoring-guide.md`](docs/governance/documentation-authoring-guide.md).

Before creating Markdown, determine its role, existing owner, need for a new file, discovery mechanism, lifecycle, filename, identity type, and validator. Unknown-role Markdown fails closed.

- `docs/` is the only canonical technical documentation root.
- Normative rules are defined once and referenced elsewhere.
- New normative language requires stable requirement IDs, validator/test mapping, and evidence paths.
- Plans live under `planning/releases/<version>/` and never override canonical rules.
- Human validation narratives live under `validation/releases/<version>/` and report observed results.
- Canonical path moves preserve the document ID and require `docs/_meta/path-migrations.yaml`.
- Current canonical prose contains no release patch blocks and ends at the canonical footer.
- All shipped textual artifacts are written in English.

## Generated Products

Do not hand-edit `docs/_meta/generated/`, `reference/`, `site/`, render output, or generated validation summaries as the final solution. Change the owning source or generator and rebuild.

## Validation

```bash
python tools/docs/audit_repository_docs.py
python tools/docs/build_all.py
python tools/docs/run_tests.py
python tools/docs/release_pipeline.py --validate-only
```
