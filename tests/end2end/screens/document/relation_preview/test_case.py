"""
Hovering or focusing a parent relation link shows a preview card with the
parent node's UID, title and STATEMENT, both when the parent is on the same
page and when it lives in another document. Covered for the static HTML
export (opened from file://) and for the server.
"""

import os

from selenium.webdriver.common.keys import Keys

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_input = os.path.join(path_to_this_test_file_folder, "input")

PREVIEW = "[data-testid='relation-preview']"
# Somewhere the card never covers, to move the pointer off the link.
AWAY_FROM_CARD = "[data-testid='header-placeholder']"
PARENT_STATEMENT = "The parent statement shall keep <tags> & markup."


def parent_link_of(uid: str) -> str:
    return (
        f"//sdoc-node[.//sdoc-anchor[@id='{uid}']]"
        "//a[contains(@class, 'requirement__link-parent')]"
    )


class Test(E2ECase):
    def assert_preview_shows_parent(self) -> None:
        self.assert_element_visible(PREVIEW, timeout=10)
        self.assert_text("REQ-PARENT-1", PREVIEW)
        self.assert_text("Parent requirement", PREVIEW)
        self.assert_text(PARENT_STATEMENT, PREVIEW, timeout=10)
        # The statement is rendered markup, not escaped text.
        self.assert_element(f"{PREVIEW} strong")

    def check_same_and_cross_document(self, base_url: str) -> None:
        # Same document: the parent is read from the page itself.
        self.open(base_url + "input/parent.html")
        self.assert_element_not_visible(PREVIEW)
        self.hover_on_element(parent_link_of("REQ-SAME-CHILD"), by="xpath")
        self.assert_preview_shows_parent()

        # Moving the pointer away hides the card again.
        self.hover_on_element(AWAY_FROM_CARD)
        self.assert_element_not_visible(PREVIEW, timeout=5)

        # Cross document: the parent comes from parent-relation-previews.js.
        self.open(base_url + "input/child.html")
        self.hover_on_element(parent_link_of("REQ-CROSS-CHILD"), by="xpath")
        self.assert_preview_shows_parent()

        # Keyboard: focusing the link shows the card, Escape hides it.
        self.hover_on_element(AWAY_FROM_CARD)
        self.assert_element_not_visible(PREVIEW, timeout=5)
        link = self.find_element(parent_link_of("REQ-CROSS-CHILD"), by="xpath")
        self.execute_script("arguments[0].focus();", link)
        self.assert_preview_shows_parent()
        self.assert_attribute(
            parent_link_of("REQ-CROSS-CHILD"),
            "aria-describedby",
            "sdoc-relation-preview",
            by="xpath",
        )
        link.send_keys(Keys.ESCAPE)
        self.assert_element_not_visible(PREVIEW, timeout=5)

        self.assert_no_js_errors()

    def test_static_export(self):
        with SDocTestHTMLExporter(input_path=path_to_this_test_file_folder) as (
            exporter
        ):
            self.check_same_and_cross_document(
                exporter.get_output_path_as_uri() + "relation_preview/"
            )

    def test_server(self):
        with SDocTestServer(input_path=path_to_this_test_file_folder) as (
            test_server
        ):
            self.check_same_and_cross_document(
                test_server.get_host_and_port() + "/relation_preview/"
            )
