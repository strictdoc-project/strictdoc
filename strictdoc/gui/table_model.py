import typing

import PySide2

from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide2.QtGui import QColor


class CustomTableModel(QAbstractTableModel):
    input_lines = None

    def __init__(self, data=None):
        QAbstractTableModel.__init__(self)
        self.load_data(data)

    def load_data(self, data):
        assert isinstance(data, list)

        self.input_lines = data

        self.column_count = 1
        self.row_count = len(data)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role):
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
            return self.input_lines[row]
        elif role == Qt.BackgroundRole:
            return QColor(Qt.black)
        elif role == Qt.ForegroundRole:
            return QColor(Qt.white)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

        return None

    def setData(self,
                index: PySide2.QtCore.QModelIndex,
                value: typing.Any,
                role: int = ...) -> bool:
        assert value
        assert isinstance(value, str)

        print("Model: setData:")
        row = index.row()

        print(value)

        self.input_lines[row] = value
        return True

    def flags(self, index: PySide2.QtCore.QModelIndex) -> PySide2.QtCore.Qt.ItemFlags:
        return super().flags(index) | Qt.ItemIsEditable

