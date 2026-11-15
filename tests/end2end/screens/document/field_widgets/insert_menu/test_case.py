"""
@relation(SDOC-SRS-208, scope=file)
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.anchor_widget import AnchorWidget
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

FIELD_TEXT = (
    "First line of the paragraph.\n"
    "Second line of the paragraph.\n"
    "\n"
    "Last paragraph.\n"
)


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

            widgets = AnchorWidget(self, "STATEMENT")

            # "/" inside a word opens the menu with a placeholder at the
            # caret. The placeholder is not part of the field text. Escape
            # closes the menu and keeps the "/".
            widgets.do_place_caret_after("Fir")
            widgets.do_type_at_caret("/")
            widgets.assert_insert_menu_open()
            widgets.assert_insert_items(["table", "link", "anchor"])
            widgets.assert_field_text(FIELD_TEXT.replace("Fir", "Fir/", 1))
            widgets.do_close_insert_menu_by_escape()
            form.assert_on_form()
            widgets.assert_field_text(FIELD_TEXT.replace("Fir", "Fir/", 1))
            widgets.do_type_at_caret(Keys.BACKSPACE)

            # The last item of the menu closes it.
            widgets.do_type_at_caret("/")
            widgets.do_close_insert_menu_by_click()
            widgets.do_type_at_caret(Keys.BACKSPACE)

            # A query that matches no item closes the menu, and the typed
            # text stays.
            widgets.do_type_at_caret("/zz")
            widgets.assert_insert_menu_closed()
            widgets.assert_field_text(FIELD_TEXT.replace("Fir", "Fir/zz", 1))
            widgets.do_type_at_caret(Keys.BACKSPACE * len("/zz"))

            # A block widget goes after the paragraph that holds the caret.
            # The "/" and the query are removed. With the caret line at the
            # bottom of the viewport, the new block is out of view, so the
            # page scrolls to the caret after it.
            widgets.do_add_space_above_field()
            widgets.do_scroll_caret_to_viewport_bottom()
            widgets.do_type_at_caret("/an")
            widgets.assert_insert_items(["anchor"])
            widgets.do_choose_insert_item_by_enter()
            self.assert_element(AnchorWidget.FORM, by=By.XPATH)
            widgets.do_type_uid("NEW-1")
            widgets.assert_insert_enabled()
            widgets.do_insert_by_enter()
            widgets.wait_for_caret_in_viewport()

            # At the end of the field, the block gets a blank line before it
            # only.
            widgets.do_place_caret_after("Last")
            widgets.do_type_at_caret("/")
            widgets.do_choose_insert_item("anchor")
            widgets.do_type_uid("NEW-2")
            widgets.assert_insert_enabled()
            widgets.do_insert_by_enter()

            widgets.assert_field_text(
                "First line of the paragraph.\n"
                "Second line of the paragraph.\n"
                "\n"
                "[ANCHOR: NEW-1]\n"
                "\n"
                "Last paragraph.\n"
                "\n"
                "[ANCHOR: NEW-2]\n"
            )

            form.do_form_submit()
            screen_document.assert_text("Last paragraph.")

        assert test_setup.compare_sandbox_and_expected_output()
