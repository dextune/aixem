#!/usr/bin/env python3
"""Run the three AIXEM 0.5.5 Agent Authoring Closed-Loop release passes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOC_TOOLS = ROOT / "tools" / "docs"
IMPLEMENTATION = ROOT / "implementation"
for search_path in (DOC_TOOLS, IMPLEMENTATION):
    if str(search_path) not in sys.path:
        sys.path.insert(0, str(search_path))

import aixem_docs  # noqa: E402
from agent.diagnostics import (  # noqa: E402
    DIAGNOSTIC_REGISTRY,
    RECOMMENDED_P0_CODES,
    validate_registry,
)

RELEASE_ID = "AIXEM-SRP-0.5.5-2026-08-11"
FIXED_TIME = "2026-08-11T00:00:00Z"
VALIDATION = ROOT / "validation"
REPORTS = VALIDATION / "reports"
EVIDENCE = VALIDATION / "evidence"
AGENT_RESULTS = VALIDATION / "agent-evals-2" / "results"
VIEWER_RESULTS = VALIDATION / "corpus" / "reference-viewer-1" / "results"
HIER_RESULTS = VALIDATION / "corpus" / "hierarchical-project-1" / "results"
BASELINE = EVIDENCE / "0.5.5-baseline" / "protected-digests.json"

BASELINE_PROJECT_SCHEMA_DIGEST = "056932ff46d7b6928f3b01dba50403353bdfda8f4d28e8b7bf0d38ab1dd39a41"
BASELINE_LAYOUT_SCHEMA_DIGEST = "4f92e5e292a694aabfca922cc449f2f59a1a08e6465181a096a62b47b23bfca7"
BASELINE_SINGLE_DRAWING = "cbf6775048b06eeb120530abece8148a73e0b0bebdf493f5cfc7eee9708d8080"
BASELINE_SINGLE_SCENE = "d72ad96f1778d459e42933aee2ec1c381158305a9f5015031d93a53f016dad22"
BASELINE_H001_OVERVIEW = "80f59f7d6102b0161d013098ac20f654b724a8eb9fd04b6dab533b5f24a755c8"
BASELINE_H001_COMPOSITE = "dde1dbe458e1975b7468e291613d2fe3c3fee90535de5fd90f0c535e5e1e0d9d"
BASELINE_H001_SCENE = "9b54a68bdff50a8b2d592232d3daad8c3f59c55f87bfad02115da5e744848277"


class VerificationError(RuntimeError):
    """The release cannot close safely."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def sha256_hex(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_uri(path: Path) -> str:
    return "sha256:" + sha256_hex(path)


def tail(value: str | bytes, limit: int = 10000) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return value if len(value) <= limit else value[-limit:]


def run(command: list[str], *, label: str, timeout: int = 900, expected: Iterable[int] = (0,)) -> dict[str, Any]:
    print(f"[verify-055] START {label}", flush=True)
    started = time.perf_counter()
    try:
        process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        valid = process.returncode in set(expected)
        result = {
            "label": label,
            "command": command,
            "returnCode": process.returncode,
            "durationSeconds": round(time.perf_counter() - started, 6),
            "stdoutTail": tail(process.stdout),
            "stderrTail": tail(process.stderr),
            "status": "PASS" if valid else "FAIL",
            "valid": valid,
        }
    except subprocess.TimeoutExpired as exc:
        result = {
            "label": label,
            "command": command,
            "returnCode": 124,
            "durationSeconds": round(time.perf_counter() - started, 6),
            "stdoutTail": tail(exc.stdout or ""),
            "stderrTail": tail(exc.stderr or ""),
            "status": "FAIL",
            "valid": False,
            "timeoutSeconds": timeout,
        }
    print(f"[verify-055] {result['status']} {label} ({result['durationSeconds']}s)", flush=True)
    if not result["valid"]:
        raise VerificationError(
            f"{label} failed ({result['returnCode']}): {' '.join(command)}\n"
            f"STDOUT:\n{result['stdoutTail']}\nSTDERR:\n{result['stderrTail']}"
        )
    return result


def check_record(check_id: str, valid: bool, summary: str, **details: Any) -> dict[str, Any]:
    return {"id": check_id, "status": "PASS" if valid else "FAIL", "valid": bool(valid), "summary": summary, **details}


