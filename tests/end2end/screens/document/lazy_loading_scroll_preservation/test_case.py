from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.document_fixtures import (
    write_long_document_with_tall_chunk_above_viewport,
    write_long_text_document_with_large_section_subtree,
)
from tests.end2end.helpers.screens.document.form_edit_grammar_elements import (
    Form_EditGrammarElements,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

CHUNK_1_ID = "document-chunk-1"
CHUNK_2_ID = "document-chunk-2"
CHUNK_3_ID = "document-chunk-3"

# The main document has 35 requirements, chunked_documents_threshold = 10
# (strictdoc_config.py), so it renders as 4 chunks: 0 (REQ-001..010, inline),
# 1 (011..020), 2 (021..030), 3 (031..035). The control document has only 9
# requirements - below the threshold - so it stays on the legacy, unchunked
# rendering path and gives every chunked scenario here a same-document,
# non-chunked counterpart.
MID_CHUNK_TARGET = "REQ-025"
LAST_CHUNK_TARGET = "REQ-035"
# Keep several rendered nodes below the witness. A witness near the document
# end would be governed by scroll clamping rather than only by upper geometry.
CHUNK_ABOVE_TARGET = "CAB-032"
USER_SCROLL_INITIAL_TARGET = "CAB-040"


class Test(E2ECase):
    def _open_main_document(self):
        screen_project_index = Screen_ProjectIndex(self)
        screen_project_index.assert_on_screen()
        return screen_project_index.do_click_on_the_document_with_title(
            "Scroll Preservation Document"
        )

    def _open_control_document(self):
        screen_project_index = Screen_ProjectIndex(self)
        screen_project_index.assert_on_screen()
        return screen_project_index.do_click_on_the_document_with_title(
            "Scroll Preservation Control Document"
        )

    def _open_chunk_above_document(self):
        screen_project_index = Screen_ProjectIndex(self)
        screen_project_index.assert_on_screen()
        return screen_project_index.do_click_on_the_document_with_title(
            "Chunk Above Viewport Stability Document"
        )

    def _open_create_below_large_section_document(self):
        screen_project_index = Screen_ProjectIndex(self)
        screen_project_index.assert_on_screen()
        return screen_project_index.do_click_on_the_document_with_title(
            "Create Below Large Section Document"
        )

    #
    # A. Full content replacement in a chunked document.
    # The user starts from the visible document area. That area must stay
    # stable after already-loaded chunks are rendered again as placeholders.
    #

    def test_visible_anchor_stays_stable_when_tall_chunk_above_loads(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_document_with_tall_chunk_above_viewport(test_setup)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_chunk_above_document()

            # Chunk 2 is directly above the target chunk. Its real content is
            # intentionally much taller than its placeholder. Navigate
            # directly to chunk 3 so chunk 2 remains estimated geometry above
            # the visible semantic witness.
            screen_document.get_toc().do_toc_go_to_anchor(
                USER_SCROLL_INITIAL_TARGET
            )
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_2_ID)
            screen_document.do_scroll_anchor_to_viewport_center(
                CHUNK_ABOVE_TARGET
            )
            screen_document.assert_document_chunk_unloaded(CHUNK_2_ID)
            top_before = screen_document.get_anchor_viewport_top(
                CHUNK_ABOVE_TARGET
            )

            # Replacing the upper placeholder with much taller real content
            # must not change the witness coordinate inside the viewport.
            screen_document.do_force_load_document_chunk(CHUNK_2_ID)
            screen_document.assert_document_chunk_loaded(CHUNK_2_ID)

            screen_document.assert_anchor_viewport_top_stable(
                CHUNK_ABOVE_TARGET,
                top_before,
                duration=1.0,
            )

    def test_tall_chunk_replacement_has_no_paint_frame_jump(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_document_with_tall_chunk_above_viewport(test_setup)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_chunk_above_document()

            # The visible witness is in chunk 3. Chunk 2 remains a strongly
            # underestimated placeholder immediately above it, so replacing
            # that placeholder creates a large deterministic geometry delta.
            screen_document.get_toc().do_toc_go_to_anchor(
                USER_SCROLL_INITIAL_TARGET
            )
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_2_ID)
            screen_document.do_scroll_anchor_to_viewport_center(
                CHUNK_ABOVE_TARGET
            )
            witness_top = screen_document.get_anchor_viewport_top(
                CHUNK_ABOVE_TARGET
            )

            # Observe every browser paint opportunity during replacement.
            # Settled equality is insufficient: no sampled frame may expose
            # the uncompensated upper height change to the user.
            (
                frame_samples,
                placeholder_height,
                loaded_height,
            ) = screen_document.do_record_anchor_during_document_chunk_load(
                chunk_id=CHUNK_2_ID,
                witness_anchor=CHUNK_ABOVE_TARGET,
            )

            assert abs(loaded_height - placeholder_height) >= 1000
            assert len(frame_samples) >= 2
            max_witness_delta = max(
                abs(sample - witness_top) for sample in frame_samples
            )
            assert max_witness_delta <= 12, (
                "A paint frame exposed an uncompensated chunk height change: "
                f"maximum witness movement was {max_witness_delta}px."
            )
            screen_document.assert_document_chunk_loaded(CHUNK_2_ID)

    def test_near_simultaneous_upper_chunk_loads_compose_stably(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_document_with_tall_chunk_above_viewport(test_setup)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_chunk_above_document()

            # Navigate directly to chunk 3. Chunks 1 and 2 remain independent
            # placeholders above one visible witness; chunk 2 has a very large
            # estimate error and chunk 1 contributes a second geometry source.
            screen_document.get_toc().do_toc_go_to_anchor(
                USER_SCROLL_INITIAL_TARGET
            )
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_1_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_2_ID)
            screen_document.do_scroll_anchor_to_viewport_center(
                CHUNK_ABOVE_TARGET
            )
            witness_top = screen_document.get_anchor_viewport_top(
                CHUNK_ABOVE_TARGET
            )

            # Start both requests in one task. Regardless of response order,
            # each frame owns its snapshot and the two compensations must
            # compose without restoring stale state or applying a delta twice.
            (
                frame_samples,
                placeholder_heights,
                loaded_heights,
            ) = screen_document.do_record_anchor_during_document_chunks_load(
                chunk_ids=[CHUNK_1_ID, CHUNK_2_ID],
                witness_anchor=CHUNK_ABOVE_TARGET,
            )

            cumulative_geometry_delta = sum(
                abs(loaded - placeholder)
                for placeholder, loaded in zip(
                    placeholder_heights,
                    loaded_heights,
                )
            )
            assert cumulative_geometry_delta >= 1000
            assert len(frame_samples) >= 2
            max_witness_delta = max(
                abs(sample - witness_top) for sample in frame_samples
            )
            assert max_witness_delta <= 12, (
                "Concurrent upper chunk loads exposed stale or duplicate "
                f"compensation: maximum witness movement was "
                f"{max_witness_delta}px."
            )
            screen_document.assert_document_chunk_loaded(CHUNK_1_ID)
            screen_document.assert_document_chunk_loaded(CHUNK_2_ID)

    def test_delayed_chunk_height_change_above_viewport_stays_stable(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_document_with_tall_chunk_above_viewport(test_setup)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_chunk_above_document()

            # Load only the lower chunk and position a witness below the still
            # estimated geometry of chunk 2.
            screen_document.get_toc().do_toc_go_to_anchor(
                USER_SCROLL_INITIAL_TARGET
            )
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_2_ID)
            screen_document.do_scroll_anchor_to_viewport_top(CHUNK_ABOVE_TARGET)
            screen_document.do_force_load_document_chunk(CHUNK_2_ID)

            witness_top = screen_document.get_anchor_viewport_top(
                CHUNK_ABOVE_TARGET
            )
            # Isolate the controller's delayed ResizeObserver path. Without
            # native anchoring, growing a node in chunk 2 must move the witness
            # unless the semantic lock compensates the new upper geometry.
            screen_document.do_disable_native_scroll_anchoring()
            height_delta = (
                screen_document.do_increase_first_node_height_in_chunk(
                    CHUNK_2_ID,
                    extra_height=600,
                )
            )

            assert height_delta >= 500
            screen_document.assert_anchor_viewport_top_close(
                CHUNK_ABOVE_TARGET,
                witness_top,
            )
            screen_document.assert_anchor_viewport_top_stable(
                CHUNK_ABOVE_TARGET,
                witness_top,
                duration=1.0,
            )

    def test_user_scroll_during_chunk_request_supersedes_old_position(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_document_with_tall_chunk_above_viewport(test_setup)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_chunk_above_document()

            # Keep chunk 2 unloaded above the witness. The test will move the
            # viewport after the response-time snapshot but before Turbo
            # replaces this placeholder.
            screen_document.get_toc().do_toc_go_to_anchor(
                USER_SCROLL_INITIAL_TARGET
            )
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_2_ID)
            screen_document.do_scroll_anchor_to_viewport_top("CAB-038")

            # Move upward by a deterministic 120px during the response/render
            # gap. The final position must follow this newer user intent, not
            # the older snapshot captured at response time.
            (
                top_before_user_scroll,
                top_after_user_scroll,
            ) = screen_document.do_scroll_during_document_chunk_response(
                chunk_id=CHUNK_2_ID,
                witness_anchor="CAB-038",
                scroll_delta=-120,
            )
            assert abs(top_after_user_scroll - top_before_user_scroll) >= 100
            screen_document.assert_anchor_viewport_top_stable(
                "CAB-038",
                top_after_user_scroll,
                duration=1.0,
            )

    def test_natural_upward_wheel_scroll_does_not_step_backward(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_document_with_tall_chunk_above_viewport(test_setup)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_chunk_above_document()

            # Start in chunk 3 with the tall chunk 2 still represented by a
            # placeholder above the viewport. Moving upward naturally crosses
            # its preload boundary and lets the browser trigger lazy loading.
            screen_document.get_toc().do_toc_go_to_anchor(
                USER_SCROLL_INITIAL_TARGET
            )
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_2_ID)
            screen_document.do_scroll_anchor_to_viewport_center(
                CHUNK_ABOVE_TARGET
            )

            # With upward wheel input, content moves down: successive witness
            # coordinates may stay equal or increase. An opposing decrease
            # means chunk stabilization pulled the viewport back against the
            # user's gesture.
            frame_samples = (
                screen_document.do_record_anchor_during_wheel_scroll(
                    chunk_id_to_load=CHUNK_2_ID,
                    witness_anchor=CHUNK_ABOVE_TARGET,
                    wheel_delta=-60,
                    steps=8,
                    pause_between_steps=0.03,
                )
            )

            assert len(frame_samples) >= 2
            assert max(frame_samples) - min(frame_samples) >= 100
            opposing_steps = [
                current - previous
                for previous, current in zip(
                    frame_samples,
                    frame_samples[1:],
                )
                if current - previous < -12
            ]
            assert opposing_steps == [], (
                "Upper chunk loading moved content opposite to the natural "
                f"upward wheel gesture: {opposing_steps}."
            )

    def test_natural_downward_wheel_scroll_does_not_step_backward(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()

            # Start in the inline first chunk while chunk 1 remains below the
            # preload boundary. A downward wheel sequence approaches that
            # placeholder and lets the browser initiate its lazy load.
            screen_document.assert_document_chunk_unloaded(CHUNK_1_ID)
            screen_document.do_scroll_anchor_to_viewport_center("REQ-003")
            screen_document.assert_document_chunk_unloaded(CHUNK_1_ID)

            # With downward wheel input, content moves up: successive witness
            # coordinates may stay equal or decrease. A positive step means
            # lazy rendering moved the viewport against the user's gesture.
            frame_samples = (
                screen_document.do_record_anchor_during_wheel_scroll(
                    chunk_id_to_load=CHUNK_1_ID,
                    witness_anchor="REQ-003",
                    wheel_delta=120,
                    steps=30,
                    pause_between_steps=0.03,
                )
            )

            assert len(frame_samples) >= 2
            assert max(frame_samples) - min(frame_samples) >= 100
            opposing_steps = [
                current - previous
                for previous, current in zip(
                    frame_samples,
                    frame_samples[1:],
                )
                if current - previous > 12
            ]
            assert opposing_steps == [], (
                "Lower chunk loading moved content opposite to the natural "
                f"downward wheel gesture: {opposing_steps}."
            )

    def test_create_scrolls_to_new_node(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()
            # Establish real geometry in chunks 1 and 2. The full content
            # replacement will turn them back into estimated placeholders
            # while the user is reading a node from the middle chunk.
            screen_document.do_load_document_chunks_by_scrolling(1, 2)
            screen_document.assert_document_chunk_unloaded(CHUNK_3_ID)
            screen_document.do_scroll_anchor_to_viewport_top(MID_CHUNK_TARGET)

            requirement = screen_document.get_node_by_anchor(MID_CHUNK_TARGET)
            requirement.assert_requirement_title("Requirement 25")
            form = (
                requirement.do_open_node_menu().do_node_add_requirement_above()
            )
            # Create has its own target: the new node should appear where the
            # form was.
            # The helper waits for the form's own scroll-into-view first.
            form_top = screen_document.get_new_requirement_form_viewport_top()
            form.do_fill_in_field_title("Injected Node")
            form.do_form_submit()

            self.assert_text("Injected Node")
            screen_document.assert_node_containing_text_viewport_top_close(
                "Injected Node", form_top, tolerance=64
            )

    def test_create_text_below_large_section_scrolls_to_distant_new_node(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_text_document_with_large_section_subtree(test_setup)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_create_below_large_section_document()

            section = screen_document.get_node_by_anchor("CREATE-PARENT")
            form = section.do_open_node_menu().do_node_add_element_below("TEXT")
            form_top = screen_document.get_new_requirement_form_viewport_top()
            form.do_fill_in_field_statement("Created text after large section")
            form.do_form_submit()

            self.assert_text("Created text after large section")
            screen_document.assert_node_containing_text_viewport_top_close(
                "Created text after large section",
                form_top,
                tolerance=64,
            )

    def test_created_node_stays_stable_when_chunk_above_loads(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()

            # Navigate directly to the last chunk, leaving chunk 1 as estimated
            # geometry above the future create target.
            screen_document.get_toc().do_toc_go_to_anchor(LAST_CHUNK_TARGET)
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_1_ID)

            requirement = screen_document.get_node_by_anchor(LAST_CHUNK_TARGET)
            form = (
                requirement.do_open_node_menu().do_node_add_requirement_above()
            )
            screen_document.get_new_requirement_form_viewport_top()
            form.do_fill_in_field_title("Created Before Last Chunk Node")
            form.do_form_submit()
            self.assert_text("Created Before Last Chunk Node")
            top_before = screen_document.get_node_containing_text_viewport_top(
                "Created Before Last Chunk Node"
            )

            # Loading the earlier chunk after create must preserve the
            # operation-specific lock on the new node.
            screen_document.assert_document_chunk_unloaded(CHUNK_1_ID)
            screen_document.do_force_load_document_chunk(CHUNK_1_ID)
            screen_document.assert_node_containing_text_viewport_top_stable(
                "Created Before Last Chunk Node",
                top_before,
                duration=1.0,
            )

    def test_delete_preserves_top_visible_node_position(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()
            # Load both preceding chunks so the replacement has a substantial
            # real-to-placeholder geometry change above the viewport.
            screen_document.do_load_document_chunks_by_scrolling(1, 2)
            screen_document.assert_document_chunk_unloaded(CHUNK_3_ID)
            # Put REQ-024 at the viewport top. The test checks that this
            # surviving top node keeps its position after REQ-025 is deleted.
            screen_document.do_scroll_anchor_to_viewport_top("REQ-024")
            top_before = screen_document.get_anchor_viewport_top("REQ-024")

            requirement = screen_document.get_node_by_anchor("REQ-025")
            requirement.assert_requirement_title("Requirement 25")
            requirement.do_delete_node()

            self.assert_text_not_visible("STMT-025")
            screen_document.assert_anchor_viewport_top_close(
                "REQ-024", top_before
            )

    def test_delete_keeps_removed_node_boundary_in_place(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()
            # REQ-025 is read with real geometry above it. After deletion, the
            # following semantic node must inherit this exact viewport edge.
            screen_document.do_load_document_chunks_by_scrolling(1, 2)
            screen_document.assert_document_chunk_unloaded(CHUNK_3_ID)
            screen_document.do_scroll_anchor_to_viewport_top("REQ-025")
            deleted_node_top = screen_document.get_anchor_viewport_top(
                "REQ-025"
            )

            requirement = screen_document.get_node_by_anchor("REQ-025")
            requirement.do_delete_node()

            self.assert_text_not_visible("STMT-025")
            screen_document.assert_anchor_viewport_top_close(
                "REQ-026",
                deleted_node_top,
            )
            screen_document.assert_anchor_viewport_top_stable(
                "REQ-026",
                deleted_node_top,
                duration=1.0,
            )

    def test_delete_last_node_falls_back_to_end_of_document(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()

            screen_document.do_scroll_to_document_chunk(3)
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            # The deleted last node cannot remain visible. The expected
            # fallback is the previous surviving node at the document end.
            screen_document.do_scroll_to_anchor("REQ-035")
            requirement = screen_document.get_node_by_anchor("REQ-035")
            requirement.assert_requirement_title("Requirement 35")
            requirement.do_delete_node()

            self.assert_text_not_visible("STMT-035")
            screen_document.assert_node_in_viewport_by_anchor("REQ-034")

    def test_move_preserves_top_visible_node_position(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()
            # Preserve a witness in chunk 2 while DnD replaces the complete
            # content frame and recreates earlier loaded chunks as placeholders.
            screen_document.do_load_document_chunks_by_scrolling(1, 2)
            screen_document.assert_document_chunk_unloaded(CHUNK_3_ID)
            # Move uses manual fetch + Turbo.renderStreamMessage(), so it has
            # its own integration path into viewport restoration.
            screen_document.do_scroll_anchor_to_viewport_top(MID_CHUNK_TARGET)
            top_before = screen_document.get_anchor_viewport_top(
                MID_CHUNK_TARGET
            )

            # Drag node 1 to after node 8 - deep within chunk 0. The nodes
            # must not be adjacent because SeleniumBase's drag_and_drop()
            # needs enough pointer travel to deliver this custom TOC drag.
            screen_document.do_drag_toc_node(1, 8)

            screen_document.assert_anchor_viewport_top_close(
                MID_CHUNK_TARGET, top_before
            )

    def test_grammar_edit_preserves_top_visible_node_position(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()

            # Grammar edit is initiated outside the content viewport, but its
            # full replacement must preserve the semantic witness in chunk 2.
            screen_document.do_load_document_chunks_by_scrolling(1, 2)
            screen_document.assert_document_chunk_unloaded(CHUNK_3_ID)
            # Grammar edit starts from the header, but it still replaces the
            # document content frame. The current content viewport must stay
            # stable.
            screen_document.do_scroll_anchor_to_viewport_top(MID_CHUNK_TARGET)
            top_before = screen_document.get_anchor_viewport_top(
                MID_CHUNK_TARGET
            )

            form_edit_grammar: Form_EditGrammarElements = (
                screen_document.do_open_modal_form_edit_grammar()
            )
            form_edit_grammar.assert_on_grammar()
            # Element 3 is REQUIREMENT (1 is SECTION, 2 is TEXT - neither
            # used by any node in this document).
            form_edit_grammar_element = (
                form_edit_grammar.do_click_edit_grammar_element(3)
            )
            grammar_field_mid = form_edit_grammar_element.do_add_grammar_field()
            form_edit_grammar_element.do_fill_in_grammar_field_mid(
                grammar_field_mid, "CUSTOM_FIELD"
            )
            form_edit_grammar_element.do_form_submit()
            screen_document.assert_anchor_viewport_top_close(
                MID_CHUNK_TARGET, top_before
            )

    #
    # B. Node-local updates in a chunked document.
    # These actions must not collapse an already-loaded chunk.
    #

    def test_edit_in_isolated_middle_chunk_keeps_neighbors_unloaded(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()

            # Force-load only chunk 2 through its TOC target. Both adjacent
            # chunks must remain placeholders while the node-local stream
            # replaces REQ-025 and updates the TOC.
            screen_document.get_toc().do_toc_go_to_anchor(MID_CHUNK_TARGET)
            screen_document.assert_document_chunk_loaded(CHUNK_2_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_1_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_3_ID)

            requirement = screen_document.get_node_by_anchor(MID_CHUNK_TARGET)
            form = requirement.do_open_form_edit_requirement()
            form.do_fill_in_field_title("Edited Title")
            form.do_form_submit()

            # This edit updates only the node frame. Chunk 2 was already
            # loaded and must still contain real nodes afterwards.
            screen_document.assert_document_chunk_loaded(CHUNK_2_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_1_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_3_ID)

    def test_create_locally_does_not_jump(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()

            requirement = screen_document.get_node_by_anchor("REQ-001")
            form = (
                requirement.do_open_node_menu().do_node_add_requirement_below()
            )
            # Local create stays in chunk 0. The created node should appear
            # where the form was.
            form_top = screen_document.get_new_requirement_form_viewport_top()
            form.do_fill_in_field_title("Locally Injected Node")
            form.do_form_submit()
            self.assert_text("Locally Injected Node")
            screen_document.assert_node_containing_text_viewport_top_close(
                "Locally Injected Node", form_top, tolerance=64
            )

    def test_delete_locally_does_not_jump(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()
            # Local delete stays in chunk 0. The visible top node should not
            # move.
            screen_document.do_scroll_anchor_to_viewport_top("REQ-002")
            top_before = screen_document.get_anchor_viewport_top("REQ-002")

            requirement = screen_document.get_node_by_anchor("REQ-003")
            requirement.assert_requirement_title("Requirement 3")
            requirement.do_delete_node()
            self.assert_text_not_visible("STMT-003")
            screen_document.assert_anchor_viewport_top_close(
                "REQ-002", top_before
            )

    #
    # C. Non-chunked counterpart.
    # The restoration script is loaded here too. Ordinary full-content updates
    # must keep the same viewport behavior when there are no document chunks.
    #

    def test_non_chunked_create_unaffected(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_control_document()
            screen_document.do_scroll_anchor_to_viewport_top("CREQ-004")
            screen_document.assert_node_in_viewport_by_anchor("CREQ-004")

            requirement = screen_document.get_node_by_anchor("CREQ-004")
            requirement.assert_requirement_title("Control Requirement 4")
            form = (
                requirement.do_open_node_menu().do_node_add_requirement_below()
            )
            form_top = screen_document.get_new_requirement_form_viewport_top()
            form.do_fill_in_field_title("Control Injected Node")
            form.do_form_submit()
            self.assert_text("Control Injected Node")
            screen_document.assert_node_containing_text_viewport_top_close(
                "Control Injected Node", form_top, tolerance=64
            )

    def test_non_chunked_delete_unaffected(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_control_document()
            screen_document.do_scroll_anchor_to_viewport_top("CREQ-004")
            top_before = screen_document.get_anchor_viewport_top("CREQ-004")

            requirement = screen_document.get_node_by_anchor("CREQ-005")
            requirement.assert_requirement_title("Control Requirement 5")
            requirement.do_delete_node()
            self.assert_text_not_visible("Control statement 005")
            screen_document.assert_anchor_viewport_top_close(
                "CREQ-004", top_before
            )

    def test_non_chunked_move_unaffected(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_control_document()
            screen_document.do_scroll_anchor_to_viewport_top("CREQ-008")
            top_before = screen_document.get_anchor_viewport_top("CREQ-008")

            screen_document.do_drag_toc_node(1, 5)
            screen_document.assert_anchor_viewport_top_close(
                "CREQ-008", top_before
            )

    def test_non_chunked_grammar_edit_unaffected(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_control_document()
            screen_document.do_scroll_anchor_to_viewport_top("CREQ-008")
            top_before = screen_document.get_anchor_viewport_top("CREQ-008")

            form_edit_grammar: Form_EditGrammarElements = (
                screen_document.do_open_modal_form_edit_grammar()
            )
            form_edit_grammar.assert_on_grammar()
            form_edit_grammar_element = (
                form_edit_grammar.do_click_edit_grammar_element(1)
            )
            grammar_field_mid = form_edit_grammar_element.do_add_grammar_field()
            form_edit_grammar_element.do_fill_in_grammar_field_mid(
                grammar_field_mid, "CUSTOM_FIELD"
            )
            form_edit_grammar_element.do_form_submit()
            screen_document.assert_anchor_viewport_top_close(
                "CREQ-008", top_before
            )
