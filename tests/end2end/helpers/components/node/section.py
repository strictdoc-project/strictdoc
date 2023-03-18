from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.node.node import Node
from tests.end2end.helpers.constants import NODE_1
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)


class Section(Node):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def assert_is_section(self, node_order: int = NODE_1) -> None:
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]/sdoc-section",
            by=By.XPATH,
        )

    # forms

    def do_open_form_edit_section(
        self, field_order: int = NODE_1
    ) -> Form_EditSection:
        self.test_case.hover_and_click(
            hover_selector=f"(//sdoc-node)[{field_order}]",
            click_selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditSection(self.test_case)
