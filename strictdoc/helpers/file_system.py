import codecs
import os
import platform
import shutil
import stat
import tempfile
from contextlib import contextmanager
from io import BufferedReader, TextIOWrapper
from pathlib import Path
from typing import Iterator, Optional

UTF8_BOM_BYTES = codecs.BOM_UTF8  # b'\xef\xbb\xbf'


def sync_dir(src_dir: str, dst_dir: str, message: Optional[str]) -> None:
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

        if _is_destination_file_up_to_date(
            full_path_to_file, full_path_to_destination_file
        ):
            skipped += 1
        else:
            shutil.copyfile(full_path_to_file, full_path_to_destination_file)

    if message is not None:
        if skipped > 0:
            print(  # noqa: T201
                f" ({skipped} files skipped as non-modified).", flush=True
            )
        else:
            print(".", flush=True)  # noqa: T201


def _is_destination_file_up_to_date(src_file: str, dst_file: str) -> bool:
    """
    Check if the destination file can be kept instead of copying the source.

    The destination file is up to date if it is not older than the source file
    and has the same size. The size check catches an outdated destination file
    that is newer than the source file, for example after an interrupted copy
    or after a restore of a source file with its original modification time.
    """
    try:
        dst_stat = os.stat(dst_file)
    except FileNotFoundError:
        return False
    if not stat.S_ISREG(dst_stat.st_mode):
        return False
    src_stat = os.stat(src_file)
    return (
        src_stat.st_mtime <= dst_stat.st_mtime
        and src_stat.st_size == dst_stat.st_size
    )


def get_portable_temp_dir() -> Path:
    return Path(
        "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
    )


@contextmanager
def file_open_read_utf8(file_path: str) -> Iterator[TextIOWrapper]:
    # utf-8-sig is important here because it strips the UTF BOM markers
    # from the beginning of source files created by some Windows tools.
    with open(file_path, encoding="utf-8-sig") as file_:
        yield file_


@contextmanager
def file_open_read_bytes(file_path: str) -> Iterator[BufferedReader]:
    with open(file_path, "rb") as raw_file:
        start = raw_file.read(len(UTF8_BOM_BYTES))
        if start != UTF8_BOM_BYTES:
            # No BOM -> rewind to beginning.
            raw_file.seek(0)
        yield raw_file


def is_binary_file(path: str, sample_size: int = 8192) -> bool:
    with open(path, "rb") as f:
        return b"\x00" in f.read(sample_size)
