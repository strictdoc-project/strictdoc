import os
import shutil
import sys

if len(sys.argv) == 1 or len(sys.argv) != 3:
    print(  # noqa: T201
        "error: expect two arguments: input file and output file."
    )
    sys.exit(1)

input_file = sys.argv[1]
if not os.path.isfile(input_file):
    print(f"error: is not a file: {input_file}")  # noqa: T201
    sys.exit(1)

output_file = sys.argv[2]

shutil.copy(input_file, output_file)
