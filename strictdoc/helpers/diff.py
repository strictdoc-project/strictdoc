# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import difflib
from difflib import SequenceMatcher

from markupsafe import Markup, escape


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


red = lambda text: f'<span class="lambda_red">{escape(text)}</span>'
green = lambda text: f'<span class="lambda_green">{escape(text)}</span>'
white = lambda text: f"<span>{escape(text)}</span>"


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
    return Markup(result)
