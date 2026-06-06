"""
@relation(SDOC-SRS-142, scope=file)
"""

from enum import IntEnum
from functools import lru_cache
from pathlib import Path, PurePath
from typing import Optional, cast

import toml
import tree_sitter_rust as ts_rust
from tree_sitter import Language, Node, Parser, Query, QueryCursor

from strictdoc.backend.sdoc_source_code.constants import FunctionAttribute
from strictdoc.backend.sdoc_source_code.marker_parser import MarkerParser
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
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_stats import SourceFileStats
from strictdoc.helpers.file_system import (
    file_open_read_bytes,
    file_open_read_utf8,
)

# @relation(SDOC-LLR-177, SDOC-LLR-171, SDOC-LLR-173, scope=line)
TS_QUERY = """
; Query 0: Outer doc attribute, line doc, or block doc in allowed positions
(
  [
    (attribute_item
      (attribute
        (identifier) @_attribute_id (#eq? @_attribute_id "doc")
          value: (string_literal (string_content) @doc.comment)))+
    (line_comment
      outer: (outer_doc_comment_marker)
      doc: (doc_comment) @doc.comment)+
    (block_comment
      outer: (outer_doc_comment_marker)
      doc: (doc_comment) @doc.comment)
  ]
  .
  (attribute_item)*
  .
  [
    ; any identifiable item, most notably functions
    (_ name: [(identifier)(field_identifier)(type_identifier)(lifetime)] @doc.item_identifier)

    ; impl MyStruct
    (impl_item type: (type_identifier) @doc.item_identifier)

    ; extern "C"
    (foreign_mod_item (extern_modifier) @doc.item_identifier)

    ; match arm
    (match_arm (match_pattern) @doc.item_identifier)

    ; assignment inside struct initializer
    (field_initializer field: (field_identifier) @doc.item_identifier)

    ; Statement like 1;
    (expression_statement) @doc.item_identifier

    ; Expression like x + y
    (binary_expression) @doc.item_identifier

    ; Expression like (x + y)
    (parenthesized_expression) @doc.item_identifier

    ; Named "type" field of any enclosing node (usually body), e.g. type within tuple struct.
    type: (_)
  ] @doc.item
)

; Query 1: Inner doc attribute, line doc or block doc in allowed positions.
; Note: We have to repeat the identical inner pattern, alternations don't help here.
;       See https://github.com/tree-sitter/tree-sitter/issues/3480.
[
  (function_item
    name: (identifier) @doc.item_identifier
    body: (block
      [
        (inner_attribute_item
          (attribute
            (identifier) @_attribute_id (#eq? @_attribute_id "doc")
            value: (string_literal (string_content) @doc.comment)))+
        (line_comment
          inner: (inner_doc_comment_marker)
          doc: (doc_comment) @doc.comment)+
        (block_comment
          inner: (inner_doc_comment_marker)
          doc: (doc_comment) @doc.comment)
      ]
    )
  )
  (mod_item
    name: (identifier) @doc.item_identifier
    body: (declaration_list
      [
        (inner_attribute_item
          (attribute
            (identifier) @_attribute_id (#eq? @_attribute_id "doc")
            value: (string_literal (string_content) @doc.comment)))+
        (line_comment
          inner: (inner_doc_comment_marker)
          doc: (doc_comment) @doc.comment)+
        (block_comment
          inner: (inner_doc_comment_marker)
          doc: (doc_comment) @doc.comment)
      ]
    )
  )
  (impl_item
    type: (type_identifier) @doc.item_identifier
    body: (declaration_list
      [
        (inner_attribute_item
          (attribute
            (identifier) @_attribute_id (#eq? @_attribute_id "doc")
            value: (string_literal (string_content) @doc.comment)))+
        (line_comment
          inner: (inner_doc_comment_marker)
          doc: (doc_comment) @doc.comment)+
        (block_comment
          inner: (inner_doc_comment_marker)
          doc: (doc_comment) @doc.comment)
      ]
    )
  )
  (foreign_mod_item (extern_modifier) @doc.item_identifier
    body: (declaration_list
      [
        (inner_attribute_item
          (attribute
            (identifier) @_attribute_id (#eq? @_attribute_id "doc")
            value: (string_literal (string_content) @doc.comment)))+
        (line_comment
          inner: (inner_doc_comment_marker)
          doc: (doc_comment) @doc.comment)+
        (block_comment
          inner: (inner_doc_comment_marker)
          doc: (doc_comment) @doc.comment)
      ]
    )
  )
] @doc.item

; Query 2: Inner line or block doc comment of file-level module.
(source_file
  [
    (line_comment
      inner: (inner_doc_comment_marker)
        doc: (doc_comment) @doc.comment)+
    (block_comment
      inner: (inner_doc_comment_marker)
        doc: (doc_comment) @doc.comment)
  ]
) @doc.item

; Query 3: normal line or block comment
[(line_comment !doc)+
 (block_comment !doc)] @normal_comment

; Query 4: Identifiable items. Those where it's clear how to link by forward relations.
[
  (const_item name: (identifier) @doc.item_identifier) @doc.item
  (enum_item name: (type_identifier) @doc.item_identifier) @doc.item
  (function_item name: (identifier) @doc.item_identifier) @doc.item
  (mod_item name: (identifier) @doc.item_identifier) @doc.item
  (static_item name: (identifier) @doc.item_identifier) @doc.item
  (struct_item name: (type_identifier) @doc.item_identifier) @doc.item
  (trait_item name: (type_identifier) @doc.item_identifier) @doc.item
  (type_item name: (type_identifier) @doc.item_identifier) @doc.item
  (union_item name: (type_identifier) @doc.item_identifier) @doc.item
]
"""


