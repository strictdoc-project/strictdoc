from PySide2.QtWidgets import (QTextEdit)
import PySide2.QtCore


class DocumentItemEditor(QTextEdit):
    editingFinished = PySide2.QtCore.Signal()

    def focusOutEvent(self, event):
        self.editingFinished.emit()
        super(DocumentItemEditor, self).focusOutEvent(event)
