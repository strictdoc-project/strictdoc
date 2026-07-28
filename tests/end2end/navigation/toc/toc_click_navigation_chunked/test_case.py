from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.toc import TOC
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self):
        """
        Regression test: clicking a TOC link in a chunked document, where
        the target is already in the DOM (chunk 0, no lazy chunk needs to
        be force-loaded - see strictdoc_config.py), must produce the same
        native hash-navigation behavior as in a non-chunked document
        (tests/end2end/navigation/toc/toc_highlighting) - in particular,
        toc_highlighting.js's hashchange-driven "targeted" attribute update
        and CSS :target must both still work.
        """

        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_document = screen_project_index.do_click_on_first_document()
            screen_toc: TOC = screen_document.get_toc()

            # Count real "hashchange" events directly, rather than only
            # inferring one happened from its downstream effects (the
            # "targeted" attribute has more than one code path that can
            # set it - only a genuine hashchange proves the browser's own
            # fragment-navigation machinery, which collapsible_toc.js also
            # depends on, actually ran).
            self.execute_script(
                "window.__sdocHashchangeCount = 0;"
                "window.addEventListener('hashchange',"
                " () => window.__sdocHashchangeCount++);"
            )

            screen_toc.do_toc_go_to_anchor("SECTION_BEFORE_LONG_NODE")
            screen_toc.assert_toc_link_has_attribute(
                "SECTION_BEFORE_LONG_NODE", "targeted"
            )
            screen_document.assert_target_by_anchor("SECTION_BEFORE_LONG_NODE")
            hashchange_count = self.execute_script(
                "return window.__sdocHashchangeCount;"
            )
            assert hashchange_count == 1, (
                f"Expected exactly one hashchange event, got "
                f"{hashchange_count}."
            )

            # Scroll away manually (simulating a user who navigated to the
            # section, then scrolled elsewhere), then click the *same* TOC
            # entry again. location.hash assignment is a no-op when the
            # value does not change - no "hashchange" fires for it - so
            # returning to the section on a repeat click must not depend
            # on one.
            self.execute_script(
                "const el = document.querySelector"
                "('[js-toc_highlighting-content_root]');"
                # .main has scroll-behavior: smooth (content.css), which
                # browsers honor even for a raw scrollTop assignment - force
                # it instant here so this setup step's own scroll has
                # already landed by the time the check below runs.
                "el.style.scrollBehavior = 'auto';"
                "el.scrollTop = el.scrollHeight;"
            )
            self.assert_false(
                self.execute_script(
                    "const target = document.getElementById"
                    "('SECTION_BEFORE_LONG_NODE');"
                    "const container = document.querySelector"
                    "('[js-toc_highlighting-content_root]');"
                    "const t = target.getBoundingClientRect();"
                    "const c = container.getBoundingClientRect();"
                    "return t.bottom > c.top && t.top < c.bottom;"
                ),
                "Test setup issue: target should be scrolled out of view "
                "at this point.",
            )
            screen_toc.do_toc_go_to_anchor("SECTION_BEFORE_LONG_NODE")
            screen_document.assert_node_in_viewport_by_anchor(
                "SECTION_BEFORE_LONG_NODE"
            )
            hashchange_count_after_repeat_click = self.execute_script(
                "return window.__sdocHashchangeCount;"
            )
            assert hashchange_count_after_repeat_click == 1, (
                "A same-hash repeat click should not fire another "
                f"hashchange, got {hashchange_count_after_repeat_click}."
            )
