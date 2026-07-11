import copy

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from strictdoc import environment as strictdoc_environment
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_generator import (
    HTMLGenerator,
    render_favicon_svg,
)
from strictdoc.export.html.html_templates import NormalHTMLTemplates


def _project_config(
    *,
    is_development_mode: bool,
    is_test_env: bool,
    is_running_on_server: bool = True,
    favicon_path: str | None = None,
) -> ProjectConfig:
    project_config = ProjectConfig()
    # A shallow copy of the real environment singleton: keeps
    # get_static_files_paths() etc. working, without mutating the shared
    # global strictdoc.environment object that other tests may rely on.
    project_config.environment = copy.copy(strictdoc_environment)
    project_config.environment.is_development_mode = is_development_mode
    project_config.environment.is_test_env = is_test_env
    project_config.is_running_on_server = is_running_on_server
    project_config.favicon_path = favicon_path
    return project_config


# Checks that get_favicon_variant() maps is_test_env/is_development_mode/
# is_running_on_server to the expected string, per the priority the
# function itself encodes. Protects against an accidental edit to that
# mapping (e.g. swapped priority, a typo in a string literal).
# LIMITATION: cannot validate that is_development_mode is the correct
# signal for "this is StrictDoc's own dev server" - that is a design
# decision, not something expressible as an assertion over this
# function's inputs/outputs. See
# tests/unit/strictdoc/cli/test_cli_arg_parser.py for coverage of the
# actual CLI-flag wiring.
def test_get_favicon_variant_test_env_takes_priority():
    project_config = _project_config(is_development_mode=True, is_test_env=True)
    assert project_config.get_favicon_variant() == "test"


def test_get_favicon_variant_dev_server():
    project_config = _project_config(
        is_development_mode=True, is_test_env=False
    )
    assert project_config.get_favicon_variant() == "dev"


def test_get_favicon_variant_user_deployed_server():
    project_config = _project_config(
        is_development_mode=False, is_test_env=False
    )
    assert project_config.get_favicon_variant() == "default"


def test_get_favicon_variant_static_export():
    project_config = _project_config(
        is_development_mode=False,
        is_test_env=False,
        is_running_on_server=False,
    )
    assert project_config.get_favicon_variant() == "export"


# Checks get_favicon_filename()/get_favicon_mime_type() branching
# (custom file vs. rendered SVG, per-variant override rule). Same
# limitation as above: confirms the branching matches the code, not that
# restricting custom favicons to the default variant is the correct
# product requirement.
def test_favicon_filename_and_mime_type_default_to_the_svg_template():
    project_config = _project_config(
        is_development_mode=False, is_test_env=False
    )
    assert project_config.get_custom_favicon_path() is None
    assert project_config.get_favicon_filename() == "favicon.svg"
    assert project_config.get_favicon_mime_type() == "image/svg+xml"


def test_custom_favicon_is_used_for_the_default_variant():
    project_config = _project_config(
        is_development_mode=False,
        is_test_env=False,
        favicon_path="/tmp/some/logo.png",
    )
    assert project_config.get_custom_favicon_path() == "/tmp/some/logo.png"
    assert project_config.get_favicon_filename() == "favicon.png"
    assert project_config.get_favicon_mime_type() == "image/png"


def test_custom_favicon_is_ignored_for_dev_and_test_variants():
    for is_development_mode, is_test_env in ((True, False), (False, True)):
        project_config = _project_config(
            is_development_mode=is_development_mode,
            is_test_env=is_test_env,
            favicon_path="/tmp/some/logo.png",
        )
        assert project_config.get_custom_favicon_path() is None
        assert project_config.get_favicon_filename() == "favicon.svg"
        assert project_config.get_favicon_mime_type() == "image/svg+xml"


def _render_favicon_template(*, variant: str) -> str:
    jinja_environment = Environment(
        loader=FileSystemLoader(
            strictdoc_environment.get_path_to_html_templates()
        ),
        undefined=StrictUndefined,
        autoescape=True,
    )
    template = jinja_environment.get_template("_shared/favicon.svg.jinja")
    return template.render(variant=variant)


# Actually renders the real .jinja file through Jinja (not a stub), so
# this catches template syntax errors and a missing/renamed data-testid
# attribute - real rendering, not just Python-side logic.
def test_favicon_template_tags_output_with_the_given_variant():
    for variant in ("default", "dev", "test", "export"):
        svg = _render_favicon_template(variant=variant)
        assert f'data-testid="{variant}-favicon"' in svg


def test_render_favicon_svg_wires_resolved_variant_into_the_template():
    """Guards the Python -> Jinja handoff, not just each half separately."""
    project_config = _project_config(
        is_development_mode=True, is_test_env=False
    )
    svg = render_favicon_svg(project_config, NormalHTMLTemplates())
    assert 'data-testid="dev-favicon"' in svg


# Exercises the real HTMLGenerator.export_assets() and real filesystem
# I/O (tmp_path), asserting on actual bytes written to disk rather than
# mocked calls.
def test_export_assets_copies_custom_favicon_for_default_variant(tmp_path):
    favicon_source = tmp_path / "logo.png"
    favicon_source.write_bytes(b"fake-png-bytes")

    project_config = _project_config(
        is_development_mode=False,
        is_test_env=False,
        favicon_path=str(favicon_source),
    )
    output_root = tmp_path / "output"
    output_root.mkdir()

    HTMLGenerator.export_assets(
        traceability_index=None,
        project_config=project_config,
        html_templates=NormalHTMLTemplates(),
        export_output_html_root=str(output_root),
    )

    static_dir = output_root / project_config.dir_for_sdoc_assets
    assert (static_dir / "favicon.png").read_bytes() == b"fake-png-bytes"
    assert not (static_dir / "favicon.svg").exists()


def test_export_assets_ignores_custom_favicon_for_dev_variant(tmp_path):
    favicon_source = tmp_path / "logo.png"
    favicon_source.write_bytes(b"fake-png-bytes")

    project_config = _project_config(
        is_development_mode=True,
        is_test_env=False,
        favicon_path=str(favicon_source),
    )
    output_root = tmp_path / "output"
    output_root.mkdir()

    HTMLGenerator.export_assets(
        traceability_index=None,
        project_config=project_config,
        html_templates=NormalHTMLTemplates(),
        export_output_html_root=str(output_root),
    )

    static_dir = output_root / project_config.dir_for_sdoc_assets
    assert (
        'data-testid="dev-favicon"' in (static_dir / "favicon.svg").read_text()
    )
    assert not (static_dir / "favicon.png").exists()
