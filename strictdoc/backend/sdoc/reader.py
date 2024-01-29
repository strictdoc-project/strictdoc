import hashlib
import os.path
import sys
import tempfile
import traceback
from pathlib import Path

from textx import metamodel_from_str

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.include_reader import SDIncludeReader
from strictdoc.backend.sdoc.models.constants import DOCUMENT_MODELS
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.fragment import Fragment
from strictdoc.backend.sdoc.processor import ParseContext, SDocParsingProcessor
from strictdoc.backend.sdoc.validations.sdoc_validator import SDocValidator
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.md5 import get_file_md5
from strictdoc.helpers.pickle import pickle_dump, pickle_load
from strictdoc.helpers.textx import drop_textx_meta


class SDReader:
    def __init__(self, path_to_output_root: str = "NOT_RELEVANT"):
        self.path_to_output_root = path_to_output_root

    @staticmethod
    def _read(input_string, file_path=None):
        meta_model = metamodel_from_str(
            SDocGrammarBuilder.create_grammar(),
            classes=DOCUMENT_MODELS,
            use_regexp_group=True,
        )

        parse_context = ParseContext()
        processor = SDocParsingProcessor(
            parse_context=parse_context, delegate=SDReader.parse_include
        )
        meta_model.register_obj_processors(processor.get_default_processors())

        document: Document = meta_model.model_from_str(
            input_string, file_name=file_path
        )
        parse_context.document_reference.set_document(document)
        document.ng_uses_old_refs_field = parse_context.uses_old_refs_field
        document.ng_at_least_one_relations_field = (
            parse_context.at_least_one_relations_field
        )

        if document.ng_uses_old_refs_field:
            print(  # noqa: T201
                "warning: "
                f'the Document "{document.title}" has requirements with a '
                "REFS field. The REFS field is deprecated and must be renamed "
                "to RELATIONS. "
                "Additionally, the requirement's RELATIONS field shall be the "
                "last field after all other fields.\n"
                "Correct requirement example:\n"
                "[REQUIREMENT]\n"
                "UID: REQ-2\n"
                "STATEMENT: When Z, the system X shall do Y.\n"
                "RELATIONS:\n"
                "- TYPE: Parent\n"
                "  VALUE: REQ-1"
            )

        return document, parse_context

    @staticmethod
    def read(input_string, file_path=None):
        document, _ = SDReader._read(input_string, file_path)
        SDocValidator.validate_document(document)

        # HACK:
        # ProcessPoolExecutor doesn't work because of non-picklable parts
        # of textx. The offending fields are stripped down because they
        # are not used anyway.
        drop_textx_meta(document)

        return document

    def read_from_file(self, file_path: str) -> Document:
        """
        This function parses the provided .sdoc file and returns a Document
        object.
        """

        path_to_tmp_dir = tempfile.gettempdir()

        full_path_to_file = (
            file_path
            if os.path.abspath(file_path)
            else os.path.abspath(file_path)
        )

        file_md5 = get_file_md5(file_path)

        # File name contains an MD5 hash of its full path to ensure the
        # uniqueness of the cached items. Additionally, the unique file name
        # contains a full path to the output root to prevent collisions
        # between StrictDoc invocations running against the same set of SDoc
        # files in parallel.
        unique_identifier = self.path_to_output_root + full_path_to_file
        unique_identifier_md5 = hashlib.md5(
            unique_identifier.encode("utf-8")
        ).hexdigest()
        file_name = os.path.basename(full_path_to_file)
        file_name += "_" + unique_identifier_md5 + "_" + file_md5

        path_to_cached_file = os.path.join(
            path_to_tmp_dir,
            "strictdoc_cache",
            file_name,
        )
        if os.path.isfile(path_to_cached_file):
            with open(path_to_cached_file, "rb") as cache_file:
                sdoc_pickled = cache_file.read()
            return assert_cast(pickle_load(sdoc_pickled), Document)

        path_to_cached_file_dir = os.path.dirname(path_to_cached_file)
        Path(path_to_cached_file_dir).mkdir(parents=True, exist_ok=True)

        with open(file_path, encoding="utf8") as file:
            sdoc_content = file.read()

        try:
            sdoc = self.read(sdoc_content, file_path=file_path)

            sdoc_pickled = pickle_dump(sdoc)
            with open(path_to_cached_file, "wb") as cache_file:
                cache_file.write(sdoc_pickled)

            return sdoc
        except StrictDocException as exception:
            print(f"error: {exception.args[0]}")  # noqa: T201
            sys.exit(1)
        except NotImplementedError:
            traceback.print_exc()
            sys.exit(1)
        except StrictDocSemanticError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            print(  # noqa: T201
                f"error: could not parse file: "
                f"{file_path}.\n{exc.__class__.__name__}: {exc}"
            )
            # TODO: when --debug is provided
            traceback.print_exc()
            sys.exit(1)

    @staticmethod
    def parse_include(include, parse_context):
        reader = SDIncludeReader()
        fragment = reader.read_from_file(
            file_path=include.file, context=parse_context
        )
        assert isinstance(fragment, Fragment)
        return fragment
