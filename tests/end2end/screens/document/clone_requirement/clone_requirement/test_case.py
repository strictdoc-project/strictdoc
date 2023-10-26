from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")
            screen_document.assert_text("Hello world!")

            # Assert clone button exists on Requirement
            self.assert_element_present(
                "//*[@data-testid='node-requirement']//*[@data-testid='node-clone-action']",
                by=By.XPATH,
            )
            # Assert clone button does not exist on Section
            self.assert_element_not_present(
                "//*[@data-testid='node-section']//*[@data-testid='node-clone-action']",
                by=By.XPATH,
            )

            requirement = screen_document.get_requirement()
            requirement.assert_requirement_title("Requirement title", "2")
            requirement.assert_requirement_uid_contains("REQ-1")
            requirement.assert_requirement_statement_contains(
                "Requirement statement."
            )
            requirement.assert_requirement_rationale_contains(
                "Requirement rationale."
            )

            form_cloned_requirement = requirement.do_clone_requirement()
            form_cloned_requirement.do_form_submit()

        assert test_setup.compare_sandbox_and_expected_output()
