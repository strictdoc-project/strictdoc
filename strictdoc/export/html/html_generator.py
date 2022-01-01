import os
from enum import Enum
from functools import partial
from pathlib import Path

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.source_tree import SourceTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.document import DocumentHTMLGenerator
from strictdoc.export.html.generators.document_deep_trace import (
    DocumentDeepTraceHTMLGenerator,
)
from strictdoc.export.html.generators.document_table import (
    DocumentTableHTMLGenerator,
)
from strictdoc.export.html.generators.document_trace import (
    DocumentTraceHTMLGenerator,
)
from strictdoc.export.html.generators.document_tree import (
    DocumentTreeHTMLGenerator,
)
from strictdoc.export.html.generators.requirements_coverage import (
    RequirementsCoverageHTMLGenerator,
)
from strictdoc.export.html.generators.source_file_coverage import (
    SourceFileCoverageHTMLGenerator,
)
from strictdoc.export.html.generators.source_file_view_generator import (
    SourceFileViewHTMLGenerator,
)
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.html.tools.html_embedded import HTMLEmbedder
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.file_system import sync_dir
from strictdoc.helpers.timing import measure_performance


class ExportOptions:
    def __init__(self, export_mode, strictdoc_src_path, strictdoc_last_update):
        self.export_mode = export_mode
        self.strictdoc_src_path = strictdoc_src_path
        self.strictdoc_last_update = strictdoc_last_update


class ExportMode(Enum):
    DOCTREE = 1
    STANDALONE = 2
    DOCTREE_AND_STANDALONE = 3


