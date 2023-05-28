import pytest

from strictdoc.helpers.path_filter import validate_mask


def test_case_01_empty_mask_allows_everything():
    # Does not raise is success.
    validate_mask("docs/")
    validate_mask("Docs/")

    with pytest.raises(SyntaxError) as exc_info:
        validate_mask("")
    assert "Path mask must not be empty." in exc_info.value.args[0]

    with pytest.raises(SyntaxError) as exc_info:
        validate_mask(".")
    assert (
        "Path mask must start with an alphanumeric character or "
        "a wildcard symbol '*'."
    ) in exc_info.value.args[0]

    with pytest.raises(SyntaxError) as exc_info:
        validate_mask("foo//")
    assert (
        "Path mask must not contain double slashes." in exc_info.value.args[0]
    )

    with pytest.raises(SyntaxError) as exc_info:
        validate_mask("bar\\\\")
    assert (
        "Path mask must not contain double slashes." in exc_info.value.args[0]
    )

    with pytest.raises(SyntaxError) as exc_info:
        validate_mask("***")
    assert "Invalid wildcard: '***'." in exc_info.value.args[0]

    with pytest.raises(SyntaxError) as exc_info:
        validate_mask("a[")
    assert (
        "Path mask must not contain any of the special characters: "
        "('[', ']', '(', ')', '{', '}', '?', '+', '!')."
    ) in exc_info.value.args[0]
