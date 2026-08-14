# AIXEM Reference Viewer 1 Behavioral Corpus

This corpus maps V001 through V018 to controlled single-sheet and hierarchical AIXEM projects, browser-level Playwright tests, deterministic artifact checks, security fixtures, and screenshot evidence. The corpus does not introduce circuit authority; every Viewer input is derived from existing renderer evidence.

Run:

```bash
python tools/validate_reference_viewer_corpus.py --repeats 3 --screenshots
```

The runner emits `results/validation-report.json`, `results/capability-matrix.json`, `results/performance-baseline.json`, `results/determinism-report.json`, and the declared screenshots.
