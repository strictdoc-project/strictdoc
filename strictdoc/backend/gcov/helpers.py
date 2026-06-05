import re
from typing import List, Optional


def normalize_gcovr_file_path(
    path: str, *, source_root_path: Optional[str] = None
) -> str:
    normalized_path = path.replace("\\", "/")
    if normalized_path.startswith("./"):
        normalized_path = normalized_path[2:]

    if source_root_path is None:
        return normalized_path

    normalized_source_root = source_root_path.replace("\\", "/").rstrip("/")
    normalized_path_lower = normalized_path.lower()
    normalized_source_root_lower = normalized_source_root.lower()
    if normalized_path_lower.startswith(normalized_source_root_lower + "/"):
        return normalized_path[len(normalized_source_root) + 1 :]
    return normalized_path


def convert_function_name_to_gcovr_style(name: str) -> str:
    """
    Convert a StrictDoc C++ function name to gcovr's demangled spelling.

    Examples:
    - "test::Adder::add(const int& a, const int& b)"
      -> "test::Adder::add(int const&, int const&)"
    - "test::Multiplier::multiply(int a, const int& b)"
      -> "test::Multiplier::multiply(int, int const&)"
    """
    opening_bracket = name.rfind("(")
    if opening_bracket == -1 or not name.endswith(")"):
        return name

    function_name = name[:opening_bracket]
    parameter_list = name[opening_bracket + 1 : -1]
    if parameter_list.strip() == "":
        return name

    parameters = _split_function_parameters(parameter_list)
    canonical_parameters = [
        _convert_function_parameter_to_gcovr_style(parameter_)
        for parameter_ in parameters
    ]
    return f"{function_name}({', '.join(canonical_parameters)})"


def _split_function_parameters(parameter_list: str) -> List[str]:
    """
    Split a C++ function parameter list on top-level commas.

    Nested template and function-call commas are preserved.

    Examples:
    - "int a, const int& b" -> ["int a", "const int& b"]
    - "Map<Key, Value> map, int count" -> ["Map<Key, Value> map", "int count"]
    """
    parameters: List[str] = []
    current_parameter: List[str] = []
    nested_angle_brackets = 0
    nested_round_brackets = 0
    nested_square_brackets = 0

    for character_ in parameter_list:
        if character_ == "," and (
            nested_angle_brackets == 0
            and nested_round_brackets == 0
            and nested_square_brackets == 0
        ):
            parameters.append("".join(current_parameter).strip())
            current_parameter = []
            continue

        current_parameter.append(character_)
        if character_ == "<":
            nested_angle_brackets += 1
        elif character_ == ">" and nested_angle_brackets > 0:
            nested_angle_brackets -= 1
        elif character_ == "(":
            nested_round_brackets += 1
        elif character_ == ")" and nested_round_brackets > 0:
            nested_round_brackets -= 1
        elif character_ == "[":
            nested_square_brackets += 1
        elif character_ == "]" and nested_square_brackets > 0:
            nested_square_brackets -= 1

    parameters.append("".join(current_parameter).strip())
    return parameters


def _convert_function_parameter_to_gcovr_style(parameter: str) -> str:
    """
    Convert one StrictDoc/tree-sitter C++ parameter to gcovr's spelling.

    The conversion removes the parameter name, normalizes pointer/reference
    spacing, and moves a leading const qualifier behind the base type.

    Examples:
    - "const int& a" -> "int const&"
    - "int a" -> "int"
    """
    parameter = re.sub(r"\s+", " ", parameter.strip())
    parameter = re.sub(r"\s*=\s*.*$", "", parameter)
    parameter = re.sub(r"\s+[A-Za-z_][A-Za-z0-9_]*$", "", parameter)
    parameter = re.sub(r"\s*([*&])\s*", r"\1", parameter)

    if parameter.startswith("const "):
        parameter = parameter[len("const ") :]
        if parameter.endswith("&"):
            parameter = f"{parameter[:-1]} const&"
        elif parameter.endswith("*"):
            parameter = f"{parameter[:-1]} const*"
        else:
            parameter = f"{parameter} const"

    return parameter
