import argparse
import base64
import json
import os.path
import pathlib
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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


def get_pdf_from_html(driver, url, output_file):
    print(f"Chrome Driver: opening URL: {url}")  # noqa: T201
    driver.get(url)
    print(  # noqa: T201
        "Chrome Driver: waiting 1 seconds just in case. "
        "TODO: Ensure HTML2PDF has finished working."
    )
    sleep(1)
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

    print("Chrome Driver: executing print command.")  # noqa: T201
    result = send_devtools(driver, "Page.printToPDF", calculated_print_options)
    data = base64.b64decode(result["data"])
    with open(output_file, "wb") as f:
        f.write(data)


def main():
    parser = argparse.ArgumentParser(description="Description of your program")
    parser.add_argument("input_file", help="Path to HTML file.")
    parser.add_argument("output_file", help="Path to PDF file.")
    args = parser.parse_args()

    input_file = args.input_file
    assert os.path.isfile(input_file)

    output_file = args.output_file
    output_file_dir = os.path.dirname(output_file)
    pathlib.Path(output_file_dir).mkdir(parents=True, exist_ok=True)

    url = pathlib.Path(os.path.abspath(input_file)).as_uri()
    webdriver_options = Options()
    # webdriver_options.add_argument("--no-sandbox")  # noqa: ERA001
    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-gpu")

    chromedriver_exec = "./chromedriver"
    driver = webdriver.Chrome(chromedriver_exec, options=webdriver_options)
    get_pdf_from_html(driver, url, output_file)
    driver.quit()


main()
