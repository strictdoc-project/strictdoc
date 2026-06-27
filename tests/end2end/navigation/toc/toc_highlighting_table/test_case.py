from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.collapsible_list import CollapsibleList
from tests.end2end.helpers.components.toc import TOC
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
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
            screen_project_index.assert_on_screen()

            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            # TOC highlighting depends on the Table screen's content root
            # being recognized by toc_highlighting.js, same as on Document.
            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()

            screen_toc: TOC = screen_table.get_toc()
            collapsible_list: CollapsibleList = (
                screen_table.get_collapsible_list()
            )
            collapsible_list.do_bulk_expand_all()

            # Click a TOC link. If toc_highlighting.js initialized correctly
            # on this screen, the link is highlighted (targeted) and the
            # IntersectionObserver fires (intersected/parented).
            screen_toc.do_toc_go_to_anchor("SECTION_BEFORE_LONG_NODE")
            screen_toc.assert_toc_link_has_attribute(
                "SECTION_BEFORE_LONG_NODE", "targeted"
            )
            screen_toc.assert_toc_link_has_attribute(
                "SECTION_BEFORE_LONG_NODE", "intersected"
            )

            # A section far from the clicked one must not be highlighted.
            screen_toc.assert_toc_link_has_not_attribute(
                "SECTION_AFTER_LONG_NODE", "intersected"
            )

        assert test_setup.compare_sandbox_and_expected_output()
