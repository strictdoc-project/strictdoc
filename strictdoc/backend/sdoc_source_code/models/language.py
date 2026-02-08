"""
@relation(SDOC-SRS-142, scope=file)
"""

from typing import Any, List, Optional, Set

from strictdoc.backend.sdoc_source_code.constants import FunctionAttribute
from strictdoc.backend.sdoc_source_code.models.language_item_marker import (
    LanguageItemMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_location import ByteRange
from strictdoc.helpers.auto_described import auto_described


@auto_described
class LanguageItem:
    def __init__(
        self,
        *,
        parent: Any,
        name: str,
        display_name: str,
        line_begin: int,
        line_end: int,
        code_byte_range: Optional[ByteRange],
        child_functions: List[Any],
        markers: List[LanguageItemMarker],
        attributes: Set[FunctionAttribute],
    ):
        """
        Create a LanguageItem object.

        A LanguageItem records essential data like name and location of
        programming language items from language-aware parsing. It's up to a
        StrictDoc language parser what items they want to support.

        For languages that scatter parts of a function over different places
        (e.g. declaration and definition in C), the caller is responsible to
        create a separate LanguageItem object for each part, where the parts
        match on name. Since it's more common to stick documentation to the
        declaration part, StrictDoc will automatically find and link
        corresponding definition parts. Not vice versa: If definition parts are
        documented, only the definition will be linked.

        parent should be set to the SourceFileTraceabilityInfo that corresponds
        to the file where the function is defined. Purpose is to provide meta
        information like file name and path while the FileTraceabilityIndex is
        not yet fully resolved.

        name is an identifier that should be globally unique for a set of
        declarations/definitions. Its purpose is to tie declarations and
        definitions. It's up to StrictDoc language parsers to define a naming
        convention for their language. The convention should follow language
        specific notation for qualified names. E.g. in C++, a member bar in
        class Foo will be named "Foo:bar(const CanFrame &frame)". It may be
        hard to reimplement the full module and naming system of each language,
        so naming is best-effort.

        display_name is an identifier used to resolve forward relations from
        users to function objects created by language parsers. The display_name
        must thus be predictable for users and as unique as possible. It's up
        to StrictDoc language parsers to define a naming convention for their
        language. The convention should follow language specific notation for
        qualified identifiers. E.g. in C++, a member bar in class Foo will be
        named "Foo:bar".

        line start/end (1-based) mark first and last line of the definition
        block, *without* leading comment lines, if any. Used to jump to and
        highlight the function in source file view in case of forward
        relations.

        child_functions could store LanguageItem objects that represent nested
        functions. It's currently unused and may be removed.

        markers are only needed if the LanguageItem is a declaration function
        (C, C++) that shall be automatically linked to the corresponding
        definition function, or if it is a test framework function that shall
        be automatically linked with requirements and test results. Otherwise,
        it can be empty.

        attributes: For example static, declaration, definition. Enables some
        special handling, e.g. automatic linking of definitions if the
        LanguageItem is a declaration.
        """

        assert parent is not None
        self.parent = parent

        # Full qualified name.
        self.name = name

        self.display_name = display_name

        # Child functions are supported in programming languages that can nest
        # functions, for example, Python.
        self.child_functions: List[LanguageItem] = child_functions
        self.markers: List[LanguageItemMarker] = markers
        self.line_begin = line_begin
        self.line_end = line_end

        # Not all source code functions have ranges.
        # Example: Robot framework files.
        self.code_byte_range: Optional[ByteRange] = code_byte_range

        self.attributes: Set[FunctionAttribute] = attributes

    def is_declaration(self) -> bool:
        return FunctionAttribute.DECLARATION in self.attributes

    def is_definition(self) -> bool:
        return FunctionAttribute.DEFINITION in self.attributes

    def is_public(self) -> bool:
        return FunctionAttribute.STATIC not in self.attributes
