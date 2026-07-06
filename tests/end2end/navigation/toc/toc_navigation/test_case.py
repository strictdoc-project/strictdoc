from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.collapsible_list import CollapsibleList
from tests.end2end.helpers.components.toc import TOC
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

            # start: on the document tree
            screen_project_index.assert_on_screen()

            # go to document
            screen_document = screen_project_index.do_click_on_first_document()
            screen_toc: TOC = screen_document.get_toc()

            # toc is on the document view, opened
            screen_document.assert_on_screen_document()
            screen_toc.assert_toc_opened()

            section_without_uid = screen_document.get_node(1)
            section_with_uid = screen_document.get_node(2)
            # Requirement #1 has not a title and doesn't go in the TOC
            requirement_with_title = screen_document.get_node(4)

            section_without_uid.assert_requirement_title("Section without UID")
            section_with_uid.assert_requirement_title("Section with UID")
            requirement_with_title.assert_requirement_title(
                "Requirement 2 title"
            )
            requirement_with_title.assert_requirement_uid_contains("REQ_02")

            toc_section_without_uid_anchor = "1-Section-without-UID"
            toc_section_with_uid_anchor = "SECTION_01"
            toc_requirement_with_title_anchor = "REQ_02"

            screen_toc.do_toc_go_to_anchor(toc_section_without_uid_anchor)
            screen_document.assert_target_by_anchor(
                toc_section_without_uid_anchor
            )
            screen_toc.do_toc_go_to_anchor(toc_section_with_uid_anchor)
            screen_document.assert_target_by_anchor(toc_section_with_uid_anchor)
            screen_toc.do_toc_go_to_anchor(toc_requirement_with_title_anchor)
            screen_document.assert_target_by_anchor(
                toc_requirement_with_title_anchor
            )

            # TOC - expanding a collapsed branch when navigating to its anchor

            collapsible_list: CollapsibleList = (
                screen_document.get_collapsible_list()
            )
            collapsible_list.do_bulk_expand_all()

            # Collapse "Child section" so its own child ("Grandchild section")
            # becomes hidden.
            collapsible_list.do_toggle_collapsible("Child section")
            collapsible_list.assert_is_collapsed("Child section")
            collapsible_list.assert_visible_not("Grandchild section")

            # Also collapse "Parent section" so "Child section" itself
            # becomes hidden.
            collapsible_list.do_toggle_collapsible("Parent section")
            collapsible_list.assert_is_collapsed("Parent section")
            collapsible_list.assert_visible_not("Child section")

            base_url = self.get_current_url().split("#")[0]

            # Navigate to the page directly on a hidden anchor (e.g. an
            # external/bookmarked link), as opposed to clicking inside the
            # TOC. Expected: the collapsed ancestor branch ("Parent section")
            # opens up to the anchor, revealing "Child section".
            self.open(f"{base_url}#SECTION_CHILD")
            collapsible_list.assert_is_expanded("Parent section")
            collapsible_list.assert_visible("Child section")
            screen_toc.assert_toc_link_has_attribute(
                "SECTION_CHILD", "targeted"
            )

            # "Child section" is itself a collapsed folder: its own child
            # ("Grandchild section") must stay hidden — the branch opens up
            # to the anchor, not deeper than it.
            collapsible_list.assert_is_collapsed("Child section")
            collapsible_list.assert_visible_not("Grandchild section")

        assert test_setup.compare_sandbox_and_expected_output()
