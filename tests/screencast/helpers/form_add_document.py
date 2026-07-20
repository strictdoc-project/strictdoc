from __future__ import annotations

from tests.screencast.helpers.form import Form


class Form_AddDocument(Form):
    def do_fill_in_title(self, field_value: str) -> None:
        super().do_fill_in("document_title", field_value)

    def do_fill_in_path(self, field_value: str) -> None:
        super().do_fill_in("document_path", field_value)
