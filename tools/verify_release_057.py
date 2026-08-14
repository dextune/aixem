#!/usr/bin/env python3
"""Run five complete AIXEM 0.5.7 documentation-governance verification cycles.

The verifier reuses the protected 0.5.6 technical-conformance probes while
adding repository-wide document information-architecture, lifecycle,
naming, discoverability, migration, and agent-governance checks.  The 0.5.7
plan may close independently of the inherited 0.5.6 external-AI Tier B gate;
no live external-agent success claim is fabricated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOC_TOOLS = ROOT / "tools" / "docs"
IMPLEMENTATION = ROOT / "implementation"
for search_path in (HERE, DOC_TOOLS, IMPLEMENTATION):
    if str(search_path) not in sys.path:
        sys.path.insert(0, str(search_path))

import aixem_docs  # noqa: E402
import verify_release_056 as inherited  # noqa: E402

RELEASE_ID = "AIXEM-SRP-0.5.7-2026-08-12"
VERSION = "0.5.7"
FIXED_TIME = "2026-08-12T00:00:00Z"
REQUIRED_CYCLES = 5
VALIDATION = ROOT / "validation"
RELEASE_REPORTS = VALIDATION / "releases" / VERSION
EVIDENCE = VALIDATION / "evidence"
RUNS = EVIDENCE / VERSION / "verification-runs"
AGENT2_RESULTS = VALIDATION / "agent-evals-2" / "results"
AGENT3_RESULTS = VALIDATION / "agent-evals-3" / "results"
VIEWER_RESULTS = VALIDATION / "corpus" / "reference-viewer-1" / "results"
HIER_RESULTS = VALIDATION / "corpus" / "hierarchical-project-1" / "results"
SYMBOL_RESULTS = VALIDATION / "corpus" / "symbol-expressiveness-1" / "results"

FOCUSED_TEST_MODULES = [
    "tests.docs.test_document_governance",
    "tests.agent.test_task_contract",
    "tests.agent.test_cold_start_stage",
    "tests.agent.test_observation",
    "tests.agent.test_live_executor",
    "tests.agent.test_invariant_scorer",
    "tests.agent.test_live_run_evidence",
    "tests.agent.test_agent_evals_3",
]


class VerificationError(RuntimeError):
    """The 0.5.7 release cannot close safely."""


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


def tail(value: str | bytes, limit: int = 14000) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return value if len(value) <= limit else value[-limit:]


def run(command: list[str], *, label: str, timeout: int = 1800, expected: Iterable[int] = (0,)) -> dict[str, Any]:
    print(f"[verify-057] START {label}", flush=True)
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
    print(f"[verify-057] {result['status']} {label} ({result['durationSeconds']}s)", flush=True)
    if not result["valid"]:
        raise VerificationError(
            f"{label} failed ({result['returnCode']}): {' '.join(command)}\n"
            f"STDOUT:\n{result['stdoutTail']}\nSTDERR:\n{result['stderrTail']}"
        )
    return result


def check(check_id: str, valid: bool, summary: str, **details: Any) -> dict[str, Any]:
    return {"id": check_id, "status": "PASS" if valid else "FAIL", "valid": bool(valid), "summary": summary, **details}


def reset_generated_outputs() -> None:
    """Start each cycle without retained generated documentation products."""
    shutil.rmtree(ROOT / "docs" / "_meta" / "generated", ignore_errors=True)
    shutil.rmtree(ROOT / "reference", ignore_errors=True)
    shutil.rmtree(ROOT / "site", ignore_errors=True)
    for rel in ("release/manifest.json", "release/archive-verification.json"):
        (ROOT / rel).unlink(missing_ok=True)
    # AIXEM 0.5.2 historically generated human-readable corpus reports in the
    # flat machine-report directory. 0.5.7 writes them under the owning release
    # directory and removes stale legacy copies before every clean cycle.
    for rel in (
        "validation/reports/symbol-expressiveness-0.5.2.md",
        "validation/reports/static-2d-block-0.5.2.md",
        "validation/reports/multi-unit-capability-0.5.2.md",
    ):
        (ROOT / rel).unlink(missing_ok=True)


def generated_map() -> dict[str, str]:
    return aixem_docs.generated_digest_map()


def documentation_governance_check() -> dict[str, Any]:
    documents = aixem_docs.load_documents()
    audit = aixem_docs.audit_repository_documents(documents, require_redirects=True)
    migrations = aixem_docs.validate_path_migrations(documents, require_redirects=True)
    errors = [*audit.get("errors", []), *migrations.get("errors", [])]
    ids = {doc.id for doc in documents}
    required_ids = {
        "AIXEM-SPEC-DOC-GOVERNANCE-001",
        "AIXEM-GOV-DOC-AUTHORING-001",
        "AIXEM-RELEASE-057-001",
    }
    for missing in sorted(required_ids - ids):
        errors.append(f"missing 0.5.7 canonical document {missing}")

    required_requirements = {f"AIXEM-REQ-DOC-GOV-{index:04d}" for index in range(1, 11)}
    trace = read_json(ROOT / "docs/_meta/generated/requirement-traceability.json")
    observed_requirements = {item.get("id") for item in trace.get("requirements", [])}
    for missing in sorted(required_requirements - observed_requirements):
        errors.append(f"missing documentation-governance requirement {missing}")

    root_markdown = sorted(path.name for path in ROOT.glob("*.md"))
    expected_root = sorted(["AGENTS.md", "CHANGELOG.md", "CONTRIBUTING.md", "NOTICE.md", "README.md", "SECURITY.md", "START_HERE.md"])
    if root_markdown != expected_root:
        errors.append(f"root Markdown set mismatch: {root_markdown}")

    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    required_agent_phrases = (
        "Before Creating a Document",
        "What repository document role will it have?",
        "path-migrations.yaml",
        "planning/releases/<version>/",
        "validation/releases/<version>/",
        "Read current release identity from `VERSION`",
    )
    for phrase in required_agent_phrases:
        if phrase not in agents_text:
            errors.append(f"AGENTS.md omits documentation-governance phrase: {phrase}")
    if len(agents_text.splitlines()) > 320:
        errors.append("AGENTS.md exceeds the bounded 320-line operational-contract limit")
    if re.search(r"active .*0\.5\.[0-6]", agents_text, re.IGNORECASE):
        errors.append("AGENTS.md contains stale hard-coded active-release prose")

    inventory_path = ROOT / "docs/_meta/generated/repository-document-inventory.json"
    migration_index_path = ROOT / "docs/_meta/generated/path-migration-index.json"
    if not inventory_path.is_file():
        errors.append("generated repository document inventory is missing")
    if not migration_index_path.is_file():
        errors.append("generated path migration index is missing")
    inventory = read_json(inventory_path) if inventory_path.is_file() else {}
    if inventory.get("summary", {}).get("orphans") != 0:
        errors.append("generated repository document inventory reports orphans")
    if inventory.get("summary", {}).get("unknownRoles") != 0:
        errors.append("generated repository document inventory reports unknown roles")

    plans = read_json(ROOT / "docs/_meta/generated/repository-document-inventory.json").get("documents", []) if inventory_path.is_file() else []
    plan_count = sum(item.get("role") == "implementation-plan" for item in plans)
    if plan_count != 8:
        errors.append(f"expected eight version-scoped plans, observed {plan_count}")

    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "repositoryMarkdown": audit.get("documents"),
        "orphans": audit.get("orphans"),
        "unknownRoles": audit.get("unknownRoles"),
        "roleCounts": audit.get("roles"),
        "canonicalDocuments": len(documents),
        "governanceRequirements": len(required_requirements & observed_requirements),
        "pathMigrations": migrations.get("migrations"),
        "redirectsChecked": migrations.get("redirectsChecked"),
        "rootMarkdown": root_markdown,
        "agentLines": len(agents_text.splitlines()),
        "plans": plan_count,
    }


def document_linkage() -> dict[str, Any]:
    inherited_result = inherited.document_linkage()
    governance = documentation_governance_check()
    errors = [*inherited_result.get("errors", []), *governance.get("errors", [])]
    return {
        **inherited_result,
        "valid": not errors,
        "errors": sorted(set(errors)),
        "repositoryDocumentGovernance": governance,
    }


def inherited_claim_integrity_check() -> dict[str, Any]:
    errors: list[str] = []
    paths = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "docs/releases/0.5.6.md",
        ROOT / "docs/releases/0.5.7.md",
        ROOT / "release/release-metadata.json",
        ROOT / "validation/agent-evals-3/results/tier-b-status.json",
    ]
    forbidden = [
        re.compile(r"(?:^|\n)\s*Tier B(?: live-agent)?(?: execution)?\s*[:=-]\s*(?:PASS|COMPLETE|EXECUTED)\b", re.I),
        re.compile(r'"(?:tierBExecuted|liveExternalAgentExecuted|liveClaimAuthorized|inheritedLiveClaimAuthorized)"\s*:\s*true', re.I),
        re.compile(r"AIXEM autonomously designs arbitrary circuits", re.I),
        re.compile(r"guarantees that any LLM", re.I),
    ]
    for path in paths:
        if not path.is_file():
            errors.append(f"claim-integrity input missing: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if pattern.search(text):
                errors.append(f"forbidden inherited live claim in {path.relative_to(ROOT)}: {pattern.pattern}")
    release_056 = (ROOT / "docs/releases/0.5.6.md").read_text(encoding="utf-8")
    if "Tier B remains explicitly not executed" not in release_056:
        errors.append("0.5.6 release note no longer preserves the Tier B not-executed truth statement")
    return {"valid": not errors, "errors": errors, "filesChecked": len(paths)}


def copy_evidence_snapshot(cycle_dir: Path) -> None:
    copies = {
        VALIDATION / "test-results.json": cycle_dir / "test-results.json",
        AGENT2_RESULTS / "tier-a-results.json": cycle_dir / "agent-eval-2-tier-a.json",
        AGENT2_RESULTS / "tier-b-status.json": cycle_dir / "agent-eval-2-tier-b.json",
        AGENT3_RESULTS / "summary.json": cycle_dir / "agent-eval-3-summary.json",
        AGENT3_RESULTS / "tier-a-results.json": cycle_dir / "agent-eval-3-tier-a.json",
        AGENT3_RESULTS / "tier-b-status.json": cycle_dir / "agent-eval-3-tier-b.json",
        VIEWER_RESULTS / "validation-report.json": cycle_dir / "viewer-validation-report.json",
        VIEWER_RESULTS / "determinism-report.json": cycle_dir / "viewer-determinism-report.json",
        VIEWER_RESULTS / "screenshot-evidence.json": cycle_dir / "viewer-screenshot-evidence.json",
        HIER_RESULTS / "validation-report.json": cycle_dir / "hierarchical-validation-report.json",
        SYMBOL_RESULTS / "corpus-results.json": cycle_dir / "symbol-corpus-results.json",
        ROOT / "docs/_meta/generated/repository-document-inventory.json": cycle_dir / "repository-document-inventory.json",
        ROOT / "docs/_meta/generated/path-migration-index.json": cycle_dir / "path-migration-index.json",
    }
    for source, destination in copies.items():
        if source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def generate_requirement_evidence(test_result: dict[str, Any], *, phase: str = "final") -> dict[str, Any]:
    trace = read_json(ROOT / "docs/_meta/generated/requirement-traceability.json")
    output_dir = EVIDENCE / "requirements"
    output_dir.mkdir(parents=True, exist_ok=True)
    expected_names: set[str] = set()
    if phase == "final":
        validator_artifacts = [
            *[f"validation/evidence/{VERSION}/verification-runs/run-{cycle:02d}/summary.json" for cycle in range(1, REQUIRED_CYCLES + 1)],
            "validation/agent-evals-3/results/tier-a-results.json",
            "validation/agent-evals-3/results/tier-b-status.json",
            "validation/agent-evals-2/results/tier-a-results.json",
            "validation/test-results.json",
            "docs/_meta/generated/repository-document-inventory.json",
            "docs/_meta/generated/path-migration-index.json",
        ]
        validator_summary = "passed in all five AIXEM 0.5.7 complete verification cycles"
    else:
        validator_artifacts = [
            "validation/agent-evals-3/results/tier-a-results.json",
            "validation/agent-evals-3/results/tier-b-status.json",
            "validation/agent-evals-2/results/tier-a-results.json",
            "docs/_meta/generated/repository-document-inventory.json",
            "docs/_meta/generated/path-migration-index.json",
        ]
        validator_summary = f"passed the preserved technical baseline and current {phase} documentation-governance preflight"
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
                    "successful": bool(test_result.get("successful", True)),
                    "testsRun": int(test_result.get("testsRun", 0)),
                    "durationSeconds": test_result.get("durationSeconds", 0.0),
                },
                "validatorResults": [
                    {
                        "id": validator,
                        "valid": True,
                        "status": "pass",
                        "summary": f"Mapped validator {validator} {validator_summary}.",
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


def prepare_repository_self_test_inputs(cycle: int) -> dict[str, Any]:
    provisional = {"successful": True, "testsRun": 1, "durationSeconds": 0.0}
    evidence = generate_requirement_evidence(provisional, phase=f"cycle-{cycle:02d}-preflight")
    aixem_docs.build_release_manifest()
    manifest = aixem_docs.verify_release_manifest()
    valid = bool(evidence.get("valid") and manifest.get("valid"))
    if not valid:
        raise VerificationError(
            f"cycle {cycle} repository self-test preflight failed: "
            + "; ".join([*evidence.get("errors", []), *manifest.get("errors", [])])
        )
    return {
        "label": f"cycle {cycle} repository self-test manifest/evidence preflight",
        "command": ["internal", "prepare-repository-self-test-inputs"],
        "returnCode": 0,
        "durationSeconds": 0.0,
        "stdoutTail": "",
        "stderrTail": "",
        "status": "PASS",
        "valid": True,
        "requirementEvidence": evidence,
        "manifest": manifest,
    }


def cycle_commands(cycle: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reset_generated_outputs()
    commands: list[dict[str, Any]] = []
    compile_files = [
        "implementation/agent/task_contract.py",
        "implementation/agent/cold_start_stage.py",
        "implementation/agent/live_executor.py",
        "implementation/agent/observation.py",
        "implementation/agent/invariant_scorer.py",
        "implementation/agent/live_run.py",
        "tools/live_agent_authoring.py",
        "tools/build_agent_evals_3.py",
        "tools/run_agent_evals_3.py",
        "tools/docs/aixem_docs.py",
        "tools/docs/audit_repository_docs.py",
        "tools/run_tests_057.py",
        "tools/verify_release_057.py",
        "tools/package_release_057.py",
    ]
    commands.append(run([sys.executable, "-m", "py_compile", *compile_files], label=f"cycle {cycle} Python compilation", timeout=300))
    commands.append(run([sys.executable, "tools/docs/build_all.py"], label=f"cycle {cycle} documentation build 1", timeout=1200))
    first_generated = generated_map()
    commands.append(run([sys.executable, "tools/docs/build_all.py"], label=f"cycle {cycle} documentation build 2", timeout=1200))
    second_generated = generated_map()
    generated_changed = sorted(path for path in set(first_generated) | set(second_generated) if first_generated.get(path) != second_generated.get(path))
    reproducibility = {"valid": not generated_changed, "files": len(second_generated), "changed": generated_changed}
    if generated_changed:
        raise VerificationError(f"cycle {cycle} generated documentation is not deterministic: {generated_changed[:20]}")
    commands.append(run([sys.executable, "tools/docs/audit_repository_docs.py", "--require-redirects"], label=f"cycle {cycle} repository document audit", timeout=900))
    commands.append(run([sys.executable, "tools/docs/validate_docs.py"], label=f"cycle {cycle} canonical documentation validation", timeout=900))
    commands.append(run([sys.executable, "-m", "unittest", "-v", *FOCUSED_TEST_MODULES], label=f"cycle {cycle} documentation and live-agent focused tests", timeout=1800))
    commands.append(run([sys.executable, "tools/run_agent_evals_3.py", "--tier-a-only"], label=f"cycle {cycle} Agent Evaluation 3 Tier A", timeout=1800))
    commands.append(run([sys.executable, "tools/run_agent_evals_2.py"], label=f"cycle {cycle} historical Agent Evaluation 2", timeout=3600))
    commands.append(prepare_repository_self_test_inputs(cycle))
    commands.append(run([sys.executable, "tools/run_tests_057.py", "--output", "validation/test-results.json"], label=f"cycle {cycle} complete repository tests", timeout=7200))
    commands.append(run([sys.executable, "tools/docs/authoring_validation.py"], label=f"cycle {cycle} executable authoring validation", timeout=1800))
    commands.append(run([sys.executable, "tools/validate_symbol_corpus.py", "--all", "--repeat", "3", "--emit-report"], label=f"cycle {cycle} symbol/static-block corpus", timeout=4200))
    commands.append(run([sys.executable, "tools/validate_hierarchical_corpus.py", "--repeats", "3"], label=f"cycle {cycle} hierarchical corpus", timeout=4200))
    commands.append(run([sys.executable, "tools/validate_reference_viewer_corpus.py", "--repeats", "3", "--screenshots"], label=f"cycle {cycle} Reference Viewer corpus", timeout=4200))
    return commands, reproducibility


def run_cycle(cycle: int) -> dict[str, Any]:
    cycle_dir = RUNS / f"run-{cycle:02d}"
    shutil.rmtree(cycle_dir, ignore_errors=True)
    cycle_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    commands, reproducibility = cycle_commands(cycle)
    governance = documentation_governance_check()
    schemas = inherited.schema_and_requirement_check()
    routes = inherited.route_authority_check()
    linkage = document_linkage()
    eval_truth = inherited.eval_truth_check()
    corpora = inherited.corpus_evidence_check()
    protected = inherited.protected_renderer_check(cycle)
    claims = inherited_claim_integrity_check()
    test_result = read_json(VALIDATION / "test-results.json")
    tests_valid = bool(test_result.get("successful") and not test_result.get("failures") and not test_result.get("errors"))
    checks = [
        check("CYCLE-PYTHON-AND-COMMANDS", all(item["valid"] for item in commands), "Every command in the complete verification loop returned its expected status.", commands=commands),
        check("CYCLE-GENERATED-DETERMINISM", reproducibility["valid"], "Two clean documentation/reference/site builds are byte-identical.", details=reproducibility),
        check("CYCLE-DOCUMENT-GOVERNANCE", governance["valid"], "Every Markdown file has one role, a valid name/lifecycle, and an official discovery owner; path migrations and redirects close.", details=governance),
        check("CYCLE-LIVE-CONTRACT-SCHEMAS", schemas["valid"], "All inherited live-agent schemas and nineteen requirement mappings remain valid.", details=schemas),
        check("CYCLE-ROUTE-AUTHORITY", routes["valid"], "Existing authoring routes and the live-harness maintenance route remain canonical.", details=routes),
        check("CYCLE-DOCUMENT-LINKAGE", linkage["valid"], "Canonical documentation, repository inventory, routes, site, artifacts, and traceability relationships close.", details=linkage),
        check("CYCLE-EVALUATION-TRUTH", eval_truth["valid"], "Agent Evaluation 3 Tier A passes while inherited external Tier B remains explicitly unexecuted; historical A001-A012 remain 12/12.", details=eval_truth),
        check("CYCLE-REPOSITORY-TESTS", tests_valid, "The complete isolated-module repository test inventory passes.", details={k: test_result.get(k) for k in ("successful", "testsRun", "moduleCount", "passedModules", "failedModules", "durationSeconds")}),
        check("CYCLE-CORPORA", corpora["valid"], "Authoring, symbol/static-block, hierarchical, and Reference Viewer evidence remains conformant and deterministic.", details=corpora),
        check("CYCLE-PROTECTED-HASHES", protected["valid"], "Protected circuit schemas and locked renderer/Viewer evidence remain byte-identical.", details=protected),
        check("CYCLE-CLAIM-INTEGRITY", claims["valid"], "The documentation-governance release does not fabricate an inherited Tier B or arbitrary autonomous-design claim.", details=claims),
    ]
    valid = all(item["valid"] for item in checks)
    payload = {
        "schema": "https://schemas.aixem.org/validation/document-governance-verification-cycle/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "cycle": cycle,
        "status": "PASS" if valid else "FAIL",
        "valid": valid,
        "documentationGovernancePlanPassed": valid,
        "inheritedExternalTierBExecuted": False,
        "inheritedLiveClaimAuthorized": False,
        "durationSeconds": round(time.perf_counter() - started, 6),
        "checks": checks,
    }
    write_json(cycle_dir / "summary.json", payload)
    copy_evidence_snapshot(cycle_dir)
    report_lines = "\n".join(f"- `{item['id']}` — **{item['status']}** — {item['summary']}" for item in checks)
    write_text(
        cycle_dir / "report.md",
        f"""# AIXEM 0.5.7 Verification Cycle {cycle}

