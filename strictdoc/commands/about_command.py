import strictdoc


class AboutCommand:
    @staticmethod
    def execute() -> None:
        print("=============")  # noqa: T201
        print("= StrictDoc =")  # noqa: T201
        print("=============")  # noqa: T201
        print(  # noqa: T201
            "Purpose: Software for writing technical requirements specifications."
        )
        print(f"Version: {strictdoc.__version__}")  # noqa: T201
        print(  # noqa: T201
            "Docs:    https://strictdoc.readthedocs.io/en/stable/"
        )
        print(  # noqa: T201
            "Github:  https://github.com/strictdoc-project/strictdoc"
        )
        print("License: Apache 2")  # noqa: T201
