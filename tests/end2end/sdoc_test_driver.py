from seleniumbase import BaseCase


class SDocTestDriver:
    def __init__(self, base_case: BaseCase):
        assert isinstance(base_case, BaseCase)
        self.base_case = base_case

    def select_date_picker_date(self, year_str, month_str, day_str):
        self.base_case.click_visible_elements(
            '//button[@class="button view-switch"]'
        )
        self.base_case.click_visible_elements(
            '//button[@class="button view-switch"]'
        )

        self.base_case.click_visible_elements(
            f"//span[contains(@class, 'datepicker-cell') and contains(@class, 'year') and text()[contains(., '{year_str}')]]",
            limit=1,
        )
        self.base_case.click_visible_elements(
            f"//span[contains(@class, 'datepicker-cell') and contains(@class, 'month') and text()[contains(., '{month_str}')]]",
            limit=1,
        )
        self.base_case.click_visible_elements(
            f"//span[contains(@class, 'datepicker-cell') and contains(@class, 'day') and text()[contains(., '{day_str}')]]",
            limit=1,
        )
