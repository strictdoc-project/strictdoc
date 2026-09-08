import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.helpers.components.media_zoom import MediaZoom
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

DOC_PATH = "media_zoom/input/index.html"

# input/index.sdoc has a small and a large image (used below to check that
# the overlay's initial scale depends on the image's own size), plus one
# Mermaid and one PlantUML diagram (used to check the overlay works for
# every media kind).


class Test(E2ECase):
    def test_media_zoom(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(exporter.get_output_path_as_uri() + DOC_PATH)

            screen_document = Screen_Document(self)
            screen_document.assert_on_screen_document()

            # Async Mermaid/PlantUML rendering must complete before the
            # click targets below exist.
            self.assert_element("pre.mermaid svg")
            self.assert_element("pre.plantuml svg")

            # Zoomability marking runs asynchronously (image load / async
            # diagram render); wait for it to settle before reading
            # attributes off specific elements.
            self.assert_element("sdoc-autogen img[data-js-zoomable]")
            self.assert_element("pre.mermaid svg[data-js-zoomable]")
            self.assert_element("pre.plantuml svg[data-js-zoomable]")

            small_image = self.find_element('sdoc-autogen img[src*="small"]')
            large_image = self.find_element('sdoc-autogen img[src*="large"]')
            assert small_image.get_attribute("data-js-zoomable") is not None
            assert large_image.get_attribute("data-js-zoomable") is not None

            mermaid = self.find_element("pre.mermaid svg")
            plantuml = self.find_element("pre.plantuml svg")

            media_zoom = MediaZoom(self)

            # The overlay's initial view fits the media to the viewport but
            # never enlarges it past its natural pixel size: a small image
            # opens at its real size (scale 1), a large one opens shrunk to
            # fit (scale < 1).
            small_image.click()
            media_zoom.assert_open()
            assert media_zoom.get_stage_scale() == 1.0
            media_zoom.do_close_with_escape()

            large_image.click()
            media_zoom.assert_open()
            assert media_zoom.get_stage_scale() < 1.0

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

            # Mermaid: cloning must keep the source SVG's id, or Mermaid's
            # id-scoped generated <style> ("#mermaid-<n> .node rect {...}")
            # stops matching the clone's shapes, leaving them unstyled.
            # Comparing against the source's own computed fill (rather
            # than hardcoding Mermaid's current theme color in the main
            # comparison) is what actually catches that. The sanity check
            # below still names Mermaid's actual default node color
            # explicitly -- an unstyled rect falls back to a dark grey
            # (verified empirically: NOT plain black), which would make a
            # "not black" guard pass right through an unstyled source.
            get_node_rect_fill_js = (
                "return window.getComputedStyle("
                "  arguments[0].querySelector('.node rect')"
                ").fill;"
            )
            source_id = mermaid.get_attribute("id")
            source_rect_fill = self.execute_script(
                get_node_rect_fill_js, mermaid
            )
            assert source_rect_fill == "rgb(236, 236, 255)"  # Mermaid's #ECECFF

            mermaid.click()
            media_zoom.assert_open()

            # The fit/natural toggle must not leave the browser's own
            # double-click-to-select-word behavior selecting a diagram
            # label in passing (Mermaid's node text is real, selectable
            # SVG text).
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

            plantuml.click()
            media_zoom.assert_open()
            media_zoom.do_close_with_escape()
