import pytest

from strictdoc.helpers.google_test import convert_function_name_to_gtest_macro


def test_convert_function_name_to_gtest_macro():
    assert (
        convert_function_name_to_gtest_macro("TestPrtMath.TransitionDistance")
        == "TEST_F(TestPrtMath, TransitionDistance)"
    )

    with pytest.raises(ValueError, match="Input string must contain a dot."):
        convert_function_name_to_gtest_macro("InvalidString")

    with pytest.raises(
        ValueError, match="Input string must contain exactly one dot."
    ):
        convert_function_name_to_gtest_macro("Too.Many.Dots")

    with pytest.raises(AssertionError):
        convert_function_name_to_gtest_macro(123)  # Non-string input

    with pytest.raises(AssertionError):
        convert_function_name_to_gtest_macro("")  # Empty string
