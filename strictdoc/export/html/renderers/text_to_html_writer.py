import html


class TextToHtmlWriter:
    @staticmethod
    def write(text_fragment):
        return html.escape(text_fragment, quote=True).replace("\n", "<br/>\n")

    @staticmethod
    def write_link(title, _):
        return f"{title}"
