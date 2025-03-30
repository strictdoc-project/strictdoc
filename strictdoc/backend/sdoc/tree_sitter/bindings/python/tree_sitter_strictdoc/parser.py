import tree_sitter

from strictdoc.backend.sdoc.tree_sitter.bindings.python import \
    tree_sitter_strictdoc
from strictdoc.backend.sdoc.tree_sitter.bindings.python.tree_sitter_strictdoc.helpers import \
    traverse_tree_with_validation


class StrictDocParser:
    @staticmethod
    def parse(input_content: bytes) -> tree_sitter.Tree:
        language = tree_sitter.Language(tree_sitter_strictdoc.language())

        parser = tree_sitter.Parser(language)

        tree: tree_sitter.Tree = parser.parse(input_content + b"%%%")

        list(traverse_tree_with_validation(tree))

        return tree
