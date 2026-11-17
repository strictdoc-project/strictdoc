from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def autocomplete_list_xpath(field: WebElement) -> str:
    """
    The options list of an autocompletable field: the element whose id the
    aria-controls attribute of the field names (see autocomplete.js).
    """

    list_id = field.get_attribute("aria-controls")
    assert list_id, "The autocompletable field has no aria-controls."
    return f"//*[@id='{list_id}']"


def autocomplete_list(field: WebElement) -> WebElement:
    return field.parent.find_element(By.XPATH, autocomplete_list_xpath(field))
