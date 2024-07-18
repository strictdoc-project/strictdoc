from markupsafe import Markup, escape


class TextToHtmlWriter:
    @staticmethod
    def write(text_fragment: str) -> Markup:
        return escape(text_fragment).replace("\n", Markup("<br/>\n"))

    @staticmethod
    def write_anchor_link(title: str, href: str) -> str:
        return f'<a href="{href}">🔗&nbsp;{title}</a>`'
