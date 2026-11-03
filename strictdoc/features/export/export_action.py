import sys
from typing import Optional

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.reference import FileReference
from strictdoc.core.feature import FeatureContext
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
        self._print_missing_relations_warning()
        self._print_unresolved_inline_links_warning()
        return traceability_index

    def _print_missing_relations_warning(self) -> None:
        if not self.project_config.relaxed_mode:
            return

        missing_relations = self.traceability_index.get_all_missing_relations()
        if len(missing_relations) == 0:
            return

        print(  # noqa: T201
            "warning: unresolved relations were "
            "detected and allowed by configuration."
        )
        print(  # noqa: T201
            f"warning: missing relations count: {len(missing_relations)}"
        )

        for requirement_, relation_ in missing_relations:
            requirement_identifier = (
                requirement_.reserved_uid
                if requirement_.reserved_uid is not None
                else requirement_.reserved_mid
            )
            document = requirement_.get_document()
            document_title = (
                document.reserved_title
                if isinstance(document, SDocDocument)
                else "UNKNOWN_DOCUMENT"
            )
            role_message = (
                f", role '{relation_.role}'"
                if relation_.role is not None
                else ""
            )

            if isinstance(relation_, FileReference):
                relation_target = f"file '{relation_.get_posix_path()}'"
            else:
                relation_target = f"requirement '{relation_.ref_uid}'"

            print(  # noqa: T201
                "warning: "
                f"requirement '{requirement_identifier}' in document "
                f"'{document_title}' has a missing relation of type "
                f"'{relation_.ref_type}' to {relation_target}{role_message}."
            )

    def _print_unresolved_inline_links_warning(self) -> None:
        if not self.project_config.relaxed_mode:
            return

        unresolved_inline_links = (
            self.traceability_index.get_all_unresolved_inline_links()
        )
        if len(unresolved_inline_links) == 0:
            return

        print(  # noqa: T201
            "warning: unresolved inline links were "
            "detected and allowed by configuration."
        )
        print(  # noqa: T201
            "warning: unresolved inline links count: "
            f"{len(unresolved_inline_links)}"
        )

        for node_, inline_link_ in unresolved_inline_links:
            node_identifier = (
                node_.reserved_uid
                if node_.reserved_uid is not None
                else node_.reserved_mid
            )
            document = node_.get_document()
            document_title = (
                document.reserved_title
                if isinstance(document, SDocDocument)
                else "UNKNOWN_DOCUMENT"
            )

            print(  # noqa: T201
                "warning: "
                f"node '{node_identifier}' in document "
                f"'{document_title}' has an unresolved inline link to "
                f"'{inline_link_.link}'."
            )

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

        # Features (cross-cutting export/server capabilities that are not
        # document-content conversion, e.g. project statistics) are exported
        # alongside formats. Gated on "html" specifically (not "html2pdf"),
        # matching the pre-Feature behavior where project statistics was
        # only ever generated as part of HTMLGenerator's own export() flow.
        if "html" in requested_handles:
            assert html_templates is not None
            feature_context = FeatureContext(
                project_config=self.project_config,
                traceability_index=self.traceability_index,
                html_templates=html_templates,
            )
            for feature_ in self.project_config.get_features():
                if not feature_.supports_export():
                    continue
                if self.traceability_index.is_up_to_date():
                    print(  # noqa: T201
                        "All documents are up-to-date. "
                        f"Skipping the generation of {feature_.HANDLE}."
                    )
                    continue
                feature_.export(feature_context)