class RustTsQuery(IntEnum):
    """Give the queries from TS_QUERY a friendly name."""

    OUTER_DOC_COMMENT = 0
    INNER_DOC_COMMENT = 1
    INNER_DOC_COMMENT_FILEMODULE = 2
    NORMAL_COMMENT = 3
    IDENTIFIABLE_ITEM = 4


@lru_cache(maxsize=None)
def rust_crate_root_and_name(directory: str) -> Optional[tuple[str, str]]:
    """
    ``(crate_root, package_name)`` of the nearest ``Cargo.toml`` with a
    ``[package]`` at or above ``directory``, or ``None`` if there is none.
    ``lru_cache`` memoizes the result per directory, so the many files of one
    crate cost a single manifest read.
    """
    for current in (Path(directory), *Path(directory).parents):
        manifest = current / "Cargo.toml"
        if not manifest.is_file():
            continue
        try:
            with file_open_read_utf8(str(manifest)) as manifest_file:
                package = toml.loads(manifest_file.read()).get("package")
        except (OSError, toml.TomlDecodeError):
            continue
        if isinstance(package, dict):
            name = package.get("name")
            if isinstance(name, str):
                return str(current), name
    return None


def rust_module_segments_within_crate(rel_parts: tuple[str, ...]) -> list[str]:
    """
    Module path of a source file *within its crate*, from the file's path
    relative to the crate root split into ``rel_parts``. Applies Rust's
    file<->module convention (the reader sees one file, so it cannot follow
    ``mod`` declarations)::

        src/lib.rs | src/main.rs   -> []                 (the crate root)
        src/model.rs               -> ["model"]
        src/model/mod.rs           -> ["model"]
        src/a/b/c.rs               -> ["a", "b", "c"]
        tests/it.rs                -> ["it"]             (integration target)
        tests/it/helper.rs         -> ["it", "helper"]

    The module path is taken from the file's location, so ``#[path = "..."]``
    overrides and non-default ``[lib]`` / ``[[bin]]`` target paths are not
    supported.
    """

    def module_name(file: str) -> str:
        return file[:-3] if file.endswith(".rs") else file

    if not rel_parts:
        return []
    target_dir, inner = rel_parts[0], list(rel_parts[1:])
    if not inner:
        stem = module_name(target_dir)
        return [] if stem in ("lib", "main") else [stem]
    *dirs, leaf = inner
    stem = module_name(leaf)
    if target_dir == "src" and not dirs and stem in ("lib", "main"):
        return []
    if stem in ("mod", "main"):
        return dirs
    return [*dirs, stem]


