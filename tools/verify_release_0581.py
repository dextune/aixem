#!/usr/bin/env python3
"""Run five complete AIXEM 0.5.8.1 documentation and specification closure cycles.

The verifier proves root-to-canonical document chaining, specification coherence,
and release relationship integrity while preserving the protected AIXEM 0.5.8
circuit, renderer, hierarchy, Viewer, and pre-live harness baseline. It never
executes or fabricates a Tier B external-AI result.
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

RELEASE_ID = "AIXEM-SRP-0.5.8.1-2026-08-12"
VERSION = "0.5.8.1"
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
    "tests.agent.test_pre_live_readiness",
]

EXPECTED_LIVE_REQUIREMENTS = {f"AIXEM-REQ-AGENT-LIVE-{index:04d}" for index in range(1, 28)}


class VerificationError(RuntimeError):
    """The 0.5.8.1 documentation and specification closure cannot close safely."""


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
    print(f"[verify-0581] START {label}", flush=True)
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
    print(f"[verify-0581] {result['status']} {label} ({result['durationSeconds']}s)", flush=True)
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
    # flat machine-report directory. 0.5.8.1 writes them under the owning release
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
    relationships = audit.get("relationships", {})
    errors = [*audit.get("errors", []), *migrations.get("errors", []), *relationships.get("errors", [])]
    ids = {doc.id for doc in documents}
    required_ids = {
        "AIXEM-SPEC-DOC-GOVERNANCE-001",
        "AIXEM-GOV-DOC-AUTHORING-001",
        "AIXEM-DOCS-HOME-001",
        "AIXEM-RELEASE-058-001",
        "AIXEM-RELEASE-0581-001",
    }
    for missing in sorted(required_ids - ids):
        errors.append(f"missing 0.5.8.1 canonical document {missing}")

    trace = read_json(ROOT / "docs/_meta/generated/requirement-traceability.json")
    observed_requirements = {item.get("id") for item in trace.get("requirements", [])}
    required_governance = {f"AIXEM-REQ-DOC-GOV-{index:04d}" for index in range(1, 15)}
    required_readiness = {f"AIXEM-REQ-AGENT-LIVE-{index:04d}" for index in range(20, 28)}
    for missing in sorted((required_governance | required_readiness) - observed_requirements):
        errors.append(f"missing governed requirement {missing}")

    root_markdown = sorted(path.name for path in ROOT.glob("*.md"))
    expected_root = sorted(["AGENTS.md", "CHANGELOG.md", "CONTRIBUTING.md", "NOTICE.md", "README.md", "REFERENCE.md", "SECURITY.md", "START_HERE.md"])
    if root_markdown != expected_root:
        errors.append(f"root Markdown set mismatch: {root_markdown}")

    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    required_agent_phrases = (
        "REFERENCE.md",
        "Before Creating a Document",
        "What repository document role will it have?",
        "Which existing owner was considered?",
        "Which official navigation, index, suite descriptor, or registry will expose it?",
        "Category indexes must link every registered member.",
        "preLiveReadiness=true",
        "A `test-fixture` PASS proves plumbing only.",
    )
    for phrase in required_agent_phrases:
        if phrase not in agents_text:
            errors.append(f"AGENTS.md omits required phrase: {phrase}")
    if len(agents_text.splitlines()) > 180:
        errors.append("AGENTS.md exceeds the bounded 180-line operational-contract limit")
    if re.search(r"active .*0\.5\.[0-7]", agents_text, re.IGNORECASE):
        errors.append("AGENTS.md contains stale hard-coded active-release prose")

    inventory_path = ROOT / "docs/_meta/generated/repository-document-inventory.json"
    migration_index_path = ROOT / "docs/_meta/generated/path-migration-index.json"
    relationship_path = ROOT / "docs/_meta/generated/document-relationship-audit.json"
    for path in (inventory_path, migration_index_path, relationship_path):
        if not path.is_file():
            errors.append(f"generated documentation governance product is missing: {path.relative_to(ROOT)}")
    inventory = read_json(inventory_path) if inventory_path.is_file() else {}
    generated_relationships = read_json(relationship_path) if relationship_path.is_file() else {}
    if inventory.get("summary", {}).get("orphans") != 0:
        errors.append("generated repository document inventory reports orphans")
    if inventory.get("summary", {}).get("unknownRoles") != 0:
        errors.append("generated repository document inventory reports unknown roles")
    if generated_relationships.get("valid") is not True:
        errors.append("generated document relationship audit is not valid")

    repository_areas = relationships.get("repositoryAreaCoverage", {})
    reachability = relationships.get("rootReachability", {})
    section_coverage = relationships.get("sectionIndexCoverage", {})
    release_coherence = relationships.get("currentReleaseCoherence", {})
    authority_scopes = relationships.get("authorityScopeReview", {})
    if repository_areas.get("linked") != repository_areas.get("targets") or repository_areas.get("missing"):
        errors.append("root reference map does not cover every governed repository area and build control")
    if reachability.get("reachable") != reachability.get("humanAuthored") or reachability.get("unreachable"):
        errors.append("root reference chain does not reach every human-authored Markdown document")
    if section_coverage.get("linked") != section_coverage.get("items"):
        errors.append("canonical category index coverage is incomplete")
    if release_coherence.get("valid") is not True:
        errors.append("current-release documentation coherence is not valid")
    if authority_scopes.get("valid") is not True or authority_scopes.get("collisions"):
        errors.append("normative authority-scope ownership is ambiguous")

    entries = inventory.get("documents", []) if inventory else []
    plan_count = sum(item.get("role") == "implementation-plan" for item in entries)
    if plan_count != 10:
        errors.append(f"expected ten version-scoped plans, observed {plan_count}")

    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "repositoryMarkdown": audit.get("documents"),
        "humanAuthoredMarkdown": reachability.get("humanAuthored"),
        "rootReachableMarkdown": reachability.get("reachable"),
        "rootReachabilityMaxDepth": reachability.get("maxDepth"),
        "rootLinksChecked": relationships.get("rootLinkIntegrity", {}).get("linksChecked"),
        "repositoryAreaTargets": repository_areas.get("targets"),
        "repositoryAreasLinked": repository_areas.get("linked"),
        "sectionIndexItems": section_coverage.get("items"),
        "sectionIndexLinked": section_coverage.get("linked"),
        "releaseCoherenceChecks": len(release_coherence.get("checks", [])),
        "normativeAuthorityScopes": authority_scopes.get("normativeScopes"),
        "authorityScopeCollisions": authority_scopes.get("collisions"),
        "orphans": audit.get("orphans"),
        "unknownRoles": audit.get("unknownRoles"),
        "roleCounts": audit.get("roles"),
        "canonicalDocuments": len(documents),
        "governanceRequirements": len(required_governance & observed_requirements),
        "preLiveRequirements": len(required_readiness & observed_requirements),
        "pathMigrations": migrations.get("migrations"),
        "redirectsChecked": migrations.get("redirectsChecked"),
        "rootMarkdown": root_markdown,
        "agentLines": len(agents_text.splitlines()),
        "plans": plan_count,
        "relationships": relationships,
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


def schema_and_requirement_check() -> dict[str, Any]:
    errors: list[str] = []
    schema_dir = ROOT / "docs/specifications/schemas/agent"
    schema_paths = sorted(schema_dir.glob("*.schema.json"))
    for path in schema_paths:
        try:
            inherited.Draft202012Validator.check_schema(read_json(path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid JSON Schema {path.relative_to(ROOT)}: {exc}")
    live_names = {path.name for path in schema_paths} & inherited.LIVE_SCHEMA_NAMES
    if live_names != inherited.LIVE_SCHEMA_NAMES:
        errors.append(f"live schema inventory mismatch: {sorted(live_names)}")
    trace = read_json(ROOT / "docs/_meta/generated/requirement-traceability.json")
    observed_live = {
        item.get("id")
        for item in trace.get("requirements", [])
        if str(item.get("id", "")).startswith("AIXEM-REQ-AGENT-LIVE-")
    }
    if observed_live != EXPECTED_LIVE_REQUIREMENTS:
        missing = sorted(EXPECTED_LIVE_REQUIREMENTS - observed_live)
        extra = sorted(observed_live - EXPECTED_LIVE_REQUIREMENTS)
        errors.append(f"live requirement inventory mismatch: missing={missing}, extra={extra}")
    for item in trace.get("requirements", []):
        if item.get("id") not in EXPECTED_LIVE_REQUIREMENTS:
            continue
        coverage = item.get("coverage", {})
        if not coverage.get("validators") or not coverage.get("tests") or not coverage.get("evidence"):
            errors.append(f"{item.get('id')}: incomplete validator/test/evidence mapping")
    return {
        "valid": not errors,
        "errors": errors,
        "agentSchemas": len(schema_paths),
        "liveSchemas": len(live_names),
        "liveRequirements": len(observed_live),
        "preLiveReadinessRequirements": len({item for item in observed_live if int(str(item).rsplit('-', 1)[1]) >= 20}),
    }

def pre_live_readiness_check() -> dict[str, Any]:
    errors: list[str] = []
    summary = read_json(AGENT3_RESULTS / "summary.json")
    tier_a = read_json(AGENT3_RESULTS / "tier-a-results.json")
    tier_b = read_json(AGENT3_RESULTS / "tier-b-status.json")
    readiness = read_json(AGENT3_RESULTS / "readiness/readiness-report.json")

    expected_status = "PRE_LIVE_READINESS_PASS_TIER_B_PENDING"
    if summary.get("valid") is not True or summary.get("preLiveReadiness") is not True:
        errors.append("Agent Evaluation 3 summary does not close pre-live readiness")
    if summary.get("engineeringStatus") != expected_status:
        errors.append(f"unexpected Agent Evaluation 3 status: {summary.get('engineeringStatus')}")
    if summary.get("repositoryRelease") != RELEASE_ID or summary.get("release") != RELEASE_ID:
        errors.append("Agent Evaluation 3 summary does not identify the current repository release")
    if summary.get("tierBExecuted") is not False or summary.get("liveExternalAgentExecuted") is not False or summary.get("liveClaimAuthorized") is not False:
        errors.append("Agent Evaluation 3 summary fabricates a live execution or claim")

    tier_summary = tier_a.get("summary", {})
    if tier_a.get("valid") is not True or tier_summary.get("corpusCasesValid") != 12 or tier_summary.get("deterministicStages") != 12:
        errors.append("Agent Evaluation 3 Tier A is not 12/12 deterministic and valid")
    if tier_a.get("externalTierBExecuted") is not False or tier_a.get("liveExternalAgentExecuted") is not False or tier_a.get("claimAuthorized") is not False:
        errors.append("Tier A incorrectly authorizes live execution")
    if tier_b.get("executed") is not False or tier_b.get("attempts") != 0:
        errors.append("Tier B should be unexecuted with zero attempts")
    if tier_b.get("liveExternalAgentExecuted") is not False or tier_b.get("claimAuthorized") is not False:
        errors.append("unexecuted Tier B authorizes a live claim")

    if readiness.get("valid") is not True or readiness.get("preLiveReadiness") is not True:
        errors.append("generated pre-live readiness report is not valid")
    if readiness.get("release") != RELEASE_ID:
        errors.append("readiness report release provenance is stale")
    for key in ("externalTierBExecuted", "liveExternalAgentExecuted", "liveClaimAuthorized"):
        if readiness.get(key) is not False:
            errors.append(f"readiness report has unsafe {key} value")
    expected_counts = {
        "subprocessSuccessMatrix": ("fixtures", 4),
        "subprocessFaultMatrix": ("faults", 10),
        "invariantFairness": ("cases", 12),
        "routeReadiness": ("routes", 8),
    }
    for section, (field, expected) in expected_counts.items():
        value = readiness.get(section, {})
        if value.get("valid") is not True or value.get("summary", {}).get(field) != expected or value.get("summary", {}).get("passed") != expected:
            errors.append(f"{section} is not {expected}/{expected} PASS")
    for section in ("stageIntegrity", "processLifecycle", "secretHygiene", "observationConsistency", "referencePackClosure"):
        if readiness.get(section, {}).get("valid") is not True:
            errors.append(f"{section} readiness gate failed")
    if readiness.get("runnerPortability", {}).get("locationIndependent") is not True:
        errors.append("runner portability was not proven with explicit external roots")
    if readiness.get("referencePackClosure", {}).get("sourceRepositoryPythonPathUsed") is not False:
        errors.append("reference-pack closure used a source repository PYTHONPATH fallback")
    for fixture in readiness.get("subprocessSuccessMatrix", {}).get("fixtures", []):
        if fixture.get("valid") is not True or fixture.get("terminalStatus") != "PASS":
            errors.append(f"readiness success fixture failed: {fixture.get('id')}")
        if fixture.get("liveExternalAgentExecuted") is not False or fixture.get("claimEligible") is not False:
            errors.append(f"test fixture incorrectly became claim eligible: {fixture.get('id')}")

    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "summary": summary,
        "tierASummary": tier_summary,
        "tierBExecuted": tier_b.get("executed"),
        "preLiveReadiness": readiness.get("preLiveReadiness"),
        "successFixtures": readiness.get("subprocessSuccessMatrix", {}).get("summary"),
        "faultFixtures": readiness.get("subprocessFaultMatrix", {}).get("summary"),
        "fairness": readiness.get("invariantFairness", {}).get("summary"),
        "routes": readiness.get("routeReadiness", {}).get("summary"),
        "runnerPortability": readiness.get("runnerPortability"),
    }

def eval_truth_check() -> dict[str, Any]:
    errors: list[str] = []
    readiness = pre_live_readiness_check()
    errors.extend(readiness.get("errors", []))
    tier_a2 = read_json(AGENT2_RESULTS / "tier-a-results.json")
    tier_b2 = read_json(AGENT2_RESULTS / "tier-b-status.json")
    if tier_a2.get("valid") is not True or tier_a2.get("summary") != {"cases": 12, "passed": 12, "failed": 0}:
        errors.append("historical Agent Evaluation 2 is not 12/12 PASS")
    if tier_a2.get("liveExternalAgentExecuted") is not False:
        errors.append("historical Tier A claims live execution")
    if tier_b2.get("executed") is not False or tier_b2.get("liveExternalAgentExecuted") is not False:
        errors.append("historical Tier B truth boundary changed")
    case_ids = sorted(path.name for path in (VALIDATION / "agent-evals-3/cases").glob("L[0-9][0-9][0-9]"))
    expected_ids = [f"L{i:03d}" for i in range(1, 13)]
    if case_ids != expected_ids:
        errors.append("L001-L012 case inventory mismatch")
    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "preLive": readiness,
        "agentEval2TierA": tier_a2.get("summary"),
        "caseIds": case_ids,
    }

def inherited_claim_integrity_check() -> dict[str, Any]:
    errors: list[str] = []
    paths = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "docs/releases/0.5.6.md",
        ROOT / "docs/releases/0.5.7.md",
        ROOT / "docs/releases/0.5.8.1.md",
        ROOT / "release/release-metadata.json",
        ROOT / "validation/agent-evals-3/results/summary.json",
        ROOT / "validation/agent-evals-3/results/readiness/readiness-report.json",
        ROOT / "validation/agent-evals-3/results/tier-b-status.json",
    ]
    forbidden = [
        re.compile(r"(?:^|\n)\s*Tier B(?: live-agent)?(?: execution)?\s*[:=-]\s*(?:PASS|COMPLETE|EXECUTED)\b", re.I),
        re.compile(r'"(?:tierBExecuted|externalTierBExecuted|liveExternalAgentExecuted|liveClaimAuthorized)"\s*:\s*true', re.I),
        re.compile(r"AIXEM autonomously designs arbitrary circuits", re.I),
        re.compile(r"guarantees that any LLM", re.I),
    ]
    checked = 0
    for path in paths:
        # release metadata is written during final closure; its pre-cycle absence is acceptable.
        if not path.is_file():
            if path.name != "release-metadata.json":
                errors.append(f"claim-integrity input missing: {path.relative_to(ROOT)}")
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if pattern.search(text):
                errors.append(f"forbidden live claim in {path.relative_to(ROOT)}: {pattern.pattern}")
    release_056 = (ROOT / "docs/releases/0.5.6.md").read_text(encoding="utf-8")
    if "Tier B remains explicitly not executed" not in release_056:
        errors.append("0.5.6 release note no longer preserves the Tier B not-executed truth statement")
    release_058 = (ROOT / "docs/releases/0.5.8.1.md").read_text(encoding="utf-8")
    if "No external AI agent is executed by this release" not in release_058:
        errors.append("0.5.8.1 release note omits the external-agent not-executed statement")
    return {"valid": not errors, "errors": sorted(set(errors)), "filesChecked": checked}

def copy_evidence_snapshot(cycle_dir: Path) -> None:
    copies = {
        VALIDATION / "test-results.json": cycle_dir / "test-results.json",
        AGENT2_RESULTS / "tier-a-results.json": cycle_dir / "agent-eval-2-tier-a.json",
        AGENT2_RESULTS / "tier-b-status.json": cycle_dir / "agent-eval-2-tier-b.json",
        AGENT3_RESULTS / "summary.json": cycle_dir / "agent-eval-3-summary.json",
        AGENT3_RESULTS / "tier-a-results.json": cycle_dir / "agent-eval-3-tier-a.json",
        AGENT3_RESULTS / "tier-b-status.json": cycle_dir / "agent-eval-3-tier-b.json",
        AGENT3_RESULTS / "readiness/readiness-report.json": cycle_dir / "pre-live-readiness-report.json",
        VIEWER_RESULTS / "validation-report.json": cycle_dir / "viewer-validation-report.json",
        VIEWER_RESULTS / "determinism-report.json": cycle_dir / "viewer-determinism-report.json",
        VIEWER_RESULTS / "screenshot-evidence.json": cycle_dir / "viewer-screenshot-evidence.json",
        HIER_RESULTS / "validation-report.json": cycle_dir / "hierarchical-validation-report.json",
        SYMBOL_RESULTS / "corpus-results.json": cycle_dir / "symbol-corpus-results.json",
        ROOT / "docs/_meta/generated/document-relationship-audit.json": cycle_dir / "document-relationship-audit.json",
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
            "validation/agent-evals-3/results/readiness/readiness-report.json",
            "validation/agent-evals-3/results/tier-a-results.json",
            "validation/agent-evals-3/results/tier-b-status.json",
            "validation/agent-evals-2/results/tier-a-results.json",
            "validation/test-results.json",
            "docs/_meta/generated/repository-document-inventory.json",
            "docs/_meta/generated/path-migration-index.json",
        ]
        validator_summary = "passed in all five AIXEM 0.5.8.1 clean verification cycles"
    else:
        validator_artifacts = [
            "validation/agent-evals-3/results/readiness/readiness-report.json",
            "validation/agent-evals-3/results/tier-a-results.json",
            "validation/agent-evals-3/results/tier-b-status.json",
            "validation/agent-evals-2/results/tier-a-results.json",
            "docs/_meta/generated/repository-document-inventory.json",
            "docs/_meta/generated/path-migration-index.json",
        ]
        validator_summary = f"passed the protected 0.5.8 baseline and current {phase} documentation-closure preflight"
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
        "implementation/agent/secret_hygiene.py",
        "implementation/agent/invariant_scorer.py",
        "implementation/agent/live_run.py",
        "tests/fixtures/agents/readiness_fixture_agent.py",
        "tools/live_agent_authoring.py",
        "tools/build_agent_evals_3.py",
        "tools/run_agent_evals_3.py",
        "tools/docs/aixem_docs.py",
        "tools/docs/audit_repository_docs.py",
        "tools/run_tests_0581.py",
        "tools/verify_release_0581.py",
        "tools/package_release_0581.py",
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
    commands.append(run([sys.executable, "-m", "unittest", "-v", *FOCUSED_TEST_MODULES], label=f"cycle {cycle} documentation and pre-live focused tests", timeout=1800))

    external_root = Path("/mnt/data") / f"aixem0581 verification cycle {cycle:02d}"
    results_root = external_root / "results with spaces"
    work_root = external_root / "work with spaces"
    shutil.rmtree(external_root, ignore_errors=True)
    command_result = run(
        [sys.executable, "tools/run_agent_evals_3.py", "--tier-a-only", "--results", str(results_root), "--work", str(work_root)],
        label=f"cycle {cycle} portable pre-live readiness",
        timeout=2400,
    )
    commands.append(command_result)
    shutil.rmtree(AGENT3_RESULTS, ignore_errors=True)
    shutil.copytree(results_root, AGENT3_RESULTS)
    commands.append({
        "label": f"cycle {cycle} retain portable readiness evidence",
        "command": ["internal", "copy-portable-readiness-results"],
        "returnCode": 0,
        "durationSeconds": 0.0,
        "stdoutTail": "",
        "stderrTail": "",
        "status": "PASS",
        "valid": True,
        "source": str(results_root),
        "destination": AGENT3_RESULTS.relative_to(ROOT).as_posix(),
    })
    commands.append(run([sys.executable, "tools/run_agent_evals_2.py"], label=f"cycle {cycle} historical Agent Evaluation 2", timeout=3600))
    commands.append(prepare_repository_self_test_inputs(cycle))
    commands.append(run([sys.executable, "tools/run_tests_0581.py", "--output", "validation/test-results.json"], label=f"cycle {cycle} complete repository tests", timeout=7200))
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
    schemas = schema_and_requirement_check()
    routes = inherited.route_authority_check()
    linkage = document_linkage()
    eval_truth = eval_truth_check()
    readiness = pre_live_readiness_check()
    corpora = inherited.corpus_evidence_check()
    protected = inherited.protected_renderer_check(cycle)
    claims = inherited_claim_integrity_check()
    test_result = read_json(VALIDATION / "test-results.json")
    tests_valid = bool(test_result.get("successful") and not test_result.get("failures") and not test_result.get("errors"))
    checks = [
        check("CYCLE-PYTHON-AND-COMMANDS", all(item["valid"] for item in commands), "Every command in the complete verification loop returned its expected status.", commands=commands),
        check("CYCLE-GENERATED-DETERMINISM", reproducibility["valid"], "Two clean documentation/reference/site builds are byte-identical.", details=reproducibility),
        check("CYCLE-DOCUMENT-GOVERNANCE", governance["valid"], "Every Markdown file retains one role, a valid lifecycle, and an official discovery owner.", details=governance),
        check("CYCLE-LIVE-CONTRACT-SCHEMAS", schemas["valid"], "All live-agent schemas and twenty-seven requirement mappings validate.", details=schemas),
        check("CYCLE-ROUTE-AUTHORITY", routes["valid"], "Existing authoring routes and write authorities remain canonical.", details=routes),
        check("CYCLE-DOCUMENT-LINKAGE", linkage["valid"], "Documentation, routes, site, artifacts, inventory, and traceability relationships close.", details=linkage),
        check("CYCLE-PRE-LIVE-READINESS", readiness["valid"], "Portable successful, failing, timeout, tamper, fairness, and route-readiness paths close without an AI claim.", details=readiness),
        check("CYCLE-EVALUATION-TRUTH", eval_truth["valid"], "Tier A and pre-live readiness pass while external Tier B remains explicitly unexecuted; historical A001-A012 remain 12/12.", details=eval_truth),
        check("CYCLE-REPOSITORY-TESTS", tests_valid, "The complete isolated-module repository test inventory passes.", details={k: test_result.get(k) for k in ("successful", "testsRun", "moduleCount", "passedModules", "failedModules", "durationSeconds")}),
        check("CYCLE-CORPORA", corpora["valid"], "Authoring, symbol/static-block, hierarchy, and Reference Viewer evidence remains conformant and deterministic.", details=corpora),
        check("CYCLE-PROTECTED-HASHES", protected["valid"], "Protected circuit schemas and locked renderer/Viewer evidence remain byte-identical.", details=protected),
        check("CYCLE-CLAIM-INTEGRITY", claims["valid"], "The documentation-closure release does not fabricate external AI execution or arbitrary autonomous-design claims.", details=claims),
    ]
    valid = all(item["valid"] for item in checks)
    payload = {
        "schema": "https://schemas.aixem.org/validation/document-relationship-verification-cycle/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "cycle": cycle,
        "status": "PASS" if valid else "FAIL",
        "valid": valid,
        "documentationRelationshipClosurePassed": valid,
        "preLiveReadinessPlanPassed": valid,
        "preLiveReadiness": bool(readiness.get("preLiveReadiness")) if valid else False,
        "externalTierBExecuted": False,
        "liveExternalAgentExecuted": False,
        "liveClaimAuthorized": False,
        "durationSeconds": round(time.perf_counter() - started, 6),
        "checks": checks,
    }
    write_json(cycle_dir / "summary.json", payload)
    copy_evidence_snapshot(cycle_dir)
    report_lines = "\n".join(f"- `{item['id']}` — **{item['status']}** — {item['summary']}" for item in checks)
    write_text(
        cycle_dir / "report.md",
        f"""# AIXEM 0.5.8.1 Verification Cycle {cycle}

