from typing import List, Union

from markupsafe import Markup

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.statistics.metric import Metric, MetricSection
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.project_statistics_view_object import (
    ProjectStatisticsViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class CustomStatisticsGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
    ) -> Markup:

        #
        # Create all metrics.
        #

        metrics: List[Union[Metric, MetricSection]] = []

        section = MetricSection(name="Custom section", metrics=[])
        metrics.append(section)

        section.metrics.append(
            Metric(name="Custom metric", value="Custom value")
        )

        #
        # Return the final view object.
        #

        view_object = ProjectStatisticsViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            metrics=metrics,
        )
        return view_object.render_screen(html_templates.jinja_environment())
