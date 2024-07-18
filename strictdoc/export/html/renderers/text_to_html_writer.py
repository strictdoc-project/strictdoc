# mypy: disable-error-code="no-untyped-def"
from markupsafe import Markup, escape


class TextToHtmlWriter:
    @staticmethod
    def write(text_fragment):
        return escape(text_fragment).replace("\n", Markup("<br/>\n"))

    @staticmethod
    def write_link(title, _):
        return f"{title}"
