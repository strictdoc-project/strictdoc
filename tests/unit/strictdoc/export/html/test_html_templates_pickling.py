"""
An HTMLTemplates object is pickled as a reference, so that the tasks of the
parallelizer can carry it to worker processes. Unpickling returns the
HTMLTemplates object of the receiving process.
"""

import multiprocessing
import pickle
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pytest

from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html import html_templates as html_templates_module
from strictdoc.export.html.html_templates import (
    CompiledHTMLTemplates,
    NormalHTMLTemplates,
)

TEMPLATE = "screens/document/document/index.jinja"


def _compiled_templates(tmp_path: Path) -> CompiledHTMLTemplates:
    project_config = ProjectConfig.default_config()
    project_config.output_dir = "./output/server"
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    templates = CompiledHTMLTemplates(project_config)
    templates.compile_jinja_templates()
    return templates


def _forget_templates_of_this_process(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A worker process that is not forked starts without HTMLTemplates objects.
    """
    monkeypatch.setattr(
        html_templates_module, "_html_templates_of_this_process", {}
    )


def test_01_compiled_templates_are_pickled_as_a_reference(
    tmp_path: Path,
) -> None:
    templates = _compiled_templates(tmp_path)
    # A Jinja environment cannot be pickled. The reference does not include
    # it.
    templates.jinja_environment()

    data = pickle.dumps(templates)

    assert len(data) < 1000
    assert pickle.loads(data) is templates


def test_02_compiled_templates_in_a_process_without_templates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    templates = _compiled_templates(tmp_path)
    data = pickle.dumps(templates)
    _forget_templates_of_this_process(monkeypatch)

    unpickled_templates = pickle.loads(data)

    assert isinstance(unpickled_templates, CompiledHTMLTemplates)
    assert unpickled_templates is not templates
    assert (
        unpickled_templates.path_to_jinja_cache_bucket_dir
        == templates.path_to_jinja_cache_bucket_dir
    )
    assert unpickled_templates.jinja_environment().get_template(TEMPLATE)
    # The later tasks in the same process reuse the object.
    assert pickle.loads(data) is unpickled_templates


def test_03_normal_templates_are_pickled_as_a_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    templates = NormalHTMLTemplates()
    data = pickle.dumps(templates)

    assert pickle.loads(data) is templates

    _forget_templates_of_this_process(monkeypatch)
    unpickled_templates = pickle.loads(data)

    assert isinstance(unpickled_templates, NormalHTMLTemplates)
    assert unpickled_templates is not templates
    assert unpickled_templates.jinja_environment().get_template(TEMPLATE)
    assert pickle.loads(data) is unpickled_templates


def test_04_compiled_templates_in_a_spawned_worker_process(
    tmp_path: Path,
) -> None:
    templates = _compiled_templates(tmp_path)

    # A spawned worker process starts without HTMLTemplates objects, like a
    # worker process on Windows. It must unpickle the templates from the
    # reference.
    with ProcessPoolExecutor(
        max_workers=1, mp_context=multiprocessing.get_context("spawn")
    ) as executor:
        path_in_worker = executor.submit(
            getattr, templates, "path_to_jinja_cache_bucket_dir"
        ).result()

    assert path_in_worker == templates.path_to_jinja_cache_bucket_dir
