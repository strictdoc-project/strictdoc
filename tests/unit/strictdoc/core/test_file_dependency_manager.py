"""
@relation(SDOC-SRS-2, scope=file)
"""

import datetime
from pathlib import Path
from typing import Any, List

import pytest

from strictdoc.core import file_dependency_manager as file_dependency_module
from strictdoc.core.file_dependency_manager import FileDependencyManager
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.file_modification_time import (
    set_file_modification_time,
)

TIME_1 = datetime.datetime(2026, 1, 1, 12, 0, 0)
TIME_2 = datetime.datetime(2026, 1, 1, 12, 0, 10)
TIME_3 = datetime.datetime(2026, 1, 1, 12, 0, 20)


def create_manager(tmp_path: Path) -> FileDependencyManager:
    project_config = ProjectConfig.default_config()
    project_config.output_dir = str(tmp_path / "output")
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    return FileDependencyManager.create_from_cache(project_config)


def create_file(path: Path, modification_time: datetime.datetime) -> str:
    path.write_text("content")
    set_file_modification_time(str(path), modification_time)
    return str(path)


def test_01_up_to_date_output_is_not_regenerated(tmp_path: Path) -> None:
    input_file = create_file(tmp_path / "input.sdoc", TIME_1)
    output_file = create_file(tmp_path / "output.html", TIME_2)
    manager = create_manager(tmp_path)
    manager.add_dependency(input_file, output_file)

    manager.resolve_modification_dates(TIME_1)

    assert not manager.must_generate(output_file)


def test_02_missing_output_is_regenerated(tmp_path: Path) -> None:
    input_file = create_file(tmp_path / "input.sdoc", TIME_1)
    output_file = str(tmp_path / "output.html")
    manager = create_manager(tmp_path)
    manager.add_dependency(input_file, output_file)

    manager.resolve_modification_dates(TIME_1)

    assert manager.must_generate(output_file)


def test_03_output_older_than_input_is_regenerated(tmp_path: Path) -> None:
    input_file = create_file(tmp_path / "input.sdoc", TIME_2)
    output_file = create_file(tmp_path / "output.html", TIME_1)
    manager = create_manager(tmp_path)
    manager.add_dependency(input_file, output_file)

    manager.resolve_modification_dates(TIME_1)

    assert manager.must_generate(output_file)


def test_04_output_older_than_strictdoc_is_regenerated(
    tmp_path: Path,
) -> None:
    input_file = create_file(tmp_path / "input.sdoc", TIME_1)
    output_file = create_file(tmp_path / "output.html", TIME_2)
    manager = create_manager(tmp_path)
    manager.add_dependency(input_file, output_file)

    manager.resolve_modification_dates(TIME_3)

    assert manager.must_generate(output_file)


def test_05_output_of_a_removed_input_is_regenerated(tmp_path: Path) -> None:
    input_file = create_file(tmp_path / "input.sdoc", TIME_1)
    output_file = create_file(tmp_path / "output.html", TIME_2)
    manager = create_manager(tmp_path)
    manager.add_dependency(input_file, output_file)
    manager.resolve_modification_dates(TIME_1)
    # The next run has no dependencies yet, and the input file is removed.
    # Only the previous dependencies know the output.
    manager.dependencies_now.clear()
    Path(input_file).unlink()

    manager.resolve_modification_dates(TIME_1)

    assert manager.must_generate(output_file)


def test_06_previous_dependencies_are_a_copy(tmp_path: Path) -> None:
    input_file = create_file(tmp_path / "input.sdoc", TIME_1)
    output_file = create_file(tmp_path / "output.html", TIME_2)
    manager = create_manager(tmp_path)
    manager.add_dependency(input_file, output_file)

    manager.resolve_modification_dates(TIME_1)
    manager.add_dependency(input_file, str(tmp_path / "other.html"))

    assert manager.dependencies_prev == {input_file: {output_file}}


def test_07_each_file_is_checked_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_file_1 = create_file(tmp_path / "input_1.sdoc", TIME_1)
    input_file_2 = create_file(tmp_path / "input_2.sdoc", TIME_1)
    output_files = [
        create_file(tmp_path / f"output_{index_}.html", TIME_2)
        for index_ in range(3)
    ]
    manager = create_manager(tmp_path)
    for output_file_ in output_files:
        manager.add_dependency(input_file_1, output_file_)
        manager.add_dependency(input_file_2, output_file_)
    # The previous dependencies are the same as the current ones.
    manager.resolve_modification_dates(TIME_1)
    for output_file_ in output_files:
        manager.add_dependency(input_file_1, output_file_)
        manager.add_dependency(input_file_2, output_file_)

    checked_files: List[str] = []
    get_file_modification_time = (
        file_dependency_module.get_file_modification_time
    )

    def get_file_modification_time_(path: str) -> Any:
        checked_files.append(path)
        return get_file_modification_time(path)

    monkeypatch.setattr(
        file_dependency_module,
        "get_file_modification_time",
        get_file_modification_time_,
    )

    manager.resolve_modification_dates(TIME_1)

    assert sorted(checked_files) == sorted(
        [input_file_1, input_file_2, *output_files]
    )
    assert not any(
        manager.must_generate(output_file_) for output_file_ in output_files
    )
