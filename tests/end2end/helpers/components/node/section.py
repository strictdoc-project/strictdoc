from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.node.node import Node
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)


class Section(Node):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase, node_order: int = 1) -> None:
        assert isinstance(test_case, BaseCase)
        assert isinstance(node_order, int)
        xpath = f"(//sdoc-node[@data-testid='node-section'])[{node_order}]"
        super().__init__(test_case, xpath)
        self.node_order: int = node_order

    def assert_is_section(self) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}",
            by=By.XPATH,
        )

    def assert_section_title(
        self,
        node_title: str,
        node_level: str = "",
    ) -> None:
        title = super().create_node_title_string(node_title, node_level)
        self.test_case.assert_element(
            f"{self.node_xpath}"
            f"//sdoc-section-title//*[contains(., '{title}')]",
            by=By.XPATH,
        )

    def assert_section_text(self, text: str) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            f"//sdoc-section-text//*[contains(., '{text}')]",
            by=By.XPATH,
        )

    # forms

    def do_open_form_edit_section(self) -> Form_EditSection:
        self.test_case.hover_and_click(
            hover_selector=f"{self.node_xpath}",
            click_selector=(
                f'{self.node_xpath}//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditSection(self.test_case)
