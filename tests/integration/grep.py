import argparse
import re
import sys


main_parser = argparse.ArgumentParser()
main_parser.add_argument("pattern", type=str, help="")
main_parser.add_argument("input", type=str, help="")
args = main_parser.parse_args()

match = False
with open(args.input, "r") as f:
    for line in f:
        pattern = re.compile(args.pattern)
        m = pattern.search(line)
        if m:
            match = True
            sys.stdout.write(
                m.group(1) if len(m.groups()) > 1 else m.group(0) + "\n"
            )

if not match:
    sys.exit(f"Pattern not found in {args.input}")
