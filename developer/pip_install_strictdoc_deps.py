import os
import subprocess
import sys
import tempfile

import pkg_resources
import toml

print(  # noqa: T201
    "pip_install_strictdoc_deps.py: "
    "checking if the current Python environment has all packages installed"
    ".",
    flush=True
)

pyproject_content = toml.load("pyproject.toml")

# The development dependencies are ignored, because they are managed in tox.ini.
dependencies = pyproject_content["project"]["dependencies"]

needs_installation = False
try:
    # Quicker way of checking if an environment has all packages installed.
    # It is faster than running pip install ... every time.
    # https://stackoverflow.com/a/65606063/598057
    pkg_resources.require(dependencies)
except pkg_resources.DistributionNotFound as exception:
    print(  # noqa: T201
        f"pip_install_strictdoc_deps.py: {exception}", flush=True
    )
    needs_installation = True

if not needs_installation:
    print(  # noqa: T201
        "pip_install_strictdoc_deps.py: all packages seem to be installed.",
        flush=True
    )
    sys.exit(0)

all_packages = "\n".join(dependencies) + "\n"

with tempfile.TemporaryDirectory() as tmp_dir:
    with open(
        os.path.join(tmp_dir, "requirements.txt"), "w", encoding="utf8"
    ) as tmp_requirements_txt_file:
        tmp_requirements_txt_file.write(all_packages)

    command = [
        sys.executable, "-m", "pip", "install", "-r", tmp_requirements_txt_file.name
    ]

    result = subprocess.run(
        command,
        check=True,
        encoding="utf8"
    )
    print(  # noqa: T201
        f"'pip install' command exited with: {result.returncode}", flush=True
    )
