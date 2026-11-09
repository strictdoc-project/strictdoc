"""
Hovering or focusing a relation link shows a preview card:
- Parent and Child links, with and without a role, on the same page and
  across documents: the linked node's UID, title and STATEMENT.
- File links: the file path and the first lines of the linked range, cut at
  15 lines with a note when the range is longer.
Covered for the static HTML export (opened from file://) and for the server,
on the DOCUMENT screen and, for the static export, on the TRACE screen.
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


CHILD_STATEMENT = "The cross-document child statement."


def parent_link_of(uid: str) -> str:
    return (
        f"//sdoc-node[.//sdoc-anchor[@id='{uid}']]"
        "//a[contains(@class, 'requirement__link-parent')]"
    )


def child_link_of(uid: str, child_uid: str) -> str:
    return (
        f"//sdoc-node[.//sdoc-anchor[@id='{uid}']]"
        "//a[contains(@class, 'requirement__link-child')]"
        f"[.//*[normalize-space()='{child_uid}']]"
    )


def file_link_of(uid: str, first_line: int) -> str:
    return (
        f"(//sdoc-node[.//sdoc-anchor[@id='{uid}']]"
        "//a[contains(@class, 'requirement__link-file')]"
        f"[contains(@href, '#{uid}#{first_line}#')])[1]"
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

    def show_preview_of(self, link: str) -> None:
        self.hover_on_element(AWAY_FROM_CARD)
        self.assert_element_not_visible(PREVIEW, timeout=5)
        self.scroll_to(link, by="xpath")
        self.hover_on_element(link, by="xpath")
        self.assert_element_visible(PREVIEW, timeout=10)

    def check_child_role_and_file_links(self, base_url: str) -> None:
        # A Child link to another document.
        self.open(base_url + "input/parent.html")
        self.show_preview_of(child_link_of("REQ-PARENT-1", "REQ-CROSS-CHILD"))
        self.assert_text("REQ-CROSS-CHILD", PREVIEW)
        self.assert_text(CHILD_STATEMENT, PREVIEW, timeout=10)

        # A Parent link with a custom role shows the role next to the title.
        self.open(base_url + "input/source.html")
        self.show_preview_of(parent_link_of("REQ-SOURCE"))
        self.assert_preview_shows_parent()
        self.assert_text("(Refines)", PREVIEW)

        # A File link with a short line range shows all of its lines.
        self.show_preview_of(file_link_of("REQ-SOURCE", 1))
        self.assert_text("src/example.py, lines: 1-2", PREVIEW)
        self.assert_text('return "<short> & sweet"', PREVIEW, timeout=10)
        self.assert_element(f"{PREVIEW} pre.code .nf")
        self.assert_element_not_present(
            f"{PREVIEW} .relation_preview-truncated"
        )

        # A File link to a long function is cut at 15 lines.
        self.show_preview_of(file_link_of("REQ-SOURCE", 5))
        self.assert_text("lines: 5-23", PREVIEW)
        self.assert_text("(Implementation)", PREVIEW)
        self.assert_text("def long_function():", PREVIEW, timeout=10)
        self.assert_text("total += 12", PREVIEW)
        self.assert_text_not_visible("total += 13", PREVIEW)
        self.assert_text("Showing 15 of 19 lines.", PREVIEW)

        self.assert_no_js_errors()

    def test_static_export(self):
        with SDocTestHTMLExporter(input_path=path_to_this_test_file_folder) as (
            exporter
        ):
            base_url = exporter.get_output_path_as_uri() + "relation_preview/"
            self.check_same_and_cross_document(base_url)
            self.check_child_role_and_file_links(base_url)

            # The TRACE screen links to the TRACE page of another document.
            self.open(base_url + "input/child-TRACE.html")
            self.show_preview_of(parent_link_of("REQ-CROSS-CHILD"))
            self.assert_preview_shows_parent()
            self.assert_no_js_errors()

    def test_server(self):
        with SDocTestServer(input_path=path_to_this_test_file_folder) as (
            test_server
        ):
            base_url = test_server.get_host_and_port() + "/relation_preview/"
            self.check_same_and_cross_document(base_url)
            self.check_child_role_and_file_links(base_url)
