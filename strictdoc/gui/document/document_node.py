import PySide2.QtGui

from PySide2.QtGui import (QTextDocument)

DOCUMENT_MARGIN = 20


class DocumentNode:
    document = None

    def __init__(self, text, estimated_width):
        css = "body { margin-left: 0px; }"

        document = QTextDocument()

        document.setDefaultStyleSheet(css)
        document.setDocumentMargin(DOCUMENT_MARGIN)
        document.setTextWidth(estimated_width)

        text_option = document.defaultTextOption()
        text_option.setWrapMode(PySide2.QtGui.QTextOption.WrapMode.WordWrap)

        document.setDefaultTextOption(text_option)

        self.document = document
        self.update_text(text, estimated_width)

    def update_text(self, new_text, estimated_width):
        assert isinstance(new_text, str)
        assert isinstance(estimated_width, int)
        assert estimated_width > 0

        self.document.setHtml("<body>" + new_text + "</body>")
        self.document.setTextWidth(estimated_width)

    def get_document(self):
        return self.document

    def get_document_clone(self, text):
        assert isinstance(text, str)
        clone = self.document.clone()
        clone.setPlainText(text)
        clone.setDocumentMargin(DOCUMENT_MARGIN)
        return clone
