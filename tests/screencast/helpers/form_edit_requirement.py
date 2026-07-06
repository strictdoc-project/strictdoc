from __future__ import annotations

from tests.screencast.helpers.form import Form


class Form_EditRequirement(Form):
    def do_fill_in_field_uid(self, field_value: str) -> None:
        super().do_fill_in("UID", field_value)

    def do_fill_in_field_title(self, field_value: str) -> None:
        super().do_fill_in("TITLE", field_value)

    def do_fill_in_field_statement(self, field_value: str) -> None:
        super().do_fill_in("STATEMENT", field_value)
