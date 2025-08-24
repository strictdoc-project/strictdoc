"""
A simple container class for tracking dependencies between artifacts.

It provides answers to whether a given artifact has to be re-generated or not.

@relation(SDOC-SRS-2, scope=file)
"""

import datetime
import os.path
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Set

from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.file_modification_time import (
    get_file_modification_time,
)
from strictdoc.helpers.pickle import pickle_dump, pickle_load


@dataclass
class FileDependencyManager:
    path_to_cache_dir: str
    path_to_cache: str
    dependencies_now: Dict[str, Set[str]]
    dependencies_prev: Dict[str, Set[str]]
    dependencies_must_renegerate: Set[str]

    @staticmethod
    def create_from_cache(
        project_config: ProjectConfig,
    ) -> "FileDependencyManager":
        path_to_cache_dir = project_config.get_path_to_cache_dir()
        path_to_cache = os.path.join(path_to_cache_dir, "dependencies")

        if not os.path.isfile(path_to_cache):
            return FileDependencyManager(
                path_to_cache_dir, path_to_cache, {}, {}, set()
            )

        with open(path_to_cache, "rb") as cache_file:
            cache_file_bytes = cache_file.read()

        unpickled_content: Optional[FileDependencyManager] = pickle_load(
            cache_file_bytes
        )

        if unpickled_content is not None:
            assert isinstance(unpickled_content, FileDependencyManager), (
                unpickled_content,
            )
            unpickled_content.dependencies_now.clear()
            return unpickled_content

        raise AssertionError(  # pragma: no cover
            f"Problem reading the file dependency cache file: {path_to_cache}"
        )

    def must_generate(self, path_to_input_file: str) -> bool:
        must_regenerate = (
            path_to_input_file in self.dependencies_must_renegerate
        )
        return must_regenerate

    def add_dependency(
        self,
        path_to_file: str,
        path_to_dependent_file: str,
    ) -> None:
        dependencies = self.dependencies_now.setdefault(path_to_file, set())
        dependencies.add(path_to_dependent_file)

    def save_to_cache(self) -> None:
        self.dependencies_prev = deepcopy(self.dependencies_now)

        pickled_content = pickle_dump(self)

        Path(self.path_to_cache_dir).mkdir(exist_ok=True, parents=True)
        with open(self.path_to_cache, "wb") as cache_file:
            cache_file.write(pickled_content)

    def resolve_modification_dates(
        self, strictdoc_last_update: datetime.datetime
    ) -> None:
        self.dependencies_must_renegerate.clear()

        items_now, items_before = (
            self.dependencies_now.items(),
            self.dependencies_prev.items(),
        )
        for items_ in [items_now, items_before]:
            for path_to_input_file_, dependencies_ in items_:
                for path_to_dependency_ in dependencies_:
                    if (
                        # The file has not been generated yet.
                        not os.path.isfile(path_to_dependency_)
                        # The file used to exist but not anymore.
                        or not os.path.isfile(path_to_input_file_)
                        # The file is outdated compared to its HTML output artifact.
                        or get_file_modification_time(path_to_input_file_)
                        > get_file_modification_time(path_to_dependency_)
                        # The file is outdated compared to StrictDoc's own code (this
                        # branch is development-only).
                        or strictdoc_last_update
                        > get_file_modification_time(path_to_dependency_)
                    ):
                        self.dependencies_must_renegerate.add(
                            path_to_dependency_
                        )

        self.save_to_cache()
