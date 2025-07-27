import re
from typing import Dict, List, Match, Optional, Tuple, Union

from typing_extensions import TypeAlias

ParsedFormDataLeaf: TypeAlias = str

ParsedFormDataContainer: TypeAlias = Union[
    Dict[str, Union[ParsedFormDataLeaf, "ParsedFormDataContainer"]],
    List[Union[ParsedFormDataLeaf, "ParsedFormDataContainer"]],
]

ParsedFormData: TypeAlias = Dict[
    str, Union[ParsedFormDataLeaf, ParsedFormDataContainer]
]

ParsedFormDataNode: TypeAlias = Union[
    str,
    Dict[str, "ParsedFormDataNode"],
    List["ParsedFormDataNode"],
]


def as_dict(node: ParsedFormDataNode) -> Dict[str, ParsedFormDataNode]:
    if not isinstance(node, dict):
        raise KeyError("Expected dict node")
    return node


def as_list(node: ParsedFormDataNode) -> List[ParsedFormDataNode]:
    if not isinstance(node, list):
        raise KeyError("Expected list node")
    return node


def _set_value_by_key_path(
    obj: Dict[str, ParsedFormDataNode],
    parts: List[Union[str, int]],
    value: Union[ParsedFormDataLeaf, ParsedFormDataContainer],
) -> None:
    cursor: ParsedFormDataNode = obj
    for part_idx, part in enumerate(parts):
        try:
            next_component = parts[part_idx + 1]

            if isinstance(part, str):
                cursor_dict = as_dict(cursor)

                if isinstance(next_component, str):
                    if next_component != "":
                        if part not in cursor:
                            if not isinstance(cursor, dict):
                                raise KeyError
                            cursor_dict[part] = {}
                    else:
                        if part not in cursor:
                            cursor_dict[part] = []
                else:
                    if part not in cursor:
                        cursor_dict[part] = []

                cursor = cursor_dict[part]
            else:
                assert isinstance(part, int)

                if isinstance(next_component, str):
                    cursor_list = as_list(cursor)

                    try:
                        cursor = cursor_list[part]
                    except IndexError:
                        if part != len(cursor):
                            raise IndentationError(
                                "The ordering [0], [1], ... "
                                "is broken in this form data: "
                                f"{obj} {parts} {value}."
                            ) from None
                        cursor_list.append({})
                        cursor = cursor_list[part]
                else:
                    raise NotImplementedError("No [][] supported.")
        except IndexError:
            if isinstance(part, str):
                assert len(part) > 0, part
                assert isinstance(cursor, dict)
                cursor[part] = value
            else:
                raise NotImplementedError from None  # pragma: no cover


FIELD_NAME = "[A-Za-z0-9_]*"


def parse_form_data(
    form_data: List[Tuple[str, str]],
) -> ParsedFormData:
    result_dict: ParsedFormData = {}

    for key, value in form_data:
        first_match: Optional[Match[str]] = re.match(rf"({FIELD_NAME})", key)

        assert first_match is not None, "first_match must not be None."

        match_groups = first_match.groups()
        assert len(match_groups) == 1

        match = re.findall(rf"\[({FIELD_NAME}|\d+)]", key)
        strings: List[Union[str, int]] = list(map(str, match))
        for part_idx, part in enumerate(strings):
            try:
                strings[part_idx] = int(part)
            except ValueError:
                continue

        components = [match_groups[0]] + strings

        _set_value_by_key_path(result_dict, components, value)

    return result_dict