class HTMLGenerator:
    @staticmethod
    def export_tree(
        config: ExportCommandConfig,
        document_tree: DocumentTree,
        traceability_index: TraceabilityIndex,
        output_html_root,
        strictdoc_last_update,
        asset_dirs,
        parallelizer,
    ):  # pylint: disable=too-many-arguments,too-many-statements
        if "html" in config.formats:
            if "html-standalone" in config.formats:
                export_mode = ExportMode.DOCTREE_AND_STANDALONE
            else:
                export_mode = ExportMode.DOCTREE
        else:
            if "html-standalone" in config.formats:
                export_mode = ExportMode.STANDALONE
            else:
                raise NotImplementedError

        export_options = ExportOptions(
            export_mode, config.strictdoc_root_path, strictdoc_last_update
        )
        link_renderer = LinkRenderer(output_html_root)

        writer = DocumentTreeHTMLGenerator()
        output = writer.export(config, document_tree, traceability_index)

        output_html_static_files = os.path.join(output_html_root, "_static")
        output_file = os.path.join(output_html_root, "index.html")

        with open(output_file, "w", encoding="utf8") as file:
            file.write(output)

        static_files_src = os.path.join(
            config.strictdoc_root_path, "strictdoc/export/html/_static"
        )
        sync_dir(static_files_src, output_html_static_files)

        if config.enable_mathjax:
            output_html_mathjax = os.path.join(
                output_html_root, "_static", "mathjax"
            )
            Path(output_html_mathjax).mkdir(parents=True, exist_ok=True)
            mathjax_src = os.path.join(
                config.strictdoc_root_path,
                "strictdoc/export/html/_static_extra/mathjax",
            )
            sync_dir(mathjax_src, output_html_mathjax)

        for asset_dir in asset_dirs:
            source_path = asset_dir["full_path"]
            output_relative_path = asset_dir["relative_path"]
            destination_path = os.path.join(
                output_html_root, output_relative_path
            )
            sync_dir(source_path, destination_path)

        document: Document
        for document in document_tree.document_list:
            # If a document file exists we want to check its modification path
            # in order to skip its generation in case it has not changed since
            # the last generation. We also check the Traceability Index for the
            # document's dependencies to see if they must be regenerated as
            # well.
            document_meta: DocumentMeta = document.meta
            full_output_path = os.path.join(
                export_options.strictdoc_src_path,
                document_meta.get_html_doc_path(),
            )
            if not os.path.isfile(full_output_path):
                document.ng_needs_generation = True
            else:
                output_file_mtime = get_file_modification_time(full_output_path)
                sdoc_mtime = get_file_modification_time(
                    document_meta.input_doc_full_path
                )
                if not (
                    sdoc_mtime < output_file_mtime
                    and export_options.strictdoc_last_update < output_file_mtime
                ):
                    document.ng_needs_generation = True
            if document.ng_needs_generation:
                todo_list = [document]
                finished = set()
                while todo_list:
                    document = todo_list.pop()
                    if document in finished:
                        continue
                    document.ng_needs_generation = True
                    document_parents = traceability_index.get_document_parents(
                        document
                    )
                    document_children = (
                        traceability_index.get_document_children(document)
                    )
                    todo_list.extend(document_parents)
                    todo_list.extend(document_children)
                    finished.add(document)

        export_binding = partial(
            HTMLGenerator._export_with_performance,
            config,
            export_options=export_options,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
        )

        parallelizer.map(document_tree.document_list, export_binding)

        requirements_coverage_content = (
            RequirementsCoverageHTMLGenerator.export(
                config,
                document_tree,
                traceability_index,
                link_renderer,
            )
        )
        output_html_requirements_coverage = os.path.join(
            output_html_root, "requirements_coverage.html"
        )
        with open(
            output_html_requirements_coverage, "w", encoding="utf8"
        ) as file:
            file.write(requirements_coverage_content)

        if config.experimental_enable_file_traceability:
            assert isinstance(document_tree.source_tree, SourceTree)
            print("Generating source files:")
            for source_file in document_tree.source_tree.source_files:
                if not source_file.is_referenced:
                    continue

                with measure_performance(
                    f"File: {source_file.in_doctree_source_file_rel_path}"
                ):
                    Path(source_file.output_dir_full_path).mkdir(
                        parents=True, exist_ok=True
                    )
                    document_content = SourceFileViewHTMLGenerator.export(
                        source_file,
                        traceability_index,
                        link_renderer,
                    )
                    with open(
                        source_file.output_file_full_path, "w", encoding="utf-8"
                    ) as file:
                        file.write(document_content)

            source_coverage_content = SourceFileCoverageHTMLGenerator.export(
                config=config,
                document_tree=document_tree,
                traceability_index=traceability_index,
                link_renderer=link_renderer,
            )
            output_html_source_coverage = os.path.join(
                output_html_root, "source_coverage.html"
            )
            with open(
                output_html_source_coverage, "w", encoding="utf8"
            ) as file:
                file.write(source_coverage_content)

        print(
            "Export completed. Documentation tree can be found at:\n"
            f"{output_html_root}"
        )

    @staticmethod
    def _export_with_performance(
        config: ExportCommandConfig,
        document,
        export_options: ExportOptions,
        traceability_index,
        link_renderer,
    ):
        if not document.ng_needs_generation:
            with measure_performance(f"Skip: {document.name}"):
                return
        with measure_performance(f"Published: {document.name}"):
            HTMLGenerator._export(
                config,
                export_options.export_mode,
                document,
                traceability_index,
                link_renderer,
            )
        return

    @staticmethod
    def _export(
        config: ExportCommandConfig,
        export_mode,
        document,
        traceability_index,
        link_renderer,
    ):
        document_meta: DocumentMeta = document.meta

        document_output_folder = document_meta.output_document_dir_full_path
        Path(document_output_folder).mkdir(parents=True, exist_ok=True)

        markup_renderer = MarkupRenderer.create(
            document.config.markup,
            traceability_index,
            link_renderer,
            document,
        )

        if export_mode in (
            ExportMode.DOCTREE,
            ExportMode.DOCTREE_AND_STANDALONE,
        ):
            # Single Document pages
            document_content = DocumentHTMLGenerator.export(
                config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                standalone=False,
            )
            document_out_file = document_meta.get_html_doc_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

            # Single Document Table pages
            document_content = DocumentTableHTMLGenerator.export(
                config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
            )
            document_out_file = document_meta.get_html_table_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

            # Single Document Traceability pages
            document_content = DocumentTraceHTMLGenerator.export(
                config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
            )
            document_out_file = document_meta.get_html_traceability_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

            # Single Document Deep Traceability pages
            document_content = DocumentDeepTraceHTMLGenerator.export_deep(
                config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
            )
            document_out_file = document_meta.get_html_deep_traceability_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        if export_mode in (
            ExportMode.STANDALONE,
            ExportMode.DOCTREE_AND_STANDALONE,
        ):
            # Single Document pages (standalone)
            document_content = DocumentHTMLGenerator.export(
                config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                standalone=True,
            )
            document_out_file = document_meta.get_html_doc_standalone_path()
            document_content_with_embedded_assets = HTMLEmbedder.embed_assets(
                document_content, document_out_file
            )
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content_with_embedded_assets)

        return document
