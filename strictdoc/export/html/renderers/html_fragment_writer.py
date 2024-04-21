# mypy: disable-error-code="no-untyped-def"
class HTMLFragmentWriter:
    @staticmethod
    def write(text_fragment):
        return text_fragment

    @staticmethod
    def write_link(title, _):
        return f"{title}"
