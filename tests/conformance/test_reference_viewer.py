"""Behavioral and deterministic conformance for AIXEM Reference Viewer 1."""
from __future__ import annotations

import json
import pathlib
import re
import tempfile
import unittest
from collections import Counter

from tests.conformance.viewer_test_support import (
    ViewerFixture,
    browser_page,
    render_multi,
    render_single,
    sha256_hex,
)


class ReferenceViewerConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = ViewerFixture("H001", "H004", "H013")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.close()

    def test_v001_single_sheet_reference_viewer(self) -> None:
        model = self.fixture.model("single")
        html = self.fixture.html("single")
        self.assertEqual(["sheet"], [item["id"] for item in model["views"]])
        self.assertEqual("main", model["initialState"]["activeSheet"])
        self.assertIn('data-aixem-profile="reference-viewer"', html)
        self.assertNotIn('data-mode="overview"', html)
        self.assertNotIn('data-mode="composite"', html)
        for unsupported in ("Place wire", "Place symbol", "Place net label", "Save", "Undo", "Redo"):
            self.assertNotIn(unsupported, html)
        with browser_page(html) as (page, errors, requests):
            self.assertEqual("sheet", page.locator(".view-panel:not([hidden])").get_attribute("data-aixem-view"))
            first_entity = next(qid for qid in model["objects"] if qid.startswith("entity:main:"))
            page.locator(f'[data-aixem-select="{first_entity}"]').click()
            self.assertIn(first_entity, page.locator("#inspector-body").inner_text())
            self.assertGreater(page.locator(f'[data-aixem-qid="{first_entity}"].selected').count(), 0)
            self.assertEqual([], errors)
            self.assertEqual([], requests)

    def test_v002_v003_multisheet_modes_and_hierarchy_navigation(self) -> None:
        model = self.fixture.model("H001")
        self.assertEqual(["sheet", "overview", "composite"], [item["id"] for item in model["views"]])
        self.assertEqual(["power", "control"], [item["id"] for item in model["hierarchy"]])
        with browser_page(self.fixture.html("H001")) as (page, errors, requests):
            self.assertEqual("power", page.locator(".view-panel:not([hidden])").get_attribute("data-sheet-panel"))
            page.locator('[data-aixem-select="sheet:control"]').click()
            self.assertEqual("control", page.locator(".view-panel:not([hidden])").get_attribute("data-sheet-panel"))
            for mode in ("overview", "composite", "sheet"):
                page.locator(f'[data-mode="{mode}"]').click()
                self.assertEqual(mode, page.locator(".view-panel:not([hidden])").get_attribute("data-aixem-view"))
                self.assertEqual("true", page.locator(f'[data-mode="{mode}"]').get_attribute("aria-pressed"))
            page.locator('[data-mode="overview"]').click()
            page.locator('.view-panel:not([hidden]) [data-aixem-qid="sheet:power"]').first.click()
            self.assertEqual("sheet", page.locator(".view-panel:not([hidden])").get_attribute("data-aixem-view"))
            self.assertEqual("power", page.locator(".view-panel:not([hidden])").get_attribute("data-sheet-panel"))
            self.assertEqual([], errors)
            self.assertEqual([], requests)

    def test_v004_same_name_local_net_isolation(self) -> None:
        html = self.fixture.html("H004")
        with browser_page(html) as (page, errors, _requests):
            page.fill("#viewer-search", "local-net:alpha:vcc")
            alpha = page.locator('[data-aixem-select="local-net:alpha:vcc"]')
            self.assertFalse(alpha.is_hidden())
            alpha.click()
            self.assertIn("local-net:alpha:vcc", page.locator("#inspector-body").inner_text())
            self.assertGreater(page.locator('[data-aixem-qid="local-net:alpha:vcc"].selected').count(), 0)
            self.assertEqual(0, page.locator('[data-aixem-qid="local-net:beta:vcc"].selected').count())
            self.assertEqual([], errors)

    def test_v005_v006_project_net_and_interface_selection(self) -> None:
        html = self.fixture.html("H001")
        with browser_page(html) as (page, errors, _requests):
            page.fill("#viewer-search", "project-net:control_signal")
            page.locator('[data-aixem-select="project-net:control_signal"]').click()
            inspector = page.locator("#inspector-body").inner_text()
            self.assertIn("project-net:control_signal", inspector)
            self.assertIn("interface:power:OUT", inspector)
            self.assertIn("interface:control:IN", inspector)
            for mode in ("overview", "composite"):
                page.locator(f'[data-mode="{mode}"]').click()
                panel = page.locator(".view-panel:not([hidden])")
                self.assertGreater(panel.locator('[data-aixem-qid="project-net:control_signal"].selected').count(), 0)
                self.assertGreater(panel.locator('[data-aixem-qid="interface:power:OUT"].selected').count(), 0)
                self.assertGreater(panel.locator('[data-aixem-qid="interface:control:IN"].selected').count(), 0)
                self.assertEqual(0, panel.locator('[data-aixem-qid="project-net:vcc_5v"].selected').count())
            page.fill("#viewer-search", "interface:control:VCC")
            page.locator('[data-aixem-select="interface:control:VCC"]').click()
            self.assertIn("interface:control:VCC", page.locator("#inspector-body").inner_text())
            self.assertIn("local-net:control:vcc", page.locator("#inspector-body").inner_text())
            self.assertIn("project-net:vcc_5v", page.locator("#inspector-body").inner_text())
            self.assertEqual([], errors)

    def test_v007_sheet_scoped_layer_visibility(self) -> None:
        html = self.fixture.html("H001")
        with browser_page(html) as (page, errors, _requests):
            page.locator('[data-mode="composite"]').click()
            power_layer = page.locator('[data-sheet-canvas="power"] [data-layer="connections"]').last
            control_layer = page.locator('[data-sheet-canvas="control"] [data-layer="connections"]').last
            self.assertNotEqual("none", power_layer.evaluate("e => e.style.display"))
            self.assertNotEqual("none", control_layer.evaluate("e => e.style.display"))
            page.locator('[data-toggle-sheet-layer][data-layer-sheet-id="power"][data-layer-id="connections"]').uncheck()
            self.assertEqual("none", power_layer.evaluate("e => e.style.display"))
            self.assertNotEqual("none", control_layer.evaluate("e => e.style.display"))
            model = json.loads(page.locator("#aixem-viewer-model").text_content())
            self.assertTrue(model["initialState"]["visibleLayersBySheet"]["power"]["connections"])
            self.assertEqual([], errors)

    def test_v008_cross_view_selection_continuity(self) -> None:
        with browser_page(self.fixture.html("H001")) as (page, errors, _requests):
            page.fill("#viewer-search", "project-net:vcc_5v")
            page.locator('[data-aixem-select="project-net:vcc_5v"]').click()
            identity = page.locator("#inspector-body").inner_text()
            for mode in ("overview", "composite", "sheet", "overview"):
                page.locator(f'[data-mode="{mode}"]').click()
                self.assertIn("project-net:vcc_5v", page.locator("#inspector-body").inner_text())
            self.assertEqual(identity, page.locator("#inspector-body").inner_text())
            self.assertEqual([], errors)

    def test_v009_component_search_opens_owning_sheet(self) -> None:
        with browser_page(self.fixture.html("H001")) as (page, errors, _requests):
            page.locator('[data-mode="overview"]').click()
            page.fill("#viewer-search", "entity:control:U1")
            page.locator('[data-aixem-select="entity:control:U1"]').click()
            visible = page.locator(".view-panel:not([hidden])")
            self.assertEqual("sheet", visible.get_attribute("data-aixem-view"))
            self.assertEqual("control", visible.get_attribute("data-sheet-panel"))
            self.assertIn("entity:control:U1", page.locator("#inspector-body").inner_text())
            self.assertEqual([], errors)

    def test_v010_pan_zoom_fit_per_view_state(self) -> None:
        with browser_page(self.fixture.html("H001")) as (page, errors, _requests):
            sheet_canvas = page.locator('[data-canvas-key="sheet:power"]')
            initial = sheet_canvas.get_attribute("style")
            page.locator('[data-aixem-action="zoom-in"]').click()
            zoomed = sheet_canvas.get_attribute("style")
            self.assertNotEqual(initial, zoomed)
            page.keyboard.press("ArrowRight")
            page.locator('[data-mode="overview"]').click()
            overview = page.locator('[data-canvas-key="overview"]')
            overview_before = overview.get_attribute("style")
            page.locator('[data-aixem-action="zoom-in"]').click()
            self.assertNotEqual(overview_before, overview.get_attribute("style"))
            page.locator('[data-mode="sheet"]').click()
            self.assertEqual(zoomed, sheet_canvas.get_attribute("style"))
            page.keyboard.press("0")
            self.assertIn("transform:", sheet_canvas.get_attribute("style"))
            self.assertEqual([], errors)

    def test_v015_dom_identity_closure_and_unique_ids(self) -> None:
        model = self.fixture.model("H001")
        with browser_page(self.fixture.html("H001")) as (page, errors, _requests):
            ids = page.eval_on_selector_all("[id]", "elements => elements.map(element => element.id)")
            self.assertEqual([], [item for item, count in Counter(ids).items() if count > 1])
            dom_qids = set(page.eval_on_selector_all("[data-aixem-qid]", "elements => elements.map(element => element.dataset.aixemQid)"))
            self.assertTrue(dom_qids.issubset(model["objects"].keys()))
            self.assertTrue({"entity:power:U1", "entity:control:U1"}.issubset(dom_qids))
            self.assertTrue({"local-net:power:vcc", "local-net:control:vcc"}.issubset(dom_qids))
            self.assertEqual("1", page.locator('[data-aixem-viewer="1"]').get_attribute("data-aixem-dom-contract"))
            self.assertEqual([], errors)

    def test_v016_ten_sheet_scale_baseline(self) -> None:
        model = self.fixture.model("H013")
        self.assertEqual(10, model["statistics"]["sheets"])
        with browser_page(self.fixture.html("H013"), width=1600, height=1000) as (page, errors, requests):
            self.assertEqual(10, page.locator('[data-nav-group="sheet"] [data-aixem-select^="sheet:"]').count())
            for mode in ("overview", "composite"):
                page.locator(f'[data-mode="{mode}"]').click()
                self.assertEqual(mode, page.locator(".view-panel:not([hidden])").get_attribute("data-aixem-view"))
            page.fill("#viewer-search", "project-net:vcc")
            page.locator('[data-aixem-select="project-net:vcc"]').click()
            self.assertIn("project-net:vcc", page.locator("#inspector-body").inner_text())
            self.assertEqual([], errors)
            self.assertEqual([], requests)

    def test_v017_viewer_workbench_are_distinct_shared_profiles(self) -> None:
        output = self.fixture.outputs["H001"]
        viewer = self.fixture.html("H001", "viewer")
        workbench = self.fixture.html("H001", "workbench")
        self.assertNotEqual(sha256_hex(output / "viewer.html"), sha256_hex(output / "workbench.html"))
        self.assertIn('data-aixem-profile="reference-viewer"', viewer)
        self.assertNotIn('data-aixem-workbench-region="evidence"', viewer)
        self.assertIn('data-aixem-profile="review-workbench"', workbench)
        self.assertIn('data-aixem-workbench-region="evidence"', workbench)
        for marker in ('data-mode="sheet"', 'data-mode="overview"', 'data-mode="composite"', 'data-aixem-action="fit"'):
            self.assertIn(marker, viewer)
            self.assertIn(marker, workbench)

    def test_v018_three_run_viewer_artifact_determinism(self) -> None:
        runs: list[dict[str, str]] = []
        with tempfile.TemporaryDirectory(prefix="aixem-viewer-v018-") as temporary:
            root = pathlib.Path(temporary)
            for index in range(3):
                output = root / str(index)
                render_multi("H001", output)
                runs.append({name: sha256_hex(output / name) for name in ("viewer-model.json", "viewer.html", "workbench.html")})
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(runs[0], runs[2])


if __name__ == "__main__":
    unittest.main()
