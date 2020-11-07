import argparse
import os
import sys

import html5lib

parser = argparse.ArgumentParser(description='HTML Markup validator')
parser.add_argument('input_file', type=str,
                    help='Path to HTML file')
args = parser.parse_args()

input_file = args.input_file
if not os.path.isfile(input_file):
    sys.stdout.flush()
    err = "error: input file does not exist: {}".format(input_file)
    print(err)
    exit(1)

with open(input_file, 'r') as file:
    html_content = file.read()

# html5parser = html5lib.HTMLParser(strict=True)
# try:
#     html5parser.parse(html_content)
# except NotImplementedError as e:
#     print(e)
#     exit(1)
#
# from tidylib import tidy_document
# document, errors = tidy_document(html_content, options={
#     'new-blocklevel-tags': 'main',
#     'char-encoding': 'utf8',
#     'input-encoding': 'utf8'
# })
#
# for error in errors.split('\n'):
#     print(error)

from xml.etree import ElementTree as etree
from io import StringIO
obj = etree.parse(StringIO(html_content), etree.XMLParser())
print(obj)