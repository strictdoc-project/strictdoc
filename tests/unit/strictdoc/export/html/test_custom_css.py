import copy

from strictdoc import environment as strictdoc_environment
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.html.html_templates import NormalHTMLTemplates
from tests.unit.helpers.view_object_builder import (
    create_document_screen_view_object,
)


def _project_config(
    *,
    custom_css_path: str | None = None,
) -> ProjectConfig:
    project_config = ProjectConfig()
    # A shallow copy of the real environment singleton: keeps
    # get_static_files_paths() etc. working, without mutating the shared
    # global strictdoc.environment object that other tests may rely on.
    project_config.environment = copy.copy(strictdoc_environment)
    project_config.custom_css_path = custom_css_path
    return project_config


def test_custom_css_is_not_configured_by_default():
    project_config = _project_config()
    assert project_config.custom_css_path is None


# Exercises the real HTMLGenerator.export_assets() and real filesystem
# I/O (tmp_path), asserting on actual bytes written to disk rather than
# mocked calls.
def test_export_assets_copies_custom_css(tmp_path):
    css_source = tmp_path / "my_styles.css"
    css_source.write_text("body { background: hotpink; }")

    project_config = _project_config(custom_css_path=str(css_source))
    output_root = tmp_path / "output"
    output_root.mkdir()

    HTMLGenerator.export_assets(
        traceability_index=None,
        project_config=project_config,
        html_templates=NormalHTMLTemplates(),
        export_output_html_root=str(output_root),
    )

    static_dir = output_root / project_config.dir_for_sdoc_assets
    custom_css_output = static_dir / project_config.get_custom_css_filename()
    assert custom_css_output.read_text() == "body { background: hotpink; }"


def test_export_assets_writes_no_custom_css_when_not_configured(tmp_path):
    project_config = _project_config()
    output_root = tmp_path / "output"
    output_root.mkdir()

    HTMLGenerator.export_assets(
        traceability_index=None,
        project_config=project_config,
        html_templates=NormalHTMLTemplates(),
        export_output_html_root=str(output_root),
    )

    static_dir = output_root / project_config.dir_for_sdoc_assets
    assert not (static_dir / project_config.get_custom_css_filename()).exists()


# Regression test for custom.css needing to load after every other
# stylesheet, including ones a screen-specific template adds to head_css
# via super() (e.g. move_node_tree.css for the document screen). Renders
# the actual document screen template rather than asserting on template
# source, so it catches a future head_css/head_custom_css block reordering.
def test_custom_css_loads_after_screen_specific_stylesheets():
    view_object = create_document_screen_view_object(
        custom_css_path="/tmp/some/custom.css",
    )

    html = str(view_object.render_screen())

    move_node_tree_pos = html.index("move_node_tree.css")
    custom_css_pos = html.index("custom.css")
    assert move_node_tree_pos < custom_css_pos
