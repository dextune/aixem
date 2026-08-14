"""Repository-wide document information architecture and governance tests."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools" / "docs"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import aixem_docs  # noqa: E402


class DocumentGovernanceTests(unittest.TestCase):
    """Release-gating checks referenced by Repository Document Governance Contract 1."""

    @classmethod
    def setUpClass(cls) -> None:
        aixem_docs.compile_generated()
        aixem_docs.build_site()

    def audit(self, *, redirects: bool = False) -> dict:
        result = aixem_docs.audit_repository_documents(require_redirects=redirects)
        self.assertTrue(result["valid"], result["errors"])
        return result

    def test_every_markdown_has_exactly_one_role(self) -> None:
        result = self.audit()
        self.assertEqual(0, result["unknownRoles"])
        inventory = result["inventory"]
        paths = [item["path"] for item in inventory["documents"]]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn("unknown", {item["role"] for item in inventory["documents"]})

    def test_root_hygiene_and_reserved_names(self) -> None:
        result = self.audit()
        policy = aixem_docs.load_repository_document_policy()
        observed = sorted(path.name for path in ROOT.glob("*.md"))
        self.assertEqual(sorted(policy["rootMarkdownAllowlist"]), observed)
        self.assertEqual(
            {"AGENTS.md", "README.md", "REFERENCE.md", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", "NOTICE.md", "START_HERE.md"},
            set(observed),
        )
        self.assertNotIn("RELEASE_NOTES.md", observed)
        self.assertFalse(any(name.startswith("PLAN-") for name in observed))
        self.assertEqual(0, result["orphans"])

    def test_role_aware_discoverability_has_no_orphans(self) -> None:
        result = self.audit()
        human = [item for item in result["inventory"]["documents"] if item["humanAuthored"]]
        self.assertTrue(human)
        self.assertTrue(all(item["discoverable"] for item in human))
        self.assertEqual([], [item["path"] for item in human if not item["discoverable"]])

    def test_canonical_structure_has_terminal_footer_and_no_patch_blocks(self) -> None:
        self.audit()
        for doc in aixem_docs.load_documents():
            text = doc.path.read_text(encoding="utf-8").rstrip()
            self.assertTrue(text.endswith(aixem_docs.CANONICAL_FOOTER), doc.rel)
            self.assertEqual(1, text.count(aixem_docs.CANONICAL_FOOTER), doc.rel)
            self.assertIsNone(aixem_docs.PATCH_MARKER_RE.search(text), doc.rel)

    def test_path_migrations_preserve_identity_and_redirects(self) -> None:
        result = self.audit(redirects=True)
        migration = result["pathMigrations"]
        self.assertTrue(migration["valid"], migration["errors"])
        self.assertEqual(4, migration["migrations"])
        index = json.loads((ROOT / "docs" / "_meta" / "generated" / "path-migration-index.json").read_text(encoding="utf-8"))
        self.assertEqual(4, len(index["migrations"]))
        for record in index["migrations"]:
            self.assertTrue((ROOT / "site" / record["fromSitePath"]).is_file())
            self.assertTrue((ROOT / record["to"]).is_file())

    def test_metadata_vocabularies_and_token_estimates(self) -> None:
        self.audit()
        for doc in aixem_docs.load_documents():
            self.assertIn(doc.meta["domain"], aixem_docs.CONTROLLED_DOMAINS, doc.rel)
            self.assertIn(doc.meta["kind"], aixem_docs.CONTROLLED_KINDS, doc.rel)
            expected = aixem_docs.deterministic_token_estimate(doc.body)
            observed = int(doc.meta["agent"]["estimated_tokens"])
            self.assertLessEqual(abs(expected - observed), max(64, int(expected * 0.20)), doc.rel)

    def test_repository_inventory_is_deterministic(self) -> None:
        first = aixem_docs.audit_repository_documents()["inventory"]
        second = aixem_docs.audit_repository_documents()["inventory"]
        self.assertEqual(aixem_docs.canonical_json(first), aixem_docs.canonical_json(second))
        generated = json.loads((ROOT / "docs" / "_meta" / "generated" / "repository-document-inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(aixem_docs.canonical_json(first), aixem_docs.canonical_json(generated))

    def test_planning_and_validation_lifecycles(self) -> None:
        result = self.audit()
        records = result["inventory"]["documents"]
        plans = [item for item in records if item["role"] == "implementation-plan"]
        reports = [item for item in records if item["role"] == "validation-report"]
        self.assertEqual(11, len(plans))
        self.assertTrue(reports)
        self.assertTrue(all(item["release"] for item in plans + reports))
        self.assertTrue(all(item["lifecycle"] == "historical" for item in plans))
        self.assertTrue(all(item["lifecycle"] == "release-scoped" for item in reports))

    def test_agents_document_creation_gate(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for phrase in (
            "Before Creating a Document",
            "What repository document role will it have?",
            "Which existing owner was considered?",
            "Which official navigation, index, suite descriptor, or registry will expose it?",
            "What is its lifecycle",
            "Does its path and filename satisfy the role rule?",
            "Which validator proves it is classified, linked, and discoverable?",
        ):
            self.assertIn(phrase, text)

    def test_root_reference_chain_reaches_all_human_documents(self) -> None:
        result = self.audit()["relationships"]
        links = result["rootLinkIntegrity"]
        areas = result["repositoryAreaCoverage"]
        reachability = result["rootReachability"]
        self.assertTrue(links["valid"], links["errors"])
        self.assertGreater(links["linksChecked"], 0)
        self.assertTrue(areas["valid"], areas["errors"])
        self.assertEqual(areas["targets"], areas["linked"])
        self.assertEqual([], areas["missing"])
        self.assertTrue(reachability["valid"], reachability["errors"])
        self.assertEqual(reachability["humanAuthored"], reachability["reachable"])
        self.assertEqual([], reachability["unreachable"])
        self.assertLessEqual(reachability["maxDepth"], 6)
        self.assertTrue((ROOT / "docs" / "_meta" / "generated" / "document-relationship-audit.json").is_file())

    def test_section_indexes_cover_navigation_members(self) -> None:
        coverage = self.audit()["relationships"]["sectionIndexCoverage"]
        self.assertTrue(coverage["valid"], coverage["errors"])
        self.assertEqual(coverage["items"], coverage["linked"])
        self.assertTrue(all(not item["missing"] for item in coverage["records"]))

    def test_current_release_pointers_are_coherent(self) -> None:
        coherence = self.audit()["relationships"]["currentReleaseCoherence"]
        self.assertTrue(coherence["valid"], coherence["errors"])
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), coherence["version"])
        self.assertTrue(all(item["valid"] for item in coherence["checks"]))

    def test_normative_authority_scopes_are_unambiguous(self) -> None:
        scopes = self.audit()["relationships"]["authorityScopeReview"]
        self.assertTrue(scopes["valid"], scopes["errors"])
        self.assertEqual({}, scopes["collisions"])
        self.assertIn("architecture-decision", scopes["sharedAllowed"])

    def test_unknown_markdown_fails_closed(self) -> None:
        probe = ROOT / "unclassified-governance-probe.md"
        self.assertFalse(probe.exists())
        try:
            probe.write_text("# Unclassified probe\n", encoding="utf-8")
            result = aixem_docs.audit_repository_documents()
            self.assertFalse(result["valid"])
            self.assertTrue(any("expected exactly one document role" in error for error in result["errors"]), result["errors"])
        finally:
            probe.unlink(missing_ok=True)
        self.audit()


if __name__ == "__main__":
    unittest.main()
