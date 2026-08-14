#!/usr/bin/env python3
"""Run three complete AIXEM 0.5.2 verification cycles and create a deterministic release package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for import_root in (ROOT, HERE):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import aixem_docs  # noqa: E402

RELEASE_ID = "AIXEM-SRP-0.5.2-2026-08-11"
FIXED_TIME = "2026-08-11T00:00:00Z"
VALIDATION = ROOT / "validation"
EVIDENCE = VALIDATION / "evidence" / "0.5.2"
REPORTS = VALIDATION / "reports"
RELEASE = ROOT / "release"
SYMBOL_CORPUS = VALIDATION / "corpus" / "symbol-expressiveness-1"
B2D_CORPUS = VALIDATION / "corpus" / "static-2d-block-1"
EXTERNAL_ARCHIVE = Path("/mnt/data/aixem-schematic-reference-platform-0.5.2-2026-08-11.zip")
BASELINE_SCHEMA_DIGEST = "sha256:ba4d442591f6e53daf07f9d8f85e2026043f4e93ae0710e2578447dd3c466831"
BASELINE_STYLE_DIGEST = "sha256:ee4bcad451b37f6e998768c378a3c5a82217619c9b35a9962d6c696cb46db393"
BASELINE_RENDER_PROJECT_DIGEST = "sha256:8adda99a19b511ad20a6bd072eb67a0944b3b4c236bffe6359a173604df69e1c"
BASELINE_COMPONENT_CORE_DIGEST = "sha256:dfd5cc216de63637459f1cef87813cba52760b79a8095efa2e7c3c8705784100"


class ReleaseError(RuntimeError):
    """Fail-closed AIXEM 0.5.2 release error."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if check and proc.returncode != 0:
        raise ReleaseError(
            f"command failed ({proc.returncode}): {' '.join(command)}\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc


def parse_json_stdout(proc: subprocess.CompletedProcess[str], label: str) -> dict[str, Any]:
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ReleaseError(f"{label} did not emit valid JSON: {exc}\n{proc.stdout}") from exc


def locate_baseline(explicit: Path | None) -> Path:
    candidates = [
        explicit,
        Path("/mnt/data/aixem-schematic-reference-platform-0.5.1-2026-08-11(1).zip"),
        Path("/mnt/data/aixem-schematic-reference-platform-0.5.1-2026-08-11.zip"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate.resolve()
    raise ReleaseError("AIXEM 0.5.1 baseline ZIP was not found")


def zip_inventory(path: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ReleaseError(f"baseline ZIP integrity failed at {bad}")
        names = [name for name in archive.namelist() if not name.endswith("/")]
        top = {PurePosixPath(name).parts[0] for name in names}
        if len(top) != 1:
            raise ReleaseError(f"baseline ZIP must have one root, observed {sorted(top)}")
        root_name = next(iter(top))
        for name in sorted(names):
            data = archive.read(name)
            rel = PurePosixPath(name).relative_to(root_name).as_posix()
            records.append({
                "path": rel,
                "bytes": len(data),
                "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
            })
    return {
        "schema": "https://schemas.aixem.org/validation/baseline-inventory/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "baselineVersion": "0.5.1",
        "baselineArchive": path.name,
        "baselineArchiveDigest": aixem_docs.sha256_file(path),
        "root": root_name,
        "summary": {"files": len(records), "bytes": sum(item["bytes"] for item in records)},
        "files": records,
    }


def baseline_member_digest(path: Path, suffix: str) -> str:
    with zipfile.ZipFile(path) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        if len(matches) != 1:
            raise ReleaseError(f"baseline member resolution failed for {suffix}: {matches}")
        return "sha256:" + hashlib.sha256(archive.read(matches[0])).hexdigest()


def build_baseline_evidence(path: Path) -> dict[str, Any]:
    inventory = zip_inventory(path)
    write_json(EVIDENCE / "baseline-0.5.1-inventory.json", inventory)
    contracts = {
        "symbolSchema": {
            "path": "docs/specifications/schemas/component-graphics-1/aixem-symbol-asset-1.schema.json",
            "baseline": baseline_member_digest(path, "docs/specifications/schemas/component-graphics-1/aixem-symbol-asset-1.schema.json"),
            "current": aixem_docs.sha256_file(ROOT / "docs/specifications/schemas/component-graphics-1/aixem-symbol-asset-1.schema.json"),
            "classification": "unchanged",
        },
        "styleProfile": {
            "path": "profiles/aixem-grid-schematic-style-1.aixstyle.json",
            "baseline": baseline_member_digest(path, "profiles/aixem-grid-schematic-style-1.aixstyle.json"),
            "current": aixem_docs.sha256_file(ROOT / "profiles/aixem-grid-schematic-style-1.aixstyle.json"),
            "classification": "unchanged",
        },
        "renderProject": {
            "path": "implementation/schematic/render_project.py",
            "baseline": baseline_member_digest(path, "implementation/schematic/render_project.py"),
            "current": aixem_docs.sha256_file(ROOT / "implementation/schematic/render_project.py"),
            "classification": "unchanged",
        },
        "componentCore": {
            "path": "implementation/schematic/component_core.py",
            "baseline": baseline_member_digest(path, "implementation/schematic/component_core.py"),
            "current": aixem_docs.sha256_file(ROOT / "implementation/schematic/component_core.py"),
            "classification": "F3 renderer defect repair: explicit deterministic dimension-label text styling",
        },
    }
    errors: list[str] = []
    expected = {
        "symbolSchema": BASELINE_SCHEMA_DIGEST,
        "styleProfile": BASELINE_STYLE_DIGEST,
        "renderProject": BASELINE_RENDER_PROJECT_DIGEST,
        "componentCore": BASELINE_COMPONENT_CORE_DIGEST,
    }
    for name, expected_digest in expected.items():
        if contracts[name]["baseline"] != expected_digest:
            errors.append(f"unexpected 0.5.1 baseline digest for {name}")
    for name in ("symbolSchema", "styleProfile", "renderProject"):
        if contracts[name]["baseline"] != contracts[name]["current"]:
            errors.append(f"frozen contract drift: {name}")
    if contracts["componentCore"]["baseline"] == contracts["componentCore"]["current"]:
        errors.append("dimension-label renderer repair is not present")
    payload = {
        "schema": "https://schemas.aixem.org/validation/contract-baseline/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "valid": not errors,
        "contracts": contracts,
        "coreFormatExtension": False,
        "newPrimitive": False,
        "multiUnitExtension": False,
        "errors": errors,
    }
    write_json(EVIDENCE / "baseline-0.5.1-contract-digests.json", payload)
    if errors:
        raise ReleaseError("baseline contract verification failed: " + "; ".join(errors))
    return payload


def assert_corpus(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload["summary"]
    errors: list[str] = []
    if len(payload.get("cases", [])) != 36:
        errors.append("corpus invocation did not cover 36 cases")
    if summary["S-Core"]["status"] != "PASS":
        errors.append("S-Core failed")
    if summary["S-Extended"]["status"] != "PASS":
        errors.append("S-Extended failed")
    if summary["B2D"]["status"] != "PASS":
        errors.append("B2D failed")
    if summary["MU"].get("result") != "NOT_SUPPORTED" or summary["MU"].get("valid") is not True:
        errors.append("MU result is not the expected valid NOT_SUPPORTED boundary")
    if any(item.get("automatedStatus") != "PASS" for item in payload.get("cases", [])):
        errors.append("one or more automated case gates failed")
    if any(item.get("approvedDigestStatus") != "PASS" for item in payload.get("cases", [])):
        errors.append("one or more approved render digests failed")
    if any(item.get("visualReview", {}).get("status") != "PASS" for item in payload.get("cases", [])):
        errors.append("one or more visual reviews failed")
    if any(item.get("render", {}).get("deterministic") is not True for item in payload.get("cases", [])):
        errors.append("one or more render results are not deterministic")
    if errors:
        raise ReleaseError("corpus gate failed: " + "; ".join(errors))
    return {
        "valid": True,
        "cases": len(payload["cases"]),
        "S-Core": summary["S-Core"],
        "S-Extended": summary["S-Extended"],
        "MU": summary["MU"],
        "B2D": summary["B2D"],
    }


def visual_review_integrity() -> dict[str, Any]:
    errors: list[str] = []
    total = 0
    modes: set[str] = set()
    for root in (SYMBOL_CORPUS, B2D_CORPUS):
        manifest = read_json(root / "manifest.json")
        approved = read_json(root / "expected" / "approved-render-digests.json")["cases"]
        review = read_json(root / "results" / "visual-review.json")
        modes.add(str(review.get("reviewMethod", "")))
        expected_ids = {item["id"] for item in manifest["cases"]}
        records = review.get("cases", {})
        if set(records) != expected_ids:
            errors.append(f"{root.name}: visual-review inventory mismatch")
        for case_id in sorted(expected_ids):
            total += 1
            record = records.get(case_id, {})
            baseline = approved.get(case_id, {})
            if record.get("result") != "PASS":
                errors.append(f"{case_id}: visual review is not PASS")
            if record.get("sourceDigest") != baseline.get("sourceDigest"):
                errors.append(f"{case_id}: visual source digest is stale")
            if record.get("svgDigest") != baseline.get("svgDigest"):
                errors.append(f"{case_id}: visual SVG digest is stale")
            if not record.get("checks") or not all(record["checks"].values()):
                errors.append(f"{case_id}: visual checks are incomplete")
        if "AI-assisted" not in str(review.get("reviewMethod", "")):
            errors.append(f"{root.name}: AI-assisted review method is not disclosed")
        if "third-party certification is outside" not in str(review.get("certificationBoundary", "")):
            errors.append(f"{root.name}: certification boundary is not disclosed")
    return {"valid": not errors, "cases": total, "reviewMethods": sorted(modes), "errors": errors}


def agent_route_integrity() -> dict[str, Any]:
    documents = aixem_docs.load_documents()
    routes = aixem_docs.load_routes()
    route_validation = aixem_docs.validate_routes(routes, documents)
    result = aixem_docs.route_query("validate symbol expressiveness")
    route = result.get("route") or {}
    errors = list(route_validation.get("errors", []))
    if route.get("id") != "validate-symbol-expressiveness" or result.get("fallbackUsed"):
        errors.append("validate-symbol-expressiveness did not resolve exactly")
    computed = route.get("computed", {})
    budget = route.get("budget", {})
    if computed.get("documents", 999) > budget.get("max_documents", 0):
        errors.append("route document budget exceeded")
    if computed.get("bytes", 999999) > budget.get("max_bytes", 0):
        errors.append("route byte budget exceeded")
    docs = [step.get("document") for step in route.get("steps", [])]
    if "AIXEM-EXAMPLE-SYMBOL-CORPUS-001" not in docs:
        errors.append("nearest-corpus construction index is absent from route")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    if "Nearest validated corpus pattern first" not in agents:
        errors.append("AGENTS.md lacks nearest-corpus rule")
    return {"valid": not errors, "route": route.get("id"), "computed": computed, "errors": errors}


def claim_integrity() -> dict[str, Any]:
    targets = [ROOT / "README.md", ROOT / "RELEASE_NOTES.md", ROOT / "IMPLEMENTATION_STATUS.md"]
    errors: list[str] = []
    pattern = re.compile(r"\b(?:fully\s+|native\s+)?(?:kicad|orcad|dwg|dxf)\s+(?:compatible|compatibility)\b", re.IGNORECASE)
    for path in targets:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line) and not any(term in line.lower() for term in ("not ", "does not", "no ", "exclusion", "explicit")):
                errors.append(f"{path.name}:{number}: unsupported compatibility claim")
    reports = [
        read_json(REPORTS / "symbol-expressiveness-0.5.2.json"),
        read_json(REPORTS / "static-2d-block-0.5.2.json"),
        read_json(REPORTS / "multi-unit-capability-0.5.2.json"),
    ]
    if reports[0]["summary"]["S-Core"]["status"] != "PASS":
        errors.append("public S-Core claim lacks PASS evidence")
    if reports[0]["summary"]["S-Extended"]["status"] != "PASS":
        errors.append("public S-Extended claim lacks PASS evidence")
    if reports[1]["summary"]["status"] != "PASS":
        errors.append("public B2D claim lacks PASS evidence")
    if reports[2]["result"] != "NOT_SUPPORTED":
        errors.append("MU limitation is not published independently")
    return {"valid": not errors, "filesScanned": len(targets), "errors": errors}


def generated_reproducibility() -> dict[str, Any]:
    run([sys.executable, str(HERE / "build_all.py")])
    first = aixem_docs.generated_digest_map()
    run([sys.executable, str(HERE / "build_all.py")])
    second = aixem_docs.generated_digest_map()
    changed = sorted(path for path in set(first) | set(second) if first.get(path) != second.get(path))
    return {"valid": not changed, "files": len(second), "changed": changed}


def run_cycle(index: int) -> dict[str, Any]:
    cycle_dir = EVIDENCE / f"verification-cycle-{index:02d}"
    cycle_dir.mkdir(parents=True, exist_ok=True)
    print(f"[AIXEM 0.5.2] verification cycle {index}: representability", flush=True)

    pass1_path = cycle_dir / "pass-01-corpus.json"
    run([
        sys.executable, str(ROOT / "tools" / "validate_symbol_corpus.py"),
        "--all", "--repeat", "1", "--json-out", str(pass1_path),
    ])
    pass1_corpus = assert_corpus(read_json(pass1_path))
    contract = read_json(EVIDENCE / "baseline-0.5.1-contract-digests.json")
    pass1 = {
        "schema": "https://schemas.aixem.org/validation/0.5.2/pass-01/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "cycle": index,
        "valid": pass1_corpus["valid"] and contract["valid"],
        "focus": "representability and coverage",
        "corpus": pass1_corpus,
        "contractFreeze": contract,
        "unclassifiedFailures": 0,
        "coreFormatExtension": False,
    }
    write_json(cycle_dir / "pass-01-representability.json", pass1)
    if not pass1["valid"]:
        raise ReleaseError(f"cycle {index} PASS 1 failed")

    print(f"[AIXEM 0.5.2] verification cycle {index}: quality and agent usability", flush=True)
    run([sys.executable, str(HERE / "build_all.py")])
    authoring = parse_json_stdout(run([sys.executable, str(HERE / "authoring_validation.py")]), "authoring validation")
    agent = parse_json_stdout(run([sys.executable, str(HERE / "run_agent_evals.py")]), "agent evaluation")
    visual = visual_review_integrity()
    route = agent_route_integrity()
    high_pin = {
        item["id"]: {
            "ports": item["static"]["portCount"],
            "visiblePorts": item["static"]["visiblePortCount"],
            "sceneStatistics": item["render"]["sceneStatistics"],
            "visual": item["visualReview"]["status"],
        }
        for item in read_json(pass1_path)["cases"] if item["id"] in {"S021", "S024"}
    }
    pass2_errors: list[str] = []
    if not authoring.get("valid"):
        pass2_errors.append("0.5.1 authoring baseline validation failed")
    if not agent.get("valid"):
        pass2_errors.append("agent route simulation failed")
    if not visual["valid"]:
        pass2_errors.extend(visual["errors"])
    if not route["valid"]:
        pass2_errors.extend(route["errors"])
    if set(high_pin) != {"S021", "S024"} or any(item["visual"] != "PASS" for item in high_pin.values()):
        pass2_errors.append("100-pin connector/MCU scale evidence is incomplete")
    pass2 = {
        "schema": "https://schemas.aixem.org/validation/0.5.2/pass-02/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "cycle": index,
        "valid": not pass2_errors,
        "focus": "visual quality, scale, and agent usability",
        "authoringBaseline": authoring,
        "agentEvaluation": agent,
        "visualReview": visual,
        "agentRoute": route,
        "highPinCount": high_pin,
        "errors": pass2_errors,
    }
    write_json(cycle_dir / "pass-02-quality-agent.json", pass2)
    if pass2_errors:
        raise ReleaseError(f"cycle {index} PASS 2 failed: {'; '.join(pass2_errors)}")

    print(f"[AIXEM 0.5.2] verification cycle {index}: regression and claim integrity", flush=True)
    pass3_path = cycle_dir / "pass-03-corpus-repeat-3.json"
    run([
        sys.executable, str(ROOT / "tools" / "validate_symbol_corpus.py"),
        "--all", "--repeat", "3", "--json-out", str(pass3_path),
    ])
    pass3_corpus = assert_corpus(read_json(pass3_path))
    test_path = VALIDATION / "test-results.json"
    run([sys.executable, str(HERE / "run_tests.py"), "--output", str(test_path)])
    tests = read_json(test_path)
    reproducibility = generated_reproducibility()
    docs = aixem_docs.validate_documents(aixem_docs.load_documents())
    site = aixem_docs.validate_site()
    claims = claim_integrity()
    schema_digest = aixem_docs.sha256_file(ROOT / "docs/specifications/schemas/component-graphics-1/aixem-symbol-asset-1.schema.json")
    pass3_errors: list[str] = []
    if not tests.get("successful") or tests.get("failures") or tests.get("errors"):
        pass3_errors.append("repository tests failed")
    if int(tests.get("testsRun", 0)) < 27:
        pass3_errors.append("expected at least 27 repository tests")
    if not reproducibility["valid"]:
        pass3_errors.append("generated artifacts are not reproducible")
    if not docs["valid"]:
        pass3_errors.extend(docs["errors"])
    if not site["valid"]:
        pass3_errors.extend(site["errors"])
    if not claims["valid"]:
        pass3_errors.extend(claims["errors"])
    if schema_digest != BASELINE_SCHEMA_DIGEST:
        pass3_errors.append("0.5.1 symbol schema changed")
    pass3 = {
        "schema": "https://schemas.aixem.org/validation/0.5.2/pass-03/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "cycle": index,
        "valid": not pass3_errors,
        "focus": "regression, determinism, compatibility, and claim integrity",
        "corpus": pass3_corpus,
        "tests": {"successful": tests.get("successful"), "testsRun": tests.get("testsRun"), "failures": tests.get("failures"), "errors": tests.get("errors")},
        "generatedReproducibility": reproducibility,
        "canonicalDocumentation": docs,
        "site": site,
        "claimIntegrity": claims,
        "symbolSchemaDigest": schema_digest,
        "errors": pass3_errors,
    }
    write_json(cycle_dir / "pass-03-regression-claims.json", pass3)
    if pass3_errors:
        raise ReleaseError(f"cycle {index} PASS 3 failed: {'; '.join(pass3_errors)}")

    summary = {
        "schema": "https://schemas.aixem.org/validation/0.5.2/verification-cycle/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "cycle": index,
        "valid": True,
        "passes": {
            "representabilityAndCoverage": "PASS",
            "qualityScaleAndAgentUsability": "PASS",
            "regressionDeterminismAndClaimIntegrity": "PASS",
        },
        "caseCount": 36,
        "testsRun": tests.get("testsRun"),
    }
    write_json(cycle_dir / "summary.json", summary)
    return summary


def write_failure_classification() -> None:
    payload = {
        "schema": "https://schemas.aixem.org/validation/failure-classification/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "unclassifiedFailures": 0,
        "records": [
            {
                "id": "AIXEM-052-F3-001",
                "class": "F3",
                "case": "B005",
                "symptom": "Static dimension labels inherited unsuitable SVG default text sizing.",
                "owner": "production renderer component primitive serialization",
                "resolution": "Emit explicit deterministic dimension-label fill, stroke, family, and 3 mm-equivalent SVG font size.",
                "coreFormatChange": False,
                "regressionTest": "tests/conformance/test_symbol_expressiveness_corpus.py::SymbolCorpusConformanceTests.test_dimension_label_regression_is_explicit_and_deterministic",
                "status": "closed",
            },
            {
                "id": "AIXEM-052-F5-001",
                "class": "F5",
                "case": "S030",
                "symptom": "The model cannot place multiple unit presentations sharing one semantic component identity and disjoint port subsets.",
                "owner": "future component/placement semantics",
                "resolution": "Publish MU as NOT_SUPPORTED; do not misuse variants or duplicate component entities; require a dedicated ADR before implementation.",
                "coreFormatChange": False,
                "status": "documented-not-implemented",
            },
        ],
        "F4GraphicalGaps": 0,
        "P2Decision": "NOT_TRIGGERED",
    }
    write_json(EVIDENCE / "failure-classification.json", payload)


def write_plan_matrix(cycles: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [
        ("P0.1", "Symbol Expressiveness Conformance Profile 1", "PASS", "docs/conformance/symbol-expressiveness.md"),
        ("P0.2", "24-case S-Core corpus", "PASS", "validation/corpus/symbol-expressiveness-1/manifest.json"),
        ("P0.3", "Case schema and machine-readable metadata", "PASS", "validation/corpus/symbol-expressiveness-1/schema/corpus-case-1.schema.json"),
        ("P0.4", "Production renderer batch harness", "PASS", "tools/validate_symbol_corpus.py"),
        ("P0.5", "Schema/binding/geometry/determinism/visual gates", "PASS", "validation/reports/symbol-expressiveness-0.5.2.json"),
        ("P0.6", "Capability and primitive matrices", "PASS", "validation/corpus/symbol-expressiveness-1/results/capability-matrix.json"),
        ("P0.7", "Claim boundaries and exclusions", "PASS", "docs/conformance/compatibility-conformance.md"),
        ("P0.8", "0.5.1 regression compatibility", "PASS", "validation/evidence/0.5.2/baseline-0.5.1-contract-digests.json"),
        ("P1.1", "Five complex/edge cases", "PASS", "validation/corpus/symbol-expressiveness-1/manifest.json"),
        ("P1.2", "S030 multi-unit capability probe", "PASS: NOT_SUPPORTED published", "validation/reports/multi-unit-capability-0.5.2.json"),
        ("P1.3", "Static 2D Block Profile and six cases", "PASS", "validation/reports/static-2d-block-0.5.2.json"),
        ("P1.4", "Agent route and cookbook integration", "PASS", "docs/_meta/routes/validate-symbol-expressiveness.yaml"),
        ("P2", "Conditional core extension", "NOT_TRIGGERED", "validation/evidence/0.5.2/failure-classification.json"),
        ("V1", "Verification cycle 1", "PASS", "validation/evidence/0.5.2/verification-cycle-01/summary.json"),
        ("V2", "Verification cycle 2", "PASS", "validation/evidence/0.5.2/verification-cycle-02/summary.json"),
        ("V3", "Verification cycle 3", "PASS", "validation/evidence/0.5.2/verification-cycle-03/summary.json"),
    ]
    payload = {
        "schema": "https://schemas.aixem.org/validation/plan-implementation-matrix/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "valid": len(cycles) >= 3 and all(item.get("valid") for item in cycles),
        "plan": "PLAN-0.5.2-SYMBOL-EXPRESSIVENESS-CONFORMANCE.md",
        "summary": {"items": len(rows), "pass": sum(status.startswith("PASS") for _, _, status, _ in rows), "notTriggered": 1, "cycles": len(cycles)},
        "items": [{"id": item_id, "requirement": requirement, "status": status, "evidence": evidence} for item_id, requirement, status, evidence in rows],
    }
    write_json(REPORTS / "plan-implementation-matrix-0.5.2.json", payload)
    lines = [
        "# AIXEM 0.5.2 Plan Implementation Matrix",
        "",
        f"Status: **{'PASS' if payload['valid'] else 'FAIL'}**",
        "",
        "| ID | Plan item | Status | Evidence |",
        "|---|---|---:|---|",
    ]
    for item_id, requirement, status, evidence in rows:
        lines.append(f"| {item_id} | {requirement} | **{status}** | `{evidence}` |")
    write_text(REPORTS / "plan-implementation-matrix-0.5.2.md", "\n".join(lines))
    return payload


def write_release_metadata(cycles: list[dict[str, Any]]) -> dict[str, Any]:
    documents = aixem_docs.load_documents()
    routes = aixem_docs.load_routes()
    site = aixem_docs.validate_site()
    metadata = {
        "schema": "https://schemas.aixem.org/release/metadata/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "version": "0.5.2",
        "releaseDate": "2026-08-11",
        "language": "en",
        "status": "final",
        "canonicalDocumentationRoot": "docs/",
        "staticSiteEntrypoint": "site/index.html",
        "agentEntrypoint": "AGENTS.md",
        "routeIndex": "docs/_meta/generated/route-index.json",
        "validationReport": "validation/final-validation-report.md",
        "conformance": {
            "S-Core": "PASS",
            "S-Extended": "PASS",
            "MU": "NOT_SUPPORTED",
            "B2D": "PASS",
            "verificationCycles": len(cycles),
        },
        "statistics": {
            "canonicalDocuments": len(documents),
            "normativeDocuments": sum(doc.meta.get("status") == "normative" for doc in documents),
            "taskRoutes": len(routes),
            "sitePages": site.get("pages", 0),
            "symbolCases": 30,
            "staticBlockCases": 6,
            "repositoryTests": read_json(VALIDATION / "test-results.json").get("testsRun", 0),
        },
        "compatibility": {
            "symbolSchemaChangedFrom051": False,
            "newPrimitive": False,
            "multiUnitExtension": False,
            "nativeKiCadOrOrCADCompatibilityClaim": False,
            "nativeDwgDxfCompatibilityClaim": False,
            "dynamicBlockCompatibilityClaim": False,
        },
        "reviewBoundary": "Digest-bound AI-assisted internal release-candidate review; no independent human or third-party certification is claimed.",
    }
    write_json(RELEASE / "release-metadata.json", metadata)
    return metadata


def write_final_report(cycles: list[dict[str, Any]], plan: dict[str, Any]) -> None:
    tests = read_json(VALIDATION / "test-results.json")
    contract = read_json(EVIDENCE / "baseline-0.5.1-contract-digests.json")
    lines = [
        "# AIXEM 0.5.2 Final Validation Report",
        "",
        "Status: **PASS**",
        "",
        f"Release: `{RELEASE_ID}`",
        "",
        "## Conformance results",
        "",
        "| Tier | Result | Evidence |",
        "|---|---:|---|",
        "| S-Core | **PASS** — 24/24 | `validation/reports/symbol-expressiveness-0.5.2.json` |",
        "| S-Extended | **PASS** — 5/5 plus Core | `validation/reports/symbol-expressiveness-0.5.2.json` |",
        "| MU | **NOT_SUPPORTED** — valid independent result | `validation/reports/multi-unit-capability-0.5.2.json` |",
        "| B2D | **PASS** — 6/6 | `validation/reports/static-2d-block-0.5.2.json` |",
        "",
        "## Three complete verification cycles",
        "",
        "Each cycle independently executed representability/coverage, visual quality/scale/agent usability, and regression/repeat-determinism/claim-integrity passes.",
        "",
        "| Cycle | PASS 1 | PASS 2 | PASS 3 |",
        "|---:|---:|---:|---:|",
    ]
    for cycle in cycles:
        lines.append(f"| {cycle['cycle']} | PASS | PASS | PASS |")
    lines.extend([
        "",
        "## Regression and conservative-extension result",
        "",
        f"- Repository tests: **{tests.get('testsRun', 0)}/{tests.get('testsRun', 0)} PASS**.",
        f"- Symbol schema: **unchanged** at `{contract['contracts']['symbolSchema']['current']}`.",
        "- Style profile and production project renderer entry point: **unchanged**.",
        "- New primitive or top-level symbol field: **none**.",
        "- Conditional P2 extension: **NOT_TRIGGERED**.",
        "- Closed defect: B005 dimension label browser-default sizing, classified F3 and protected by regression test.",
        "- Multi-unit semantic gap: documented as F5; no variant or duplicate-entity simulation accepted.",
        "",
        "## Review boundary",
        "",
        "All 36 cases have digest-bound AI-assisted structured visual review records. This is internal release-candidate evidence and is not represented as independent human or third-party certification.",
        "",
        "## Claim boundary",
        "",
        "The release proves only the AIXEM-owned S-Core, S-Extended, MU, and B2D results above. It does not claim native KiCad, OrCAD, DWG, DXF, AutoCAD Dynamic Block, 3D CAD, PCB footprint, or SPICE compatibility.",
        "",
        "## Plan closure",
        "",
        f"The implementation matrix contains {plan['summary']['items']} plan items and records all mandatory P0/P1 work as complete. P2 is not triggered because no F4 graphical gap was proven.",
    ])
    write_text(VALIDATION / "final-validation-report.md", "\n".join(lines))
    write_json(VALIDATION / "final-validation-report.json", {
        "schema": "https://schemas.aixem.org/validation/final-report/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "valid": True,
        "results": {"S-Core": "PASS", "S-Extended": "PASS", "MU": "NOT_SUPPORTED", "B2D": "PASS"},
        "verificationCycles": cycles,
        "testsRun": tests.get("testsRun", 0),
        "planMatrix": "validation/reports/plan-implementation-matrix-0.5.2.json",
        "schemaChangedFrom051": False,
        "P2": "NOT_TRIGGERED",
    })


def cleanup_non_release_artifacts() -> None:
    for name in ("corpus-bootstrap-0.5.2.json", "corpus-post-renderer-fix-0.5.2.json"):
        (REPORTS / name).unlink(missing_ok=True)
    for path in ROOT.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)
    for path in ROOT.rglob("*.pyc"):
        path.unlink(missing_ok=True)
    (RELEASE / "manifest.json").unlink(missing_ok=True)
    (RELEASE / "archive-verification.json").unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, help="Optional explicit AIXEM 0.5.1 baseline ZIP")
    parser.add_argument("--attempts", type=int, default=3, help="Number of complete verification cycles; release minimum is three")
    parser.add_argument("--package", action="store_true", help="Create and externally verify the deterministic ZIP")
    args = parser.parse_args()
    if args.attempts < 3:
        parser.error("AIXEM 0.5.2 release closure requires at least three complete verification cycles")

    cleanup_non_release_artifacts()
    baseline = locate_baseline(args.baseline)
    build_baseline_evidence(baseline)
    write_failure_classification()

    # Canonical reports are generated once before cycle-level verification.
    run([sys.executable, str(ROOT / "tools" / "validate_symbol_corpus.py"), "--all", "--repeat", "3", "--emit-report"])

    cycles = [run_cycle(index) for index in range(1, args.attempts + 1)]
    verification = {
        "schema": "https://schemas.aixem.org/validation/0.5.2/verification-summary/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "valid": len(cycles) >= 3 and all(item.get("valid") for item in cycles),
        "cyclesRequired": 3,
        "cyclesCompleted": len(cycles),
        "cycles": cycles,
    }
    write_json(EVIDENCE / "verification-summary.json", verification)
    plan = write_plan_matrix(cycles)

    # Final canonical publication and tests occur after all evidence exists.
    run([sys.executable, str(HERE / "build_all.py")])
    run([sys.executable, str(HERE / "run_tests.py"), "--output", str(VALIDATION / "test-results.json")])
    write_release_metadata(cycles)
    write_final_report(cycles, plan)
    cleanup_non_release_artifacts()

    # Regenerate publication once more after top-level release records are finalized.
    run([sys.executable, str(HERE / "build_all.py")])
    run([sys.executable, str(HERE / "run_tests.py"), "--output", str(VALIDATION / "test-results.json")])
    if not read_json(VALIDATION / "test-results.json").get("successful"):
        raise ReleaseError("final repository test run failed")

    # Final report records the final test count; rewrite it after the last test run.
    write_final_report(cycles, plan)
    cleanup_non_release_artifacts()
    manifest = aixem_docs.build_release_manifest()
    manifest_check = aixem_docs.verify_release_manifest()
    if not manifest_check["valid"]:
        raise ReleaseError("release manifest failed: " + "; ".join(manifest_check["errors"]))

    outcome: dict[str, Any] = {
        "release": RELEASE_ID,
        "valid": True,
        "verificationCycles": len(cycles),
        "manifestFiles": manifest["fileCount"],
        "manifestDigest": aixem_docs.sha256_file(RELEASE / "manifest.json"),
    }
    if args.package:
        archive = aixem_docs.deterministic_zip(ROOT, EXTERNAL_ARCHIVE)
        archive_check = aixem_docs.verify_archive(EXTERNAL_ARCHIVE)
        if not archive_check["valid"]:
            raise ReleaseError("archive verification failed: " + "; ".join(archive_check["errors"]))
        checksum_path = EXTERNAL_ARCHIVE.with_suffix(EXTERNAL_ARCHIVE.suffix + ".sha256")
        checksum_path.write_text(f"{archive['digest'].removeprefix('sha256:')}  {EXTERNAL_ARCHIVE.name}\n", encoding="utf-8", newline="\n")
        verification_path = EXTERNAL_ARCHIVE.with_suffix(EXTERNAL_ARCHIVE.suffix + ".verification.json")
        write_json(verification_path, {
            "schema": "https://schemas.aixem.org/release/external-archive-verification/1",
            "formatVersion": "1.0",
            "release": RELEASE_ID,
            "generatedAt": FIXED_TIME,
            "valid": True,
            "archive": archive,
            "verification": archive_check,
            "internalManifestDigest": outcome["manifestDigest"],
            "verificationCycles": len(cycles),
        })
        outcome.update({
            "archive": archive,
            "archiveVerification": archive_check,
            "checksumPath": str(checksum_path),
            "verificationPath": str(verification_path),
        })
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
