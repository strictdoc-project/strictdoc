from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class Nav:  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_active_link(self, test_id: str) -> None:
        self.test_case.assert_element(
            f'//div[@class="nav"]//a[@data-testid="{test_id}"]'
            '[@aria-current="page"]',
            by=By.XPATH,
        )
        self.test_case.assert_element_not_present(
            f'//div[@class="nav"]//a[@aria-current="page"]'
            f'[not(@data-testid="{test_id}")]',
            by=By.XPATH,
        )

    def do_click_link(self, test_id: str) -> None:
        self.test_case.click_xpath(
            f'//div[@class="nav"]//a[@data-testid="{test_id}"]'
        )
