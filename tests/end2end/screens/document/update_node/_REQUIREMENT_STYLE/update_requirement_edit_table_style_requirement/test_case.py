"""
@relation(SDOC-SRS-55, scope=file)
"""

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
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
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            requirement = screen_document.get_node()
            # Make sure that the table-based requirement is rendered.
            requirement.assert_requirement_style_table()

            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )
            form_edit_requirement.do_fill_in_field_uid("Modified UID")
            form_edit_requirement.do_fill_in_field_title("Modified title")
            form_edit_requirement.do_fill_in_field_statement(
                "Modified statement."
            )
            form_edit_requirement.do_fill_in_field_rationale(
                "Modified rationale."
            )
            form_edit_requirement.do_form_submit()

            requirement.assert_requirement_title("Modified title", "1")
            requirement.assert_requirement_uid_contains("Modified UID")
            requirement.assert_requirement_statement_contains(
                "Modified statement."
            )
            requirement.assert_requirement_rationale_contains(
                "Modified rationale."
            )
            # Make sure that after saving we return to the same display style
            # and the table-based requirement is rendered.
            requirement.assert_requirement_style_table()
            screen_document.assert_toc_contains("Modified title")

        assert test_setup.compare_sandbox_and_expected_output()
