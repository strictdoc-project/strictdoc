from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.modal import Modal
from tests.end2end.helpers.components.node.node import Node
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)


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

    #
    # Requirement style.
    #
    def assert_requirement_style_simple(self) -> None:
        """
        Make sure that the normal (not table-based) requirement
        is rendered.
        """
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
            f"//sdoc-requirement-title//*[contains(text(), '{title}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_mid(self) -> None:
        """Use it with full requirement. <sdoc-requirement-field ...>"""
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='MID']",
            by=By.XPATH,
        )

    def assert_requirement_has_no_uid(self) -> None:
        """Use it with full requirement. <sdoc-requirement-field ...>"""
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='UID']",
            by=By.XPATH,
        )

    def assert_field_contains(
        self,
        field_name: str,
        field_value: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            f"//sdoc-requirement-field[@data-field-label='{field_name}']"
            f"//*[contains(text(), '{field_value}')]",
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
            f"//*[contains(text(), '{uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_uid(
        self,
        uid: str,
    ) -> None:
        """Use it on card. <sdoc-requirement-uid>"""
        self.test_case.assert_element(
            f"{self.node_xpath}//sdoc-requirement-uid//*[contains(., '{uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_statement_contains(
        self,
        text: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='statement']"
            f"//*[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_requirement_rationale_contains(
        self,
        text: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='rationale']"
            f"//*[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_child_relation(
        self,
        child_uid: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='child relations']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_parent_relation(
        self,
        parent_uid: str,
    ) -> None:
        self.test_case.assert_element(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='parent relations']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_child_relation(
        self,
        child_uid: str,
    ) -> None:
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='child relations']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_parent_relation(
        self,
        parent_uid: str,
    ) -> None:
        self.test_case.assert_element_not_present(
            f"{self.node_xpath}"
            "//sdoc-requirement-field[@data-field-label='parent relations']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    # clone

    def do_clone_requirement(self) -> Form_EditRequirement:
        self.test_case.hover_and_click(
            hover_selector=f"{self.node_xpath}",
            click_selector=(
                f"{self.node_xpath}//*[@data-testid='node-clone-action']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    # in CARD view:

    # modal

    def _hover_and_click_to_open_modal_requirement(self) -> None:
        self.test_case.hover_and_click(
            hover_selector=f"{self.node_xpath}",
            click_selector=(
                f"{self.node_xpath}"
                "//*[@data-testid='requirement-show-more-action']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )

    def do_open_modal_requirement(self) -> Modal:
        modal = Modal(self.test_case)
        modal.assert_not_modal()
        self._hover_and_click_to_open_modal_requirement()
        modal.assert_modal()
        modal.assert_in_modal("//sdoc-requirement")
        return modal

    def do_go_to_this_requirement_in_document_view(self):
        self.test_case.hover_and_click(
            hover_selector=f"{self.node_xpath}",
            click_selector=(
                f"{self.node_xpath}"
                "//*[@data-testid='requirement-find-in-document']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        from tests.end2end.helpers.screens.document.screen_document import (
            Screen_Document,
        )

        return Screen_Document(self.test_case)
