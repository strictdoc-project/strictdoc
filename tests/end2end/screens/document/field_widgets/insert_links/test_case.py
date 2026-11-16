"""
@relation(SDOC-SRS-208, scope=file)
"""

from selenium.webdriver.common.keys import Keys

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.link_widget import LinkWidget
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

            link_widget = LinkWidget(self, "STATEMENT")

            # "[LINK:" opens the popup. Enter chooses the first target.
            link_widget.do_place_caret_after("First paragraph.")
            link_widget.do_type_at_caret(" See [LINK: over")
            link_widget.wait_for_options(["SECT-1"])
            link_widget.do_choose_by_enter()

            # A click chooses a target.
            link_widget.do_type_at_caret(" and [LINK: anch")
            link_widget.wait_for_options(["ANCHOR-1"])
            link_widget.do_choose_by_click("ANCHOR-1")

            # Escape closes only the popup, and the typed text stays. The
            # popup stays closed while the user types the same trigger. A "/"
            # after "[LINK:" is a part of the UID, so it does not open the
            # insert menu.
            link_widget.do_type_at_caret(" [LINK: ")
            link_widget.wait_for_options(["SECT-1", "ANCHOR-1", "REQ-1"])
            link_widget.do_close_popup_by_escape()
            link_widget.do_type_at_caret("x/")
            link_widget.assert_popup_closed()
            link_widget.assert_insert_menu_closed()
            form.assert_on_form()

            # After the closed trigger is deleted, a new trigger at the same
            # place opens the popup again.
            link_widget.do_type_at_caret(Keys.BACKSPACE * len("[LINK: x/"))
            link_widget.do_type_at_caret("[LINK: ")
            link_widget.wait_for_options(["SECT-1", "ANCHOR-1", "REQ-1"])
            link_widget.do_close_popup_by_escape()
            link_widget.do_type_at_caret(Keys.BACKSPACE * len(" [LINK: "))

            # "/" inside a word opens the insert menu, the text after "/"
            # filters it. The link goes to the caret position with spaces
            # around it.
            link_widget.do_place_caret_after("Fir")
            link_widget.do_type_at_caret("/li")
            link_widget.assert_insert_menu_open()
            link_widget.assert_insert_items(["link"])
            link_widget.do_choose_insert_item_by_enter()
            link_widget.do_type_at_caret("over")
            link_widget.wait_for_options(["SECT-1"])
            link_widget.do_choose_by_enter()

            # The insert button on a blank line opens the same menu. On a
            # blank line, the link forms its own paragraph.
            link_widget.do_place_caret_on_next_line("[LINK: ANCHOR-1]")
            link_widget.do_open_insert_menu()
            link_widget.do_choose_insert_item("link")
            # A query can have several words.
            link_widget.do_type_at_caret("target req")
            link_widget.wait_for_options(["REQ-1"])
            link_widget.do_choose_by_enter()

            # Before a space, the link gets no space after it.
            link_widget.do_place_caret_after("Second")
            link_widget.do_type_at_caret("/")
            link_widget.do_choose_insert_item("link")
            link_widget.do_type_at_caret("target")
            link_widget.wait_for_options(["REQ-1"])
            link_widget.do_choose_by_click("REQ-1")

            link_widget.assert_field_text(
                "Fir [LINK: SECT-1] st paragraph. See [LINK: SECT-1] and"
                " [LINK: ANCHOR-1]\n"
                "\n"
                "[LINK: REQ-1]\n"
                "\n"
                "Second [LINK: REQ-1] paragraph.\n"
            )

            form.do_form_submit()
            screen_document.assert_text("Target requirement")

        assert test_setup.compare_sandbox_and_expected_output()
