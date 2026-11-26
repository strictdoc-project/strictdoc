from typing import List, Optional, Tuple

from strictdoc.core.format import ExportContext, Format
from strictdoc.export.html.document_type import DocumentType


class HTMLFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["html"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".html"]

    @staticmethod
    def supports_import() -> bool:
        return False

    @staticmethod
    def supports_export() -> bool:
        return True

    @staticmethod
    def supports_read() -> bool:
        return False

    @staticmethod
    def supports_edit() -> bool:
        return False

    @staticmethod
    def supports_grammar() -> bool:
        return False

    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        assert handle in self.handles(), handle
        assert context.html_templates is not None

        # The HTML generator imports the generators of all HTML screens.
        # Imported here so that a command or export without HTML does not
        # load them.
        from strictdoc.export.html.html_generator import (  # noqa: PLC0415
            HTMLGenerator,
        )

        html_generator = HTMLGenerator(
            context.project_config, context.html_templates
        )
        html_generator.export_complete_tree(
            traceability_index=context.traceability_index,
            parallelizer=context.parallelizer,
        )

        if context.project_config.generate_bundle_document:
            assert context.bundle_document is not None
            assert context.bundle_traceability_index is not None
            html_generator.export_single_document(
                document=context.bundle_document,
                traceability_index=context.bundle_traceability_index,
                specific_documents=(DocumentType.DOCUMENT,),
            )

        if (
            diff_git_revisions := context.project_config.diff_git_revisions
        ) is not None:
            from strictdoc.features.diff_and_changelog.change_generator import (  # noqa: PLC0415
                ChangeGenerator,
            )

            ChangeGenerator().generate_from_revisions(
                diff_git_revisions,
                project_config=context.project_config,
                html_templates=context.html_templates,
            )
        if (
            diff_dir_revisions := context.project_config.diff_dir_revisions
        ) is not None:
            from strictdoc.features.diff_and_changelog.change_generator import (  # noqa: PLC0415
                ChangeGenerator,
            )

            ChangeGenerator().generate_from_paths(
                path_to_lhs_tree=diff_dir_revisions[0],
                path_to_rhs_tree=diff_dir_revisions[1],
                project_config=context.project_config,
                html_templates=context.html_templates,
            )

    def export_single_document(
        self,
        context: ExportContext,
        document: object,
        specific_documents: Optional[Tuple[DocumentType, ...]] = None,
    ) -> None:
        assert context.html_templates is not None

        from strictdoc.export.html.html_generator import (  # noqa: PLC0415
            HTMLGenerator,
        )

        html_generator = HTMLGenerator(
            context.project_config, context.html_templates
        )
        html_generator.export_single_document(
            document,  # type: ignore[arg-type]
            context.traceability_index,
            specific_documents=specific_documents,
        )
