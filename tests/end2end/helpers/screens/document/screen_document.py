from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.constants import NBSP, NODE_0, NODE_1
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


class Screen_Document:  # pylint: disable=invalid-name, too-many-public-methods
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

    def assert_confirm(self) -> None:
        self.test_case.assert_element('//*[@data-testid="confirm-message"]')

    def assert_confirm_requirement_delete(self) -> None:
        self.test_case.assert_element('//*[@data-testid="confirm-message"]')
        self.test_case.assert_element(
            '//*[@data-testid="confirm-action"]'
            '[contains(., "Delete requirement")]',
            by=By.XPATH,
        )

    def assert_confirm_section_delete(self) -> None:
        self.test_case.assert_element('//*[@data-testid="confirm-message"]')
        self.test_case.assert_element(
            '//*[@data-testid="confirm-action"]'
            '[contains(., "Delete section")]',
            by=By.XPATH,
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
            '//sdoc-requirement[@data-testid="requirement-style-simple"]',
            by=By.XPATH,
        )

    def assert_requirement_style_table(self) -> None:
        # Make sure that the table-based requirement is rendered.
        self.test_case.assert_element(
            '//sdoc-requirement[@data-testid="requirement-style-table"]',
            by=By.XPATH,
        )

    # TOC

    def assert_toc_contains_string(self, string: str) -> None:
        self.test_case.assert_element(
            f"//turbo-frame[@id='frame-toc']//*[contains(., '{string}')]",
            by=By.XPATH,
        )

    def assert_toc_contains_not(self, string: str) -> None:
        self.test_case.assert_element_not_present(
            f"//turbo-frame[@id='frame-toc']//*[contains(., '{string}')]",
            by=By.XPATH,
        )

    def assert_node_title_contains(
        self,
        node_title: str,
        node_level: str = "",
        node_order: int = NODE_1,
    ) -> None:
        # title pattern: "1.2.3.&nbsp:Title"
        # data_level (node_level) pattern: "1.2.3" (node_level)
        prefix = "" if node_level == "" else f"{node_level}.{NBSP}"
        self.test_case.assert_element(
            # TODO: improve pattern / testid
            f"(//sdoc-node)[{node_order}]"
            f"//*[contains(., '{prefix}{node_title}')]",
            by=By.XPATH,
        )

    def assert_requirement_uid_contains(
        self,
        uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='UID']"
            f"[contains(., '{uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_child_link(
        self,
        child_uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='child links']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_parent_link(
        self,
        parent_uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='parent links']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_child_link(
        self,
        child_uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element_not_present(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='child links']"
            f"[contains(., '{child_uid}')]",
            by=By.XPATH,
        )

    def assert_requirement_has_not_parent_link(
        self,
        parent_uid: str,
        node_order: int = NODE_1,
    ) -> None:
        # TODO: improve pattern
        self.test_case.assert_element_not_present(
            f"(//sdoc-node)[{node_order}]/sdoc-requirement"
            "/sdoc-requirement-field[@data-field-label='parent links']"
            f"[contains(., '{parent_uid}')]",
            by=By.XPATH,
        )

    # Assert fields content:
    # Method with the 'field_name' can be used,
    # but named methods are recommended.

    def assert_xpath_contains(self, xpath: str, text: str) -> None:
        self.test_case.assert_element(
            f"{xpath}[contains(., '{text}')]", by=By.XPATH
        )

    # Assert fields content: named methods

    def assert_document_title_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO H1 -> testid
        self.test_case.assert_element(
            f"//*[@data-testid='node-root']/H1[contains(., '{text}')]",
            by=By.XPATH
        )

    def assert_document_uid_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO table_meta -> testid
        self.test_case.assert_element(
            "//table[@class='table_meta']//th[contains(., 'UID')]",
            by=By.XPATH,
        )
        self.test_case.assert_element(
            f"//table[@class='table_meta']//td[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_document_version_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO table_meta -> testid
        self.test_case.assert_element(
            "//table[@class='table_meta']//th[contains(., 'VERSION')]",
            by=By.XPATH,
        )
        self.test_case.assert_element(
            f"//table[@class='table_meta']//td[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_document_classification_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO table_meta -> testid
        self.test_case.assert_element(
            "//table[@class='table_meta']//th"
            "[contains(., 'CLASSIFICATION')]",
            by=By.XPATH,
        )
        self.test_case.assert_element(
            f"//table[@class='table_meta']//td[contains(., '{text}')]",
            by=By.XPATH,
        )

    def assert_document_abstract_contains(self, text: str) -> None:
        assert isinstance(text, str)
        # TODO table_meta -> testid
        self.test_case.assert_element(
            f"//sdoc-node[contains(., '{text}')]", by=By.XPATH
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
            hover_selector="//*[@data-testid='node-root']",
            click_selector=(
                "//*[@data-testid='node-root']"
                "//*[@data-testid='document-edit-config-action']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditConfig(self.test_case)

    def do_open_form_edit_requirement(
        self, field_order: int = NODE_1
    ) -> Form_EditRequirement:
        self.test_case.hover_and_click(
            hover_selector=f"(//sdoc-node)[{field_order}]",
            click_selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-edit-action"]'
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

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

    # Node actions

    def do_open_node_menu(self, field_order: int = NODE_0) -> None:
        self.test_case.hover_and_click(
            hover_selector=f"(//sdoc-node)[{field_order}]",
            click_selector=(
                f"(//sdoc-node)[{field_order}]"
                "//*[@data-testid='node-menu-handler']"
            ),
            hover_by=By.XPATH,
            click_by=By.XPATH,
        )

    # Node delete

    def do_node_delete(self, field_order: int = NODE_1) -> None:
        self.do_open_node_menu(field_order)
        self.test_case.click(
            selector=(
                f"(//sdoc-node)[{field_order}]"
                '//*[@data-testid="node-delete-action"]'
            ),
            by=By.XPATH,
        )

    # Add section

    def do_node_add_section_first(self) -> Form_EditSection:
        self.do_open_node_menu()
        self.test_case.click(
            selector=(
                "//*[@data-testid='node-root']"
                '//*[@data-testid="node-add-section-first-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditSection(self.test_case)

    def do_node_add_section_above(
        self, field_order: int = NODE_1
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
        self, field_order: int = NODE_1
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
        self, field_order: int = NODE_1
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
                "//*[@data-testid='node-root']"
                '//*[@data-testid="node-add-requirement-first-action"]'
            ),
            by=By.XPATH,
        )
        return Form_EditRequirement(self.test_case)

    def do_node_add_requirement_above(
        self, field_order: int = NODE_1
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
        self, field_order: int = NODE_1
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
        self, field_order: int = NODE_1
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

    def do_confirm_action(self) -> None:
        self.test_case.click(
            selector=('//*[@data-testid="confirm-action"]'),
            by=By.XPATH,
        )
