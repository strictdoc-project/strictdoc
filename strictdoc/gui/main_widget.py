from PySide2.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget)

from strictdoc.gui.document.document_item_delegate import DocumentItemDelegate
from strictdoc.gui.document.document_model import DocumentTableModel


class Widget(QWidget):
    def __init__(self, data):
        QWidget.__init__(self)

        # Getting the Model
        self.model = DocumentTableModel(data)

        # Creating a QTableView
        table_delegate = DocumentItemDelegate()
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setItemDelegate(table_delegate)
        # TODO: table_delegate retains table_view
        # TODO: check if it causes any issues with reference cycles.
        table_delegate.table_view = self.table_view

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
