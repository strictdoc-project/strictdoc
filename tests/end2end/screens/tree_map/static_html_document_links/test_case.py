"""
@relation(SDOC-SRS-157, scope=file)
"""

import os

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_document_link_from_nested_document(self):
        # The source document lives one folder below the project root
        # (input/nested_document.sdoc), so its exported HTML page is not at
        # the output root. The Tree Map's static links must still resolve to
        # that page, not one with the project folder segment duplicated.
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(exporter.get_output_path_as_uri() + "tree_map.html")

            self.assert_element(
                '//body[@data-viewtype="tree-map"]',
                by=By.XPATH,
            )
            self.click(
                '[data-testid="tree-map-preview-folder-contents-control"]'
            )
            requirement_element = self.driver.find_element(
                By.CSS_SELECTOR,
                '[data-testid="tree-map-node"]'
                '[data-node-title="Nested requirement"]',
            )

            original_window = self.driver.current_window_handle
            window_handles = set(self.driver.window_handles)
            ActionChains(self.driver).key_down(Keys.SHIFT).click(
                requirement_element
            ).key_up(Keys.SHIFT).perform()
            WebDriverWait(self.driver, 5).until(
                lambda driver: (
                    len(driver.window_handles) == len(window_handles) + 1
                )
            )
            document_window = (
                set(self.driver.window_handles) - window_handles
            ).pop()
            self.driver.switch_to.window(document_window)

            screen_document = Screen_Document(self)
            screen_document.assert_on_screen_document()
            screen_document.assert_target_by_anchor("REQ-NESTED-1")

            self.driver.close()
            self.driver.switch_to.window(original_window)
