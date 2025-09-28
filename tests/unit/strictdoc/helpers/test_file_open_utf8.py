import os
import tempfile
from io import TextIOWrapper

import pytest

from strictdoc.helpers.file_system import UTF8_BOM_BYTES, file_open_read_utf8

UTF8_BOM_STR = UTF8_BOM_BYTES.decode("utf-8")


@pytest.mark.parametrize(
    "initial_text,expected_text",
    [
        ("", ""),
        ("A", "A"),
        (UTF8_BOM_STR + "Hello", "Hello"),
        ("Hello", "Hello"),
    ],
)
def test_file_open_read_utf8(initial_text, expected_text):
    tmp_file = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False
    )
    tmp_path = tmp_file.name

    try:
        tmp_file.write(initial_text)
        tmp_file.close()

        with file_open_read_utf8(tmp_path) as f:
            assert isinstance(f, TextIOWrapper)
            content = f.read()
            assert content == expected_text
    finally:
        os.remove(tmp_path)
