import os
from datetime import datetime

from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import BaseCase

from tests.end2end.helpers.components.actions_menu import (
    ActionsMenu,
)
from tests.end2end.helpers.components.confirm import Confirm
from tests.end2end.helpers.components.node.requirement import Requirement
from tests.end2end.helpers.screens.document.form_edit_grammar_elements import (
    Form_EditGrammarElements,
)
from tests.end2end.helpers.screens.screen import Screen


class Screen_Document(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)
        self.actions_menu = ActionsMenu(test_case)

    #
    # Overridden for Screen_Document.
    #

    def assert_on_screen_document(self) -> None:
        super().assert_on_screen("document")

    def assert_empty_document(self) -> None:
        super().assert_empty_view("document-root-placeholder")

    def assert_not_empty_document(self) -> None:
        super().assert_not_empty_view("document-root-placeholder")

    def assert_target_by_anchor(self, anchor) -> None:
        # check if the link was successfully clicked
        # and that the target is highlighted
        targeted_anchor = f"sdoc-anchor[id='{anchor}']:target"
        self.test_case.assert_element_present(targeted_anchor)

    def assert_node_in_viewport_by_anchor(
        self,
        anchor: str,
        *,
        timeout: int = 20,
    ) -> None:
        # DOM presence and :target both leave open whether the scroll
        # itself actually landed on the target - the real scroll container
        # is the content div (js-toc_highlighting-content_root), which
        # clips its content via overflow, not the outer window, so
        # visibility must be checked against that container's own bounds.
        def _node_is_in_viewport(_) -> bool:
            return self.test_case.execute_script(
                """
                const el = document.getElementById(arguments[0]);
                if (!el) return false;
                const container = document.querySelector(
                    '[js-toc_highlighting-content_root]'
                );
                if (!container) return false;
                const elRect = el.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                return (
                    elRect.bottom > containerRect.top &&
                    elRect.top < containerRect.bottom
                );
                """,
                anchor,
            )

        try:
            WebDriverWait(self.test_case.driver, timeout).until(
                _node_is_in_viewport
            )
        except TimeoutException as exception:
            raise TimeoutException(
                f"Element with anchor '{anchor}' did not appear within "
                f"the content viewport in {timeout}s."
            ) from exception

    def assert_node_containing_text_in_viewport(self, text: str) -> None:
        is_in_viewport = self.test_case.execute_script(
            """
            const el = [...document.querySelectorAll('sdoc-node')]
              .find((node) => node.textContent.includes(arguments[0]));
            if (!el) return false;
            const container = document.querySelector(
                '[js-toc_highlighting-content_root]'
            );
            if (!container) return false;
            const elRect = el.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            return (
                elRect.bottom > containerRect.top &&
                elRect.top < containerRect.bottom
            );
            """,
            text,
        )
        assert is_in_viewport, (
            f"Node containing text '{text}' is not within the content viewport."
        )

    def get_node_by_anchor(self, anchor: str) -> Requirement:
        requirement = Requirement(
            test_case=self.test_case,
            node_xpath=f"//sdoc-node[.//*[@id='{anchor}']]",
        )
        requirement.assert_is_requirement()
        return requirement

    #
    # Viewport geometry helpers.
    #
    # These helpers measure element position inside the document viewport.
    #

    def get_anchor_viewport_top(self, anchor: str) -> float:
        top = self.test_case.execute_script(
            """
            const anchor = document.getElementById(arguments[0]);
            const container = document.querySelector(
                '[js-toc_highlighting-content_root]'
            );
            if (!anchor || !container) return null;
            const anchorRect = anchor.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            return anchorRect.top - containerRect.top;
            """,
            anchor,
        )
        assert top is not None, (
            f"Could not measure viewport top for anchor '{anchor}'."
        )
        return top

    def wait_for_new_requirement_form_visible(self) -> None:
        def _form_top(_) -> dict | None:
            return self.test_case.execute_script(
                """
                // New forms have data-js-scroll-into-view on the inner form.
                // scroll_into_view.js scrolls that element into the document
                // viewport, and the page uses smooth scroll behavior. Measure
                // the inner form only after that scroll has made it visible.
                const form = document.querySelector('sdoc-form form');
                const container = document.querySelector(
                    '[js-toc_highlighting-content_root]'
                );
                if (!form || !container) return null;
                const formRect = form.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                if (
                  formRect.top < containerRect.top ||
                  formRect.bottom > containerRect.bottom
                ) {
                  return null;
                }
                return { top: formRect.top - containerRect.top };
                """
            )

        WebDriverWait(self.test_case.driver, 20).until(_form_top)

    def get_node_containing_text_viewport_top(self, text: str) -> float:
        top = self.test_case.execute_script(
            """
            const node = [...document.querySelectorAll("sdoc-node")]
              .find((item) => item.textContent.includes(arguments[0]));
            const container = document.querySelector(
                "[js-toc_highlighting-content_root]"
            );
            if (!node || !container) return null;
            return (
              node.getBoundingClientRect().top -
              container.getBoundingClientRect().top
            );
            """,
            text,
        )
        assert top is not None, (
            f"Could not measure viewport top for node containing '{text}'."
        )
        return top

    def get_stable_node_containing_text_viewport_top(
        self,
        text: str,
        *,
        stable_duration: float = 0.3,
        sample_interval: float = 0.05,
        tolerance: float = 1,
        timeout: int = 20,
    ) -> float:
        # Some production restorations correct a node's position over one or
        # more async ticks after it first appears (e.g. a setTimeout()+rAF
        # pair). Reading the position too early captures that transient
        # value rather than the settled one a later assertion must compare
        # against. Wait until consecutive samples stop moving instead of
        # relying on a single read.
        start_time = datetime.now()
        last_top = self.get_node_containing_text_viewport_top(text)
        stable_since = datetime.now()

        while True:
            self.test_case.sleep(sample_interval)
            current_top = self.get_node_containing_text_viewport_top(text)
            now = datetime.now()
            if abs(current_top - last_top) > tolerance:
                stable_since = now
            elif (now - stable_since).total_seconds() >= stable_duration:
                return current_top
            last_top = current_top
            if (now - start_time).total_seconds() >= timeout:
                return current_top

    def assert_anchor_viewport_top_close(
        self,
        anchor: str,
        expected_top: float,
        *,
        tolerance: float = 12,
        timeout: int = 20,
    ) -> None:
        last_top: list[float | None] = [None]

        def _anchor_top_matches(_) -> bool:
            top = self.test_case.execute_script(
                """
                const anchor = document.getElementById(arguments[0]);
                const container = document.querySelector(
                    '[js-toc_highlighting-content_root]'
                );
                if (!anchor || !container) return null;
                const anchorRect = anchor.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                return anchorRect.top - containerRect.top;
                """,
                anchor,
            )
            last_top[0] = top
            return top is not None and abs(top - expected_top) <= tolerance

        try:
            WebDriverWait(self.test_case.driver, timeout).until(
                _anchor_top_matches
            )
        except TimeoutException as exception:
            raise TimeoutException(
                f"Anchor '{anchor}' viewport top did not stay within "
                f"{tolerance}px of {expected_top}; last top was {last_top[0]}."
            ) from exception

    def assert_anchor_viewport_top_stable(
        self,
        anchor: str,
        expected_top: float,
        *,
        duration: float = 1.0,
        sample_interval: float = 0.05,
        tolerance: float = 12,
    ) -> None:
        start_time = datetime.now()
        measured_tops: list[float] = []

        while (datetime.now() - start_time).total_seconds() < duration:
            measured_top = self.get_anchor_viewport_top(anchor)
            measured_tops.append(measured_top)
            if abs(measured_top - expected_top) > tolerance:
                raise AssertionError(
                    f"Anchor '{anchor}' viewport top moved outside "
                    f"{tolerance}px of {expected_top}; measured "
                    f"{measured_top}."
                )
            self.test_case.sleep(sample_interval)

        assert len(measured_tops) > 0

    def assert_node_containing_text_viewport_top_close(
        self,
        text: str,
        expected_top: float,
        *,
        tolerance: float = 24,
        timeout: int = 20,
    ) -> None:
        last_top: list[float | None] = [None]

        def _node_top_matches(_) -> bool:
            top = self.test_case.execute_script(
                """
                const node = [...document.querySelectorAll('sdoc-node')]
                  .find((item) => item.textContent.includes(arguments[0]));
                const container = document.querySelector(
                    '[js-toc_highlighting-content_root]'
                );
                if (!node || !container) return null;
                const nodeRect = node.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                return nodeRect.top - containerRect.top;
                """,
                text,
            )
            last_top[0] = top
            return top is not None and abs(top - expected_top) <= tolerance

        try:
            WebDriverWait(self.test_case.driver, timeout).until(
                _node_top_matches
            )
        except TimeoutException as exception:
            raise TimeoutException(
                f"Node containing '{text}' viewport top did not stay within "
                f"{tolerance}px of {expected_top}; last top was {last_top[0]}."
            ) from exception

    def assert_node_containing_text_viewport_top_stable(
        self,
        text: str,
        expected_top: float,
        *,
        duration: float = 1.0,
        sample_interval: float = 0.05,
        tolerance: float = 24,
    ) -> None:
        start_time = datetime.now()
        measured_tops: list[float] = []

        while (datetime.now() - start_time).total_seconds() < duration:
            measured_top = self.get_node_containing_text_viewport_top(text)
            measured_tops.append(measured_top)
            if abs(measured_top - expected_top) > tolerance:
                raise AssertionError(
                    f"Node containing '{text}' viewport top moved outside "
                    f"{tolerance}px of {expected_top}; measured "
                    f"{measured_top}."
                )
            self.test_case.sleep(sample_interval)

        assert len(measured_tops) > 0

    #
    # Actions on the page.
    #

    def do_export_reqif(self) -> None:
        self.actions_menu.do_click_action("document-export-reqif-action")

    def do_export_pdf(self) -> None:
        self.actions_menu.do_click_action("document-export-html2pdf-action")

    def do_delete_document(self, confirm: bool = True) -> None:
        self.actions_menu.do_click_action("document-delete-action")

        # Confirmation required
        if confirm:
            confirm_dialog = Confirm(self.test_case)
            confirm_dialog.do_confirm_action()

    #
    # Open forms.
    #

    def do_open_modal_form_edit_grammar(self) -> Form_EditGrammarElements:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.actions_menu.do_click_action("document-edit-grammar-action")
        self.test_case.assert_element(
            "//sdoc-modal",
            by=By.XPATH,
        )
        return Form_EditGrammarElements(self.test_case)

    def do_scroll_to_anchor(self, anchor: str) -> None:
        self.test_case.sdoc_do_scroll_to_element_by_xpath(
            f"//sdoc-node[.//*[@id='{anchor}']]"
        )

    def do_scroll_anchor_to_viewport_top(self, anchor: str) -> None:
        element = self.test_case.wait_for_element_visible(
            f"//sdoc-node[.//*[@id='{anchor}']]",
            by=By.XPATH,
        )
        self.test_case.execute_script(
            """
            const scrollElementToOffset =
              window.StrictDoc.contentViewport?.scrollElementToOffset;
            if (scrollElementToOffset) {
              scrollElementToOffset(arguments[0], 0);
              return;
            }
            arguments[0].scrollIntoView({
              behavior: 'instant',
              block: 'start'
            });
            """,
            element,
        )

    def do_scroll_anchor_to_viewport_center(self, anchor: str) -> None:
        element = self.test_case.wait_for_element_visible(
            f"//sdoc-node[.//*[@id='{anchor}']]",
            by=By.XPATH,
        )
        # Selenium's ordinary scroll helpers target the outer page and do not
        # provide a reliable center coordinate inside StrictDoc's nested
        # document viewport. scrollIntoView() acts on the correct scrollable
        # ancestor and makes the test geometry independent of the window.
        self.test_case.execute_script(
            """
            arguments[0].scrollIntoView({
              behavior: "instant",
              block: "center"
            });
            """,
            element,
        )

    def do_count_toc_geometry_reads(
        self,
        anchor: str,
    ) -> int:
        # Wall-clock performance assertions are unstable in end-to-end tests.
        # Count the expensive geometry reads performed on semantic anchors
        # instead. This captures the algorithmic cost of one TOC highlight
        # update independently of machine speed.
        #
        # Element geometry can only be instrumented in the browser. Two
        # animation frames let initial IntersectionObserver delivery settle
        # before replacing the DOM method; the replacement is always restored
        # after the measurement.
        self.test_case.execute_async_script(
            """
            const done = arguments[0];
            requestAnimationFrame(() => {
              requestAnimationFrame(() => {
                window.__strictdocTocGeometryReadCount = 0;
                window.__strictdocOriginalGetBoundingClientRect =
                  Element.prototype.getBoundingClientRect;
                Element.prototype.getBoundingClientRect = function() {
                  if (this.matches?.("sdoc-anchor")) {
                    window.__strictdocTocGeometryReadCount += 1;
                  }
                  return (
                    window.__strictdocOriginalGetBoundingClientRect
                      .apply(this, arguments)
                  );
                };
                done();
              });
            });
            """
        )

        geometry_read_count = 0
        try:
            self.do_scroll_anchor_to_viewport_center(anchor)
            self.get_toc().assert_toc_link_has_attribute(
                anchor,
                "intersected",
            )
        finally:
            geometry_read_count = self.test_case.execute_script(
                """
                Element.prototype.getBoundingClientRect =
                  window.__strictdocOriginalGetBoundingClientRect;
                delete window.__strictdocOriginalGetBoundingClientRect;
                const geometryReadCount =
                  window.__strictdocTocGeometryReadCount;
                delete window.__strictdocTocGeometryReadCount;
                return geometryReadCount;
                """
            )
        return geometry_read_count

    def do_count_toc_observations(
        self,
        chunk_id: str,
    ) -> int:
        # Count semantic-anchor registrations rather than wall-clock time.
        # Re-observing every previously loaded anchor makes lazy insertion
        # progressively more expensive even when every chunk has the same
        # size. Instrumenting IntersectionObserver.observe() exposes that
        # algorithmic cost without depending on machine speed.
        self.test_case.execute_async_script(
            """
            const done = arguments[0];
            requestAnimationFrame(() => {
              requestAnimationFrame(() => {
                window.__strictdocTocAnchorObservationCount = 0;
                window.__strictdocOriginalIntersectionObserve =
                  IntersectionObserver.prototype.observe;
                IntersectionObserver.prototype.observe = function(target) {
                  if (target.matches?.("sdoc-anchor")) {
                    window.__strictdocTocAnchorObservationCount += 1;
                  }
                  return (
                    window.__strictdocOriginalIntersectionObserve
                      .call(this, target)
                  );
                };
                done();
              });
            });
            """
        )

        observation_count = 0
        try:
            self.do_force_load_document_chunk(chunk_id)
            # Chunk frame-load precedes the rAF-coalesced TOC anchor update.
            # Wait for that registration work before restoring the prototype.
            self.test_case.execute_async_script(
                """
                const done = arguments[0];
                requestAnimationFrame(() => {
                  requestAnimationFrame(done);
                });
                """
            )
        finally:
            observation_count = self.test_case.execute_script(
                """
                IntersectionObserver.prototype.observe =
                  window.__strictdocOriginalIntersectionObserve;
                delete window.__strictdocOriginalIntersectionObserve;
                const observationCount =
                  window.__strictdocTocAnchorObservationCount;
                delete window.__strictdocTocAnchorObservationCount;
                return observationCount;
                """
            )
        return observation_count

    def do_start_toc_anchor_subscription_recording(
        self,
        anchor: str,
    ) -> None:
        # A Turbo Save/Cancel can replace an anchor with a new DOM element
        # while preserving the same logical ID. Record observer calls by
        # element identity so the test proves that the detached target is
        # released and its replacement is subscribed.
        self.test_case.execute_script(
            """
            const anchorId = arguments[0];
            const oldAnchor = document.getElementById(anchorId);
            if (!oldAnchor) {
              throw new Error(`Missing anchor: ${anchorId}`);
            }
            const originalObserve =
              IntersectionObserver.prototype.observe;
            const originalUnobserve =
              IntersectionObserver.prototype.unobserve;
            const recording = {
              anchorId,
              oldAnchor,
              newAnchorObserved: false,
              oldAnchorUnobserved: false,
              originalObserve,
              originalUnobserve,
            };
            window.__strictdocTocSubscriptionRecording = recording;
            IntersectionObserver.prototype.observe = function(target) {
              if (
                target.id === recording.anchorId &&
                target !== recording.oldAnchor
              ) {
                recording.newAnchorObserved = true;
              }
              return recording.originalObserve.call(this, target);
            };
            IntersectionObserver.prototype.unobserve = function(target) {
              if (target === recording.oldAnchor) {
                recording.oldAnchorUnobserved = true;
              }
              return recording.originalUnobserve.call(this, target);
            };
            """,
            anchor,
        )

    def do_stop_toc_anchor_subscription_recording(self) -> tuple[bool, bool]:
        # Anchor reconciliation is coalesced to an animation frame. Wait until
        # it has run before restoring the instrumented browser prototypes.
        return self.test_case.execute_async_script(
            """
            const done = arguments[0];
            requestAnimationFrame(() => {
              requestAnimationFrame(() => {
                const recording =
                  window.__strictdocTocSubscriptionRecording;
                IntersectionObserver.prototype.observe =
                  recording.originalObserve;
                IntersectionObserver.prototype.unobserve =
                  recording.originalUnobserve;
                delete window.__strictdocTocSubscriptionRecording;
                done([
                  recording.newAnchorObserved,
                  recording.oldAnchorUnobserved,
                ]);
              });
            });
            """
        )

    def do_scroll_to_document_chunk(self, chunk_number: int) -> None:
        self.test_case.sdoc_do_scroll_to_element_by_xpath(
            f"//turbo-frame[@id='document-chunk-{chunk_number}']"
        )

    def do_load_document_chunks_by_scrolling(
        self,
        *chunk_numbers: int,
    ) -> None:
        # Scroll through the chunks in document order. This models normal lazy
        # loading and, unlike setting loading="eager", also establishes the
        # real geometry of every preceding chunk.
        for chunk_number in chunk_numbers:
            self.do_scroll_to_document_chunk(chunk_number)
            self.assert_document_chunk_loaded(f"document-chunk-{chunk_number}")

    def do_force_load_document_chunk(self, chunk_id: str) -> None:
        self.test_case.execute_script(
            """
            const frame = document.getElementById(arguments[0]);
            if (frame) {
              frame.setAttribute("loading", "eager");
            }
            """,
            chunk_id,
        )
        self.assert_chunk_frame_placeholder_cleared(chunk_id)

    def do_scroll_during_document_chunk_response(
        self,
        *,
        chunk_id: str,
        witness_anchor: str,
        scroll_delta: int,
    ) -> tuple[float, float]:
        # This helper deliberately uses JavaScript rather than Selenium wheel
        # actions. The regression requires a precise lifecycle ordering:
        #
        # Snapshot capture happens on turbo:before-fetch-response. The helper
        # must then move the user viewport before Turbo mutates the chunk
        # frame.
        #
        # A Selenium action cannot be scheduled synchronously between event
        # listeners of the same Turbo event. The WheelEvent establishes real
        # user-scroll intent for the controller; changing scrollTop supplies a
        # deterministic geometric delta before the DOM mutation starts.
        self.test_case.execute_script(
            """
            const frame = document.getElementById(arguments[0]);
            const target = document.getElementById(arguments[1]);
            const scrollDelta = arguments[2];
            const container = document.querySelector(
              "[js-toc_highlighting-content_root]"
            );
            window.__strictdocViewportRace = null;

            document.addEventListener(
              "turbo:before-fetch-response",
              (event) => {
                if (event.target !== frame) return;

                // The production listener was registered during page
                // initialization and has already captured its response-time
                // snapshot. Establish newer user intent before Turbo is
                // allowed to mutate the frame.
                container.dispatchEvent(new WheelEvent("wheel", {
                  bubbles: true,
                  deltaY: scrollDelta
                }));
                const containerTop =
                  container.getBoundingClientRect().top;
                const topBefore =
                  target.getBoundingClientRect().top - containerTop;
                const previousScrollBehavior =
                  container.style.scrollBehavior;
                container.style.scrollBehavior = "auto";
                container.scrollTop += scrollDelta;
                container.dispatchEvent(new Event("scroll"));
                const topAfter =
                  target.getBoundingClientRect().top - containerTop;
                container.style.scrollBehavior = previousScrollBehavior;
                window.__strictdocViewportRace = {
                  topBefore,
                  topAfter
                };
              },
              { once: true }
            );
            frame.setAttribute("loading", "eager");
            """,
            chunk_id,
            witness_anchor,
            scroll_delta,
        )
        self.assert_chunk_frame_placeholder_cleared(chunk_id)

        result = WebDriverWait(self.test_case.driver, 20).until(
            lambda _: self.test_case.execute_script(
                "return window.__strictdocViewportRace;"
            )
        )
        return result["topBefore"], result["topAfter"]

    def do_record_anchor_during_document_chunk_load(
        self,
        *,
        chunk_id: str,
        witness_anchor: str,
    ) -> tuple[list[float], float, float]:
        (
            samples,
            placeholder_heights,
            loaded_heights,
        ) = self.do_record_anchor_during_document_chunks_load(
            chunk_ids=[chunk_id],
            witness_anchor=witness_anchor,
        )
        return samples, placeholder_heights[0], loaded_heights[0]

    def do_record_anchor_during_document_chunks_load(
        self,
        *,
        chunk_ids: list[str],
        witness_anchor: str,
    ) -> tuple[list[float], list[float], list[float]]:
        # Post-load assertions can miss a one-frame jump that is corrected
        # before Selenium observes the settled DOM. Sample after every paint
        # opportunity from before the request through two frames after
        # all requested frames have loaded.
        #
        # A requestAnimationFrame callback alone is too early: Turbo may have a
        # later callback in the same frame and still compensate before paint.
        # The zero-delay task scheduled from rAF reads geometry after the
        # browser has had that paint opportunity. Synchronous intermediate DOM
        # states are therefore correctly treated as invisible to the user.
        #
        # Every frame is switched to eager loading in the same JavaScript task.
        # Their responses may finish in either order, which exercises
        # per-frame snapshot isolation and cumulative geometry compensation.
        self.test_case.execute_script(
            """
            const frames = arguments[0].map(
              (chunkId) => document.getElementById(chunkId)
            );
            const target = document.getElementById(arguments[1]);
            const container = document.querySelector(
              "[js-toc_highlighting-content_root]"
            );
            const state = {
              complete: false,
              placeholderHeights: frames.map(
                (frame) => frame.getBoundingClientRect().height
              ),
              loadedHeights: frames.map(() => null),
              samples: []
            };
            window.__strictdocFrameGeometry = state;
            const remainingFrames = new Set(frames);

            const schedulePostPaintSample = () => {
              requestAnimationFrame(() => {
                setTimeout(sample, 0);
              });
            };
            const sample = () => {
              state.samples.push(
                target.getBoundingClientRect().top -
                container.getBoundingClientRect().top
              );
              if (!state.complete) {
                schedulePostPaintSample();
              }
            };
            schedulePostPaintSample();

            const onFrameLoad = (event) => {
              const frameIndex = frames.indexOf(event.target);
              if (frameIndex === -1) return;
              state.loadedHeights[frameIndex] =
                event.target.getBoundingClientRect().height;
              remainingFrames.delete(event.target);
              if (remainingFrames.size !== 0) return;

              document.removeEventListener(
                "turbo:frame-load",
                onFrameLoad
              );
              requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                  state.complete = true;
                });
              });
            };
            document.addEventListener("turbo:frame-load", onFrameLoad);
            frames.forEach(
              (frame) => frame.setAttribute("loading", "eager")
            );
            """,
            chunk_ids,
            witness_anchor,
        )

        state = WebDriverWait(self.test_case.driver, 20).until(
            lambda _: self.test_case.execute_script(
                """
                const state = window.__strictdocFrameGeometry;
                return state?.complete ? state : null;
                """
            )
        )
        assert all(
            loaded_height is not None
            for loaded_height in state["loadedHeights"]
        )
        return (
            state["samples"],
            state["placeholderHeights"],
            state["loadedHeights"],
        )

    def do_record_anchor_during_wheel_scroll(
        self,
        *,
        chunk_id_to_load: str,
        witness_anchor: str,
        wheel_delta: int,
        steps: int,
        pause_between_steps: float,
    ) -> list[float]:
        # Use Selenium's W3C wheel input here: this scenario must exercise the
        # browser's natural scrolling and IntersectionObserver-driven lazy
        # loading, not a programmatic scrollTop assignment.
        #
        # Geometry is sampled after paint opportunities. Wheel input moves the
        # document content opposite to its delta: a negative (upward) delta
        # moves the witness down, and a positive (downward) delta moves it up.
        # The scenarios use this trajectory to distinguish normal user motion
        # from a stabilization step back against the gesture. The helper only
        # records geometry; each scenario asserts its expected direction.
        self.test_case.execute_script(
            """
            const target = document.getElementById(arguments[0]);
            const container = document.querySelector(
              "[js-toc_highlighting-content_root]"
            );
            const state = {
              complete: false,
              samples: []
            };
            window.__strictdocWheelGeometry = state;

            const schedulePostPaintSample = () => {
              requestAnimationFrame(() => {
                setTimeout(sample, 0);
              });
            };
            const sample = () => {
              state.samples.push(
                target.getBoundingClientRect().top -
                container.getBoundingClientRect().top
              );
              if (!state.complete) {
                schedulePostPaintSample();
              }
            };
            schedulePostPaintSample();
            """,
            witness_anchor,
        )

        container = self.test_case.find_element(
            "[js-toc_highlighting-content_root]"
        )
        scroll_origin = ScrollOrigin.from_element(container)
        actions = ActionChains(self.test_case.driver)
        for _ in range(steps):
            actions.scroll_from_origin(
                scroll_origin,
                0,
                wheel_delta,
            )
            actions.pause(pause_between_steps)
        actions.perform()

        self.assert_document_chunk_loaded(chunk_id_to_load)
        samples = self.test_case.execute_async_script(
            """
            const done = arguments[0];
            requestAnimationFrame(() => {
              setTimeout(() => {
                const state = window.__strictdocWheelGeometry;
                state.complete = true;
                done(state.samples);
              }, 0);
            });
            """
        )
        return samples

    def do_record_anchor_while_scrolling_upward(
        self,
        *,
        chunk_id_to_load: str,
        prerequisite_chunk_id: str,
        witness_anchor: str,
        initial_witness_anchor: str,
        wheel_delta: int,
        max_steps: int,
        pause_between_steps: float,
        continuous_input: bool = False,
        scroll_key: str | None = None,
    ) -> dict:
        # Record both anchors after paint opportunities during stepwise wheel
        # or keyboard input. Also record frame-load order and the sample index
        # at each relevant load so the test can inspect the corresponding
        # trajectory.
        self.test_case.execute_script(
            """
            const state = {
              complete: false,
              detailedSamples: [],
              initialInputSamples: [],
              initialSamples: [],
              inputSamples: [],
              lifecycleEvents: [],
              loadedChunkIds: [],
              prerequisiteLoadSampleIndex: null,
              samples: [],
              targetLoadInitialSampleIndex: null,
              targetLoadSampleIndex: null,
              wheelMovement: 0
            };
            window.__strictdocSlowUpwardGeometry = state;
            document.addEventListener("wheel", (event) => {
              state.wheelMovement -= event.deltaY;
            }, { capture: true, passive: true });

            const schedulePostPaintSample = () => {
              requestAnimationFrame(() => {
                setTimeout(sample, 0);
              });
            };
            const sample = () => {
              const target = document.getElementById(arguments[0]);
              const initialTarget = document.getElementById(arguments[2]);
              const container = document.querySelector(
                "[js-toc_highlighting-content_root]"
              );
              const detailedSample = {
                initialWitnessTop: null,
                loadedChunkIds: [...state.loadedChunkIds],
                scrollTop: container.scrollTop,
                timestamp: performance.now(),
                wheelMovement: state.wheelMovement,
                witnessTop: null,
              };
              if (initialTarget) {
                detailedSample.initialWitnessTop =
                  initialTarget.getBoundingClientRect().top -
                  container.getBoundingClientRect().top;
                state.initialInputSamples.push(state.wheelMovement);
                state.initialSamples.push(detailedSample.initialWitnessTop);
              }
              if (target) {
                detailedSample.witnessTop =
                  target.getBoundingClientRect().top -
                  container.getBoundingClientRect().top;
                state.inputSamples.push(state.wheelMovement);
                state.samples.push(detailedSample.witnessTop);
              }
              state.detailedSamples.push(detailedSample);
              if (!state.complete) {
                schedulePostPaintSample();
              }
            };
            schedulePostPaintSample();

            document.addEventListener("turbo:frame-load", (event) => {
              if (!event.target.id?.startsWith("document-chunk-")) return;
              state.loadedChunkIds.push(event.target.id);
              state.lifecycleEvents.push({
                chunkId: event.target.id,
                detailedSampleIndex: state.detailedSamples.length,
                initialSampleIndex: state.initialSamples.length,
                sampleIndex: state.samples.length,
                timestamp: performance.now(),
                type: "turbo:frame-load",
              });
              if (event.target.id === arguments[1]) {
                state.targetLoadSampleIndex = state.samples.length;
                state.targetLoadInitialSampleIndex =
                  state.initialSamples.length;
              }
              if (event.target.id === arguments[3]) {
                state.prerequisiteLoadSampleIndex =
                  state.initialSamples.length;
              }
            });
            """,
            witness_anchor,
            chunk_id_to_load,
            initial_witness_anchor,
            prerequisite_chunk_id,
        )

        container = self.test_case.find_element(
            "[js-toc_highlighting-content_root]"
        )
        scroll_origin = ScrollOrigin.from_element(container)
        if scroll_key is not None:
            self.test_case.execute_script(
                "arguments[0].tabIndex = -1; arguments[0].focus();",
                container,
            )
        target_loaded = False
        if continuous_input:
            actions = ActionChains(self.test_case.driver)
            for _ in range(max_steps):
                actions.scroll_from_origin(scroll_origin, 0, wheel_delta)
                actions.pause(pause_between_steps)
            actions.perform()
            target_loaded = bool(
                self.test_case.execute_script(
                    """
                    const frame = document.getElementById(arguments[0]);
                    return !frame.classList.contains(
                      "document-chunk-placeholder"
                    );
                    """,
                    chunk_id_to_load,
                )
            )
        for _ in range(max_steps):
            if continuous_input:
                break
            actions = ActionChains(self.test_case.driver)
            if scroll_key is not None:
                actions.send_keys(scroll_key)
            else:
                actions.scroll_from_origin(scroll_origin, 0, wheel_delta)
            actions.pause(pause_between_steps)
            actions.perform()
            target_loaded = bool(
                self.test_case.execute_script(
                    """
                    const frame = document.getElementById(arguments[0]);
                    return !frame.classList.contains(
                      "document-chunk-placeholder"
                    );
                    """,
                    chunk_id_to_load,
                )
            )
            if target_loaded:
                break

        assert target_loaded, (
            f"Chunk '{chunk_id_to_load}' did not load after "
            f"{max_steps} upward wheel steps."
        )
        self.assert_document_chunk_loaded(prerequisite_chunk_id)

        state = self.test_case.execute_async_script(
            """
            const done = arguments[0];
            requestAnimationFrame(() => {
              requestAnimationFrame(() => {
                setTimeout(() => {
                  const state = window.__strictdocSlowUpwardGeometry;
                  state.complete = true;
                  done(state);
                }, 0);
              });
            });
            """
        )
        return state

    def do_set_future_node_heights(self, heights_by_anchor: dict[str, int]):
        # Add fixed heights before lazy chunks render, so replacing their
        # placeholders produces the exact vertical geometry required by the
        # test instead of depending on font metrics or statement wrapping.
        self.test_case.execute_script(
            """
            const style = document.createElement("style");
            style.textContent = Object.entries(arguments[0])
              .map(([anchor, height]) => `
                sdoc-node:has(sdoc-anchor#${CSS.escape(anchor)}) {
                  box-sizing: border-box;
                  height: ${height}px !important;
                  overflow: hidden;
                }
              `)
              .join("\\n");
            document.head.append(style);
            """,
            heights_by_anchor,
        )

    def do_increase_first_node_height_in_chunk(
        self,
        chunk_id: str,
        extra_height: int,
    ) -> float:
        height_delta = self.test_case.execute_script(
            """
            const frame = document.getElementById(arguments[0]);
            const node = frame?.querySelector("sdoc-node");
            if (!node) return null;

            const heightBefore = node.getBoundingClientRect().height;
            node.style.paddingBottom = `${arguments[1]}px`;
            const heightAfter = node.getBoundingClientRect().height;
            return heightAfter - heightBefore;
            """,
            chunk_id,
            extra_height,
        )
        assert height_delta is not None, (
            f"Could not increase a node height in chunk '{chunk_id}'."
        )
        return height_delta

    def do_drag_toc_node(self, from_order: int, to_order: int) -> None:
        xpath_from = f'(//li[@draggable="true"])[{from_order}]'
        xpath_to = f'(//li[@draggable="true"])[{to_order}]'

        from_node = self.test_case.find_element(xpath_from)
        from_mid = from_node.get_attribute("data-nodeid")
        original_y = from_node.location["y"]

        self.test_case.drag_and_drop(xpath_from, xpath_to)

        start_time = datetime.now()
        while True:
            try:
                moved_node = self.test_case.find_element(
                    f'(//li[@data-nodeid="{from_mid}"])[1]'
                )
                if abs(moved_node.location["y"] - original_y) > 5:
                    break
            except StaleElementReferenceException:
                pass

            self.test_case.sleep(0.1)
            if (datetime.now() - start_time).total_seconds() > 10:
                raise TimeoutError(
                    "StrictDoc custom timeout: Moving element in the TOC"
                )

    def do_drag_first_toc_node_to_the_second(self) -> None:
        xpath_first_toc_node = '(//li[@draggable="true"])[1]'
        xpath_second_toc_node = '(//li[@draggable="true"])[2]'

        first_toc_node = self.test_case.find_element(xpath_first_toc_node)
        first_toc_node_mid = first_toc_node.get_attribute("data-nodeid")

        second_toc_node = self.test_case.find_element(xpath_second_toc_node)
        second_toc_node_mid = second_toc_node.get_attribute("data-nodeid")

        self.test_case.drag_and_drop(
            xpath_first_toc_node, xpath_second_toc_node
        )

        #
        # Drag and drop action takes some time before server/Turbo sends
        # an updated AJAX HTML template back. Sometimes a
        # StaleElementReferenceException is thrown by Selenium because it still
        # finds an old element as it is being moved. To solve this, set a timeout
        # to wait some time until the new TOC is rendered.
        #
        start_time = datetime.now()
        while True:
            new_root_node = self.test_case.find_element(
                f'(//li[@data-nodeid="{second_toc_node_mid}"])[1]'
            )
            moved_node = self.test_case.find_element(
                f'(//li[@data-nodeid="{first_toc_node_mid}"])[1]'
            )

            try:
                if new_root_node.location["y"] < moved_node.location["y"]:
                    break
            except StaleElementReferenceException:
                # The element is the one from an old TOC. Keep waiting.
                self.test_case.sleep(0.1)

            if (datetime.now() - start_time).total_seconds() > 10:
                raise TimeoutError(
                    "StrictDoc custom timeout: Moving element in the TOC"
                )

    def do_click_on_tree_document(self, doc_order: int = 1) -> None:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.test_case.click_xpath(
            f'(//*[@data-testid="tree-document-link"])[{doc_order}]'
        )

    def assert_document_config_edit_is_locked(self):
        """Verifies the document-level edit button is disabled."""
        element_class = self.test_case.get_attribute(
            '[data-testid="document-edit-config-action-disabled"]', "class"
        )
        assert "action_button--disabled" in element_class

    def assert_document_config_edit_is_unlocked(self):
        """Verifies the document-level edit button is fully interactive."""
        self.test_case.assert_element_present(
            '[data-testid="document-edit-config-action"]'
        )

        element_class = self.test_case.get_attribute(
            '[data-testid="document-edit-config-action"]', "class"
        )
        assert "action_button--disabled" not in element_class

    #
    # Lazy document chunks.
    #

    def assert_document_chunk_loaded(
        self,
        chunk_id: str,
        *,
        timeout: int = 20,
    ) -> None:
        # A cleared placeholder class is the lifecycle marker, while a rendered
        # sdoc-node proves that real document geometry has replaced the
        # estimate. Check both parts of the loaded state.
        self.assert_chunk_frame_placeholder_cleared(chunk_id)
        self.test_case.assert_element_present(
            f"turbo-frame#{chunk_id} sdoc-node",
            timeout=timeout,
        )

    def assert_document_chunk_unloaded(self, chunk_id: str) -> None:
        # An unloaded chunk must still be represented by its estimated-height
        # placeholder and must not contain any real node geometry.
        self.test_case.assert_element_present(
            f"turbo-frame#{chunk_id}.document-chunk-placeholder"
        )
        self.test_case.assert_element_not_present(
            f"turbo-frame#{chunk_id} sdoc-node"
        )

    def assert_chunk_frame_placeholder_cleared(self, chunk_id: str) -> None:
        # The placeholder class is StrictDoc's state marker for an unloaded
        # chunk frame. Turbo loads chunks asynchronously, so wait until the
        # frame content arrives and StrictDoc removes the placeholder class.
        self.test_case.assert_element_not_present(
            f"turbo-frame#{chunk_id}.document-chunk-placeholder",
            timeout=20,
        )

    def assert_chunk_frame_loading_attribute(
        self, chunk_id: str, expected_loading: str
    ) -> None:
        # Used for lazy-chunk preload checks where the browser-side script
        # changes Turbo's loading attribute asynchronously after observing
        # a placeholder.
        self.test_case.assert_attribute(
            f"turbo-frame#{chunk_id}",
            "loading",
            expected_loading,
            timeout=20,
        )

    def do_drop_image_to_requirement(
        self, field_name: str, image_path: str, field_order: int = 1
    ) -> None:
        # Verify the file exists locally
        absolute_image_path = os.path.abspath(image_path)
        assert os.path.exists(absolute_image_path), (
            f"Test image not found at {absolute_image_path}"
        )

        # Find the target editable field for the specific requirement
        field_order_str = "last()" if field_order == -1 else str(field_order)
        xpath_field = (
            f"(//*[@data-testid='form-field-{field_name}'])[{field_order_str}]"
        )
        target_element = self.test_case.find_element(By.XPATH, xpath_field)

        # Use a JS script to simulate the drop event.
        # Selenium cannot drag from the OS, so we need to simulate the DataTransfer object.
        js_drop_files = """
            var target = arguments[0];
            var offsetX = 0;
            var offsetY = 0;
            var document = target.ownerDocument || document;
            var window = document.defaultView || window;

            var input = document.createElement('input');
            input.type = 'file';
            input.style.display = 'none';
            input.onchange = function () {
            var rect = target.getBoundingClientRect();
            var x = rect.left + (offsetX || (rect.width >> 1));
            var y = rect.top + (offsetY || (rect.height >> 1));

            var dataTransfer = { files: this.files, types: ['Files'], dropEffect: 'copy' };

            ['dragenter', 'dragover', 'drop'].forEach(function (name) {
                var evt = document.createEvent('MouseEvent');
                evt.initMouseEvent(name, true, true, window, 0, 0, 0, x, y, false, false, false, false, 0, null);
                evt.dataTransfer = dataTransfer;
                target.dispatchEvent(evt);
            });

            setTimeout(function () { document.body.removeChild(input); }, 20);
            };
            document.body.appendChild(input);
            return input;
        """

        # Execute the script to create the input, then "upload" the file to it
        file_input = self.test_case.driver.execute_script(
            js_drop_files, target_element
        )
        file_input.send_keys(absolute_image_path)

        # Wait for the UI to update
        # We wait until the placeholder "Uploading..." disappears
        # and is replaced by the actual RST directive path.
        start_time = datetime.now()
        while True:
            current_content = target_element.text
            if ".. image:: ./_assets/" in current_content:
                break
            if '<img src="./_assets/' in current_content:
                break
            if "![](./_assets/" in current_content:
                break
            if "Image upload failed" in current_content:
                break

            if (datetime.now() - start_time).total_seconds() > 10:
                raise TimeoutError(
                    "Image upload failed or RST path never appeared."
                )

            self.test_case.sleep(0.5)

    def do_paste_image_to_requirement(
        self, field_name: str, image_path: str, field_order: int = 1
    ) -> None:
        # Verify the file exists locally
        absolute_image_path = os.path.abspath(image_path)
        assert os.path.exists(absolute_image_path), (
            f"Test image not found at {absolute_image_path}"
        )

        # Find the target editable field for the specific requirement
        field_order_str = "last()" if field_order == -1 else str(field_order)
        xpath_field = (
            f"(//*[@data-testid='form-field-{field_name}'])[{field_order_str}]"
        )
        target_element = self.test_case.find_element(By.XPATH, xpath_field)

        # Use a JS script to simulate the image paste event with a mocked ClipboardEvent.
        js_paste_files = """
            var target = arguments[0];
            var document = target.ownerDocument || document;

            var input = document.createElement('input');
            input.type = 'file';
            input.style.display = 'none';
            input.onchange = function () {
                var files = this.files;

                // Mock the DataTransfer/Clipboard items structure
                var mockClipboardItems = [];
                for (var i = 0; i < files.length; i++) {
                    let file = files[i];
                    mockClipboardItems.push({
                        type: file.type || 'image/png', // Fallback type just in case
                        getAsFile: function() { return file; }
                    });
                }

                var mockClipboardData = {
                    items: mockClipboardItems,
                    getData: function(format) { return ''; } // Mock getData to prevent errors
                };

                // Create the paste event and define the clipboardData property
                var pasteEvent = new Event('paste', { bubbles: true, cancelable: true });
                Object.defineProperty(pasteEvent, 'clipboardData', { value: mockClipboardData });

                target.dispatchEvent(pasteEvent);

                setTimeout(function () { document.body.removeChild(input); }, 20);
            };
            document.body.appendChild(input);
            return input;
        """

        # Execute the script to create the input, then "upload" the file to it
        file_input = self.test_case.driver.execute_script(
            js_paste_files, target_element
        )
        file_input.send_keys(absolute_image_path)

        # Wait for the UI to update
        # We wait until the placeholder "Uploading..." disappears
        # and is replaced by the actual RST directive path.
        start_time = datetime.now()
        while True:
            current_content = target_element.text
            # Checking for both asset path variations just to be safe
            if ".. image:: ./_assets/" in current_content:
                break
            if '<img src="./_assets/' in current_content:
                break
            if "![](./_assets/" in current_content:
                break
            if "Image upload failed" in current_content:
                break

            if (datetime.now() - start_time).total_seconds() > 10:
                raise TimeoutError(
                    "Image paste failed or RST path never appeared."
                )

            self.test_case.sleep(0.5)
