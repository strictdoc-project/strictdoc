import os
import re
from typing import List, Optional

from strictdoc.helpers.md5 import get_md5
from strictdoc.helpers.net import is_valid_url


def create_gcovr_html_details_link(
    *,
    gcovr_html_report: str,
    source_file_path: str,
    export_output_html_root: str,
    document_level: int,
) -> str:
    """
    Create a link from a GCOV report page to the gcovr HTML details page of
    one source file.

    gcovr names each details page after the main HTML report, which is the
    -o file of "gcovr --html-details":
    <report stem>.<source file name>.<MD5 of the source file path><suffix>.
    The source file path is the "file" path of the gcovr JSON report.

    The gcovr_html_report argument is an http(s) URL or an absolute path:
    - For a URL, the link is an absolute URL.
    - For a path, the link is relative to the GCOV report page. The page is
      document_level folders below export_output_html_root.

    Examples:
    - "https://ci.example.com/coverage.html", "src/functions.cpp"
      -> "https://ci.example.com/coverage.functions.cpp.c5e7...227b.html"
    - "/project/build/coverage.html", "src/functions.cpp",
      export_output_html_root="/project/output/html", document_level=1
      -> "../../../build/coverage.functions.cpp.c5e7...227b.html"
    """
    if is_valid_url(gcovr_html_report):
        report_folder_url, _, report_file_name = gcovr_html_report.rpartition(
            "/"
        )
        details_file_name = _create_gcovr_html_details_file_name(
            report_file_name, source_file_path
        )
        return f"{report_folder_url}/{details_file_name}"

    details_file_name = _create_gcovr_html_details_file_name(
        os.path.basename(gcovr_html_report), source_file_path
    )
    details_file_path = os.path.join(
        os.path.dirname(gcovr_html_report), details_file_name
    )
    details_file_rel_path = os.path.relpath(
        details_file_path, start=os.path.abspath(export_output_html_root)
    ).replace(os.sep, "/")
    return "../" * document_level + details_file_rel_path


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


def _create_gcovr_html_details_file_name(
    report_file_name: str, source_file_path: str
) -> str:
    """
    Create the file name of a gcovr HTML details page.

    Example:
    - "coverage.html", "src/functions.cpp"
      -> "coverage.functions.cpp.c5e71015e270864c89a8b6e26afb227b.html"
    """
    report_stem, report_suffix = os.path.splitext(report_file_name)
    source_file_name = source_file_path.rpartition("/")[2]
    source_file_path_hash = get_md5(source_file_path)
    return (
        f"{report_stem}.{source_file_name}.{source_file_path_hash}"
        f"{report_suffix}"
    )


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
