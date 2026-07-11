import sys
from typing import Optional

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.format import ExportContext
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.helpers.timing import timing_decorator


class ExportAction:
    def __init__(
        self,
        project_config: ProjectConfig,
        parallelizer: Parallelizer,
    ):
        assert parallelizer
        self.project_config: ProjectConfig = project_config
        self.parallelizer = parallelizer
        self.traceability_index: TraceabilityIndex = self.build_index()

    @timing_decorator("Parse SDoc project tree")
    def build_index(self) -> TraceabilityIndex:
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    project_config=self.project_config,
                    parallelizer=self.parallelizer,
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        self.traceability_index = traceability_index
        return traceability_index

    @timing_decorator("Export SDoc")
    def export(self) -> None:
        assert self.traceability_index is not None, (
            "The index must be built at this point."
        )
        assert self.project_config.export_formats is not None, (
            "The export_formats must not be None."
        )

        requested_handles = self.project_config.export_formats

        needs_html_templates = (
            "html" in requested_handles or "html2pdf" in requested_handles
        )

        html_templates: Optional[HTMLTemplates] = None
        bundle_traceability_index: Optional[TraceabilityIndex] = None
        bundle_document: Optional[SDocDocument] = None

        if needs_html_templates:
            is_small_project = self.traceability_index.is_small_project()

            html_templates = HTMLTemplates.create(
                project_config=self.project_config,
                enable_caching=not is_small_project,
                strictdoc_last_update=self.traceability_index.strictdoc_last_update,
            )

            # The bundle document is generated only when the option is provided.
            if self.project_config.generate_bundle_document:
                bundle_traceability_index, bundle_document = (
                    self.traceability_index.clone_to_bundle_document(
                        self.project_config
                    )
                )

        context = ExportContext(
            project_config=self.project_config,
            traceability_index=self.traceability_index,
            parallelizer=self.parallelizer,
            html_templates=html_templates,
            bundle_traceability_index=bundle_traceability_index,
            bundle_document=bundle_document,
        )

        # Iterate over the registered formats (not the user-requested
        # handles) so that the execution order matches the fixed order the
        # formats were originally hardcoded in, regardless of how the user
        # ordered --formats.
        for format_ in self.project_config.formats:
            for handle_ in format_.handles():
                if handle_ in requested_handles:
                    format_.export_complete_tree(context, handle=handle_)
