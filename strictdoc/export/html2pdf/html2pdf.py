import argparse
import atexit
import base64
import json
import os.path
import pathlib
from typing import Optional

import requests
from requests import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.http import HttpClient


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


def get_inches_from_millimeters(mm: float) -> float:
    return mm / 25.4


def send_devtools(driver, cmd, params):
    resource = (
        "/session/%s/chromium/send_command_and_get_result" % driver.session_id
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


def create_webdriver():
    print("HTML2PDF: creating Chrome Driver service.", flush=True)  # noqa: T201

    http_client = HTML2PDF_HTTPClient()
    download_manager = WDMDownloadManager(http_client)
    path_to_chrome = ChromeDriverManager(
        download_manager=download_manager
    ).install()
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
    driver.set_page_load_timeout(15)

    return driver


def main():
    # By default, all driver binaries are saved to user.home/.wdm folder.
    # You can override this setting and save binaries to project.root/.wdm.
    os.environ["WDM_LOCAL"] = "1"

    parser = argparse.ArgumentParser(description="HTML2PDF printer script.")
    parser.add_argument("paths", help="Paths to input HTML file.")
    args = parser.parse_args()

    paths = args.paths

    separate_path_pairs = paths.split(";")

    driver = create_webdriver()

    @atexit.register
    def exit_handler():
        print("HTML2PDF: exit handler: quitting the Chrome Driver.")  # noqa: T201
        driver.quit()

    for separate_path_pair_ in separate_path_pairs:
        path_to_input_html, path_to_output_pdf = separate_path_pair_.split(",")
        assert os.path.isfile(path_to_input_html), path_to_input_html

        path_to_output_pdf_dir = os.path.dirname(path_to_output_pdf)
        pathlib.Path(path_to_output_pdf_dir).mkdir(parents=True, exist_ok=True)

        url = pathlib.Path(os.path.abspath(path_to_input_html)).as_uri()

        pdf_bytes = get_pdf_from_html(driver, url)
        with open(path_to_output_pdf, "wb") as f:
            f.write(pdf_bytes)


if __name__ == "__main__":
    main()
