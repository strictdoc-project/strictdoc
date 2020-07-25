from textx import metamodel_from_str, get_children_of_type

from strictdoc.backend.dsl.grammar import STRICTDOC_GRAMMAR
from strictdoc.backend.dsl.models import Document, Requirement, ReqComment, Section

DOCUMENT_MODELS = [Document, ReqComment, Section, Requirement]


class SDReader:
    def __init__(self):
        self.meta_model = metamodel_from_str(STRICTDOC_GRAMMAR,
                                             classes=DOCUMENT_MODELS)

    def read(self, input):
        document = self.meta_model.model_from_str(input)
        return document
