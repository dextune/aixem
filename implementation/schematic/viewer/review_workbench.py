"""AIXEM Review Workbench 1 HTML renderer."""
from __future__ import annotations

from typing import Any

from .core import jinja_environment, prepare_template_context


class ReviewWorkbenchRenderer:
    """Render the read-only engineering-review extension of Viewer Core 1."""

    def render(
        self,
        model: dict[str, Any],
        *,
        sheet_svgs: dict[str, str],
        overview_svg: str | None = None,
        composite_svg: str | None = None,
    ) -> str:
        environment = jinja_environment()
        template = environment.get_template("review-workbench.html.j2")
        context = prepare_template_context(
            model,
            sheet_svgs=sheet_svgs,
            overview_svg=overview_svg,
            composite_svg=composite_svg,
            profile="review-workbench",
        )
        return template.render(**context)
