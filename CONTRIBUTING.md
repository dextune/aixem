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

## Licensing and Contributions

AIXEM-authored code, specifications, and documentation are licensed under the Apache License, Version 2.0 unless a file or directory states otherwise. See [`LICENSE`](LICENSE), [`NOTICE.md`](NOTICE.md), and [`TRADEMARKS.md`](TRADEMARKS.md).

By intentionally submitting a contribution for inclusion in AIXEM, you agree that the contribution is submitted under the terms of the Apache License 2.0 unless you explicitly state otherwise or a separate written agreement applies, consistent with Section 5 of that license. Do not submit material that you do not have the right to contribute. Third-party material must be clearly identified together with its applicable license or permission.

Contributing code or documentation does not grant rights to use the AIXEM name or official AIXEM brand assets beyond the uses permitted by the AIXEM Trademark Policy.

## Generated Products

Do not hand-edit `docs/_meta/generated/`, `reference/`, `site/`, render output, or generated validation summaries as the final solution. Change the owning source or generator and rebuild.

## Validation

```bash
python tools/docs/audit_repository_docs.py
python tools/docs/build_all.py
python tools/docs/run_tests.py
python tools/docs/release_pipeline.py --validate-only
```
