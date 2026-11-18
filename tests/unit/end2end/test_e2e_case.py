from unittest.mock import Mock, patch

import pytest
from seleniumbase import BaseCase

from tests.end2end.e2e_case import E2ECase


def _assert_no_js_errors(base_case, *, exclude=None):  # noqa: ARG001
    base_case.driver.get_log("browser")
    raise AssertionError("Failed to load resource")


def test_assert_no_js_errors_preserves_no_buffer_space_in_exception():
    test_case = E2ECase()
    test_case.driver = Mock()
    test_case.driver.get_log.return_value = [
        {
            "level": "SEVERE",
            "message": (
                "http://localhost:5112/_static/content.css - Failed to load "
                "resource: net::ERR_NO_BUFFER_SPACE"
            ),
        }
    ]

    with patch.object(BaseCase, "assert_no_js_errors", _assert_no_js_errors):
        with pytest.raises(AssertionError, match="ERR_NO_BUFFER_SPACE"):
            test_case.assert_no_js_errors()


def test_assert_no_js_errors_does_not_change_other_failures():
    test_case = E2ECase()
    test_case.driver = Mock()
    test_case.driver.get_log.return_value = [
        {
            "level": "SEVERE",
            "message": "Uncaught TypeError: example",
        }
    ]

    with patch.object(BaseCase, "assert_no_js_errors", _assert_no_js_errors):
        with pytest.raises(AssertionError, match="^Failed to load resource$"):
            test_case.assert_no_js_errors()