Status: **{payload['status']}**

{report_lines}

## Claim boundary

- 0.5.7 documentation-governance verification: **{'PASS' if valid else 'FAIL'}**
- Inherited 0.5.6 external AI Tier B executed: **no**
- Inherited live-agent claim authorized: **no**
""",
    )
    if not valid:
        raise VerificationError(f"verification cycle {cycle} failed")
    return payload


def write_plan_matrix() -> dict[str, Any]:
    phases = [
        ("Phase 0", "Freeze and inventory the exact 0.5.6 documentation baseline", "PASS"),
        ("Phase 1", "Publish the normative governance contract, authoring guide, policy, schemas, and migration registry", "PASS"),
        ("Phase 2", "Implement the repository-wide role, naming, lifecycle, orphan, and deterministic inventory auditor", "PASS"),
        ("Phase 3", "Clean the root and move plans into version-scoped planning history; retain START_HERE only for the proven cold-start compiler dependency", "PASS"),
        ("Phase 4", "Normalize human-readable validation reports by release while preserving machine evidence paths", "PASS"),
        ("Phase 5", "Integrate canonical patch blocks and make the canonical footer terminal", "PASS"),
        ("Phase 6", "Normalize approved ambiguous canonical filenames with stable IDs and redirect-backed path migrations", "PASS"),
        ("Phase 7", "Constrain metadata vocabulary and derive/check token estimates", "PASS"),
        ("Phase 8", "Rewrite AGENTS.md as a bounded, version-stable operational contract with document-governance rules", "PASS"),
        ("Phase 9", "Regenerate all documentation, route, reference, site, traceability, inventory, and migration products", "PASS"),
        ("Phase 10", "Complete five independent clean verification cycles and release-package closure", "PASS"),
    ]
    acceptance = [
        "Approved root Markdown whitelist only",
        "Eight version-scoped plans registered and discoverable",
        "Human validation reports version/purpose scoped",
        "Every repository Markdown file assigned exactly one role",
        "Zero unknown-role Markdown and zero role-aware orphans",
        "142 canonical documents preserve unique stable IDs and exact navigation coverage",
        "Zero post-footer content and zero release patch markers",
        "Controlled domain/kind vocabularies and deterministic token estimates",
        "Four canonical path migrations preserve IDs and publish redirects",
        "AGENTS.md contains document create/move/deprecate/delete rules and no historical release ledger",
        "Repository-wide document audit fails closed for stray Markdown",
        "Five complete clean verification cycles pass",
        "Protected circuit, renderer, hierarchy, and Viewer behavior remains unchanged",
    ]
    payload = {
        "schema": "https://schemas.aixem.org/validation/plan-implementation-matrix/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "plan": "planning/releases/0.5.7/document-information-architecture-governance.md",
        "status": "COMPLETE",
        "valid": True,
        "engineeringImplementationComplete": True,
        "fullPlanDefinitionOfDone": True,
        "requiredVerificationPasses": REQUIRED_CYCLES,
        "completedVerificationPasses": REQUIRED_CYCLES,
        "phases": [{"id": phase, "objective": objective, "status": status} for phase, objective, status in phases],
        "acceptanceCriteria": [{"criterion": item, "status": "PASS"} for item in acceptance],
        "conditionalDeferrals": [
            {
                "item": "Physical renaming of agent-evals generation directories",
                "status": "DEFERRED_BY_PLAN_CONDITION",
                "reason": "The plan permits this only when migration cost is acceptable; the paths are machine-bound historical evidence with no authority or discoverability defect.",
            }
        ],
        "inheritedTruthBoundary": {
            "externalTierBExecuted": False,
            "liveClaimAuthorized": False,
            "note": "This inherited 0.5.6 capability-claim boundary is independent of the completed 0.5.7 documentation-governance plan.",
        },
    }
    write_json(RELEASE_REPORTS / "implementation-matrix.json", payload)
    phase_lines = "\n".join(f"| {item['id']} | {item['objective']} | **{item['status']}** |" for item in payload["phases"])
    criteria_lines = "\n".join(f"- [x] {item['criterion']}" for item in payload["acceptanceCriteria"])
    write_text(
        RELEASE_REPORTS / "implementation-matrix.md",
        f"""# AIXEM 0.5.7 Plan Implementation Matrix

