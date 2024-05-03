from strictdoc.helpers.string import create_safe_requirement_tag_string


def test_is_safe_alphanumeric_string():
    assert create_safe_requirement_tag_string("REQUIREMENT") == "REQUIREMENT"
    assert (
        create_safe_requirement_tag_string("Requirement Type")
        == "REQUIREMENT_TYPE"
    )
    assert (
        create_safe_requirement_tag_string("REQUIREMENT TYPE")
        == "REQUIREMENT_TYPE"
    )
    assert (
        create_safe_requirement_tag_string("REQUIREMENT 2") == "REQUIREMENT_2"
    )
