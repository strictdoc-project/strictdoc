from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import (
    ViewType_Selector,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer
from tests.end2end.test_helpers import available_systems


# FIXME: This test fails on Windows with
#        Element {(//sdoc-node[@data-testid='node-requirement'])[2]//*[@data-testid='requirement-find-in-document']} was not present after 10 seconds!
#        We don't have a Windows machine to investigate this in detail.
@available_systems(["macos", "linux"])
class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document #1 title")
            screen_project_index.assert_contains_document("Document #2 title")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document #1 title")

            viewtype_selector = ViewType_Selector(self)
            screen_deep_traceability = (
                viewtype_selector.do_go_to_deep_traceability()
            )
            screen_deep_traceability.assert_on_screen_deep_traceability()

            requirement = screen_deep_traceability.get_requirement(2)
            requirement.assert_requirement_uid("REQ-002")

            screen_document_ = (
                requirement.do_go_to_this_requirement_in_document_view()
            )
            screen_document_.assert_on_screen_document()
            screen_document_.assert_target_by_anchor("1-REQ-002")

        assert test_setup.compare_sandbox_and_expected_output()
