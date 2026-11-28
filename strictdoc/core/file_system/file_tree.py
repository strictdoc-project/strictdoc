import os
import stat
from operator import attrgetter
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union

from typing_extensions import TypeAlias

from strictdoc.core.file_system.file_listing_cache import (
    CACHE_FORMAT_VERSION,
    CachedFile,
    CachedFolder,
    FileListingCache,
    create_cached_file,
)
from strictdoc.helpers.path_filter import PathFilter
from strictdoc.helpers.paths import SDocRelativePath, path_to_posix_path
from strictdoc.helpers.sorting import alphanumeric_sort

FileOrFolderEntry: TypeAlias = Union["File", "Folder"]


class File:
    def __init__(self, level: int, full_path: str, rel_path: SDocRelativePath):
        # No check that the path exists: the callers pass paths that they
        # found on disk, and a check would cost a stat() call for every file
        # on every export.
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
        # No check that the path exists: the callers pass paths that they
        # found on disk, and a check would cost a stat() call for every folder
        # on every export.
        assert os.path.isabs(full_path)
        assert isinstance(rel_path, str)

        self.full_path: str = full_path
        self.rel_path: str = rel_path if rel_path != "." else ""
        self.mount_folder: str = os.path.basename(self.full_path)
        # os.path.normpath() changes the last component of a path only if
        # the path ends with a separator, ".", or "..". For other paths, for
        # example all folders that os.walk() finds, skip the slow call.
        self.folder_name: str = (
            self.mount_folder
            if self.mount_folder not in ("", ".", "..")
            else os.path.basename(os.path.normpath(full_path))
        )
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
        path_to_cache_dir: Optional[str] = None,
    ) -> FileTree:
        """
        Find the files below root_path that pass the filters.

        With path_to_cache_dir, the scan of each folder is stored, and a later
        search reuses the scans of the unchanged folders. See
        file_listing_cache.py.
        """
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
        listing_cache = FileListingCache.create(
            path_to_cache_dir,
            root_path,
            extensions,
            key=(
                CACHE_FORMAT_VERSION,
                root_path,
                tuple(ignored_dirs),
                extensions_tuple,
                tuple(include_paths),
                tuple(exclude_paths),
            ),
        )
        root_level: int = root_path.count(os.sep)
        # A Windows drive root, for example "C:\\", ends with a separator.
        root_prefix: str = (
            root_path if root_path.endswith(os.sep) else root_path + os.sep
        )

        root_folder: Folder = Folder(root_path, ".", 0)
        folder_map: Dict[str, Folder] = {root_path: root_folder}

        count = 0

        # The scan of a folder leaves out its ignored and excluded subfolders,
        # so a folder from the cache needs no filter check. Only the root
        # folder is checked here.
        folders_to_walk: List[str] = (
            [root_path]
            if root_path not in ignored_dirs
            and not path_filter_excludes.match("")
            else []
        )

        # Depth-first, with the subfolders in their sorted order, as
        # os.walk(topdown=True) walks.
        while len(folders_to_walk) > 0:
            current_dir_full_path_ = folders_to_walk.pop()

            # Every folder path below the root starts with the root prefix.
            # Cutting it off gives the same result as os.path.relpath(),
            # without the cost of normalizing both paths for every folder.
            current_dir_rel_path_ = (
                (current_dir_full_path_[len(root_prefix) :] + "/")
                if current_dir_full_path_ != root_path
                else ""
            )
            current_dir_rel_path = SDocRelativePath(current_dir_rel_path_)

            scanned_folder = listing_cache.get(current_dir_full_path_)
            if scanned_folder is None:
                scan_result = FileFinder._scan_folder(
                    current_dir_full_path_,
                    current_dir_rel_path.relative_path_posix,
                    ignored_dirs=ignored_dirs,
                    extensions_tuple=extensions_tuple,
                    path_filter_includes=path_filter_includes,
                    path_filter_excludes=path_filter_excludes,
                )
                if scan_result is None:
                    # Like os.walk(), skip a folder that cannot be listed.
                    continue
                scanned_folder, can_be_cached = scan_result
                if can_be_cached:
                    listing_cache.put(current_dir_full_path_, scanned_folder)
            else:
                listing_cache.put(current_dir_full_path_, scanned_folder)

            count += 1

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

            for file_ in scanned_folder.files:
                full_file_path = os.path.join(
                    current_dir_full_path_, file_.name
                )

                # TODO: For now, ignore the binary files but one day a user
                # might want to create a Relation to a binary file like a
                # published PDF.
                if file_.is_binary:
                    print(  # noqa: T201
                        f"warning: Skip reading binary file {full_file_path}"
                    )
                    continue

                # The folder path is empty or ends with "/", so concatenation
                # gives the same result as os.path.join(), but faster.
                current_tree.files.append(
                    File(
                        current_tree.level + 1,
                        full_file_path,
                        SDocRelativePath(
                            current_dir_rel_path.relative_path + file_.name
                        ),
                    )
                )

            current_tree.files.sort(key=attrgetter("file_name"))

            if len(current_tree.files) > 0:
                current_tree.has_sdoc_content = True

            for subfolder_ in reversed(scanned_folder.subfolders):
                folders_to_walk.append(
                    os.path.join(current_dir_full_path_, subfolder_)
                )

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

        listing_cache.save()

        file_tree_structure = FileTree(
            root_folder_or_file=folder_map[root_path]
        )
        return file_tree_structure

    @staticmethod
    def _scan_folder(
        folder_path: str,
        folder_rel_path_posix: str,
        *,
        ignored_dirs: List[str],
        extensions_tuple: Tuple[str, ...],
        path_filter_includes: PathFilter,
        path_filter_excludes: PathFilter,
    ) -> Optional[Tuple[CachedFolder, bool]]:
        """
        List a folder and apply the filters to its entries.

        Return the scan and whether the cache can store it, or None if the
        folder cannot be listed. The scan does not depend on anything outside
        the folder's entries and the search settings, except for a symbolic
        link, so a folder with a symbolic link is not stored.
        """
        try:
            folder_mtime_ns = os.stat(folder_path).st_mtime_ns
            entries = list(os.scandir(folder_path))
        except OSError:
            return None

        can_be_cached = True
        dirs: List[str] = []
        linked_dirs: Set[str] = set()
        files: List[str] = []
        for entry_ in entries:
            try:
                is_symlink = entry_.is_symlink()
                is_dir = entry_.is_dir()
            except OSError:
                is_symlink = False
                is_dir = False
            if is_symlink:
                can_be_cached = False
            if is_dir:
                dirs.append(entry_.name)
                if is_symlink:
                    linked_dirs.add(entry_.name)
            else:
                files.append(entry_.name)

        # Skip the folders that cannot contain an included file, for example
        # build/ or .venv/ when only /docs/ is included. Like os.walk(), do
        # not walk into a symbolic link to a folder.
        subfolders = [
            d
            for d in dirs
            if d not in ("output", "Output")
            and d not in linked_dirs
            and path_filter_includes.may_match_inside(
                f"{folder_rel_path_posix}{d}/"
            )
            and os.path.join(folder_path, d) not in ignored_dirs
            and not path_filter_excludes.match(
                f"{folder_rel_path_posix}{path_to_posix_path(d)}/"
            )
        ]
        # Most folders have at most one subfolder, and the sort key is a
        # regex split of each name.
        if len(subfolders) > 1:
            subfolders.sort(key=alphanumeric_sort)

        cached_files: List[CachedFile] = []
        for file_ in files:
            if len(extensions_tuple) > 0 and not file_.endswith(
                extensions_tuple
            ):
                continue

            # The folder path is empty or ends with "/". The POSIX path of the
            # folder is already converted, so only the file name needs the
            # conversion.
            rel_file_path_posix = folder_rel_path_posix + path_to_posix_path(
                file_
            )

            # Most found files are not included, so the include filter runs
            # first. The exclude filter then runs only for the included files.
            if not path_filter_includes.match(
                rel_file_path_posix
            ) or path_filter_excludes.match(rel_file_path_posix):
                continue

            # A known edge case: a found file is a Linux pipe file, which is
            # not a regular file. The check runs after the path filters, so
            # only the included files cost a stat() call.
            full_file_path = os.path.join(folder_path, file_)
            try:
                file_stat = os.stat(full_file_path)
            except OSError:  # pragma: no cover
                continue
            if not stat.S_ISREG(file_stat.st_mode):  # pragma: no cover
                continue

            cached_files.append(
                create_cached_file(full_file_path, file_, file_stat)
            )

        return (
            CachedFolder(
                mtime_ns=folder_mtime_ns,
                subfolders=subfolders,
                files=cached_files,
            ),
            can_be_cached,
        )


class PathFinder:
    @staticmethod
    def find_directories(
        root_path: str,
        directory: str,
        include_paths: List[str],
        exclude_paths: List[str],
    ) -> List[str]:
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)

        path_filter_includes = PathFilter(
            include_paths, positive_or_negative=True
        )
        path_filter_excludes = PathFilter(
            exclude_paths, positive_or_negative=False
        )

        directories = []
        count = 0

        # Declare str type to make os.path.relpath type checking happy.
        current_dir_full_path_: str
        for current_dir_full_path_, dirs, _ in os.walk(root_path, topdown=True):
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

            if len(current_root_relative_path) > 0:
                if path_filter_excludes.match(
                    current_root_relative_path_posix
                ) or not path_filter_includes.match(
                    current_root_relative_path_posix
                ):
                    dirs[:] = []
                    continue

            dirs[:] = [
                d
                for d in dirs
                if not d.startswith("__")
                and d not in ("build", "output", "Output", "tests")
            ]

            if os.path.basename(current_dir_full_path_) == directory:
                directories.append(current_dir_full_path_)

        print(f"Scanned {count} directories.")  # noqa: T201

        return directories
