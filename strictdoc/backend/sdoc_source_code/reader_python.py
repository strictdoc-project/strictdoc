# mypy: disable-error-code="no-redef,no-untyped-call,no-untyped-def,type-arg,var-annotated"
import sys
import traceback
from typing import List, Optional, Union

import tree_sitter_python
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


class SourceFileTraceabilityReader_Python:
    def read(self, input_buffer: bytes, file_path=None):
        assert isinstance(input_buffer, bytes)

        file_size = len(input_buffer)

        traceability_info = SourceFileTraceabilityInfo([])

        if file_size == 0:
            return traceability_info

        length = get_lines_count(input_buffer)
        parse_context = ParseContext(file_path, length)

        # Works since Python 3.9 but we also lint this with mypy from Python 3.8.
        language_arg = tree_sitter_python.language()
        py_language = Language(  # type: ignore[call-arg, unused-ignore]
            language_arg
        )
        parser = Parser(py_language)  # type: ignore[call-arg, unused-ignore]

        tree = parser.parse(input_buffer)

        functions_stack: List[Function] = []

        nodes = traverse_tree(tree)
        map_function_to_node = {}
        for node_ in nodes:
            if node_.type == "module":
                function = Function(
                    parent=None,
                    name="module",
                    line_begin=node_.start_point[0] + 1,
                    line_end=node_.end_point[0] + 1,
                    parts=[],
                )
                functions_stack.append(function)
                map_function_to_node[function] = node_
            elif node_.type == "function_definition":
                function_name: str = ""
                function_block: Optional[Node] = None

                # assert 0, node_.children
                for child_ in node_.children:
                    if child_.type == "identifier":
                        if child_.text is not None:
                            function_name = child_.text.decode("utf-8")
                    if child_.type == "function_declarator":
                        # FIXME
                        # assert 0, child_.children
                        function_name = "FOO"
                    if child_.type == "block":
                        function_block = child_

                assert function_name is not None, "Function name"

                block_comment = None
                if (
                    function_block is not None
                    and len(function_block.children) > 0
                    and function_block.children[0].type
                    == "expression_statement"
                ):
                    if len(function_block.children[0].children) > 0:
                        if (
                            function_block.children[0].children[0].type
                            == "string"
                        ):
                            block_comment = function_block.children[0].children[
                                0
                            ]
                            # string contains of three parts:
                            # string_start string_content string_end
                            string_content = block_comment.children[1]
                            assert string_content.text is not None

                            block_comment_text = string_content.text.decode(
                                "utf-8"
                            )
                            markers = MarkerParser.parse(
                                block_comment_text,
                                node_.start_point[0] + 1,
                                node_.end_point[0] + 1,
                                string_content.start_point[0] + 1,
                                string_content.start_point[1] + 1,
                            )
                            for marker_ in markers:
                                if isinstance(
                                    marker_, FunctionRangeMarker
                                ) and (function_range_marker_ := marker_):
                                    function_range_marker_processor(
                                        function_range_marker_, parse_context
                                    )
                                    traceability_info.markers.append(
                                        function_range_marker_
                                    )

                # FIXME: This look more complex than needed but can't make mypy happy.
                cursor_: Optional[Node] = node_
                while cursor_ is not None and (cursor_ := cursor_.parent):
                    if cursor_ == map_function_to_node[functions_stack[-1]]:
                        break
                    if cursor_.type == "function_definition":
                        functions_stack.pop()
                        assert len(functions_stack) > 0
                else:
                    # This is counterintuitive:
                    # The top-level functions don't have the top-level module set
                    # as their parent, so in this branch, we simply clear the whole
                    # function stack, leaving the top module only.
                    functions_stack = functions_stack[:1]

                new_function = Function(
                    parent=None,
                    name=function_name,
                    line_begin=node_.range.start_point[0] + 1,
                    line_end=node_.range.end_point[0] + 1,
                    parts=[],
                )
                map_function_to_node[new_function] = node_

                parent_function = functions_stack[-1]

                parent_function.parts.append(new_function)
                functions_stack.append(new_function)
                traceability_info.functions.append(new_function)
            elif node_.type == "comment":
                # A marker example:
                # @sdoc[REQ-001]
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
                        range_marker := marker_
                    ):
                        range_marker_processor(range_marker, parse_context)
                    elif isinstance(marker_, LineMarker) and (
                        line_marker := marker_
                    ):
                        line_marker_processor(line_marker, parse_context)
                    else:
                        continue
            else:
                pass

        assert (
            functions_stack[0].name == "module"
            or functions_stack[0].name == "translation_unit"
        )

        traceability_info.parts = functions_stack[0].parts

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
