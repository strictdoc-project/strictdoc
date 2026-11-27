"""
@relation(SDOC-SRS-35, scope=file)
"""

import os
from pathlib import Path
from typing import List

from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.source_coverage.source_files_snapshot import (
    SNAPSHOT_FILE_NAME,
    create_source_files_snapshot,
    read_previous_source_files_snapshot,
    save_source_files_snapshot,
)


def create_source_files(root: Path, names: List[str]) -> List[SourceFile]:
    source_files = []
    for name_ in names:
        path_to_file = root / name_
        if not path_to_file.exists():
            path_to_file.write_text(f"# {name_}\n")
        source_files.append(
            SourceFile(
                level=0,
                full_path=str(path_to_file),
                in_doctree_source_file_rel_path=name_,
                output_dir_full_path=str(root / "output"),
                output_file_full_path=str(root / "output" / f"{name_}.html"),
            )
        )
    return source_files


def create_project_config(tmp_path: Path) -> ProjectConfig:
    project_config = ProjectConfig.default_config()
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    return project_config


def test_01_snapshot_has_path_modification_time_and_size(
    tmp_path: Path,
) -> None:
    source_files = create_source_files(tmp_path, ["b.py", "a.py"])

    snapshot = create_source_files_snapshot(source_files)

    a_stat = os.stat(tmp_path / "a.py")
    b_stat = os.stat(tmp_path / "b.py")
    assert snapshot == [
        ("a.py", a_stat.st_mtime_ns, a_stat.st_size),
        ("b.py", b_stat.st_mtime_ns, b_stat.st_size),
    ]


def test_02_snapshot_changes_with_new_changed_and_deleted_files(
    tmp_path: Path,
) -> None:
    snapshot = create_source_files_snapshot(
        create_source_files(tmp_path, ["a.py", "b.py"])
    )

    with_new_file = create_source_files_snapshot(
        create_source_files(tmp_path, ["a.py", "b.py", "c.py"])
    )
    without_deleted_file = create_source_files_snapshot(
        create_source_files(tmp_path, ["a.py"])
    )
    (tmp_path / "b.py").write_text("# b.py has a new line\n# and another\n")
    with_changed_file = create_source_files_snapshot(
        create_source_files(tmp_path, ["a.py", "b.py"])
    )

    assert with_new_file != snapshot
    assert without_deleted_file != snapshot
    assert with_changed_file != snapshot


def test_03_saved_snapshot_is_read_back(tmp_path: Path) -> None:
    project_config = create_project_config(tmp_path)
    snapshot = create_source_files_snapshot(
        create_source_files(tmp_path, ["a.py", "b.py"])
    )

    save_source_files_snapshot(project_config, snapshot)

    assert read_previous_source_files_snapshot(project_config) == snapshot


def test_04_missing_or_broken_snapshot_reads_as_none(tmp_path: Path) -> None:
    project_config = create_project_config(tmp_path)

    assert read_previous_source_files_snapshot(project_config) is None

    (tmp_path / "cache").mkdir()
    (tmp_path / "cache" / SNAPSHOT_FILE_NAME).write_text("{not json")

    assert read_previous_source_files_snapshot(project_config) is None
