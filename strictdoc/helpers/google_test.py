def convert_function_name_to_gtest_macro(input_str: str) -> str:
    """
    Converts a Google Test-produced test name from JUnit XML as follows:
    TestPrtMath.TransitionDistance -> TEST_F(TestPrtMath, TransitionDistance)
    The TEST_F... format is how tree-sitter-cpp parses this macro from C++ code,
    and this is the format used for matching the test function with the
    corresponding test result.
    """
    assert isinstance(input_str, str)
    assert len(input_str) > 0

    if "." not in input_str:
        raise ValueError("Input string must contain a dot.")

    parts = input_str.split(".")
    if len(parts) != 2:
        raise ValueError("Input string must contain exactly one dot.")

    return f"TEST_F({parts[0]}, {parts[1]})"
