from strictdoc.export.rst.rst_to_html_fragment_writer import RstToHtmlFragmentWriter


class SingleDocumentFragmentRenderer:
    def render_text_fragment(self, free_text):
        output = RstToHtmlFragmentWriter.write(free_text)

        return output
