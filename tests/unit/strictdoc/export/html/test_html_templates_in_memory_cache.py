"""
The Jinja environments of the HTML export keep the loaded templates in a
plain dict without a size limit, not in the default LRU cache of Jinja. See
JINJA_TEMPLATE_CACHE_SIZE for the reasons.
"""

from jinja2 import Environment

from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import (
    CompiledHTMLTemplates,
    NormalHTMLTemplates,
)

TEMPLATE = "features/document/index.jinja"


def _assert_unbounded_cache(environment: Environment) -> None:
    assert type(environment.cache) is dict
    template = environment.get_template(TEMPLATE)
    assert environment.get_template(TEMPLATE) is template
    assert len(environment.cache) > 0


def test_normal_templates_use_unbounded_cache():
    templates = NormalHTMLTemplates()
    _assert_unbounded_cache(templates.jinja_environment().environment)


def test_compiled_templates_use_unbounded_cache(tmp_path):
    project_config = ProjectConfig.default_config()
    project_config.output_dir = "./output/server"
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    templates = CompiledHTMLTemplates(project_config)
    templates.compile_jinja_templates()
    _assert_unbounded_cache(templates.jinja_environment().environment)
