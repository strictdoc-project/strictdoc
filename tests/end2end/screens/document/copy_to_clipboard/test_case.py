import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

DOC_PATH = "copy_to_clipboard/input/index.html"


class Test(E2ECase):
    def test_copy_to_clipboard(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(exporter.get_output_path_as_uri() + DOC_PATH)

            screen_document = Screen_Document(self)
            screen_document.assert_on_screen_document()

            node = screen_document.get_node(node_order=1)

            # Node anchor: hover reveals the anchor button; click copies the node UID.
            node.do_copy_anchor_to_buffer()
            assert self.paste_text() == "ROOT-1"

            # Inline RST anchor: hover over the TEXT node reveals the anchor button;
            # click copies the anchor ID defined with [ANCHOR: RST-ANCHOR, ...].
            # TEXT is the second node-requirement in the DOM.
            text_node = screen_document.get_node(node_order=2)
            text_node.do_copy_rst_anchor_to_buffer("RST-ANCHOR")
            assert self.paste_text() == "RST-ANCHOR"

            # Field content: hover reveals the copy button; click copies the
            # plain text content of the STATEMENT field.
            node.do_copy_field_content_to_buffer("statement")
            assert self.paste_text() == "Field content to copy."

            # Stable link: hover reveals the stable link button; click copies
            # a full URL resolved to ?a=UID format.
            node.do_copy_stable_link_to_buffer()
            assert (
                self.paste_text()
                == exporter.get_output_path_as_uri() + "index.html?a=ROOT-1"
            )
