"""
@relation(SDOC-SRS-95, scope=file)
"""

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.md5 import get_file_md5
from strictdoc.helpers.pickle import pickle_dump, pickle_load


@dataclass
class PickleCacheEntry:
    mtime_ns: int
    size: int
    md5: str
    content: Any


class PickleCache:
    @staticmethod
    def read_from_cache(
        file_path: str, project_config: ProjectConfig, content_kind: str
    ) -> Any:
        path_to_cached_file: str = PickleCache.get_cached_file_path(
            file_path, project_config, content_kind
        )
        if not os.path.isfile(path_to_cached_file):
            return None

        with open(path_to_cached_file, "rb") as cache_file:
            pickled_entry = cache_file.read()
        try:
            entry = pickle_load(pickled_entry)
        except Exception as exception_:
            raise AssertionError(
                "MUST NOT REACH HERE: "
                f"Error when unpickling a cache file: {path_to_cached_file}. "
                "To fix the issue, simply remove the cache file or the whole cache folder. "
                "Please report this exception to StrictDoc developers: "
                f"https://github.com/strictdoc-project/strictdoc/issues/new"
            ) from exception_

        # A None result (schema change, see pickle_load()) or an entry
        # written by a previous, incompatible cache format both count as a
        # cache miss.
        if not isinstance(entry, PickleCacheEntry):
            return None

        # Fast path: if the file's mtime and size are unchanged since the
        # entry was written, trust the cache without reading and hashing the
        # file's content. This is the common case on a no-op re-run and
        # turns the cache-freshness check into a single stat() call.
        file_stat = os.stat(file_path)
        if (
            file_stat.st_mtime_ns == entry.mtime_ns
            and file_stat.st_size == entry.size
        ):
            return entry.content

        # Slow path: mtime/size changed (e.g., a git checkout touching the
        # file's mtime without changing its content). Fall back to a content
        # hash, like ccache/git do, before deciding the cache is stale.
        if get_file_md5(file_path) == entry.md5:
            # Content is unchanged: heal the entry so that the next read
            # hits the fast path again.
            entry.mtime_ns = file_stat.st_mtime_ns
            entry.size = file_stat.st_size
            with open(path_to_cached_file, "wb") as cache_file:
                cache_file.write(pickle_dump(entry))
            return entry.content

        return None

    @staticmethod
    def save_to_cache(
        content: Any,
        file_path: str,
        project_config: ProjectConfig,
        content_kind: str,
    ) -> None:
        path_to_cached_file: str = PickleCache.get_cached_file_path(
            file_path, project_config, content_kind
        )
        path_to_cached_file_dir: str = os.path.dirname(path_to_cached_file)
        Path(path_to_cached_file_dir).mkdir(parents=True, exist_ok=True)

        file_stat = os.stat(file_path)
        entry = PickleCacheEntry(
            mtime_ns=file_stat.st_mtime_ns,
            size=file_stat.st_size,
            md5=get_file_md5(file_path),
            content=content,
        )
        pickled_entry: bytes = pickle_dump(entry)
        with open(path_to_cached_file, "wb") as cache_file:
            cache_file.write(pickled_entry)

    @staticmethod
    def get_cached_file_path(
        file_path: str, project_config: ProjectConfig, content_kind: str
    ) -> str:
        path_to_tmp_dir = project_config.get_path_to_cache_dir()

        full_path_to_file = (
            file_path
            if os.path.isabs(file_path)
            else os.path.abspath(file_path)
        )

        # File name contains an MD5 hash of its full path to ensure the
        # uniqueness of the cached items. Additionally, the unique file name
        # contains a full path to the output root to prevent collisions
        # between StrictDoc invocations running against the same set of SDoc
        # files in parallel.
        #
        # The file name is stable across content changes: unlike before, it
        # no longer embeds a content hash, because computing that hash is
        # exactly the per-run cost this cache is meant to avoid (see
        # read_from_cache()'s stat-based fast path). One cache entry is
        # reused and overwritten in place per input file, instead of
        # accumulating one file per historical content version.
        unique_identifier = project_config.output_dir + full_path_to_file
        unique_identifier_md5 = hashlib.md5(
            unique_identifier.encode("utf-8")
        ).hexdigest()
        file_name = (
            os.path.basename(full_path_to_file) + "_" + unique_identifier_md5
        )

        path_to_cached_file = os.path.join(
            path_to_tmp_dir,
            content_kind,
            file_name,
        )

        return path_to_cached_file
