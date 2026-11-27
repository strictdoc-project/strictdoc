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


def test_case_22_mask_with_underscore():
    """
    Verify that the underscores in the masks are supported.

    https://github.com/strictdoc-project/strictdoc/issues/2211
    """
    mask = "_foobar.sdoc"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("_foobar.sdoc")


def test_case_23_wildcards_match_parentheses_in_paths():
    """
    Verify that the wildcards match file and folder names with parentheses.

    https://github.com/strictdoc-project/strictdoc/issues/3235
    """
    for mask_ in ("/docs/", "docs/**", "docs/*.sdoc", "**.sdoc"):
        path_filter = PathFilter([mask_], positive_or_negative=True)

        # POSITIVE
        assert path_filter.match("docs/input(1).sdoc"), mask_
        assert path_filter.match("docs/(input.sdoc"), mask_
        assert path_filter.match("docs/input).sdoc"), mask_

    path_filter = PathFilter(["docs/**/*.sdoc"], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("docs/sub(1)/input(1).sdoc")

    # NEGATIVE
    assert not path_filter.match("docs/input(1).sdoc")

    path_filter = PathFilter(["docs/*.sdoc"], positive_or_negative=True)

    # NEGATIVE
    assert not path_filter.match("docs/sub(1)/input(1).sdoc")
    assert not path_filter.match("docs\\input(1).sdoc")


def test_case_24_double_wildcard_matches_any_depth_and_separators():
    mask = "**.test.py"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match(".test.py")
    assert path_filter.match("file.test.py")
    assert path_filter.match("/file.test.py")
    assert path_filter.match("folder/subfolder/file.test.py")
    assert path_filter.match("folder\\subfolder\\file.test.py")
    assert path_filter.match("folder/subfolder\\file.test.py")
    assert path_filter.match("folder//file.test.py")

    # NEGATIVE
    assert not path_filter.match("folder/subfolder/file.py")
    assert not path_filter.match("folder/subfolder/file.test.pyc")
    assert not path_filter.match("folder/file.test.py.bak")


def test_case_25_double_wildcard_matches_only_name_characters():
    mask = "/docs/**.sdoc"
    path_filter = PathFilter([mask], positive_or_negative=True)

    # POSITIVE
    assert path_filter.match("docs/a b/(c)/file-1_2.sdoc")

    # NEGATIVE
    # "**" matches the characters that "*" matches, and path separators.
    assert not path_filter.match("docs/a+b/file.sdoc")
    assert not path_filter.match("docs/a/fil\u00e9.sdoc")


def test_case_26_double_wildcard_in_unanchored_folder_mask():
    mask = "__pycache__"
    path_filter = PathFilter([mask], positive_or_negative=False)

    # POSITIVE
    assert path_filter.match("__pycache__")
    assert path_filter.match("strictdoc/__pycache__/module.cpython-310.pyc")

    # NEGATIVE
    assert not path_filter.match("strictdoc/not__pycache__/module.pyc")
    assert not path_filter.match("strictdoc/__pycache__2/module.pyc")


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


def test_case_90_may_match_inside_anchored_masks():
    path_filter = PathFilter(
        ["/strictdoc/**.py", "/tests/integration/**itest", "/LICENSE"],
        positive_or_negative=True,
    )

    # POSITIVE: the folder is on the way to an included path, or inside it.
    assert path_filter.may_match_inside("strictdoc/")
    assert path_filter.may_match_inside("strictdoc/core/")
    assert path_filter.may_match_inside("tests/")
    assert path_filter.may_match_inside("tests/integration/")
    assert path_filter.may_match_inside("tests/integration/commands/")
    # "/LICENSE" also matches the files inside a folder called LICENSE.
    assert path_filter.may_match_inside("LICENSE/")

    # NEGATIVE
    assert not path_filter.may_match_inside("build/")
    assert not path_filter.may_match_inside(".venv/")
    assert not path_filter.may_match_inside("tests/unit/")
    assert not path_filter.may_match_inside("docs/strictdoc/")


def test_case_91_may_match_inside_skips_no_folder_for_other_masks():
    # An empty filter, a mask that is not anchored, and a mask with Windows
    # separators can match in any folder.
    for masks in (
        [],
        ["docs/"],
        ["/docs/", "*.sdoc"],
        ["/docs/", "**/requirements/"],
        ["/docs\\sub"],
    ):
        path_filter = PathFilter(masks, positive_or_negative=True)
        assert path_filter.may_match_inside("build/"), masks
        assert path_filter.may_match_inside("build/docs/"), masks


def test_case_92_may_match_inside_agrees_with_match():
    """
    If match() accepts a path, may_match_inside() accepts every folder of the
    path.
    """
    masks = [
        "/docs/",
        "/docs/*.sdoc",
        "/strictdoc/**.py",
        "/src/*/module/**",
        "/str*/x.py",
        "/LICENSE",
        "/**.md",
        "/sub(2)/",
    ]
    paths = [
        "docs/a.sdoc",
        "docs/sub/b.sdoc",
        "docs/x.sdoc/inner.txt",
        "strictdoc/core/file.py",
        "strictdoc/file.py",
        "src/lib/module/a/b.c",
        "stringutils/x.py",
        "LICENSE",
        "LICENSE/file.txt",
        "deep/folder/readme.md",
        "sub(2)/input.sdoc",
        "build/docs/a.sdoc",
        ".venv/lib/strictdoc/file.py",
    ]
    for mask_ in masks:
        path_filter = PathFilter([mask_], positive_or_negative=True)
        for path_ in paths:
            if not path_filter.match(path_):
                continue
            parts = path_.split("/")[:-1]
            for index_ in range(1, len(parts) + 1):
                folder = "/".join(parts[:index_]) + "/"
                assert path_filter.may_match_inside(folder), (mask_, path_)
