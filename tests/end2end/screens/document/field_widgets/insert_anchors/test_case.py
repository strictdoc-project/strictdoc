"""
@relation(SDOC-SRS-208, scope=file)
"""

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.anchor_widget import AnchorWidget
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

            anchor_widget = AnchorWidget(self, "STATEMENT")

            # Escape closes the form, and the field stays as it was.
            anchor_widget.do_place_caret_on_next_line("First paragraph.")
            anchor_widget.do_open_form()
            anchor_widget.do_close_form_by_escape()
            form.assert_on_form()
            anchor_widget.assert_field_text(
                "First paragraph.\n\nSecond paragraph.\n"
            )

            # The UID syntax, a UID used in the project, and a title that
            # the tag cannot hold block the insert.
            anchor_widget.do_place_caret_on_next_line("First paragraph.")
            anchor_widget.do_open_form()
            anchor_widget.do_type_uid("-unit")
            anchor_widget.assert_uid_message("A UID starts with a letter")
            anchor_widget.assert_insert_disabled()
            anchor_widget.do_type_uid("REQ-1")
            anchor_widget.assert_uid_message(
                "This UID is already used by REQUIREMENT."
            )
            anchor_widget.assert_insert_disabled()
            anchor_widget.do_type_uid("UNIT")
            anchor_widget.do_type_title('"Unit", plural')
            anchor_widget.assert_title_message(
                'A title with "," or "]" cannot contain double quotes.'
            )
            anchor_widget.assert_insert_disabled()

            # A title with "," goes in double quotes.
            anchor_widget.do_type_title("Unit, plural")
            anchor_widget.assert_insert_enabled()
            anchor_widget.do_insert_by_enter()
            anchor_widget.assert_field_text(
                "First paragraph.\n"
                "\n"
                '[ANCHOR: UNIT, "Unit, plural"]\n'
                "\n"
                "Second paragraph.\n"
            )

            # The new anchor is not saved yet, but the form finds its UID in
            # the field text.
            anchor_widget.do_place_caret_on_next_line('plural"]')
            anchor_widget.do_open_form()
            anchor_widget.do_type_uid("UNIT")
            anchor_widget.assert_uid_message(
                "This field already has an anchor with this UID."
            )
            anchor_widget.assert_insert_disabled()
            anchor_widget.do_close_form_by_escape()

            form.do_form_submit()
            screen_document.assert_text("Second paragraph.")

        assert test_setup.compare_sandbox_and_expected_output()
