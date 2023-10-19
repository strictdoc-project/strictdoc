from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.modal import Modal
from tests.end2end.helpers.components.node.node import Node


class Requirement(Node):  # pylint: disable=invalid-name
    def __init__(
        self, *, test_case: BaseCase, node_xpath: str, node_order: int = 1
    ) -> None:
        assert isinstance(test_case, BaseCase)
        assert isinstance(node_xpath, str)
        assert isinstance(node_order, int)
        super().__init__(test_case, node_xpath=node_xpath)
        self.node_order: int = node_order

    @staticmethod
    def with_node(test_case: BaseCase, node_order: int = 1) -> "Requirement":
        assert isinstance(test_case, BaseCase)
        assert isinstance(node_order, int)

        xpath = f"(//sdoc-node[@data-testid='node-requirement'])[{node_order}]"

        return Requirement(
            test_case=test_case, node_xpath=xpath, node_order=node_order
        )

    @staticmethod
    def without_node(test_case: BaseCase, node_order: int = 1) -> "Requirement":
        assert isinstance(test_case, BaseCase)
        assert isinstance(node_order, int)

        xpath = f"(//sdoc-requirement)[{node_order}]"

        return Requirement(
            test_case=test_case, node_xpath=xpath, node_order=node_order
        )

    # Specific methods

    def assert_is_requirement(self) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}",
            by=By.XPATH,
        )

    # requirement style

    def assert_requirement_style_simple(self) -> None:
        """Make sure that the normal (not table-based) requirement
        is rendered."""
        self.test_case.assert_element(
            f"{self.node_xpath}"
            '//sdoc-requirement[@data-testid="requirement-style-simple"]',
            by=By.XPATH,
        )

    def assert_requirement_style_table(self) -> None:
        """Make sure that the table-based requirement is rendered."""
        self.test_case.assert_element(
            f"{self.node_xpath}"
            '//sdoc-requirement[@data-testid="requirement-style-table"]',
            by=By.XPATH,
        )

    # requirement named fields

    def assert_requirement_title(
        self,
        node_title: str,
        node_level: str = "",
    ) -> None:
        title = super().create_node_title_string(node_title, node_level)
        self.test_case.assert_element(
            f"{self.node_xpath}"
            f"//sdoc-requirement-title[contains(text(), '{title}')]",
            by=By.XPATH,
        )

    def assert_requirement_uid_contains(
        self,
        uid: str,
    ) -> None:
        """Use it with full requirement. <sdoc-requirement-field ...>"""
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='UID']"
            f"[contains(text(), '{uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_uid(
        self,
        uid: str,
    ) -> None:
        """Use it on card. <sdoc-requirement-uid>"""
        self.test_case.assert_element(
            f"{self.node_xpath}//sdoc-requirement-uid[contains(., '{uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_statement_contains(
        self,
        text: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='statement']"
            f"[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_requirement_rationale_contains(
        self,
        text: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='rationale']"
            f"[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_child_link(
        self,
        child_uid: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='child relations']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_parent_link(
        self,
        parent_uid: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='parent relations']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_child_link(
        self,
        child_uid: str,
    ) -> None:
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='child relations']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_parent_link(
        self,
        parent_uid: str,
    ) -> None:
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='parent relations']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    # modal

    def _click_to_open_modal_requirement(self) -> None:
        self.test_case.click_xpath(
            f"{self.node_xpath}"
            "//*[@data-testid='requirement-show-more-action']"
        )

    def do_open_modal_requirement(self) -> Modal:
        modal = Modal(self.test_case)
        modal.assert_not_modal()
        self._click_to_open_modal_requirement()
        modal.assert_modal()
        modal.assert_in_modal("//sdoc-requirement")
        return modal
