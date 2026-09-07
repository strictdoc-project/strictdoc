import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.helpers.components.media_zoom import MediaZoom
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

DOC_PATH = "media_zoom/input/index.html"

# input/index.sdoc pairs a "small" node per media type (must render well
# under any reasonable content column width -- never zoomable) with a
# "large" one (must render far wider than any reasonable column -- always
# zoomable). The large PlantUML diagram needs its full 20 participants:
# an earlier 8-participant version wasn't reliably wider than the shrunk
# display width in the actual test browser window.


class Test(E2ECase):
    def test_media_zoom(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(exporter.get_output_path_as_uri() + DOC_PATH)

            screen_document = Screen_Document(self)
            screen_document.assert_on_screen_document()

            # Async Mermaid/PlantUML rendering must complete before the
            # zoomability checks and click targets below exist.
            self.assert_element("pre.mermaid svg")
            self.assert_element("pre.plantuml svg")

            # The zoomability check itself (natural vs. displayed size) also
            # runs asynchronously; wait for the large element of each media
            # type to have settled on "zoomable" first, then assert the
            # exact counts on both sides -- this is what actually verifies
            # the small counterpart stayed excluded (assert_element alone
            # only waits for *one* match, it does not bound the count).
            self.assert_element("sdoc-autogen img[data-js-zoomable]")
            self.assert_element("pre.mermaid svg[data-js-zoomable]")
            self.assert_element("pre.plantuml svg[data-js-zoomable]")

            for zoomable_selector, not_zoomable_selector in (
                (
                    "sdoc-autogen img[data-js-zoomable]",
                    "sdoc-autogen img:not([data-js-zoomable])",
                ),
                (
                    "pre.mermaid svg[data-js-zoomable]",
                    "pre.mermaid svg:not([data-js-zoomable])",
                ),
                (
                    "pre.plantuml svg[data-js-zoomable]",
                    "pre.plantuml svg:not([data-js-zoomable])",
                ),
            ):
                assert len(self.find_elements(zoomable_selector)) == 1
                assert len(self.find_elements(not_zoomable_selector)) == 1

            media_zoom = MediaZoom(self)

            small_image = self.find_element(
                "sdoc-autogen img:not([data-js-zoomable])"
            )
            large_image = self.find_element(
                "sdoc-autogen img[data-js-zoomable]"
            )
            small_mermaid = self.find_element(
                "pre.mermaid svg:not([data-js-zoomable])"
            )
            large_mermaid = self.find_element(
                "pre.mermaid svg[data-js-zoomable]"
            )
            small_plantuml = self.find_element(
                "pre.plantuml svg:not([data-js-zoomable])"
            )
            large_plantuml = self.find_element(
                "pre.plantuml svg[data-js-zoomable]"
            )

            # A non-zoomable element must not open the overlay. Checked for
            # all three media kinds: the click delegate matches on
            # [data-js-zoomable], and only the size-threshold check above
            # decides which elements carry it -- a bug in either could
            # still open the overlay for a "small" element of one kind but
            # not another.
            small_image.click()
            media_zoom.assert_not_open()
            small_mermaid.click()
            media_zoom.assert_not_open()
            small_plantuml.click()
            media_zoom.assert_not_open()

            # A zoomable element opens the full-viewport overlay with a
            # clone of that element.
            large_image.click()
            media_zoom.assert_open()
            assert media_zoom.get_stage_element("img") is not None

            # Double-click toggles between fit-to-screen and natural
            # (100%, scale factor 1) size.
            media_zoom.do_toggle_fit_natural_with_double_click()
            assert media_zoom.get_stage_scale() == 1.0

            # Wheel-zooming in from the natural (scale=1) view must
            # increase the scale, not just change it -- a sign error in
            # the zoom-direction math would still "change" the transform
            # while zooming the wrong way.
            media_zoom.do_wheel_zoom_in()
            assert media_zoom.get_stage_scale() > 1.0

            media_zoom.do_close_with_escape()

            # Regression: cloning must keep the source SVG's id, or
            # Mermaid's id-scoped generated <style> ("#mermaid-<n> .node
            # rect {...}") stops matching the clone's shapes, leaving them
            # unstyled. Comparing against the source's own computed fill
            # (rather than hardcoding Mermaid's current theme color in the
            # main comparison) is what actually catches that. The sanity
            # check below still names Mermaid's actual default node color
            # explicitly -- an unstyled rect falls back to a dark grey
            # (verified empirically: NOT plain black), which would make a
            # "not black" guard pass right through an unstyled source.
            get_node_rect_fill_js = (
                "return window.getComputedStyle("
                "  arguments[0].querySelector('.node rect')"
                ").fill;"
            )
            source_id = large_mermaid.get_attribute("id")
            source_rect_fill = self.execute_script(
                get_node_rect_fill_js, large_mermaid
            )
            assert source_rect_fill == "rgb(236, 236, 255)"  # Mermaid's #ECECFF

            large_mermaid.click()
            media_zoom.assert_open()

            # The fit/natural toggle must not leave the browser's own
            # double-click-to-select-word behavior selecting a diagram
            # label in passing (mermaid's node text is real, selectable
            # SVG text, unlike the plain <img> used for the scale check
            # above).
            media_zoom.do_toggle_fit_natural_with_double_click()
            assert (
                self.execute_script("return window.getSelection().toString();")
                == ""
            )

            clone_svg = media_zoom.get_stage_element("svg")
            assert clone_svg.get_attribute("id") == source_id
            clone_rect_fill = self.execute_script(
                get_node_rect_fill_js, clone_svg
            )
            assert clone_rect_fill == source_rect_fill

            media_zoom.do_close_with_backdrop_click()

            large_plantuml.click()
            media_zoom.assert_open()
            media_zoom.do_close_with_escape()
