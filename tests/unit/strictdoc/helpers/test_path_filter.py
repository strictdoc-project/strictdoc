from strictdoc.helpers.path_filter import PathFilter


def test_case_01_empty_mask_allows_everything():
    path_filter = PathFilter([], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("hello.sdoc")
    assert path_filter.match("docs")
    assert path_filter.match("docs/something/test.sdoc")
    assert path_filter.match("docs/01_user_manual.sdoc")
    assert path_filter.match("docs/.sdoc")
    assert path_filter.match("sdoc")


def test_case_02_single_wildcard():
    mask = "*.sdoc"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("hello.sdoc")
    assert path_filter.match("docs/01_user_manual.sdoc")
    assert path_filter.match("docs/something/test.sdoc")
    assert path_filter.match("docs/.sdoc")

    # NEGATIVE
    assert not path_filter.match("docs")
    assert not path_filter.match("sdoc")


def test_case_03_single_wildcard():
    mask = "docs/*"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("docs/01_user_manual.sdoc")
    # This is possible, but it will be filtered by extension before this filter
    # anyway.
    assert path_filter.match("docs/01_user_manual_sdoc")
    assert path_filter.match("docs/.sdoc")

    # NEGATIVE
    assert not path_filter.match("docs.sdoc")
    assert not path_filter.match("docs")
    assert not path_filter.match("docs/something/test.sdoc")


def test_case_04_single_wildcard():
    mask = "docs/*.sdoc"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("docs/01_user_manual.sdoc")
    assert path_filter.match("docs/.sdoc")

    # NEGATIVE
    assert not path_filter.match("docs.sdoc")
    assert not path_filter.match("docs")
    assert not path_filter.match("docs/something/test.sdoc")
    assert not path_filter.match("docs/01_user_manual_sdoc")


def test_case_05_double_wildcard_and_single_wildcard():
    mask = "docs/**/*.sdoc"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("docs/foobar/01_user_manual.sdoc")
    assert path_filter.match("docs/foo/bar/01_user_manual.sdoc")

    # NEGATIVE
    assert not path_filter.match("docs/01_user_manual.sdoc")


def test_case_06_double_wildcard_only():
    mask = "docs/**"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("docs/foobar/01_user_manual.sdoc")
    assert path_filter.match("docs/01_user_manual.sdoc")

    # NEGATIVE
    assert not path_filter.match("01_user_manual.sdoc")


def test_case_07_double_wildcard_middle_no_slash_before():
    mask = "**docs/**"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("docs/foobar/01_user_manual.sdoc")
    assert path_filter.match("docs/01_user_manual.sdoc")
    assert path_filter.match("pydocs/01_user_manual.sdoc")
    assert path_filter.match("root/docs/01_user_manual.sdoc")

    # NEGATIVE
    assert not path_filter.match("01_user_manual.sdoc")


def test_case_08_double_wildcard_middle_slash_before():
    mask = "**/docs/**"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("root/docs/01_user_manual.sdoc")
    assert path_filter.match("foo/bar/docs/01_user_manual.sdoc")

    # NEGATIVE
    assert not path_filter.match("01_user_manual.sdoc")
    assert not path_filter.match("docs/foobar/01_user_manual.sdoc")
    assert not path_filter.match("docs/01_user_manual.sdoc")
    assert not path_filter.match("pydocs/01_user_manual.sdoc")


def test_case_09_multiple_dots_in_filename():
    mask = "*.sdoc"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("filename.part.sdoc")

    # NEGATIVE
    assert not path_filter.match("01_user_manual.sdoc.part")


def test_case_10_dot_slash_in_the_beginning():
    mask = "*.sdoc"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("./filename.part.sdoc")


def test_case_11_mask_starts_with_dot():
    path_filter = PathFilter(
        [".github/workflows/**"], positive_or_negative=True
    )

    # POSITIVE
    assert path_filter.match(".github/workflows/release.yml")


def test_case_13_ending_slashes_act_like_double_wildcards():
    mask = "build"
    path_filter = PathFilter([mask], positive_or_negative=False)

    # POSITIVE
    assert path_filter.match("build/foo")
    assert path_filter.match("build/foo.txt")
    assert path_filter.match("build/foo/bar")


def test_case_14_ending_slashes_act_like_double_wildcards():
    mask = "build/"
    path_filter = PathFilter([mask], positive_or_negative=False)

    # POSITIVE
    assert path_filter.match("build/foo")
    assert path_filter.match("build/foo.txt")
    assert path_filter.match("build/foo/bar")


def test_case_15_ending_slashes_act_like_double_wildcards():
    mask = "buil"
    path_filter = PathFilter([mask], positive_or_negative=False)

    assert not path_filter.match("build/foo")
    assert not path_filter.match("build/foo.txt")
    assert not path_filter.match("build/foo/bar")


def test_case_16_range_of_characters():
    mask = "*.py[codz]"
    path_filter = PathFilter([mask], positive_or_negative=False)

    assert path_filter.match("foo.pyc")
    assert path_filter.match("foo/foo.pyo")
    assert path_filter.match("foo/foo/foo.pyo")


def test_case_17_range_of_characters():
    mask = "fo[o-]"
    path_filter = PathFilter([mask], positive_or_negative=True)

    assert path_filter.match("foo")
    assert path_filter.match("fo-")
    assert path_filter.match("foo/fo-")

    assert not path_filter.match("foz")


def test_case_18_known_dollar_character_use():
    """
    The Jython files are generated as: example.py -> example$py.class.
    """

    mask = "*$py.class"
    path_filter = PathFilter([mask], positive_or_negative=False)

    assert path_filter.match("foo$py.class")
    assert path_filter.match("foo/foo$py.class")
    assert path_filter.match("foo/foo/foo$py.class")


def test_case_19_parentheses():
    mask = "tree(not_in_use).css"
    path_filter = PathFilter([mask], positive_or_negative=False)

    assert path_filter.match("tree(not_in_use).css")
    assert path_filter.match("foo/tree(not_in_use).css")


def test_case_20_file_with_double_wildcard():
    mask = ".DS_Store"
    path_filter = PathFilter([mask], positive_or_negative=False)

    # POSITIVE
    assert path_filter.match(".DS_Store")
    assert path_filter.match("docs/.DS_Store")
    assert path_filter.match("docs/foo/.DS_Store")
    assert path_filter.match("docs/foo/.DS_Store/foo")


def test_case_21_file_with_double_wildcard():
    mask = "**.DS_Store"
    path_filter = PathFilter([mask], positive_or_negative=False)

    # POSITIVE
    assert path_filter.match(".DS_Store")
    assert path_filter.match("docs/.DS_Store")
    assert path_filter.match("docs/foo/.DS_Store")


def test_case_40_root_slash():
    mask = "/build"
    path_filter = PathFilter([mask], positive_or_negative=False)

    assert path_filter.match("build/foo")

    assert not path_filter.match("strictdoc/build")
    assert not path_filter.match("foo/build/foo.txt")


def test_case_41_root_slash():
    """
    TODO: This is the opposite of what Git's gitignore does but not fighting
          with it yet because it is less intuitive.
    """

    mask = "/**build"
    path_filter = PathFilter([mask], positive_or_negative=False)

    assert path_filter.match("strictdoc/build/")


def test_case_50_negative_empty_mask():
    path_filter = PathFilter([], positive_or_negative=False)

    # NEGATIVE
    assert not path_filter.match("hello.sdoc")
    assert not path_filter.match("docs/hello.sdoc")
    assert not path_filter.match("foo/bar/hello.sdoc")


def test_case_51_negative_behaves_just_like_positive():
    mask = "*.sdoc"
    path_filter = PathFilter([mask], positive_or_negative=False)

    # POSITIVE
    assert path_filter.match("hello.sdoc")
    assert path_filter.match("docs/something/test.sdoc")
    assert path_filter.match("docs/01_user_manual.sdoc")
    assert path_filter.match("docs/.sdoc")

    # NEGATIVE
    assert not path_filter.match("docs")
    assert not path_filter.match("sdoc")


def test_case_80_windows_supported():
    mask = "docs/*.sdoc"
    path_filter = PathFilter([mask], positive_or_negative=False)

    assert not path_filter.match("docs\\hello.sdoc")


def test_case_81_windows_hidden_files_with_dollar_are_supported():
    mask = "~$ProjectPlan.docx"
    path_filter = PathFilter([mask], positive_or_negative=True)

    assert path_filter.match("~$ProjectPlan.docx")


def test_case_82_windows_hidden_files_with_dollar_are_supported():
    mask = "~$*"
    path_filter = PathFilter([mask], positive_or_negative=True)

    assert path_filter.match("~$ProjectPlan.docx")
    assert path_filter.match("foo/bar/~$ProjectPlan.docx")

    assert not path_filter.match("$ProjectPlan.docx")
