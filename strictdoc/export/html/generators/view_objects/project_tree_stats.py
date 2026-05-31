from strictdoc.features.project_statistics.models.project_tree_stats import (
    DocumentStats,
    DocumentTreeStats,
)
from strictdoc.helpers.deprecation_engine import DEPRECATION_ENGINE

DEPRECATION_ENGINE.add_message(
    "strictdoc.export.html.generators.view_objects.project_tree_stats",
    (
        "WARNING: Importing project statistics data models from "
        "'strictdoc.export.html.generators.view_objects.project_tree_stats' "
        "is deprecated. Use "
        "'strictdoc.features.project_statistics.models.project_tree_stats' "
        "instead."
    ),
)

__all__ = ("DocumentStats", "DocumentTreeStats")
