from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
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

            section_without_uid = screen_document.get_section(1)
            section_with_uid = screen_document.get_section(2)
            # Requirement #1 has not a title and doesn't go in the TOC
            requirement_with_title = screen_document.get_requirement(2)

            section_without_uid.assert_section_title("Section without UID")
            section_with_uid.assert_section_title("Section with UID")
            requirement_with_title.assert_requirement_title(
                "Requirement 2 title"
            )
            requirement_with_title.assert_requirement_uid_contains("REQ_02")

            # # FIXME after:
            # # TODO: https://github.com/strictdoc-project/strictdoc/issues/1382

            # Anchor generation formats
            # * in section:
            # f"{unique_prefix}-{self._string_to_link(node.title)}" # noqa: ERA001
            # * in requirement:
            # f"{unique_prefix}-{self._string_to_link(node.reserved_uid)}" # noqa: ERA001
            # f"{unique_prefix}-{self._string_to_link(node.reserved_title)}" # noqa: ERA001
            # *** where unique_prefix = node.context.title_number_string

            toc_section_without_uid_anchor = "1-Section-without-UID"
            toc_section_with_uid_anchor = "2-Section-with-UID"
            toc_requirement_with_title_anchor = "3-REQ_02"

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

        assert test_setup.compare_sandbox_and_expected_output()