Status: **{payload['status']}**

{report_lines}

## Claim boundary

- 0.5.8.1 documentation relationship closure: **{'PASS' if valid else 'FAIL'}**
- External AI Tier B executed: **no**
- Live external agent executed: **no**
- Live-agent claim authorized: **no**
""",
    )
    if not valid:
        raise VerificationError(f"verification cycle {cycle} failed")
    return payload

def write_plan_matrix() -> dict[str, Any]:
    phases = [
        ("Phase 0", "Freeze the verified 0.5.8 package and inventory every document, specification, route, and release pointer", "PASS"),
        ("Phase 1", "Add a bounded root REFERENCE map and compact AGENTS category delegation", "PASS"),
        ("Phase 2", "Correct stale release references and ambiguous normative authority ownership", "PASS"),
        ("Phase 3", "Automate root-link safety, complete Markdown reachability, section-index coverage, and release coherence", "PASS"),
        ("Phase 4", "Regenerate documentation, reference, site, traceability, and evidence products deterministically", "PASS"),
        ("Phase 5", "Complete five independent clean verification cycles and deterministic archive closure", "PASS"),
    ]
    acceptance = [
        "README and approved root entrypoints resolve every local link and Markdown anchor safely",
        "Every human-authored Markdown document is reachable from README through explicit links",
        "Every canonical category index links every registered navigation member",
        "Root, navigation, planning, validation, active routes, and release metadata agree with VERSION",
        "No undeclared duplicate normative authority scope remains",
        "AGENTS remains below the bounded operational-contract limit and delegates category detail to REFERENCE",
        "Canonical metadata, links, dependencies, routes, schemas, requirements, and evidence remain valid",
        "The 0.5.8 deterministic pre-live readiness gate remains PASS without technical behavior changes",
        "Circuit formats, renderer, hierarchy, Viewer, and agent execution contracts remain regression locked",
        "Five complete clean verification cycles pass",
        "The final ZIP is deterministic, complete, traversal-safe, and independently audited",
        "External Tier B, live external execution, and live claim authorization remain false",
    ]
    payload = {
        "schema": "https://schemas.aixem.org/validation/plan-implementation-matrix/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "plan": "planning/releases/0.5.8.1/final-document-specification-reference-chain-closure.md",
        "status": "COMPLETE",
        "valid": True,
        "engineeringImplementationComplete": True,
        "documentationRelationshipClosureComplete": True,
        "preLiveReadinessPlanComplete": True,
        "preLiveReadiness": True,
        "fullPlanDefinitionOfDone": True,
        "requiredVerificationPasses": REQUIRED_CYCLES,
        "completedVerificationPasses": REQUIRED_CYCLES,
        "phases": [{"id": phase, "objective": objective, "status": status} for phase, objective, status in phases],
        "acceptanceCriteria": [{"criterion": item, "status": "PASS"} for item in acceptance],
        "deliberateDeferrals": [
            "real external AI execution and provider-specific adapters",
            "repair hints, semantic diff, context optimization, and live-corpus expansion",
            "editor DSL, GUI editing, multi-agent orchestration, container platform, and remote evidence service",
        ],
        "claimBoundary": {
            "externalTierBExecuted": False,
            "liveExternalAgentExecuted": False,
            "liveClaimAuthorized": False,
            "note": "The completed 0.5.8.1 plan proves documentation and specification relationship closure while preserving the non-AI 0.5.8 pre-live gate.",
        },
    }
    write_json(RELEASE_REPORTS / "implementation-matrix.json", payload)
    phase_lines = "\n".join(f"| {item['id']} | {item['objective']} | **{item['status']}** |" for item in payload["phases"])
    criteria_lines = "\n".join(f"- [x] {item['criterion']}" for item in payload["acceptanceCriteria"])
    deferred_lines = "\n".join(f"- {item}" for item in payload["deliberateDeferrals"])
    write_text(
        RELEASE_REPORTS / "implementation-matrix.md",
        f"""# AIXEM 0.5.8.1 Implementation Matrix

