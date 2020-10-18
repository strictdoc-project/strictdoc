from docutils.core import publish_parts


class RstToHtmlFragmentWriter:

    @staticmethod
    def write(rst_fragment):
        # How do I convert a docutils document tree into an HTML string?
        # https://stackoverflow.com/a/32168938/598057
        html = publish_parts(rst_fragment, writer_name='html')['html_body']
        return html
