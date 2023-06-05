from strictdoc.helpers.string import (
    create_safe_title_string,
)


def test_01():
    input_string = "Hello World"
    result = create_safe_title_string(input_string)
    assert result == "Hello-World"


def test_02():
    input_string = "CPU200 User Manual"
    result = create_safe_title_string(input_string)
    assert result == "CPU200-User-Manual"


def test_03_utf8():
    input_string = "CPU200 Тех Docüment"
    result = create_safe_title_string(input_string)
    assert result == "CPU200-Тех-Docüment"


def test_04_dots():
    input_string = "CPU200.User.Manual"
    result = create_safe_title_string(input_string)
    assert result == "CPU200-User-Manual"


def test_05_dots():
    input_string = "F.A.Q."
    result = create_safe_title_string(input_string)
    assert result == "F-A-Q"
