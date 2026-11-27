"""
@relation(SDOC-SRS-215, scope=file)
"""

import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

SELECTOR_STATUS = 'select[data-testid="form-field-STATUS"]'


def _option(option: str) -> str:
    return f'[data-testid="form-field-PLATFORM-option-{option}"]'


class Test(E2ECase):
    def test(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(
                exporter.get_output_path_as_uri()
                + "05_select_choice_options/input/input.sdoc.html"
            )
            self.assert_text("System X shall do Y.")

            # A SingleChoice field is a dropdown, a MultipleChoice field a
            # group of checkboxes.
            self.hover('[data-testid="node-requirement"]')
            self.click('[data-testid="node-static-edit-action"]')
            assert self.get_value(SELECTOR_STATUS) == "Draft"
            assert self.is_selected(_option("Linux"))
            assert not self.is_selected(_option("Windows"))
            assert self.is_selected(_option("macOS"))

            # Saving without a change stores nothing.
            self.click('[data-testid="form-submit-action"]')
            self.assert_element_not_present(
                '[data-testid="static-editing-change-count"]'
            )

            self.hover('[data-testid="node-requirement"]')
            self.click('[data-testid="node-static-edit-action"]')
            self.select_option_by_text(SELECTOR_STATUS, "Active")
            self.click(_option("Linux"))
            self.click(_option("Windows"))
            self.click('[data-testid="form-submit-action"]')
            self.assert_text(
                "1 local change", '[data-testid="static-editing-change-count"]'
            )

            changes_export = self.execute_async_script(
                "const done = arguments[arguments.length - 1];"
                "window.StrictDoc.staticEditing.getExport().then(done);"
            )
            assert changes_export["changes"][0]["fields"] == [
                {
                    "name": "STATUS",
                    "index": 0,
                    "old_value": "Draft",
                    "new_value": "Active",
                },
                {
                    "name": "PLATFORM",
                    "index": 0,
                    "old_value": "Linux, macOS",
                    "new_value": "Windows, macOS",
                },
            ]

            # The form shows the stored change.
            self.hover('[data-testid="node-requirement"]')
            self.click('[data-testid="node-static-edit-action"]')
            assert self.get_value(SELECTOR_STATUS) == "Active"
            assert not self.is_selected(_option("Linux"))
            assert self.is_selected(_option("Windows"))
            self.click('[data-testid="form-cancel-action"]')
