VALID_AFTER_INLINE_MARKUP = " \t\n-.,:;!?\\/'\")]}>"


def escape_str_after_inline_markup(str_after_inline_markup: str) -> str:
    # Ensure inline markup recognition rule #7
    # https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#inline-markup-recognition-rules
    if (
        str_after_inline_markup
        and str_after_inline_markup[0] not in VALID_AFTER_INLINE_MARKUP
    ):
        return f"\\{str_after_inline_markup}"
    return str_after_inline_markup
