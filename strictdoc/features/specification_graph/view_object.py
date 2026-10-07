"""
Provide the specification graph views to the feature template.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.specification_graph.svg_graph.render import (
    RenderedGraph,
)

# Constant styles of the generated SVG. They belong to the generator, the
# screen embeds them in the page.
GRAPH_CSS_PATH = Path(__file__).parent / "svg_graph" / "specification_graph.css"


@dataclass(frozen=True)
class SpecificationGraphView:
    view_id: str
    label: str
    rendered_graph: Optional[RenderedGraph] = None
    error: Optional[str] = None
    # A view that the server builds in the background: the version of the
    # traceability index it is built for and the URL of its data.
    pending_version: Optional[str] = None
    pending_url: Optional[str] = None

    @property
    def svg(self) -> Markup:
        assert self.rendered_graph is not None
        return Markup(self.rendered_graph.svg)


class SpecificationGraphViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        link_renderer: LinkRenderer,
        views: List[SpecificationGraphView],
    ) -> None:
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.views: List[SpecificationGraphView] = views
        self.graph_style: Markup = Markup(
            "<style>" + GRAPH_CSS_PATH.read_text(encoding="utf8") + "</style>"
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version: str = __version__

    def get_document_level(self) -> int:
        return 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "features/specification_graph/index.jinja",
            view_object=self,
        )

    def render_static_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url(url))

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))
