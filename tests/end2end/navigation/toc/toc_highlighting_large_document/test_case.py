from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.document_fixtures import (
    write_long_document_for_toc_geometry,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

DOCUMENT_NODE_COUNT = 600
SCROLL_TARGET = "TOC-PERF-0500"


class Test(E2ECase):
    def test_toc_highlighting_reads_only_near_viewport_geometry(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_document_for_toc_geometry(
            test_setup,
            node_count=DOCUMENT_NODE_COUNT,
        )

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "TOC Geometry Performance Document"
                )
            )

            # Keep all anchors loaded from the start. This isolates the
            # steady-state scrolling hot path from the separate, less frequent
            # cost of registering anchors when a lazy chunk is inserted.
            #
            # A single instant jump crosses most of the document and triggers
            # one TOC visibility update. Correctness requires the destination
            # link to be highlighted. The geometry-read count describes the
            # algorithmic work used to find that small visible range.
            geometry_read_count = screen_document.do_count_toc_geometry_reads(
                SCROLL_TARGET
            )

            # The previous linear implementation read 1199 anchor rectangles
            # for this 600-node fixture. A logarithmic lookup needs 19 in the
            # same scenario. Keep a browser-tolerant ceiling that is still
            # independent of the total document size.
            assert geometry_read_count <= 64

            toc = screen_document.get_toc()
            toc.assert_toc_link_has_attribute(
                SCROLL_TARGET,
                "intersected",
            )
            toc.assert_toc_link_has_not_attribute(
                "TOC-PERF-0001",
                "intersected",
            )
