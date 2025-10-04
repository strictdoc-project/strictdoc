import pytest

from strictdoc import environment
from strictdoc.server.helpers.http import get_etag


def test_get_etag_file_does_not_exist():
    with pytest.raises(FileNotFoundError):
        get_etag("DOES-NOT-EXIST")

    # Use a known StrictDoc location to trigger a "not a file" error.
    with pytest.raises(RuntimeError):
        get_etag(environment.get_path_to_html_templates())
