import os
import sys

if len(sys.argv) == 1 or len(sys.argv) != 2:
    print("error: expect one argument: input file.")
    sys.exit(1)

input_file = sys.argv[1]
if not os.path.isfile(input_file):
    print(f"error: is not a file: {input_file}")
    sys.exit(1)

# How to make python 3 print() utf8
# https://stackoverflow.com/a/68007720/598057
sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)

# How to print without a newline or space
# https://stackoverflow.com/a/71272802/598057
print(open(input_file, "r", encoding="utf-8").read(), end="")
