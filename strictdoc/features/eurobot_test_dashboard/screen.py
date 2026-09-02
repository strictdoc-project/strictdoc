import os

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.eurobot_test_dashboard.generator import (
    EurobotTestDashboardGenerator,
)


def render_eurobot_test_dashboard_screen(
    project_config: ProjectConfig,
    traceability_index: TraceabilityIndex,
    html_templates: HTMLTemplates,
) -> None:
    """
    Export the Eurobot test execution dashboard to a dedicated HTML page.

    @relation(SDOC-SRS-97, scope=function)
    """

    link_renderer = LinkRenderer(
        root_path="",
        static_path=project_config.dir_for_sdoc_assets,
    )

    document_content = EurobotTestDashboardGenerator.export(
        project_config,
        traceability_index,
        link_renderer,
        html_templates=html_templates,
    )
    output_path = os.path.join(
        project_config.export_output_html_root,
        "eurobot_test_dashboard.html",
    )
    with open(output_path, "w", encoding="utf8") as file:
        file.write(document_content)