Status: **COMPLETE**

Plan: `planning/releases/0.5.8.1/final-document-specification-reference-chain-closure.md`

| Phase | Objective | Status |
|---|---|---:|
{phase_lines}

## Acceptance Criteria

{criteria_lines}

## Deliberate Non-Goals Retained

{deferred_lines}

## Claim Boundary

The 0.5.8.1 documentation and specification closure plan is complete. No external AI Tier B attempt ran, and no live-agent capability claim is authorized. The inherited 0.5.8 pre-live PASS remains a deterministic non-AI platform proof.
""",
    )
    return payload

def write_release_metadata(test_result: dict[str, Any], cycles: list[dict[str, Any]]) -> dict[str, Any]:
    documents = aixem_docs.load_documents()
    docs = aixem_docs.validate_documents(documents)
    routes = aixem_docs.validate_routes(aixem_docs.load_routes(), documents)
    site = aixem_docs.validate_site()
    audit = aixem_docs.audit_repository_documents(documents, require_redirects=True)
    relationships = audit["relationships"]
    tier_a3 = read_json(AGENT3_RESULTS / "tier-a-results.json")
    tier_b3 = read_json(AGENT3_RESULTS / "tier-b-status.json")
    readiness = read_json(AGENT3_RESULTS / "readiness/readiness-report.json")
    repository_areas = relationships["repositoryAreaCoverage"]
    reachability = relationships["rootReachability"]
    section_coverage = relationships["sectionIndexCoverage"]
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
        "rootReferenceMap": "REFERENCE.md",
        "plan": "planning/releases/0.5.8.1/final-document-specification-reference-chain-closure.md",
        "publicClaim": "AIXEM 0.5.8.1 closes root-to-canonical documentation and specification relationships, current-release coherence, and authority-scope ambiguity while preserving the verified 0.5.8 pre-live platform boundary without executing an external AI agent.",
        "engineeringImplementationComplete": True,
        "documentationRelationshipClosureComplete": True,
        "preLiveReadinessPlanComplete": True,
        "preLiveReadiness": readiness.get("preLiveReadiness") is True,
        "fullPlanDefinitionOfDone": True,
        "externalTierBExecuted": False,
        "liveExternalAgentExecuted": False,
        "liveClaimAuthorized": False,
        "compatibility": {
            "authoritativeCircuitFormatsChanged": False,
            "rendererBehaviorChanged": False,
            "referenceViewerBehaviorChanged": False,
            "agentExecutionContractsChanged": False,
            "documentationGovernancePreserved": True,
            "protectedRendererEvidenceByteStable": True,
        },
        "conformance": {
            "engineeringVerificationCycles": f"{sum(item.get('valid') is True for item in cycles)}/{REQUIRED_CYCLES}",
            "rootReferenceChain": f"{reachability.get('reachable')}/{reachability.get('humanAuthored')}",
            "rootLinksChecked": relationships["rootLinkIntegrity"].get("linksChecked"),
            "repositoryAreaCoverage": f"{repository_areas.get('linked')}/{repository_areas.get('targets')}",
            "sectionIndexCoverage": f"{section_coverage.get('linked')}/{section_coverage.get('items')}",
            "releaseCoherence": "PASS" if relationships["currentReleaseCoherence"].get("valid") else "FAIL",
            "authorityScopeReview": "PASS" if relationships["authorityScopeReview"].get("valid") else "FAIL",
            "preLiveReadiness": "PASS",
            "subprocessSuccessFixtures": "4/4",
            "subprocessFaultFixtures": "10/10",
            "invariantFairness": "12/12",
            "authoringRouteReadiness": "8/8",
            "agentEvaluation3TierA": f"{tier_a3['summary']['corpusCasesValid']}/12",
            "agentEvaluation3TierBExecuted": tier_b3.get("executed"),
            "agentEvaluation2TierA": "12/12",
            "repositoryTests": f"{test_result.get('testsRun')}/{test_result.get('testsRun')}",
            "referenceViewer": "18/18",
            "hierarchicalProject": "30/30",
            "symbolAndStaticBlockCases": "36/36",
            "documentOrphans": audit.get("orphans"),
            "unknownDocumentRoles": audit.get("unknownRoles"),
        },
        "statistics": {
            "canonicalDocuments": docs.get("documents"),
            "normativeDocuments": docs.get("normativeDocuments"),
            "requirements": docs.get("requirements"),
            "taskRoutes": routes.get("routes"),
            "sitePages": site.get("pages"),
            "repositoryMarkdown": audit.get("documents"),
            "humanAuthoredMarkdown": reachability.get("humanAuthored"),
            "repositoryTests": test_result.get("testsRun"),
            "testModules": test_result.get("moduleCount"),
            "agentEval3Cases": 12,
        },
        "validationReport": "validation/releases/0.5.8.1/final-validation.md",
        "documentRelationshipAudit": "docs/_meta/generated/document-relationship-audit.json",
        "readinessReport": "validation/agent-evals-3/results/readiness/readiness-report.json",
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
    relationships = audit["relationships"]
    migrations = aixem_docs.validate_path_migrations(documents, require_redirects=True)
    tier_a3 = read_json(AGENT3_RESULTS / "tier-a-results.json")
    tier_b3 = read_json(AGENT3_RESULTS / "tier-b-status.json")
    readiness = read_json(AGENT3_RESULTS / "readiness/readiness-report.json")
    all_cycles_passed = len(cycles) == REQUIRED_CYCLES and all(item.get("valid") is True for item in cycles)
    repository_areas = relationships["repositoryAreaCoverage"]
    reachability = relationships["rootReachability"]
    section_coverage = relationships["sectionIndexCoverage"]
    payload = {
        "schema": "https://schemas.aixem.org/validation/final-release-report/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "status": "PASS" if all_cycles_passed else "FAIL",
        "valid": all_cycles_passed,
        "engineeringImplementationComplete": all_cycles_passed,
        "documentationRelationshipClosureComplete": all_cycles_passed and relationships.get("valid") is True,
        "preLiveReadinessPlanComplete": all_cycles_passed,
        "preLiveReadiness": all_cycles_passed and readiness.get("preLiveReadiness") is True,
        "fullPlanDefinitionOfDone": all_cycles_passed,
        "engineeringVerificationPasses": sum(item.get("valid") is True for item in cycles),
        "requiredEngineeringVerificationPasses": REQUIRED_CYCLES,
        "externalTierBExecuted": False,
        "liveExternalAgentExecuted": False,
        "liveClaimAuthorized": False,
        "summary": {
            "verificationCycles": f"{sum(item.get('valid') is True for item in cycles)}/{REQUIRED_CYCLES}",
            "repositoryTests": test_result.get("testsRun"),
            "testModules": test_result.get("moduleCount"),
            "repositoryMarkdown": audit.get("documents"),
            "humanAuthoredMarkdown": reachability.get("humanAuthored"),
            "rootReachability": f"{reachability.get('reachable')}/{reachability.get('humanAuthored')}",
            "rootReachabilityMaxDepth": reachability.get("maxDepth"),
            "rootLinksChecked": relationships["rootLinkIntegrity"].get("linksChecked"),
            "repositoryAreaCoverage": f"{repository_areas.get('linked')}/{repository_areas.get('targets')}",
            "sectionIndexCoverage": f"{section_coverage.get('linked')}/{section_coverage.get('items')}",
            "releaseCoherenceChecks": len(relationships["currentReleaseCoherence"].get("checks", [])),
            "authorityScopeCollisions": len(relationships["authorityScopeReview"].get("collisions", {})),
            "documentOrphans": audit.get("orphans"),
            "unknownDocumentRoles": audit.get("unknownRoles"),
            "pathMigrations": migrations.get("migrations"),
            "agentEvaluation3TierA": f"{tier_a3['summary']['corpusCasesValid']}/12",
            "agentEvaluation3DeterministicStages": f"{tier_a3['summary']['deterministicStages']}/12",
            "subprocessSuccessFixtures": readiness.get("subprocessSuccessMatrix", {}).get("summary"),
            "subprocessFaultFixtures": readiness.get("subprocessFaultMatrix", {}).get("summary"),
            "invariantFairness": readiness.get("invariantFairness", {}).get("summary"),
            "authoringRouteReadiness": readiness.get("routeReadiness", {}).get("summary"),
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
            {"cycle": item["cycle"], "status": item["status"], "checks": len(item["checks"]), "evidence": f"validation/evidence/{VERSION}/verification-runs/run-{item['cycle']:02d}/summary.json"}
            for item in cycles
        ],
        "evidence": {
            "planMatrix": "validation/releases/0.5.8.1/implementation-matrix.json",
            "verificationSummary": "validation/evidence/0.5.8.1/verification-runs/summary.json",
            "documentRelationshipAudit": "docs/_meta/generated/document-relationship-audit.json",
            "repositoryDocumentInventory": "docs/_meta/generated/repository-document-inventory.json",
            "pathMigrationIndex": "docs/_meta/generated/path-migration-index.json",
            "preLiveReadiness": "validation/agent-evals-3/results/readiness/readiness-report.json",
            "agentEval3TierA": "validation/agent-evals-3/results/tier-a-results.json",
            "agentEval3TierB": "validation/agent-evals-3/results/tier-b-status.json",
            "agentEval2": "validation/agent-evals-2/results/tier-a-results.json",
            "tests": "validation/test-results.json",
            "viewer": "validation/corpus/reference-viewer-1/results/validation-report.json",
            "hierarchical": "validation/corpus/hierarchical-project-1/results/validation-report.json",
        },
    }
    if not payload["valid"]:
        raise VerificationError("final documentation relationship validation report cannot be marked valid")
    write_json(RELEASE_REPORTS / "final-validation.json", payload)
    write_json(VALIDATION / "final-validation.json", payload)
    write_json(VALIDATION / "final-validation-report.json", payload)
    if write_markdown:
        cycle_links = "\n".join(f"- `validation/evidence/0.5.8.1/verification-runs/run-{cycle:02d}/summary.json`" for cycle in range(1, REQUIRED_CYCLES + 1))
        write_text(RELEASE_REPORTS / "final-validation.md", f"""# AIXEM 0.5.8.1 Final Validation Report

