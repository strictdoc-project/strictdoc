import pkg_resources


class VersionCommand:
    @staticmethod
    def execute():
        version = pkg_resources.require("strictdoc")[0].version
        print(version)
