import PySide2.QtGui

from PySide2.QtGui import (QTextDocument)

DOCUMENT_MARGIN = 20


class DocumentNode:
    document = None

    def __init__(self, text, width):
        css = "body { margin-left: 0px; }"

        doc = QTextDocument()

        doc.setDefaultStyleSheet(css)
        doc.setDocumentMargin(DOCUMENT_MARGIN)
        doc.setTextWidth(width)

        text_option = doc.defaultTextOption()
        text_option.setWrapMode(PySide2.QtGui.QTextOption.WrapMode.WordWrap)

        doc.setDefaultTextOption(text_option)

        self.document = doc
        self.update_text(text)

    def update_text(self, new_text):
        self.document.setHtml("<body>" + new_text + "</body>")

    def get_document(self):
        return self.document

    def get_document_clone(self, text):
        assert isinstance(text, str)
        clone = self.document.clone()
        clone.setPlainText(text)
        clone.setDocumentMargin(DOCUMENT_MARGIN)
        return clone
