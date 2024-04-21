# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from textx import metamodel_from_str

from strictdoc.core.query_engine.grammar import QUERY_GRAMMAR
from strictdoc.core.query_engine.query_object import (
    AndExpression,
    EqualExpression,
    InExpression,
    NodeContainsAnyFreeTextExpression,
    NodeContainsExpression,
    NodeFieldExpression,
    NodeHasChildRequirementsExpression,
    NodeHasParentRequirementsExpression,
    NodeIsRequirementExpression,
    NodeIsRootExpression,
    NodeIsSectionExpression,
    NoneExpression,
    NotEqualExpression,
    NotExpression,
    NotInExpression,
    OrExpression,
    Query,
    StringExpression,
)

QUERY_MODELS = [
    AndExpression,
    EqualExpression,
    InExpression,
    NodeContainsExpression,
    NodeContainsAnyFreeTextExpression,
    NodeFieldExpression,
    NodeHasChildRequirementsExpression,
    NodeHasParentRequirementsExpression,
    NodeIsRequirementExpression,
    NodeIsRootExpression,
    NodeIsSectionExpression,
    NoneExpression,
    NotEqualExpression,
    NotExpression,
    NotInExpression,
    OrExpression,
    Query,
    StringExpression,
]


class QueryParseContext:
    pass


class QueryParsingProcessor:
    def __init__(self, parse_context: QueryParseContext):
        self.parse_context: QueryParseContext = parse_context

    def get_default_processors(self):
        return {}

    def process_document(self, query: Query):
        pass


class QueryReader:
    def __init__(self, path_to_output_root: str = "NOT_RELEVANT"):
        self.path_to_output_root = path_to_output_root

    @staticmethod
    def _read(input_string, file_path=None):
        meta_model = metamodel_from_str(
            QUERY_GRAMMAR,
            classes=QUERY_MODELS,
            use_regexp_group=True,
        )

        parse_context = QueryParseContext()
        processor = QueryParsingProcessor(parse_context=parse_context)
        meta_model.register_obj_processors(processor.get_default_processors())

        query: Query = meta_model.model_from_str(
            input_string, file_name=file_path
        )

        return query, parse_context

    @staticmethod
    def read(input_string, file_path=None):
        document, _ = QueryReader._read(input_string, file_path)
        return document
