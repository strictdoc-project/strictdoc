import os
import sys


def rm_dir(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


if len(sys.argv) == 1 or len(sys.argv) != 2:
    print("error: expect one argument: file or folder to be deleted.")
    sys.exit(1)

input_dir_or_file = sys.argv[1]
if os.path.isdir(input_dir_or_file):
    rm_dir(input_dir_or_file)
    sys.exit(0)

if os.path.isfile(input_dir_or_file):
    os.remove(input_dir_or_file)
    sys.exit(0)

print(f"error: is neither a file or a folder: {input_dir_or_file}")
sys.exit(1)
