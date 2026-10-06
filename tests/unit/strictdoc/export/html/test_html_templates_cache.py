"""
The precompiled Jinja template cache (CompiledHTMLTemplates) must never serve
a page with TemplateNotFound because its cache bucket is incomplete.
"""

import glob
import os

from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import CompiledHTMLTemplates

TEMPLATE = "screens/document/document/index.jinja"


def _templates(tmp_path) -> CompiledHTMLTemplates:
    project_config = ProjectConfig.default_config()
    project_config.output_dir = "./output/server"
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    return CompiledHTMLTemplates(project_config)


def _compiled_modules(templates: CompiledHTMLTemplates):
    return glob.glob(
        os.path.join(templates.path_to_jinja_cache_bucket_dir, "*.py")
    )


def test_bucket_path_is_absolute(tmp_path, monkeypatch):
    # The server's default cache folder is relative to the current folder.
    monkeypatch.chdir(tmp_path)
    project_config = ProjectConfig.default_config()
    project_config.output_dir = "./output/server"
    project_config.dir_for_sdoc_cache = "./output/server/_cache"
    templates = CompiledHTMLTemplates(project_config)
    assert templates.path_to_jinja_cache_bucket_dir == os.path.join(
        os.getcwd(),
        "output",
        "server",
        "_cache",
        "jinja",
        os.path.basename(templates.path_to_jinja_cache_bucket_dir),
    )


def test_compile_writes_complete_bucket(tmp_path):
    templates = _templates(tmp_path)
    templates.compile_jinja_templates()
    assert len(_compiled_modules(templates)) > 100
    assert templates.is_jinja_cache_complete(
        CompiledHTMLTemplates.get_templates_fingerprint()
    )
    # No temporary compile folder is left behind.
    parent = os.path.dirname(templates.path_to_jinja_cache_bucket_dir)
    assert os.listdir(parent) == [
        os.path.basename(templates.path_to_jinja_cache_bucket_dir)
    ]
    templates.jinja_environment().get_template(TEMPLATE)


def test_incomplete_bucket_is_compiled_again(tmp_path):
    # A bucket without the completion marker, e.g. left by a run that was
    # stopped while compiling, or by an older StrictDoc.
    templates = _templates(tmp_path)
    templates.compile_jinja_templates()
    n_modules = len(_compiled_modules(templates))
    os.remove(
        os.path.join(
            templates.path_to_jinja_cache_bucket_dir,
            CompiledHTMLTemplates.COMPLETE_MARKER,
        )
    )
    for path in _compiled_modules(templates)[::2]:
        os.remove(path)

    templates = _templates(tmp_path)
    templates.compile_jinja_templates()
    assert len(_compiled_modules(templates)) == n_modules


def test_missing_compiled_module_falls_back_to_source(tmp_path):
    # The bucket is complete but loses files afterwards: templates still
    # load, from their source files.
    templates = _templates(tmp_path)
    templates.compile_jinja_templates()
    for path in _compiled_modules(templates):
        os.remove(path)
    templates.jinja_environment().get_template(TEMPLATE)
