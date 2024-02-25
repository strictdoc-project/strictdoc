from strictdoc.helpers.string import is_uppercase_underscore_string


def test_is_uppercase_underscore_string():
    assert is_uppercase_underscore_string("HELLO")
    assert is_uppercase_underscore_string("HELLO_WORLD")
    assert is_uppercase_underscore_string("HELLO1_WORLD2")
    assert is_uppercase_underscore_string("HELLO_WORLD_2")

    assert not is_uppercase_underscore_string("")
    assert not is_uppercase_underscore_string("hello")
    assert not is_uppercase_underscore_string("hello_world")
    assert not is_uppercase_underscore_string("2HELLO")
    assert not is_uppercase_underscore_string("HELLO%")
