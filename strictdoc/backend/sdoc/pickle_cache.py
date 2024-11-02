import hashlib
import os
from pathlib import Path
from typing import Any

from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.md5 import get_file_md5
from strictdoc.helpers.pickle import pickle_dump, pickle_load


class PickleCache:
    @staticmethod
    def read_from_cache(
        file_path: str, project_config: ProjectConfig, content_kind: str
    ) -> Any:
        path_to_cached_file: str = PickleCache.get_cached_file_path(
            file_path, project_config, content_kind
        )
        if os.path.isfile(path_to_cached_file):
            with open(path_to_cached_file, "rb") as cache_file:
                unpickled_content = cache_file.read()
            try:
                return pickle_load(unpickled_content)
            except Exception as exception_:
                raise AssertionError(
                    "MUST NOT REACH HERE: "
                    f"Error when unpickling a cache file: {path_to_cached_file}. "
                    "To fix the issue, simply remove the cache file or the whole cache folder. "
                    "Please report this exception to StrictDoc developers: "
                    f"https://github.com/strictdoc-project/strictdoc/issues/new"
                ) from exception_
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
        pickled_content: Any = pickle_dump(content)
        with open(path_to_cached_file, "wb") as cache_file:
            cache_file.write(pickled_content)

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

        file_md5: str = get_file_md5(file_path)

        # File name contains an MD5 hash of its full path to ensure the
        # uniqueness of the cached items. Additionally, the unique file name
        # contains a full path to the output root to prevent collisions
        # between StrictDoc invocations running against the same set of SDoc
        # files in parallel.
        unique_identifier = project_config.output_dir + full_path_to_file
        unique_identifier_md5 = hashlib.md5(
            unique_identifier.encode("utf-8")
        ).hexdigest()
        file_name = os.path.basename(full_path_to_file)
        file_name += "_" + unique_identifier_md5 + "_" + file_md5

        path_to_cached_file = os.path.join(
            path_to_tmp_dir,
            content_kind,
            file_name,
        )

        return path_to_cached_file
