"""
A cache of the folder scans of FileFinder.

Use case: static export and server, run again without changes to the folder
structure. FileFinder walks every folder below a search root. The result of
the scan of one folder depends only on the names of the folder's direct
entries and on the search settings. The mtime of a folder changes when an
entry of the folder is added, removed, or renamed. If the mtime of a folder is
the same as in the previous run, FileFinder reuses the stored result of the
folder: it does not list the folder or match the names against the filters.

Three cases need more care:

- Coarse timestamps: some file systems store mtimes in steps of 1-2 s. A
  folder could change in the same step in which it was scanned, and keep its
  mtime. A folder whose mtime is less than RACY_SECONDS before the time the
  cache was written is therefore scanned again. The untracked cache of git
  uses the same rule.
- Binary files: FileFinder skips binary files, and a file can become binary
  without a change of its name. The cache stores the mtime and the size of
  each file with the result of the binary check, and the check runs again
  only for a file with a changed mtime or size.
- Symbolic links: the target of a link can change without a change of the
  folder that holds the link. A folder that holds a symbolic link is never
  stored.
"""

import hashlib
import os
import pickle
import stat
import tempfile
import time
from typing import Dict, List, NamedTuple, Optional, Tuple

from strictdoc.helpers.file_system import is_binary_file

# A folder with an mtime closer than this to the time the cache was written is
# scanned again.
RACY_SECONDS = 2

# Change this number when the meaning of the stored data changes.
CACHE_FORMAT_VERSION = 1

CacheKey = Tuple[object, ...]


class CachedFile(NamedTuple):
    name: str
    mtime_ns: int
    size: int
    is_binary: bool


class CachedFolder(NamedTuple):
    mtime_ns: int
    # The subfolders to walk into, after all filters, in the order of the
    # walk.
    subfolders: List[str]
    # The files that passed the filters and are regular files.
    files: List[CachedFile]


class FileListingCache:
    def __init__(self, path_to_cache: Optional[str], key: CacheKey) -> None:
        self.path_to_cache: Optional[str] = path_to_cache
        self.key: CacheKey = key
        self.folders: Dict[str, CachedFolder] = {}
        self.new_folders: Dict[str, CachedFolder] = {}
        self.written_ns: int = 0
        # A folder that is scanned again only because of its recent mtime
        # needs a new cache write, so that a later run can trust it.
        self.has_recent_folders: bool = False
        if path_to_cache is not None:
            self._load()

    @staticmethod
    def create(
        path_to_cache_dir: Optional[str],
        root_path: str,
        extensions: Optional[List[str]],
        key: CacheKey,
    ) -> "FileListingCache":
        """
        Create the cache of one search. Without a cache folder, the cache
        stores nothing.
        """
        if path_to_cache_dir is None:
            return FileListingCache(None, key)
        # One file per search root and set of extensions, so that the
        # document search and the source file search do not overwrite each
        # other's cache.
        file_name = hashlib.md5(
            repr((root_path, extensions)).encode("utf-8")
        ).hexdigest()
        return FileListingCache(
            os.path.join(path_to_cache_dir, "file_listing", file_name), key
        )

    def get(self, folder_path: str) -> Optional[CachedFolder]:
        """
        Return the stored scan of a folder, or None if the folder must be
        scanned.
        """
        cached_folder = self.folders.get(folder_path)
        if cached_folder is None:
            return None
        try:
            folder_mtime_ns = os.stat(folder_path).st_mtime_ns
        except OSError:
            return None
        if folder_mtime_ns != cached_folder.mtime_ns:
            return None
        if folder_mtime_ns >= self.written_ns - RACY_SECONDS * 1_000_000_000:
            self.has_recent_folders = True
            return None
        return self._revalidate_files(folder_path, cached_folder)

    def put(self, folder_path: str, cached_folder: CachedFolder) -> None:
        self.new_folders[folder_path] = cached_folder

    def save(self) -> None:
        """
        Write the folders of this run if they differ from the stored ones.
        The folders that this run did not walk are dropped.
        """
        if self.path_to_cache is None:
            return
        if not self.has_recent_folders and self.new_folders == self.folders:
            return
        path_to_cache_dir = os.path.dirname(self.path_to_cache)
        os.makedirs(path_to_cache_dir, exist_ok=True)
        content = {
            "key": self.key,
            "written_ns": time.time_ns(),
            "folders": self.new_folders,
        }
        # A temporary file with a unique name and a rename: an export and a
        # server can write the same cache at the same time.
        file_descriptor, path_to_tmp_file = tempfile.mkstemp(
            dir=path_to_cache_dir
        )
        try:
            with os.fdopen(file_descriptor, "wb") as cache_file:
                pickle.dump(content, cache_file, pickle.HIGHEST_PROTOCOL)
            os.replace(path_to_tmp_file, self.path_to_cache)
        except BaseException:
            os.unlink(path_to_tmp_file)
            raise

    def _load(self) -> None:
        assert self.path_to_cache is not None
        try:
            with open(self.path_to_cache, "rb") as cache_file:
                content = pickle.load(cache_file)
        except (OSError, pickle.UnpicklingError, EOFError, AttributeError):
            return
        if not isinstance(content, dict) or content.get("key") != self.key:
            return
        self.folders = content["folders"]
        self.written_ns = content["written_ns"]

    @staticmethod
    def _revalidate_files(
        folder_path: str, cached_folder: CachedFolder
    ) -> Optional[CachedFolder]:
        """
        Check the stored files of an unchanged folder. Return the folder with
        a new binary check for each changed file, or None if a file is not a
        regular file anymore.
        """
        updated_files: Optional[List[CachedFile]] = None
        for index_, file_ in enumerate(cached_folder.files):
            full_file_path = os.path.join(folder_path, file_.name)
            try:
                file_stat = os.stat(full_file_path)
            except OSError:
                return None
            if not stat.S_ISREG(file_stat.st_mode):
                return None
            if (
                file_stat.st_mtime_ns == file_.mtime_ns
                and file_stat.st_size == file_.size
            ):
                continue
            if updated_files is None:
                updated_files = list(cached_folder.files)
            updated_files[index_] = create_cached_file(
                full_file_path, file_.name, file_stat
            )
        if updated_files is None:
            return cached_folder
        return cached_folder._replace(files=updated_files)


def create_cached_file(
    full_file_path: str, name: str, file_stat: os.stat_result
) -> CachedFile:
    return CachedFile(
        name=name,
        mtime_ns=file_stat.st_mtime_ns,
        size=file_stat.st_size,
        is_binary=is_binary_file(full_file_path),
    )
