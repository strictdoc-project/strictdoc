import os
from functools import partial
from pathlib import Path
from typing import Optional, Tuple

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.project_config import ProjectConfig, ProjectFeature
from strictdoc.core.source_tree import SourceTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.document import DocumentHTMLGenerator
from strictdoc.export.html.generators.document_deep_trace import (
    DocumentDeepTraceHTMLGenerator,
)
from strictdoc.export.html.generators.document_pdf import (
    DocumentHTML2PDFGenerator,
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
from strictdoc.export.html.generators.project_statistics import (
    ProgressStatisticsGenerator,
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
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.html.tools.html_embedded import HTMLEmbedder
from strictdoc.helpers.file_system import sync_dir
from strictdoc.helpers.timing import measure_performance


class HTMLGenerator:
    def __init__(
        self, project_config: ProjectConfig, html_templates: HTMLTemplates
    ):
        self.project_config: ProjectConfig = project_config
        self.html_templates = html_templates

    def export_complete_tree(
        self,
        *,
        traceability_index: TraceabilityIndex,
        parallelizer,
    ):  # pylint: disable=too-many-arguments,too-many-statements
        Path(self.project_config.export_output_html_root).mkdir(
            parents=True, exist_ok=True
        )

        # Export assets.
        self.export_assets(
            traceability_index=traceability_index,
        )

        # Export all documents in parallel.
        export_binding = partial(
            self.export_single_document_with_performance,
            traceability_index=traceability_index,
        )

        parallelizer.map(
            traceability_index.document_tree.document_list, export_binding
        )

        # Export document tree.
        # FIXME: It is important that this export is **after** the parallelized
        # export of single documents. It turns out that Jinja does not play
        # well with the multiprocessing's processed-based parallelization.
        # _pickle.PicklingError: Can't pickle <function sync_do_first at 0x1077bdf80>: it's not the same object as jinja2.filters.sync_do_first
        self.export_project_tree_screen(traceability_index=traceability_index)

        # Export project statistics.
        if self.project_config.is_feature_activated(
            ProjectFeature.PROJECT_STATISTICS_SCREEN
        ):
            self.export_project_statistics(traceability_index)

        # Export requirements coverage.
        if self.project_config.is_feature_activated(
            ProjectFeature.REQUIREMENTS_COVERAGE_SCREEN
        ):
            self.export_requirements_coverage_screen(
                traceability_index=traceability_index,
            )

        # Export source coverage.
        if self.project_config.is_feature_activated(
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
        ):
            self.export_source_coverage_screen(
                traceability_index=traceability_index,
            )

        print(  # noqa: T201
            "Export completed. Documentation tree can be found at:\n"
            f"{self.project_config.export_output_html_root}"
        )

    def export_assets(self, *, traceability_index: TraceabilityIndex):
        # Export StrictDoc's own assets.
        output_html_static_files = os.path.join(
            self.project_config.export_output_html_root,
            self.project_config.dir_for_sdoc_assets,
        )
        sync_dir(
            self.project_config.get_static_files_path(),
            output_html_static_files,
            message="Copying StrictDoc's assets",
        )

        # Export MathJax
        if self.project_config.is_feature_activated(ProjectFeature.MATHJAX):
            output_html_mathjax = os.path.join(
                self.project_config.export_output_html_root,
                self.project_config.dir_for_sdoc_assets,
                "mathjax",
            )
            Path(output_html_mathjax).mkdir(parents=True, exist_ok=True)
            mathjax_src = os.path.join(
                self.project_config.get_extra_static_files_path(), "mathjax"
            )
            sync_dir(
                mathjax_src,
                output_html_mathjax,
                message="Copying MathJax assets",
            )

        # Export Mermaid
        if self.project_config.is_feature_activated(ProjectFeature.MERMAID):
            output_html_mathjax = os.path.join(
                self.project_config.export_output_html_root,
                self.project_config.dir_for_sdoc_assets,
                "mermaid",
            )
            Path(output_html_mathjax).mkdir(parents=True, exist_ok=True)
            mermaid_src = os.path.join(
                self.project_config.get_extra_static_files_path(), "mermaid"
            )
            sync_dir(
                mermaid_src,
                output_html_mathjax,
                message="Copying Mermaid assets",
            )

        # Export project's assets.
        for asset_dir in traceability_index.asset_dirs:
            source_path = asset_dir["full_path"]
            output_relative_path = asset_dir["relative_path"]
            destination_path = os.path.join(
                self.project_config.export_output_html_root,
                output_relative_path,
            )
            sync_dir(
                source_path,
                destination_path,
                message=f'Copying project assets "{output_relative_path}"',
            )

    def export_single_document_with_performance(
        self,
        document,
        traceability_index,
        specific_documents: Optional[Tuple[DocumentType]] = None,
    ):
        if specific_documents is None:
            specific_documents = DocumentType.all()

        if (
            not self.project_config.is_running_on_server
            and not document.ng_needs_generation
        ):
            with measure_performance(f"Skip: {document.title}"):
                return
        with measure_performance(f"Published: {document.title}"):
            self.export_single_document(
                document,
                traceability_index,
                specific_documents=specific_documents,
            )

    def export_single_document(
        self,
        document: Document,
        traceability_index,
        specific_documents: Optional[Tuple[DocumentType]] = None,
    ):
        if specific_documents is None:
            specific_documents = DocumentType.all()

        assert document.meta is not None

        document_meta: DocumentMeta = document.meta

        document_output_folder = document_meta.output_document_dir_full_path
        Path(document_output_folder).mkdir(parents=True, exist_ok=True)

        root_path = document.meta.get_root_path_prefix()
        link_renderer = LinkRenderer(
            root_path=root_path,
            static_path=self.project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            document.config.markup,
            traceability_index,
            link_renderer,
            self.html_templates,
            self.project_config,
            document,
        )

        if DocumentType.DOCUMENT in specific_documents:
            # Single Document pages
            document_content = DocumentHTMLGenerator.export(
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                standalone=False,
                html_templates=self.html_templates,
            )
            document_out_file = document_meta.get_html_doc_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        # Single Document Table pages
        if (
            self.project_config.is_feature_activated(
                ProjectFeature.TABLE_SCREEN
            )
            and DocumentType.TABLE in specific_documents
        ):
            document_content = DocumentTableHTMLGenerator.export(
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                self.html_templates,
            )
            document_out_file = document_meta.get_html_table_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        # Single Document Traceability pages
        if (
            self.project_config.is_feature_activated(
                ProjectFeature.TRACEABILITY_SCREEN
            )
            and DocumentType.TRACE in specific_documents
        ):
            document_content = DocumentTraceHTMLGenerator.export(
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                self.html_templates,
            )
            document_out_file = document_meta.get_html_traceability_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        # Single Document Deep Traceability pages
        if (
            self.project_config.is_feature_activated(
                ProjectFeature.DEEP_TRACEABILITY_SCREEN
            )
            and DocumentType.DEEPTRACE in specific_documents
        ):
            document_content = DocumentDeepTraceHTMLGenerator.export_deep(
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                self.html_templates,
            )
            document_out_file = document_meta.get_html_deep_traceability_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        # Single Document PDF pages
        if (
            self.project_config.is_feature_activated(ProjectFeature.HTML2PDF)
            and DocumentType.PDF in specific_documents
        ):
            document_content = DocumentHTML2PDFGenerator.export(
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                standalone=False,
                html_templates=self.html_templates,
            )
            document_out_file = document_meta.get_html_pdf_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        if self.project_config.is_feature_activated(
            ProjectFeature.STANDALONE_DOCUMENT_SCREEN
        ):
            # Single Document pages (standalone)
            document_content = DocumentHTMLGenerator.export(
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                standalone=True,
                html_templates=self.html_templates,
            )
            document_out_file = document_meta.get_html_doc_standalone_path()
            document_content_with_embedded_assets = HTMLEmbedder.embed_assets(
                document_content, document_out_file
            )
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content_with_embedded_assets)

        return document

    def export_project_tree_screen(
        self,
        *,
        traceability_index: TraceabilityIndex,
    ):
        Path(self.project_config.export_output_html_root).mkdir(
            parents=True, exist_ok=True
        )
        output_file = os.path.join(
            self.project_config.export_output_html_root, "index.html"
        )
        writer = DocumentTreeHTMLGenerator()
        output = writer.export(
            self.project_config,
            traceability_index=traceability_index,
            html_templates=self.html_templates,
        )
        with open(output_file, "w", encoding="utf8") as file:
            file.write(output)

    def export_requirements_coverage_screen(
        self,
        *,
        traceability_index: TraceabilityIndex,
    ):
        requirements_coverage_content = (
            RequirementsCoverageHTMLGenerator.export(
                project_config=self.project_config,
                traceability_index=traceability_index,
                html_templates=self.html_templates,
            )
        )
        output_html_requirements_coverage = os.path.join(
            self.project_config.export_output_html_root,
            "requirements_coverage.html",
        )
        with open(
            output_html_requirements_coverage, "w", encoding="utf8"
        ) as file:
            file.write(requirements_coverage_content)

    def export_source_coverage_screen(
        self,
        *,
        traceability_index: TraceabilityIndex,
    ):
        assert isinstance(
            traceability_index.document_tree.source_tree, SourceTree
        ), traceability_index.document_tree.source_tree
        print("Generating source files:")  # noqa: T201
        for (
            source_file
        ) in traceability_index.document_tree.source_tree.source_files:
            if not source_file.is_referenced:
                continue

            with measure_performance(
                f"File: {source_file.in_doctree_source_file_rel_path}"
            ):
                Path(source_file.output_dir_full_path).mkdir(
                    parents=True, exist_ok=True
                )
                document_content = SourceFileViewHTMLGenerator.export(
                    project_config=self.project_config,
                    source_file=source_file,
                    traceability_index=traceability_index,
                    html_templates=self.html_templates,
                )
                with open(
                    source_file.output_file_full_path, "w", encoding="utf-8"
                ) as file:
                    file.write(document_content)

        source_coverage_content = SourceFileCoverageHTMLGenerator.export(
            project_config=self.project_config,
            traceability_index=traceability_index,
            html_templates=self.html_templates,
        )
        output_html_source_coverage = os.path.join(
            self.project_config.export_output_html_root, "source_coverage.html"
        )
        with open(output_html_source_coverage, "w", encoding="utf8") as file:
            file.write(source_coverage_content)

    def export_project_statistics(
        self,
        traceability_index: TraceabilityIndex,
    ):
        link_renderer = LinkRenderer(
            root_path="",
            static_path=self.project_config.dir_for_sdoc_assets,
        )
        document_content = ProgressStatisticsGenerator.export(
            self.project_config,
            traceability_index,
            link_renderer,
            html_templates=self.html_templates,
        )
        output_html_source_coverage = os.path.join(
            self.project_config.export_output_html_root,
            "project_statistics.html",
        )
        with open(output_html_source_coverage, "w", encoding="utf8") as file:
            file.write(document_content)
