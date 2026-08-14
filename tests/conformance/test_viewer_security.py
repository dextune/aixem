"""Security, embedding, and fail-closed tests for AIXEM Reference Viewer 1."""
from __future__ import annotations

import copy
import json
import pathlib
import re
import sys
import unittest

from tests.conformance.viewer_test_support import ViewerFixture, browser_page

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMATIC = ROOT / "implementation" / "schematic"
if str(SCHEMATIC) not in sys.path:
    sys.path.insert(0, str(SCHEMATIC))

from viewer import ReferenceViewerRenderer, ViewerModelError, validate_viewer_model  # noqa: E402
from viewer.core import safe_json_for_script  # noqa: E402


class ViewerSecurityConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = ViewerFixture("H001")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.close()

    def test_v013_offline_network_denial_and_csp(self) -> None:
        html = self.fixture.html("H001")
        self.assertIn("default-src 'none'", html)
        self.assertIn("connect-src 'none'", html)
        self.assertIn("form-action 'none'", html)
        self.assertIn("base-uri 'none'", html)
        self.assertNotRegex(html, r'''(?:src|href)=["']https?://''')
        runtime = html.split('<script id="aixem-viewer-model"', 1)[1]
        for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "sendBeacon", "localStorage", "sessionStorage", "indexedDB", "document.cookie", "eval(", "new Function"):
            self.assertNotIn(forbidden, runtime)
        with browser_page(html) as (page, errors, requests):
            page.locator('[data-mode="overview"]').click()
            page.locator('[data-aixem-action="zoom-in"]').click()
            page.fill("#viewer-search", "vcc")
            self.assertEqual([], requests)
            self.assertEqual([], errors)

    def test_v014_hostile_authored_text_is_inert(self) -> None:
        model = copy.deepcopy(self.fixture.model("H001"))
        hostile = '</script><img id="aixem-attack" src=x onerror="window.__aixemPwned=1">&\"\u2028'
        model["project"]["title"] = hostile
        model["objects"]["sheet:power"]["label"] = hostile
        model["objects"]["sheet:power"]["properties"].append({"label": "Hostile", "value": hostile})
        model["diagnostics"].append({"code": "HOSTILE", "severity": "info", "status": "PASS", "message": hostile})
        validate_viewer_model(model)
        output = self.fixture.outputs["H001"]
        sheet_svgs = {
            item["id"]: (output / "sheets" / f"{item['id']}.svg").read_text(encoding="utf-8")
            for item in model["sheets"]
        }
        rendered = ReferenceViewerRenderer().render(
            model,
            sheet_svgs=sheet_svgs,
            overview_svg=(output / "project-overview.svg").read_text(encoding="utf-8"),
            composite_svg=(output / "project-composite.svg").read_text(encoding="utf-8"),
        )
        self.assertNotIn("</script><img", rendered)
        self.assertIn("\\u003c/script\\u003e", rendered)
        self.assertIn("&lt;/script&gt;&lt;img", rendered)
        serialized = str(safe_json_for_script({"value": hostile}))
        self.assertNotIn("</script>", serialized)
        with browser_page(rendered) as (page, errors, requests):
            self.assertEqual(0, page.locator("#aixem-attack").count())
            self.assertIsNone(page.evaluate("window.__aixemPwned"))
            embedded = json.loads(page.locator("#aixem-viewer-model").text_content())
            self.assertEqual(hostile, embedded["project"]["title"])
            page.locator('[data-aixem-select="sheet:power"]').click()
            self.assertIn(hostile, page.locator("#inspector-body").inner_text())
            self.assertEqual([], errors)
            self.assertEqual([], requests)

    def test_structural_negative_viewer_models_fail_closed(self) -> None:
        baseline = self.fixture.model("H001")
        cases = []
        invalid = copy.deepcopy(baseline)
        invalid["schema"] = "https://schemas.aixem.org/viewer/viewer-model/999"
        cases.append((invalid, "VIEWER_SCHEMA_UNSUPPORTED"))
        invalid = copy.deepcopy(baseline)
        invalid["objects"]["sheet:power"]["relatedQids"] = ["entity:missing:U1"]
        cases.append((invalid, "VIEWER_UNRESOLVED_QIDS"))
        invalid = copy.deepcopy(baseline)
        invalid["initialState"]["activeSheet"] = "missing"
        cases.append((invalid, "VIEWER_ACTIVE_SHEET_UNKNOWN"))
        invalid = copy.deepcopy(baseline)
        invalid["objects"]["entity:power:U1"]["qid"] = "entity:control:U1"
        cases.append((invalid, "VIEWER_QID_KEY_MISMATCH"))
        for model, code in cases:
            with self.subTest(code=code), self.assertRaisesRegex(ViewerModelError, code):
                validate_viewer_model(model)


if __name__ == "__main__":
    unittest.main()
