"""
@relation(SDOC-SRS-211, scope=file)
"""

from selenium.webdriver.common.keys import Keys

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.field_widgets import FieldWidgets
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


# The form shows a multiline field with a line break at the end. The typing
# is not at the end of the field: there, Firefox deletes the last line break
# together with the character before it.
def statement_text(line_one: str) -> str:
    return f"Line one.{line_one}\nLine two.\n"


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

            # Each typed character is one undo step.
            statement = FieldWidgets(self, "STATEMENT")
            statement.do_place_caret_after("Line one.")
            statement.do_type_at_caret(" ab")
            statement.assert_field_text(statement_text(" ab"))

            statement.do_undo()
            statement.wait_for_field_text(statement_text(" a"))
            statement.do_undo()
            statement.wait_for_field_text(statement_text(" "))
            statement.do_redo()
            statement.wait_for_field_text(statement_text(" a"))
            statement.do_redo()
            statement.wait_for_field_text(statement_text(" ab"))

            # Ctrl+Y redoes too.
            statement.do_undo()
            statement.wait_for_field_text(statement_text(" a"))
            statement.do_redo_by_ctrl_y()
            statement.wait_for_field_text(statement_text(" ab"))

            # Each deleted character is one undo step. After the undo, the
            # caret is after the restored character.
            statement.do_type_at_caret(Keys.BACKSPACE + Keys.BACKSPACE)
            statement.assert_field_text(statement_text(" "))
            statement.do_undo()
            statement.wait_for_field_text(statement_text(" a"))
            statement.do_type_at_caret("!")
            statement.assert_field_text(statement_text(" a!"))

            # Each field has its own history: Ctrl+Z in the single-line
            # field changes only that field, and does nothing when the
            # field has no more steps.
            title = FieldWidgets(self, "TITLE")
            title.do_place_caret_after("Title")
            title.do_type_at_caret("X")
            title.assert_field_text("TitleX")
            title.do_undo()
            title.wait_for_field_text("Title")
            title.do_undo()
            title.assert_field_text("Title")
            statement.assert_field_text(statement_text(" a!"))

            # The form sends the text after undo and redo.
            form.do_form_submit()
            screen_document.assert_text("a!")

        assert test_setup.compare_sandbox_and_expected_output()
