import functools
import os
from typing import Dict, Iterator, List, Optional, Tuple, Union

from typing_extensions import TypeAlias

from strictdoc.helpers.file_system import is_binary_file
from strictdoc.helpers.path_filter import PathFilter
from strictdoc.helpers.paths import SDocRelativePath
from strictdoc.helpers.sorting import alphanumeric_sort

FileOrFolderEntry: TypeAlias = Union["File", "Folder"]


class File:
    def __init__(self, level: int, full_path: str, rel_path: SDocRelativePath):
        assert os.path.isfile(full_path)
        assert os.path.isabs(full_path)
        assert isinstance(rel_path, SDocRelativePath)

        self.level: int = level
        self.full_path: str = full_path
        self.rel_path: SDocRelativePath = rel_path
        self.folder_path: str = os.path.dirname(self.full_path)
        self.mount_folder: str = os.path.basename(self.folder_path)
        self.file_name: str = os.path.basename(self.full_path)
        self.files = [self]
        self.subfolder_trees: List[Folder] = []

    def is_folder(self) -> bool:
        return False

    def has_extension(self, extension: str) -> bool:
        return self.full_path.endswith(extension)


class Folder:
    def __init__(self, full_path: str, rel_path: str, level: int) -> None:
        assert os.path.isdir(full_path)
        assert os.path.isabs(full_path)
        assert isinstance(rel_path, str)

        self.full_path: str = full_path
        self.rel_path: str = rel_path if rel_path != "." else ""
        self.folder_name: str = os.path.basename(os.path.normpath(full_path))
        self.mount_folder: str = os.path.basename(self.full_path)
        self.level: int = level
        self.files: List[File] = []
        self.subfolder_trees: List[Folder] = []
        self.parent_folder: Optional[Folder] = None
        self.has_sdoc_content = False

    def __repr__(self) -> str:
        return f"Folder: (root_path: {self.full_path}, files: {self.files})"

    def is_folder(self) -> bool:
        return True

    def has_content(self) -> bool:
        if len(self.files) > 0:
            return True
        for subfolder_ in self.subfolder_trees:
            if subfolder_.has_content():
                return True
        return False

    def add_subfolder_tree(self, subfolder_tree: "Folder") -> None:
        assert isinstance(subfolder_tree, Folder)
        self.subfolder_trees.append(subfolder_tree)

    def set_parent_folder(self, parent_folder: "Folder") -> None:
        assert isinstance(parent_folder, Folder)
        self.parent_folder = parent_folder


class FileTree:
    def __init__(self, *, root_folder_or_file: FileOrFolderEntry) -> None:
        self.root_folder_or_file: FileOrFolderEntry = root_folder_or_file

    @staticmethod
    def create_single_file_tree(root_path: str) -> "FileTree":
        single_file = File(1, root_path, SDocRelativePath(""))
        return FileTree(root_folder_or_file=single_file)

    def iterate(self) -> Iterator[Tuple[Union[Folder, File], File, str]]:
        file_tree_mount_folder = self.root_folder_or_file.mount_folder

        task_list = [self.root_folder_or_file]
        while len(task_list) > 0:
            current_tree = task_list.pop(0)

            for doc_file in current_tree.files:
                yield self.root_folder_or_file, doc_file, file_tree_mount_folder

            task_list.extend(current_tree.subfolder_trees)


