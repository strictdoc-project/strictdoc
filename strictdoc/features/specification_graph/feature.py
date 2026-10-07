from strictdoc.core.feature import Feature, FeatureContext
from strictdoc.features.specification_graph.background import (
    NODES_VIEW_BUILDER,
)
from strictdoc.features.specification_graph.screen import (
    render_specification_graph_screen,
)


class SpecificationGraphFeature(Feature):
    HANDLE = "SPECIFICATION_GRAPH_SCREEN"

    @staticmethod
    def supports_export() -> bool:
        return True

    def export(self, context: FeatureContext) -> None:
        render_specification_graph_screen(
            project_config=context.project_config,
            traceability_index=context.traceability_index,
            html_templates=context.html_templates,
        )

    @staticmethod
    def supports_server() -> bool:
        return True

    def on_server_start(self, context: FeatureContext) -> None:
        NODES_VIEW_BUILDER.start(
            project_config=context.project_config,
            traceability_index=context.traceability_index,
            html_templates=context.html_templates,
        )

    def screen_filename(self) -> str:
        return "specification_graph.html"

    def render_screen(self, context: FeatureContext) -> None:
        render_specification_graph_screen(
            project_config=context.project_config,
            traceability_index=context.traceability_index,
            html_templates=context.html_templates,
        )

    def screen_icon(self) -> str:
        return "features/specification_graph/ico16_graph.svg"
