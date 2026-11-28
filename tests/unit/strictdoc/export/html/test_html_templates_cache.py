"""
The precompiled Jinja template cache must not leave a half-filled bucket
if a compile is interrupted. The next run must compile the cache again.
"""

import glob
import os
from typing import Any, List

import pytest
from jinja2 import Environment

from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import CompiledHTMLTemplates

TEMPLATE = "features/document/index.jinja"


def _templates(tmp_path) -> CompiledHTMLTemplates:
    project_config = ProjectConfig.default_config()
    project_config.output_dir = "./output/server"
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    return CompiledHTMLTemplates(project_config)


def _compiled_modules(templates: CompiledHTMLTemplates) -> List[str]:
    return glob.glob(
        os.path.join(templates.path_to_jinja_cache_bucket_dir, "*.py")
    )


def _temporary_compile_folders(
    templates: CompiledHTMLTemplates,
) -> List[str]:
    parent = os.path.dirname(templates.path_to_jinja_cache_bucket_dir)
    if not os.path.isdir(parent):
        return []
    return [name_ for name_ in os.listdir(parent) if name_.startswith(".tmp-")]


def test_full_compile_leaves_no_temporary_folder(tmp_path):
    templates = _templates(tmp_path)
    templates.compile_jinja_templates()
    assert len(_compiled_modules(templates)) > 100
    parent = os.path.dirname(templates.path_to_jinja_cache_bucket_dir)
    assert os.listdir(parent) == [
        os.path.basename(templates.path_to_jinja_cache_bucket_dir)
    ]
    templates.jinja_environment().get_template(TEMPLATE)


def test_interrupted_compile_leaves_no_bucket(tmp_path, monkeypatch):
    templates = _templates(tmp_path)

    def compile_and_raise(
        _self: Environment, target: str, *_args: Any, **_kwargs: Any
    ) -> None:
        os.makedirs(target, exist_ok=True)
        with open(
            os.path.join(target, "partial.py"), "w", encoding="utf-8"
        ) as file:
            file.write("# incomplete\n")
        raise RuntimeError("interrupted")

    monkeypatch.setattr(Environment, "compile_templates", compile_and_raise)
    with pytest.raises(RuntimeError, match="interrupted"):
        templates.compile_jinja_templates()

    assert not os.path.isdir(templates.path_to_jinja_cache_bucket_dir)
    assert _temporary_compile_folders(templates) == []

    monkeypatch.undo()
    templates = _templates(tmp_path)
    templates.compile_jinja_templates()
    assert len(_compiled_modules(templates)) > 100
    templates.jinja_environment().get_template(TEMPLATE)
