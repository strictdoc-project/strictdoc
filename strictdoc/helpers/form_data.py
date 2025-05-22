# mypy: disable-error-code="no-untyped-call,no-untyped-def,union-attr"
import re
from typing import Dict, List, Tuple, Union

from typing_extensions import TypeAlias

ParsedFormDataLeaf: TypeAlias = str

ParsedFormDataContainer: TypeAlias = Union[
    Dict[str, Union[ParsedFormDataLeaf, "ParsedFormDataContainer"]],
    List[Union[ParsedFormDataLeaf, "ParsedFormDataContainer"]],
]

ParsedFormData: TypeAlias = Dict[
    str, Union[ParsedFormDataLeaf, ParsedFormDataContainer]
]


def _set_value_by_key_path(obj, parts, value):
    cursor = obj
    for part_idx, part in enumerate(parts):
        try:
            next_component = parts[part_idx + 1]

            if isinstance(part, str):
                if isinstance(next_component, str):
                    if next_component != "":
                        if part not in cursor:
                            if not isinstance(cursor, dict):
                                raise KeyError
                            cursor[part] = {}
                    else:
                        if part not in cursor:
                            cursor[part] = []
                else:
                    if part not in cursor:
                        cursor[part] = []
                cursor = cursor[part]
            else:
                assert isinstance(part, int)
                if isinstance(next_component, str):
                    try:
                        cursor = cursor[part]
                    except IndexError:
                        if part != len(cursor):
                            raise IndentationError(
                                "The ordering [0], [1], ... "
                                "is broken in this form data: "
                                f"{obj} {parts} {value}."
                            ) from None
                        cursor.append({})
                        cursor = cursor[part]
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
        first_match = re.match(rf"({FIELD_NAME})", key)
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
