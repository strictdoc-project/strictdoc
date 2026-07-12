import importlib
import os
import sys

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.project_statistics.generator import (
    ProgressStatisticsGenerator,
)
from strictdoc.helpers.exception import StrictDocException


def render_project_statistics_screen(
    project_config: ProjectConfig,
    traceability_index: TraceabilityIndex,
    html_templates: HTMLTemplates,
) -> None:
    """
    Export project statistics to a dedicated HTML page.

    @relation(SDOC-SRS-97, scope=function)
    @relation(SDOC-SRS-154, scope=function)
    """

    link_renderer = LinkRenderer(
        root_path="",
        static_path=project_config.dir_for_sdoc_assets,
    )

    statistics_generator = ProgressStatisticsGenerator

    if (
        custom_statistics_generator_path := project_config.statistics_generator
    ) is not None:
        # It is important to add the input folder to the import path.
        # Otherwise, the custom statistics generator may not be found.
        # In fact, a more reasonable path to add would be the project config
        # path, but since it is not maintained by ProjectConfig yet and
        # usually equals the input path, add the input path for
        # now.
        input_paths = project_config.input_paths
        assert input_paths is not None and len(input_paths) > 0, (
            "Expected a valid input path."
        )
        sys.path.insert(0, input_paths[0])

        module_path, class_name = custom_statistics_generator_path.rsplit(
            ".", 1
        )
        try:
            module = importlib.import_module(module_path)
            statistics_generator = getattr(module, class_name)
        except ModuleNotFoundError as module_not_found_error_:
            raise StrictDocException(
                "Could not import a user-provided statistics generator: "
                f"{module_not_found_error_}."
            ) from module_not_found_error_

    document_content = statistics_generator.export(
        project_config,
        traceability_index,
        link_renderer,
        html_templates=html_templates,
    )
    output_html_source_coverage = os.path.join(
        project_config.export_output_html_root,
        "project_statistics.html",
    )
    with open(output_html_source_coverage, "w", encoding="utf8") as file:
        file.write(document_content)
