# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.git.project_diff_analyzer import (
    ChangeStats,
    ProjectDiffAnalyzer,
    ProjectTreeDiffStats,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.parallelizer import NullParallelizer


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


class ChangeGenerator:
    @staticmethod
    def generate(
        lhs_project_config: ProjectConfig,
        rhs_project_config: ProjectConfig,
    ) -> ChangeContainer:
        assert isinstance(lhs_project_config, ProjectConfig)
        assert isinstance(rhs_project_config, ProjectConfig)

        parallelizer = NullParallelizer()

        traceability_index_lhs: TraceabilityIndex = (
            TraceabilityIndexBuilder.create(
                project_config=lhs_project_config,
                parallelizer=parallelizer,
                # We don't want to deal with source files for Diff.
                skip_source_files=True,
            )
        )

        traceability_index_rhs: TraceabilityIndex = (
            TraceabilityIndexBuilder.create(
                project_config=rhs_project_config,
                parallelizer=parallelizer,
                # We don't want to deal with source files for Diff.
                skip_source_files=True,
            )
        )

        lhs_stats: ProjectTreeDiffStats = (
            ProjectDiffAnalyzer.analyze_document_tree(traceability_index_lhs)
        )
        rhs_stats: ProjectTreeDiffStats = (
            ProjectDiffAnalyzer.analyze_document_tree(traceability_index_rhs)
        )
        change_stats: ChangeStats = ChangeStats.create_from_two_indexes(
            traceability_index_lhs, traceability_index_rhs, lhs_stats, rhs_stats
        )

        documents_iterator_lhs = DocumentTreeIterator(
            assert_cast(traceability_index_lhs.document_tree, DocumentTree)
        )
        documents_iterator_rhs = DocumentTreeIterator(
            assert_cast(traceability_index_rhs.document_tree, DocumentTree)
        )

        return ChangeContainer(
            change_stats=change_stats,
            documents_iterator_lhs=documents_iterator_lhs,
            documents_iterator_rhs=documents_iterator_rhs,
            lhs_stats=lhs_stats,
            rhs_stats=rhs_stats,
            traceability_index_lhs=traceability_index_lhs,
            traceability_index_rhs=traceability_index_rhs,
        )
