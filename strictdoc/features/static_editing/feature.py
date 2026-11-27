"""
@relation(SDOC-SRS-214, scope=file)
"""

from strictdoc.core.feature import Feature, FeatureContext

# The methods below import the export code on first use, so that a project
# without this feature does not load it.


class StaticEditingFeature(Feature):
    HANDLE = "STATIC_EDITING"

    @staticmethod
    def supports_export() -> bool:
        return True

    def export(self, context: FeatureContext) -> None:
        from strictdoc.features.static_editing.edit_data_exporter import (  # noqa: PLC0415
            export_static_editing_data,
        )

        export_static_editing_data(context.traceability_index)

    @staticmethod
    def supports_server() -> bool:
        return False
