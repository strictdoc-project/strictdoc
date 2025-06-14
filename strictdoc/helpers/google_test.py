from typing import List


def convert_function_name_to_gtest_macro(input_str: str) -> List[str]:
    """
    Convert a Google Test name from the JUnit XML format to a C++ macro definition.

    Converts a Google Test-produced test name from JUnit XML as follows:
    TestPrtMath.TransitionDistance -> TEST_F(TestPrtMath, TransitionDistance)
    The TEST_F... format is how tree-sitter-cpp parses this macro from C++ code,
    and this is the format used for matching the test function with the
    corresponding test result.
    """
    assert isinstance(input_str, str)
    assert len(input_str) > 0

    # Google Test parts show up like this in the XML:
    # XML: MyTestPattern/MyTestHelperPattern.TestName3/3  # noqa: ERA001
    # C++: TEST_P(MyTestHelperPattern, TestName3)
    is_pattern_function = "/" in input_str
    if is_pattern_function:
        input_str_parts = input_str.split("/")
        input_str = input_str_parts[1]

    if "." not in input_str:
        raise ValueError(f"Input string must contain a dot: '{input_str}'.")

    parts = input_str.split(".")
    if len(parts) != 2:
        raise ValueError(
            f"Input string must contain exactly one dot: '{input_str}'."
        )

    if is_pattern_function:
        return [
            f"TEST_P({parts[0]}, {parts[1]})",
        ]

    return [f"TEST({parts[0]}, {parts[1]})", f"TEST_F({parts[0]}, {parts[1]})"]
