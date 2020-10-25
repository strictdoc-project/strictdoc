import argparse
import sys

from PySide2.QtWidgets import QApplication, QShortcut
from PySide2.QtGui import QKeySequence, QFont

from strictdoc.gui.main_widget import Widget
from strictdoc.gui.main_window import MainWindow
from strictdoc.backend.rst.rst_reader import RSTReader
from strictdoc.core.logger import Logger


if __name__ == "__main__":
    options = argparse.ArgumentParser()
    options.add_argument("-f", "--file", type=str, required=True)
    options.add_argument("--available-loggers", required=False, action='store_true')
    options.add_argument("--enable-loggers", type=str, required=False)
    args = options.parse_args()

    available_loggers = args.available_loggers
    if available_loggers:
        print("available loggers:")
        print(', '.join(Logger.available_loggers))
        exit(1)

    enabled_loggers_as_string = args.enable_loggers
    if enabled_loggers_as_string:
        enabled_loggers = enabled_loggers_as_string.split(',')
        for enabled_logger in enabled_loggers:
            if enabled_logger not in Logger.available_loggers:
                print("cannot enable logger because it does not exist: {}".format(
                    enabled_logger
                ))
                exit(1)
        Logger.enabled_loggers = enabled_loggers

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
