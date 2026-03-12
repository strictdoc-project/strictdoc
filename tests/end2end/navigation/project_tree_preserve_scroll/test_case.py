from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.aside_project_tree import (
    AsideProjectTree,
)
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

            screen_project_index.assert_on_screen()
            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            aside_project_tree = AsideProjectTree(self)
            aside_project_tree.assert_is_aside_tree()

            tree_scroll_selector = (
                '[js-resizable_bar-scroll][data-content="tree"]'
            )
            baseline_scroll_top = 100
            document_25_title = "Test document 25"

            def get_tree_scroll_top():
                return self.execute_script(
                    f"""
                    const el = document.querySelector('{tree_scroll_selector}');
                    return el ? el.scrollTop : null;
                    """
                )

            # Part 1:
            # We set tree scrollTop to a deterministic synthetic value on purpose.
            # This test validates StrictDoc's persistence mechanism itself
            # (save on tree click + restore after reload), and should not depend
            # on browser/driver auto-scrolling behavior before click.
            self.execute_script(
                f"""
                const el = document.querySelector('{tree_scroll_selector}');
                if (el) el.scrollTop = {baseline_scroll_top};
                """
            )

            # Click target document 25 in tree.
            aside_project_tree.do_tree_go_to_document(document_25_title)

            # Measure scroll at click-time position.
            clicked_scroll_top_doc25 = get_tree_scroll_top()
            assert clicked_scroll_top_doc25 is not None, (
                "Tree scroll container not found after click on document 25."
            )
            print(  # noqa: T201
                f"[telemetry] doc25 clicked_scroll_top: {clicked_scroll_top_doc25}"
            )

            # Move tree to top and verify.
            self.execute_script(
                f"""
                const el = document.querySelector('{tree_scroll_selector}');
                if (el) el.scrollTop = 0;
                """
            )
            scroll_top_after_manual_reset = get_tree_scroll_top()
            assert scroll_top_after_manual_reset == 0, (
                f"Expected manual tree scroll reset to 0, got: {scroll_top_after_manual_reset}."
            )
            print(  # noqa: T201
                f"[telemetry] after manual reset scroll_top: {scroll_top_after_manual_reset}"
            )

            # Reload page and verify restoration to click-time position of temp25.
            self.refresh_page()
            restored_scroll_top_doc25 = get_tree_scroll_top()
            assert restored_scroll_top_doc25 is not None, (
                "Tree scroll container not found after refresh on document 25."
            )
            print(  # noqa: T201
                f"[telemetry] doc25 restored_scroll_top: {restored_scroll_top_doc25}"
            )
            assert (
                abs(restored_scroll_top_doc25 - clicked_scroll_top_doc25) <= 3
            ), (
                "Expected tree scroll to be restored close to click-time value "
                "for document 25. "
                f"clicked={clicked_scroll_top_doc25}, "
                f"restored={restored_scroll_top_doc25}."
            )

            # Part 2:
            # Click regular content link (NOT tree link): DOC-75.
            self.click_xpath(
                '//sdoc-node[@data-testid="node-requirement"]'
                '//a[contains(@href, "temp75.html#DOC-75")]'
            )

            # Fallback centering should bring active tree item (DOC-75) into
            # a deep/centered area of the scroll container.
            centered_scroll_top_doc75 = get_tree_scroll_top()
            assert centered_scroll_top_doc75 is not None, (
                "Tree scroll container not found after navigation to temp75."
            )
            print(  # noqa: T201
                f"[telemetry] doc75 centered_scroll_top: {centered_scroll_top_doc75}"
            )

            telemetry_doc75 = self.execute_script(
                f"""
                const container = document.querySelector('{tree_scroll_selector}');
                const active = document.querySelector(
                  '[js-project_tree_preserve_scroll] .tree_item[active="true"]'
                );
                if (!container || !active) return null;

                const c = container.getBoundingClientRect();
                const a = active.getBoundingClientRect();

                const containerCenter = c.top + c.height / 2;
                const activeCenter = a.top + a.height / 2;

                return {{
                  scrollTop: container.scrollTop,
                  fullyVisible: a.top >= c.top && a.bottom <= c.bottom,
                  distanceToCenter: Math.abs(activeCenter - containerCenter),
                  containerTop: c.top,
                  containerBottom: c.bottom,
                  containerHeight: c.height,
                  activeTop: a.top,
                  activeBottom: a.bottom,
                  activeHeight: a.height,
                  activeCenter,
                  containerCenter,
                }};
                """
            )
            print(f"[telemetry] doc75 geometry: {telemetry_doc75}")  # noqa: T201

            # For the chosen low baseline, DOC-75 should be outside viewport.
            # Fallback-centering must then move scroll away from baseline and
            # place active item close to the viewport center.
            assert telemetry_doc75 is not None, (
                "Expected DOC-75 telemetry to be available."
            )
            assert centered_scroll_top_doc75 > baseline_scroll_top + 200, (
                "Expected fallback-centering to change tree scroll significantly. "
                f"baseline={baseline_scroll_top}, got={centered_scroll_top_doc75}."
            )
            assert telemetry_doc75["distanceToCenter"] <= 60, (
                "Expected active DOC-75 tree item to be near center after fallback. "
                f"telemetry={telemetry_doc75}."
            )

            # Part 3:
            # Centered position of DOC-75 must also be persisted.
            self.execute_script(
                f"""
                const el = document.querySelector('{tree_scroll_selector}');
                if (el) el.scrollTop = 0;
                """
            )
            scroll_top_after_second_manual_reset = get_tree_scroll_top()
            assert scroll_top_after_second_manual_reset == 0, (
                "Expected manual tree scroll reset to 0 before final refresh, "
                f"got: {scroll_top_after_second_manual_reset}."
            )
            print(  # noqa: T201
                "[telemetry] after second manual reset scroll_top: "
                f"{scroll_top_after_second_manual_reset}"
            )

            self.refresh_page()
            restored_scroll_top_doc75 = get_tree_scroll_top()
            assert restored_scroll_top_doc75 is not None, (
                "Tree scroll container not found after final refresh on temp75."
            )
            print(  # noqa: T201
                f"[telemetry] doc75 restored_scroll_top: {restored_scroll_top_doc75}"
            )
            assert (
                abs(restored_scroll_top_doc75 - centered_scroll_top_doc75) <= 3
            ), (
                "Expected DOC-75 centered scroll to be persisted and restored. "
                f"centered={centered_scroll_top_doc75}, "
                f"restored={restored_scroll_top_doc75}."
            )
