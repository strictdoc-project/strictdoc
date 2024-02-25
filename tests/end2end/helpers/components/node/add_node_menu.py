from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)


class AddNode_Menu:  # pylint: disable=invalid-name  # noqa: E501
    """Drop-down list of links to add nodes."""

    def __init__(self, test_case: BaseCase, node_xpath: str) -> None:
        assert isinstance(test_case, BaseCase)
        assert isinstance(node_xpath, str)
        self.test_case: BaseCase = test_case
        self.node_xpath: str = node_xpath

    # base actions

    def assert_node_menu(self) -> None:
        self.test_case.assert_element_visible(  # ?????????
            "//sdoc-menu/sdoc-menu-list",
            by=By.XPATH,
        )

    # asserts

    def assert_node_has_action_add_requirement_above(self) -> None:
        self.test_case.assert_element_present(
            f"{self.node_xpath}"
            '//*[@data-testid="node-add-requirement-above-action"]'
        )

    def assert_node_has_action_add_section_above(self) -> None:
        self.test_case.assert_element_present(
            f"{self.node_xpath}"
            '//*[@data-testid="node-add-section-above-action"]'
        )

    def assert_node_has_action_add_requirement_below(self) -> None:
        self.test_case.assert_element_present(
            f"{self.node_xpath}"
            '//*[@data-testid="node-add-requirement-below-action"]'
        )

    def assert_node_has_action_add_section_below(self) -> None:
        self.test_case.assert_element_present(
            f"{self.node_xpath}"
            '//*[@data-testid="node-add-section-below-action"]'
        )

    def assert_node_has_action_add_requirement_child(self) -> None:
        self.test_case.assert_element_present(
            f"{self.node_xpath}"
            '//*[@data-testid="node-add-requirement-child-action"]'
        )

    def assert_node_has_action_add_section_child(self) -> None:
        self.test_case.assert_element_present(
            f"{self.node_xpath}"
            '//*[@data-testid="node-add-section-child-action"]'
        )

    # Add section

    # From ROOT
    def do_node_add_section_first(self) -> Form_EditSection:
        self.test_case.click(
            selector=(
                '//*[@data-testid="node-root"]'
                '//*[@data-testid="node-add-section-first-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    # From Node
    def do_node_add_section_above(self) -> Form_EditSection:
        self.test_case.click(
            selector=(
                f"{self.node_xpath}"
                '//*[@data-testid="node-add-section-above-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    def do_node_add_section_below(self) -> Form_EditSection:
        self.test_case.click(
            selector=(
                f"{self.node_xpath}"
                '//*[@data-testid="node-add-section-below-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    def do_node_add_section_child(self) -> Form_EditSection:
        self.test_case.click(
            selector=(
                f"{self.node_xpath}"
                '//*[@data-testid="node-add-section-child-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    # Add requirement

    # From ROOT
    def do_node_add_requirement_first(self) -> Form_EditRequirement:
        self.test_case.click(
            selector=(
                '//*[@data-testid="node-root"]'
                '//*[@data-testid="node-add-requirement-first-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_element_first(
        self, element_tag: str
    ) -> Form_EditRequirement:
        self.test_case.click(
            selector=(
                '//*[@data-testid="node-root"]'
                f'//*[@data-testid="node-add-{element_tag.lower()}-first-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    # From Node
    def do_node_add_requirement_above(self) -> Form_EditRequirement:
        self.test_case.click(
            selector=(
                f"{self.node_xpath}"
                '//*[@data-testid="node-add-requirement-above-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_requirement_below(self) -> Form_EditRequirement:
        self.test_case.click(
            selector=(
                f"{self.node_xpath}"
                '//*[@data-testid="node-add-requirement-below-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_requirement_child(self) -> Form_EditRequirement:
        self.test_case.click(
            selector=(
                f"{self.node_xpath}"
                '//*[@data-testid="node-add-requirement-child-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_element_child(
        self, element_type: str
    ) -> Form_EditRequirement:
        self.test_case.click(
            selector=(
                f"{self.node_xpath}"
                f'//*[@data-testid="node-add-{element_type.lower()}-child-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_element_above(
        self, element_type: str
    ) -> Form_EditRequirement:
        self.test_case.click(
            selector=(
                f"{self.node_xpath}"
                f'//*[@data-testid="node-add-{element_type.lower()}-above-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_element_below(
        self, element_type: str
    ) -> Form_EditRequirement:
        self.test_case.click(
            selector=(
                f"{self.node_xpath}"
                f'//*[@data-testid="node-add-{element_type.lower()}-below-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)
