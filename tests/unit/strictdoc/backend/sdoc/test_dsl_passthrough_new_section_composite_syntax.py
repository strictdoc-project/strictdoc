import pytest

from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.helpers.exception import StrictDocException


def test_010_multiple_sections():
    input_sdoc = """\
[DOCUMENT]
TITLE: Test Doc

[SECTION]
TITLE: Test Section

[SECTION]
TITLE: Test Section (Nested)

[SECTION]
TITLE: Test Section (Sub-nested)

[REQUIREMENT]
STATEMENT: >>>
This is a statement 1
This is a statement 2
This is a statement 3
<<<

[/SECTION]

[/SECTION]

[/SECTION]
"""

    reader = SDReader()

    with pytest.raises(Exception) as exc_info:
        _ = reader.read(input_sdoc)

    assert exc_info.type is StrictDocException
    assert (
        "[SECTION] elements are no longer supported by StrictDoc. "
        "See the migration guide for more details:"
    ) in exc_info.value.args[0]
