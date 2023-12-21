import os
from copy import deepcopy
from datetime import datetime

from strictdoc import __version__
from strictdoc.cli.cli_arg_parser import DiffCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
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

        project_config_copy_lhs.export_input_paths = [lhs_export_input_abs_path]
        project_config_copy_rhs.export_input_paths = [rhs_export_input_abs_path]

        change_container: ChangeContainer = ChangeGenerator.generate(
            lhs_project_config=project_config_copy_lhs,
            rhs_project_config=project_config_copy_rhs,
        )

        html_templates = HTMLTemplates.create(
            project_config=project_config,
            enable_caching=False,
            strictdoc_last_update=datetime.today(),
        )

        template = html_templates.jinja_environment().get_template(
            "screens/git/index.jinja"
        )

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )

        output = template.render(
            project_config=project_config,
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
            link_renderer=link_renderer,
            document_type=DocumentType.document(),
            link_document_type=DocumentType.document(),
            standalone=False,
            strictdoc_version=__version__,
            results=True,
            tab="diff",
            error_message=None,
        )

        path_to_output_file = os.path.join(
            project_config.export_output_html_root, "diff.html"
        )
        with open(path_to_output_file, "w", encoding="utf8") as output_file:
            output_file.write(output)

        # Diff summary generator...
        template = html_templates.jinja_environment().get_template(
            "screens/git/index.jinja"
        )

        output = template.render(
            change_container=change_container,
            change_stats=change_container.change_stats,
            link_renderer=link_renderer,
            left_revision=lhs_export_input_abs_path,
            left_revision_urlencoded=lhs_export_input_abs_path,
            right_revision=rhs_export_input_abs_path,
            right_revision_urlencoded=rhs_export_input_abs_path,
            project_config=project_config,
            standalone=False,
            strictdoc_version=__version__,
            error_message=None,
            results=True,
            tab="changelog",
        )

        path_to_output_file = os.path.join(
            project_config.export_output_html_root, "changelog.html"
        )
        with open(path_to_output_file, "w", encoding="utf8") as output_file:
            output_file.write(output)

        # Copy assets.
        html_generator = HTMLGenerator(
            project_config=project_config, html_templates=html_templates
        )
        # FIXME: Traceability argument is not really important here.
        html_generator.export_assets(
            traceability_index=change_container.traceability_index_lhs
        )
