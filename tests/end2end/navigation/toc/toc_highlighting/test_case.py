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

            collapsible_list: CollapsibleList = (
                screen_document.get_collapsible_list()
            )
            collapsible_list.do_bulk_expand_all()

            # Click on the link in the TOC.
            # It is highlighted and gets the expected attributes.
            screen_toc.do_toc_go_to_anchor("SECTION_BEFORE_LONG_NODE")
            screen_toc.assert_toc_link_has_attribute(
                "SECTION_BEFORE_LONG_NODE", "parented"
            )
            screen_toc.assert_toc_link_has_attribute(
                "SECTION_BEFORE_LONG_NODE", "targeted"
            )
            screen_toc.assert_toc_link_has_attribute(
                "SECTION_BEFORE_LONG_NODE", "intersected"
            )

            # Click on the inline link to the anchor in the middle of long node.
            # Its beginning and end are both outside the screen.
            # It is the only one highlighted.
            # The nodes before and after it are not highlighted.
            self.click_xpath('(//*[@href="#ANCHOR-EXAMPLE"])[1]')
            screen_toc.assert_toc_link_has_attribute(
                "THE_LONG_NODE_ID", "intersected"
            )
            screen_toc.assert_toc_link_has_not_attribute(
                "SECTION_BEFORE_LONG_NODE", "intersected"
            )
            screen_toc.assert_toc_link_has_not_attribute(
                "SECTION_AFTER_LONG_NODE", "intersected"
            )

            # TOC - collapsing and highlighting

            # Step 1. initial child highlight when expanded

            # Start with expanded "Examples". A child inside this branch is in-view,
            # so the child TOC item ("THE_LONG_NODE_ID") is highlighted.
            # Parent ("SECTION_BEFORE_LONG_NODE") must not be highlighted.
            collapsible_list.assert_is_expanded("Examples")
            collapsible_list.assert_visible("Hello World")
            screen_toc.assert_toc_link_has_attribute(
                "THE_LONG_NODE_ID", "intersected"
            )
            screen_toc.assert_toc_link_has_not_attribute(
                "SECTION_BEFORE_LONG_NODE", "intersected"
            )

            # Step 2. highlight transfer to collapsed parent

            # Collapse "Examples". The highlighted child becomes hidden.
            # Expected behavior: highlight moves up to the collapsed parent item
            # ("SECTION_BEFORE_LONG_NODE"), which remains visible in TOC.
            collapsible_list.do_toggle_collapsible("Examples")  # collapse
            collapsible_list.assert_is_collapsed("Examples")
            collapsible_list.assert_visible_not("Hello World")
            screen_toc.assert_toc_link_has_attribute(
                "SECTION_BEFORE_LONG_NODE", "intersected"
            )

            # Step 3. highlight return to child after re-expanding

            # Expand "Examples" again and navigate to a child item.
            # Expected behavior: highlight is recalculated back to the visible child
            # ("THE_LAST_SECTION"), and parent highlight is removed.
            collapsible_list.do_toggle_collapsible("Examples")  # expand
            collapsible_list.assert_is_expanded("Examples")
            screen_toc.assert_toc_link_has_attribute(
                "THE_LONG_NODE_ID", "intersected"
            )
            screen_toc.assert_toc_link_has_not_attribute(
                "SECTION_BEFORE_LONG_NODE", "intersected"
            )

            # Step 4. navigate to another child and verify child highlight
            collapsible_list.assert_visible("Last section")
            screen_toc.do_toc_go_to_anchor("THE_LAST_SECTION")
            screen_toc.assert_toc_link_has_attribute(
                "THE_LAST_SECTION", "intersected"
            )
            screen_toc.assert_toc_link_has_not_attribute(
                "SECTION_BEFORE_LONG_NODE", "intersected"
            )

            # Step 5. transfer back to parent after collapsing again

            # Collapse the branch once more while the child is highlighted.
            # Expected behavior: highlight moves from the hidden child back to
            # the visible collapsed parent.
            collapsible_list.do_toggle_collapsible("Examples")  # collapse
            collapsible_list.assert_is_collapsed("Examples")
            collapsible_list.assert_visible_not("Last section")
            screen_toc.assert_toc_link_has_attribute(
                "SECTION_BEFORE_LONG_NODE", "intersected"
            )
