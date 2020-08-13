from textx import metamodel_from_str, get_children_of_type

from strictdoc.backend.dsl.grammar import STRICTDOC_GRAMMAR
from strictdoc.backend.dsl.models import Document, Requirement, ReqComment, Section, Body, Reference

DOCUMENT_MODELS = [Document, ReqComment, Section, Requirement, Body, Reference]


class SDReader:
    def __init__(self):
        self.meta_model = metamodel_from_str(STRICTDOC_GRAMMAR,
                                             classes=DOCUMENT_MODELS,
                                             use_regexp_group=True)

    def read(self, input):
        document = self.meta_model.model_from_str(input)
        return document

    def read_from_file(self, file_path):
        with open(file_path, 'r') as file:
            sdoc_content = file.read()
        sdoc = self.read(sdoc_content)
        sdoc.assign_path(file_path)
        return sdoc
