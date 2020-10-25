

from strictdoc.backend.rst.visitors.html_write_visitor import HTMLWriteVisitor
from strictdoc.backend.rst.docutils_helper import DocutilsHelper


class HTMLWriter:
    def write_document(self, rst_document):
        visitor = HTMLWriteVisitor(rst_document)
        rst_document.walkabout(visitor)

        html_output = visitor.get_output()

        return html_output

    def write_fragment(self, rst_fragment):
        children = []
        if isinstance(rst_fragment, list):
            for node in rst_fragment:
                children.append(node.deepcopy())
        else:
            children.append(rst_fragment)

        document_wrapper = DocutilsHelper.create_new_doc()
        document_wrapper.children = children

        return self.write_document(document_wrapper)
