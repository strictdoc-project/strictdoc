import strictdoc


class AboutCommand:
    @staticmethod
    def execute():
        print("=============")
        print("= StrictDoc =")
        print("=============")
        print(
            "Purpose: Software for writing technical requirements specifications."  # noqa: E501
        )
        print(f"Version: {strictdoc.__version__}")
        print("Docs:    https://strictdoc.readthedocs.io/en/stable/")
        print("Github:  https://github.com/strictdoc-project/strictdoc")
        print("License: Apache 2")
