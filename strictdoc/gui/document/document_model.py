import typing

import PySide2
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide2.QtGui import QColor

from strictdoc.backend.rst.rst_document_editor import RSTDocumentEditor
from strictdoc.backend.rst.rst_document import RSTDocument
from strictdoc.backend.rst.rst_to_html_writer import HTMLWriter
from strictdoc.backend.rst.rst_writer import RSTWriter


class DocumentTableModel(QAbstractTableModel):
    rst_document = None
    input_lines = None
    rst_document_editor = None
    html_writer = None
    rst_writer = None
    column_count = 0
    row_count = 0

    def __init__(self, rst_document):
        assert isinstance(rst_document, RSTDocument)
        QAbstractTableModel.__init__(self)

        self.rst_document = rst_document
        self.input_lines = rst_document.get_as_list()
        self.rst_document_editor = RSTDocumentEditor(rst_document)
        self.html_writer = HTMLWriter()
        self.rst_writer = RSTWriter()
        self.column_count = 1
        self.row_count = len(self.input_lines)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self,
                   section: int,
                   orientation: PySide2.QtCore.Qt.Orientation,
                   role: int = ...) -> typing.Any:
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return "Foobar"
        else:
            # TODO
            return "{}".format(section)

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            assert column == 0

            rst_node = self.input_lines[row]

            return self.html_writer.write_fragment(rst_node)
        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)
        elif role == Qt.ForegroundRole:
            return QColor(Qt.black)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

        return None

    def setData(self,
                index: PySide2.QtCore.QModelIndex,
                value: typing.Any,
                role: int = ...) -> bool:
        raise NotImplementedError

    def flags(self, index: PySide2.QtCore.QModelIndex) -> PySide2.QtCore.Qt.ItemFlags:
        return super().flags(index) | Qt.ItemIsEditable

    def get_item_as_rst(self, index):
        row = index.row()

        assert row < len(self.input_lines), \
            "row is {}, len is {}".format(row, len(self.input_lines))

        rst_node = self.input_lines[row]
        print("rst_node: {}".format(rst_node))

        return self.rst_writer.write_rst_fragment(rst_node).strip()

    def set_item_from_rst(self,
                          index: PySide2.QtCore.QModelIndex,
                          value: typing.Any) -> bool:
        assert isinstance(value, str)

        print("Model: setData:")
        row = index.row()
        print("current: {}".format(self.input_lines[row]))

        self.rst_document_editor.replace_node(self.input_lines[row], value)

        self.input_lines = self.rst_document.get_as_list()

        self.row_count = len(self.input_lines)

        print(self.rst_document.rst_document.pformat())

        # This ensures that the cells are resized if the new content is
        # smaller/larger.
        self.dataChanged.emit(index, index)

        return True