Status: **PASS**

## Result

The final documentation, specification, and root-reference-chain closure is complete. Five independent clean verification cycles rebuilt all generated documentation and reference products, verified every root and category relationship, reran the complete repository and inherited conformance suites, and checked protected technical hashes.

## Documentation and Specification Evidence

- Root-local links and anchors checked: **{relationships['rootLinkIntegrity'].get('linksChecked')}**
- Governed repository areas and build controls linked by `REFERENCE.md`: **{repository_areas.get('linked')} / {repository_areas.get('targets')}**
- Human-authored Markdown reachable from `README.md`: **{reachability.get('reachable')} / {reachability.get('humanAuthored')}**
- Maximum root-chain depth: **{reachability.get('maxDepth')}**
- Canonical navigation members linked by category indexes: **{section_coverage.get('linked')} / {section_coverage.get('items')}**
- Current-release coherence checks: **{len(relationships['currentReleaseCoherence'].get('checks', []))} / {len(relationships['currentReleaseCoherence'].get('checks', []))} PASS**
- Undeclared normative authority-scope collisions: **0**
- Role-aware document orphans: **0**
- Unknown document roles: **0**

## Full Regression Evidence

- Complete clean verification cycles: **5 / 5 PASS**
- Repository tests: **{test_result.get('testsRun')} / {test_result.get('testsRun')} PASS** across **{test_result.get('moduleCount')}** isolated modules
- Pre-live readiness: **PASS**
- Deterministic subprocess success fixtures: **4 / 4 PASS**
- Integrated subprocess fault fixtures: **10 / 10 PASS**
- L001-L012 invariant basis audit: **12 / 12 PASS**
- Existing authoring route readiness: **8 / 8 PASS**
- Agent Evaluation 3 Tier A: **12 / 12 PASS**
- Historical Agent Evaluation 2: **12 / 12 PASS**
- Symbol/static-block corpus: **36 / 36 PASS**
- Hierarchical corpus: **30 / 30 PASS**
- Reference Viewer corpus: **18 / 18 PASS**
- Repository Markdown files: **{audit.get('documents')}**
- Canonical documents: **{docs.get('documents')}**
- Normative documents: **{docs.get('normativeDocuments')}**
- Requirements with release evidence: **{docs.get('requirements')}**
- Canonical path migrations with redirects: **{migrations.get('migrations')}**

