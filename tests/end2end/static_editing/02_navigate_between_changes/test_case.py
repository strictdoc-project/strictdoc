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
SELECTOR_PREVIOUS = '[data-testid="static-editing-previous-change-action"]'
SELECTOR_CURRENT = "sdoc-node[data-static-editing-current]"


class Test(E2ECase):
    def edit_statement(self, node_number: int, statement: str) -> None:
        self.hover(
            f'(//*[@data-testid="node-requirement"])[{node_number}]',
            by=By.XPATH,
        )
        self.click(
            f'(//*[@data-testid="node-static-edit-action"])[{node_number}]',
            by=By.XPATH,
        )
        self.update_text('[data-testid="form-field-STATEMENT"]', statement)
        self.click('[data-testid="form-submit-action"]')
        self.assert_element(
            f'//sdoc-static-editing-preview[contains(., "{statement}")]',
            by=By.XPATH,
        )
        self.assert_element_not_present('[data-testid="form-submit-action"]')

    def test(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(
                exporter.get_output_path_as_uri()
                + "02_navigate_between_changes/input/input.sdoc.html"
            )
            self.assert_text("System X shall do A.")

            # Without changes, the panel shows no navigation.
            self.assert_element_not_present(
                '[data-testid="static-editing-navigation"]'
            )

            self.edit_statement(1, "System X shall do A1.")
            self.edit_statement(3, "System X shall do C1.")
            self.assert_text(
                "2 local changes",
                '[data-testid="static-editing-change-count"]',
            )

            # The navigation starts without a current change.
            self.assert_text("– / 2", SELECTOR_POSITION)
            self.assert_element_not_present(SELECTOR_CURRENT)

            # The down button jumps to the changed nodes in document order
            # and skips the unchanged node.
            self.click(SELECTOR_NEXT)
            self.assert_text("1 / 2", SELECTOR_POSITION)
            self.assert_text("System X shall do A1.", SELECTOR_CURRENT)

            self.click(SELECTOR_NEXT)
            self.assert_text("2 / 2", SELECTOR_POSITION)
            self.assert_text("System X shall do C1.", SELECTOR_CURRENT)

            # The navigation wraps around at the last and the first change.
            self.click(SELECTOR_NEXT)
            self.assert_text("1 / 2", SELECTOR_POSITION)
            self.assert_text("System X shall do A1.", SELECTOR_CURRENT)

            self.click(SELECTOR_PREVIOUS)
            self.assert_text("2 / 2", SELECTOR_POSITION)
            self.assert_text("System X shall do C1.", SELECTOR_CURRENT)
