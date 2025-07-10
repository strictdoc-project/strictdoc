"""
@relation(SDOC-SRS-53, scope=file)
"""

from markupsafe import Markup

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.project_tree_view_object import (
    ProjectTreeViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates


class DocumentTreeHTMLGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> Markup:
        assert isinstance(html_templates, HTMLTemplates)

        view_object = ProjectTreeViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
        )
        return view_object.render_screen(html_templates.jinja_environment())
