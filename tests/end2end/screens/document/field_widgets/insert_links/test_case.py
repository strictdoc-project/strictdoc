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

            # "@" opens the popup. Enter chooses the first target.
            link_widget.do_place_caret_after("First paragraph.")
            link_widget.do_type_at_caret(" See @over")
            link_widget.wait_for_options(["SECT-1"])
            link_widget.do_choose_by_enter()

            # "[LINK:" opens the popup too. A click chooses a target.
            link_widget.do_type_at_caret(" and [LINK: anch")
            link_widget.wait_for_options(["ANCHOR-1"])
            link_widget.do_choose_by_click("ANCHOR-1")

            # Escape closes only the popup, and the typed text stays. The
            # popup stays closed while the user types the same trigger.
            link_widget.do_type_at_caret(" @")
            link_widget.wait_for_options(["SECT-1", "ANCHOR-1", "REQ-1"])
            link_widget.do_close_popup_by_escape()
            link_widget.do_type_at_caret("x")
            link_widget.assert_popup_closed()
            form.assert_on_form()

            # After "@", a query with a space that finds nothing is plain
            # text: the popup closes and stays closed.
            link_widget.do_type_at_caret(" @overview")
            link_widget.wait_for_options(["SECT-1"])
            link_widget.do_type_at_caret(" zzz")
            link_widget.wait_for_popup_closed()
            link_widget.do_type_at_caret(" end")
            link_widget.assert_popup_closed()

            # After the closed trigger is deleted, a new "@" at the same
            # place opens the popup again.
            link_widget.do_type_at_caret(
                Keys.BACKSPACE * len("@overview zzz end")
            )
            link_widget.do_type_at_caret("@")
            link_widget.wait_for_options(["SECT-1", "ANCHOR-1", "REQ-1"])
            link_widget.do_close_popup_by_escape()
            link_widget.do_type_at_caret(Keys.BACKSPACE)
            link_widget.do_type_at_caret("@overview zzz end")
            link_widget.wait_for_popup_closed()

            # The Link item of the insert menu opens the popup on the blank
            # line.
            link_widget.do_place_caret_on_next_line("zzz end")
            link_widget.do_open_insert_menu()
            link_widget.do_choose_insert_item("link")
            # A query can have several words.
            link_widget.do_type_at_caret("target req")
            link_widget.wait_for_options(["REQ-1"])
            link_widget.do_choose_by_enter()

            link_widget.assert_field_text(
                "First paragraph. See [LINK: SECT-1] and [LINK: ANCHOR-1] @x"
                " @overview zzz end\n"
                "\n"
                "[LINK: REQ-1]\n"
                "\n"
                "Second paragraph.\n"
            )

            form.do_form_submit()
            screen_document.assert_text("Target requirement")

        assert test_setup.compare_sandbox_and_expected_output()
