import argparse
import os
import sys
from io import StringIO
from xml.etree import ElementTree as etree

import html5lib
from tidylib import tidy_document

parser = argparse.ArgumentParser(description="HTML Markup validator")
parser.add_argument("input_file", type=str, help="Path to HTML file")
args = parser.parse_args()

input_file = args.input_file
if not os.path.isfile(input_file):
    sys.stdout.flush()
    err = (
        f"error: html_markup_validator: input file does not exist: {input_file}"
    )
    print(err)  # noqa: T201
    exit(1)

with open(input_file, encoding="utf8") as file:
    html_content = file.read()

errors = []
warnings = []

# Validation #1: html5parser
html5parser = html5lib.HTMLParser(strict=True)
try:
    html5parser.parse(html_content)
except Exception as e:
    errors.append(f"Error: {str(e)}")

# Validation #2: tidylib
_, tidylib_messages_string = tidy_document(
    html_content,
    options={
        "new-blocklevel-tags": (
            # HTML 5
            "main, aside, header, footer, section, article, nav, menu, "
            # Turbo.js
            "turbo-frame, "
            # SVG
            "svg, path, line, circle, polyline, "
            # StrictDoc
            "sdoc-anchor, "
            "sdoc-menu, sdoc-menu-handler, sdoc-menu-list, "
            "sdoc-node, "
            "sdoc-node-controls, "
            "sdoc-requirement, "
            "sdoc-requirement-uid, "
            "sdoc-requirement-title, "
            "sdoc-requirement-field, "
            "sdoc-requirement-field-label, "
            "sdoc-section, "
            "sdoc-section-title, sdoc-section-text, "
            "sdoc-main-placeholder, "
        ),
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
    errors.append(f"Error: {str(e)}")

MESSAGE_PREFIX = "HTML markup validation COMPLETED"

if len(errors) > 0 or len(warnings) > 0:
    for message in warnings + errors:
        print(message)  # noqa: T201

    if len(errors) > 0:
        print(  # noqa: T201
            "{}: {}: {} errors, {} warnings".format(
                MESSAGE_PREFIX, input_file, len(errors), len(warnings)
            )
        )
        exit(1)
    else:
        # Warnings are ok for now.
        print(  # noqa: T201
            "{}: {}: {} errors, {} warnings".format(
                MESSAGE_PREFIX, input_file, len(errors), len(warnings)
            )
        )
        exit(0)
else:
    print(f"{MESSAGE_PREFIX}: {input_file}: 0 errors, 0 warnings")  # noqa: T201
