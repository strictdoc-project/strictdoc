"""
Print the HTML stored in a static-export chunk .js file
(window.StrictDoc.chunks[...] = {"z": base64(gzip(html))}).
"""

import base64
import gzip
import json
import sys

if len(sys.argv) != 2:
    print("error: expect one argument: input file.")  # noqa: T201
    sys.exit(1)

sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)

with open(sys.argv[1], encoding="utf-8") as input_file:
    content = input_file.read()

payload = json.loads(content.split("] = ", 1)[1].rstrip().rstrip(";"))
if isinstance(payload, dict):
    payload = gzip.decompress(base64.b64decode(payload["z"])).decode("utf-8")
print(payload, end="")  # noqa: T201