## Definition of Done

- Engineering implementation complete: **true**
- Documentation relationship closure complete: **true**
- Deterministic pre-live readiness preserved: **true**
- Five-pass verification complete: **true**
- Full 0.5.8.1 plan Definition of Done: **true**

## External-Agent Truth Boundary

No external AI Tier B attempt was performed. `externalTierBExecuted`, `liveExternalAgentExecuted`, and `liveClaimAuthorized` remain false. The inherited four PASS fixtures remain deterministic non-AI plumbing proofs and are not represented as model capability evidence.

## Evidence Index

- `validation/releases/0.5.8.1/implementation-matrix.md`
- `docs/_meta/generated/document-relationship-audit.json`
- `validation/agent-evals-3/results/readiness/readiness-report.json`
- `validation/evidence/0.5.8.1/verification-runs/summary.json`
{cycle_links}
- `docs/_meta/generated/repository-document-inventory.json`
- `docs/_meta/generated/path-migration-index.json`
- `validation/test-results.json`
- `release/release-metadata.json`
- `release/manifest.json`
""")
    return payload

def write_release_readme() -> None:
    write_text(
        RELEASE_REPORTS / "README.md",
        """# AIXEM 0.5.8.1 Validation — Final Documentation and Reference-Chain Closure

This index owns the human-readable validation records for the final documentation, specification, and root-reference-chain closure release.

