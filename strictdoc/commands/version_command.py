from pathlib import Path

import toml


class VersionCommand:
    @staticmethod
    def execute():
        path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(str(path), "r", encoding="utf-8") as file_handle:
            pyproject = toml.loads(file_handle.read())
        print(pyproject["tool"]["poetry"]["version"])
