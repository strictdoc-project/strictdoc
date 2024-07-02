import re

# Possible tags with arguments and without:
# .. image:: _assets/picture.svg
# .. csv-table:: (has no argument)
RST_DIRECTIVE_PATTERN = re.compile(r"^\.\. [a-z-]+:: ?.*$", re.MULTILINE)
VALID_AFTER_INLINE_MARKUP = " \t\n-.,:;!?\\/'\")]}>"


def string_contains_rst_directive(input_string: str) -> bool:
    return RST_DIRECTIVE_PATTERN.match(input_string) is not None


def escape_str_after_inline_markup(str_after_inline_markup: str) -> str:
    # Ensure inline markup recognition rule #7
    # https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#inline-markup-recognition-rules
    if (
        str_after_inline_markup
        and str_after_inline_markup[0] not in VALID_AFTER_INLINE_MARKUP
    ):
        return f"\\{str_after_inline_markup}"
    return str_after_inline_markup
