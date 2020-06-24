import re

from collections import OrderedDict

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from strictdoc.backend.rst.rst_field_parser import RSTFieldParser
from strictdoc.backend.rst.rst_parser_shared_state import RSTParserSharedState


class DocumentMetadata:
    def __init__(self):
        self.fields = []

    def has_field(self, field, type):
        for registered_field in self.fields:
            if registered_field['name'] == field and registered_field['type'] == type:
                return True
        else:
            return False

    def __str__(self):
        return 'DocumentMetadata (fields: {})'.format(self.fields)


class DocumentMetadataNode(nodes.General, nodes.Element):
    metadata = None

    def __init__(self, metadata):
        assert metadata
        super(DocumentMetadataNode, self).__init__()
        self.metadata = metadata

    def get_metadata(self):
        return self.metadata


class DocumentMetadataDirective(Directive):
    has_content = True

    option_spec = {
        "fields": directives.unchanged_required
    }

    def __init__(self, *args):
        super(DocumentMetadataDirective, self).__init__(*args)
        self.field_parser = RSTFieldParser()

    def run(self):
        meta_information = OrderedDict()

        if not self.options:
            raise RuntimeError("problem with options")

        assert 'fields' in self.options.keys()
        fields_raw = self.options.get("fields", '')
        document_metadata = DocumentMetadata()
        fields = self.field_parser.parse_dict_array(fields_raw)
        document_metadata.fields.extend(fields)

        container = DocumentMetadataNode(document_metadata)

        # HACK HACK HACK
        for field in document_metadata.fields:
            RSTParserSharedState.categories_spec[field['name']] = directives.unchanged_required

        return [container]
