from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.node.node import Node
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
# 1 (011..020), 2 (021..030), 3 (031..035).
MID_CHUNK_TARGET = "REQ-025"
LAST_CHUNK_TARGET = "REQ-035"
# Keep several rendered nodes below the witness. A witness near the document
# end would be governed by scroll clamping rather than only by upper geometry.
CHUNK_ABOVE_TARGET = "CAB-032"
USER_SCROLL_INITIAL_TARGET = "CAB-040"
CONTENT_VIEWPORT_TOP = 0
UNTITLED_TEXT_24_MID = f"{24:032x}"
UNTITLED_TEXT_25_MID = f"{25:032x}"


class Test(E2ECase):
    def _open_main_document(self):
        screen_project_index = Screen_ProjectIndex(self)
        screen_project_index.assert_on_screen()
        return screen_project_index.do_click_on_the_document_with_title(
            "Scroll Preservation Document"
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

    def test_slow_upward_scroll_does_not_jump_when_oversized_chunk_loads(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_document_with_tall_chunk_above_viewport(
            test_setup,
            single_tall_node_index=19,
            tall_statement_repetitions=240,
        )

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_chunk_above_document()

            screen_document.get_toc().do_toc_go_to_anchor(
                USER_SCROLL_INITIAL_TARGET
            )
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_1_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_2_ID)

            # Slow upward scrolling first renders the ordinary middle chunk
            # and moves CAB-021 down through the viewport. The earlier chunk
            # then replaces its placeholder with a node taller than the
            # viewport; the samples below distinguish these two transitions.
            state = screen_document.do_record_anchor_while_scrolling_upward(
                chunk_id_to_load=CHUNK_1_ID,
                prerequisite_chunk_id=CHUNK_2_ID,
                witness_anchor="CAB-021",
                initial_witness_anchor="CAB-031",
                wheel_delta=-80,
                max_steps=100,
                pause_between_steps=0.05,
            )

            assert state["loadedChunkIds"][:2] == [CHUNK_2_ID, CHUNK_1_ID]
            assert state["targetLoadSampleIndex"] is not None
            samples = state["samples"]
            assert len(samples) >= 2
            target_load_sample_index = state["targetLoadSampleIndex"]
            samples_before_target_load = samples[:target_load_sample_index]
            assert samples_before_target_load
            assert any(
                abs(sample) <= 160 for sample in samples_before_target_load
            ), samples_before_target_load
            steps_before_target_load = [
                current - previous
                for previous, current in zip(
                    samples_before_target_load,
                    samples_before_target_load[1:],
                )
            ]
            assert any(
                40 <= step <= 160 for step in steps_before_target_load
            ), steps_before_target_load

            oversized_node_geometry = self.execute_script(
                """
                const anchor = document.getElementById('CAB-019');
                const node = anchor.closest('sdoc-node');
                const viewport = document.querySelector(
                  '[js-toc_highlighting-content_root]'
                );
                return {
                  nodeHeight: node.getBoundingClientRect().height,
                  viewportHeight: viewport.getBoundingClientRect().height,
                };
                """
            )
            assert (
                oversized_node_geometry["nodeHeight"]
                > oversized_node_geometry["viewportHeight"]
            )

            steps = [
                current - previous
                for previous, current in zip(samples, samples[1:])
            ]
            target_load_steps = steps[
                max(0, target_load_sample_index - 3) : min(
                    len(steps), target_load_sample_index + 3
                )
            ]
            assert target_load_steps
            assert max(abs(step) for step in target_load_steps) <= 240, (
                "Loading the oversized previous chunk caused a large viewport "
                f"step while CAB-021 moved down: {target_load_steps}."
            )

            prerequisite_load_sample_index = state[
                "prerequisiteLoadSampleIndex"
            ]
            assert prerequisite_load_sample_index is not None
            initial_samples = state["initialSamples"]
            initial_steps = [
                current - previous
                for previous, current in zip(
                    initial_samples,
                    initial_samples[1:],
                )
            ]
            prerequisite_load_steps = initial_steps[
                max(0, prerequisite_load_sample_index - 3) : min(
                    len(initial_steps), prerequisite_load_sample_index + 3
                )
            ]
            assert prerequisite_load_steps
            assert max(abs(step) for step in prerequisite_load_steps) <= 240, (
                "Loading the ordinary intermediate chunk moved the existing "
                f"CAB-031 witness: {prerequisite_load_steps}."
            )

    def _assert_upward_scroll_preserves_short_last_node(
        self,
        wheel_step: int,
        *,
        additional_upper_chunk_height: int = 0,
        delayed_height_change: int = 0,
        scroll_key: str | None = None,
    ) -> None:
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_document_with_tall_chunk_above_viewport(
            test_setup,
            single_tall_node_index=2,
            tall_statement_repetitions=80,
        )
        test_setup.write_to_sandbox_file(
            "strictdoc_config.py",
            "from strictdoc.core.project_config import ProjectConfig\n\n"
            "def create_config() -> ProjectConfig:\n"
            "    return ProjectConfig(\n"
            "        project_title='Slow Scroll Geometry Test',\n"
            "        chunked_documents_threshold=5,\n"
            "    )\n",
        )

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_chunk_above_document()
            screen_document.do_set_future_node_heights(
                {
                    "CAB-006": 150,
                    "CAB-007": 900 + additional_upper_chunk_height,
                    "CAB-008": 145,
                    "CAB-009": 460,
                    "CAB-010": 140,
                    "CAB-011": 520,
                    "CAB-012": 140,
                }
            )
            # Begin one chunk farther down so the fast local server cannot
            # finish loading the measured chunk before sampling starts. Slow
            # upward input then crosses the ordinary middle chunk and reaches
            # the five-node geometry from the reported document.
            screen_document.get_toc().do_toc_go_to_anchor("CAB-017")
            screen_document.assert_document_chunk_loaded(CHUNK_3_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_1_ID)
            screen_document.assert_document_chunk_unloaded(CHUNK_2_ID)

            if delayed_height_change:
                self.execute_script(
                    """
                    document.addEventListener("turbo:frame-load", (event) => {
                      if (event.target.id !== arguments[0]) return;
                      requestAnimationFrame(() => {
                        const anchor = document.getElementById(arguments[1]);
                        const node = anchor.closest("sdoc-node");
                        const height = node.getBoundingClientRect().height;
                        node.style.setProperty(
                          "height",
                          `${height + arguments[2]}px`,
                          "important"
                        );
                      });
                    });
                    """,
                    CHUNK_1_ID,
                    "CAB-007",
                    delayed_height_change,
                )

            state = screen_document.do_record_anchor_while_scrolling_upward(
                chunk_id_to_load=CHUNK_1_ID,
                prerequisite_chunk_id=CHUNK_2_ID,
                witness_anchor="CAB-010",
                initial_witness_anchor="CAB-016",
                wheel_delta=-wheel_step,
                max_steps=(
                    100
                    if scroll_key is not None
                    else 40
                    if wheel_step >= 50
                    else 500
                ),
                pause_between_steps=(
                    0.05
                    if scroll_key is not None
                    else 0.005
                    if wheel_step >= 50
                    else 0.05
                ),
                continuous_input=wheel_step >= 50 and scroll_key is None,
                scroll_key=scroll_key,
            )

            target_load_sample_index = state["targetLoadSampleIndex"]
            assert target_load_sample_index is not None
            samples = state["samples"]
            steps = [
                current - previous
                for previous, current in zip(samples, samples[1:])
            ]
            input_steps = [
                current - previous
                for previous, current in zip(
                    state["inputSamples"], state["inputSamples"][1:]
                )
            ]
            residual_steps = [
                coordinate_step - input_step
                for coordinate_step, input_step in zip(steps, input_steps)
            ]
            load_steps = steps[max(0, target_load_sample_index - 3) :]
            load_residual_steps = residual_steps[
                max(0, target_load_sample_index - 3) :
            ]
            assert load_steps
            assert (
                min(load_steps) >= -1 and max(load_steps) <= 80
                if scroll_key is not None
                else max(abs(step) for step in load_residual_steps) <= 4
            ), (
                "Loading the five-node preceding chunk moved its visible "
                "last node opposite to or independently of the upward input: "
                f"{load_residual_steps}."
            )

            initial_load_sample_index = state["targetLoadInitialSampleIndex"]
            assert initial_load_sample_index is not None
            initial_samples = state["initialSamples"]
            initial_steps = [
                current - previous
                for previous, current in zip(
                    initial_samples, initial_samples[1:]
                )
            ]
            initial_input_steps = [
                current - previous
                for previous, current in zip(
                    state["initialInputSamples"],
                    state["initialInputSamples"][1:],
                )
            ]
            initial_residual_steps = [
                coordinate_step - input_step
                for coordinate_step, input_step in zip(
                    initial_steps, initial_input_steps
                )
            ]
            initial_load_steps = initial_steps[
                max(0, initial_load_sample_index - 3) :
            ]
            initial_load_residual_steps = initial_residual_steps[
                max(0, initial_load_sample_index - 3) :
            ]
            assert initial_load_steps
            assert (
                min(initial_load_steps) >= -1 and max(initial_load_steps) <= 80
                if scroll_key is not None
                else max(abs(step) for step in initial_load_residual_steps) <= 4
            ), (
                "Loading the five-node preceding chunk moved an existing "
                "node opposite to or independently of the upward input: "
                f"{initial_load_residual_steps}."
            )

    def test_very_slow_upward_scroll_preserves_short_last_node(self):
        self._assert_upward_scroll_preserves_short_last_node(8)

    def test_50px_upward_scroll_preserves_short_last_node(self):
        self._assert_upward_scroll_preserves_short_last_node(50)

    def test_60px_upward_scroll_preserves_delayed_chunk_height_change(self):
        self._assert_upward_scroll_preserves_short_last_node(
            60,
            delayed_height_change=120,
        )

    def test_arrow_up_scroll_does_not_reverse_when_chunk_loads(self):
        self._assert_upward_scroll_preserves_short_last_node(
            50,
            additional_upper_chunk_height=200,
            scroll_key=Keys.ARROW_UP,
        )

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
            # Growing a node in chunk 2 must move the witness unless the
            # controller's ResizeObserver lock compensates the new upper
            # geometry. Production code already disables native anchoring in
            # the content viewport, so no test-only override is needed.
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
            # The form must be visible before submit. After creation, the new
            # node must start at the top of the content viewport.
            screen_document.wait_for_new_requirement_form_visible()
            form.do_fill_in_field_title("Injected Node")
            form.do_form_submit()

            self.assert_text("Injected Node")
            screen_document.assert_node_containing_text_viewport_top_close(
                "Injected Node", CONTENT_VIEWPORT_TOP, tolerance=24
            )

    def test_create_from_second_open_form_scrolls_to_its_new_node(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_main_document()
            screen_document.get_toc().do_toc_go_to_anchor(MID_CHUNK_TARGET)

            first_requirement = screen_document.get_node_by_anchor("REQ-024")
            (
                first_requirement.do_open_node_menu().do_node_add_requirement_above()
            )

            second_requirement = screen_document.get_node_by_anchor(
                MID_CHUNK_TARGET
            )
            second_form = second_requirement.do_open_node_menu().do_node_add_requirement_above()

            WebDriverWait(self.driver, 3).until(
                lambda _: self.execute_script(
                    """
                    return document.querySelectorAll(
                      'form[action="/actions/document/create_requirement"]'
                    ).length === 2;
                    """
                )
            )

            create_forms = self.execute_script(
                """
                return Array.from(document.querySelectorAll(
                  'form[action="/actions/document/create_requirement"]'
                )).map((form) => ({
                  frameId: form.closest('turbo-frame')?.id,
                  referenceMid: form.querySelector(
                    'input[name="reference_mid"]'
                  )?.value,
                }));
                """
            )
            assert len(create_forms) == 2, create_forms

            # Submit the second form explicitly. Generic form helpers select
            # the first matching field or button and cannot distinguish two
            # simultaneously open forms.
            second_form.do_fill_in(
                "TITLE", "Created From Second Open Form", field_order=-1
            )
            self.execute_script(
                """
                const forms = document.querySelectorAll(
                  'form[action="/actions/document/create_requirement"]'
                );
                forms[forms.length - 1].requestSubmit();
                """
            )

            self.assert_text("Created From Second Open Form")
            screen_document.assert_node_containing_text_viewport_top_close(
                "Created From Second Open Form",
                CONTENT_VIEWPORT_TOP,
                tolerance=24,
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
            screen_document.wait_for_new_requirement_form_visible()
            form.do_fill_in_field_statement("Created text after large section")
            form.do_form_submit()

            self.assert_text("Created text after large section")
            screen_document.assert_node_containing_text_viewport_top_close(
                "Created text after large section",
                CONTENT_VIEWPORT_TOP,
                tolerance=24,
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
            screen_document.wait_for_new_requirement_form_visible()
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

    def test_delete_untitled_text_keeps_removed_boundary_in_place(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        write_long_text_document_with_large_section_subtree(test_setup)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_document = self._open_create_below_large_section_document()

            # The TOC target loads chunk 2, which also contains the two TEXT
            # siblings used below. Neither TEXT has a title or a TOC item.
            screen_document.get_toc().do_toc_go_to_anchor(
                "CREATE-NEXT-SECTION"
            )
            screen_document.assert_document_chunk_loaded(CHUNK_2_ID)
            self.assert_element_not_present(
                f"#frame-toc li[data-nodeid='{UNTITLED_TEXT_24_MID}']",
            )

            screen_document.do_scroll_anchor_to_viewport_top(
                UNTITLED_TEXT_24_MID
            )
            deleted_node_top = screen_document.get_anchor_viewport_top(
                UNTITLED_TEXT_24_MID
            )
            text_node = Node(
                test_case=self,
                node_xpath=(
                    "//sdoc-node[.//*[@id="
                    f"'{UNTITLED_TEXT_24_MID}'"
                    "]]"
                ),
            )
            text_node.do_delete_node()

            self.assert_text_not_visible("Section child text 24.")
            screen_document.assert_anchor_viewport_top_close(
                UNTITLED_TEXT_25_MID,
                deleted_node_top,
            )
            screen_document.assert_anchor_viewport_top_stable(
                UNTITLED_TEXT_25_MID,
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
