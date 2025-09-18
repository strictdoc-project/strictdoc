from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.diff.diff import Screen_Diff
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.helpers.screens.project_index.form_add_document import (
    Form_AddDocument,
)
from tests.end2end.helpers.screens.project_index.form_import_reqif import (
    Form_ImportReqIF,
)
from tests.end2end.helpers.screens.project_statistics.project_statistics import (
    Screen_ProjectStatistics,
)
from tests.end2end.helpers.screens.search.search import Screen_Search
from tests.end2end.helpers.screens.source_coverage.screen_source_coverage import (
    Screen_SourceCoverage,
)
from tests.end2end.helpers.screens.traceability_matrix.screen_requirements_coverage import (
    Screen_RequirementsCoverage,
)
from tests.end2end.helpers.screens.tree_map.tree_map import Screen_TreeMap


class Screen_ProjectIndex:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="document-tree"]',
            by=By.XPATH,
        )
        self.test_case.wait_for_ready_state_complete()
        self.assert_no_js_and_404_errors()

    def assert_no_js_and_404_errors(self) -> None:
        self.test_case.assert_no_404_errors()
        self.test_case.assert_no_js_errors()

    def assert_header_project_name(self, project_title: str) -> None:
        self.test_case.assert_element(
            "//*[@class='header__project_name']"
            f"[contains(., '{project_title}')]",
            by=By.XPATH,
        )

    def assert_contains_document(self, document_title: str) -> None:
        self.test_case.assert_element(
            "//*[@data-testid='tree-file-link']"
            f"//*[contains(., '{document_title}')]",
            by=By.XPATH,
        )

    def assert_document_is_hidden(self, document_title: str) -> None:
        # fragment is hidden
        self.test_case.assert_element_not_visible(
            "//*[@data-testid='tree-file-link']"
            f"//*[contains(., '{document_title}')]",
            by=By.XPATH,
        )

    def assert_empty_tree(self) -> None:
        self.test_case.assert_element(
            "//*[@data-testid='document-tree-empty-text']"
            "[contains(., 'The document tree has no documents yet.')]",
            by=By.XPATH,
        )

    def assert_link_to_project_statistics_present(self) -> None:
        self.test_case.assert_element(
            '//a[@data-testid="project-tree-link-project-statistics"]',
            by=By.XPATH,
        )

    def assert_link_to_requirements_coverage_present(self) -> None:
        self.test_case.assert_element(
            '//a[@data-testid="project-tree-link-requirements-coverage"]',
            by=By.XPATH,
        )

    def assert_link_to_source_coverage_present(self) -> None:
        self.test_case.assert_element(
            '//a[@data-testid="project-tree-link-source-coverage"]',
            by=By.XPATH,
        )

    def assert_link_to_search_screen_present(self) -> None:
        self.test_case.assert_element(
            '//a[@data-testid="project-tree-link-search"]',
            by=By.XPATH,
        )

    def assert_link_to_diff_screen_present(self) -> None:
        self.test_case.assert_element(
            '//a[@data-testid="project-tree-link-diff"]',
            by=By.XPATH,
        )

    def do_click_on_first_document(self) -> Screen_Document:
        self.test_case.click_xpath('//*[@data-testid="tree-file-link"]')
        return Screen_Document(self.test_case)

    def do_click_on_project_statistics_link(
        self,
    ) -> Screen_ProjectStatistics:
        self.test_case.click_xpath(
            '//a[@data-testid="project-tree-link-project-statistics"]',
        )
        return Screen_ProjectStatistics(self.test_case)

    def do_click_on_requirements_coverage_link(
        self,
    ) -> Screen_RequirementsCoverage:
        self.test_case.click_xpath(
            '//a[@data-testid="project-tree-link-requirements-coverage"]',
        )
        return Screen_RequirementsCoverage(self.test_case)

    def do_click_on_source_coverage_link(self) -> Screen_SourceCoverage:
        self.test_case.click_xpath(
            '//a[@data-testid="project-tree-link-source-coverage"]',
        )
        return Screen_SourceCoverage(self.test_case)

    def do_click_on_search_screen_link(
        self,
    ) -> Screen_Search:
        self.test_case.click_xpath(
            '//a[@data-testid="project-tree-link-search"]',
        )
        return Screen_Search(self.test_case)

    def do_click_on_diff_screen_link(
        self,
    ) -> Screen_Diff:
        self.test_case.click_xpath(
            '//a[@data-testid="project-tree-link-diff"]',
        )
        return Screen_Diff(self.test_case)

    def do_click_on_the_document(self, doc_order: int = 1) -> Screen_Document:
        self.test_case.click_xpath(
            f"(//*[@data-testid='tree-file-link'])[{doc_order}]"
        )
        return Screen_Document(self.test_case)

    def do_click_on_the_document_with_title(
        self, document_title: str
    ) -> Screen_Document:
        self.test_case.click_xpath(
            f"//a[@data-testid='tree-file-link'][.//div[@class='project_tree-file-title' and normalize-space(text())='{document_title}']]"
        )
        return Screen_Document(self.test_case)

    def do_click_on_tree_map_screen_link(
        self,
    ) -> Screen_TreeMap:
        self.test_case.click_xpath(
            '//a[@data-testid="project-tree-link-tree-map"]',
        )
        return Screen_TreeMap(self.test_case)

    #
    # Static HTML search.
    #

    def do_enter_search_query(self, search_query: str) -> None:
        input_xpath = "//input[@data-testid='static-html-search-input']"

        # We simulate a user typing the supplied field_value.
        self.test_case.type(input_xpath, search_query, by=By.XPATH)

    def do_go_to_search_result(self, result: int) -> None:
        assert result > 0, f"Result is 1-based index: {result}"
        xpath = f"(//div[@class='static_search-result-node-link']//a)[{result}]"
        self.test_case.click_xpath(xpath)

    def do_click_search_result_start(self) -> None:
        input_xpath = "//span[@data-testid='static-html-search-button-start']"
        self.test_case.click_xpath(input_xpath)

    def do_click_search_result_previous(self) -> None:
        input_xpath = (
            "//span[@data-testid='static-html-search-button-previous']"
        )
        self.test_case.click_xpath(input_xpath)

    def do_click_search_result_next(self) -> None:
        input_xpath = "//span[@data-testid='static-html-search-button-next']"
        self.test_case.click_xpath(input_xpath)

    def do_click_search_result_end(self) -> None:
        input_xpath = "//span[@data-testid='static-html-search-button-end']"
        self.test_case.click_xpath(input_xpath)

    def assert_search_results(
        self, range_start: int, range_end: int, total: int
    ) -> None:
        self.test_case.assert_text("Results:")
        self.test_case.assert_text(f"{range_start}–{range_end}")
        self.test_case.assert_text(f"from {total}")

    #
    # Add new document
    #

    def do_open_modal_form_add_document(self) -> Form_AddDocument:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.test_case.click_xpath(
            '(//*[@data-testid="tree-add-document-action"])'
        )
        self.test_case.assert_element("//sdoc-modal", by=By.XPATH)
        return Form_AddDocument(self.test_case)

    # Import / Export

    def do_open_modal_import_reqif(self) -> Form_ImportReqIF:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.test_case.click_xpath(
            '//*[@data-testid="tree-import-reqif-action"]'
        )
        self.test_case.assert_element("//sdoc-modal", by=By.XPATH)
        return Form_ImportReqIF(self.test_case)

    def do_export_reqif(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="tree-export-reqif-action"]'
        )

    # project_tree_controls
    # Show/Hide fragments

    def assert_project_tree_controls_present(self) -> None:
        self.test_case.assert_element(
            '//*[@id="project_tree_controls"]',
            by=By.XPATH,
        )

    def do_click_on_fragment_switcher(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="show-hide-fragments-toggler"]'
        )
        return Screen_Document(self.test_case)
