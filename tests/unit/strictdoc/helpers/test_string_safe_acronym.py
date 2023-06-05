from strictdoc.helpers.string import create_safe_acronym


def test_01():
    input_string = "Hello World"
    result = create_safe_acronym(input_string)
    assert result == "HW"


def test_02():
    input_string = "HelloWorld"
    result = create_safe_acronym(input_string)
    assert result == "H"


def test_03():
    input_string = "Hello 1orld"
    result = create_safe_acronym(input_string)
    assert result == "H"


def test_04():
    input_string = "hello world"
    result = create_safe_acronym(input_string)
    assert result == "HW"


def test_05():
    input_string = "F.A.Q"
    result = create_safe_acronym(input_string)
    assert result == "FAQ"