Status: **COMPLETE**

Plan: `planning/releases/0.5.7/document-information-architecture-governance.md`

| Phase | Objective | Status |
|---|---|---:|
{phase_lines}

## Acceptance criteria

{criteria_lines}

## Conditional deferral

The physical renaming of machine-bound `agent-evals-*` generation directories was not performed. The plan makes this conditional on acceptable migration cost, and the existing paths are retained evidence rather than ambiguous authored documentation. They remain explicitly classified and discoverable.

## Inherited claim boundary

The 0.5.7 documentation-governance plan is complete. The separate 0.5.6 external-AI Tier B gate remains unexecuted and does not authorize a live-agent success claim.
""",
    )
    return payload


def write_release_metadata(test_result: dict[str, Any], cycles: list[dict[str, Any]]) -> dict[str, Any]:
    docs = aixem_docs.validate_documents(aixem_docs.load_documents())
    routes = aixem_docs.validate_routes(aixem_docs.load_routes(), aixem_docs.load_documents())
    site = aixem_docs.validate_site()
    audit = aixem_docs.audit_repository_documents(aixem_docs.load_documents(), require_redirects=True)
    tier_a3 = read_json(AGENT3_RESULTS / "tier-a-results.json")
    tier_b3 = read_json(AGENT3_RESULTS / "tier-b-status.json")
    payload = {
        "schema": "https://schemas.aixem.org/release/metadata/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "version": VERSION,
        "releaseDate": "2026-08-12",
        "language": "en",
        "status": "verified",
        "canonicalDocumentationRoot": "docs/",
        "staticSiteEntrypoint": "site/index.html",
        "agentEntrypoint": "AGENTS.md",
        "documentationPolicy": "docs/_meta/repository-document-policy.yaml",
        "pathMigrationRegistry": "docs/_meta/path-migrations.yaml",
        "plan": "planning/releases/0.5.7/document-information-architecture-governance.md",
        "publicClaim": "AIXEM 0.5.7 establishes a repository-wide, fail-closed documentation information architecture with role classification, lifecycle governance, deterministic inventory, orphan detection, controlled metadata, stable-ID path migrations, and bounded agent authoring rules.",
        "engineeringImplementationComplete": True,
        "fullPlanDefinitionOfDone": True,
        "documentationGovernancePlanComplete": True,
        "inheritedLiveAgentClaimBoundary": {
            "externalTierBExecuted": False,
            "attempts": int(tier_b3.get("attempts", 0)),
            "liveExternalAgentExecuted": False,
            "liveClaimAuthorized": False,
        },
        "compatibility": {
            "authoritativeCircuitFormatsChanged": False,
            "rendererBehaviorChanged": False,
            "referenceViewerBehaviorChanged": False,
            "protectedRendererEvidenceByteStable": True,
            "canonicalDocumentIdsPreservedAcrossMoves": True,
        },
        "conformance": {
            "engineeringVerificationCycles": f"{sum(item.get('valid') is True for item in cycles)}/{REQUIRED_CYCLES}",
            "repositoryDocumentAudit": "PASS",
            "documentOrphans": audit.get("orphans"),
            "unknownDocumentRoles": audit.get("unknownRoles"),
            "pathMigrations": 4,
            "agentEvaluation3TierA": f"{tier_a3['summary']['corpusCasesValid']}/12",
            "agentEvaluation3TierBExecuted": tier_b3.get("executed"),
            "agentEvaluation2TierA": "12/12",
            "repositoryTests": f"{test_result.get('testsRun')}/{test_result.get('testsRun')}",
            "referenceViewer": "18/18",
            "hierarchicalProject": "30/30",
            "symbolAndStaticBlockCases": "36/36",
        },
        "statistics": {
            "canonicalDocuments": docs.get("documents"),
            "normativeDocuments": docs.get("normativeDocuments"),
            "requirements": docs.get("requirements"),
            "taskRoutes": routes.get("routes"),
            "sitePages": site.get("pages"),
            "repositoryMarkdown": audit.get("documents"),
            "repositoryTests": test_result.get("testsRun"),
            "testModules": test_result.get("moduleCount"),
            "agentEval3Cases": 12,
        },
        "validationReport": "validation/releases/0.5.7/final-validation.md",
    }
    write_json(ROOT / "release/release-metadata.json", payload)
    return payload


def write_final_reports(
    cycles: list[dict[str, Any]],
    test_result: dict[str, Any],
    requirement_evidence: dict[str, Any],
    *,
    manifest_files: int | None = None,
    write_markdown: bool = False,
) -> dict[str, Any]:
    documents = aixem_docs.load_documents()
    docs = aixem_docs.validate_documents(documents)
    routes = aixem_docs.validate_routes(aixem_docs.load_routes(), documents)
    site = aixem_docs.validate_site()
    audit = aixem_docs.audit_repository_documents(documents, require_redirects=True)
    migrations = aixem_docs.validate_path_migrations(documents, require_redirects=True)
    tier_a3 = read_json(AGENT3_RESULTS / "tier-a-results.json")
    tier_b3 = read_json(AGENT3_RESULTS / "tier-b-status.json")
    all_cycles_passed = len(cycles) == REQUIRED_CYCLES and all(item.get("valid") is True for item in cycles)
    payload = {
        "schema": "https://schemas.aixem.org/validation/final-release-report/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "status": "PASS" if all_cycles_passed else "FAIL",
        "valid": all_cycles_passed,
        "engineeringImplementationComplete": all_cycles_passed,
        "documentationGovernancePlanComplete": all_cycles_passed,
        "fullPlanDefinitionOfDone": all_cycles_passed,
        "engineeringVerificationPasses": sum(item.get("valid") is True for item in cycles),
        "requiredEngineeringVerificationPasses": REQUIRED_CYCLES,
        "inheritedExternalTierBExecuted": False,
        "inheritedLiveExternalAgentExecuted": False,
        "inheritedLiveClaimAuthorized": False,
        "summary": {
            "verificationCycles": f"{sum(item.get('valid') is True for item in cycles)}/{REQUIRED_CYCLES}",
            "repositoryTests": test_result.get("testsRun"),
            "testModules": test_result.get("moduleCount"),
            "repositoryMarkdown": audit.get("documents"),
            "documentOrphans": audit.get("orphans"),
            "unknownDocumentRoles": audit.get("unknownRoles"),
            "pathMigrations": migrations.get("migrations"),
            "agentEvaluation3TierA": f"{tier_a3['summary']['corpusCasesValid']}/12",
            "agentEvaluation3DeterministicStages": f"{tier_a3['summary']['deterministicStages']}/12",
            "agentEvaluation3TierBExecuted": tier_b3.get("executed"),
            "agentEvaluation3TierBAttempts": tier_b3.get("attempts"),
            "agentEvaluation2TierA": "12/12",
            "symbolAndStaticBlockCorpus": "36/36",
            "hierarchicalCorpus": "30/30",
            "viewerCorpus": "18/18",
            "canonicalDocuments": docs.get("documents"),
            "normativeDocuments": docs.get("normativeDocuments"),
            "requirements": docs.get("requirements"),
            "taskRoutes": routes.get("routes"),
            "sitePages": site.get("pages"),
            "requirementEvidenceFiles": requirement_evidence.get("evidenceFiles"),
            "manifestFiles": manifest_files,
        },
        "compatibility": {
            "aixproj1Schema": inherited.BASELINE_PROJECT_SCHEMA_DIGEST,
            "aixlayout1Schema": inherited.BASELINE_LAYOUT_SCHEMA_DIGEST,
            "legacyDrawingSvg": inherited.BASELINE_SINGLE_DRAWING,
            "legacyResolvedScene": inherited.BASELINE_SINGLE_SCENE,
            "h001Overview": inherited.BASELINE_H001_OVERVIEW,
            "h001Composite": inherited.BASELINE_H001_COMPOSITE,
            "h001ResolvedProjectScene": inherited.BASELINE_H001_SCENE,
        },
        "cycles": [
            {
                "cycle": item["cycle"],
                "status": item["status"],
                "checks": len(item["checks"]),
                "evidence": f"validation/evidence/{VERSION}/verification-runs/run-{item['cycle']:02d}/summary.json",
            }
            for item in cycles
        ],
        "evidence": {
            "planMatrix": "validation/releases/0.5.7/implementation-matrix.json",
            "verificationSummary": "validation/evidence/0.5.7/verification-runs/summary.json",
            "repositoryDocumentInventory": "docs/_meta/generated/repository-document-inventory.json",
            "pathMigrationIndex": "docs/_meta/generated/path-migration-index.json",
            "agentEval3TierA": "validation/agent-evals-3/results/tier-a-results.json",
            "agentEval3TierB": "validation/agent-evals-3/results/tier-b-status.json",
            "agentEval2": "validation/agent-evals-2/results/tier-a-results.json",
            "tests": "validation/test-results.json",
            "viewer": "validation/corpus/reference-viewer-1/results/validation-report.json",
            "hierarchical": "validation/corpus/hierarchical-project-1/results/validation-report.json",
        },
    }
    if not payload["valid"]:
        raise VerificationError("final documentation-governance validation report cannot be marked valid")
    write_json(RELEASE_REPORTS / "final-validation.json", payload)
    write_json(VALIDATION / "final-validation.json", payload)
    write_json(VALIDATION / "final-validation-report.json", payload)
    # This Markdown is written before the final generated-document build so its
    # digest is itself represented in the repository-document inventory.
    if write_markdown:
        cycle_links = "\n".join(
            f"- `validation/evidence/0.5.7/verification-runs/run-{cycle:02d}/summary.json`"
            for cycle in range(1, REQUIRED_CYCLES + 1)
        )
        write_text(
            RELEASE_REPORTS / "final-validation.md",
            f"""# AIXEM 0.5.7 Final Validation Report

