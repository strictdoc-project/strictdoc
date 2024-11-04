# mypy: disable-error-code="no-redef,no-untyped-call,no-untyped-def,type-arg,var-annotated"
import sys
import traceback
from typing import List, Optional, Union

import tree_sitter_c
from tree_sitter import Language, Node, Parser

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    LineMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.parse_context import ParseContext
from strictdoc.backend.sdoc_source_code.processors.general_language_marker_processors import (
    function_range_marker_processor,
    line_marker_processor,
    range_marker_processor,
    source_file_traceability_info_processor,
)
from strictdoc.backend.sdoc_source_code.tree_sitter_helpers import traverse_tree
from strictdoc.helpers.string import get_lines_count


class SourceFileTraceabilityReader_C:
    def read(
        self, input_buffer: bytes, file_path=None
    ) -> SourceFileTraceabilityInfo:
        assert isinstance(input_buffer, bytes)

        file_size = len(input_buffer)

        traceability_info = SourceFileTraceabilityInfo([])

        if file_size == 0:
            return traceability_info

        length = get_lines_count(input_buffer)
        parse_context = ParseContext(file_path, length)

        # Works since Python 3.9 but we also lint this with mypy from Python 3.8.
        language_arg = tree_sitter_c.language()
        py_language = Language(  # type: ignore[call-arg, unused-ignore]
            language_arg
        )
        parser = Parser(py_language)  # type: ignore[call-arg, unused-ignore]

        tree = parser.parse(input_buffer)

        nodes = traverse_tree(tree)
        for node_ in nodes:
            if node_.type == "translation_unit":
                if (
                    len(node_.children) > 0
                    and node_.children[0].type == "comment"
                    and (comment_node := node_.children[0])
                ):
                    if comment_node.text is not None:
                        comment_text = comment_node.text.decode("utf-8")
                        markers = MarkerParser.parse(
                            comment_text,
                            node_.start_point[0] + 1,
                            # It is important that +1 is not present here because
                            # currently StrictDoc does not display the last empty line (\n is 10).
                            node_.end_point[0]
                            if input_buffer[-1] == 10
                            else node_.end_point[0] + 1,
                            node_.start_point[0] + 1,
                            node_.start_point[1] + 1,
                        )
                        for marker_ in markers:
                            if isinstance(marker_, FunctionRangeMarker) and (
                                function_range_marker_ := marker_
                            ):
                                function_range_marker_processor(
                                    function_range_marker_, parse_context
                                )
                                traceability_info.markers.append(
                                    function_range_marker_
                                )
            elif node_.type == "function_definition":
                function_name: str = ""

                for child_ in node_.children:
                    if child_.type == "function_declarator":
                        assert child_.children[0].type == "identifier"
                        assert child_.children[0].text

                        function_name = child_.children[0].text.decode("utf8")
                assert function_name is not None, "Function name"

                function_comment_node: Optional[Node] = None
                function_comment_text = None
                if (
                    node_.prev_sibling is not None
                    and node_.prev_sibling.type == "comment"
                ):
                    function_comment_node = node_.prev_sibling
                    assert function_comment_node.text is not None
                    function_comment_text = function_comment_node.text.decode(
                        "utf8"
                    )

                    function_last_line = node_.end_point[0] + 1

                    markers: List[
                        Union[FunctionRangeMarker, RangeMarker, LineMarker]
                    ] = MarkerParser.parse(
                        function_comment_text,
                        function_comment_node.start_point[0] + 1,
                        function_last_line,
                        function_comment_node.start_point[0] + 1,
                        function_comment_node.start_point[1] + 1,
                        entity_name=function_name,
                    )
                    for marker_ in markers:
                        if isinstance(marker_, FunctionRangeMarker) and (
                            function_range_marker_ := marker_
                        ):
                            function_range_marker_processor(
                                function_range_marker_, parse_context
                            )
                            traceability_info.markers.append(
                                function_range_marker_
                            )
                            traceability_info.parts.append(
                                function_range_marker_
                            )

                # The function range includes the top comment if it exists.
                new_function = Function(
                    parent=None,
                    name=function_name,
                    line_begin=function_comment_node.start_point[0] + 1
                    if function_comment_node is not None
                    else node_.range.start_point[0] + 1,
                    line_end=node_.range.end_point[0] + 1,
                    parts=[],
                )
                traceability_info.functions.append(new_function)
            elif node_.type == "comment":
                if node_.text is None:
                    raise NotImplementedError("Comment without a text")

                node_text_string = node_.text.decode("utf8")

                markers: List[
                    Union[FunctionRangeMarker, RangeMarker, LineMarker]
                ] = MarkerParser.parse(
                    node_text_string,
                    node_.start_point[0] + 1,
                    node_.end_point[0] + 1,
                    node_.start_point[0] + 1,
                    node_.start_point[1] + 1,
                )
                for marker_ in markers:
                    if isinstance(marker_, RangeMarker) and (
                        range_marker_ := marker_
                    ):
                        range_marker_processor(range_marker_, parse_context)
                        traceability_info.parts.append(range_marker_)
                    elif isinstance(marker_, LineMarker) and (
                        line_marker_ := marker_
                    ):
                        line_marker_processor(line_marker_, parse_context)
                        traceability_info.parts.append(line_marker_)
                    else:
                        continue
            else:
                pass

        source_file_traceability_info_processor(
            traceability_info, parse_context
        )

        traceability_info.ng_map_reqs_to_markers = (
            parse_context.map_reqs_to_markers
        )

        return traceability_info

    def read_from_file(self, file_path):
        try:
            with open(file_path, "rb") as file:
                sdoc_content = file.read()
                sdoc = self.read(sdoc_content, file_path=file_path)
                return sdoc
        except NotImplementedError:
            traceback.print_exc()
            sys.exit(1)
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            print(  # noqa: T201
                f"error: SourceFileTraceabilityReader_Python: could not parse file: "
                f"{file_path}.\n{exc.__class__.__name__}: {exc}"
            )
            # TODO: when --debug is provided
            # traceback.print_exc()  # noqa: ERA001
            sys.exit(1)
