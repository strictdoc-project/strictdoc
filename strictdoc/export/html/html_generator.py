import os
from enum import Enum
from functools import partial
from pathlib import Path

from strictdoc.backend.source_file_syntax.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import DocumentTree, FileTree
from strictdoc.core.finders.source_files_finder import (
    SourceFilesFinder,
    SourceFile,
)
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
        formats_string,
        document_tree: DocumentTree,
        traceability_index,
        output_html_root,
        strictdoc_src_path,
        strictdoc_last_update,
        asset_dirs,
        parallelizer,
    ):
        if "html" in formats_string:
            if "html-standalone" in formats_string:
                export_mode = ExportMode.DOCTREE_AND_STANDALONE
            else:
                export_mode = ExportMode.DOCTREE
        else:
            if "html-standalone" in formats_string:
                export_mode = ExportMode.STANDALONE
            else:
                raise NotImplementedError

        export_options = ExportOptions(
            export_mode, strictdoc_src_path, strictdoc_last_update
        )
        link_renderer = LinkRenderer(output_html_root)

        writer = DocumentTreeHTMLGenerator()
        output = writer.export(document_tree)

        output_html_static_files = "{}/_static".format(output_html_root)
        output_file = "{}/index.html".format(output_html_root)

        with open(output_file, "w") as file:
            file.write(output)

        static_files_src = os.path.join(
            strictdoc_src_path, "strictdoc/export/html/_static"
        )
        sync_dir(static_files_src, output_html_static_files)
        for asset_dir in asset_dirs:
            source_path = asset_dir["full_path"]
            output_relative_path = asset_dir["relative_path"]
            destination_path = os.path.join(
                output_html_root, output_relative_path
            )
            sync_dir(source_path, destination_path)

        export_binding = partial(
            HTMLGenerator._export_with_performance,
            export_options=export_options,
            document_tree=document_tree,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
        )

        parallelizer.map(document_tree.document_list, export_binding)

        if document_tree.source_files:
            print("Generating source files")
            for source_file in document_tree.source_files:
                Path(source_file.output_path_dir_full_path).mkdir(
                    parents=True, exist_ok=True
                )
                document_content = SourceFileViewHTMLGenerator.export(
                    source_file,
                    document_tree,
                    traceability_index,
                    link_renderer,
                )
                with open(source_file.output_path_file_full_path, "w") as file:
                    file.write(document_content)

        print(
            "Export completed. Documentation tree can be found at:\n{}".format(
                output_html_root
            )
        )

    @staticmethod
    def _export_with_performance(
        document,
        export_options: ExportOptions,
        document_tree,
        traceability_index,
        link_renderer,
    ):
        document_meta: DocumentMeta = document.meta
        full_output_path = os.path.join(
            export_options.strictdoc_src_path, document_meta.get_html_doc_path()
        )

        # If file exists we want to check its modification path in order to skip
        # its generation in case it has not changed since the last generation.
        if os.path.isfile(full_output_path):
            output_file_mtime = get_file_modification_time(full_output_path)
            sdoc_mtime = get_file_modification_time(
                document_meta.input_doc_full_path
            )

            if (
                sdoc_mtime < output_file_mtime
                and export_options.strictdoc_last_update < output_file_mtime
            ):
                with measure_performance("Skip: {}".format(document.name)):
                    return

        with measure_performance("Published: {}".format(document.name)):
            HTMLGenerator._export(
                export_options.export_mode,
                document,
                document_tree,
                traceability_index,
                link_renderer,
            )
        return None

    @staticmethod
    def _export(
        export_mode,
        document,
        document_tree,
        traceability_index,
        link_renderer,
    ):
        document_meta: DocumentMeta = document.meta

        document_output_folder = document_meta.output_document_dir_full_path
        Path(document_output_folder).mkdir(parents=True, exist_ok=True)

        if (
            export_mode == ExportMode.DOCTREE
            or export_mode == ExportMode.DOCTREE_AND_STANDALONE
        ):
            # Single Document pages
            document_content = DocumentHTMLGenerator.export(
                document_tree,
                document,
                traceability_index,
                link_renderer,
            )

            document_out_file = document_meta.get_html_doc_path()
            with open(document_out_file, "w") as file:
                file.write(document_content)

            # Single Document Table pages
            document_content = DocumentTableHTMLGenerator.export(
                document, traceability_index, link_renderer
            )
            document_out_file = document_meta.get_html_table_path()

            with open(document_out_file, "w") as file:
                file.write(document_content)

            # Single Document Traceability pages
            document_content = DocumentTraceHTMLGenerator.export(
                document, traceability_index, link_renderer
            )
            document_out_file = document_meta.get_html_traceability_path()

            with open(document_out_file, "w") as file:
                file.write(document_content)

            # Single Document Deep Traceability pages
            document_content = DocumentDeepTraceHTMLGenerator.export_deep(
                document, traceability_index, link_renderer
            )
            document_out_file = document_meta.get_html_deep_traceability_path()

            with open(document_out_file, "w") as file:
                file.write(document_content)

        if (
            export_mode == ExportMode.STANDALONE
            or export_mode == ExportMode.DOCTREE_AND_STANDALONE
        ):
            # Single Document pages (standalone)
            document_content = DocumentHTMLGenerator.export(
                document_tree,
                document,
                traceability_index,
                link_renderer,
                standalone=True,
            )

            document_out_file = document_meta.get_html_doc_standalone_path()
            document_content_with_embedded_assets = HTMLEmbedder.embed_assets(
                document_content, document_out_file
            )
            with open(document_out_file, "w") as file:
                file.write(document_content_with_embedded_assets)

        return document
