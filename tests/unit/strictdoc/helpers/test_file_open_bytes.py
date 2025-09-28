import os
import tempfile
from io import BufferedReader

import pytest

from strictdoc.helpers.file_system import UTF8_BOM_BYTES, file_open_read_bytes


@pytest.mark.parametrize(
    "initial_bytes,expected_bytes",
    [
        (b"", b""),
        (b"A", b"A"),
        (b"AB", b"AB"),
        (UTF8_BOM_BYTES + b"Hello", b"Hello"),
        (b"Hello", b"Hello"),
    ],
)
def test_file_open_read_bytes(initial_bytes, expected_bytes):
    tmp_file = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    tmp_path = tmp_file.name

    try:
        tmp_file.write(initial_bytes)
        tmp_file.close()

        with file_open_read_bytes(tmp_path) as f:
            assert isinstance(f, BufferedReader)
            content = f.read()
            assert content == expected_bytes
    finally:
        os.remove(tmp_path)
