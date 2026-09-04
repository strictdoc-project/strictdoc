"""
Render the tree map screen.

@relation(SDOC-SRS-157, scope=file)
"""

import os

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.tree_map.data_generator import (
    TreeMapDataGenerator,
)
from strictdoc.features.tree_map.view_object import TreeMapViewObject


def render_tree_map_screen(
    *,
    project_config: ProjectConfig,
    traceability_index: TraceabilityIndex,
    html_templates: HTMLTemplates,
) -> None:
    tree_map_data = TreeMapDataGenerator.generate(
        project_config=project_config,
        traceability_index=traceability_index,
    )
    link_renderer = LinkRenderer(
        root_path="",
        static_path=project_config.dir_for_sdoc_assets,
    )
    view_object = TreeMapViewObject(
        traceability_index=traceability_index,
        project_config=project_config,
        link_renderer=link_renderer,
        tree_map_data=tree_map_data,
    )
    document_content = view_object.render_screen(
        html_templates.jinja_environment()
    )
    output_path = os.path.join(
        project_config.export_output_html_root,
        "tree_map.html",
    )
    with open(output_path, "w", encoding="utf8") as output_file:
        output_file.write(document_content)