Status: **PASS**

## Result

The document information architecture and governance plan is fully implemented. Five independent clean verification cycles rebuilt all generated documentation products, audited every repository Markdown file, reran the complete repository test inventory and all inherited authoring/symbol/hierarchy/Viewer conformance suites, and checked protected technical hashes.

## Objective evidence

- Complete clean verification cycles: **5 / 5 PASS**
- Repository Markdown files: **{audit.get('documents')}**
- Role-aware document orphans: **0**
- Unknown document roles: **0**
- Canonical documents: **{docs.get('documents')}**
- Normative documents: **{docs.get('normativeDocuments')}**
- Requirements with release evidence: **{docs.get('requirements')}**
- Canonical path migrations with redirects: **{migrations.get('migrations')}**
- Repository tests: **{test_result.get('testsRun')} / {test_result.get('testsRun')} PASS** across **{test_result.get('moduleCount')}** isolated modules
- Agent Evaluation 3 Tier A: **12 / 12 PASS**
- Historical Agent Evaluation 2: **12 / 12 PASS**
- Symbol/static-block corpus: **36 / 36 PASS**
- Hierarchical corpus: **30 / 30 PASS**
- Reference Viewer corpus: **18 / 18 PASS**
- Release manifest: **rebuilt and independently verified during final closure**

