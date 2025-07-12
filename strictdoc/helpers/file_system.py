import os
import platform
import shutil
import tempfile
from pathlib import Path
from typing import Optional


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


def get_portable_temp_dir() -> Path:
    return Path(
        "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
    )
