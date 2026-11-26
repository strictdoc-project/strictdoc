from strictdoc.core.feature import Feature, FeatureContext

# The methods below import the screen code on first use, so that a project
# without this feature does not load it.


class ProjectStatisticsFeature(Feature):
    HANDLE = "PROJECT_STATISTICS_SCREEN"

    @staticmethod
    def supports_export() -> bool:
        return True

    def export(self, context: FeatureContext) -> None:
        from strictdoc.features.project_statistics.screen import (  # noqa: PLC0415
            render_project_statistics_screen,
        )

        render_project_statistics_screen(
            context.project_config,
            context.traceability_index,
            context.html_templates,
        )

    @staticmethod
    def supports_server() -> bool:
        return True

    def screen_filename(self) -> str:
        return "project_statistics.html"

    def render_screen(self, context: FeatureContext) -> None:
        from strictdoc.features.project_statistics.screen import (  # noqa: PLC0415
            render_project_statistics_screen,
        )

        render_project_statistics_screen(
            context.project_config,
            context.traceability_index,
            context.html_templates,
        )

    def screen_icon(self) -> str:
        return "features/project_statistics/ico16_stat.svg"
