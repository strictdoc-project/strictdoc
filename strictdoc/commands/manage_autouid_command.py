# mypy: disable-error-code="no-untyped-call,no-untyped-def,union-attr"
import sys

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.analyzers.document_stats import (
    DocumentStats,
    DocumentTreeStats,
)
from strictdoc.core.analyzers.document_uid_analyzer import DocumentUIDAnalyzer
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.helpers.string import (
    create_safe_acronym,
)


class ManageAutoUIDCommand:
    @staticmethod
    def execute(*, project_config: ProjectConfig, parallelizer: Parallelizer):
        # FIXME: Traceability Index is coupled with HTML output.
        project_config.export_output_html_root = "NOT_RELEVANT"

        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    project_config=project_config,
                    parallelizer=parallelizer,
                    auto_uid_mode=True,
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)

        document_tree_stats: DocumentTreeStats = (
            DocumentUIDAnalyzer.analyze_document_tree(traceability_index)
        )

        if project_config.autouuid_include_sections:
            document_stats_: DocumentStats
            for document_stats_ in document_tree_stats.single_document_stats:
                document_acronym = create_safe_acronym(
                    document_stats_.document.title
                )
                for section in document_stats_.sections_without_uid:
                    auto_uid = document_tree_stats.get_auto_section_uid(
                        document_acronym, section
                    )
                    section.uid = auto_uid
                    section.reserved_uid = auto_uid

        for (
            prefix,
            prefix_requirements,
        ) in document_tree_stats.requirements_per_prefix.items():
            next_number = document_tree_stats.get_next_requirement_uid_number(
                prefix
            )

            for requirement in prefix_requirements.requirements_no_uid:
                requirement_prefix = requirement.get_requirement_prefix()
                requirement_uid = f"{requirement_prefix}{next_number}"
                requirement.set_field_value(
                    field_name="UID",
                    form_field_index=0,
                    value=requirement_uid,
                )
                next_number += 1

        for document in traceability_index.document_tree.document_list:
            document_content = SDWriter(project_config).write(document)
            document_meta = document.meta
            with open(
                document_meta.input_doc_full_path, "w", encoding="utf8"
            ) as output_file:
                output_file.write(document_content)
