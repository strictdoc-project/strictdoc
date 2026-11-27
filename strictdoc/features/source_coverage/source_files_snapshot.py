"""
@relation(SDOC-SRS-35, scope=file)

Use case: static export.

The source coverage page lists all source files with their line
statistics, also the files without markers. The file dependency manager
tracks only the source files with markers, because only these files are
inputs of documents. To decide if the source coverage page is up to date,
the static export compares the list of source files with the list of the
previous export: the path, the modification time, and the size of each
file. A new, deleted, or changed source file changes the list.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.project_config import ProjectConfig

# (path, modification time in nanoseconds, size in bytes)
SourceFileState = Tuple[str, int, int]

SNAPSHOT_FILE_NAME = "source_coverage_source_files.json"


def create_source_files_snapshot(
    source_files: Sequence[SourceFile],
) -> List[SourceFileState]:
    snapshot: List[SourceFileState] = []
    for source_file_ in source_files:
        file_stat = os.stat(source_file_.full_path)
        snapshot.append(
            (
                source_file_.in_doctree_source_file_rel_path_posix,
                file_stat.st_mtime_ns,
                file_stat.st_size,
            )
        )
    return sorted(snapshot)


def read_previous_source_files_snapshot(
    project_config: ProjectConfig,
) -> Optional[List[SourceFileState]]:
    """
    Return the snapshot of the previous export, or None if there is none or
    if it cannot be read. None makes the export generate the page.
    """
    path_to_snapshot = _get_path_to_snapshot(project_config)
    if not os.path.isfile(path_to_snapshot):
        return None
    try:
        with open(path_to_snapshot, encoding="utf8") as snapshot_file:
            rows = json.load(snapshot_file)
        return [(str(row_[0]), int(row_[1]), int(row_[2])) for row_ in rows]
    except (OSError, ValueError, TypeError, IndexError):
        return None


def save_source_files_snapshot(
    project_config: ProjectConfig, snapshot: List[SourceFileState]
) -> None:
    path_to_snapshot = _get_path_to_snapshot(project_config)
    Path(os.path.dirname(path_to_snapshot)).mkdir(parents=True, exist_ok=True)
    with open(path_to_snapshot, "w", encoding="utf8") as snapshot_file:
        json.dump(snapshot, snapshot_file)


def _get_path_to_snapshot(project_config: ProjectConfig) -> str:
    return os.path.join(
        project_config.get_path_to_cache_dir(), SNAPSHOT_FILE_NAME
    )
