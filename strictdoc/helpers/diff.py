import difflib
from difflib import SequenceMatcher
from typing import Callable

from markupsafe import Markup, escape


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


red: Callable[[str], str] = (
    lambda text: f'<span class="lambda_red">{escape(text)}</span>'
)
green: Callable[[str], str] = (
    lambda text: f'<span class="lambda_green">{escape(text)}</span>'
)
white: Callable[[str], str] = lambda text: f"<span>{escape(text)}</span>"


def get_colored_html_diff_string(old: str, new: str, flag: str) -> Markup:
    assert old is not None
    assert new is not None
    assert flag in ("left", "right")

    result = ""
    codes = difflib.SequenceMatcher(a=old, b=new).get_opcodes()
    for code in codes:
        if code[0] == "equal":
            result += white(old[code[1] : code[2]])
        elif code[0] == "delete":
            if flag == "left":
                result += red(old[code[1] : code[2]])
        elif code[0] == "insert":
            if flag == "right":
                result += green(new[code[3] : code[4]])
        elif code[0] == "replace":
            if flag == "left":
                result += red(old[code[1] : code[2]])
            else:
                result += green(new[code[3] : code[4]])
        else:
            raise NotImplementedError(code)  # pragma: no cover
    return Markup(result)
