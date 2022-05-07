import sys

import pkg_resources

print(
    "check_environment.py: "
    "checking if the current Python environment has all packages installed"
    "."
)

try:
    # Quicker way of checking if an environment has all packages installed.
    # It is faster than running pip install ... every time.
    # https://stackoverflow.com/a/65606063/598057
    pkg_resources.require(open("requirements.txt", mode="r"))
    pkg_resources.require(open("requirements.development.txt", mode="r"))
except pkg_resources.DistributionNotFound as exception:
    print(f"check_environment.py: {exception}")
    sys.exit(11)

print(f"check_environment.py: all packages seem to be installed.")
