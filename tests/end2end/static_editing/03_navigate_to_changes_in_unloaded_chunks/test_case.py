"""
@relation(SDOC-SRS-215, scope=file)
"""

import os

from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

SELECTOR_POSITION = '[data-testid="static-editing-navigation-position"]'
SELECTOR_NEXT = '[data-testid="static-editing-next-change-action"]'
SELECTOR_CURRENT = "sdoc-node[data-static-editing-current]"
XPATH_LAST_NODE = '//sdoc-node[contains(., "REQ-40")]'


class Test(E2ECase):
    def edit_statement(self, uid: str, statement: str) -> None:
        node_xpath = f'//sdoc-node[.//*[text()="{uid}"]]'
        self.hover(node_xpath, by=By.XPATH)
        self.click(
            f'{node_xpath}//*[@data-testid="node-static-edit-action"]',
            by=By.XPATH,
        )
        self.update_text('[data-testid="form-field-STATEMENT"]', statement)
        self.click('[data-testid="form-submit-action"]')
        self.assert_element(
            f'//sdoc-static-editing-preview[contains(., "{statement}")]',
            by=By.XPATH,
        )

    def test(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            document_uri = (
                exporter.get_output_path_as_uri()
                + "03_navigate_to_changes_in_unloaded_chunks/input/input.sdoc.html"
            )

            # Open the document at the last node to load its chunk.
            self.open(document_uri + "#REQ-40")
            self.edit_statement("REQ-40", "System X shall do 40 changed.")

            # Open the document from the start. The chunk of the last node
            # is not loaded.
            self.open(document_uri)
            self.edit_statement("REQ-1", "System X shall do 1 changed.")
            self.assert_element_not_present(XPATH_LAST_NODE, by=By.XPATH)

            # The stored changes define the number of changes.
            self.assert_text("– / 2", SELECTOR_POSITION)

            self.click(SELECTOR_NEXT)
            self.assert_text("1 / 2", SELECTOR_POSITION)
            self.assert_text("System X shall do 1 changed.", SELECTOR_CURRENT)

            # The next change is in a chunk that is not loaded yet. The
            # navigation loads the chunk and marks the node.
            self.click(SELECTOR_NEXT)
            self.assert_text("2 / 2", SELECTOR_POSITION)
            self.assert_text("System X shall do 40 changed.", SELECTOR_CURRENT)
