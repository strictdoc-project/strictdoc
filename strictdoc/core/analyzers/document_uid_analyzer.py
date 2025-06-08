import typing
from collections import Counter
from typing import Dict, List

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.analyzers.document_stats import (
    DocumentStats,
    DocumentTreeStats,
    SinglePrefixRequirements,
)
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.string import (
    extract_last_numeric_part,
    extract_numeric_uid_prefix_part,
)


class DocumentUIDAnalyzer:
    @staticmethod
    def analyze_document_tree(
        traceability_index: TraceabilityIndex,
    ) -> DocumentTreeStats:
        global_requirements_per_prefix: Dict[str, SinglePrefixRequirements] = {}
        document_tree_stats: List[DocumentStats] = []
        section_uids_so_far: typing.Counter[str] = Counter()

        document_tree: DocumentTree = assert_cast(
            traceability_index.document_tree, DocumentTree
        )

        for document in document_tree.document_list:
            document_stats: DocumentStats = (
                DocumentUIDAnalyzer.analyze_document(document)
            )
            for (
                requirement_prefix_,
                prefix_requirements_,
            ) in document_stats.requirements_per_prefix.items():
                global_prefix_requirements = (
                    global_requirements_per_prefix.setdefault(
                        requirement_prefix_, SinglePrefixRequirements()
                    )
                )
                global_prefix_requirements.requirements_no_uid.extend(
                    prefix_requirements_.requirements_no_uid
                )
                global_prefix_requirements.requirements_uid_numbers.extend(
                    prefix_requirements_.requirements_uid_numbers
                )
            document_tree_stats.append(document_stats)
            for section_uid_ in document_stats.section_uids_so_far:
                section_uids_so_far[section_uid_] += 1
        return DocumentTreeStats(
            single_document_stats=document_tree_stats,
            requirements_per_prefix=global_requirements_per_prefix,
            section_uids_so_far=section_uids_so_far,
        )

    @staticmethod
    def analyze_document(
        document: SDocDocument,
    ) -> DocumentStats:
        this_document_stats = DocumentStats(document)
        document_iterator = DocumentCachingIterator(document)
        for node, _ in document_iterator.all_content():
            if isinstance(node, SDocSection) or (
                isinstance(node, SDocNode) and node.node_type == "SECTION"
            ):
                if node.reserved_uid is not None:
                    this_document_stats.section_uids_so_far[
                        node.reserved_uid
                    ] += 1
                else:
                    this_document_stats.sections_without_uid.append(node)
                continue
            if not isinstance(node, SDocNode):
                continue
            if node.node_type in ("TEXT", "SECTION"):
                continue
            requirement: SDocNode = node
            node_prefix: typing.Optional[str] = requirement.get_prefix()
            if node_prefix is None:
                continue

            if node_prefix not in this_document_stats.requirements_per_prefix:
                this_document_stats.requirements_per_prefix[node_prefix] = (
                    SinglePrefixRequirements()
                )

            prefix_requirements: SinglePrefixRequirements = (
                this_document_stats.requirements_per_prefix[node_prefix]
            )
            if requirement.reserved_uid is None:
                prefix_requirements.requirements_no_uid.append(requirement)
            else:
                requirement_prefix = extract_numeric_uid_prefix_part(
                    requirement.reserved_uid
                )

                # If the requirement has a prefix which is different to that of
                # the parent section/document's prefix, we ignore this node as
                # incredible for contributing to the next UID calculation.
                if requirement_prefix != node_prefix:
                    continue

                requirement_uid_numeric_part = extract_last_numeric_part(
                    requirement.reserved_uid
                )
                assert len(requirement_uid_numeric_part) > 0
                requirement_uid_number = int(requirement_uid_numeric_part)

                prefix_requirements.requirements_uid_numbers.append(
                    requirement_uid_number
                )

        return this_document_stats
