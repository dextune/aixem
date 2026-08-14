"""AIXEM 0.5.4 hierarchical multi-sheet and Viewer regression tests."""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMATIC = ROOT / "implementation" / "schematic"
TOOLS = ROOT / "tools"
for path in (SCHEMATIC, TOOLS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from component_core import AixemGraphicsError, parse_aixem  # noqa: E402
from project_composition import ProjectCompositionResolver  # noqa: E402
from render_project import (  # noqa: E402
    DEFAULT_SCHEMA_ROOT,
    DEFAULT_STYLE,
    GridProjectRenderer,
    MultiSheetProjectRenderer,
)

CORPUS = ROOT / "validation" / "corpus" / "hierarchical-project-1"
PROJECT_SCHEMA_V1 = ROOT / "docs" / "specifications" / "schemas" / "component-graphics-1" / "aixem-project-manifest-1.schema.json"
LAYOUT_SCHEMA_V1 = ROOT / "docs" / "specifications" / "schemas" / "component-graphics-1" / "aixem-explicit-layout-1.schema.json"
BASELINE_PROJECT_SCHEMA_DIGEST = "056932ff46d7b6928f3b01dba50403353bdfda8f4d28e8b7bf0d38ab1dd39a41"
BASELINE_LAYOUT_SCHEMA_DIGEST = "4f92e5e292a694aabfca922cc449f2f59a1a08e6465181a096a62b47b23bfca7"
BASELINE_LEGACY_DRAWING_DIGEST = "cbf6775048b06eeb120530abece8148a73e0b0bebdf493f5cfc7eee9708d8080"
BASELINE_CANONICAL_LIBRARY_SCENE_DIGEST = "ebdd9d963765ff7b771683ead96e209ed7f0ef8cb7d7d21c12f4daa84decdd0a"


def read_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_hex(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case_dir(case_id: str, *, negative: bool = False) -> pathlib.Path:
    parent = CORPUS / ("negative" if negative else "cases")
    matches = sorted(parent.glob(f"{case_id}-*"))
    if len(matches) != 1:
        raise AssertionError(f"expected one {case_id} case, found {matches}")
    return matches[0]


def leaf_factory(project_file, schema_root, project_doc, project_root):
    return GridProjectRenderer(
        project_file, schema_root, DEFAULT_STYLE,
        project_doc=project_doc, project_root=project_root,
    )


class HierarchicalProjectConformanceTests(unittest.TestCase):
    def test_inventory_is_exact(self) -> None:
        manifest = read_json(CORPUS / "manifest.json")
        self.assertEqual(15, len(manifest["cases"]))
        self.assertEqual(15, len(manifest["negativeFixtures"]))
        self.assertEqual([f"H{index:03d}" for index in range(1, 16)], [read_json(CORPUS / item)["id"] for item in manifest["cases"]])
        self.assertEqual([f"N{index:03d}" for index in range(1, 16)], [read_json(CORPUS / item)["id"] for item in manifest["negativeFixtures"]])

    def test_v1_schema_contracts_are_immutable(self) -> None:
        self.assertEqual(BASELINE_PROJECT_SCHEMA_DIGEST, sha256_hex(PROJECT_SCHEMA_V1))
        self.assertEqual(BASELINE_LAYOUT_SCHEMA_DIGEST, sha256_hex(LAYOUT_SCHEMA_V1))

    def test_interface_endpoint_is_a_real_leaf_semantic_endpoint(self) -> None:
        semantic = parse_aixem(case_dir("H002") / "circuits" / "source.aixem")
        self.assertIn("OUT", semantic["ports"])
        self.assertEqual(["U1.5", "@OUT"], semantic["nets"]["out"])
        self.assertEqual("out", semantic["endpointOwners"]["@OUT"])
        self.assertTrue(any(item["id"] == "hierarchical.interface@1" and item["required"] == "true" for item in semantic["features"]))

    def test_project_graph_queries_and_name_isolation(self) -> None:
        h001 = ProjectCompositionResolver(case_dir("H001") / "project.aixproj.json", DEFAULT_SCHEMA_ROOT, leaf_factory)
        self.assertEqual(["power", "control"], h001.participating_sheets("vcc_5v"))
        self.assertEqual("vcc", h001.local_net_for_port("control", "VCC"))
        self.assertIn("entity:control:U1.9", h001.transitive_endpoints("vcc_5v"))
        self.assertTrue(h001.project_net_crosses_hierarchy_boundary("vcc_5v"))

        h004 = ProjectCompositionResolver(case_dir("H004") / "project.aixproj.json", DEFAULT_SCHEMA_ROOT, leaf_factory)
        self.assertEqual({}, h004.project_nets)
        self.assertEqual(4, len(h004.unconnected_ports()))
        self.assertEqual("vcc", h004.local_net_for_port("alpha", "VCC"))
        self.assertEqual("vcc", h004.local_net_for_port("beta", "VCC"))

    def test_hierarchy_is_explicit_acyclic_and_deterministic(self) -> None:
        resolver = ProjectCompositionResolver(case_dir("H005") / "project.aixproj.json", DEFAULT_SCHEMA_ROOT, leaf_factory)
        self.assertEqual(["system", "control", "debug"], resolver.preorder)
        self.assertEqual([0, 1, 2], [resolver.hierarchy_depth(item) for item in resolver.preorder])
        self.assertEqual("control", resolver.sheets["debug"].parent)

        with self.assertRaisesRegex(AixemGraphicsError, "PROJECT_HIERARCHY_CYCLE"):
            ProjectCompositionResolver(case_dir("N012", negative=True) / "project.aixproj.json", DEFAULT_SCHEMA_ROOT, leaf_factory)

    def test_project_net_equivalence_collision_fails_closed(self) -> None:
        with self.assertRaisesRegex(AixemGraphicsError, "PROJECT_NET_EQUIVALENCE_COLLISION"):
            ProjectCompositionResolver(case_dir("H015") / "project.aixproj.json", DEFAULT_SCHEMA_ROOT, leaf_factory)

    def test_multi_view_render_outputs_and_workbench_are_data_driven(self) -> None:
        renderer = MultiSheetProjectRenderer(case_dir("H001") / "project.aixproj.json", DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE)
        with tempfile.TemporaryDirectory(prefix="aixem-h001-test-") as temporary:
            output = pathlib.Path(temporary)
            result = renderer.render(output)
            self.assertTrue(result["validation"]["valid"])
            for relative in (
                "sheets/power.svg", "sheets/control.svg",
                "sheets/power.resolved-scene.json", "sheets/control.resolved-scene.json",
                "interface-summaries/power.json", "interface-summaries/control.json",
                "project-overview.svg", "project-composite.svg",
                "resolved-project-scene.json", "viewer-model.json", "viewer.html", "workbench.html",
            ):
                self.assertTrue((output / relative).is_file(), relative)
            viewer = (output / "viewer.html").read_text(encoding="utf-8")
            workbench = (output / "workbench.html").read_text(encoding="utf-8")
            model = read_json(output / "viewer-model.json")
            for html in (viewer, workbench):
                self.assertIn('data-mode="sheet"', html)
                self.assertIn('data-mode="overview"', html)
                self.assertIn('data-mode="composite"', html)
                self.assertIn('data-aixem-select="sheet:power"', html)
                self.assertIn('data-aixem-select="sheet:control"', html)
                self.assertNotIn("Place wire", html)
                self.assertNotIn("Place symbol", html)
                self.assertNotIn("Analog Front End", html)
                self.assertNotIn("Debug Interface", html)
            self.assertIn('data-aixem-profile="reference-viewer"', viewer)
            self.assertIn('data-aixem-profile="review-workbench"', workbench)
            self.assertNotEqual(sha256_hex(output / "viewer.html"), sha256_hex(output / "workbench.html"))
            self.assertEqual(["sheet", "overview", "composite"], [item["id"] for item in model["views"]])
            self.assertEqual("power", model["initialState"]["activeSheet"])
            composite = (output / "project-composite.svg").read_text(encoding="utf-8")
            self.assertIn('data-sheet="power"', composite)
            self.assertIn('data-project-net="vcc_5v"', composite)
            ids = []
            import re
            ids = re.findall(r'\bid="([^"]+)"', composite)
            self.assertEqual(len(ids), len(set(ids)))

    def test_ten_sheet_project_and_three_run_determinism(self) -> None:
        project = case_dir("H013") / "project.aixproj.json"
        digests: list[dict[str, str]] = []
        for repeat in range(3):
            with tempfile.TemporaryDirectory(prefix=f"aixem-h013-{repeat}-") as temporary:
                output = pathlib.Path(temporary)
                renderer = MultiSheetProjectRenderer(project, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE)
                result = renderer.render(output)
                self.assertEqual(10, result["scene"]["statistics"]["sheets"])
                self.assertEqual(2, result["scene"]["statistics"]["projectNets"])
                digests.append({
                    "overview": sha256_hex(output / "project-overview.svg"),
                    "composite": sha256_hex(output / "project-composite.svg"),
                    "scene": sha256_hex(output / "resolved-project-scene.json"),
                    "viewer-model": sha256_hex(output / "viewer-model.json"),
                    "viewer": sha256_hex(output / "viewer.html"),
                    "workbench": sha256_hex(output / "workbench.html"),
                    **{f"sheet:{sheet_id}:svg": sha256_hex(output / "sheets" / f"{sheet_id}.svg") for sheet_id in renderer.resolver.preorder},
                    **{f"sheet:{sheet_id}:scene": sha256_hex(output / "sheets" / f"{sheet_id}.resolved-scene.json") for sheet_id in renderer.resolver.preorder},
                })
        self.assertEqual(digests[0], digests[1])
        self.assertEqual(digests[0], digests[2])

    def test_production_geometry_remains_stable_after_canonical_library_migration(self) -> None:
        project = ROOT / "examples" / "electronics-grid-controller" / "project.aixproj.json"
        with tempfile.TemporaryDirectory(prefix="aixem-v1-regression-") as temporary:
            output = pathlib.Path(temporary)
            GridProjectRenderer(project, DEFAULT_SCHEMA_ROOT, DEFAULT_STYLE).render(output)
            self.assertEqual(BASELINE_LEGACY_DRAWING_DIGEST, sha256_hex(output / "drawing.svg"))
            self.assertEqual(BASELINE_CANONICAL_LIBRARY_SCENE_DIGEST, sha256_hex(output / "resolved-scene.json"))
            viewer = (output / "viewer.html").read_text(encoding="utf-8")
            workbench = (output / "workbench.html").read_text(encoding="utf-8")
            model = read_json(output / "viewer-model.json")
            self.assertEqual(["sheet"], [item["id"] for item in model["views"]])
            self.assertEqual("main", model["initialState"]["activeSheet"])
            self.assertIn('data-aixem-select="sheet:main"', viewer)
            self.assertIn('data-aixem-profile="reference-viewer"', viewer)
            self.assertIn('data-aixem-profile="review-workbench"', workbench)
            self.assertNotIn("Place wire", viewer + workbench)
            self.assertNotIn("Power Supply", workbench)
            self.assertNotEqual(sha256_hex(output / "viewer.html"), sha256_hex(output / "workbench.html"))

    def test_complete_corpus_runner(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aixem-hierarchical-report-"):
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "validate_hierarchical_corpus.py"), "--repeats", "1", "--no-commit-outputs"],
                cwd=ROOT, text=True, capture_output=True,
            )
        self.assertEqual(0, proc.returncode, proc.stdout + "\n" + proc.stderr)
        self.assertIn("hierarchical corpus: PASS (30/30)", proc.stdout)


if __name__ == "__main__":
    unittest.main()