class FileFinder:
    @staticmethod
    def find_files_with_extensions(
        *,
        root_path: str,
        ignored_dirs: List[str],
        extensions: Optional[List[str]],
        include_paths: List[str],
        exclude_paths: List[str],
        dev_include_paths: Optional[List[str]] = None,
    ) -> FileTree:
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path), root_path
        assert not root_path.endswith("/"), root_path

        extensions_tuple = tuple(extensions) if extensions is not None else ()

        path_filter_includes = PathFilter(
            include_paths, positive_or_negative=True
        )
        path_filter_excludes = PathFilter(
            exclude_paths, positive_or_negative=False
        )
        path_filter_dev_includes = PathFilter(
            dev_include_paths or [], positive_or_negative=True
        )
        root_level: int = root_path.count(os.sep)

        root_folder: Folder = Folder(root_path, ".", 0)
        folder_map: Dict[str, Folder] = {root_path: root_folder}

        count = 0

        for current_dir_full_path_, dirs, files in os.walk(
            root_path, topdown=True
        ):
            # ignored_dirs contains system exclusions that no path filter can
            # override. Stop scanning these directories before applying the
            # configurable filters.
            if current_dir_full_path_ in ignored_dirs:
                dirs[:] = []
                continue

            current_dir_rel_path_ = os.path.relpath(
                current_dir_full_path_, start=root_path
            )
            current_dir_rel_path_ = (
                (current_dir_rel_path_ + "/")
                if current_dir_rel_path_ != "."
                else ""
            )
            current_dir_rel_path = SDocRelativePath(current_dir_rel_path_)

            directory_is_excluded = path_filter_excludes.match(
                current_dir_rel_path.relative_path_posix
            )
            directory_is_dev_included = (
                dev_include_paths is not None
                and len(dev_include_paths) > 0
                and path_filter_dev_includes.match(
                    current_dir_rel_path.relative_path_posix
                )
            )
            directory_may_contain_dev_include = (
                path_filter_dev_includes.may_match_descendant(
                    current_dir_rel_path.relative_path_posix
                )
            )
            # An excluded parent must remain open while it leads to a selected
            # development path. Unrelated excluded branches stay pruned.
            if (
                directory_is_excluded
                and not directory_is_dev_included
                and not directory_may_contain_dev_include
            ):
                dirs[:] = []
                continue

            count += 1

            filtered_dirs: List[str] = []
            for child_dir_ in dirs:
                if child_dir_ in ("output", "Output"):
                    child_relative_path = "/".join(
                        filter(
                            None,
                            (
                                current_dir_rel_path.relative_path_posix.rstrip(
                                    "/"
                                ),
                                child_dir_,
                            ),
                        )
                    )
                    if not path_filter_dev_includes.match(
                        child_relative_path
                    ) and not path_filter_dev_includes.may_match_descendant(
                        child_relative_path
                    ):
                        continue
                filtered_dirs.append(child_dir_)
            dirs[:] = filtered_dirs
            dirs.sort(key=alphanumeric_sort)

            current_root_path_level: int = (
                current_dir_full_path_.count(os.sep) - root_level
            )

            current_tree = folder_map.setdefault(
                current_dir_full_path_,
                Folder(
                    current_dir_full_path_,
                    current_dir_rel_path.relative_path,
                    current_root_path_level,
                ),
            )

            for file in files:
                if len(extensions_tuple) > 0 and not file.endswith(
                    extensions_tuple
                ):
                    continue

                full_file_path = os.path.join(current_dir_full_path_, file)

                # A known edge case: A file is found by os.walk(), but it is a
                # Linux pipe file which fails an os.path.isfile() check.
                # It seems to be safe to ignore this and possibly other cases
                # here without writing any test for this case.
                if not os.path.isfile(full_file_path):  # pragma: no cover
                    continue

                rel_file_path = SDocRelativePath(
                    os.path.join(current_dir_rel_path.relative_path, file)
                )

                file_is_excluded = path_filter_excludes.match(
                    rel_file_path.relative_path_posix
                )
                file_is_dev_included = (
                    dev_include_paths is not None
                    and len(dev_include_paths) > 0
                    and path_filter_dev_includes.match(
                        rel_file_path.relative_path_posix
                    )
                )
                if file_is_excluded and not file_is_dev_included:
                    continue

                if file_is_dev_included or path_filter_includes.match(
                    rel_file_path.relative_path_posix
                ):
                    # TODO: For now, ignore the binary files but one day a user
                    # might want to create a Relation to a binary file like a
                    # published PDF.
                    if is_binary_file(full_file_path):
                        print(  # noqa: T201
                            f"warning: Skip reading binary file {full_file_path}"
                        )
                        continue

                    current_tree.files.append(
                        File(
                            current_tree.level + 1,
                            full_file_path,
                            rel_file_path,
                        )
                    )

            def file_path_sort_key(lhs: File, rhs: File) -> int:
                return (rhs.file_name < lhs.file_name) - (
                    lhs.file_name < rhs.file_name
                )

            sort_key = functools.cmp_to_key(file_path_sort_key)
            current_tree.files.sort(key=sort_key)

            if len(current_tree.files) > 0:
                current_tree.has_sdoc_content = True

            if current_dir_full_path_ == root_path:
                continue

            current_parent_path = os.path.dirname(current_dir_full_path_)

            # Top-down search assumes we have seen the parent before.
            assert current_parent_path in folder_map, (
                current_parent_path,
                folder_map,
            )

            current_parent_folder: Folder = folder_map[current_parent_path]
            current_tree.set_parent_folder(current_parent_folder)
            if current_tree.has_sdoc_content:
                parent_folder_cursor: Optional[Folder] = current_parent_folder
                while (
                    parent_folder_cursor
                    and not parent_folder_cursor.has_sdoc_content
                ):
                    parent_folder_cursor.has_sdoc_content = True
                    parent_folder_cursor = parent_folder_cursor.parent_folder

            current_parent_folder.add_subfolder_tree(current_tree)

        print(f"Scanned {count} directories.")  # noqa: T201

        file_tree_structure = FileTree(
            root_folder_or_file=folder_map[root_path]
        )
        return file_tree_structure


