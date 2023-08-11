import sys
from collections import Counter

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
    create_safe_title_string,
)


class ManageAutoUIDCommand:
    @staticmethod
    def execute(*, project_config: ProjectConfig, parallelizer: Parallelizer):
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    project_config=project_config,
                    parallelizer=parallelizer,
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)

        document_tree_stats: DocumentTreeStats = (
            DocumentUIDAnalyzer.analyze_document_tree(traceability_index)
        )

        document_stats: DocumentStats
        for document_stats in document_tree_stats.single_document_stats:
            document_acronym = create_safe_acronym(
                document_stats.document.title
            )
            section_uids_so_far = Counter()
            for section in document_stats.sections_without_uid:
                section_title = create_safe_title_string(section.title)
                auto_uid = f"SECTION-{document_acronym}-{section_title}"

                count_so_far = section_uids_so_far[auto_uid]
                section_uids_so_far[auto_uid] += 1

                if count_so_far >= 1:
                    auto_uid += f"-{section_uids_so_far[auto_uid]}"

                section.uid = auto_uid
                section.reserved_uid = auto_uid

            for (
                prefix,
                prefix_requirements,
            ) in document_stats.requirements_per_prefix.items():
                next_number = document_stats.get_next_requirement_uid_number(
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
            document_content = SDWriter().write(document)
            document_meta = document.meta
            with open(
                document_meta.input_doc_full_path, "w", encoding="utf8"
            ) as output_file:
                output_file.write(document_content)
