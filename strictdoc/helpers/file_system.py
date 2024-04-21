# mypy: disable-error-code="no-untyped-def"
import hashlib
import os
import platform
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Optional


def sync_dir(src_dir, dst_dir, message: Optional[str]):
    assert os.path.isabs(src_dir), f"Expected {src_dir} to be an absolute path"
    assert os.path.isdir(src_dir), f"Expected {src_dir} to be a directory"

    Path(dst_dir).mkdir(parents=True, exist_ok=True)

    # First, collect all source files to be copied.
    source_files = []
    for root, _, filenames in os.walk(src_dir, topdown=True):
        for filename in filenames:
            full_path_to_file = os.path.join(root, filename)
            relative_path_to_file_dir = os.path.relpath(root, start=src_dir)
            if relative_path_to_file_dir == ".":
                relative_path_to_file_dir = ""
            source_files.append(
                (
                    filename,
                    full_path_to_file,
                    relative_path_to_file_dir,
                )
            )

    if len(source_files) == 0:
        return

    # Print progress message.
    if message is not None:
        print(f"{message}: {len(source_files)} files", end="")  # noqa: T201

    # Iterate through the files to be copied and copy them one by one.
    skipped = 0
    for (
        filename,
        full_path_to_file,
        relative_path_to_file_dir,
    ) in source_files:
        full_path_to_destination_dir = os.path.join(
            dst_dir, relative_path_to_file_dir
        )
        Path(full_path_to_destination_dir).mkdir(parents=True, exist_ok=True)
        full_path_to_destination_file = os.path.join(
            full_path_to_destination_dir, filename
        )

        # StrictDoc: We don't want to copy files if they are not newer.
        if not os.path.isfile(
            full_path_to_destination_file
        ) or os.path.getmtime(full_path_to_file) > os.path.getmtime(
            full_path_to_destination_file
        ):
            shutil.copyfile(full_path_to_file, full_path_to_destination_file)
        else:
            skipped += 1

    if message is not None:
        if skipped > 0:
            print(  # noqa: T201
                f" ({skipped} files skipped as non-modified).", flush=True
            )
        else:
            print(".", flush=True)  # noqa: T201


def get_portable_temp_dir():
    return Path(
        "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
    )


def get_etag(file_path):
    """
    This implementation is taken from StackOverflow. The implementation itself
    is taken from Starlette.
    https://stackoverflow.com/a/76263874/598057

    NOTE: The Starlette's version is async and uses anyio.
    """
    assert os.path.isfile(file_path)
    stat_result = os.stat(file_path)
    mode = stat_result.st_mode
    if not stat.S_ISREG(mode):
        raise RuntimeError(f"File at path {file_path} is not a file.")

    # calculate the etag based on file size and last modification time
    etag_base = str(stat_result.st_mtime) + "-" + str(stat_result.st_size)
    etag = hashlib.md5(etag_base.encode()).hexdigest()
    return etag
