import os
from copy import deepcopy
from typing import Type

from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.generators.view_objects.diff_screen_results_view_object import (
    DiffScreenResultsViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.git.change_container import ChangeContainer
from strictdoc.git.git_client import GitClient
from strictdoc.git.project_diff_analyzer import (
    ChangeStats,
    ProjectDiffAnalyzer,
    ProjectTreeDiffStats,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.parallelizer import NullParallelizer


class ChangeGenerator:
    @classmethod
    def generate_from_paths(
        cls: Type["ChangeGenerator"],
        path_to_lhs_tree: str,
        path_to_rhs_tree: str,
        project_config: ProjectConfig,
        html_templates: HTMLTemplates,
    ) -> None:
        assert isinstance(project_config, ProjectConfig)

        if os.path.isabs(path_to_lhs_tree):
            lhs_export_input_abs_path = path_to_lhs_tree
        else:
            lhs_export_input_abs_path = os.path.join(
                os.getcwd(), path_to_lhs_tree
            )
        if os.path.isabs(path_to_rhs_tree):
            rhs_export_input_abs_path = path_to_rhs_tree
        else:
            rhs_export_input_abs_path = os.path.join(
                os.getcwd(), path_to_rhs_tree
            )

        project_config_copy_lhs: ProjectConfig = deepcopy(project_config)
        project_config_copy_rhs: ProjectConfig = deepcopy(project_config)

        project_config_copy_lhs.input_paths = [lhs_export_input_abs_path]
        project_config_copy_rhs.input_paths = [rhs_export_input_abs_path]

        change_container: ChangeContainer = ChangeGenerator.generate(
            lhs_project_config=project_config_copy_lhs,
            rhs_project_config=project_config_copy_rhs,
        )

        assert change_container.traceability_index_lhs.document_tree is not None
        assert change_container.traceability_index_rhs.document_tree is not None

        view_object = DiffScreenResultsViewObject(
            project_config=project_config,
            change_container=change_container,
            document_tree_lhs=change_container.traceability_index_lhs.document_tree,
            document_tree_rhs=change_container.traceability_index_rhs.document_tree,
            documents_iterator_lhs=change_container.documents_iterator_lhs,
            documents_iterator_rhs=change_container.documents_iterator_rhs,
            left_revision=lhs_export_input_abs_path,
            right_revision=rhs_export_input_abs_path,
            lhs_stats=change_container.lhs_stats,
            rhs_stats=change_container.rhs_stats,
            change_stats=change_container.change_stats,
            traceability_index_lhs=change_container.traceability_index_lhs,
            traceability_index_rhs=change_container.traceability_index_rhs,
            tab="diff",
        )

        output = view_object.render_screen(html_templates.jinja_environment())
        path_to_output_file = os.path.join(
            project_config.export_output_html_root, "diff.html"
        )
        with open(path_to_output_file, "w", encoding="utf8") as output_file:
            output_file.write(output)

        # Diff summary generator...

        view_object = DiffScreenResultsViewObject(
            project_config=project_config,
            change_container=change_container,
            document_tree_lhs=change_container.traceability_index_lhs.document_tree,
            document_tree_rhs=change_container.traceability_index_rhs.document_tree,
            documents_iterator_lhs=change_container.documents_iterator_lhs,
            documents_iterator_rhs=change_container.documents_iterator_rhs,
            left_revision=lhs_export_input_abs_path,
            right_revision=rhs_export_input_abs_path,
            lhs_stats=change_container.lhs_stats,
            rhs_stats=change_container.rhs_stats,
            change_stats=change_container.change_stats,
            traceability_index_lhs=change_container.traceability_index_lhs,
            traceability_index_rhs=change_container.traceability_index_rhs,
            tab="changelog",
        )
        output = view_object.render_screen(html_templates.jinja_environment())
        path_to_output_file = os.path.join(
            project_config.export_output_html_root, "changelog.html"
        )
        with open(path_to_output_file, "w", encoding="utf8") as output_file:
            output_file.write(output)

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

    def generate_from_revisions(
        self,
        diff_git_revisions: str,
        project_config: ProjectConfig,
        html_templates: HTMLTemplates,
    ) -> None:
        assert ".." in diff_git_revisions, diff_git_revisions

        left_revision, right_revision = diff_git_revisions.split("..")
        if (
            left_revision is None
            or len(left_revision) == 0
            or right_revision is None
            or len(right_revision) == 0
        ):
            raise StrictDocException("Valid Git revisions must be provided.")

        git_client = GitClient(".")
        try:
            if left_revision != "HEAD+":
                left_revision_resolved = git_client.check_revision(
                    left_revision
                )
            else:
                raise StrictDocException(
                    "Left revision argument 'HEAD+' is not supported. "
                    "'HEAD+' can only be used as a right revision argument."
                )

            if right_revision == "HEAD+":
                right_revision_resolved = "HEAD+"
            else:
                right_revision_resolved = git_client.check_revision(
                    right_revision
                )
        except LookupError as exception_:
            error_message = exception_.args[0]
            raise StrictDocException(error_message) from exception_

        assert left_revision_resolved is not None
        assert right_revision_resolved is not None

        git_client_lhs = GitClient.create_repo_from_local_copy(
            left_revision_resolved, project_config
        )

        assert project_config.input_paths is not None
        export_input_rel_path = os.path.relpath(
            project_config.input_paths[0], os.getcwd()
        )
        export_input_abs_path_lhs = os.path.join(
            git_client_lhs.path_to_git_root, export_input_rel_path
        )

        git_client_rhs = GitClient.create_repo_from_local_copy(
            right_revision_resolved, project_config
        )

        export_input_abs_path_rhs = os.path.join(
            git_client_rhs.path_to_git_root, export_input_rel_path
        )
        self.generate_from_paths(
            export_input_abs_path_lhs,
            export_input_abs_path_rhs,
            project_config=project_config,
            html_templates=html_templates,
        )
