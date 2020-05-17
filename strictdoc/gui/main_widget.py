from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QHBoxLayout, QHeaderView, QLineEdit, QSizePolicy,
                               QTableView, QWidget, QItemDelegate)

from strictdoc.gui.table_model import CustomTableModel


class Delegate(QItemDelegate):
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


class Widget(QWidget):
    def __init__(self, data):
        QWidget.__init__(self)

        # Getting the Model
        self.model = CustomTableModel(data)

        # Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setItemDelegate(Delegate())

        # QTableView Headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.horizontal_header.setStretchLastSection(True)

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        ## Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)