def rust_canonical_crate_segments(full_path: Optional[str]) -> list[str]:
    """
    Canonical-path prefix shared by every item in a Rust file: the crate name
    (the ``[package]`` of the nearest ``Cargo.toml``, or the file stem when
    there is none) followed by the file's module path within the crate.
    """
    if not full_path:
        return []
    path = PurePath(full_path)
    crate = rust_crate_root_and_name(str(path.parent))
    if crate is None:
        return [path.stem]
    crate_root, crate_name = crate
    try:
        rel_parts = path.relative_to(crate_root).parts
    except ValueError:
        return [path.stem]
    return [crate_name, *rust_module_segments_within_crate(rel_parts)]


def comments_text_from_comment_nodes(comments: list[Node]) -> str:
    """
    Join multiple comment nodes into one multi-line string.
    @relation(SDOC-LLR-175, scope=function)
    """
    comment_text = assert_cast(comments[0].text, bytes).decode("utf-8")
    last_row = comments[0].start_point.row
    for comment_part in comments[1:]:
        new_lines = comment_part.start_point.row - last_row
        last_row = comment_part.start_point.row
        comment_text += "\n" * new_lines + assert_cast(
            comment_part.text, bytes
        ).decode("utf-8")
    return comment_text


def item_definition_line_begin(item: Node) -> int:
    """
    First 1-based line of ``item``'s definition, including the leading outer
    attributes (``#[test]``, ``#[cfg(...)]``) and doc/line comments above it,
    which tree-sitter models as siblings rather than part of the item node.
    """
    line_begin_0_based = item.start_point[0]
    sibling = item.prev_sibling
    while sibling is not None and sibling.type in (
        "attribute_item",
        "line_comment",
        "block_comment",
    ):
        # A line comment node extends to the start of the following line, so its
        # last line of content is its start row; attributes and block comments
        # end where their end point is.
        sibling_content_end = (
            sibling.start_point[0]
            if sibling.type == "line_comment"
            else sibling.end_point[0]
        )
        # Stop once a blank line separates the sibling from the header: such a
        # comment documents something else, not this definition.
        if sibling_content_end != line_begin_0_based - 1:
            break
        line_begin_0_based = sibling.start_point[0]
        sibling = sibling.prev_sibling
    return line_begin_0_based + 1


def special_description(item: Node, identifier_text: str) -> Optional[str]:
    """
    Make a description for language constructs that are not functions.

    The default Function description assumes the object actually represents a function.
    However, the Rust reader reuses Function to represent many different Rust specific object types.
    We have to give them a suitable Rust specific description.
    """
    if item.type == "associated_type":
        return f"associated type {identifier_text}"
    elif item.type in ("binary_expression", "parenthesized_expression"):
        return f"expression {identifier_text}"
    elif item.type == "const_item":
        return f"const {identifier_text}"
    elif item.type == "const_parameter":
        return f"const parameter {identifier_text}"
    elif item.type == "function_item":
        return f"fn {identifier_text}()"
    elif item.type == "enum_item":
        return f"enum {identifier_text}"
    elif item.type == "enum_variant":
        return f"enum variant {identifier_text}"
    elif item.type == "expression_statement":
        return f"statement {identifier_text}"
    elif item.type == "extern_crate_declaration":
        return f"crate {identifier_text}"
    elif item.type == "field_declaration":
        return f"field {identifier_text}"
    elif item.type == "field_initializer":
        return f"field initializer {identifier_text}"
    elif item.type == "foreign_mod_item":
        return f"foreign module {identifier_text}"
    elif item.type == "impl_item":
        return f"impl {identifier_text}"
    elif item.type == "match_arm":
        return f"match arm {identifier_text}"
    elif item.type == "macro_definition":
        return f"macro {identifier_text}"
    elif item.type == "mod_item":
        return f"module {identifier_text}"
    elif item.type == "lifetime_parameter":
        return f"lifetime {identifier_text}"
    elif item.type == "static_item":
        return f"static {identifier_text}"
    elif item.type == "struct_item":
        return f"struct {identifier_text}"
    elif item.type == "trait_item":
        return f"trait {identifier_text}"
    elif item.type == "type_item":
        return f"type {identifier_text}"
    elif item.type == "type_parameter":
        return f"type parameter {identifier_text}"
    elif item.type == "union_item":
        return f"union {identifier_text}"
    elif item.type in ("primitive_type", "type_identifier"):
        return f"type {identifier_text}"
    return None


