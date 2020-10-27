import argparse
import os.path

# https://stackoverflow.com/a/19476216/598057
import sys

main_parser = argparse.ArgumentParser()

main_parser.add_argument('input_path',
                         type=str,
                         help='One or more folders with *.sdoc files')

main_parser.add_argument('--file',
                         action='store_true',
                         default=False,
                         help='Enforce checking that input_path is a file')

main_parser.add_argument('--dir',
                         action='store_true',
                         default=False,
                         help='Enforce checking that input_path is a directory')

args = main_parser.parse_args()

if not os.path.exists(args.input_path):
    print('error: path does not exist: {}'.format(args.input_path),
          file=sys.stderr)
    exit(1)

if args.file and not os.path.isfile(args.input_path):
    print('error: path is not a file: {}'.format(args.input_path),
          file=sys.stderr)
    exit(1)

if args.dir and not os.path.isdir(args.input_path):
    print('error: path is not a directory: {}'.format(args.input_path),
          file=sys.stderr)
    exit(1)

exit(0)
