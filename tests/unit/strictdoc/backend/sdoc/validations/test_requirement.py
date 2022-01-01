from strictdoc.backend.sdoc.validations.requirement import (
    multi_choice_regex_match,
)


def test_01_positive():
    assert multi_choice_regex_match("A, B") is True


def test_02_positive():
    assert multi_choice_regex_match("TAG1, TAG2, TAG3") is True


def test_03_negative():
    assert multi_choice_regex_match("A,B") is False