class SourceFileTraceabilityReader_Rust:
    @staticmethod
    def supported_elements() -> list[str]:
        return []

    def __init__(self, custom_tags: Optional[set[str]] = None) -> None:
        self.custom_tags: Optional[set[str]] = custom_tags

    def read(
        self,
        input_buffer: bytes,
        file_path: Optional[str] = None,
    ) -> SourceFileTraceabilityInfo:
        file_stats = SourceFileStats.create(input_buffer)
        parse_context = ParseContext(file_path, file_stats)
        traceability_info = SourceFileTraceabilityInfo([])
        parser = ParserRun(
            input_buffer, parse_context, traceability_info, self.custom_tags
        )
        parser()
        source_file_traceability_info_processor(
            traceability_info, parse_context
        )
        return traceability_info

    def read_from_file(self, file_path: str) -> SourceFileTraceabilityInfo:
        """
        Generate the source file traceability info for one particular Rust file.

        The created SourceFileTraceabilityInfo is filled partially local information:
        - functions: Markers are associated, but only those resulting from local markers.
        - markers: Markers that stem from markup in this file.
        - ng_map_reqs_to_markers: Mapping of requirement IDs to Marker objects for markers directly defined in the source file.
        """
        with file_open_read_bytes(file_path) as file:
            sdoc_content = file.read()
            sdoc = self.read(sdoc_content, file_path=file_path)
            return sdoc


