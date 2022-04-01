# -*- coding: utf-8 -*-
import glob
import os

from setuptools import setup, find_packages

package_data = {}

data_files = []
start_point = os.path.join("strictdoc", "export", "html")
for root, dirs, files in os.walk(start_point):
    root_files = []
    for file in files:
        if file.endswith(".py") or file.endswith(".pyc"):
            continue
        root_files.append(os.path.join(root, file))
    if len(root_files) > 0:
        data_files.append((root, root_files))

REQUIREMENTS = [
    'dataclasses==0.7; python_version >= "3.6" and python_version < "3.7" and python_full_version >= "3.6.2"',
    "textx==2.3.0",
    "jinja2>=2.11.2,<=4.0",
    "docutils~=0.16",
    "XlsxWriter~=1.3.7",
    "python-datauri~=0.2.9",
    "beautifulsoup4~=4.9.3",
    "pygments~=2.10.0",
    "lxml~=4.6.2",
    "reqif~=0.0.18",
    "pyfakefs~=4.5.5",
]


REQUIREMENTS_SETUP = [
    "wheel",
]


REQUIREMENTS_DEVELOPMENT = {
    "development": [
        "wheel",
        "tween",
        "coverage~=5.4",
        "invoke~=1.4.1",
        "pytest~=6.2.2",
        "lit~=0.11.0.post1",
        "mypy~=0.910",
        "filecheck~=0.0.20",
        "black~=21.9b0",
        "click==8.0.0",  # https://github.com/psf/black/issues/2964
        "pylint~=2.11.1",
        "flake8~=3.9.2",
        "sphinx~=3.2.1",
        "guzzle_sphinx_theme~=0.7.11",
        "html5lib~=1.1",
        "pytidylib~=0.3.2",
        "openpyxl~=3.0.5",
    ]
}

extras_require = {
    ':python_version >= "3.6" and python_version < "3.7"': [
        "dataclasses>=0.7,<0.8"
    ]
}

entry_points = {"console_scripts": ["strictdoc = strictdoc.cli.main:main"]}

setup_kwargs = {
    "name": "strictdoc",
    "version": "0.0.21",
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
    "package_data": package_data,
    # 'package_dir': {"": "strictdoc"},
    "data_files": data_files,
    "install_requires": REQUIREMENTS,
    "extras_require": REQUIREMENTS_DEVELOPMENT,
    "setup_requires": REQUIREMENTS_SETUP,
    "entry_points": entry_points,
    "python_requires": ">=3.6.2,<4.0.0",
}


setup(**setup_kwargs)
