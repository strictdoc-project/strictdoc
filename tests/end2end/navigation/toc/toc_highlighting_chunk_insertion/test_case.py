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
FIRST_LAZY_CHUNK_ID = "document-chunk-1"
LAST_LAZY_CHUNK_ID = "document-chunk-5"
LAST_ANCHOR = "TOC-PERF-0600"
REPLACED_ANCHOR = "TOC-PERF-0550"


class Test(E2ECase):
    def test_chunk_insertion_observes_only_new_anchors(self):
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

            toc_observation_counter_ = screen_document.do_count_toc_observations

            # Every chunk contains 100 anchors. Measure the first lazy
            # insertion with 100 anchors already loaded.
            first_insertion_observations = toc_observation_counter_(
                FIRST_LAZY_CHUNK_ID
            )

            # Establish 500 loaded anchors, then insert one more equal-size
            # chunk. Registration cost should depend on the 100 new anchors,
            # not on all anchors accumulated earlier in the document.
            screen_document.do_force_load_document_chunk("document-chunk-2")
            screen_document.do_force_load_document_chunk("document-chunk-3")
            screen_document.do_force_load_document_chunk("document-chunk-4")
            last_insertion_observations = toc_observation_counter_(
                LAST_LAZY_CHUNK_ID
            )

            # The previous full reconciliation registered 200 anchors for the
            # first insertion and 600 for the last. Both insertions now
            # register only their 100 new anchors.
            assert first_insertion_observations <= 110
            assert last_insertion_observations <= 110

            # The incrementally registered final anchor must participate in
            # normal TOC visibility calculation.
            screen_document.do_scroll_anchor_to_viewport_center(LAST_ANCHOR)
            screen_document.get_toc().assert_toc_link_has_attribute(
                LAST_ANCHOR,
                "intersected",
            )

            # Replacing an existing anchor with a new DOM element is not a
            # pure insertion. It deliberately uses the full reconciliation
            # fallback. Logical ID/order equality must not hide the change in
            # DOM identity from IntersectionObserver.
            screen_document.do_start_toc_anchor_subscription_recording(
                REPLACED_ANCHOR
            )
            try:
                requirement = screen_document.get_node_by_anchor(
                    REPLACED_ANCHOR
                )
                form = requirement.do_open_form_edit_requirement()
                form.do_form_cancel()
            finally:
                (
                    new_anchor_observed,
                    old_anchor_unobserved,
                ) = screen_document.do_stop_toc_anchor_subscription_recording()
            assert new_anchor_observed
            assert old_anchor_unobserved

            # The reconnected anchor must also retain normal visible behavior.
            screen_document.do_scroll_anchor_to_viewport_center(REPLACED_ANCHOR)
            screen_document.get_toc().assert_toc_link_has_attribute(
                REPLACED_ANCHOR,
                "intersected",
            )
