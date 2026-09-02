from strictdoc.core.feature import Feature, FeatureContext
from strictdoc.features.eurobot_test_dashboard.screen import (
    render_eurobot_test_dashboard_screen,
)


class EurobotTestDashboardFeature(Feature):
    HANDLE = "EUROBOT_TEST_DASHBOARD"

    @staticmethod
    def supports_export() -> bool:
        return True

    def export(self, context: FeatureContext) -> None:
        render_eurobot_test_dashboard_screen(
            context.project_config,
            context.traceability_index,
            context.html_templates,
        )

    @staticmethod
    def supports_server() -> bool:
        return True

    def screen_filename(self) -> str:
        return "eurobot_test_dashboard.html"

    def render_screen(self, context: FeatureContext) -> None:
        render_eurobot_test_dashboard_screen(
            context.project_config,
            context.traceability_index,
            context.html_templates,
        )

    def screen_icon(self) -> str:
        return "features/eurobot_test_dashboard/ico16_dashboard.svg"
