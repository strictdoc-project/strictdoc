from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import BaseCase

from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)


class Screen_WorkPlanner:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_on_screen(self) -> None:
        self.test_case.assert_element(
            '//body[@data-viewtype="work-planner"]',
            by=By.XPATH,
        )
        self.test_case.wait_for_ready_state_complete()
        self.test_case.assert_no_js_errors()

    def assert_contains_text(self, text: str) -> None:
        self.test_case.assert_text(text)

    def do_open_add_epic_form(self) -> Form_EditRequirement:
        self.test_case.click_xpath(
            "(//a[@data-work-planner-add-template"
            " and contains(@data-work-planner-add-template, 'element_type=EPIC')])[1]"
        )
        form = Form_EditRequirement(self.test_case)
        form.assert_on_modal()
        form.assert_on_form()
        return form

    def do_open_edit_epic_form(self, title: str = "") -> Form_EditRequirement:
        if len(title) > 0:
            self.test_case.click_xpath(
                "//article[contains(@class, 'work_planner__epic')]"
                f"[.//*[contains(normalize-space(), '{title}')]]"
                "//a[normalize-space()='Edit']"
            )
        else:
            self.test_case.click_xpath(
                "(//article[contains(@class, 'work_planner__epic')]"
                "//a[normalize-space()='Edit'])[1]"
            )
        form = Form_EditRequirement(self.test_case)
        form.assert_on_modal()
        form.assert_on_form()
        return form

    def assert_visible_text_not_present(self, text: str) -> None:
        visible_text = str(
            self.test_case.execute_script(
                """
                const view = document.querySelector('.work_planner__view');
                return view ? view.innerText : '';
                """
            )
        )
        assert text not in visible_text, (text, visible_text)

    def assert_visible_text_present(self, text: str) -> None:
        visible_text = str(
            self.test_case.execute_script(
                """
                const view = document.querySelector('.work_planner__view');
                return view ? view.innerText : '';
                """
            )
        )
        assert text in visible_text, (text, visible_text)

    def assert_lane_epics_do_not_overlap(self, lane_title: str) -> None:
        result = self.test_case.execute_script(
            """
            const view = document.querySelector('.work_planner__view');
            if (!view) {
              return { found: false, overlaps: ['No work planner view.'] };
            }
            const lane = Array.from(
              view.querySelectorAll('[data-work-planner-lane]')
            ).find((candidate) => candidate.dataset.workPlannerLane === arguments[0]);
            if (!lane) {
              return { found: false, overlaps: [`Lane not found: ${arguments[0]}`] };
            }
            const cards = Array.from(lane.querySelectorAll('.work_planner__epic'));
            const rects = cards.map((card) => {
              const rect = card.getBoundingClientRect();
              return {
                title: card.querySelector('.work_planner__epic_title')?.innerText.trim(),
                left: rect.left,
                right: rect.right,
                top: rect.top,
                bottom: rect.bottom,
              };
            });
            const overlaps = [];
            for (let i = 0; i < rects.length; i += 1) {
              for (let j = i + 1; j < rects.length; j += 1) {
                const a = rects[i];
                const b = rects[j];
                const separated =
                  a.right <= b.left ||
                  b.right <= a.left ||
                  a.bottom <= b.top ||
                  b.bottom <= a.top;
                if (!separated) {
                  overlaps.push(`${a.title} overlaps ${b.title}`);
                }
              }
            }
            return { found: true, overlaps };
            """,
            lane_title,
        )
        assert result["found"] is True, result
        assert result["overlaps"] == [], result["overlaps"]

    def get_canvas_scroll_left(self) -> int:
        return int(
            self.test_case.execute_script(
                "return document.querySelector('[data-work-planner-canvas-scroll]').scrollLeft;"
            )
        )

    def get_canvas_scroll_top(self) -> int:
        return int(
            self.test_case.execute_script(
                "return document.querySelector('[data-work-planner-canvas-scroll]').scrollTop;"
            )
        )

    def get_zoom_scale(self) -> float:
        return float(
            self.test_case.execute_script(
                """
                const root = document.querySelector('[data-work-planner-root]');
                return Number.parseFloat(
                  getComputedStyle(root)
                    .getPropertyValue('--work-planner-scale')
                );
                """
            )
        )

    def get_zoom_state(self) -> dict:
        return self.test_case.execute_script(
            """
            const root = document.querySelector('[data-work-planner-root]');
            const scrollContainer = document.querySelector(
              '[data-work-planner-canvas-scroll]'
            );
            const surface = document.querySelector(
              '[data-work-planner-canvas-surface]'
            );
            const scale = Number.parseFloat(
              getComputedStyle(root)
                .getPropertyValue('--work-planner-scale')
            );
            const monthWidth = Number.parseFloat(
              getComputedStyle(root)
                .getPropertyValue('--work-planner-month-width')
                .replace('px', '')
            );
            const fixedWidth = 0;
            const surfaceWidth = Math.max(surface.scrollWidth, surface.offsetWidth, 1);
            const surfaceHeight = Math.max(surface.scrollHeight, surface.offsetHeight, 1);
            const minScale = Math.min(
              1,
              scrollContainer.clientWidth / surfaceWidth,
              scrollContainer.clientHeight / surfaceHeight
            );
            const maxScale = Math.max(
              minScale,
              scrollContainer.clientWidth / Math.max(1, fixedWidth + monthWidth)
            );
            return {
              scale,
              monthWidth,
              fixedWidth,
              minScale,
              maxScale,
              surfaceWidth,
              surfaceHeight,
              scrollWidth: scrollContainer.scrollWidth,
              clientWidth: scrollContainer.clientWidth,
              scrollHeight: scrollContainer.scrollHeight,
              clientHeight: scrollContainer.clientHeight,
            };
            """
        )

    def do_click_zoom_in(self) -> None:
        self.test_case.click(
            "[data-work-planner-zoom-in]",
            by=By.CSS_SELECTOR,
        )

    def do_click_zoom_out(self) -> None:
        self.test_case.click(
            "[data-work-planner-zoom-out]",
            by=By.CSS_SELECTOR,
        )

    def do_click_zoom_reset(self) -> None:
        self.test_case.click(
            "[data-work-planner-zoom-reset]",
            by=By.CSS_SELECTOR,
        )

    def do_zoom_canvas_with_ctrl_wheel(self, delta_y: int) -> None:
        self.test_case.execute_script(
            """
            const scrollContainer = document.querySelector(
              '[data-work-planner-canvas-scroll]'
            );
            const rect = scrollContainer.getBoundingClientRect();
            const event = new WheelEvent('wheel', {
              deltaY: arguments[0],
              ctrlKey: true,
              bubbles: true,
              cancelable: true,
              clientX: rect.left + rect.width / 2,
              clientY: rect.top + rect.height / 2,
            });
            scrollContainer.dispatchEvent(event);
            """,
            delta_y,
        )

    def do_pan_canvas_to_the_right(self) -> None:
        canvas = self.test_case.find_element(
            "[data-work-planner-canvas-scroll]",
            by=By.CSS_SELECTOR,
        )
        ActionChains(self.test_case.driver).move_to_element_with_offset(
            canvas, 120, 40
        ).key_down(Keys.SPACE).click_and_hold().move_by_offset(
            -240, 0
        ).release().key_up(Keys.SPACE).perform()

    def do_pan_canvas_down(self) -> None:
        canvas = self.test_case.find_element(
            "[data-work-planner-canvas-scroll]",
            by=By.CSS_SELECTOR,
        )
        ActionChains(self.test_case.driver).move_to_element_with_offset(
            canvas, 120, 40
        ).key_down(Keys.SPACE).click_and_hold().move_by_offset(
            0, -240
        ).release().key_up(Keys.SPACE).perform()

    def do_simulate_ajax_refresh(self) -> None:
        self.test_case.driver.execute_async_script(
            """
            const done = arguments[0];
            const frame = document.getElementById('frame_work_planner_content');
            const replacement = frame.outerHTML;
            document.dispatchEvent(
              new CustomEvent('turbo:before-stream-render', { bubbles: true })
            );
            frame.outerHTML = replacement;
            requestAnimationFrame(() => requestAnimationFrame(done));
            """
        )