class PathFinder:
    @staticmethod
    def find_directories(
        root_path: str,
        directory: str,
        include_paths: List[str],
        exclude_paths: List[str],
        ignored_dirs: Optional[List[str]] = None,
        dev_include_paths: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Find named directories using two levels of path exclusion.

        Project exclusions may be overridden by ``dev_include_paths`` so a
        developer can load local test content. ``ignored_dirs`` is reserved
        for system directories and is always final. This is the same boundary
        used when document files are selected.
        """
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)

        path_filter_includes = PathFilter(
            include_paths, positive_or_negative=True
        )
        path_filter_excludes = PathFilter(
            exclude_paths, positive_or_negative=False
        )
        path_filter_dev_includes = PathFilter(
            dev_include_paths or [], positive_or_negative=True
        )
        ignored_dirs = ignored_dirs or []

        directories = []
        count = 0

        # Declare str type to make os.path.relpath type checking happy.
        current_dir_full_path_: str
        for current_dir_full_path_, dirs, _ in os.walk(root_path, topdown=True):
            # Apply the system boundary before either selectable filter.
            if current_dir_full_path_ in ignored_dirs:
                dirs[:] = []
                continue

            count += 1

            current_root_relative_path: str = os.path.relpath(
                current_dir_full_path_, start=root_path
            )
            current_root_relative_path = (
                current_root_relative_path + "/"
                if current_root_relative_path != "."
                else ""
            )
            current_root_relative_path_posix = SDocRelativePath(
                current_root_relative_path
            ).relative_path_posix

            normal_path_is_selected = True
            dev_path_is_selected = False
            path_may_contain_dev_include = False
            if len(current_root_relative_path) > 0:
                normal_path_is_selected = not path_filter_excludes.match(
                    current_root_relative_path_posix
                ) and path_filter_includes.match(
                    current_root_relative_path_posix
                )
                dev_path_is_selected = (
                    dev_include_paths is not None
                    and len(dev_include_paths) > 0
                    and path_filter_dev_includes.match(
                        current_root_relative_path_posix
                    )
                )
                path_may_contain_dev_include = (
                    path_filter_dev_includes.may_match_descendant(
                        current_root_relative_path_posix
                    )
                )
                if (
                    not normal_path_is_selected
                    and not dev_path_is_selected
                    and not path_may_contain_dev_include
                ):
                    dirs[:] = []
                    continue

            filtered_dirs: List[str] = []
            for child_dir_ in dirs:
                if child_dir_.startswith("__") or child_dir_ in (
                    "build",
                    "output",
                    "Output",
                    "tests",
                ):
                    child_relative_path = "/".join(
                        filter(
                            None,
                            (
                                current_root_relative_path_posix.rstrip("/"),
                                child_dir_,
                            ),
                        )
                    )
                    if not path_filter_dev_includes.match(
                        child_relative_path
                    ) and not path_filter_dev_includes.may_match_descendant(
                        child_relative_path
                    ):
                        continue
                filtered_dirs.append(child_dir_)
            dirs[:] = filtered_dirs

            if os.path.basename(current_dir_full_path_) == directory and (
                normal_path_is_selected or dev_path_is_selected
            ):
                directories.append(current_dir_full_path_)

        print(f"Scanned {count} directories.")  # noqa: T201

        return directories
