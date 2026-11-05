"""
@relation(SDOC-SRS-142, SDOC-SRS-208, scope=file)
"""

import re
from typing import List, Optional

from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.modelica_scanner import (
    ModelicaItem,
    ModelicaItemKind,
    ModelicaScanError,
    scan_modelica,
)
from strictdoc.backend.sdoc_source_code.models.language import LanguageItem
from strictdoc.backend.sdoc_source_code.models.language_item_marker import (
    LanguageItemMarker,
    RangeMarkerType,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    RelationMarkerType,
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.models.source_location import ByteRange
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.backend.sdoc_source_code.processors.general_language_marker_processors import (
    language_item_marker_processor,
    line_marker_processor,
    range_marker_processor,
    source_file_traceability_info_processor,
)
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.helpers.file_stats import SourceFileStats
from strictdoc.helpers.file_system import file_open_read_bytes

UTF8_BOM = b"\xef\xbb\xbf"

_TEXT_BEFORE_MARKER_REGEX = re.compile(r"^[^\n]*?(?=@relation[\(\{])", re.M)


class SourceFileTraceabilityReader_Modelica:
    @staticmethod
    def supported_elements() -> list[str]:
        return ["class", "function"]

    def read(
        self, input_buffer: bytes, file_path: Optional[str] = None
    ) -> SourceFileTraceabilityInfo:
        assert isinstance(input_buffer, bytes)

        traceability_info = SourceFileTraceabilityInfo([])

        if len(input_buffer) == 0:
            return traceability_info

        bom_length = len(UTF8_BOM) if input_buffer.startswith(UTF8_BOM) else 0
        source = input_buffer[bom_length:]

        try:
            scan_result = scan_modelica(source)
        except ModelicaScanError as exception_:
            return self._read_without_language_items(
                source, file_path, exception_
            )

        parse_context = ParseContext(
            file_path, SourceFileStats.create(input_buffer)
        )

        def create_byte_range(byte_begin: int, byte_end: int) -> ByteRange:
            return ByteRange(byte_begin + bom_length, byte_end + bom_length)

        for item_ in scan_result.items:
            markers: List[RelationMarkerType] = []
            if item_.description_byte_range is not None:
                description_begin, description_end = (
                    item_.description_byte_range
                )
                description = source[description_begin:description_end].decode(
                    "utf-8"
                )
                if "@relation" in description:
                    markers = self._read_description_markers(
                        item=item_,
                        description=description,
                        description_line=source.count(
                            b"\n", 0, description_begin
                        )
                        + 1,
                        description_byte_range=create_byte_range(
                            description_begin, description_end
                        ),
                        parse_context=parse_context,
                        traceability_info=traceability_info,
                    )
            traceability_info.functions.append(
                LanguageItem(
                    parent=traceability_info,
                    name=item_.name,
                    display_name=item_.name,
                    line_begin=item_.line_begin,
                    line_end=item_.line_end,
                    code_byte_range=create_byte_range(
                        item_.byte_begin, item_.byte_end
                    ),
                    child_functions=[],
                    markers=[],
                    attributes=set(),
                )
            )
            traceability_info.ng_map_names_to_markers[item_.name] = markers

        # A final newline does not open a line that StrictDoc displays.
        last_line = source.count(b"\n") + (0 if source.endswith(b"\n") else 1)

        for comment_ in scan_result.comments:
            comment = source[comment_.byte_begin : comment_.byte_end].decode(
                "utf-8"
            )
            if "@relation" not in comment:
                continue
            source_node = MarkerParser.parse(
                input_string=_blank_text_before_markers(comment),
                line_start=1,
                line_end=last_line,
                comment_line_start=comment_.line_begin,
                comment_byte_range=create_byte_range(
                    comment_.byte_begin, comment_.byte_end
                ),
                filename=parse_context.filename,
                entity_name=None,
            )
            for marker_ in source_node.markers:
                if isinstance(marker_, RangeMarker):
                    range_marker_processor(marker_, parse_context)
                elif isinstance(marker_, LineMarker):
                    line_marker_processor(marker_, parse_context)
                elif (
                    isinstance(marker_, LanguageItemMarker)
                    and marker_.scope is RangeMarkerType.FILE
                ):
                    language_item_marker_processor(marker_, parse_context)
                    traceability_info.markers.append(marker_)
                else:
                    self._print_warning(
                        file_path,
                        comment_.line_begin,
                        f"skipping a scope={marker_.scope.value} marker "
                        "in a comment. A class or component marker belongs "
                        "in the description string of the class or "
                        "component.",
                    )

        source_file_traceability_info_processor(
            traceability_info, parse_context
        )
        return traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        with file_open_read_bytes(file_path) as file:
            return self.read(file.read(), file_path=file_path)

    def _read_description_markers(
        self,
        *,
        item: ModelicaItem,
        description: str,
        description_line: int,
        description_byte_range: ByteRange,
        parse_context: ParseContext,
        traceability_info: SourceFileTraceabilityInfo,
    ) -> List[RelationMarkerType]:
        """
        Read the markers of the description string of a class or component.

        The scope of a marker is the item that the description string
        describes, so the marker can omit the scope. A marker with another
        scope is skipped with a warning.
        """
        item_scope = (
            RangeMarkerType.CLASS
            if item.kind is ModelicaItemKind.CLASS
            else RangeMarkerType.COMPONENT
        )
        source_node = MarkerParser.parse(
            input_string=_blank_text_before_markers(description),
            line_start=item.line_begin,
            line_end=item.line_end,
            comment_line_start=description_line,
            comment_byte_range=description_byte_range,
            filename=parse_context.filename,
            entity_name=item.name,
            default_scope=item_scope.value,
        )
        markers: List[RelationMarkerType] = []
        for marker_ in source_node.markers:
            if (
                isinstance(marker_, LanguageItemMarker)
                and marker_.scope is item_scope
            ):
                language_item_marker_processor(marker_, parse_context)
                traceability_info.markers.append(marker_)
                markers.append(marker_)
                continue
            scope = (
                marker_.scope.value
                if isinstance(marker_, LanguageItemMarker)
                else "line"
                if isinstance(marker_, LineMarker)
                else "range"
            )
            self._print_warning(
                parse_context.filename,
                description_line,
                f"skipping a scope={scope} marker in the description string "
                f"of the {item_scope.value} {item.name}: only "
                f"scope={item_scope.value} is valid there.",
            )
        return markers

    @classmethod
    def _read_without_language_items(
        cls,
        source: bytes,
        file_path: Optional[str],
        exception: ModelicaScanError,
    ) -> SourceFileTraceabilityInfo:
        """
        Read the file, line and range markers of a file that the scanner
        cannot follow, for example a file with a syntax error.

        @relation(SDOC-LLR-223, scope=function)
        """
        cls._print_warning(
            file_path,
            exception.line,
            f"{exception.message}. Reading the file, line and range "
            "markers of the file without classes and components.",
        )
        return SourceFileTraceabilityReader().read(
            source.decode("utf-8"), file_path=file_path
        )

    @staticmethod
    def _print_warning(
        file_path: Optional[str], line: int, message: str
    ) -> None:
        print(  # noqa: T201
            f"warning: Modelica source reader: {file_path}:{line}: {message}"
        )


def _blank_text_before_markers(text: str) -> str:
    """
    Replace the text before each marker on its line with spaces.

    The marker grammar expects a marker at the start of a line. Examples of
    text before a marker: the opening quote of a description string, the
    description itself, and "/*" of a block comment. The replacement keeps
    all offsets.
    """
    return _TEXT_BEFORE_MARKER_REGEX.sub(
        lambda match_: " " * len(match_.group()), text
    )
