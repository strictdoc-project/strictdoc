"""
The single-file export shows the pages of the HTML export, follows the
links between them, keeps the browser history and runs the static editor.

@relation(SDOC-SRS-217, scope=file)
"""

import os

from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.html_single.html_single_test_exporter import (
    HTMLSingleTestExporter,
)

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

SELECTOR_FRAME = "iframe.strictdoc-html-single-frame"
SELECTOR_CHANGE_COUNT = '[data-testid="static-editing-change-count"]'


class Test(E2ECase):
    def enter_page(self) -> None:
        # The loader replaces the iframe on every navigation.
        self.switch_to_default_content()
        self.switch_to_frame(SELECTOR_FRAME)

    def test(self):
        with HTMLSingleTestExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(exporter.get_file_uri("Single_file_test.html"))

            # The file starts with the project index.
            self.enter_page()
            self.assert_text("Static editing document")

            # A link to a document opens the document in the same file.
            self.click('a[href*="input.sdoc.html"]')
            self.enter_page()
            self.assert_text("System X shall do A.")
            self.switch_to_default_content()
            assert self.get_current_url().endswith(
                "Single_file_test.html#/01_navigate_and_edit/input/input.sdoc.html"
            )

            # The static editor stores a change in the browser.
            self.enter_page()
            self.hover('(//*[@data-testid="node-requirement"])[1]', by=By.XPATH)
            self.click(
                '(//*[@data-testid="node-static-edit-action"])[1]',
                by=By.XPATH,
            )
            self.update_text(
                '[data-testid="form-field-STATEMENT"]', "System X shall do Z."
            )
            self.click('[data-testid="form-submit-action"]')
            self.assert_text("1 local change", SELECTOR_CHANGE_COUNT)

            # The change survives a reload of the file.
            self.switch_to_default_content()
            self.refresh()
            self.enter_page()
            self.assert_text("1 local change", SELECTOR_CHANGE_COUNT)
            self.assert_text("System X shall do Z.")

            # The back button returns to the project index.
            self.switch_to_default_content()
            self.go_back()
            self.enter_page()
            self.assert_element_not_present(SELECTOR_CHANGE_COUNT)
            self.assert_text("Static editing document")
