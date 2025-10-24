from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.git.project_diff_analyzer import (
    ChangeStats,
    ProjectTreeDiffStats,
)


class ChangeContainer:
    def __init__(
        self,
        *,
        change_stats: ChangeStats,
        documents_iterator_lhs: DocumentTreeIterator,
        documents_iterator_rhs: DocumentTreeIterator,
        lhs_stats: ProjectTreeDiffStats,
        rhs_stats: ProjectTreeDiffStats,
        traceability_index_lhs: TraceabilityIndex,
        traceability_index_rhs: TraceabilityIndex,
    ):
        self.change_stats: ChangeStats = change_stats
        self.documents_iterator_lhs = documents_iterator_lhs
        self.documents_iterator_rhs = documents_iterator_rhs
        self.lhs_stats: ProjectTreeDiffStats = lhs_stats
        self.rhs_stats: ProjectTreeDiffStats = rhs_stats
        self.traceability_index_lhs: TraceabilityIndex = traceability_index_lhs
        self.traceability_index_rhs: TraceabilityIndex = traceability_index_rhs
