import os
import shutil
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import orjson
from html2pdf4doc import PATH_TO_HTML2PDF4DOC_JS

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.asset_manager import AssetDir
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.file_system.source_tree import SourceFile, SourceTree
from strictdoc.core.project_config import ProjectConfig, ProjectFeature
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.document import DocumentHTMLGenerator
from strictdoc.export.html.generators.document_table import (
    DocumentTableHTMLGenerator,
)
from strictdoc.export.html.html_templates import (
    HTMLTemplates,
    NormalHTMLTemplates,
)
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.features.deep_trace.generator import (
    DocumentDeepTraceHTMLGenerator,
)
from strictdoc.features.html2pdf.generator import (
    DocumentHTML2PDFGenerator,
)
from strictdoc.features.project_index.generator import (
    DocumentTreeHTMLGenerator,
)
from strictdoc.features.project_index.project_map_generator import (
    ProjectMapGenerator,
)
from strictdoc.features.source_coverage.generator import (
    SourceFileCoverageHTMLGenerator,
)
from strictdoc.features.source_file_view.generator import (
    SourceFileViewHTMLGenerator,
)
from strictdoc.features.trace.generator import (
    DocumentTraceHTMLGenerator,
)
from strictdoc.features.traceability_matrix.generator import (
    TraceabilityMatrixHTMLGenerator,
)
from strictdoc.features.tree_map.generator import TreeMapGenerator
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.file_system import sync_dir
from strictdoc.helpers.git_client import GitClient
from strictdoc.helpers.mid import MID
from strictdoc.helpers.parallelizer import Parallelizer, get_worker_context
from strictdoc.helpers.paths import (
    SDocRelativePath,
    path_to_posix_path,
    shorten_path,
)
from strictdoc.helpers.timing import (
    measure_performance,
    measure_performance_loop,
    timing_decorator,
)


def render_favicon_svg(
    project_config: ProjectConfig,
    html_templates: HTMLTemplates,  # noqa: ARG001
) -> str:
    # Deliberately not using html_templates.jinja_environment(): for large
    # projects it is a CompiledHTMLTemplates instance that lazily caches a
    # ModuleLoader-backed Environment (holding unpicklable compiled
    # _TemplateModule objects) on first call. The HTMLGenerator instance is
    # sent once to each worker process via the document-export parallelizer's
    # pool initializer (see export_complete_tree()), so populating that cache
    # here, in the main process, before parallel export starts, would make
    # the whole HTMLGenerator (and its html_templates) unpicklable for the
    # worker pool. A standalone, uncached environment sidesteps that
    # entirely; favicon.svg.jinja is small enough that skipping template
    # compilation has no measurable cost.
    variant = project_config.get_favicon_variant()
    return (
        NormalHTMLTemplates()
        .jinja_environment()
        .get_template("_shared/favicon.svg.jinja")
        .render(variant=variant)
    )


def _export_single_document_worker(document_mid: MID) -> Tuple[str, float]:
    """
    Module-level (picklable-by-reference) task function for the document
    export parallelizer. The (HTMLGenerator, TraceabilityIndex) pair is not
    passed as an argument here: it is sent to each worker process exactly
    once via run_parallel_with_context()'s pool initializer, instead of
    being pickled fresh into every submitted document's task.

    Only the document's MID travels per-task, not the SDocDocument object
    itself: the document is looked up in this worker's own copy of
    traceability_index instead. Nodes reachable from a document that was
    pickled separately (e.g. as a direct task argument) would not be the
    same Python objects as the ones inside the worker's traceability_index
    (a different, earlier pickle/unpickle of the same content) - and
    identity-sensitive lookups, such as NodeFilter's blacklist (a plain
    `set`, hashed/compared by object identity), would then silently fail
    to recognize them.

    Returns the document's title and export duration instead of printing
    directly: the caller (running in the main process) reports progress for
    all documents through a single measure_performance_loop(), which a
    worker process can't safely share (concurrent in-place progress-line
    writes from multiple processes would interleave and corrupt the
    terminal output).
    """
    html_generator, traceability_index = get_worker_context()
    document = traceability_index.get_node_by_mid(document_mid)
    time_start = time.time()
    html_generator.export_single_document(document, traceability_index)
    time_end = time.time()
    return document.title, time_end - time_start


