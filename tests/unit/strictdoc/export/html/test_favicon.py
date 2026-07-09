from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from strictdoc import environment as strictdoc_environment
from strictdoc.export.html.html_generator import (
    render_favicon_svg,
    resolve_favicon_variant,
)
from strictdoc.export.html.html_templates import NormalHTMLTemplates


def _project_config_stub(
    *, is_debug_mode: bool, is_test_env: bool
) -> SimpleNamespace:
    return SimpleNamespace(
        environment=SimpleNamespace(
            is_debug_mode=is_debug_mode, is_test_env=is_test_env
        )
    )


def test_resolve_favicon_variant_test_env_takes_priority():
    project_config = _project_config_stub(is_debug_mode=True, is_test_env=True)
    assert resolve_favicon_variant(project_config) == "test"


def test_resolve_favicon_variant_dev_server():
    project_config = _project_config_stub(
        is_debug_mode=True, is_test_env=False
    )
    assert resolve_favicon_variant(project_config) == "dev"


def test_resolve_favicon_variant_user_deployed_or_export():
    project_config = _project_config_stub(
        is_debug_mode=False, is_test_env=False
    )
    assert resolve_favicon_variant(project_config) == "default"


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


def test_favicon_template_tags_output_with_the_given_variant():
    for variant in ("default", "dev", "test"):
        svg = _render_favicon_template(variant=variant)
        assert f'data-testid="{variant}-favicon"' in svg


def test_render_favicon_svg_wires_resolved_variant_into_the_template():
    """Guards the Python -> Jinja handoff, not just each half separately."""
    project_config = _project_config_stub(is_debug_mode=True, is_test_env=False)
    svg = render_favicon_svg(project_config, NormalHTMLTemplates())
    assert 'data-testid="dev-favicon"' in svg
