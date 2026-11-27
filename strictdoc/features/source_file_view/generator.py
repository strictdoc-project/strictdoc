"""
@relation(SDOC-SRS-36, scope=file)

Writes source file pages. The functions in this module serve two use cases:

- Static export: HTMLGenerator.export_source_files_screens() creates the
  view objects of all source files with one SourceFileViewDataCollector and
  renders them through the parallelizer, in worker processes or in the main
  process.
- Server: HTMLGenerator.export_single_source_file_screen() renders one
  source file page on demand, in the server process.

The docstring of each function names its use case.
"""

import time
from pathlib import Path
from typing import Tuple

from markupsafe import Markup

from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.features.source_file_view.view_data import (
    SourceFileViewDataCollector,
)
from strictdoc.features.source_file_view.view_object import (
    SourceFileViewObject,
)
from strictdoc.helpers.timing import measure_performance


class SourceFileViewHTMLGenerator:
    @staticmethod
    def export_to_file(
        *,
        project_config: ProjectConfig,
        source_file: SourceFile,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> None:
        """
        Use case: server.

        Create the view object of one source file and write its page.
        """
        document_content = SourceFileViewHTMLGenerator.export(
            project_config=project_config,
            source_file=source_file,
            traceability_index=traceability_index,
            html_templates=html_templates,
        )
        SourceFileViewHTMLGenerator._write_to_file(
            source_file, document_content
        )

    @staticmethod
    def export_to_file_with_performance(
        *,
        project_config: ProjectConfig,
        source_file: SourceFile,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> None:
        """
        Use case: server.

        Write the page of one source file on demand, unless the page is up to
        date. The static export does not use this method: it renders through
        the parallelizer and reports progress for all source files through a
        single measure_performance_loop().
        """
        if not traceability_index.file_dependency_manager.must_generate(
            source_file.output_file_full_path
        ):
            with measure_performance(
                f"Skip: {source_file.in_doctree_source_file_rel_path}"
            ):
                return

        with measure_performance(
            f"File: {source_file.in_doctree_source_file_rel_path}"
        ):
            SourceFileViewHTMLGenerator.export_to_file(
                project_config=project_config,
                source_file=source_file,
                traceability_index=traceability_index,
                html_templates=html_templates,
            )

    @staticmethod
    def export(
        *,
        project_config: ProjectConfig,
        source_file: SourceFile,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> Markup:
        """
        Use case: server.

        Create the view object of one source file with its own
        SourceFileViewDataCollector and render it in this process. The static
        export creates all view objects with one shared collector instead.
        """
        data_collector = SourceFileViewDataCollector(
            traceability_index=traceability_index,
            project_config=project_config,
            html_templates=html_templates,
        )
        view_object = SourceFileViewObject.create(
            source_file=source_file, data_collector=data_collector
        )
        return view_object.render_screen(html_templates.jinja_environment())

    @staticmethod
    def export_view_object_to_file(
        *,
        view_object: SourceFileViewObject,
        html_templates: HTMLTemplates,
    ) -> None:
        """
        Use case: static export.

        Render a view object and write its page.
        export_source_file_view_object_worker() calls this method in a worker
        process or in the main process.
        """
        document_content = view_object.render_screen(
            html_templates.jinja_environment()
        )
        SourceFileViewHTMLGenerator._write_to_file(
            view_object.source_file, document_content
        )

    @staticmethod
    def _write_to_file(source_file: SourceFile, document_content: str) -> None:
        """
        Use cases: static export and server.
        """
        Path(source_file.output_dir_full_path).mkdir(
            parents=True, exist_ok=True
        )
        with open(
            source_file.output_file_full_path, "w", encoding="utf-8"
        ) as file:
            file.write(document_content)


def export_source_file_view_object_worker(
    task: Tuple[HTMLTemplates, SourceFileViewObject],
) -> Tuple[str, float]:
    """
    Use case: static export.

    Module-level task function for the parallelizer: render one source file
    page and write it to disk. The task holds the HTMLTemplates of the main
    process and the view object. Neither holds the traceability index, and
    the HTMLTemplates object is sent as a small reference (see
    HTMLTemplates).

    Returns the path of the source file and the time it took, so that the
    main process can report progress.
    """
    html_templates, view_object = task
    time_start = time.time()
    SourceFileViewHTMLGenerator.export_view_object_to_file(
        view_object=view_object, html_templates=html_templates
    )
    return (
        view_object.source_file.in_doctree_source_file_rel_path,
        time.time() - time_start,
    )
