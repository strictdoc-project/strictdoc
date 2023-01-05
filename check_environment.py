import pathlib
import sys

import pkg_resources
import toml

print(
    "check_environment.py: "
    "checking if the current Python environment has all packages installed"
    "."
)

try:
    # Quicker way of checking if an environment has all packages installed.
    # It is faster than running pip install ... every time.
    # https://stackoverflow.com/a/65606063/598057
    # Modified to read from pyproject.toml, not requirements.txt file.
    pyproject_content = toml.load("pyproject.toml")
    dependencies = pyproject_content["project"]["dependencies"]
    dependencies_development = pyproject_content["project"][
        "optional-dependencies"
    ]["development"]
    pkg_resources.require(dependencies)
    pkg_resources.require(dependencies_development)
except pkg_resources.DistributionNotFound as exception:
    print(f"check_environment.py: {exception}")
    sys.exit(11)

print(f"check_environment.py: all packages seem to be installed.")
