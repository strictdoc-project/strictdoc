from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QLineEdit, QItemDelegate)


class DocumentItemDelegate(QItemDelegate):
    def __init__(self):
        QItemDelegate.__init__(self)

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
