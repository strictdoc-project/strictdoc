# mypy: disable-error-code="no-untyped-def"
import os
from copy import deepcopy
from datetime import datetime

from strictdoc.cli.cli_arg_parser import DiffCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.generators.view_objects.diff_screen_results_view_object import (
    DiffScreenResultsViewObject,
)
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.git.change_generator import ChangeContainer, ChangeGenerator


class DiffCommand:
    @staticmethod
    def execute(
        *, project_config: ProjectConfig, diff_config: DiffCommandConfig
    ):
        if not project_config.is_activated_diff():
            raise RuntimeError(
                "The DIFF feature is not activated in the project config."
            )

        # FIXME: Handle merging of Diff config data into project config more
        # gracefully.
        if diff_config.output_dir is not None:
            assert os.path.isdir(diff_config.output_dir)
            project_config.export_output_html_root = diff_config.output_dir
        else:
            project_config.export_output_html_root = os.path.join(
                os.getcwd(), "output"
            )

        assert os.path.isdir(diff_config.path_to_lhs_tree)
        assert os.path.isdir(diff_config.path_to_rhs_tree)

        if os.path.isabs(diff_config.path_to_lhs_tree):
            lhs_export_input_abs_path = diff_config.path_to_lhs_tree
        else:
            lhs_export_input_abs_path = os.path.join(
                os.getcwd(), diff_config.path_to_lhs_tree
            )
        if os.path.isabs(diff_config.path_to_rhs_tree):
            rhs_export_input_abs_path = diff_config.path_to_rhs_tree
        else:
            rhs_export_input_abs_path = os.path.join(
                os.getcwd(), diff_config.path_to_rhs_tree
            )

        project_config_copy_lhs: ProjectConfig = deepcopy(project_config)
        project_config_copy_rhs: ProjectConfig = deepcopy(project_config)

        project_config_copy_lhs.input_paths = [lhs_export_input_abs_path]
        project_config_copy_rhs.input_paths = [rhs_export_input_abs_path]

        change_container: ChangeContainer = ChangeGenerator.generate(
            lhs_project_config=project_config_copy_lhs,
            rhs_project_config=project_config_copy_rhs,
        )

        html_templates = HTMLTemplates.create(
            project_config=project_config,
            enable_caching=False,
            strictdoc_last_update=datetime.today(),
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
            left_revision_urlencoded=lhs_export_input_abs_path,
            right_revision=rhs_export_input_abs_path,
            right_revision_urlencoded=rhs_export_input_abs_path,
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
            left_revision_urlencoded=lhs_export_input_abs_path,
            right_revision=rhs_export_input_abs_path,
            right_revision_urlencoded=rhs_export_input_abs_path,
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

        # Copy assets.
        html_generator = HTMLGenerator(
            project_config=project_config, html_templates=html_templates
        )
        html_generator.export_assets(
            traceability_index=change_container.traceability_index_lhs,
            project_config=project_config,
            export_output_html_root=project_config.export_output_html_root,
        )
