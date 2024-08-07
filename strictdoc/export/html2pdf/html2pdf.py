# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import argparse
import atexit
import base64
import json
import os.path
import sys
import tempfile
from pathlib import Path
from shutil import copy
from typing import Optional

import requests
from requests import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.driver import Driver
from webdriver_manager.core.driver_cache import DriverCacheManager
from webdriver_manager.core.file_manager import FileManager
from webdriver_manager.core.http import HttpClient
from webdriver_manager.core.os_manager import OperationSystemManager

STRICTDOC_CACHE_DIR = os.getenv("STRICTDOC_CACHE_DIR")
if STRICTDOC_CACHE_DIR is not None:
    PATH_TO_CACHE_DIR = STRICTDOC_CACHE_DIR
else:
    PATH_TO_CACHE_DIR = os.path.join(
        tempfile.gettempdir(), "strictdoc_cache", "chromedriver"
    )
PATH_TO_CHROMEDRIVER_DIR = os.path.join(PATH_TO_CACHE_DIR, "chromedriver")

# HTML2PDF.js prints unicode symbols to console. The following makes it work on
# Windows which otherwise complains:
# UnicodeEncodeError: 'charmap' codec can't encode characters in position 129-130: character maps to <undefined>
# How to make python 3 print() utf8
# https://stackoverflow.com/questions/3597480/how-to-make-python-3-print-utf8
sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf8", closefd=False)


class HTML2PDF_HTTPClient(HttpClient):
    def get(self, url, params=None, **kwargs) -> Response:
        """
        Add you own logic here like session or proxy etc.
        """
        last_error: Optional[Exception] = None
        for attempt in range(1, 3):
            print(  # noqa: T201
                f"HTML2PDF_HTTPClient: sending GET request attempt {attempt}: {url}"
            )
            try:
                return requests.get(url, params, timeout=(5, 5), **kwargs)
            except requests.exceptions.ConnectTimeout as connect_timeout_:
                last_error = connect_timeout_
            except requests.exceptions.ReadTimeout as read_timeout_:
                last_error = read_timeout_
            except Exception as exception_:
                raise AssertionError(
                    "HTML2PDF_HTTPClient: unknown exception", exception_
                ) from None
        print(  # noqa: T201
            f"HTML2PDF_HTTPClient: "
            f"failed to get response for URL: {url} with error: {last_error}"
        )


class HTML2PDF_CacheManager(DriverCacheManager):
    def find_driver(self, driver: Driver):
        os_type = self.get_os_type()
        browser_type = driver.get_browser_type()
        browser_version = self._os_system_manager.get_browser_version_from_os(
            browser_type
        )

        path_to_cached_chrome_driver_dir = os.path.join(
            PATH_TO_CHROMEDRIVER_DIR, browser_version, os_type
        )
        path_to_cached_chrome_driver = os.path.join(
            path_to_cached_chrome_driver_dir, "chromedriver"
        )
        if os.path.isfile(path_to_cached_chrome_driver):
            print(  # noqa: T201
                f"HTML2PDF_CacheManager: chromedriver exists in StrictDoc's local cache: "
                f"{path_to_cached_chrome_driver}"
            )
            return path_to_cached_chrome_driver
        print(  # noqa: T201
            f"HTML2PDF_CacheManager: chromedriver does not exist in StrictDoc's local cache: "
            f"{path_to_cached_chrome_driver}"
        )
        path_to_downloaded_chrome_driver = super().find_driver(driver)
        if path_to_downloaded_chrome_driver is None:
            return None

        print(  # noqa: T201
            f"HTML2PDF_CacheManager: saving chromedriver to StrictDoc's local cache: "
            f"{path_to_downloaded_chrome_driver} -> {path_to_cached_chrome_driver}"
        )
        Path(path_to_cached_chrome_driver_dir).mkdir(
            parents=True, exist_ok=True
        )
        copy(path_to_downloaded_chrome_driver, path_to_cached_chrome_driver)

        return path_to_cached_chrome_driver


def get_inches_from_millimeters(mm: float) -> float:
    return mm / 25.4


def send_devtools(driver, cmd, params):
    resource = (
        f"/session/{driver.session_id}/chromium/send_command_and_get_result"
    )
    url = driver.command_executor._url + resource
    body = json.dumps({"cmd": cmd, "params": params})
    response = driver.command_executor._request("POST", url, body)
    return response.get("value")


