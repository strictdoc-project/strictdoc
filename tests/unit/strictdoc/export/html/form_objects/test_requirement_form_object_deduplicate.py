from strictdoc.export.html.form_objects.requirement_form_object import (
    deduplicate_comma_separated_value,
)


def test_no_duplicates_is_unchanged():
    assert deduplicate_comma_separated_value("Tag1, Tag2") == "Tag1, Tag2"


def test_simple_duplicate_is_removed():
    assert deduplicate_comma_separated_value("Tag1, Tag1") == "Tag1"


def test_duplicate_with_different_casing_is_removed():
    assert (
        deduplicate_comma_separated_value("Tag1, tag1, TAG1, Tag2")
        == "Tag1, Tag2"
    )


def test_extra_whitespace_is_stripped():
    assert (
        deduplicate_comma_separated_value("  Tag1 ,Tag2,  Tag1  ")
        == "Tag1, Tag2"
    )


def test_empty_parts_are_dropped():
    assert deduplicate_comma_separated_value("Tag1,, ,Tag2") == "Tag1, Tag2"


def test_single_value_is_unchanged():
    assert deduplicate_comma_separated_value("Tag1") == "Tag1"


def test_empty_value_is_unchanged():
    assert deduplicate_comma_separated_value("") == ""
