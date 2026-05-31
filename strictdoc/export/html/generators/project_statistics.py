from strictdoc.features.project_statistics.generator import (
    ProgressStatisticsGenerator,
)
from strictdoc.helpers.deprecation_engine import DEPRECATION_ENGINE

DEPRECATION_ENGINE.add_message(
    "strictdoc.export.html.generators.project_statistics",
    (
        "WARNING: Importing project statistics generator from "
        "'strictdoc.export.html.generators.project_statistics' is deprecated. "
        "Use 'strictdoc.features.project_statistics.generator' instead."
    ),
)

__all__ = ("ProgressStatisticsGenerator",)