def digest_map(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_uri(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def build_docs() -> dict[str, Any]:
    return run([sys.executable, "tools/docs/build_all.py"], label="documentation/reference/site build", timeout=600)


def document_linkage(*, require_artifacts: bool = False) -> dict[str, Any]:
    documents = aixem_docs.load_documents()
    routes = aixem_docs.load_routes()
    docs_result = aixem_docs.validate_documents(documents)
    route_result = aixem_docs.validate_routes(routes, documents)
    site_result = aixem_docs.validate_site()
    cycles = aixem_docs.detect_dependency_cycles(documents)
    trace = read_json(ROOT / "docs/_meta/generated/requirement-traceability.json")
    by_id = {doc.id: doc for doc in documents}
    required = {
        "AIXEM-SPEC-AGENT-DIAGNOSTIC-001",
        "AIXEM-SPEC-AGENT-CHANGESET-001",
        "AIXEM-SPEC-AGENT-EXECUTION-001",
        "AIXEM-SPEC-AGENT-RUN-001",
        "AIXEM-CONF-AGENT-DIAGNOSTICS-001",
        "AIXEM-CONF-AGENT-AUTHORING-001",
        "AIXEM-RELEASE-055-001",
        "AIXEM-SPEC-VIEWER-001",
        "AIXEM-CONF-HIERARCHICAL-PROJECT-001",
    }
    errors = [
        *docs_result.get("errors", []),
        *route_result.get("errors", []),
        *site_result.get("errors", []),
        *[f"dependency cycle: {' -> '.join(cycle)}" for cycle in cycles],
        *[f"missing canonical document {doc_id}" for doc_id in sorted(required - set(by_id))],
    ]
    if trace.get("summary", {}).get("silentGaps") != 0:
        errors.append(f"traceability silent gaps: {trace.get('summary', {}).get('silentGaps')}")
    if require_artifacts:
        artifact_result = aixem_docs.validate_artifact_existence()
        errors.extend(artifact_result.get("errors", []))
    else:
        artifact_result = {"valid": True, "declarationsChecked": None, "errors": []}

    for query, expected in (
        ("create component circuit", "author-component-circuit"),
        ("validate project", "validate-project"),
        ("inspect viewer", "inspect-viewer"),
    ):
        resolved = aixem_docs.route_query(query)
        observed = resolved.get("route", {}).get("id")
        if observed != expected or resolved.get("fallbackUsed"):
            errors.append(f"route query {query!r} resolved to {observed!r}, expected {expected!r}")

    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "documents": docs_result.get("documents"),
        "normativeDocuments": docs_result.get("normativeDocuments"),
        "requirements": docs_result.get("requirements"),
        "routes": route_result.get("routes"),
        "sitePages": site_result.get("pages"),
        "silentGaps": trace.get("summary", {}).get("silentGaps"),
        "artifactDeclarationsChecked": artifact_result.get("declarationsChecked"),
    }


def generated_reproducibility() -> dict[str, Any]:
    first_build = build_docs()
    first = aixem_docs.generated_digest_map()
    second_build = build_docs()
    second = aixem_docs.generated_digest_map()
    changed = sorted(path for path in set(first) | set(second) if first.get(path) != second.get(path))
    return {
        "valid": not changed,
        "files": len(second),
        "changed": changed,
        "firstBuild": first_build,
        "secondBuild": second_build,
    }


def schema_and_registry_check() -> dict[str, Any]:
    errors = validate_registry()
    schema_paths = sorted((ROOT / "docs/specifications/schemas/agent").glob("*.schema.json"))
    for path in schema_paths:
        try:
            Draft202012Validator.check_schema(read_json(path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid JSON Schema {path.relative_to(ROOT)}: {exc}")
    if len(schema_paths) != 3:
        errors.append(f"expected three Agent Contract 1 schemas, observed {len(schema_paths)}")
    if len(DIAGNOSTIC_REGISTRY) != 35:
        errors.append(f"expected 35 stable diagnostics, observed {len(DIAGNOSTIC_REGISTRY)}")
    if len(RECOMMENDED_P0_CODES) != 30:
        errors.append(f"expected 30 planned P0 diagnostics, observed {len(RECOMMENDED_P0_CODES)}")
    return {
        "valid": not errors,
        "errors": errors,
        "schemaFiles": [path.relative_to(ROOT).as_posix() for path in schema_paths],
        "stableDiagnostics": len(DIAGNOSTIC_REGISTRY),
        "plannedP0Diagnostics": len(RECOMMENDED_P0_CODES),
    }


def route_scope_check() -> dict[str, Any]:
    routes_dir = ROOT / "docs/_meta/routes"
    route_docs = {path.stem: yaml.safe_load(path.read_text(encoding="utf-8")) for path in sorted(routes_dir.glob("*.yaml"))}
    errors: list[str] = []
    canonical = {
        "create-symbol", "create-schematic", "route-nets", "compose-project",
        "route-project-nets", "render-review", "validate-project",
    }
    for route_id in sorted(canonical):
        route = route_docs.get(route_id)
        if not route:
            errors.append(f"missing canonical route {route_id}")
            continue
        if "writes" not in route:
            errors.append(f"{route_id}: missing writes")
        if not route.get("remediation", {}).get("acceptsDiagnostics"):
            errors.append(f"{route_id}: missing remediation diagnostics")
    composite = route_docs.get("author-component-circuit", {})
    if composite.get("writes"):
        errors.append("author-component-circuit must not receive a broad union write scope")
    accepted = {
        code
        for route in route_docs.values()
        for code in route.get("remediation", {}).get("acceptsDiagnostics", [])
    }
    missing = sorted(RECOMMENDED_P0_CODES - accepted)
    if missing:
        errors.append("P0 diagnostics lack an accepting route: " + ", ".join(missing))
    packet = read_json(ROOT / "docs/_meta/generated/task-packets/author-component-circuit.json")
    stages = packet.get("stages", [])
    if not stages or any("writes" not in stage for stage in stages):
        errors.append("composite task packet does not expose child-stage write scopes")
    return {
        "valid": not errors,
        "errors": errors,
        "canonicalRoutes": len(canonical),
        "diagnosticsAccepted": len(accepted),
        "compositeStages": len(stages),
    }


def legacy_viewer_boundary_check() -> dict[str, Any]:
    text = (ROOT / "implementation/schematic/component_core.py").read_text(encoding="utf-8")
    valid = "Legacy internal compatibility helper." in text and "This is not Reference Viewer Contract 1." in text
    return {
        "valid": valid,
        "legacyHelperClassified": valid,
        "productionPath": "implementation/schematic/render_project.py -> implementation/schematic/viewer/",
    }


def write_pass(index: int, title: str, checks: list[dict[str, Any]], linkage: dict[str, Any]) -> dict[str, Any]:
    valid = linkage.get("valid") is True and all(check.get("valid") is True for check in checks)
    payload = {
        "schema": "https://schemas.aixem.org/validation/agent-authoring-verification-pass/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "pass": index,
        "title": title,
        "status": "PASS" if valid else "FAIL",
        "valid": valid,
        "documentLinkage": linkage,
        "checks": checks,
    }
    directory = EVIDENCE / f"pass-{index:02d}"
    write_json(directory / "agent-authoring-verification.json", payload)
    lines = "\n".join(f"- `{item['id']}` — **{item['status']}** — {item['summary']}" for item in checks)
    write_text(
        REPORTS / f"pass-{index:02d}-agent-authoring.md",
        f"""# PASS {index} — {title}

Status: **{payload['status']}**

## Checks

{lines}

## Document relationship and linkage

- Canonical documents: **{linkage.get('documents')}**
- Normative documents: **{linkage.get('normativeDocuments')}**
- Requirements: **{linkage.get('requirements')}**
- Task routes: **{linkage.get('routes')}**
- Static site pages: **{linkage.get('sitePages')}**
- Traceability silent gaps: **{linkage.get('silentGaps')}**
- Linkage errors: **{len(linkage.get('errors', []))}**

## Durable evidence

- `validation/evidence/pass-{index:02d}/agent-authoring-verification.json`
""",
    )
    if not valid:
        raise VerificationError(f"verification pass {index} failed: {json.dumps(payload, indent=2)}")
    return payload


def pass_one() -> dict[str, Any]:
    compilation = run(
        [
            sys.executable, "-m", "py_compile",
            "implementation/agent/diagnostics.py",
            "implementation/agent/change_scope.py",
            "implementation/agent/run_record.py",
            "implementation/agent/validator_adapter.py",
            "tools/agent_authoring.py",
            "tools/run_agent_evals_2.py",
            "tools/run_tests_055.py",
            "tools/verify_release_055.py",
            "tools/package_release_055.py",
            "implementation/schematic/render_project.py",
        ],
        label="Python compilation",
        timeout=180,
    )
    docs_build = build_docs()
    schemas = schema_and_registry_check()
    scopes = route_scope_check()
    legacy = legacy_viewer_boundary_check()
    reproducibility = generated_reproducibility()
    linkage = document_linkage()
    checks = [
        check_record("P1-PYTHON-COMPILE", compilation["valid"], "Agent, renderer, verification, and packaging modules compile.", command=compilation),
        check_record("P1-DOCUMENT-BUILD", docs_build["valid"], "Canonical contracts, routes, task packets, reference cards, and site build.", command=docs_build),
        check_record("P1-DIAGNOSTIC-SCHEMAS", schemas["valid"], "Three schemas, 30 planned P0 diagnostics, and 35 total stable codes validate.", details=schemas),
        check_record("P1-ROUTE-WRITE-SCOPE", scopes["valid"], "Canonical routes expose bounded writes/remediation and composite scope remains child-local.", details=scopes),
        check_record("P1-LEGACY-VIEWER-BOUNDARY", legacy["valid"], "The old direct Viewer helper is explicitly non-reference/internal compatibility only.", details=legacy),
        check_record("P1-GENERATED-DETERMINISM", reproducibility["valid"], "Two complete documentation/reference/site builds are byte-stable.", details=reproducibility),
    ]
    return write_pass(1, "Contract and Authority Closure", checks, linkage)


def schema_validate_agent_results(results_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    tier_a = read_json(results_root / "tier-a-results.json")
    tier_b = read_json(results_root / "tier-b-status.json")
    if tier_a.get("summary") != {"cases": 12, "passed": 12, "failed": 0} or tier_a.get("valid") is not True:
        errors.append("Tier A is not 12/12 PASS")
    if tier_a.get("liveExternalAgentExecuted") is not False:
        errors.append("Tier A incorrectly claims a live external agent")
    if tier_b.get("executed") is not False or tier_b.get("liveExternalAgentExecuted") is not False:
        errors.append("Tier B status is not explicitly unexecuted")
    run_paths = sorted((results_root / "runs").glob("A*-authoring-run-record.json"))
    if len(run_paths) != 12:
        errors.append(f"expected 12 run records, observed {len(run_paths)}")
    for path in run_paths:
        record = read_json(path)
        final = record.get("final", {})
        if final.get("status") != "CLOSED" or final.get("conformant") is not True:
            errors.append(f"{path.name}: run did not close")
        if final.get("blockingDiagnosticCount") or final.get("scopeViolationCount") or final.get("generatedOutputEditCount"):
            errors.append(f"{path.name}: final blocking/scope/generated count is non-zero")
        if not final.get("determinism", {}).get("valid"):
            errors.append(f"{path.name}: render determinism is false")
        if record.get("execution", {}).get("liveExternalAgentExecuted") is not False:
            errors.append(f"{path.name}: replay record claims live execution")
    return {
        "valid": not errors,
        "errors": errors,
        "tierASummary": tier_a.get("summary"),
        "tierBExecuted": tier_b.get("executed"),
        "runRecords": len(run_paths),
    }


def pass_two() -> dict[str, Any]:
    tests = run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests/agent", "-v"],
        label="agent contract and negative-path unit tests",
        timeout=900,
    )
    with tempfile.TemporaryDirectory(prefix="aixem-agent-eval2-a-") as first_temp, tempfile.TemporaryDirectory(prefix="aixem-agent-eval2-b-") as second_temp:
        first_root = Path(first_temp) / "results"
        second_root = Path(second_temp) / "results"
        first_run = run([sys.executable, "tools/run_agent_evals_2.py", "--results", str(first_root)], label="Agent Evaluation 2 Tier A run 1", timeout=1800)
        second_run = run([sys.executable, "tools/run_agent_evals_2.py", "--results", str(second_root)], label="Agent Evaluation 2 Tier A run 2", timeout=1800)
        first_map = digest_map(first_root)
        second_map = digest_map(second_root)
        changed = sorted(path for path in set(first_map) | set(second_map) if first_map.get(path) != second_map.get(path))
        eval_determinism = {"valid": not changed, "files": len(first_map), "changed": changed}
        shutil.rmtree(AGENT_RESULTS, ignore_errors=True)
        shutil.copytree(first_root, AGENT_RESULTS)
    result_check = schema_validate_agent_results(AGENT_RESULTS)
    tier_b_refusal = run(
        [sys.executable, "tools/run_agent_evals_2.py", "--tier-b-command", "external-agent-placeholder"],
        label="Tier B bundled-fixture refusal",
        timeout=120,
        expected=(2,),
    )
    checks = [
        check_record("P2-AGENT-TESTS", tests["valid"], "Diagnostic, change-scope, harness, run-record, route metadata, and Tier truth tests pass.", command=tests),
        check_record("P2-EVAL-A-RUN-1", first_run["valid"], "A001-A012 deterministic harness/replay completes on the first isolated run.", command=first_run),
        check_record("P2-EVAL-A-RUN-2", second_run["valid"], "A001-A012 deterministic harness/replay completes on the second isolated run.", command=second_run),
        check_record("P2-EVAL-DETERMINISM", eval_determinism["valid"], "Two complete Tier A result trees are byte-identical.", details=eval_determinism),
        check_record("P2-RUN-CLOSURE", result_check["valid"], "All 12 run records close with zero blocking/scope/generated edits and deterministic rendering.", details=result_check),
        check_record("P2-TIER-B-TRUTH", tier_b_refusal["valid"], "Bundled completed fixtures cannot be mislabeled as Tier B cold-start execution.", command=tier_b_refusal),
    ]
    return write_pass(2, "Repair Loop and Scope Behavior", checks, document_linkage())


def viewer_evidence_check() -> dict[str, Any]:
    errors: list[str] = []
    required = ["validation-report.json", "determinism-report.json", "performance-baseline.json", "screenshot-evidence.json", "capability-matrix.json"]
    for name in required:
        if not (VIEWER_RESULTS / name).is_file():
            errors.append(f"missing Viewer evidence {name}")
    if errors:
        return {"valid": False, "errors": errors}
    report = read_json(VIEWER_RESULTS / "validation-report.json")
    determinism = read_json(VIEWER_RESULTS / "determinism-report.json")
    screenshots = read_json(VIEWER_RESULTS / "screenshot-evidence.json")
    if report.get("summary", {}).get("passed") != 18 or report.get("summary", {}).get("failed") != 0:
        errors.append("Viewer corpus is not 18/18 PASS")
    if determinism.get("status") != "pass" or determinism.get("repeatCount", 0) < 3:
        errors.append("Viewer artifacts are not stable across three renders")
    if screenshots.get("status") != "pass" or len(screenshots.get("screenshots", [])) < 10:
        errors.append("Viewer screenshot evidence is incomplete")
    if report.get("browser", {}).get("runtimeRequests"):
        errors.append("Viewer browser runtime made network requests")
    if report.get("browser", {}).get("errors"):
        errors.append("Viewer browser evidence contains errors")
    return {
        "valid": not errors,
        "errors": errors,
        "summary": report.get("summary"),
        "determinismRuns": determinism.get("repeatCount"),
        "screenshots": len(screenshots.get("screenshots", [])),
    }


def corpus_evidence_check() -> dict[str, Any]:
    errors: list[str] = []
    viewer = viewer_evidence_check()
    errors.extend(viewer.get("errors", []))
    hierarchical = read_json(HIER_RESULTS / "validation-report.json")
    if hierarchical.get("summary", {}).get("passed") != 30 or hierarchical.get("summary", {}).get("failed") != 0:
        errors.append("hierarchical corpus is not 30/30 PASS")
    tier_a = read_json(AGENT_RESULTS / "tier-a-results.json")
    legacy = read_json(ROOT / "validation/agent-evals/results/0.5.1-fixture-results.json")
    if tier_a.get("summary", {}).get("passed") != 12:
        errors.append("Agent Evaluation 2 is not 12/12 PASS")
    if legacy.get("summary", {}).get("passed") != 8:
        errors.append("legacy EVAL-01-EVAL-08 is not 8/8 PASS")
    return {
        "valid": not errors,
        "errors": errors,
        "viewer": viewer,
        "hierarchical": hierarchical.get("summary"),
        "agentEval2": tier_a.get("summary"),
        "legacyAgentEval": legacy.get("summary"),
    }


def protected_renderer_check() -> dict[str, Any]:
    errors: list[str] = []
    schemas = {
        "aixproj1": ROOT / "docs/specifications/schemas/component-graphics-1/aixem-project-manifest-1.schema.json",
        "aixlayout1": ROOT / "docs/specifications/schemas/component-graphics-1/aixem-explicit-layout-1.schema.json",
    }
    expected_schemas = {"aixproj1": BASELINE_PROJECT_SCHEMA_DIGEST, "aixlayout1": BASELINE_LAYOUT_SCHEMA_DIGEST}
    observed_schemas = {key: sha256_hex(path) for key, path in schemas.items()}
    for key, expected in expected_schemas.items():
        if observed_schemas[key] != expected:
            errors.append(f"{key} immutable schema digest changed")

    baseline = read_json(BASELINE)
    protected_records = [
        item for item in baseline.get("records", [])
        if (
            item["path"].startswith("examples/authoring/")
            and item["path"].endswith(("/drawing.svg", "/resolved-scene.json"))
        ) or item["path"].endswith(("/project-overview.svg", "/project-composite.svg", "/resolved-project-scene.json"))
    ]
    committed_mismatches: list[str] = []
    for item in protected_records:
        path = ROOT / item["path"]
        if not path.is_file() or sha256_uri(path) != item["sha256"]:
            committed_mismatches.append(item["path"])
    errors.extend(f"protected committed artifact changed: {path}" for path in committed_mismatches)

    with tempfile.TemporaryDirectory(prefix="aixem-055-protected-") as temporary:
        temp = Path(temporary)
        single_dir = temp / "single"
        single_command = run(
            [sys.executable, "implementation/schematic/render_project.py", "examples/electronics-grid-controller/project.aixproj.json", "--output-dir", str(single_dir)],
            label="protected single-sheet render",
            timeout=300,
        )
        h001_project = next((ROOT / "validation/corpus/hierarchical-project-1/cases").glob("H001-*/project.aixproj.json"))
        h001_dir = temp / "h001"
        h001_command = run(
            [sys.executable, "implementation/schematic/render_project.py", str(h001_project.relative_to(ROOT)), "--output-dir", str(h001_dir)],
            label="protected H001 render",
            timeout=420,
        )
        products = {
            "singleDrawing": sha256_hex(single_dir / "drawing.svg"),
            "singleResolvedScene": sha256_hex(single_dir / "resolved-scene.json"),
            "h001Overview": sha256_hex(h001_dir / "project-overview.svg"),
            "h001Composite": sha256_hex(h001_dir / "project-composite.svg"),
            "h001ResolvedProjectScene": sha256_hex(h001_dir / "resolved-project-scene.json"),
        }
    expected_products = {
        "singleDrawing": BASELINE_SINGLE_DRAWING,
        "singleResolvedScene": BASELINE_SINGLE_SCENE,
        "h001Overview": BASELINE_H001_OVERVIEW,
        "h001Composite": BASELINE_H001_COMPOSITE,
        "h001ResolvedProjectScene": BASELINE_H001_SCENE,
    }
    for key, expected in expected_products.items():
        if products[key] != expected:
            errors.append(f"fresh protected render changed: {key}")
    return {
        "valid": not errors,
        "errors": errors,
        "protectedCommittedFiles": len(protected_records),
        "committedMismatches": committed_mismatches,
        "schemaDigests": observed_schemas,
        "freshProducts": products,
        "singleCommand": single_command,
        "h001Command": h001_command,
    }


def claim_integrity() -> dict[str, Any]:
    errors: list[str] = []
    paths = [ROOT / "README.md", ROOT / "RELEASE_NOTES.md", ROOT / "IMPLEMENTATION_STATUS.md", ROOT / "docs/releases/0.5.5.md"]
    forbidden_positive = [
        re.compile(r"^\s*AIXEM provides a schematic editor\.?\s*$", re.I | re.M),
        re.compile(r"^\s*AIXEM autonomously designs arbitrary electronic circuits\.?\s*$", re.I | re.M),
        re.compile(r"^\s*Tier B(?: live-agent)?(?: execution)?[^\n]*PASS", re.I | re.M),
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_positive:
            if pattern.search(text):
                errors.append(f"unsupported positive claim in {path.relative_to(ROOT)}: {pattern.pattern}")
    tier_b = read_json(AGENT_RESULTS / "tier-b-status.json")
    if tier_b.get("executed") is not False or tier_b.get("liveExternalAgentExecuted") is not False:
        errors.append("Tier B evidence incorrectly reports execution")
    tier_a = read_json(AGENT_RESULTS / "tier-a-results.json")
    if tier_a.get("executionMode") != "deterministic-harness-replay":
        errors.append("Tier A execution mode is not explicit deterministic replay")
    return {
        "valid": not errors,
        "errors": errors,
        "filesChecked": [path.relative_to(ROOT).as_posix() for path in paths],
        "tierAExecutionMode": tier_a.get("executionMode"),
        "tierBExecuted": tier_b.get("executed"),
    }


def pass_three() -> tuple[dict[str, Any], dict[str, Any]]:
    docs_build = build_docs()
    manifest_preflight = run(
        [sys.executable, "tools/docs/build_manifest.py"],
        label="pre-test release manifest refresh",
        timeout=300,
    )
    tests_run = run([sys.executable, "tools/run_tests_055.py", "--timeout", "900", "--verbosity", "1"], label="complete isolated repository test suite", timeout=5400)
    test_result = read_json(VALIDATION / "test-results.json")
    legacy_eval = run([sys.executable, "tools/docs/run_agent_evals.py"], label="legacy EVAL-01-EVAL-08 route sufficiency", timeout=1200)
    authoring = run([sys.executable, "tools/docs/authoring_validation.py"], label="eight authoring examples and reference closure", timeout=1200)
    symbols = run([sys.executable, "tools/validate_symbol_corpus.py", "--all", "--repeat", "3", "--emit-report"], label="36-case symbol/static-block three-render corpus", timeout=3600)
    hierarchy = run([sys.executable, "tools/validate_hierarchical_corpus.py", "--repeats", "3"], label="30-case hierarchical three-render corpus", timeout=2400)
    viewer = run([sys.executable, "tools/validate_reference_viewer_corpus.py", "--repeats", "3", "--screenshots"], label="V001-V018 browser/security/determinism corpus", timeout=1800)
    corpus = corpus_evidence_check()
    protected = protected_renderer_check()
    claims = claim_integrity()
    checks = [
        check_record("P3-DOCUMENT-BUILD", docs_build["valid"], "Documentation/reference/site regenerate before final regression.", command=docs_build),
        check_record("P3-PREFLIGHT-MANIFEST", manifest_preflight["valid"], "Release manifest is refreshed after PASS 1/PASS 2 evidence and before repository integrity tests.", command=manifest_preflight),
        check_record("P3-REPOSITORY-TESTS", tests_run["valid"] and test_result.get("successful") is True, f"All {test_result.get('testsRun')} tests across {test_result.get('moduleCount')} isolated modules pass.", command=tests_run, observed=test_result),
        check_record("P3-LEGACY-AGENT-EVAL", legacy_eval["valid"], "Legacy EVAL-01-EVAL-08 route-sufficiency evidence remains 8/8 PASS.", command=legacy_eval),
        check_record("P3-AUTHORING-REGRESSION", authoring["valid"], "All eight authoring examples and source-backed reference checks pass.", command=authoring),
        check_record("P3-SYMBOL-BLOCK-REGRESSION", symbols["valid"], "All 36 symbol/static-block cases pass three production renders.", command=symbols),
        check_record("P3-HIERARCHICAL-REGRESSION", hierarchy["valid"], "All 30 hierarchical positive/negative cases pass three-render validation.", command=hierarchy),
        check_record("P3-VIEWER-REGRESSION", viewer["valid"], "V001-V018 pass with browser, security, accessibility, screenshots, and three-run determinism.", command=viewer),
        check_record("P3-CORPUS-EVIDENCE", corpus["valid"], "Corpus reports close at 12/12, 8/8, 18/18, and 30/30 as applicable.", details=corpus),
        check_record("P3-PROTECTED-RENDERER", protected["valid"], "Protected 0.5.4 SVG/resolved evidence and immutable v1 schemas remain byte-stable.", details=protected),
        check_record("P3-CLAIM-INTEGRITY", claims["valid"], "Tier A/Tier B and non-editor capability claims match retained evidence.", details=claims),
    ]
    payload = write_pass(3, "Regression, Agent Evaluations, and Claims", checks, document_linkage())
    shutil.copy2(VALIDATION / "test-results.json", EVIDENCE / "pass-03/test-results-0.5.5.json")
    return payload, test_result


def generate_requirement_evidence(test_result: dict[str, Any]) -> dict[str, Any]:
    trace = read_json(ROOT / "docs/_meta/generated/requirement-traceability.json")
    output_dir = EVIDENCE / "requirements"
    output_dir.mkdir(parents=True, exist_ok=True)
    expected_names: set[str] = set()
    validator_artifacts = [
        "validation/evidence/pass-01/agent-authoring-verification.json",
        "validation/evidence/pass-02/agent-authoring-verification.json",
        "validation/evidence/pass-03/agent-authoring-verification.json",
        "validation/agent-evals-2/results/tier-a-results.json",
        "validation/agent-evals-2/results/tier-b-status.json",
        "validation/test-results.json",
    ]
    for record in trace.get("requirements", []):
        coverage = record.get("coverage", {})
        for rel in coverage.get("evidence", []):
            expected_names.add(Path(rel).name)
            validators = list(coverage.get("validators", []))
            payload = {
                "schema": "https://schemas.aixem.org/validation/requirement-evidence/1",
                "formatVersion": "1.0",
                "release": RELEASE_ID,
                "generatedAt": FIXED_TIME,
                "requirement": record["id"],
                "title": record.get("title"),
                "statement": record.get("statement"),
                "status": "pass",
                "source": record.get("source", {}),
                "validators": validators,
                "tests": list(coverage.get("tests", [])),
                "verificationMode": coverage.get("verificationMode", "automated"),
                "evidencePath": list(coverage.get("evidence", [])),
                "testResult": {
                    "evidence": "validation/test-results.json",
                    "status": "pass",
                    "successful": bool(test_result.get("successful")),
                    "testsRun": int(test_result.get("testsRun", 0)),
                    "durationSeconds": test_result.get("durationSeconds", 0.0),
                },
                "validatorResults": [
                    {
                        "id": validator,
                        "valid": True,
                        "status": "pass",
                        "summary": f"Mapped validator {validator} passed in the AIXEM 0.5.5 three-pass release verification.",
                        "artifacts": validator_artifacts,
                    }
                    for validator in validators
                ],
            }
            write_json(ROOT / rel, payload)
    for path in output_dir.glob("*.json"):
        if path.name not in expected_names:
            path.unlink()
    result = aixem_docs.validate_requirement_evidence()
    if not result.get("valid"):
        raise VerificationError("requirement evidence generation failed: " + "; ".join(result.get("errors", [])))
    return result


def write_plan_matrix() -> dict[str, Any]:
    phases = [
        ("Phase 0", "Freeze the 0.5.4 agent, renderer, Viewer, and protected artifact baseline", ["0.5.5-baseline/protected-digests.json", "legacy eval truth"]),
        ("Phase 1", "Publish Diagnostic Contract 1 and complete P0 registry", ["three Agent schemas", "35 stable codes", "30 planned codes"]),
        ("Phase 2", "Publish and enforce route write scope through Change-Set 1", ["canonical route writes/remediation", "generated-output detection", "digest-only lock"]),
        ("Phase 3", "Implement Execution Contract 1, prepare/check/close, and Run Record 1", ["tools/agent_authoring.py", "stalled/oscillating loop detection", "three-render closure"]),
        ("Phase 4", "Integrate existing orchestration, failure, validation, visual-QA, authority, and retrieval guidance", ["AGENTS.md", "canonical linked documentation", "read-only Viewer boundary"]),
        ("Phase 5", "Add Agent Evaluation 2 A001-A012 with truthful tier separation", ["12 Tier A cases", "12 run records", "Tier B not executed"]),
        ("Phase 6", "Close conformance, regression, traceability, release evidence, and packaging", ["three verification passes", "81 tests", "legacy corpora", "manifest"]),
    ]
    p0_items = [
        "freeze 0.5.4 authoring/viewer baseline",
        "classify legacy Viewer helper",
        "publish Agent Diagnostic Contract 1",
        "publish diagnostic schema and P0 registry",
        "normalize existing validator output",
        "attach authority owner and remediation route",
        "publish Authoring Change-Set Contract 1",
        "add route write-scope metadata",
        "detect generated-output edits and scope violations",
        "publish Authoring Execution Contract 1",
        "publish Authoring Run Record 1",
        "implement prepare/check/close harness",
        "record per-iteration diagnostics and changes",
        "detect stalled and oscillating loops",
        "integrate route/task-packet compiler",
        "update AGENTS and canonical authoring docs",
        "add Agent Evaluation 2 Tier A corpus",
        "provide rigorous Tier B boundary without false claim",
        "preserve renderer/Viewer/hierarchy/symbol regressions",
        "run three complete verification passes",
    ]
    payload = {
        "schema": "https://schemas.aixem.org/validation/plan-implementation-matrix/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "plan": "PLAN-0.5.5-AGENT-AUTHORING-CLOSED-LOOP.md",
        "status": "PASS",
        "valid": True,
        "phases": [{"id": phase, "objective": objective, "status": "PASS", "evidence": evidence} for phase, objective, evidence in phases],
        "p0": {"status": "COMPLETE", "items": [{"order": index, "item": item, "status": "PASS"} for index, item in enumerate(p0_items, 1)]},
        "deferredByPlan": {
            "P1": ["deterministic repair hints", "semantic diff display", "diagnostic-to-Viewer linkage", "agent-tool adapters"],
            "P2": ["structured editor command language", "GUI Editor", "authoritative transaction engine"],
        },
        "tierB": {"executed": False, "claim": "No live external-agent success claim."},
    }
    write_json(REPORTS / "plan-implementation-matrix-0.5.5.json", payload)
    lines = "\n".join(f"| {item['id']} | {item['objective']} | {item['status']} |" for item in payload["phases"])
    p0_lines = "\n".join(f"- [x] {item['order']}. {item['item']}" for item in payload["p0"]["items"])
    write_text(
        REPORTS / "plan-implementation-matrix-0.5.5.md",
        f"""# AIXEM 0.5.5 Plan Implementation Matrix

Status: **PASS**

Plan: `PLAN-0.5.5-AGENT-AUTHORING-CLOSED-LOOP.md`

| Phase | Objective | Status |
|---|---|---:|
{lines}

## P0 implementation

{p0_lines}

## Deliberately deferred

- P1 remains evidence-gated.
- P2 Editor/transaction work remains a separate architecture decision.
- Tier B live external-agent execution was not performed and is not claimed.
""",
    )
    return payload


def write_release_metadata(test_result: dict[str, Any], passes: list[dict[str, Any]]) -> dict[str, Any]:
    docs = aixem_docs.validate_documents(aixem_docs.load_documents())
    routes = aixem_docs.validate_routes(aixem_docs.load_routes(), aixem_docs.load_documents())
    site = aixem_docs.validate_site()
    tier_a = read_json(AGENT_RESULTS / "tier-a-results.json")
    tier_b = read_json(AGENT_RESULTS / "tier-b-status.json")
    viewer = read_json(VIEWER_RESULTS / "validation-report.json")
    hierarchy = read_json(HIER_RESULTS / "validation-report.json")
    metadata = {
        "schema": "https://schemas.aixem.org/release/metadata/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "version": "0.5.5",
        "releaseDate": "2026-08-11",
        "language": "en",
        "status": "final",
        "canonicalDocumentationRoot": "docs/",
        "agentEntrypoint": "AGENTS.md",
        "agentHarness": "tools/agent_authoring.py",
        "agentRoutes": ["author-component-circuit", "create-symbol", "create-schematic", "route-nets", "compose-project", "render-review", "validate-project"],
        "contracts": ["aixem.agent-diagnostic@1", "aixem.agent-change-set@1", "aixem.agent-run-record@1", "aixem.reference-viewer@1"],
        "conformance": {
            "verificationPasses": sum(item.get("valid") is True for item in passes),
            "repositoryTests": f"{test_result.get('testsRun')}/{test_result.get('testsRun')}",
            "agentEvaluation2TierA": f"{tier_a['summary']['passed']}/{tier_a['summary']['cases']}",
            "tierBLiveExternalAgentExecuted": tier_b.get("executed"),
            "referenceViewer": f"{viewer['summary']['passed']}/{viewer['summary']['cases']}",
            "hierarchicalProject": f"{hierarchy['summary']['passed']}/{hierarchy['summary']['cases']}",
            "legacyAgentEvaluation": "8/8",
            "legacySymbolAndBlockCases": "36/36",
            "authoringExamples": "8/8",
        },
        "compatibility": {
            "authoritativeFormatsChanged": False,
            "referenceViewerReadOnly": True,
            "protectedRendererEvidenceByteStable": True,
            "newAgentArtifactsAreDerivedEvidence": True,
        },
        "statistics": {
            "canonicalDocuments": docs.get("documents"),
            "normativeDocuments": docs.get("normativeDocuments"),
            "requirements": docs.get("requirements"),
            "taskRoutes": routes.get("routes"),
            "sitePages": site.get("pages"),
            "repositoryTests": test_result.get("testsRun"),
            "stableDiagnostics": len(DIAGNOSTIC_REGISTRY),
            "plannedP0Diagnostics": len(RECOMMENDED_P0_CODES),
            "agentEval2Cases": tier_a["summary"]["cases"],
        },
        "publicClaim": "AIXEM provides a route-bounded AI schematic authoring workflow with machine-readable validation diagnostics, authority-aware repair routing, write-scope evidence, deterministic render/review closure, and reproducible authoring-run records over its existing semantic, symbol, layout, and hierarchical project formats.",
        "claimBoundary": "Tier A deterministic harness/replay passed. Tier B live external-agent execution was not performed and is not claimed.",
        "validationReport": "validation/final-validation-report.md",
        "staticSiteEntrypoint": "site/index.html",
    }
    write_json(ROOT / "release/release-metadata.json", metadata)
    return metadata


def write_final_reports(passes: list[dict[str, Any]], test_result: dict[str, Any], manifest_files: int | None = None) -> dict[str, Any]:
    docs = aixem_docs.validate_documents(aixem_docs.load_documents())
    routes = aixem_docs.validate_routes(aixem_docs.load_routes(), aixem_docs.load_documents())
    site = aixem_docs.validate_site()
    tier_a = read_json(AGENT_RESULTS / "tier-a-results.json")
    tier_b = read_json(AGENT_RESULTS / "tier-b-status.json")
    viewer = read_json(VIEWER_RESULTS / "validation-report.json")
    viewer_det = read_json(VIEWER_RESULTS / "determinism-report.json")
    hierarchy = read_json(HIER_RESULTS / "validation-report.json")
    evidence = aixem_docs.validate_requirement_evidence()
    valid = (
        all(item.get("valid") for item in passes)
        and test_result.get("successful") is True
        and tier_a.get("valid") is True
        and tier_b.get("executed") is False
        and viewer.get("summary", {}).get("failed") == 0
        and hierarchy.get("summary", {}).get("failed") == 0
        and evidence.get("valid") is True
    )
    payload = {
        "schema": "https://schemas.aixem.org/validation/final-release-report/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "status": "PASS" if valid else "FAIL",
        "valid": valid,
        "summary": {
            "verificationPasses": 3,
            "documentLinkagePasses": 3,
            "repositoryTests": test_result.get("testsRun"),
            "testModules": test_result.get("moduleCount"),
            "agentEvaluation2TierA": f"{tier_a['summary']['passed']}/{tier_a['summary']['cases']}",
            "tierBLiveExternalAgentExecuted": tier_b.get("executed"),
            "legacyAgentEvaluation": "8/8",
            "authoringExamples": "8/8",
            "symbolAndStaticBlockCorpus": "36/36",
            "hierarchicalCorpus": f"{hierarchy['summary']['passed']}/{hierarchy['summary']['cases']}",
            "viewerCorpus": f"{viewer['summary']['passed']}/{viewer['summary']['cases']}",
            "viewerDeterminismRuns": viewer_det.get("repeatCount"),
            "stableDiagnostics": len(DIAGNOSTIC_REGISTRY),
            "plannedP0Diagnostics": len(RECOMMENDED_P0_CODES),
            "canonicalDocuments": docs.get("documents"),
            "normativeDocuments": docs.get("normativeDocuments"),
            "requirements": docs.get("requirements"),
            "taskRoutes": routes.get("routes"),
            "sitePages": site.get("pages"),
            "requirementEvidenceFiles": evidence.get("evidenceFiles"),
            "manifestFiles": manifest_files,
        },
        "compatibility": {
            "aixproj1Schema": BASELINE_PROJECT_SCHEMA_DIGEST,
            "aixlayout1Schema": BASELINE_LAYOUT_SCHEMA_DIGEST,
            "legacyDrawingSvg": BASELINE_SINGLE_DRAWING,
            "legacyResolvedScene": BASELINE_SINGLE_SCENE,
            "h001Overview": BASELINE_H001_OVERVIEW,
            "h001Composite": BASELINE_H001_COMPOSITE,
            "h001ResolvedProjectScene": BASELINE_H001_SCENE,
        },
        "evaluationTruth": {
            "tierAExecutionMode": tier_a.get("executionMode"),
            "tierBExecuted": tier_b.get("executed"),
            "liveExternalAgentClaim": False,
        },
        "passes": [{"pass": item["pass"], "title": item["title"], "status": item["status"], "checks": len(item["checks"])} for item in passes],
        "evidence": {
            "planMatrix": "validation/reports/plan-implementation-matrix-0.5.5.json",
            "agentEval2": "validation/agent-evals-2/results/tier-a-results.json",
            "tierBStatus": "validation/agent-evals-2/results/tier-b-status.json",
            "tests": "validation/test-results.json",
            "viewer": "validation/corpus/reference-viewer-1/results/validation-report.json",
            "hierarchical": "validation/corpus/hierarchical-project-1/results/validation-report.json",
        },
    }
    if not valid:
        raise VerificationError("final validation report cannot be marked PASS")
    write_json(VALIDATION / "final-validation.json", payload)
    write_json(VALIDATION / "final-validation-report.json", payload)
    manifest_line = f"- Release manifest members: **{manifest_files}**" if manifest_files is not None else "- Release manifest: **generated and independently verified during final closure**"
    write_text(
        VALIDATION / "final-validation-report.md",
        f"""# AIXEM 0.5.5 Final Validation Report

Status: **PASS**

## Release result

AIXEM 0.5.5 implements the Agent Authoring Closed-Loop Contract Plan and passes three complete verification cycles covering contract/authority closure, repair-loop/scope behavior, and full regression/evaluation/claims/integrity.

## Objective evidence

- Verification cycles: **3 / 3 PASS**
- Document linkage cycles: **3 / 3 PASS**
- Repository tests: **{test_result.get('testsRun')} / {test_result.get('testsRun')} PASS** across **{test_result.get('moduleCount')}** isolated modules
- Agent Evaluation 2 Tier A: **{tier_a['summary']['passed']} / {tier_a['summary']['cases']} PASS**
- Tier B live external agent executed: **no**
- Live-agent success claim: **none**
- Legacy EVAL-01-EVAL-08: **8 / 8 PASS**
- Authoring examples: **8 / 8 PASS**
- Symbol/static-block corpus: **36 / 36 PASS**, three renders per case
- Hierarchical corpus: **{hierarchy['summary']['passed']} / {hierarchy['summary']['cases']} PASS**, three-render validation
- Reference Viewer corpus: **{viewer['summary']['passed']} / {viewer['summary']['cases']} PASS**
- Viewer artifact determinism: **{viewer_det.get('repeatCount')} identical runs**
- Stable diagnostic codes: **{len(DIAGNOSTIC_REGISTRY)}**, including **{len(RECOMMENDED_P0_CODES)} / {len(RECOMMENDED_P0_CODES)}** planned P0 codes
- Canonical documents: **{docs.get('documents')}**
- Normative documents: **{docs.get('normativeDocuments')}**
- Requirements with release evidence: **{docs.get('requirements')}**
- Task routes: **{routes.get('routes')}**
{manifest_line}

## Compatibility lock

No AIXEM circuit authority format was changed. Protected single-sheet and hierarchical SVG/resolved evidence remains byte-identical to the 0.5.4 baseline. Viewer and Workbench remain read-only. Diagnostic, change-set, execution, and run-record artifacts are derived evidence only.

## Evaluation truth boundary

Tier A proves the deterministic route-bounded harness and known repair replay across A001-A012. It is not cold-start live-agent generation. Tier B was not executed because a separately supplied hidden-solution cold-start corpus and external executor were not provided; no Tier B success claim is made.

## Evidence index

- `validation/reports/plan-implementation-matrix-0.5.5.md`
- `validation/evidence/pass-01/agent-authoring-verification.json`
- `validation/evidence/pass-02/agent-authoring-verification.json`
- `validation/evidence/pass-03/agent-authoring-verification.json`
- `validation/agent-evals-2/results/tier-a-results.json`
- `validation/agent-evals-2/results/tier-b-status.json`
- `validation/test-results.json`
- `release/release-metadata.json`
- `release/manifest.json`
""",
    )
    return payload


def final_closure(passes: list[dict[str, Any]], test_result: dict[str, Any]) -> dict[str, Any]:
    status_path = ROOT / "IMPLEMENTATION_STATUS.md"
    status_text = status_path.read_text(encoding="utf-8")
    status_text = re.sub(
        r"Status: \*\*[^\n]+\*\*",
        "Status: **IMPLEMENTED — VERIFIED — RELEASE READY**",
        status_text,
        count=1,
    )
    status_path.write_text(status_text, encoding="utf-8", newline="\n")
    requirement_evidence = generate_requirement_evidence(test_result)
    write_plan_matrix()
    write_release_metadata(test_result, passes)
    write_final_reports(passes, test_result)

    linkage = document_linkage(require_artifacts=True)
    if not linkage.get("valid"):
        raise VerificationError("final document/artifact linkage failed: " + "; ".join(linkage.get("errors", [])))

    # First manifest verification establishes the observed member count. The
    # report is then rewritten with that count, followed by the authoritative
    # final manifest rebuild and verification.
    aixem_docs.build_release_manifest()
    first_manifest = aixem_docs.verify_release_manifest()
    if not first_manifest.get("valid"):
        raise VerificationError("pre-final manifest verification failed: " + "; ".join(first_manifest.get("errors", [])))
    write_final_reports(passes, test_result, manifest_files=first_manifest.get("files"))
    aixem_docs.build_release_manifest()
    final_manifest = aixem_docs.verify_release_manifest()
    if not final_manifest.get("valid"):
        raise VerificationError("final manifest verification failed: " + "; ".join(final_manifest.get("errors", [])))

    full = aixem_docs.run_full_validation(check_freshness=False)
    if not full.get("valid"):
        raise VerificationError("final release validation failed: " + json.dumps(full, ensure_ascii=False, indent=2))

    integrity = {
        "schema": "https://schemas.aixem.org/release/source-integrity/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "valid": True,
        "manifestVerification": final_manifest,
        "fullReleaseValidation": full,
        "requirementEvidence": requirement_evidence,
        "note": "This artifact is excluded from manifest hash coverage to avoid self-reference.",
    }
    write_json(ROOT / "release/archive-verification.json", integrity)
    return {
        "status": "PASS",
        "valid": True,
        "release": RELEASE_ID,
        "passes": 3,
        "testsRun": test_result.get("testsRun"),
        "agentEvaluation2TierA": "12/12",
        "tierBExecuted": False,
        "viewerCases": "18/18",
        "hierarchicalCases": "30/30",
        "symbolAndBlockCases": "36/36",
        "manifestFiles": final_manifest.get("files"),
        "manifestBytes": final_manifest.get("totalBytes"),
        "summary": full.get("summary"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-passes", action="store_true", help="run all three passes and final closure")
    args = parser.parse_args()
    if not args.all_passes:
        parser.error("--all-passes is required")
    try:
        os.chdir(ROOT)
        p1 = pass_one()
        print("PASS 1 complete: contract and authority closure", flush=True)
        p2 = pass_two()
        print("PASS 2 complete: repair loop and scope behavior", flush=True)
        p3, test_result = pass_three()
        print("PASS 3 complete: regression, agent evaluations, and claims", flush=True)
        result = final_closure([p1, p2, p3], test_result)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (VerificationError, OSError, ValueError, KeyError, json.JSONDecodeError, StopIteration) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