class ParserRun:
    def __init__(
        self,
        input_buffer: bytes,
        parse_context: ParseContext,
        traceability_info: SourceFileTraceabilityInfo,
        custom_tags: Optional[set[str]],
    ):
        rust_language = Language(ts_rust.language())
        self.parser = Parser(rust_language)  # type: ignore[call-arg, unused-ignore]
        self.TS_QUERY = Query(rust_language, TS_QUERY)
        self.input_buffer: bytes = input_buffer
        self.parse_context = parse_context
        self.traceability_info = traceability_info
        self.custom_tags: Optional[set[str]] = custom_tags

    def __call__(self) -> None:
        tree = self.parser.parse(self.input_buffer)
        cursor = QueryCursor(self.TS_QUERY)
        matches = cursor.matches(tree.root_node)

        seen_nodes = set()
        deferred_matches = []
        for query_index, captures in matches:
            if query_index == RustTsQuery.IDENTIFIABLE_ITEM:
                # The query for identifiable items overlaps with comment based queries. Move results for identifiable
                # items last, so that a result can be skipped if a LanguageItem was already created.
                deferred_matches.append(captures)
            elif query_index in (
                RustTsQuery.OUTER_DOC_COMMENT,
                RustTsQuery.INNER_DOC_COMMENT,
                RustTsQuery.INNER_DOC_COMMENT_FILEMODULE,
            ):
                assert len(captures["doc.item"]) == 1
                item = captures["doc.item"][0]
                doc_comment = captures["doc.comment"]
                if (
                    item.type == "source_file"
                    and "doc.item_identifier" not in captures
                ):
                    self._process_anonymous_module_comment(
                        doc_comment,
                        item,
                    )
                else:
                    if "doc.item_identifier" in captures:
                        # doc comment on named item
                        assert len(captures["doc.item_identifier"]) == 1
                        identifier = assert_cast(
                            captures["doc.item_identifier"][0].text, bytes
                        ).decode()
                    else:
                        # doc comment on anonymous item
                        identifier = assert_cast(item.text, bytes).decode()
                    self._process_doc_comment(
                        doc_comment,
                        item,
                        identifier,
                    )
                seen_nodes.add(item.id)
            elif query_index == RustTsQuery.NORMAL_COMMENT:
                self._process_normal_comment(captures["normal_comment"])

        for captures in deferred_matches:
            assert len(captures["doc.item"]) == 1
            assert len(captures["doc.item_identifier"]) == 1
            item = captures["doc.item"][0]
            if item.id not in seen_nodes:
                identifier = assert_cast(
                    captures["doc.item_identifier"][0].text, bytes
                ).decode()
                self._process_item_for_forward_relation(item, identifier)

    def _process_anonymous_module_comment(
        self, comments: list[Node], module: Node
    ) -> None:
        """
        Create marker, item and source nodes for file-level module from tree-sitter doc comment nodes.
        @relation(SDOC-LLR-164, SDOC-LLR-172, scope=function)
        """
        comment_text = comments_text_from_comment_nodes(comments)
        source_node = MarkerParser.parse(
            input_string=comment_text,
            line_start=1,
            line_end=self.parse_context.file_stats.lines_total,
            comment_line_start=module.start_point.row + 1,
            comment_byte_range=ByteRange.create_from_ts_nodes(
                comments[0], comments[-1]
            ),
            custom_tags=self.custom_tags,
            default_scope="file",
        )
        for marker_ in source_node.markers:
            if not isinstance(marker_, LanguageItemMarker):
                continue
            # At the top level, only accept the scope=file markers.
            # Everything else will be handled by functions and classes.
            if marker_.scope != RangeMarkerType.FILE:
                print(  # noqa: T201
                    "warning: comment to top-level module is not scope=file, ignoring"
                )
                continue
            language_item_marker_processor(marker_, self.parse_context)
            self.traceability_info.markers.append(marker_)

    def _process_doc_comment(
        self,
        comments: list[Node],
        item: Node,
        identifier_text: str,
    ) -> None:
        """
        Create markers, items and source nodes from tree-sitter doc comment nodes.
        @relation(SDOC-LLR-164, SDOC-LLR-172, scope=function)
        """
        assert len(comments) >= 1
        comment_text = comments_text_from_comment_nodes(comments)
        line_start_0_based = min(
            item.start_point[0], comments[0].start_point[0]
        )
        line_end_0_based = max(item.end_point[0], comments[-1].end_point[0])
        source_node = MarkerParser.parse(
            input_string=comment_text,
            line_start=line_start_0_based + 1,
            line_end=line_end_0_based + 1
            if self.input_buffer[-1] == 10
            else line_end_0_based,
            comment_line_start=comments[0].start_point[0] + 1,
            comment_byte_range=ByteRange.create_from_ts_nodes(
                comments[0], comments[-1]
            ),
            custom_tags=self.custom_tags,
            entity_name=identifier_text,
            default_scope="function",
        )

        function_markers: list[LanguageItemMarker] = []
        for marker_ in source_node.markers:
            if isinstance(marker_, LanguageItemMarker) and (
                language_item_marker_ := marker_
            ):
                if (
                    description := special_description(item, identifier_text)
                ) is not None:
                    language_item_marker_.set_description(description)

                # adds marker to context, and connects context requirements with marker
                language_item_marker_processor(
                    language_item_marker_, self.parse_context
                )
                self.traceability_info.markers.append(language_item_marker_)
                function_markers.append(marker_)

        name = self.canonical_path(item.parent, identifier_text)
        new_function_for_rust_item = LanguageItem(
            parent=self.traceability_info,
            name=name,
            display_name=name,
            line_begin=item_definition_line_begin(item),
            line_end=item.end_point[0] + 1,
            code_byte_range=ByteRange.create_from_ts_node(item),
            child_functions=[],
            markers=function_markers,
            attributes={FunctionAttribute.DEFINITION},
        )
        if len(source_node.fields) > 0:
            source_node.function = new_function_for_rust_item
        self.traceability_info.source_nodes.append(source_node)
        self.traceability_info.functions.append(new_function_for_rust_item)
        # list is invariant, so list[LanguageItemMarker] is not a
        # list[RelationMarkerType] even though every element is one. The widen
        # is sound; cast it for the map, which holds the wider type.
        self.traceability_info.ng_map_names_to_markers[identifier_text] = cast(
            list[RelationMarkerType], function_markers
        )

    def _process_normal_comment(self, comments: list[Node]) -> None:
        """
        Create markers and items from tree-sitter normal comment nodes.
        @relation(SDOC-LLR-171, scope=function)
        """
        comment_text = comments_text_from_comment_nodes(comments)
        line_start_0_based = comments[0].start_point.row
        line_end_0_based = comments[-1].end_point.row
        source_node = MarkerParser.parse(
            input_string=comment_text,
            line_start=line_start_0_based + 1,
            line_end=line_end_0_based + 1,
            comment_line_start=line_start_0_based + 1,
            comment_byte_range=ByteRange.create_from_ts_nodes(
                comments[0], comments[-1]
            ),
        )
        for marker_ in source_node.markers:
            if (
                isinstance(marker_, LanguageItemMarker)
                and (marker_.scope is RangeMarkerType.FILE)
                and (language_item_marker := marker_)
            ):
                language_item_marker.ng_range_line_begin = 1
                language_item_marker.ng_range_line_end = (
                    self.parse_context.file_stats.lines_total
                )
                language_item_marker_processor(
                    language_item_marker, self.parse_context
                )
            elif isinstance(marker_, RangeMarker) and (range_marker := marker_):
                range_marker_processor(range_marker, self.parse_context)
            elif isinstance(marker_, LineMarker) and (line_marker := marker_):
                line_marker_processor(line_marker, self.parse_context)
            else:
                print(  # noqa: T201
                    "warning: Ignoring @relation. Only scope=file|line|range_start is supported in regular "
                    "Rust comments. Use doc comments otherwise."
                )

    def _process_item_for_forward_relation(
        self, item: Node, identifier: str
    ) -> None:
        """
        Create item objects from tree-sitter doc comment nodes to support forward relations.

        Corresponding markers will be created and resolved later by FileTraceabilityIndex,
        see validate_and_resolve.

        @relation(SDOC-LLR-173, scope=function)
        """
        name = self.canonical_path(item.parent, identifier)
        function = LanguageItem(
            parent=self.traceability_info,
            name=name,
            display_name=name,
            line_begin=item_definition_line_begin(item),
            line_end=max(item.end_point[0] + 1, item.start_point[0] + 2),
            code_byte_range=ByteRange.create_from_ts_node(item),
            child_functions=[],
            markers=[],
            attributes={FunctionAttribute.DEFINITION},
        )
        self.traceability_info.functions.append(function)

    def canonical_path(
        self, parent_scope: Optional[Node], item_path_segment: str
    ) -> str:
        """
        Construct a canonical path in best-effort.
        @relation(SDOC-LLR-174, scope=function)
        """
        cursor: Optional[Node] = parent_scope

        if (
            cursor is not None
            and cursor.type == "declaration_list"
            and cursor.parent is not None
            and cursor.parent.type == "impl_item"
        ):
            cursor = cursor.parent
            item_being_implemented = cursor.child_by_field_name("type")
            assert item_being_implemented is not None
            canonical_path_item_being_implemented = self.canonical_path(
                cursor,
                assert_cast(item_being_implemented.text, bytes).decode("utf-8"),
            )
            impl_trait_node = cursor.child_by_field_name("trait")
            if impl_trait_node is not None:
                # rust-lang.org: For trait implementations, [the path prefix] is the canonical path of the item being
                # implemented followed by as followed by the canonical path to the trait all surrounded in angle (<>)
                # brackets.
                trait = self.canonical_path(
                    None,
                    assert_cast(impl_trait_node.text, bytes).decode("utf-8"),
                )
                path_prefix = (
                    f"<{canonical_path_item_being_implemented} as {trait}>"
                )
            else:
                # rust-lang.org: For bare implementations, [the path prefix] is the canonical path of the item being
                # implemented surrounded by angle (<>) brackets.
                path_prefix = f"<{canonical_path_item_being_implemented}>"
        else:
            path_prefix_segments = []
            while cursor is not None:
                name_node = cursor.child_by_field_name("name")
                if name_node is not None:
                    name = assert_cast(name_node.text, bytes).decode("utf-8")
                    path_prefix_segments.append(name)
                cursor = cursor.parent
            path_prefix_segments.extend(
                reversed(
                    rust_canonical_crate_segments(self.parse_context.filename)
                )
            )
            path_prefix = "::".join(reversed(path_prefix_segments))

        # rust-lang.org: The canonical path is defined as a path prefix appended by the path segment the item itself
        # defines.
        return f"{path_prefix}::{item_path_segment}"
