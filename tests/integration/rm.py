import os
import shutil
import sys

if len(sys.argv) == 1 or len(sys.argv) != 2:
    print("error: expect one argument: file or folder to be deleted.")
    sys.exit(1)

input_dir_or_file = sys.argv[1]
if os.path.isdir(input_dir_or_file):
    shutil.rmtree(input_dir_or_file)
    sys.exit(0)

if os.path.isfile(input_dir_or_file):
    os.remove(input_dir_or_file)
    sys.exit(0)

print(f"error: is neither a file or a folder: {input_dir_or_file}")
sys.exit(1)
