"""
@relation(SDOC-SRS-142, scope=file)
"""

# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import sys
import traceback
from itertools import islice
from typing import List, Optional, Sequence

import tree_sitter_python
from tree_sitter import Language, Node, Parser

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    RelationMarkerType,
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
from strictdoc.helpers.file_stats import SourceFileStats


class SourceFileTraceabilityReader_Python:
    def read(
        self, input_buffer: bytes, file_path=None
    ) -> SourceFileTraceabilityInfo:
        assert isinstance(input_buffer, bytes)

        file_size = len(input_buffer)

        traceability_info = SourceFileTraceabilityInfo([])

        if file_size == 0:
            return traceability_info

        file_stats = SourceFileStats.create(input_buffer)
        parse_context = ParseContext(file_path, file_stats)

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
                    parent=traceability_info,
                    name="module",
                    display_name="module",
                    line_begin=node_.start_point[0] + 1,
                    line_end=node_.end_point[0] + 1,
                    child_functions=[],
                    markers=[],
                    attributes=set(),
                )
                functions_stack.append(function)
                map_function_to_node[function] = node_
                if len(node_.children) > 0:
                    # Look for the docstring within the first 30 children (arbitrary chosen limit)
                    # so that we dont miss it if the file starts with comments (#!, encoding marker, etc...).
                    first_match = next(
                        (
                            child
                            for child in islice(node_.children, 30)
                            if child.type == "expression_statement"
                            and len(child.children) > 0
                            and child.children[0].type == "string"
                        ),
                        None,
                    )

                    if first_match is not None:
                        block_comment = first_match.children[0]

                        # String contains of three parts:
                        # (string_start string_content string_end)
                        string_content = block_comment.children[1]
                        assert string_content.text is not None

                        block_comment_text = string_content.text.decode("utf-8")
                        source_node = MarkerParser.parse(
                            block_comment_text,
                            node_.start_point[0] + 1,
                            # It is important that +1 is not present here because
                            # currently StrictDoc does not display the last empty line (\n is 10).
                            node_.end_point[0]
                            if input_buffer[-1] == 10
                            else node_.end_point[0] + 1,
                            string_content.start_point[0] + 1,
                        )
                        for marker_ in source_node.markers:
                            if isinstance(marker_, FunctionRangeMarker) and (
                                function_range_marker_ := marker_
                            ):
                                function_range_marker_processor(
                                    function_range_marker_, parse_context
                                )
                                traceability_info.markers.append(
                                    function_range_marker_
                                )

            elif node_.type in ("class_definition", "function_definition"):
                function_name: str = ""
                function_block: Optional[Node] = None

                for child_ in node_.children:
                    if child_.type == "identifier":
                        if child_.text is not None:
                            function_name = child_.text.decode("utf-8")
                    if child_.type == "block":
                        function_block = child_

                assert function_name is not None, "Function name"

                parent_names = self.get_node_ns(node_)
                if parent_names:
                    function_name = f"{'.'.join(parent_names)}.{function_name}"

                function_markers: List[RelationMarkerType] = []
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
                            # String contains of three parts:
                            # (string_start string_content string_end)
                            string_content = block_comment.children[1]
                            assert string_content.text is not None

                            block_comment_text = string_content.text.decode(
                                "utf-8"
                            )
                            source_node = MarkerParser.parse(
                                block_comment_text,
                                node_.start_point[0] + 1,
                                node_.end_point[0] + 1,
                                string_content.start_point[0] + 1,
                                function_name,
                            )
                            for marker_ in source_node.markers:
                                if isinstance(marker_, FunctionRangeMarker):
                                    function_range_marker_processor(
                                        marker_, parse_context
                                    )
                                    traceability_info.markers.append(marker_)
                                    function_markers.append(marker_)

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
                    parent=traceability_info,
                    name=function_name,
                    display_name=function_name,
                    line_begin=node_.range.start_point[0] + 1,
                    line_end=node_.range.end_point[0] + 1,
                    child_functions=[],
                    # Python functions do not need to track markers.
                    markers=[],
                    attributes=set(),
                )
                map_function_to_node[new_function] = node_

                parent_function = functions_stack[-1]

                parent_function.child_functions.append(new_function)
                functions_stack.append(new_function)
                traceability_info.functions.append(new_function)

                traceability_info.ng_map_names_to_markers[function_name] = (
                    function_markers
                )
            elif node_.type == "comment":
                assert node_.text is not None, (
                    f"Comment without a text: {node_}"
                )

                node_text_string = node_.text.decode("utf8")

                source_node = MarkerParser.parse(
                    node_text_string,
                    node_.start_point[0] + 1,
                    node_.end_point[0] + 1,
                    node_.start_point[0] + 1,
                    None,
                )
                for marker_ in source_node.markers:
                    if isinstance(marker_, RangeMarker) and (
                        range_marker := marker_
                    ):
                        range_marker_processor(range_marker, parse_context)
                    elif isinstance(marker_, LineMarker) and (
                        line_marker := marker_
                    ):
                        line_marker_processor(line_marker, parse_context)
                    else:
                        pass
            else:
                pass

        assert (
            functions_stack[0].name == "module"
            or functions_stack[0].name == "translation_unit"
        )

        source_file_traceability_info_processor(
            traceability_info, parse_context
        )

        return traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        try:
            with open(file_path, "rb") as file:
                sdoc_content = file.read()
                sdoc = self.read(sdoc_content, file_path=file_path)
                return sdoc
        except UnicodeDecodeError:
            raise
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

    @staticmethod
    def get_node_ns(node: Node) -> Sequence[str]:
        """
        Walk up from node to find enclosing class and function names.

        Handles nested functions, methods, and classes.
        """
        parent_scopes: List[str] = []
        cursor: Optional[Node] = node

        while cursor is not None:
            if cursor.type in ("class_definition", "function_definition"):
                # Look for the identifier child (i.e., the name).
                name_node = next(
                    (
                        child
                        for child in cursor.children
                        if child.type == "identifier"
                    ),
                    None,
                )
                if name_node and name_node.text:
                    parent_scopes.insert(0, name_node.text.decode("utf-8"))
            cursor = cursor.parent

        # The array now contains the "fully qualified" node name,
        # we want to return the namespace, so don't return the last part.
        return parent_scopes[:-1]