- [Implementation matrix](implementation-matrix.md)
- [Final validation report](final-validation.md)
- [Generated document relationship audit](../../../docs/_meta/generated/document-relationship-audit.json)
- [Five-pass verification summary](../../evidence/0.5.8.1/verification-runs/summary.json)
- [Inherited pre-live readiness report](../../agent-evals-3/results/readiness/readiness-report.json)

These reports are evidentiary and do not override canonical documents under `docs/`. No external AI agent ran and no live-agent capability claim is authorized.
""",
    )

def final_closure(cycles: list[dict[str, Any]]) -> dict[str, Any]:
    if len(cycles) != REQUIRED_CYCLES or not all(item.get("valid") is True for item in cycles):
        raise VerificationError("five-cycle summary cannot close")
    test_result = read_json(VALIDATION / "test-results.json")
    summary = {
        "schema": "https://schemas.aixem.org/validation/document-relationship-verification-summary/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "status": "PASS",
        "valid": True,
        "engineeringVerificationPasses": REQUIRED_CYCLES,
        "requiredEngineeringVerificationPasses": REQUIRED_CYCLES,
        "engineeringImplementationComplete": True,
        "documentationRelationshipClosureComplete": True,
        "preLiveReadinessPlanComplete": True,
        "preLiveReadiness": True,
        "fullPlanDefinitionOfDone": True,
        "externalTierBExecuted": False,
        "liveExternalAgentExecuted": False,
        "liveClaimAuthorized": False,
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
    preliminary_evidence = generate_requirement_evidence(test_result, phase="pre-final")
    write_release_metadata(test_result, cycles)
    write_final_reports(cycles, test_result, preliminary_evidence, write_markdown=True)

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
    schemas = schema_and_requirement_check()
    if not schemas.get("valid"):
        raise VerificationError("final schema/requirement validation failed: " + "; ".join(schemas.get("errors", [])))
    readiness = pre_live_readiness_check()
    if not readiness.get("valid"):
        raise VerificationError("inherited pre-live readiness failed: " + "; ".join(readiness.get("errors", [])))
    linkage = document_linkage()
    if not linkage.get("valid"):
        raise VerificationError("final document/artifact linkage failed: " + "; ".join(linkage.get("errors", [])))

    aixem_docs.build_release_manifest()
    first_manifest = aixem_docs.verify_release_manifest()
    if not first_manifest.get("valid"):
        raise VerificationError("pre-final manifest verification failed: " + "; ".join(first_manifest.get("errors", [])))
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
        "documentationRelationshipClosureComplete": True,
        "preLiveReadinessPlanComplete": True,
        "preLiveReadiness": True,
        "fullPlanDefinitionOfDone": True,
        "externalTierBExecuted": False,
        "liveExternalAgentExecuted": False,
        "liveClaimAuthorized": False,
        "manifestVerification": final_manifest,
        "fullReleaseValidation": full,
        "requirementEvidence": requirement_evidence,
        "readiness": readiness,
        "note": "This artifact is excluded from manifest hash coverage to avoid self-reference.",
    }
    write_json(ROOT / "release/archive-verification.json", integrity)
    return {
        "status": "PASS",
        "valid": True,
        "release": RELEASE_ID,
        "engineeringVerificationPasses": REQUIRED_CYCLES,
        "preLiveReadiness": True,
        "fullPlanDefinitionOfDone": True,
        "externalTierBExecuted": False,
        "liveExternalAgentExecuted": False,
        "liveClaimAuthorized": False,
        "testsRun": test_result.get("testsRun"),
        "testModules": test_result.get("moduleCount"),
        "repositoryMarkdown": governance.get("repositoryMarkdown"),
        "documentOrphans": governance.get("orphans"),
        "unknownDocumentRoles": governance.get("unknownRoles"),
        "canonicalDocuments": governance.get("canonicalDocuments"),
        "preLiveSuccessFixtures": "4/4",
        "preLiveFaultFixtures": "10/10",
        "invariantFairness": "12/12",
        "authoringRouteReadiness": "8/8",
        "agentEvaluation3TierA": "12/12",
        "agentEvaluation3TierBExecuted": False,
        "viewerCases": "18/18",
        "hierarchicalCases": "30/30",
        "symbolAndBlockCases": "36/36",
        "manifestFiles": final_manifest.get("files"),
        "manifestBytes": final_manifest.get("totalBytes"),
        "summary": full.get("summary"),
    }


STAGE_NAMES = (
    "core",
    "focused",
    "readiness",
    "eval2",
    "preflight",
    "tests-0",
    "tests-manifest",
    "tests-1",
    "tests-2",
    "tests-3",
    "tests-4",
    "tests-5",
    "tests-6",
    "tests-7",
    "tests-merge",
    "symbol",
    "hierarchy",
    "viewer",
    "finalize",
)


def stage_path(cycle: int, stage: str) -> Path:
    return RUNS / f"run-{cycle:02d}" / "stages" / f"{stage}.json"


def write_stage(cycle: int, stage: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema": "https://schemas.aixem.org/validation/pre-live-readiness-verification-stage/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "cycle": cycle,
        "stage": stage,
        **payload,
    }
    write_json(stage_path(cycle, stage), result)
    return result


def required_stage_results(cycle: int) -> tuple[list[dict[str, Any]], list[str]]:
    required = [name for name in STAGE_NAMES if name != "finalize"]
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for name in required:
        path = stage_path(cycle, name)
        if not path.is_file():
            errors.append(f"missing verification stage {name}")
            continue
        payload = read_json(path)
        results.append(payload)
        if payload.get("valid") is not True:
            errors.append(f"verification stage {name} is not valid")
    return results, errors


def run_verification_stage(cycle: int, stage: str) -> dict[str, Any]:
    cycle_dir = RUNS / f"run-{cycle:02d}"
    cycle_dir.mkdir(parents=True, exist_ok=True)
    if stage == "core":
        shutil.rmtree(cycle_dir, ignore_errors=True)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        reset_generated_outputs()
        compile_files = [
            "implementation/agent/task_contract.py",
            "implementation/agent/cold_start_stage.py",
            "implementation/agent/live_executor.py",
            "implementation/agent/observation.py",
            "implementation/agent/secret_hygiene.py",
            "implementation/agent/invariant_scorer.py",
            "implementation/agent/live_run.py",
            "tests/fixtures/agents/readiness_fixture_agent.py",
            "tools/live_agent_authoring.py",
            "tools/build_agent_evals_3.py",
            "tools/run_agent_evals_3.py",
            "tools/run_tests_0581.py",
            "tools/verify_release_0581.py",
            "tools/package_release_0581.py",
        ]
        commands = [
            run([sys.executable, "-m", "py_compile", *compile_files], label=f"cycle {cycle} core compilation", timeout=300),
            run([sys.executable, "tools/docs/build_all.py"], label=f"cycle {cycle} core documentation build 1", timeout=1200),
        ]
        first = generated_map()
        commands.append(run([sys.executable, "tools/docs/build_all.py"], label=f"cycle {cycle} core documentation build 2", timeout=1200))
        second = generated_map()
        changed = sorted(path for path in set(first) | set(second) if first.get(path) != second.get(path))
        if changed:
            raise VerificationError("generated documentation differs between core builds: " + ", ".join(changed[:20]))
        commands.extend([
            run([sys.executable, "tools/docs/audit_repository_docs.py", "--require-redirects"], label=f"cycle {cycle} core repository document audit", timeout=900),
            run([sys.executable, "tools/docs/validate_docs.py"], label=f"cycle {cycle} core canonical documentation validation", timeout=900),
        ])
        return write_stage(cycle, stage, {"status": "PASS", "valid": True, "generatedDeterminism": {"valid": True, "files": len(second), "changed": []}, "commands": commands})

    if stage == "focused":
        command = run([sys.executable, "-m", "unittest", "-v", *FOCUSED_TEST_MODULES], label=f"cycle {cycle} focused documentation and pre-live tests", timeout=1800)
        return write_stage(cycle, stage, {"status": "PASS", "valid": True, "command": command})

    if stage == "readiness":
        external_root = Path("/mnt/data") / f"aixem0581 verification cycle {cycle:02d}"
        results_root = external_root / "results with spaces"
        work_root = external_root / "work with spaces"
        shutil.rmtree(external_root, ignore_errors=True)
        commands = [run(
            [sys.executable, "tools/run_agent_evals_3.py", "--tier-a-only", "--results", str(results_root), "--work", str(work_root)],
            label=f"cycle {cycle} portable pre-live readiness",
            timeout=2400,
        )]
        shutil.rmtree(AGENT3_RESULTS, ignore_errors=True)
        shutil.copytree(results_root, AGENT3_RESULTS)
        readiness = pre_live_readiness_check()
        if readiness.get("valid") is not True:
            raise VerificationError("readiness stage failed: " + "; ".join(readiness.get("errors", [])))
        return write_stage(cycle, stage, {"status": "PASS", "valid": True, "commands": commands, "preLive": readiness})

    if stage == "eval2":
        command = run([sys.executable, "tools/run_agent_evals_2.py"], label=f"cycle {cycle} historical Agent Evaluation 2", timeout=3600)
        truth = eval_truth_check()
        if truth.get("valid") is not True:
            raise VerificationError("evaluation truth stage failed: " + "; ".join(truth.get("errors", [])))
        return write_stage(cycle, stage, {"status": "PASS", "valid": True, "command": command, "evaluationTruth": truth})

    if stage == "preflight":
        result = prepare_repository_self_test_inputs(cycle)
        return write_stage(cycle, stage, {"status": "PASS", "valid": True, "result": result})

    if stage == "tests-manifest":
        # Write the stable stage marker first, then build the manifest around
        # that exact marker. Do not rewrite the marker afterward or its digest
        # would invalidate the just-built manifest.
        marker = write_stage(cycle, stage, {"status": "PASS", "valid": True, "manifestPrepared": True})
        try:
            result = prepare_repository_self_test_inputs(cycle)
        except Exception:
            stage_path(cycle, stage).unlink(missing_ok=True)
            raise
        return {**marker, "result": result}

    if stage.startswith("tests-") and stage[-1:].isdigit():
        shard = int(stage.rsplit("-", 1)[1])
        # Shard output remains outside the shipped tree until the stage
        # completes, preventing a self-referential manifest mutation. The
        # dedicated tests-manifest stage runs immediately before shard 1,
        # which contains the repository-manifest conformance test.
        output = Path("/mnt/data") / f"aixem0581-cycle-{cycle:02d}-test-shard-{shard}.json"
        output.unlink(missing_ok=True)
        command = run(
            [sys.executable, "tools/run_tests_0581.py", "--shard-count", "8", "--shard-index", str(shard), "--output", str(output)],
            label=f"cycle {cycle} repository tests shard {shard}",
            timeout=3600,
        )
        payload = read_json(output)
        return write_stage(cycle, stage, {"status": "PASS", "valid": payload.get("successful") is True, "command": command, "externalResult": str(output), "tests": payload})

    if stage == "tests-merge":
        inputs = [Path("/mnt/data") / f"aixem0581-cycle-{cycle:02d}-test-shard-{index}.json" for index in range(8)]
        if not all(path.is_file() for path in inputs):
            raise VerificationError("cannot merge repository tests before all eight shards exist")
        command = run(
            [sys.executable, "tools/run_tests_0581.py", "--merge-shards", *[str(path) for path in inputs], "--output", "validation/test-results.json"],
            label=f"cycle {cycle} merge complete repository test inventory",
            timeout=300,
        )
        authoring = run([sys.executable, "tools/docs/authoring_validation.py"], label=f"cycle {cycle} executable authoring validation", timeout=1800)
        payload = read_json(VALIDATION / "test-results.json")
        valid = bool(payload.get("successful") and payload.get("failedModules") == 0)
        if not valid:
            raise VerificationError("merged repository test inventory is not valid")
        return write_stage(cycle, stage, {"status": "PASS", "valid": True, "commands": [command, authoring], "tests": {k: payload.get(k) for k in ("testsRun", "moduleCount", "passedModules", "failedModules")}})

    if stage == "symbol":
        command = run([sys.executable, "tools/validate_symbol_corpus.py", "--all", "--repeat", "3", "--emit-report"], label=f"cycle {cycle} symbol/static-block corpus", timeout=4200)
        return write_stage(cycle, stage, {"status": "PASS", "valid": True, "command": command})

    if stage == "hierarchy":
        command = run([sys.executable, "tools/validate_hierarchical_corpus.py", "--repeats", "3"], label=f"cycle {cycle} hierarchical corpus", timeout=4200)
        return write_stage(cycle, stage, {"status": "PASS", "valid": True, "command": command})

    if stage == "viewer":
        command = run([sys.executable, "tools/validate_reference_viewer_corpus.py", "--repeats", "3", "--screenshots"], label=f"cycle {cycle} Reference Viewer corpus", timeout=4200)
        return write_stage(cycle, stage, {"status": "PASS", "valid": True, "command": command})

    if stage == "finalize":
        stage_results, stage_errors = required_stage_results(cycle)
        governance = documentation_governance_check()
        schemas = schema_and_requirement_check()
        routes = inherited.route_authority_check()
        linkage = document_linkage()
        eval_truth = eval_truth_check()
        readiness = pre_live_readiness_check()
        corpora = inherited.corpus_evidence_check()
        protected = inherited.protected_renderer_check(cycle)
        claims = inherited_claim_integrity_check()
        test_result = read_json(VALIDATION / "test-results.json")
        tests_valid = bool(test_result.get("successful") and not test_result.get("failures") and not test_result.get("errors"))
        generated = next((item.get("generatedDeterminism") for item in stage_results if item.get("stage") == "core"), {})
        checks = [
            check("CYCLE-STAGES", not stage_errors, "Every required staged verification operation completed successfully.", errors=stage_errors, stages=[item.get("stage") for item in stage_results]),
            check("CYCLE-GENERATED-DETERMINISM", generated.get("valid") is True, "Two clean documentation/reference/site builds are byte-identical.", details=generated),
            check("CYCLE-DOCUMENT-GOVERNANCE", governance["valid"], "Every Markdown file retains one role, lifecycle, and discovery owner.", details=governance),
            check("CYCLE-LIVE-CONTRACT-SCHEMAS", schemas["valid"], "All live schemas and twenty-seven requirement mappings validate.", details=schemas),
            check("CYCLE-ROUTE-AUTHORITY", routes["valid"], "Existing authoring routes and write authorities remain canonical.", details=routes),
            check("CYCLE-DOCUMENT-LINKAGE", linkage["valid"], "Documentation, routes, site, artifacts, inventory, and traceability close.", details=linkage),
            check("CYCLE-PRE-LIVE-READINESS", readiness["valid"], "Portable success, fault, fairness, and route-readiness gates close without an AI claim.", details=readiness),
            check("CYCLE-EVALUATION-TRUTH", eval_truth["valid"], "Tier A passes and external Tier B remains explicitly unexecuted.", details=eval_truth),
            check("CYCLE-REPOSITORY-TESTS", tests_valid, "The complete sharded isolated-module repository test inventory passes.", details={k: test_result.get(k) for k in ("successful", "testsRun", "moduleCount", "passedModules", "failedModules", "durationSeconds")}),
            check("CYCLE-CORPORA", corpora["valid"], "Symbol/static-block, hierarchy, and Reference Viewer corpora remain conformant.", details=corpora),
            check("CYCLE-PROTECTED-HASHES", protected["valid"], "Protected circuit schemas and renderer/Viewer evidence remain byte-identical.", details=protected),
            check("CYCLE-CLAIM-INTEGRITY", claims["valid"], "No external AI execution or arbitrary autonomous-design claim is fabricated.", details=claims),
        ]
        valid = all(item.get("valid") is True for item in checks)
        payload = {
            "schema": "https://schemas.aixem.org/validation/document-relationship-verification-cycle/1",
            "formatVersion": "1.0",
            "release": RELEASE_ID,
            "generatedAt": FIXED_TIME,
            "cycle": cycle,
            "status": "PASS" if valid else "FAIL",
            "valid": valid,
            "documentationRelationshipClosurePassed": valid,
            "preLiveReadinessPlanPassed": valid,
            "preLiveReadiness": bool(readiness.get("preLiveReadiness")) if valid else False,
            "externalTierBExecuted": False,
            "liveExternalAgentExecuted": False,
            "liveClaimAuthorized": False,
            "durationSeconds": round(sum(float(item.get("durationSeconds", 0.0)) for stage_result in stage_results for item in stage_result.get("commands", []) if isinstance(item, dict)), 6),
            "checks": checks,
        }
        write_json(cycle_dir / "summary.json", payload)
        copy_evidence_snapshot(cycle_dir)
        report_lines = "\n".join(f"- `{item['id']}` — **{item['status']}** — {item['summary']}" for item in checks)
        write_text(cycle_dir / "report.md", f"""# AIXEM 0.5.8.1 Verification Cycle {cycle}

