from strictdoc.export.rst.rst_to_html_fragment_writer import RstToHtmlFragmentWriter


class SingleDocumentFragmentRenderer:
    def __init__(self):
        self.cache = {}

    def render_text_fragment(self, free_text):
        if free_text in self.cache:
            return self.cache[free_text]

        output = RstToHtmlFragmentWriter.write(free_text)
        self.cache[free_text] = output

        return output
