import argparse
import filecmp
import os
import sys

main_parser = argparse.ArgumentParser()

main_parser.add_argument("lhs_file", type=str, help="")

main_parser.add_argument("rhs_file", type=str, help="")

args = main_parser.parse_args()

if not os.path.exists(args.lhs_file):
    print(  # noqa: T201
        f"error: path does not exist: {args.lhs_file}", file=sys.stderr
    )
    exit(1)
if not os.path.exists(args.rhs_file):
    print(  # noqa: T201
        f"error: path does not exist: {args.rhs_file}", file=sys.stderr
    )
    exit(1)

if not filecmp.cmp(args.lhs_file, args.rhs_file):
    print(  # noqa: T201
        "error: files {} and {} are not identical".format(
            args.lhs_file, args.rhs_file
        )
    )
    exit(1)
