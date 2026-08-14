"""AIXEM Reference Viewer 1 HTML renderer."""
from __future__ import annotations

from typing import Any

from .core import jinja_environment, prepare_template_context


class ReferenceViewerRenderer:
    """Render the strict read-only Reference Viewer product profile."""

    def render(
        self,
        model: dict[str, Any],
        *,
        sheet_svgs: dict[str, str],
        overview_svg: str | None = None,
        composite_svg: str | None = None,
    ) -> str:
        environment = jinja_environment()
        template = environment.get_template("reference-viewer.html.j2")
        context = prepare_template_context(
            model,
            sheet_svgs=sheet_svgs,
            overview_svg=overview_svg,
            composite_svg=composite_svg,
            profile="reference-viewer",
        )
        return template.render(**context)
