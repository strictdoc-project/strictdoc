import argparse
import sys

from PySide2.QtWidgets import QApplication

from strictdoc.gui.main_widget import Widget
from strictdoc.gui.main_window import MainWindow
from strictdoc.backend.rst_reader import RSTReader

if __name__ == "__main__":
    options = argparse.ArgumentParser()
    options.add_argument("-f", "--file", type=str, required=True)
    args = options.parse_args()

    path_to_doc = args.file
    with open(path_to_doc, 'r') as file:
        doc_content = file.read()

    document = RSTReader.read_rst(doc_content)

    # document.dump_pretty()
    # rst_output = document.dump_rst()

    data = document.get_as_list()

    # Qt Application
    app = QApplication(sys.argv)

    widget = Widget(data)
    window = MainWindow(widget)
    window.show()

    sys.exit(app.exec_())
