"""
@relation(SDOC-SRS-35, scope=file)
"""

from markupsafe import Markup

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.features.source_coverage.view_object import (
    SourceCoverageViewObject,
)


class SourceFileCoverageHTMLGenerator:
    @staticmethod
    def export(
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> Markup:
        view_object = SourceCoverageViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
        )
        return view_object.render_screen(html_templates.jinja_environment())
