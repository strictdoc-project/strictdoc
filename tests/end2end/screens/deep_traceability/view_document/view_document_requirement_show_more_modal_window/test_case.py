from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import (
    ViewType_Selector,
)
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
            screen_project_index.assert_contains_document("Document title")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document title")

            viewtype_selector = ViewType_Selector(self)
            screen_deep_traceability = (
                viewtype_selector.do_go_to_deep_traceability()
            )
            screen_deep_traceability.assert_on_screen_deep_traceability()

            section = screen_deep_traceability.get_node()
            section.assert_requirement_title("Section title")

            requirement = screen_deep_traceability.get_node(2)

            requirement.assert_requirement_title("Requirement title")
            requirement.assert_requirement_uid("REC_UID")
            requirement.assert_requirement_statement_contains(
                "Requirement statement."
            )
            requirement.assert_node_does_not_contain("Requirement rationale.")

            modal = requirement.do_open_modal_requirement()
            modal.assert_modal()

            # requirement in modal turns out to be the last one on the page
            last = 3

            modal_requirement = screen_deep_traceability.get_requirement_modal(
                last
            )
            modal_requirement.assert_requirement_title("Requirement title")
            modal_requirement.assert_requirement_uid_contains("REC_UID")
            modal_requirement.assert_requirement_statement_contains(
                "Requirement statement."
            )
            modal_requirement.assert_requirement_rationale_contains(
                "Requirement rationale."
            )

            modal.do_close_modal()

        assert test_setup.compare_sandbox_and_expected_output()
