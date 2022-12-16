# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

import strictdoc

package_data = {
    "": ["requirements.txt", "requirements.development.txt"],
    # It looks like the package data in setup.py does not support globbing
    # (see pypa/setuptools#1806, https://github.com/pypa/setuptools/issues/1806)
    # Doing the globbing manually for now.
    # https://stackoverflow.com/questions/27664504/how-to-add-package-data-recursively-in-python-setup-py
    # TODO: Can be better.
    "strictdoc.export.html": [
        "*",
        "*/*",
        "*/*/*",
        "*/*/*/*",
        "*/*/*/*/*",
        "*/*/*/*/*/*",
    ],
    "strictdoc.export.rst": [
        "*",
        "*/*",
        "*/*/*",
        "*/*/*/*",
        "*/*/*/*/*",
        "*/*/*/*/*/*",
    ],
}

with open("requirements.txt") as fp:
    REQUIREMENTS = fp.read()

with open("requirements.development.txt") as fp:
    REQUIREMENTS_DEVELOPMENT = {"development": fp.read()}

REQUIREMENTS_SETUP = [
    "wheel",
]


extras_require = {
    ':python_version >= "3.6" and python_version < "3.7"': [
        "dataclasses>=0.7,<0.8"
    ]
}

entry_points = {"console_scripts": ["strictdoc = strictdoc.cli.main:main"]}

setup_kwargs = {
    "name": "strictdoc",
    "version": strictdoc.__version__,
    "description": "Software for writing technical requirements and specifications.",
    "long_description": "Software for writing technical requirements and specifications.",
    "author": "Stanislav Pankevich",
    "author_email": "s.pankevich@gmail.com",
    "maintainer": "Stanislav Pankevich",
    "maintainer_email": "s.pankevich@gmail.com",
    "url": "https://github.com/stanislaw/strictdoc",
    "packages": find_packages(
        where=".",
        exclude=[
            "tests*",
        ],
    ),
    # 'package_dir': {"": "strictdoc"},
    # package_data - defines files related to the python package, e.g.,
    #                documentation, static image files, configurations.
    # data_files -   defines files that will be installed system-wise, not in
    #                site-package directory. eg. desktop icons, fonts.
    # https://stackoverflow.com/a/66370532/598057
    "package_data": package_data,
    "data_files": [],
    "install_requires": REQUIREMENTS,
    "extras_require": REQUIREMENTS_DEVELOPMENT,
    "setup_requires": REQUIREMENTS_SETUP,
    "entry_points": entry_points,
    "python_requires": ">=3.6.2,<4.0.0",
}

setup(**setup_kwargs)
