import sys
from pathlib import Path

if len(sys.argv) == 1 or len(sys.argv) != 2:
    print("error: expect one argument: input file.")
    sys.exit(1)

input_file = sys.argv[1]
Path(input_file).touch()
