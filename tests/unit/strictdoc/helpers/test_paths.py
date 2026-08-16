from strictdoc.helpers.paths import shorten_path


def test_short_path_is_unchanged():
    assert shorten_path("file.py") == "file.py"
    assert shorten_path("src/file.py") == "src/file.py"


def test_path_at_threshold_is_unchanged():
    path = "tests/integration/features/source_code_traceability/file.py"
    assert shorten_path(path) == path


def test_deep_path_is_collapsed_to_first_and_last_segment():
    path = (
        "tests/integration/features/source_code_traceability/"
        "_language_parsers/python/file.py"
    )
    assert shorten_path(path) == "tests/.../file.py"


def test_windows_path_is_collapsed_using_posix_separators():
    path = "tests\\integration\\features\\a\\b\\c\\file.py"
    assert shorten_path(path) == "tests/.../file.py"
