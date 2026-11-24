import os
from pathlib import Path

from strictdoc.helpers.file_system import sync_dir

OLD_MTIME = 1_000_000_000
NEW_MTIME = 2_000_000_000


def _write_file(path: Path, content: str, mtime: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    os.utime(path, (mtime, mtime))


def test_sync_dir_copies_missing_files(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    _write_file(src_dir / "file.txt", "root", OLD_MTIME)
    _write_file(src_dir / "nested" / "file.txt", "nested", OLD_MTIME)

    sync_dir(str(src_dir), str(dst_dir), message=None)

    assert (dst_dir / "file.txt").read_text() == "root"
    assert (dst_dir / "nested" / "file.txt").read_text() == "nested"


def test_sync_dir_skips_file_with_same_size_and_newer_destination(
    tmp_path: Path,
) -> None:
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    _write_file(src_dir / "file.txt", "AAAA", OLD_MTIME)
    _write_file(dst_dir / "file.txt", "BBBB", NEW_MTIME)

    sync_dir(str(src_dir), str(dst_dir), message=None)

    assert (dst_dir / "file.txt").read_text() == "BBBB"


def test_sync_dir_copies_file_with_newer_source(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    _write_file(src_dir / "file.txt", "AAAA", NEW_MTIME)
    _write_file(dst_dir / "file.txt", "BBBB", OLD_MTIME)

    sync_dir(str(src_dir), str(dst_dir), message=None)

    assert (dst_dir / "file.txt").read_text() == "AAAA"


def test_sync_dir_copies_file_with_different_size_and_older_source(
    tmp_path: Path,
) -> None:
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    _write_file(src_dir / "file.txt", "AAAA", OLD_MTIME)
    _write_file(dst_dir / "file.txt", "BB", NEW_MTIME)

    sync_dir(str(src_dir), str(dst_dir), message=None)

    assert (dst_dir / "file.txt").read_text() == "AAAA"
