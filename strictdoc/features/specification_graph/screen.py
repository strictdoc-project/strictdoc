"""
Render the specification graph screen.
"""

import os
from typing import Callable, List

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.specification_graph.relations import (
    build_documents_graph,
    build_nodes_graph,
)
from strictdoc.features.specification_graph.svg_graph.model import Graph
from strictdoc.features.specification_graph.svg_graph.normalization import (
    GraphModelError,
)
from strictdoc.features.specification_graph.svg_graph.render import (
    render_graph,
)
from strictdoc.features.specification_graph.view_object import (
    SpecificationGraphView,
    SpecificationGraphViewObject,
)

SCREEN_FILENAME = "specification_graph.html"


def render_specification_graph_screen(
    *,
    project_config: ProjectConfig,
    traceability_index: TraceabilityIndex,
    html_templates: HTMLTemplates,
) -> None:
    link_renderer = LinkRenderer(
        root_path="",
        static_path=project_config.dir_for_sdoc_assets,
    )
    views: List[SpecificationGraphView] = [
        _render_view(
            view_id="documents",
            label="Documents",
            build_graph=lambda: build_documents_graph(
                traceability_index, link_renderer
            ),
        ),
        _render_view(
            view_id="nodes",
            label="Nodes",
            build_graph=lambda: build_nodes_graph(
                traceability_index, link_renderer
            ),
        ),
    ]
    view_object = SpecificationGraphViewObject(
        traceability_index=traceability_index,
        project_config=project_config,
        link_renderer=link_renderer,
        views=views,
    )
    document_content = view_object.render_screen(
        html_templates.jinja_environment()
    )
    output_path = os.path.join(
        project_config.export_output_html_root, SCREEN_FILENAME
    )
    with open(output_path, "w", encoding="utf8") as output_file:
        output_file.write(document_content)


def _render_view(
    *, view_id: str, label: str, build_graph: Callable[[], Graph]
) -> SpecificationGraphView:
    """
    Render one view. An invalid graph model gives a view with the error
    text instead of the graph, so that the rest of the export continues.
    """

    try:
        rendered_graph = render_graph(
            build_graph(), svg_id=f"specification-graph-{view_id}", debug=True
        )
    except GraphModelError as exception_:
        print(  # noqa: T201
            f"error: Specification graph, view {label}: {exception_}"
        )
        return SpecificationGraphView(
            view_id=view_id, label=label, error=str(exception_)
        )
    return SpecificationGraphView(
        view_id=view_id, label=label, rendered_graph=rendered_graph
    )
