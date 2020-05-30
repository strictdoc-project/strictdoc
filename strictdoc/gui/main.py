import argparse
import sys

from PySide2.QtWidgets import QApplication, QShortcut
from PySide2.QtGui import QKeySequence, QFont

from strictdoc.gui.main_widget import Widget
from strictdoc.gui.main_window import MainWindow
from strictdoc.backend.rst.rst_reader import RSTReader


if __name__ == "__main__":
    options = argparse.ArgumentParser()
    options.add_argument("-f", "--file", type=str, required=True)
    args = options.parse_args()

    path_to_doc = args.file
    with open(path_to_doc, 'r') as file:
        doc_content = file.read()

    rst_document = RSTReader.read_rst(doc_content)

    # Qt Application
    app = QApplication(sys.argv)

    font = QFont("Courier")
    font.setStyleHint(QFont.Monospace)
    QApplication.setFont(font)

    widget = Widget(rst_document)
    window = MainWindow(widget)
    window.show()

    def magic():
        print("dump:")
        print(rst_document.rst_document.pformat())

    QShortcut(QKeySequence("Alt+Return"), window, magic)

    sys.exit(app.exec_())
