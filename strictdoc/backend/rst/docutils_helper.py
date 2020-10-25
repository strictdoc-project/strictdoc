import docutils
import docutils.frontend
import docutils.parsers.rst
import docutils.utils


class DocutilsHelper:
    @staticmethod
    def create_new_doc():
        components = (docutils.parsers.rst.Parser,)
        options_parser = docutils.frontend.OptionParser(components=components)
        settings = options_parser.get_default_values()
        document = docutils.utils.new_document('<rst-doc>', settings=settings)
        return document
