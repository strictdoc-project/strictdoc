import argparse
import os
import sys

import html5lib
from tidylib import tidy_document
from xml.etree import ElementTree as etree
from io import StringIO

parser = argparse.ArgumentParser(description="HTML Markup validator")
parser.add_argument("input_file", type=str, help="Path to HTML file")
args = parser.parse_args()

input_file = args.input_file
if not os.path.isfile(input_file):
    sys.stdout.flush()
    err = (
        f"error: html_markup_validator: input file does not exist: {input_file}"
    )
    print(err)
    exit(1)

with open(input_file, "r", encoding="utf8") as file:
    html_content = file.read()

errors = []
warnings = []

# Validation #1: html5parser
html5parser = html5lib.HTMLParser(strict=True)
try:
    html5parser.parse(html_content)
except Exception as e:
    errors.append("Error: {}".format(str(e)))

# Validation #2: tidylib
_, tidylib_messages_string = tidy_document(
    html_content,
    options={
        "new-blocklevel-tags": "main, aside, header, section, article, nav, svg, path, turbo-frame",  # noqa: E501
        "char-encoding": "utf8",
        "input-encoding": "utf8",
        "output-encoding": "utf8",
        "drop-proprietary-attributes": "no",
        "show-warnings": False,
    },
)

for message in tidylib_messages_string.split("\n"):
    if "Error: " in message:
        errors.append(message)
    elif "Warning: " in message:
        warnings.append(message)

# Validation #3: xml.etree
try:
    etree.parse(StringIO(html_content), etree.XMLParser())
except Exception as e:
    errors.append("Error: {}".format(str(e)))

if len(errors) > 0 or len(warnings) > 0:
    for message in warnings + errors:
        print(message)

    if len(errors) > 0:
        print(
            "Validation COMPLETED: {} errors, {} warnings".format(
                len(errors), len(warnings)
            )
        )
        exit(1)
    else:
        # Warnings are ok for now.
        print(
            "Validation COMPLETED: {} errors, {} warnings".format(
                len(errors), len(warnings)
            )
        )
        exit(0)
else:
    print("Validation COMPLETED: 0 errors, 0 warnings")
