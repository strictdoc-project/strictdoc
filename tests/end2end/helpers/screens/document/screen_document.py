from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.constants import NBSP
from tests.end2end.helpers.screens.document.form_edit_config import (
    Form_EditConfig,
)
from tests.end2end.helpers.screens.document.form_edit_grammar import (
    Form_EditGrammar,
)
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)


class Screen_Document:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self):
        self.test_case.assert_element(
            '//body[@data-viewtype="document"]',
            by=By.XPATH,
        )

    def assert_empty_document(self) -> None:
        self.test_case.assert_element(
            '//*[@data-testid="document-placeholder"]'
        )

    def assert_not_empty_document(self) -> None:
        self.test_case.assert_element_not_visible(
            '//*[@data-testid="document-placeholder"]'
        )

    def assert_is_document_title(self, document_title: str) -> None:
        self.test_case.assert_text(document_title)

    def assert_text(self, text: str) -> None:
        self.test_case.assert_text(text)

    def assert_no_text(self, text: str) -> None:
        self.test_case.assert_element_not_present(
            f"//*[contains(., '{text}')]", by=By.XPATH
        )

    def assert_requirement_style_simple(self) -> None:
        # Make sure that the normal (not table-based) requirement is rendered.
        self.test_case.assert_element(
            '//sdoc-node[@data-testid="node-requirement-simple"]',
            by=By.XPATH,
        )

    def assert_requirement_style_table(self) -> None:
        # Make sure that the table-based requirement is rendered.
        self.test_case.assert_element(
            '//sdoc-node[@data-testid="node-requirement-table"]',
            by=By.XPATH,
        )

    def assert_toc_contains_string(self, string: str) -> None:
        self.test_case.assert_element(
            f"//turbo-frame[@id='frame-toc']//*[contains(., '{string}')]",
            by=By.XPATH
        )

    def assert_node_title_contains(
            self,
            node_title: str,
            node_level: str = "",
            node_order: int = 1,
        ) -> None:
        # title pattern: "1.2.3.&nbsp:Title"
        # data_level (node_level) pattern: "1.2.3" (node_level)
        prefix = "" if node_level == "" else f"{node_level}.{NBSP}"
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]"
            f"//*[contains(., '{prefix}{node_title}')]",
            by=By.XPATH
        )

    # Assert fields content:
    # Method with the 'field_name' can be used,
    # but named methods are recommended.
    #TODO

    def assert_xpath_contains(self, xpath: str, text: str) -> None:
        self.test_case.assert_element(
            f"{xpath}"
            f"[contains(., '{text}')]",
            by=By.XPATH
        )

    # Assert fields content: named methods

    def assert_document_title_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO
        self.test_case.assert_element(
            "//sdoc-node//H1"
            f"[contains(., '{text}')]",
            by=By.XPATH
        )

    def assert_document_uid_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO
        self.test_case.assert_element(
            "//table[@class='table_meta']//th"
            f"[contains(., 'UID')]",
            by=By.XPATH
        )
        self.test_case.assert_element(
            "//table[@class='table_meta']//td"
            f"[contains(., '{text}')]",
            by=By.XPATH
        )

    def assert_document_version_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO
        self.test_case.assert_element(
            "//table[@class='table_meta']//th"
            f"[contains(., 'VERSION')]",
            by=By.XPATH
        )
        self.test_case.assert_element(
            "//table[@class='table_meta']//td"
            f"[contains(., '{text}')]",
            by=By.XPATH
        )

    def assert_document_classification_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO
        self.test_case.assert_element(
            "//table[@class='table_meta']//th"
            f"[contains(., 'CLASSIFICATION')]",
            by=By.XPATH
        )
        self.test_case.assert_element(
            "//table[@class='table_meta']//td"
            f"[contains(., '{text}')]",
            by=By.XPATH
        )

    def assert_document_abstract_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO
        self.test_case.assert_element(
            "//sdoc-node"
            f"[contains(., '{text}')]",
            by=By.XPATH
        )

    # Open forms

    def do_export_reqif(self) -> None:
        self.test_case.click_xpath(
            '(//*[@data-testid="document-export-reqif-action"])'
        )

    def do_open_modal_form_edit_grammar(self) -> Form_EditGrammar:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.test_case.click_xpath(
            '(//*[@data-testid="document-edit-grammar-action"])'
        )
        self.test_case.assert_element(
            "//sdoc-modal",
            by=By.XPATH,
        )
        return Form_EditGrammar(self.test_case)

    def do_open_form_edit_config(self) -> Form_EditConfig:
        self.test_case.hover_and_click(
            hover_selector="(//sdoc-node)[1]",
            click_selector=(
                '(//sdoc-node)[1]//*[@data-testid="document-edit-config-action"]'  # noqa: E501
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditConfig(self.test_case)

    def do_open_form_edit_requirement(self) -> Form_EditRequirement:
        self.test_case.hover_and_click(
            hover_selector="(//sdoc-node)[2]",
            click_selector=(
                '(//sdoc-node)[2]//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_open_form_edit_section(self) -> Form_EditSection:
        self.test_case.hover_and_click(
            hover_selector="(//sdoc-node)[2]",
            click_selector=(
                '(//sdoc-node)[2]//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    # Node actions

    def do_open_node_menu(self, field_order: int = 1) -> None:
        self.test_case.hover_and_click(
            hover_selector=f"(//sdoc-node)[{field_order}]",
            click_selector=(
                f"(//sdoc-node)[{field_order}]"
                "//*[@data-testid='node-menu-handler']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )

    # Add section

    def do_node_add_section_first(self) -> Form_EditSection:
        self.do_open_node_menu()
        self.test_case.click(
            selector=(
                f"(//sdoc-node)[1]"
                '//*[@data-testid="node-add-section-first-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    def do_node_add_section_above(
            self, field_order: int = 1
        ) -> Form_EditSection:
        self.do_open_node_menu(field_order)
        self.test_case.click(
            selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-add-section-above-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    def do_node_add_section_below(
            self, field_order: int = 1
        ) -> Form_EditSection:
        self.do_open_node_menu(field_order)
        self.test_case.click(
            selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-add-section-below-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    def do_node_add_section_child(
            self, field_order: int = 1
        ) -> Form_EditSection:
        self.do_open_node_menu(field_order)
        self.test_case.click(
            selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-add-section-child-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    # Add requirement

    def do_node_add_requirement_first(self) -> Form_EditRequirement:
        self.do_open_node_menu()
        self.test_case.click(
            selector=(
                f"(//sdoc-node)[1]"
                '//*[@data-testid="node-add-requirement-first-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_requirement_above(
            self, field_order: int = 1
        ) -> Form_EditRequirement:
        self.do_open_node_menu(field_order)
        self.test_case.click(
            selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-add-requirement-above-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_requirement_below(
            self, field_order: int = 1
        ) -> Form_EditRequirement:
        self.do_open_node_menu(field_order)
        self.test_case.click(
            selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-add-requirement-below-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_requirement_child(
            self, field_order: int = 1
        ) -> Form_EditRequirement:
        self.do_open_node_menu(field_order)
        self.test_case.click(
            selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-add-requirement-child-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)
