"""
@relation(SDOC-SRS-215, scope=file)
"""

import os

from selenium.webdriver.common.keys import Keys

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

SELECTOR_VALUE = '[data-testid="form-relation-value"]'
SELECTOR_OPTION = '[data-testid="form-relation-autocomplete-option"]'


class Test(E2ECase):
    def test(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(
                exporter.get_output_path_as_uri()
                + "08_autocomplete_relation_uid/input/input.sdoc.html"
            )
            self.assert_text("System X shall do Y.")

            self.hover('[data-testid="node-requirement"]')
            self.click('[data-testid="node-static-edit-action"]')
            self.click('[data-testid="form-add-relation"]')

            # The text matches anywhere in the UID, also in the UIDs of
            # other documents. A UID that starts with the text comes first.
            self.type(SELECTOR_VALUE, "12")
            options = self.find_visible_elements(SELECTOR_OPTION)
            assert [
                option_.get_attribute("data-uid") for option_ in options
            ] == ["SYSR-WX-012", "SYSR-WX-120"]
            self.assert_text("Wind speed sensor", SELECTOR_OPTION)

            # Choose with the keyboard.
            self.send_keys(SELECTOR_VALUE, Keys.ARROW_DOWN)
            self.send_keys(SELECTOR_VALUE, Keys.ARROW_DOWN)
            self.send_keys(SELECTOR_VALUE, Keys.ENTER)
            assert self.get_value(SELECTOR_VALUE) == "SYSR-WX-120"
            self.assert_element_not_visible(SELECTOR_OPTION)

            # Choose with the mouse. The title matches as well.
            self.update_text(SELECTOR_VALUE, "wind")
            self.click(f'{SELECTOR_OPTION}[data-uid="SYSR-WX-012"]')
            assert self.get_value(SELECTOR_VALUE) == "SYSR-WX-012"

            self.click('[data-testid="form-submit-action"]')
            changes_export = self.execute_async_script(
                "const done = arguments[arguments.length - 1];"
                "window.StrictDoc.staticEditing.getExport().then(done);"
            )
            assert changes_export["changes"][0]["relations"] == [
                {
                    "action": "add",
                    "type": "Parent",
                    "value": "SYSR-WX-012",
                    "role": None,
                }
            ]
