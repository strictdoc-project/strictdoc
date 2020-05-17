from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import (QLineEdit, QStyledItemDelegate, QStyleOptionViewItem, QApplication, QStyle)
from PySide2.QtGui import (QTextDocument, QAbstractTextDocumentLayout)


class DocumentItemDelegate(QStyledItemDelegate):
    def __init__(self):
        QStyledItemDelegate.__init__(self)

    # How to make a fast QTableView with HTML-formatted and clickable cells?
    # https://stackoverflow.com/a/44365155/598057
    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        if options.widget:
            style = options.widget.style()
        else:
            style = QApplication.style()

        doc = QTextDocument()

        doc.setDefaultStyleSheet("div { background-color: red; color: green; padding: 20px; margin: 10px;}")
        doc.setHtml(options.text)

        options.text = ''

        style.drawControl(QStyle.CE_ItemViewItem, options, painter)
        ctx = QAbstractTextDocumentLayout.PaintContext()

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)

        painter.save()

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        painter.translate(0, 0.5*(options.rect.height() - doc.size().height()))

        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    # def sizeHint(self, option, index):
    #     options = QStyleOptionViewItem(option)
    #     self.initStyleOption(options, index)
    #
    #     doc = QTextDocument()
    #     doc.setHtml(options.text)
    #     doc.setTextWidth(options.rect.width())
    #
    #     return QSize(100, 100)

    def createEditor(self, parent, option, index):
        if index.column() == 0:
            lineedit = QLineEdit(parent)
            return lineedit
        assert 0

    def setEditorData(self, editor, index):
        print("setEditorData")
        # row = index.row()
        # column = index.column()
        value = index.model().itemData(index)
        # asdf
        # resizeRowsToContents


        print(type(value))
        print(value)

        text_value = value[Qt.DisplayRole]
        print("setting text value: {}".format(text_value))

        if isinstance(editor, QLineEdit):
            editor.setText(text_value)

    def setModelData(self, editor, model, index):
        # TODO: Why this method if there is a working DocumentModel.setData?
        super().setModelData(editor, model, index)

