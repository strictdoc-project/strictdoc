import io
import os
import re
import sys
from typing import Optional

from docutils.core import publish_parts
from docutils.parsers.rst import directives
from docutils.utils import SystemMessage

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.export.rst.directives.wildcard_enhanced_image import (
    WildcardEnhancedImage,
)


class RstToHtmlFragmentWriter:
    cache = {}

    directives.register_directive("image", WildcardEnhancedImage)

    def __init__(self, *, context_document: Optional[Document]):
        if context_document is not None:
            WildcardEnhancedImage.current_reference_path = (
                context_document.meta.output_document_dir_full_path
            )

            # This is a delicate move. Based on a user report and our findings,
            # the csv-table RST directive relies on the 'source path' to
            # calculate paths to CSV files.
            # Our case is, however, special: we do not render RST files but
            # rather RST fragments in memory, and because of that we don't have
            # RST files to point to with 'source_path=' below.
            # At the same time, passing the output folder of the document works
            # because this RST-to-HTML writer resolves path to CSV assets
            # that are copied to that output folder by StrictDoc.
            # See CSVTable().get_csv_data() where the source_path is used.
            self.source_path: str = os.path.join(
                context_document.meta.output_document_dir_full_path,
                "STRICTDOC-FRAGMENT.rst",
            )
        else:
            self.source_path: str = "<string>"
        self.context_document: Optional[Document] = context_document

    def write(self, rst_fragment):
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
            rst_fragment,
            writer_name="html",
            settings_overrides=settings,
            source_path=self.source_path,
        )

        if warning_stream.tell() > 0:
            warnings = warning_stream.getvalue().rstrip("\n")
            # A typical RST warning:
            # """
            # path-to-output-folder/file.rst:4: (WARNING/2) Bullet list ends
            # without a blank line; unexpected unindent.
            # """
            match = re.search(
                r".*:(?P<line>\d+): \(.*\) (?P<message>.*)", warnings
            )
            if match is not None:
                error_message = (
                    f"RST markup syntax error on line {match.group('line')}: "
                    f"{match.group('message')}"
                )
            else:
                error_message = f"RST markup syntax error: {warnings}"
            print(  # noqa: T201
                f"error: problems when converting RST to HTML:\n{error_message}"
            )
            print("RST fragment: >>>")  # noqa: T201
            print(rst_fragment)  # noqa: T201
            print("<<<")  # noqa: T201
            sys.exit(1)

        html = output["html_body"]

        RstToHtmlFragmentWriter.cache[rst_fragment] = html

        return html

    def write_with_validation(self, rst_fragment):
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
