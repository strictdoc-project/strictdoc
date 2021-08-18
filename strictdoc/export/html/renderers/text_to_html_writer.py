import html


class TextToHtmlWriter:
    @staticmethod
    def write(text_fragment):
        return html.escape(text_fragment, quote=True).replace(
            u"\n", u"<br />\n"
        )
