import io
import re
import sys

from docutils.core import publish_parts
from docutils.utils import SystemMessage


class RstToHtmlFragmentWriter:
    cache = {}

    @staticmethod
    def write(rst_fragment):
        assert isinstance(rst_fragment, str), rst_fragment
        if rst_fragment in RstToHtmlFragmentWriter.cache:
            return RstToHtmlFragmentWriter.cache[rst_fragment]

        # How do I convert a docutils document tree into an HTML string?
        # https://stackoverflow.com/a/32168938/598057
        # Use a io.StringIO as the warning stream to prevent warnings from
        # being printed to sys.stderr.
        # https://www.programcreek.com/python/example/88126/docutils.core.publish_parts
        warning_stream = io.StringIO()
        settings = {"warning_stream": warning_stream}

        output = publish_parts(
            rst_fragment, writer_name="html", settings_overrides=settings
        )

        if warning_stream.tell() > 0:
            warnings = warning_stream.getvalue().rstrip("\n")
            print("error: problems when converting RST to HTML:")
            print(warnings)
            print("RST fragment: >>>")
            print(rst_fragment)
            print("<<<")
            sys.exit(1)

        html = output["html_body"]

        RstToHtmlFragmentWriter.cache[rst_fragment] = html

        return html

    @staticmethod
    def write_with_validation(rst_fragment):
        # How do I convert a docutils document tree into an HTML string?
        # https://stackoverflow.com/a/32168938/598057
        # Use a io.StringIO as the warning stream to prevent warnings from
        # being printed to sys.stderr.
        # https://www.programcreek.com/python/example/88126/docutils.core.publish_parts
        warning_stream = io.StringIO()
        settings = {"warning_stream": warning_stream}

        try:
            output = publish_parts(
                rst_fragment, writer_name="html", settings_overrides=settings
            )
            warnings = (
                warning_stream.getvalue().rstrip("\n")
                if warning_stream.tell() > 0
                else None
            )
        except SystemMessage as exception:
            output = None
            warnings = str(exception)

        if warnings is not None and len(warnings) > 0:
            # A typical RST warning:
            # """
            # <string>:4: (WARNING/2) Bullet list ends without a blank line;
            # unexpected unindent.
            # """
            match = re.search(
                r".*<.*>:(?P<line>\d+): \(.*\) (?P<message>.*)", warnings
            )
            if match is not None:
                error_message = (
                    f"RST markup syntax error on line {match.group('line')}: "
                    f"{match.group('message')}"
                )
            else:
                error_message = f"RST markup syntax error: {warnings}"
            return None, error_message

        html = output["html_body"]

        return html, None

    @staticmethod
    def write_link(title, href):
        return f"`{title} <{href}>`_"
