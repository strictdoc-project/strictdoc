from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

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
from tests.end2end.helpers.screens.requirements_coverage.screen_requirements_coverage import (  # noqa: E501
    Screen_RequirementsCoverage,
)
from tests.end2end.helpers.screens.source_coverage.screen_source_coverage import (  # noqa: E501
    Screen_SourceCoverage,
)


class Screen_ProjectIndex:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="document-tree"]',
            by=By.XPATH,
        )
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

    def do_click_on_the_document(self, doc_order: int = 1) -> Screen_Document:
        self.test_case.click_xpath(
            f"(//*[@data-testid='tree-file-link'])[{doc_order}]"
        )
        return Screen_Document(self.test_case)

    # Add new document

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