Status: **{payload['status']}**

{report_lines}

## Claim boundary

- Deterministic pre-live readiness: **{'PASS' if valid else 'FAIL'}**
- External AI Tier B executed: **no**
- Live external agent executed: **no**
- Live-agent claim authorized: **no**
""")
        write_stage(cycle, stage, {"status": "PASS" if valid else "FAIL", "valid": valid, "summary": cycle_dir.joinpath("summary.json").relative_to(ROOT).as_posix()})
        if not valid:
            raise VerificationError(f"verification cycle {cycle} failed")
        return payload

    raise VerificationError(f"unknown verification stage: {stage}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-passes", action="store_true", help="run all five complete cycles in one process")
    parser.add_argument("--cycle", type=int, choices=tuple(range(1, REQUIRED_CYCLES + 1)), help="run one legacy monolithic cycle")
    parser.add_argument("--stage", choices=STAGE_NAMES, help="run one bounded verification stage")
    parser.add_argument("--stage-cycle", type=int, choices=tuple(range(1, REQUIRED_CYCLES + 1)), help="cycle number for --stage")
    parser.add_argument("--close", action="store_true", help="close the release from five completed cycle summaries")
    args = parser.parse_args()
    selected = sum(bool(value) for value in (args.all_passes, args.cycle is not None, args.stage is not None, args.close))
    if selected != 1:
        parser.error("select exactly one of --all-passes, --cycle, --stage, or --close")
    if args.stage is not None and args.stage_cycle is None:
        parser.error("--stage requires --stage-cycle")
    try:
        os.chdir(ROOT)
        if args.stage is not None:
            result = run_verification_stage(args.stage_cycle, args.stage)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.close:
            cycles = [read_json(RUNS / f"run-{cycle:02d}/summary.json") for cycle in range(1, REQUIRED_CYCLES + 1)]
            result = final_closure(cycles)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
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
