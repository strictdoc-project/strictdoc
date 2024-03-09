import hashlib
import os
import tempfile

from strictdoc.helpers.md5 import get_file_md5


class PickleCache:
    @staticmethod
    def get_cached_file_path(file_path: str, path_to_output_root: str):
        path_to_tmp_dir = tempfile.gettempdir()

        full_path_to_file = (
            file_path
            if os.path.abspath(file_path)
            else os.path.abspath(file_path)
        )

        file_md5 = get_file_md5(file_path)

        # File name contains an MD5 hash of its full path to ensure the
        # uniqueness of the cached items. Additionally, the unique file name
        # contains a full path to the output root to prevent collisions
        # between StrictDoc invocations running against the same set of SDoc
        # files in parallel.
        unique_identifier = path_to_output_root + full_path_to_file
        unique_identifier_md5 = hashlib.md5(
            unique_identifier.encode("utf-8")
        ).hexdigest()
        file_name = os.path.basename(full_path_to_file)
        file_name += "_" + unique_identifier_md5 + "_" + file_md5

        path_to_cached_file = os.path.join(
            path_to_tmp_dir,
            "strictdoc_cache",
            file_name,
        )

        return path_to_cached_file
