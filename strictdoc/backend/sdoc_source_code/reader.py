"""
@relation(SDOC-SRS-142, scope=file)
"""

import threading
from functools import partial
from typing import ClassVar, Optional, TypedDict

from textx import get_location, metamodel_from_str
from textx.metamodel import TextXMetaModel

from strictdoc.backend.sdoc_source_code.grammar import SOURCE_FILE_GRAMMAR
from strictdoc.backend.sdoc_source_code.models.language_item_marker import (
    LanguageItemMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.backend.sdoc_source_code.processors.general_language_marker_processors import (
    _handle_skip_marker,
    create_begin_end_range_reqs_mismatch_error,
    create_end_without_begin_error,
    create_unmatch_range_error,
    line_marker_processor,
    validate_marker_uids,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_stats import SourceFileStats
from strictdoc.helpers.file_system import file_open_read_utf8
from strictdoc.helpers.textx import drop_textx_meta


class TextXLocation(TypedDict):
    line: int
    col: int
    filename: str


def req_processor(req: Req) -> None:
    assert isinstance(req, Req), (
        f"Expected req to be Req, got: {req}, {type(req)}"
    )
    location = get_location(req)
    assert location
    req.ng_source_line = location["line"]
    req.ng_source_column = location["col"]


def source_file_traceability_info_processor(
    source_file_traceability_info: SourceFileTraceabilityInfo,
    parse_context: ParseContext,
) -> None:
    if len(parse_context.marker_stack) > 0:
        if any(
            not marker_.ng_is_nodoc for marker_ in parse_context.marker_stack
        ):
            raise create_unmatch_range_error(
                parse_context.marker_stack, filename=parse_context.filename
            )
    source_file_traceability_info.markers = parse_context.markers
    source_file_traceability_info.file_stats = parse_context.file_stats


def range_marker_processor(
    marker: RangeMarker, parse_context: ParseContext
) -> None:
    validate_marker_uids(marker, parse_context)

    location = get_location(marker)
    line = location["line"]
    column = location["col"]
    marker.ng_source_line_begin = line
    marker.ng_source_column_begin = column

    if marker.ng_is_nodoc:
        _handle_skip_marker(marker, parse_context)
        return

    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "@relation(skip...)" block, so we ignore it.
        return

    parse_context.markers.append(marker)

    if marker.is_begin():
        marker.ng_range_line_begin = line
        parse_context.marker_stack.append(marker)
        for req in marker.reqs:
            markers = parse_context.map_reqs_to_markers.setdefault(req, [])
            markers.append(marker)

    elif marker.is_end():
        try:
            current_top_marker = parse_context.marker_stack.pop()
            if marker.reqs != current_top_marker.reqs:
                raise create_begin_end_range_reqs_mismatch_error(
                    parse_context.filename,
                    assert_cast(current_top_marker.ng_source_line_begin, int),
                    assert_cast(current_top_marker.ng_range_line_begin, int),
                    current_top_marker.reqs,
                    marker.reqs,
                )
            current_top_marker.ng_range_line_end = line

            marker.ng_range_line_begin = current_top_marker.ng_range_line_begin
            marker.ng_range_line_end = line

        except IndexError:
            raise create_end_without_begin_error(
                parse_context.filename, line, location["col"]
            ) from None
    else:
        raise NotImplementedError


def language_item_marker_processor(
    language_item_marker: LanguageItemMarker, parse_context: ParseContext
) -> None:
    validate_marker_uids(language_item_marker, parse_context)

    location = get_location(language_item_marker)
    line = location["line"]
    column = location["col"]

    language_item_marker.ng_source_line_begin = line
    language_item_marker.ng_source_column_begin = column
    language_item_marker.ng_range_line_begin = 1
    language_item_marker.ng_range_line_end = (
        parse_context.file_stats.lines_total
    )

    if language_item_marker.ng_is_nodoc:
        _handle_skip_marker(language_item_marker, parse_context)
        return

    if (
        len(parse_context.marker_stack) > 0
        and parse_context.marker_stack[-1].ng_is_nodoc
    ):
        # This marker is within a "@relation(skip...)" block, so we ignore it.
        return

    parse_context.markers.append(language_item_marker)

    # Language item markers supported by this general reader can only
    # be of scope=file. Only the language-aware parsing results in
    # markers also having scope=function or scope=class.
    language_item_marker.set_description("entire file")

    for req in language_item_marker.reqs:
        markers = parse_context.map_reqs_to_markers.setdefault(req, [])
        markers.append(language_item_marker)


class SourceFileTraceabilityReader:
    SOURCE_FILE_MODELS = [
        LanguageItemMarker,
        LineMarker,
        Req,
        SourceFileTraceabilityInfo,
        RangeMarker,
    ]

    # Building a textX metamodel from SOURCE_FILE_GRAMMAR takes about 4.5 ms,
    # and a project can have thousands of source files. As a result, all
    # readers share one metamodel, which is built on first use.
    #
    # Source files are read when the traceability index is built:
    # - Export reads source files in its main thread.
    # - The server reads source files when it rebuilds the traceability index:
    #   at startup, in request handlers, and in the file watcher thread. The
    #   global write lock of the server lets only one rebuild run at a time.
    #
    # The reader does not rely on the callers to read one file at a time. The
    # lock lets only one thread at a time build the metamodel, register
    # processors, and parse, because textX is not thread-safe in three places:
    # - metamodel_from_str() parses the grammar with one parser that textX
    #   caches at module level and shares between all calls.
    # - The metamodel holds the object processors. read() registers new
    #   processors for each file because the processors write to the
    #   ParseContext of that file. Without the lock, a second thread can
    #   replace the processors while the first thread parses. The markers of
    #   one file then end up in the ParseContext of the other file.
    # - During each parse, textX replaces __setattr__, __getattribute__ and
    #   __delattr__ of the user classes (SOURCE_FILE_MODELS) and restores them
    #   at the end. textX tracks this with a counter on each class and no lock.
    #   Two parallel parses can restore the methods while one parse still needs
    #   them, or keep the replaced methods after both parses end. This risk
    #   exists even with one metamodel per thread, because all metamodels use
    #   the same user classes.
    #
    # With the current callers, no thread ever waits for the lock, so the lock
    # costs almost nothing.
    _meta_model: ClassVar[Optional[TextXMetaModel]] = None
    _meta_model_lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def supported_elements() -> list[str]:
        return []

    def read(
        self, input_string: str, file_path: Optional[str] = None
    ) -> SourceFileTraceabilityInfo:
        # TODO: This might be possible to handle directly in the textx grammar.
        # AttributeError: 'str' object has no attribute '_tx_parser'.
        file_size = len(input_string)
        if file_size == 0:
            return SourceFileTraceabilityInfo([])

        file_stats = SourceFileStats.create(input_string)
        parse_context = ParseContext(file_path, file_stats)

        parse_source_traceability_processor = partial(
            source_file_traceability_info_processor, parse_context=parse_context
        )
        parse_req_processor = partial(req_processor)
        parse_range_marker_processor = partial(
            range_marker_processor, parse_context=parse_context
        )
        parse_line_marker_processor = partial(
            line_marker_processor, parse_context=parse_context
        )
        parse_language_item_marker_processor = partial(
            language_item_marker_processor, parse_context=parse_context
        )

        obj_processors = {
            "LanguageItemMarker": parse_language_item_marker_processor,
            "LineMarker": parse_line_marker_processor,
            "RangeMarker": parse_range_marker_processor,
            "Req": parse_req_processor,
            "SourceFileTraceabilityInfo": parse_source_traceability_processor,
        }

        with SourceFileTraceabilityReader._meta_model_lock:
            meta_model = SourceFileTraceabilityReader._get_meta_model()
            meta_model.register_obj_processors(obj_processors)
            source_file_traceability_info: SourceFileTraceabilityInfo = (
                meta_model.model_from_str(input_string, file_name=file_path)
            )
        source_file_traceability_info.ng_map_reqs_to_markers = (
            parse_context.map_reqs_to_markers
        )

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        drop_textx_meta(source_file_traceability_info)
        return source_file_traceability_info

    @staticmethod
    def _get_meta_model() -> TextXMetaModel:
        """
        Return the shared metamodel. The caller must hold _meta_model_lock.

        The metamodel is built on the first read, not at import time. Every
        export and every server start imports this module, also for projects
        without source files. A build at import time would add about 5-13 ms
        to each of these processes.
        """
        if SourceFileTraceabilityReader._meta_model is None:
            SourceFileTraceabilityReader._meta_model = metamodel_from_str(
                SOURCE_FILE_GRAMMAR,
                classes=SourceFileTraceabilityReader.SOURCE_FILE_MODELS,
                use_regexp_group=True,
            )
        return SourceFileTraceabilityReader._meta_model

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        with file_open_read_utf8(file_path) as file:
            sdoc_content = file.read()
            sdoc = self.read(sdoc_content, file_path=file_path)
            return sdoc
