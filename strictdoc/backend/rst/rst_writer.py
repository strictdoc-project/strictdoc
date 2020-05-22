# TODO: create something like this later:
# https://github.com/sphinx-contrib/restbuilder
# https://stackoverflow.com/questions/19523151/is-there-a-way-to-create-an-intermediate-output-from-sphinx-extensions/19526851#19526851
# also this: https://stackoverflow.com/questions/61666809/parse-and-write-rst-using-docutils

from strictdoc.backend.rst.docutils_helper import DocutilsHelper
from strictdoc.backend.rst.visitors.rst_write_visitor import RSTWriteVisitor


class RSTWriter:
    @staticmethod
    def write_rst_document(rst_document):
        print("RSTWriter.write_rst_document: {}".format(rst_document))
        visitor = RSTWriteVisitor(rst_document)
        rst_document.walkabout(visitor)

        return visitor.get_output()

    @staticmethod
    def write_rst_fragment(rst_fragment):
        print("RSTWriter.write_rst_fragment: {}".format(rst_fragment))
        children = []
        if isinstance(rst_fragment, list):
            for node in rst_fragment:
                children.append(node.deepcopy())
        else:
            children.append(rst_fragment)

        document_wrapper = DocutilsHelper.create_new_doc()
        document_wrapper.children = children

        visitor = RSTWriteVisitor(document_wrapper)
        document_wrapper.walkabout(visitor)

        return visitor.get_output()


def write_rst(rst_document):
    return RSTWriter.write_rst_document(rst_document)
