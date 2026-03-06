from seleniumbase import BaseCase


class ActionsMenu:
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def do_open(self) -> None:
        self.test_case.click_xpath(
            '//*[@data-testid="header-action-menu-handler"]'
        )

    def do_click_action(self, testid: str) -> None:
        assert isinstance(testid, str)
        self.do_open()
        self.test_case.click_xpath(f'//*[@data-testid="{testid}"]')
