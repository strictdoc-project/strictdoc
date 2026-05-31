from strictdoc.features.project_statistics.view_object import (
    ProjectStatisticsViewObject,
)
from strictdoc.helpers.deprecation_engine import DEPRECATION_ENGINE

DEPRECATION_ENGINE.add_message(
    "strictdoc.export.html.generators.view_objects.project_statistics_view_object",
    (
        "WARNING: Importing ProjectStatisticsViewObject from "
        "'strictdoc.export.html.generators.view_objects."
        "project_statistics_view_object' is deprecated. Use "
        "'strictdoc.features.project_statistics.view_object' instead."
    ),
)

__all__ = ("ProjectStatisticsViewObject",)
