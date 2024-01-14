import argparse
import atexit
import base64
import json
import os.path
import pathlib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


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
    path_to_chrome = ChromeDriverManager().install()

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
    return driver


def main():
    parser = argparse.ArgumentParser(description="HTML2PDF printer script.")
    parser.add_argument("input_file", help="Path to input HTML file.")
    parser.add_argument("output_file", help="Path to output PDF file.")
    args = parser.parse_args()

    input_file = args.input_file
    assert os.path.isfile(input_file)

    output_file = args.output_file
    output_file_dir = os.path.dirname(output_file)
    pathlib.Path(output_file_dir).mkdir(parents=True, exist_ok=True)

    url = pathlib.Path(os.path.abspath(input_file)).as_uri()

    driver = create_webdriver()

    @atexit.register
    def exit_handler():
        print("HTML2PDF: exit handler: quitting the Chrome Driver.")  # noqa: T201
        driver.quit()

    pdf_bytes = get_pdf_from_html(driver, url)
    with open(output_file, "wb") as f:
        f.write(pdf_bytes)


if __name__ == "__main__":
    main()
