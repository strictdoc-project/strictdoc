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

    # NEGATIVE
    assert not path_filter.match("docs")
    assert not path_filter.match("docs/something/test.sdoc")
    assert not path_filter.match("docs/01_user_manual.sdoc")
    assert not path_filter.match("docs/.sdoc")
    assert not path_filter.match("sdoc")


def test_case_03_single_wildcard():
    mask = "docs/*"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("docs/01_user_manual.sdoc")
    # This is possible, but it will be filtered by extension before this filter
    # anyway.
    assert path_filter.match("docs/01_user_manual_sdoc")

    # FIXME: Disallow this?
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

    # NEGATIVE
    assert not path_filter.match("docs/.sdoc")
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

    # NEGATIVE
    assert not path_filter.match("docs")
    assert not path_filter.match("docs/something/test.sdoc")
    assert not path_filter.match("docs/01_user_manual.sdoc")
    assert not path_filter.match("docs/.sdoc")
    assert not path_filter.match("sdoc")
