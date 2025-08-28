import importlib
import os
import sys
from collections import defaultdict
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import orjson
from html2pdf4doc.html2pdf4doc import PATH_TO_HTML2PDF4DOC_JS

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.asset_manager import AssetDir
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
from strictdoc.export.html.generators.project_map import (
    ProjectMapGenerator,
)
from strictdoc.export.html.generators.project_statistics import (
    ProgressStatisticsGenerator,
)
from strictdoc.export.html.generators.source_file_coverage import (
    SourceFileCoverageHTMLGenerator,
)
from strictdoc.export.html.generators.source_file_view_generator import (
    SourceFileViewHTMLGenerator,
)
from strictdoc.export.html.generators.traceability_matrix import (
    TraceabilityMatrixHTMLGenerator,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.html.tools.html_embedded import HTMLEmbedder
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.file_system import sync_dir
from strictdoc.helpers.git_client import GitClient
from strictdoc.helpers.mid import MID
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.helpers.paths import SDocRelativePath
from strictdoc.helpers.timing import measure_performance, timing_decorator


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
            export_output_html_root=self.project_config.export_output_html_root,
        )

        # Export static search index.
        self.export_static_html_search_index(
            traceability_index=traceability_index
        )

        # Export all documents in parallel.
        export_binding = partial(
            self.export_single_document_with_performance,
            traceability_index=traceability_index,
        )

        # By default, do not export included documents. Only, if the option to
        # include is provided.
        documents_to_export: List[SDocDocument] = []

        if self.project_config.export_included_documents:
            documents_to_export[:] = (
                traceability_index.document_tree.document_list
            )
        else:
            for document_ in traceability_index.document_tree.document_list:
                if document_.document_is_included():
                    continue

                document_meta = assert_cast(document_.meta, DocumentMeta)

                input_doc_full_path = document_meta.input_doc_full_path
                output_doc_full_path = document_meta.output_document_full_path

                if os.path.isfile(output_doc_full_path) and (
                    get_file_modification_time(input_doc_full_path)
                    < get_file_modification_time(output_doc_full_path)
                    and not traceability_index.file_dependency_manager.must_generate(
                        document_meta.output_document_full_path
                    )
                ):
                    with measure_performance(f"Skip: {document_.title}"):
                        continue

                documents_to_export.append(document_)

        if len(documents_to_export) > 0:
            if len(traceability_index.document_tree.document_list) <= 25:
                parallelizer.run_parallel(documents_to_export, export_binding)
            else:
                print(  # noqa: T201
                    "NOTE: Running document export without parallelization "
                    "because the document tree contains more than 25 documents."
                )
                for document_ in documents_to_export:
                    export_binding(document_)

        # Export document tree.
        # FIXME: It is important that this export is **after** the parallelized
        # export of single documents. It turns out that Jinja does not play
        # well with the multiprocessing's processed-based parallelization.
        # _pickle.PicklingError: Can't pickle <function sync_do_first at 0x1077bdf80>: it's not the same object as jinja2.filters.sync_do_first.
        self.export_project_tree_screen(traceability_index=traceability_index)

        # Export JavaScript map of the document tree (project map)
        self.export_project_map(traceability_index=traceability_index)

        # Export project statistics.
        if self.project_config.is_feature_activated(
            ProjectFeature.PROJECT_STATISTICS_SCREEN
        ):
            self.export_project_statistics(traceability_index)

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
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
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
        sync_dir(
            project_config.get_static_files_path(),
            output_html_static_files,
            message="Copying StrictDoc's assets",
        )

        # Export MathJax.
        if project_config.is_feature_activated(ProjectFeature.MATHJAX):
            output_html_mathjax = os.path.join(
                export_output_html_root,
                project_config.dir_for_sdoc_assets,
                "mathjax",
            )
            Path(output_html_mathjax).mkdir(parents=True, exist_ok=True)
            mathjax_src = os.path.join(
                project_config.get_extra_static_files_path(), "mathjax"
            )
            sync_dir(
                mathjax_src,
                output_html_mathjax,
                message="Copying MathJax assets",
            )

        # Export Mermaid.
        if project_config.is_feature_activated(ProjectFeature.MERMAID):
            output_html_mathjax = os.path.join(
                export_output_html_root,
                project_config.dir_for_sdoc_assets,
                "mermaid",
            )
            Path(output_html_mathjax).mkdir(parents=True, exist_ok=True)
            mermaid_src = os.path.join(
                project_config.get_extra_static_files_path(), "mermaid"
            )
            sync_dir(
                mermaid_src,
                output_html_mathjax,
                message="Copying Mermaid assets",
            )

        # Export Rapidoc.
        if project_config.is_feature_activated(ProjectFeature.RAPIDOC):
            output_html_rapidoc = os.path.join(
                export_output_html_root,
                project_config.dir_for_sdoc_assets,
                "rapidoc",
            )
            Path(output_html_rapidoc).mkdir(parents=True, exist_ok=True)
            rapidoc_src = os.path.join(
                project_config.get_extra_static_files_path(), "rapidoc"
            )
            sync_dir(
                rapidoc_src,
                output_html_rapidoc,
                message="Copying Rapidoc assets",
            )

        # Export NESTOR.
        if project_config.is_feature_activated(ProjectFeature.NESTOR):
            output_html_nestor = os.path.join(
                export_output_html_root,
                project_config.dir_for_sdoc_assets,
                "nestor",
            )
            Path(output_html_nestor).mkdir(parents=True, exist_ok=True)
            mathjax_src = os.path.join(
                project_config.get_extra_static_files_path(), "nestor"
            )
            sync_dir(
                mathjax_src,
                output_html_nestor,
                message="Copying Nestor assets",
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
                ].append(included_document_.meta.input_doc_assets_dir_rel_path)

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
            document.config.markup,
            traceability_index,
            link_renderer,
            self.html_templates,
            self.project_config,
            document,
        )

        if DocumentType.DOCUMENT in specific_documents:
            # Single Document pages.
            document_content = DocumentHTMLGenerator.export(
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                git_client=self.git_client,
                standalone=False,
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
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
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
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
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
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
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
                self.project_config,
                document,
                traceability_index,
                markup_renderer,
                link_renderer,
                git_client=self.git_client,
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
                git_client=self.git_client,
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

    def export_source_coverage_screen(
        self,
        *,
        traceability_index: TraceabilityIndex,
    ) -> None:
        assert isinstance(
            traceability_index.document_tree.source_tree, SourceTree
        ), traceability_index.document_tree.source_tree
        print("Generating source files:")  # noqa: T201
        for (
            source_file
        ) in traceability_index.document_tree.source_tree.source_files:
            if not source_file.is_referenced:
                continue

            SourceFileViewHTMLGenerator.export_to_file(
                project_config=self.project_config,
                source_file=source_file,
                traceability_index=traceability_index,
                html_templates=self.html_templates,
            )

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
    ) -> None:
        """
        Export project statistics to a dedicated HTML page.

        @relation(SDOC-SRS-97, scope=function)
        @relation(SDOC-SRS-154, scope=function)
        """

        link_renderer = LinkRenderer(
            root_path="",
            static_path=self.project_config.dir_for_sdoc_assets,
        )

        statistics_generator = ProgressStatisticsGenerator

        if (
            custom_statistics_generator_path
            := self.project_config.statistics_generator
        ) is not None:
            # It is important to add the input folder to the import path.
            # Otherwise, the custom statistics generator may not be found.
            # In fact, a more reasonable path to add would be the project config
            # path, but since it is not maintained by ProjectConfig yet and
            # usually equals the input path, add the input path for
            # now.
            input_paths = self.project_config.input_paths
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

    @timing_decorator("Export static HTML search index")
    def export_static_html_search_index(
        self,
        traceability_index: TraceabilityIndex,
    ) -> None:
        """
        Export a static search index as dictionaries in .js files.

        @relation(SDOC-SRS-155, scope=function)
        @relation(SDOC-SRS-156, scope=function)
        """

        # First check if there is nothing to do because no documents have been
        # changed or regenerated.
        for document_ in traceability_index.document_tree.document_list:
            assert document_.meta is not None
            if traceability_index.file_dependency_manager.must_generate(
                document_.meta.output_document_full_path
            ):
                break
        else:
            print(  # noqa: T201
                "All documents are up-to-date. "
                "Skipping the generation of a search index."
            )
            # If no documents need to be regenerated, set the search_index_timestamp
            # to the timestamp of the first document. The assumption here is
            # that StrictDoc does not randomize the document list, and the first
            # document will always be the same.
            # The HTML/JS code can rely on this timestamp to decide whether it
            # has to re-read the search index from the JS file or it can simply
            # fetch it from the DB which is 2x faster when it comes to very
            # large indexes.
            if len(traceability_index.document_tree.document_list) > 0:
                first_document = traceability_index.document_tree.document_list[
                    0
                ]
                assert first_document.meta is not None
                traceability_index.search_index_timestamp = (
                    get_file_modification_time(
                        first_document.meta.input_doc_full_path
                    )
                )
            return

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
            node = traceability_index.get_node_by_mid(MID(node_["MID"]))
            node_["_LINK"] = link_renderer.render_local_anchor(node)

        def default(obj: Any) -> Any:
            if isinstance(obj, set):
                return list(obj)
            raise TypeError

        with measure_performance("Serialize search index to JS"):
            document_content = (
                b"window.SDOC_SEARCH_INDEX = "
                + orjson.dumps(
                    global_index,
                    option=orjson.OPT_NON_STR_KEYS,
                    default=default,
                )
                + b";\n\n"
            )

        with measure_performance("Serialize lookup map {MID => node} to JS"):
            document_content += (
                b"window.SDOC_MAP_MID_TO_NODES = "
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
