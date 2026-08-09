import importlib.metadata as importlib_metadata
import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile

import toml
from packaging.requirements import Requirement


class PackageNotFound(Exception):
    pass


class PackageVersionConflict(Exception):
    pass


def link_nix_numpy_stack_if_available() -> None:
    """
    If STRICTDOC_NIX_NUMPY_STACK is set (only ever done by flake.nix's
    devShell, never on a non-Nix setup), symlink those Nix-built
    packages (numpy, pandas, ...) into this venv's site-packages instead
    of leaving them to be pip-installed from PyPI below. This avoids
    pip-installed manylinux wheels for numpy/pandas needing libstdc++.so.6
    at runtime, which Nix's own dynamic linker won't find unpatched --
    see flake.nix for the full explanation.
    """
    nix_stack_paths = os.environ.get("STRICTDOC_NIX_NUMPY_STACK")
    if not nix_stack_paths:
        return

    site_packages = sysconfig.get_path("purelib")
    python_dir = f"python{sys.version_info.major}.{sys.version_info.minor}"

    for nix_pkg_path in nix_stack_paths.split():
        nix_site_packages = os.path.join(
            nix_pkg_path, "lib", python_dir, "site-packages"
        )
        if not os.path.isdir(nix_site_packages):
            continue
        for entry in os.listdir(nix_site_packages):
            source = os.path.join(nix_site_packages, entry)
            target = os.path.join(site_packages, entry)
            if os.path.islink(target) and os.readlink(target) == source:
                # Already linked to this exact Nix store path.
                continue
            if os.path.isdir(target) and not os.path.islink(target):
                # A real (e.g. pip-installed) copy from before -- replace
                # it so this is self-healing on an existing venv.
                shutil.rmtree(target)
            elif os.path.exists(target) or os.path.islink(target):
                os.remove(target)
            os.symlink(source, target)


# A simplified version inspired by:
# https://github.com/HansBug/hbutils/blob/37879186c489bced2791309c43d131f1703b7bd4/hbutils/system/python/package.py#L171
def check_if_package_installed(package_name: str):
    requirement: Requirement = Requirement(package_name)
    try:
        version = importlib_metadata.distribution(requirement.name).version
    except importlib_metadata.PackageNotFoundError:
        raise PackageNotFound(requirement) from None
    if not requirement.specifier.contains(version):
        raise PackageVersionConflict(version)


link_nix_numpy_stack_if_available()

print(  # noqa: T201
    "pip_install_strictdoc_deps.py: "
    "checking if the current Python environment has all packages installed"
    ".",
    flush=True,
)

pyproject_content = toml.load("pyproject.toml")


# The development dependencies are ignored, because they are managed in tox.ini.
dependencies = pyproject_content["project"]["dependencies"]

needs_installation = False

for dependency in dependencies:
    try:
        check_if_package_installed(dependency)
    except PackageNotFound:
        print(  # noqa: T201
            f"pip_install_strictdoc_deps.py: "
            f"Package is not installed: '{dependency}'.",
            flush=True,
        )
        needs_installation = True
        break
    except PackageVersionConflict as exception_:
        print(  # noqa: T201
            (
                f"pip_install_strictdoc_deps.py: version conflict between "
                f"StrictDoc's requirement '{dependency}' "
                f"and the already installed package: "
                f"{exception_.args[0]}."
            ),
            flush=True,
        )
        needs_installation = True
        break

if not needs_installation:
    print(  # noqa: T201
        "pip_install_strictdoc_deps.py: all packages seem to be installed.",
        flush=True,
    )
    sys.exit(0)

print(  # noqa: T201
    "pip_install_strictdoc_deps.py: will install packages.", flush=True
)

all_packages = "\n".join(dependencies) + "\n"

with tempfile.TemporaryDirectory() as tmp_dir:
    with open(
        os.path.join(tmp_dir, "requirements.txt"), "w", encoding="utf8"
    ) as tmp_requirements_txt_file:
        tmp_requirements_txt_file.write(all_packages)

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        tmp_requirements_txt_file.name,
    ]

    result = subprocess.run(command, check=True, encoding="utf8")
    print(  # noqa: T201
        f"'pip install' command exited with: {result.returncode}", flush=True
    )
