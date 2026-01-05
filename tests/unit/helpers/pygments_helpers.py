from pygments import highlight
from pygments.formatters import (
    HtmlFormatter,
    RawTokenFormatter,
    TestcaseFormatter,
)


def dump_lexed_code(lexer, code) -> None:
    print(highlight(code, lexer, RawTokenFormatter()))  # noqa: T201
    print(highlight(code, lexer, HtmlFormatter()))  # noqa: T201
    print(highlight(code, lexer, TestcaseFormatter()))  # noqa: T201
