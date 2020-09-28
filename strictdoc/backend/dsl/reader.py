from textx import metamodel_from_str, get_children_of_type

from strictdoc.backend.dsl.grammar import STRICTDOC_GRAMMAR
from strictdoc.backend.dsl.models import Document, Requirement, ReqComment, Section, Body, Reference, FreeText

DOCUMENT_MODELS = [
    Document,
    ReqComment,
    Section,
    Requirement,
    Body,
    Reference,
    FreeText
]


def section_obj_processor(section):
    section.parent.ng_sections.append(section)


class SDReader:
    def __init__(self):
        self.meta_model = metamodel_from_str(STRICTDOC_GRAMMAR,
                                             classes=DOCUMENT_MODELS,
                                             use_regexp_group=True)
        obj_processors = {
            'Section': section_obj_processor
        }

        self.meta_model.register_obj_processors(obj_processors)

    def read(self, input):
        document = self.meta_model.model_from_str(input)
        return document

    def read_from_file(self, file_path):
        with open(file_path, 'r') as file:
            sdoc_content = file.read()

        try:
            sdoc = self.read(sdoc_content)
            sdoc.assign_path(file_path)
            return sdoc
        except Exception as exc:
            print("error: could not parse file: {}.\nException: {}".format(file_path, exc))
            exit(1)
