"""
Generate the "Specification graph" HTML screen: an SVG diagram of the
project's documents and the cross-document relations between them.
"""

import os

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.features.specification_graph.layout import (
    compute_document_layout,
    get_skip_edges,
)
from strictdoc.features.specification_graph.relations import (
    get_document_relation_edges,
)
from strictdoc.features.specification_graph.svg_renderer import render_svg
from strictdoc.features.specification_graph.view_object import (
    SpecificationGraphViewObject,
)


class SpecificationGraphGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> None:
        documents = list(traceability_index.document_tree.document_list)
        edges = get_document_relation_edges(traceability_index)
        layout = compute_document_layout(documents=documents, edges=edges)
        skip_edges = get_skip_edges(edges, layout)

        svg = render_svg(layout=layout, edges=edges, skip_edges=skip_edges)

        view_object = SpecificationGraphViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
            svg_content=svg,
        )
        html = view_object.render_screen(html_templates.jinja_environment())

        output_html = os.path.join(
            project_config.export_output_html_root,
            "specification_graph.html",
        )

        with open(output_html, "w", encoding="utf-8") as file_:
            file_.write(html)