def get_pdf_from_html(driver, url) -> bytes:
    print(f"HTML2PDF: opening URL with Chrome Driver: {url}")  # noqa: T201

    driver.get(url)

    # https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-printToPDF
    calculated_print_options = {
        "landscape": False,
        "displayHeaderFooter": False,
        "printBackground": True,
        # This is an experimental feature that generates a document outline
        # (table of contents).
        "generateDocumentOutline": True,
        # Whether to prefer page size as defined by css. Defaults to
        # false, in which case the content will be scaled to fit the paper size.
        "preferCSSPageSize": True,
        # Paper width in inches. Defaults to 8.5 inches.
        "paperWidth": get_inches_from_millimeters(210),
        # Paper height in inches. Defaults to 11 inches.
        "paperHeight": get_inches_from_millimeters(297),
        # WIP: Changing the margin settings has no effect.
        # Top margin in inches. Defaults to 1cm (~0.4 inches).
        "marginTop": get_inches_from_millimeters(12),
        # Bottom margin in inches. Defaults to 1cm (~0.4 inches).
        "marginBottom": get_inches_from_millimeters(12),
        # Left margin in inches. Defaults to 1cm (~0.4 inches).
        "marginLeft": get_inches_from_millimeters(21),
        # Right margin in inches. Defaults to 1cm (~0.4 inches).
        "marginRight": get_inches_from_millimeters(21),
    }

    print("HTML2PDF: executing print command with Chrome Driver.")  # noqa: T201
    result = send_devtools(driver, "Page.printToPDF", calculated_print_options)

    print("HTML2PDF: JS logs from the print session:")  # noqa: T201
    print('"""')  # noqa: T201
    for entry in driver.get_log("browser"):
        print(entry)  # noqa: T201
    print('"""')  # noqa: T201

    data = base64.b64decode(result["data"])
    return data


def create_webdriver(chromedriver: Optional[str]):
    print("HTML2PDF: creating Chrome Driver service.", flush=True)  # noqa: T201
    if chromedriver is None:
        cache_manager = HTML2PDF_CacheManager(
            file_manager=FileManager(os_system_manager=OperationSystemManager())
        )

        http_client = HTML2PDF_HTTPClient()
        download_manager = WDMDownloadManager(http_client)
        path_to_chrome = ChromeDriverManager(
            download_manager=download_manager, cache_manager=cache_manager
        ).install()
    else:
        path_to_chrome = chromedriver
    print(f"HTML2PDF: Chrome Driver available at path: {path_to_chrome}")  # noqa: T201

    service = Service(path_to_chrome)

    webdriver_options = Options()
    webdriver_options.add_argument("start-maximized")
    webdriver_options.add_argument("disable-infobars")
    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-extensions")

    webdriver_options.add_experimental_option("useAutomationExtension", False)
    webdriver_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"]
    )

    # Enable the capturing of everything in JS console.
    webdriver_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    print("HTML2PDF: creating Chrome Driver.", flush=True)  # noqa: T201

    driver = webdriver.Chrome(
        options=webdriver_options,
        service=service,
    )
    driver.set_page_load_timeout(60)

    return driver


def main():
    # By default, all driver binaries are saved to user.home/.wdm folder.
    # You can override this setting and save binaries to project.root/.wdm.
    os.environ["WDM_LOCAL"] = "1"

    parser = argparse.ArgumentParser(description="HTML2PDF printer script.")
    parser.add_argument(
        "--chromedriver",
        type=str,
        help="Optional chromedriver path. Downloaded if not given.",
    )
    parser.add_argument("paths", help="Paths to input HTML file.")
    args = parser.parse_args()

    paths = args.paths

    separate_path_pairs = paths.split(";")

    driver = create_webdriver(args.chromedriver)

    @atexit.register
    def exit_handler():
        print("HTML2PDF: exit handler: quitting the Chrome Driver.")  # noqa: T201
        driver.quit()

    for separate_path_pair_ in separate_path_pairs:
        path_to_input_html, path_to_output_pdf = separate_path_pair_.split(",")
        assert os.path.isfile(path_to_input_html), path_to_input_html

        path_to_output_pdf_dir = os.path.dirname(path_to_output_pdf)
        Path(path_to_output_pdf_dir).mkdir(parents=True, exist_ok=True)

        url = Path(os.path.abspath(path_to_input_html)).as_uri()

        pdf_bytes = get_pdf_from_html(driver, url)
        with open(path_to_output_pdf, "wb") as f:
            f.write(pdf_bytes)


if __name__ == "__main__":
    main()
