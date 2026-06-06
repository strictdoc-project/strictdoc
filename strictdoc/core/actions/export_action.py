from strictdoc.features.export.export_action import ExportAction
from strictdoc.helpers.deprecation_engine import DEPRECATION_ENGINE

DEPRECATION_ENGINE.add_message(
    "strictdoc.core.actions.export_action",
    (
        "WARNING: Importing export action from "
        "'strictdoc.core.actions.export_action' is deprecated. "
        "Use 'strictdoc.features.export.export_action' instead."
    ),
)

__all__ = ("ExportAction",)
