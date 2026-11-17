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

# The form shows a multiline field with a line break at the end.
TYPED = "Line one.\nLine two. Typed.\n"
PASTED = "Line one.\nLine two. Typed.\nPasted one.\nPasted two.\n"


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

            # A multiline field. The paste at the end of the field is one
            # undo step, and the typing before it can still be undone, one
            # character at a time.
            statement = FieldWidgets(self, "STATEMENT")
            statement.do_place_caret_after("Line two.")
            statement.do_type_at_caret(" Typed.")
            statement.do_paste_at_caret("\nPasted one.\nPasted two.")
            statement.assert_field_text(PASTED)

            statement.do_undo()
            statement.wait_for_field_text(TYPED)
            statement.do_undo()
            statement.wait_for_field_text(TYPED.replace("Typed.", "Typed"))
            statement.do_redo()
            statement.wait_for_field_text(TYPED)
            statement.do_redo()
            statement.wait_for_field_text(PASTED)

            # A single-line field: the pasted line breaks become spaces.
            title = FieldWidgets(self, "TITLE")
            title.do_place_caret_after("Title")
            title.do_paste_at_caret("\nSingle\nline")
            title.assert_field_text("Title Single line")

            title.do_undo()
            title.wait_for_field_text("Title")
            title.do_redo()
            title.wait_for_field_text("Title Single line")

            # The hidden fields get the text after undo and redo too.
            form.do_form_submit()
            screen_document.assert_text("Pasted two.")

        assert test_setup.compare_sandbox_and_expected_output()
