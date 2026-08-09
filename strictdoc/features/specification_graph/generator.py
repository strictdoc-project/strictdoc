"""
Generate the "Specification graph" HTML screen: an SVG diagram of the
project's documents and the cross-document relations between them.
"""

import os

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.features.specification_graph.view_object import (
    SpecificationGraphViewObject,
)

# Step 1 placeholder: hardcoded SVG proving the screen plumbing (nav ->
# export -> screen) works end to end. Real relation extraction and the
# "highway" layered layout land in follow-up commits (see task.md).
PLACEHOLDER_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 140" \
width="320" height="140" role="img" aria-label="Specification graph placeholder">
  <defs>
    <marker id="specification_graph_arrow" markerWidth="10" markerHeight="10" \
refX="8" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" />
    </marker>
  </defs>
  <rect x="10" y="10" width="140" height="40" fill="none" stroke="black" />
  <text x="80" y="35" text-anchor="middle">Document A</text>
  <rect x="10" y="90" width="140" height="40" fill="none" stroke="black" />
  <text x="80" y="115" text-anchor="middle">Document B</text>
  <line x1="80" y1="90" x2="80" y2="52" stroke="black" \
marker-end="url(#specification_graph_arrow)" />
</svg>
"""


class SpecificationGraphGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> None:
        view_object = SpecificationGraphViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
            svg_content=PLACEHOLDER_SVG,
        )
        html = view_object.render_screen(html_templates.jinja_environment())

        output_html = os.path.join(
            project_config.export_output_html_root,
            "specification_graph.html",
        )

        with open(output_html, "w", encoding="utf-8") as file_:
            file_.write(html)