class HTMLGenerator:
    def __init__(
        self, project_config: ProjectConfig, html_templates: HTMLTemplates
    ):
        self.project_config: ProjectConfig = project_config
        self.html_templates = html_templates
        self.git_client: GitClient = GitClient()

    def export_complete_tree(
        self,
        *,
        traceability_index: TraceabilityIndex,
        parallelizer: Parallelizer,
    ) -> None:
        Path(self.project_config.export_output_html_root).mkdir(
            parents=True, exist_ok=True
        )

        # Export assets.
        HTMLGenerator.export_assets(
            traceability_index=traceability_index,
            project_config=self.project_config,
            html_templates=self.html_templates,
            export_output_html_root=self.project_config.export_output_html_root,
        )

        # Export static search index.
        self.export_static_html_search_index(
            traceability_index=traceability_index
        )

        # By default, do not export included documents. Only, if the option to
        # include is provided.
        documents_to_export: List[SDocDocument] = []

        if self.project_config.export_included_documents:
            documents_to_export[:] = (
                traceability_index.document_tree.document_list
            )
        else:
            with measure_performance_loop(
                "Skip",
                len(traceability_index.document_tree.document_list),
            ) as report_progress:
                for document_ in traceability_index.document_tree.document_list:
                    if document_.document_is_included():
                        continue

                    document_meta = assert_cast(document_.meta, DocumentMeta)

                    input_doc_full_path = document_meta.input_doc_full_path
                    output_doc_full_path = (
                        document_meta.output_document_full_path
                    )

                    if os.path.isfile(output_doc_full_path) and (
                        get_file_modification_time(input_doc_full_path)
                        < get_file_modification_time(output_doc_full_path)
                        and not traceability_index.file_dependency_manager.must_generate(
                            document_meta.output_document_full_path
                        )
                    ):
                        with report_progress(document_.title):
                            continue

                    documents_to_export.append(document_)

        if len(documents_to_export) > 0:
            with measure_performance_loop(
                "Export to HTML", len(documents_to_export)
            ) as report_progress:

                def on_item_complete(_: int, result: Tuple[str, float]) -> None:
                    title, elapsed_time = result
                    with report_progress(title, elapsed_time=elapsed_time):
                        pass

                parallelizer.run_parallel_with_context(
                    [
                        document_.reserved_mid
                        for document_ in documents_to_export
                    ],
                    _export_single_document_worker,
                    (self, traceability_index),
                    on_item_complete,
                )

        # Export document tree.
        # FIXME: It is important that this export is **after** the parallelized
        # export of single documents. It turns out that Jinja does not play
        # well with the multiprocessing's processed-based parallelization.
        # _pickle.PicklingError: Can't pickle <function sync_do_first at 0x1077bdf80>: it's not the same object as jinja2.filters.sync_do_first.
        self.export_project_tree_screen(traceability_index=traceability_index)

        # Export JavaScript map of the document tree (project map)
        self.export_project_map(traceability_index=traceability_index)

        if self.project_config.is_activated_tree_map():
            self.export_tree_map_screen(traceability_index)

        # Project statistics is exported by the ExportAction class via the
        # Feature abstraction (see the ProjectStatisticsFeature class), not
        # here.

        # Export requirements coverage.
        if self.project_config.is_feature_activated(
            ProjectFeature.TRACEABILITY_MATRIX_SCREEN
        ):
            self.export_requirements_coverage_screen(
                traceability_index=traceability_index,
            )

        # Export source coverage.
        if self.project_config.is_feature_activated(
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
        ):
            self.export_source_files_screens(
                traceability_index=traceability_index,
            )
            self.export_source_coverage_screen(
                traceability_index=traceability_index,
            )

        print(  # noqa: T201
            "Export completed. Documentation tree can be found at:\n"
            f"{self.project_config.export_output_html_root}"
        )

    @staticmethod
    def export_assets(
        *,
        traceability_index: Optional[TraceabilityIndex],
        project_config: ProjectConfig,
        html_templates: HTMLTemplates,
        export_output_html_root: str,
        flat_assets: bool = False,
    ) -> None:
        """
        Copy all assets to output dir during HTML/PDF generation.

        :param bool flat_assets: This parameter is always set to False except when
                                 exporting a "bundle document" with HTML2PDF.
                                 The bundle document contains all documents of
                                 the documentation tree. In this case, all assets
                                 are simply copied to the top level _assets folder,
                                 independently on how nested the contained documents are.
        """

        # Export StrictDoc's own assets.
        output_html_static_files = os.path.join(
            export_output_html_root,
            project_config.dir_for_sdoc_assets,
        )
        for static_files_path in project_config.get_static_files_paths():
            sync_dir(
                static_files_path,
                output_html_static_files,
                message="Copying StrictDoc's assets",
            )

        # Write the favicon: a project's own custom file if configured
        # (see ProjectConfig.get_custom_favicon_path()), or else render it
        # from the Jinja template so it can encode which kind of StrictDoc
        # instance (dev/test/docs export) rendered it.
        favicon_output_path = os.path.join(
            output_html_static_files, project_config.get_favicon_filename()
        )
        custom_favicon_path = project_config.get_custom_favicon_path()
        if custom_favicon_path is not None:
            shutil.copyfile(custom_favicon_path, favicon_output_path)
        else:
            favicon_svg = render_favicon_svg(project_config, html_templates)
            with open(favicon_output_path, "w", encoding="utf8") as output_file:
                output_file.write(favicon_svg)

        # Copy the project's custom CSS file, if configured. base.jinja.html
        # links it after StrictDoc's own stylesheets so it can override them.
        custom_css_path = project_config.custom_css_path
        if custom_css_path is not None:
            shutil.copyfile(
                custom_css_path,
                os.path.join(
                    output_html_static_files,
                    project_config.get_custom_css_filename(),
                ),
            )

        # Export HTML2PDF.
        if project_config.is_feature_activated(ProjectFeature.HTML2PDF):
            sync_dir(
                os.path.dirname(PATH_TO_HTML2PDF4DOC_JS),
                output_html_static_files,
                message="Copying HTML2PDF.js",
            )

        # Export custom html2pdf template.
        if project_config.html2pdf_template is not None:
            output_custom_html2pdf_template = os.path.join(
                export_output_html_root,
                project_config.dir_for_sdoc_assets,
                "html2pdf_template",
            )
            sync_dir(
                os.path.abspath(
                    os.path.dirname(project_config.html2pdf_template)
                ),
                output_custom_html2pdf_template,
                message="Copying Custom HTML2PDF template assets",
            )

        # Export project's assets.

        if traceability_index is not None:
            redundant_assets: Dict[str, List[SDocRelativePath]] = {}
            for document_ in traceability_index.document_tree.document_list:
                assert document_.meta is not None
                for (
                    included_document_
                ) in document_.iterate_included_documents_depth_first():
                    assert included_document_.meta is not None

                    redundant_assets.setdefault(
                        document_.meta.input_doc_assets_dir_rel_path.relative_path_posix,
                        [],
                    )
                    redundant_assets[
                        document_.meta.input_doc_assets_dir_rel_path.relative_path_posix
                    ].append(
                        included_document_.meta.input_doc_assets_dir_rel_path
                    )

            assert traceability_index.asset_manager is not None

            asset_dir_: AssetDir
            for asset_dir_ in traceability_index.asset_manager.iterate():
                source_path = asset_dir_.full_path
                output_relative_path = asset_dir_.relative_path

                destination_path = os.path.join(
                    export_output_html_root,
                    output_relative_path.relative_path
                    if not flat_assets
                    else "_assets",
                )

                sync_dir(
                    source_path,
                    destination_path,
                    message=f'Copying project assets "{output_relative_path.relative_path}"',
                )
                redundant_asset_paths = redundant_assets.get(
                    output_relative_path.relative_path_posix
                )
                if redundant_asset_paths is not None:
                    for redundant_asset_ in redundant_asset_paths:
                        destination_path = os.path.join(
                            export_output_html_root,
                            redundant_asset_.relative_path
                            if not flat_assets
                            else "_assets",
                        )
                        sync_dir(
                            source_path,
                            destination_path,
                            message=f'Copying project assets "{output_relative_path.relative_path}"',
                        )

    def export_single_document_with_performance(
        self,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
        specific_documents: Optional[Tuple[DocumentType, ...]] = None,
    ) -> None:
        if specific_documents is None:
            specific_documents = DocumentType.all()

        with measure_performance(f"Published: {document.title}"):
            self.export_single_document(
                document,
                traceability_index,
                specific_documents=specific_documents,
            )

    def export_single_document(
        self,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
        specific_documents: Optional[Tuple[DocumentType, ...]] = None,
    ) -> SDocDocument:
        if document.config.layout == "Website":
            specific_documents = (DocumentType.DOCUMENT,)
        elif specific_documents is None:
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
            markup=document.config.markup,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            html_templates=self.html_templates,
            config=self.project_config,
            context_document=document,
        )

        if DocumentType.DOCUMENT in specific_documents:
            # Single Document pages.
            document_content = DocumentHTMLGenerator.export(
                project_config=self.project_config,
                document=document,
                traceability_index=traceability_index,
                markup_renderer=markup_renderer,
                link_renderer=link_renderer,
                git_client=self.git_client,
                html_templates=self.html_templates,
            )
            document_out_file = document_meta.get_html_doc_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        # Single Document Table pages.
        if (
            self.project_config.is_feature_activated(
                ProjectFeature.TABLE_SCREEN
            )
            and DocumentType.TABLE in specific_documents
        ):
            document_content = DocumentTableHTMLGenerator.export(
                project_config=self.project_config,
                document=document,
                traceability_index=traceability_index,
                markup_renderer=markup_renderer,
                link_renderer=link_renderer,
                git_client=self.git_client,
                html_templates=self.html_templates,
            )
            document_out_file = document_meta.get_html_table_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        # Single Document Traceability pages.
        if (
            self.project_config.is_feature_activated(
                ProjectFeature.TRACEABILITY_SCREEN
            )
            and DocumentType.TRACE in specific_documents
        ):
            document_content = DocumentTraceHTMLGenerator.export(
                project_config=self.project_config,
                document=document,
                traceability_index=traceability_index,
                markup_renderer=markup_renderer,
                link_renderer=link_renderer,
                git_client=self.git_client,
                html_templates=self.html_templates,
            )
            document_out_file = document_meta.get_html_traceability_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        # Single Document Deep Traceability pages.
        if (
            self.project_config.is_feature_activated(
                ProjectFeature.DEEP_TRACEABILITY_SCREEN
            )
            and DocumentType.DEEPTRACE in specific_documents
        ):
            document_content = DocumentDeepTraceHTMLGenerator.export_deep(
                project_config=self.project_config,
                document=document,
                traceability_index=traceability_index,
                markup_renderer=markup_renderer,
                link_renderer=link_renderer,
                git_client=self.git_client,
                html_templates=self.html_templates,
            )
            document_out_file = document_meta.get_html_deep_traceability_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        # Single Document PDF pages.
        if (
            self.project_config.is_feature_activated(ProjectFeature.HTML2PDF)
            and DocumentType.PDF in specific_documents
        ):
            document_content = DocumentHTML2PDFGenerator.export(
                project_config=self.project_config,
                document=document,
                traceability_index=traceability_index,
                markup_renderer=markup_renderer,
                link_renderer=link_renderer,
                git_client=self.git_client,
                html_templates=self.html_templates,
            )
            document_out_file = document_meta.get_html_pdf_path()
            with open(document_out_file, "w", encoding="utf8") as file:
                file.write(document_content)

        return document

    def export_project_tree_screen(
        self,
        *,
        traceability_index: TraceabilityIndex,
    ) -> None:
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

    def export_project_map(
        self,
        *,
        traceability_index: TraceabilityIndex,
    ) -> None:
        assets_dir = os.path.join(
            self.project_config.export_output_html_root,
            self.project_config.dir_for_sdoc_assets,
        )
        output_file = os.path.join(assets_dir, "project_map.js")
        writer = ProjectMapGenerator()
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
    ) -> None:
        requirements_coverage_content = TraceabilityMatrixHTMLGenerator.export(
            project_config=self.project_config,
            traceability_index=traceability_index,
            html_templates=self.html_templates,
        )
        output_html_requirements_coverage = os.path.join(
            self.project_config.export_output_html_root,
            "traceability_matrix.html",
        )
        with open(
            output_html_requirements_coverage, "w", encoding="utf8"
        ) as file:
            file.write(requirements_coverage_content)

    @timing_decorator("Export source file pages")
    def export_source_files_screens(
        self,
        *,
        traceability_index: TraceabilityIndex,
    ) -> None:
        assert isinstance(
            traceability_index.document_tree.source_tree, SourceTree
        ), traceability_index.document_tree.source_tree
        print("Generating source files:")  # noqa: T201

        referenced_source_files = [
            source_file
            for source_file in traceability_index.document_tree.source_tree.source_files
            if source_file.is_referenced
        ]

        source_files_to_export: List[SourceFile] = []
        with measure_performance_loop(
            "Skip", len(referenced_source_files)
        ) as report_progress:
            for source_file in referenced_source_files:
                if not traceability_index.file_dependency_manager.must_generate(
                    source_file.output_file_full_path
                ):
                    with report_progress(
                        source_file.in_doctree_source_file_rel_path,
                        short_title=shorten_path(
                            source_file.in_doctree_source_file_rel_path
                        ),
                    ):
                        continue
                source_files_to_export.append(source_file)

        if len(source_files_to_export) > 0:
            with measure_performance_loop(
                "File", len(source_files_to_export)
            ) as report_progress:
                for source_file in source_files_to_export:
                    with report_progress(
                        source_file.in_doctree_source_file_rel_path,
                        short_title=shorten_path(
                            source_file.in_doctree_source_file_rel_path
                        ),
                    ):
                        SourceFileViewHTMLGenerator.export_to_file(
                            project_config=self.project_config,
                            source_file=source_file,
                            traceability_index=traceability_index,
                            html_templates=self.html_templates,
                        )

    def export_source_coverage_screen(
        self,
        *,
        traceability_index: TraceabilityIndex,
    ) -> None:
        assert isinstance(
            traceability_index.document_tree.source_tree, SourceTree
        ), traceability_index.document_tree.source_tree

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

    def export_single_source_file_screen(
        self,
        *,
        traceability_index: TraceabilityIndex,
        path_to_source_file: str,
    ) -> None:
        assert isinstance(
            traceability_index.document_tree.source_tree, SourceTree
        ), traceability_index.document_tree.source_tree

        # FIXME: path_to_source_file must not enter this function with forward slashes.
        #        Test and fix this on Windows.
        #        https://github.com/strictdoc-project/strictdoc/issues/2068
        relative_path_to_source_file = path_to_posix_path(path_to_source_file)
        relative_path_to_source_file = (
            relative_path_to_source_file.removeprefix("_source_files/")
        )
        relative_path_to_source_file = (
            relative_path_to_source_file.removesuffix(".html")
        )

        for (
            source_file
        ) in traceability_index.document_tree.source_tree.source_files:
            if not source_file.is_referenced:
                continue

            if (
                relative_path_to_source_file
                == source_file.in_doctree_source_file_rel_path_posix
            ):
                SourceFileViewHTMLGenerator.export_to_file_with_performance(
                    project_config=self.project_config,
                    source_file=source_file,
                    traceability_index=traceability_index,
                    html_templates=self.html_templates,
                )
                return

        raise FileNotFoundError

    @timing_decorator("Export static HTML search index")
    def export_static_html_search_index(
        self,
        traceability_index: TraceabilityIndex,
        *,
        force_regeneration: bool = False,
    ) -> None:
        """
        Export a static search index as dictionaries in .js files.

        @relation(SDOC-SRS-155, scope=function)
        @relation(SDOC-SRS-156, scope=function)
        """

        if not force_regeneration:
            # First check if there is nothing to do because no documents have
            # been changed or regenerated.

            # FIXME: This is wrong. FIX!
            must_regenerate = (
                len(traceability_index.document_tree.document_list) == 0
            )

            for document_ in traceability_index.document_tree.document_list:
                assert document_.meta is not None
                if traceability_index.file_dependency_manager.must_generate(
                    document_.meta.output_document_full_path
                ):
                    must_regenerate = True
                    break

            if not must_regenerate:
                print(  # noqa: T201
                    "All documents are up-to-date. "
                    "Skipping the generation of a search index."
                )
                # If no documents need to be regenerated, set the
                # search_index_timestamp to the timestamp of the first document.
                # The HTML/JS code can rely on this timestamp to decide whether
                # it has to re-read the search index from the JS file or it can
                # fetch it from the DB.
                if len(traceability_index.document_tree.document_list) > 0:
                    first_document = (
                        traceability_index.document_tree.document_list[0]
                    )
                    assert first_document.meta is not None
                    traceability_index.search_index_timestamp = (
                        get_file_modification_time(
                            first_document.meta.input_doc_full_path
                        )
                    )
                return

        if force_regeneration:
            for document_ in traceability_index.document_tree.document_list:
                document_.build_search_index()

        global_index: Dict[str, Set[int]] = defaultdict(set)
        global_map_nodes_by_mid: Dict[int, Dict[str, str]] = {}

        document_index_list: List[Dict[str, Set[str]]] = []
        document_map_list: List[Dict[int, Dict[str, str]]] = []

        map_mid_to_numbers: Dict[str, int] = {}

        with measure_performance("Build search index"):
            for document_ in traceability_index.document_tree.document_list:
                assert document_.meta is not None
                document_index_list.append(
                    document_.search_index.document_index
                )
                map_nodes_by_numbers: Dict[int, Dict[str, str]] = {}
                for (
                    node_mid_,
                    node_dict_,
                ) in document_.search_index.map_nodes_by_mid.items():
                    if node_mid_ not in map_mid_to_numbers:
                        map_mid_to_numbers[node_mid_] = (
                            len(map_mid_to_numbers) + 1
                        )
                    document_mid_number = map_mid_to_numbers[node_mid_]
                    assert isinstance(document_mid_number, int)
                    map_nodes_by_numbers[document_mid_number] = node_dict_

                document_map_list.append(map_nodes_by_numbers)
            for document_index_ in document_index_list:
                for term_, document_mids_ in document_index_.items():
                    document_mid_numbers = set()
                    for document_mid_ in document_mids_:
                        document_mid_number = map_mid_to_numbers[document_mid_]
                        document_mid_numbers.add(document_mid_number)
                    global_index[term_].update(document_mid_numbers)
            for map_nodes_by_mid_ in document_map_list:
                global_map_nodes_by_mid.update(map_nodes_by_mid_)

        link_renderer = LinkRenderer(
            root_path="",
            static_path=self.project_config.dir_for_sdoc_assets,
        )
        for _, node_ in global_map_nodes_by_mid.items():
            # When running on server, the MID is used as a link to the node.
            # The MID is then resolved to the correct URL by the server when
            # requested at /UID/{uid_or_mid}.
            # This ensures that all nodes can be reached with MID, including
            # the nodes that don't have a UID.
            if self.project_config.is_running_on_server:
                node_["_LINK"] = node_["MID"]

            # When running static HTML, the resolution of _LINKs happens through
            # the auto-generated static JS project_map.js that has a format of:
            # {<local anchor>: MID}
            else:
                node = traceability_index.get_node_by_mid(MID(node_["MID"]))
                node_["_LINK"] = link_renderer.render_local_anchor(node)

        def default(obj: Any) -> Any:
            if isinstance(obj, set):
                return list(obj)
            raise TypeError

        with measure_performance("Serialize search index to JS"):
            document_content = (
                b"window.StrictDoc = window.StrictDoc || {};\n"
                b"window.StrictDoc.search = window.StrictDoc.search || {};\n"
                b"window.StrictDoc.search.index = "
                + orjson.dumps(
                    global_index,
                    option=orjson.OPT_NON_STR_KEYS,
                    default=default,
                )
                + b";\n\n"
            )

        with measure_performance("Serialize lookup map {MID => node} to JS"):
            document_content += (
                b"window.StrictDoc.search.nodesByMid = "
                + orjson.dumps(
                    global_map_nodes_by_mid, option=orjson.OPT_NON_STR_KEYS
                )
                + b";\n"
            )

        # Export StrictDoc's own assets.
        output_html_static_files = os.path.join(
            self.project_config.export_output_html_root,
            self.project_config.dir_for_sdoc_assets,
        )
        output_html_source_coverage = os.path.join(
            output_html_static_files,
            "static_html_search_index.js",
        )
        with open(output_html_source_coverage, "wb") as file:
            file.write(document_content)

        traceability_index.search_index_timestamp = get_file_modification_time(
            output_html_source_coverage
        )

    def export_tree_map_screen(
        self,
        traceability_index: TraceabilityIndex,
    ) -> None:
        TreeMapGenerator.export(
            project_config=self.project_config,
            traceability_index=traceability_index,
            html_templates=self.html_templates,
        )