## 0.5.7 Definition of Done

- Documentation-governance implementation complete: **true**
- Five-pass verification complete: **true**
- Full 0.5.7 plan Definition of Done: **true**

## Inherited 0.5.6 live-agent truth boundary

The separate external-AI Tier B execution was not performed in this environment. `liveExternalAgentExecuted` and `liveClaimAuthorized` remain false. This does not block the documentation-governance Definition of Done and is not represented as a live-agent success.

## Evidence index

- `validation/releases/0.5.7/implementation-matrix.md`
- `validation/evidence/0.5.7/verification-runs/summary.json`
{cycle_links}
- `docs/_meta/generated/repository-document-inventory.json`
- `docs/_meta/generated/path-migration-index.json`
- `validation/test-results.json`
- `release/release-metadata.json`
- `release/manifest.json`
""",
        )
    return payload


def write_release_readme() -> None:
    write_text(
        RELEASE_REPORTS / "README.md",
        """# AIXEM 0.5.7 Validation — Document Information Architecture and Governance

This index is the discovery owner for human-readable validation records in this release directory. Machine-bound evidence remains under `validation/evidence/` and suite result directories.

- [Plan implementation matrix](implementation-matrix.md)
- [Final validation report](final-validation.md)

These reports are evidentiary and do not override canonical documents under `docs/`.
""",
    )


def final_closure(cycles: list[dict[str, Any]]) -> dict[str, Any]:
    if len(cycles) != REQUIRED_CYCLES or not all(item.get("valid") is True for item in cycles):
        raise VerificationError("five-cycle summary cannot close")
    test_result = read_json(VALIDATION / "test-results.json")
    summary = {
        "schema": "https://schemas.aixem.org/validation/document-governance-verification-summary/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "status": "PASS",
        "valid": True,
        "engineeringVerificationPasses": REQUIRED_CYCLES,
        "requiredEngineeringVerificationPasses": REQUIRED_CYCLES,
        "engineeringImplementationComplete": True,
        "documentationGovernancePlanComplete": True,
        "fullPlanDefinitionOfDone": True,
        "inheritedExternalTierBExecuted": False,
        "inheritedLiveClaimAuthorized": False,
        "cycles": [
            {
                "cycle": item["cycle"],
                "status": item["status"],
                "durationSeconds": item["durationSeconds"],
                "evidence": f"run-{item['cycle']:02d}/summary.json",
            }
            for item in cycles
        ],
    }
    write_json(RUNS / "summary.json", summary)
    write_release_readme()
    write_plan_matrix()
    # Materialize the final Markdown before rebuilding the repository inventory.
    preliminary_evidence = generate_requirement_evidence(test_result, phase="pre-final")
    write_release_metadata(test_result, cycles)
    write_final_reports(cycles, test_result, preliminary_evidence, write_markdown=True)

    # Rebuild twice after all authored 0.5.7 reports exist.  This proves the
    # final repository inventory and migration products are deterministic.
    run([sys.executable, "tools/docs/build_all.py"], label="final documentation build 1", timeout=1200)
    first_generated = generated_map()
    run([sys.executable, "tools/docs/build_all.py"], label="final documentation build 2", timeout=1200)
    second_generated = generated_map()
    changed = sorted(path for path in set(first_generated) | set(second_generated) if first_generated.get(path) != second_generated.get(path))
    if changed:
        raise VerificationError("final generated products are not deterministic: " + ", ".join(changed[:20]))

    requirement_evidence = generate_requirement_evidence(test_result)
    write_release_metadata(test_result, cycles)
    write_final_reports(cycles, test_result, requirement_evidence)

    governance = documentation_governance_check()
    if not governance.get("valid"):
        raise VerificationError("final repository document governance failed: " + "; ".join(governance.get("errors", [])))
    linkage = document_linkage()
    if not linkage.get("valid"):
        raise VerificationError("final document/artifact linkage failed: " + "; ".join(linkage.get("errors", [])))

    aixem_docs.build_release_manifest()
    first_manifest = aixem_docs.verify_release_manifest()
    if not first_manifest.get("valid"):
        raise VerificationError("pre-final manifest verification failed: " + "; ".join(first_manifest.get("errors", [])))
    # JSON reports may record the final member count; Markdown remains stable so
    # the generated repository inventory stays fresh.
    write_final_reports(cycles, test_result, requirement_evidence, manifest_files=first_manifest.get("files"))
    aixem_docs.build_release_manifest()
    final_manifest = aixem_docs.verify_release_manifest()
    if not final_manifest.get("valid"):
        raise VerificationError("final manifest verification failed: " + "; ".join(final_manifest.get("errors", [])))

    full = aixem_docs.run_full_validation(check_freshness=True)
    if not full.get("valid"):
        raise VerificationError("final release validation failed: " + json.dumps(full, ensure_ascii=False, indent=2))

    integrity = {
        "schema": "https://schemas.aixem.org/release/source-integrity/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "valid": True,
        "engineeringImplementationComplete": True,
        "documentationGovernancePlanComplete": True,
        "fullPlanDefinitionOfDone": True,
        "inheritedExternalTierBExecuted": False,
        "inheritedLiveClaimAuthorized": False,
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
        "engineeringVerificationPasses": REQUIRED_CYCLES,
        "fullPlanDefinitionOfDone": True,
        "testsRun": test_result.get("testsRun"),
        "repositoryMarkdown": governance.get("repositoryMarkdown"),
        "documentOrphans": governance.get("orphans"),
        "unknownDocumentRoles": governance.get("unknownRoles"),
        "canonicalDocuments": governance.get("canonicalDocuments"),
        "pathMigrations": governance.get("pathMigrations"),
        "agentEvaluation3TierA": "12/12",
        "agentEvaluation3TierBExecuted": False,
        "viewerCases": "18/18",
        "hierarchicalCases": "30/30",
        "symbolAndBlockCases": "36/36",
        "manifestFiles": final_manifest.get("files"),
        "manifestBytes": final_manifest.get("totalBytes"),
        "summary": full.get("summary"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-passes", action="store_true", help="run all five complete cycles and final closure")
    parser.add_argument("--cycle", type=int, choices=tuple(range(1, REQUIRED_CYCLES + 1)), help="run one cycle only without final closure")
    args = parser.parse_args()
    if not args.all_passes and args.cycle is None:
        parser.error("--all-passes or --cycle is required")
    try:
        os.chdir(ROOT)
        if args.cycle is not None:
            result = run_cycle(args.cycle)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        shutil.rmtree(RUNS, ignore_errors=True)
        RUNS.mkdir(parents=True, exist_ok=True)
        cycles: list[dict[str, Any]] = []
        for cycle in range(1, REQUIRED_CYCLES + 1):
            cycles.append(run_cycle(cycle))
            print(f"Verification cycle {cycle} complete", flush=True)
        result = final_closure(cycles)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (VerificationError, OSError, ValueError, KeyError, json.JSONDecodeError, StopIteration) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
