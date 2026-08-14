"""Keyboard, focus, semantic-state, and narrow-viewport Viewer conformance."""
from __future__ import annotations

import unittest

from tests.conformance.viewer_test_support import ViewerFixture, browser_page


class ViewerAccessibilityConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = ViewerFixture("H001")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.close()

    def test_v011_keyboard_only_required_workflow(self) -> None:
        with browser_page(self.fixture.html("H001")) as (page, errors, _requests):
            page.keyboard.press("/")
            self.assertEqual("viewer-search", page.evaluate("document.activeElement.id"))
            page.keyboard.type("project-net:vcc_5v")
            result = page.locator('[data-aixem-select="project-net:vcc_5v"]')
            result.focus()
            page.keyboard.press("Enter")
            self.assertIn("project-net:vcc_5v", page.locator("#inspector-body").inner_text())
            page.keyboard.press("Escape")
            self.assertIn("No semantic object selected", page.locator("#inspector-body").inner_text())
            viewport = page.locator('.view-panel:not([hidden]) .viewport')
            viewport.focus()
            page.keyboard.press("0")
            transform = page.locator('.view-panel:not([hidden]) .canvas-transform').get_attribute("style")
            page.keyboard.press("+")
            self.assertNotEqual(transform, page.locator('.view-panel:not([hidden]) .canvas-transform').get_attribute("style"))
            page.keyboard.press("ArrowRight")
            self.assertEqual([], errors)

    def test_programmatic_control_state_and_visible_focus(self) -> None:
        with browser_page(self.fixture.html("H001")) as (page, errors, _requests):
            self.assertEqual("true", page.locator('[data-mode="sheet"]').get_attribute("aria-pressed"))
            page.locator('[data-mode="overview"]').click()
            self.assertEqual("true", page.locator('[data-mode="overview"]').get_attribute("aria-pressed"))
            self.assertEqual("false", page.locator('[data-mode="sheet"]').get_attribute("aria-pressed"))
            page.locator('[data-nav-category="project-net"]').click()
            self.assertEqual("true", page.locator('[data-nav-category="project-net"]').get_attribute("aria-selected"))
            button = page.locator('[data-aixem-action="fit"]')
            button.focus()
            page.keyboard.press("Shift+Tab")
            page.keyboard.press("Tab")
            self.assertEqual("fit", page.evaluate("document.activeElement.dataset.aixemAction"))
            focus_outline = button.evaluate("element => getComputedStyle(element).outlineStyle")
            focus_shadow = button.evaluate("element => getComputedStyle(element).boxShadow")
            self.assertTrue(focus_outline != "none" or focus_shadow != "none")
            self.assertEqual([], errors)

    def test_v012_narrow_viewport_retains_navigation_and_inspection(self) -> None:
        with browser_page(self.fixture.html("H001"), width=760, height=700) as (page, errors, _requests):
            nav_toggle = page.locator('[data-aixem-action="toggle-navigator"]')
            inspector_toggle = page.locator('[data-aixem-action="toggle-inspector"]')
            self.assertTrue(nav_toggle.is_visible())
            self.assertTrue(inspector_toggle.is_visible())
            nav_toggle.click()
            self.assertEqual("true", nav_toggle.get_attribute("aria-expanded"))
            page.fill("#viewer-search", "entity:control:U1")
            page.locator('[data-aixem-select="entity:control:U1"]').click()
            self.assertTrue(page.locator("#viewer-workspace").evaluate("element => element.classList.contains('inspector-open')"))
            self.assertIn("entity:control:U1", page.locator("#inspector-body").inner_text())
            self.assertTrue(page.locator("#viewer-inspector").is_visible())
            page.locator('[data-aixem-action="close-inspector"]').click()
            self.assertEqual("false", inspector_toggle.get_attribute("aria-expanded"))
            self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
