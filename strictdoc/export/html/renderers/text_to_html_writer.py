import html


class TextToHtmlWriter:
    @staticmethod
    def write(text_fragment: str) -> str:
        return html.escape(text_fragment, quote=True).replace("\n", "<br/>\n")

    @staticmethod
    def write_anchor_link(title: str, href: str) -> str:
        return f'<a href="{href}">🔗&nbsp;{title}</a>`'
