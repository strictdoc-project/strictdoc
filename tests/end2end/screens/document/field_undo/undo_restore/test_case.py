"""
@relation(SDOC-SRS-211, scope=file)
"""

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.field_widgets import FieldWidgets
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
            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()
            form = screen_document.get_node().do_open_form_edit_requirement()
            form.assert_on_form()

            # The server rejects the new UID: the requirement has child
            # relations. The Restore button writes the old UID back.
            form.do_fill_in_field_uid("Modified UID")
            form.do_form_submit_and_catch_error(
                "Not supported yet: "
                "Renaming a requirement UID when the requirement has child "
                "requirement relations. For now, manually delete the relations,"
                " rename the UID, recreate the relations.",
            )
            form.do_restore_uid_field()

            # The restore is one undo step of the field.
            uid = FieldWidgets(self, "UID")
            uid.wait_for_field_text("REQ-001")
            uid.do_place_caret_after("REQ-001")
            uid.do_undo()
            uid.wait_for_field_text("Modified UID")
            uid.do_redo()
            uid.wait_for_field_text("REQ-001")

            # The form sends the restored UID.
            form.do_form_submit()
            screen_document.assert_text("REQ-001")

        assert test_setup.compare_sandbox_and_expected_output()
