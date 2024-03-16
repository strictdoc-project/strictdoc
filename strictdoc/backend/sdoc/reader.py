import os.path
import sys
import traceback
from pathlib import Path
from typing import Tuple

from textx import metamodel_from_str

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.models.constants import DOCUMENT_MODELS
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.backend.sdoc.processor import ParseContext, SDocParsingProcessor
from strictdoc.backend.sdoc.validations.sdoc_validator import SDocValidator
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
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

        parse_context = ParseContext(path_to_sdoc_file=file_path)
        processor = SDocParsingProcessor(parse_context=parse_context)
        meta_model.register_obj_processors(processor.get_default_processors())

        document: SDocDocument = meta_model.model_from_str(
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
    def read(input_string, file_path=None) -> SDocDocument:
        document, _ = SDReader.read_with_parse_context(input_string, file_path)
        return document

    @staticmethod
    def read_with_parse_context(
        input_string, file_path=None
    ) -> Tuple[SDocDocument, ParseContext]:
        document, parse_context = SDReader._read(input_string, file_path)
        SDocValidator.validate_document(document)

        return document, parse_context

    def read_from_file(self, file_path: str) -> SDocDocument:
        """
        This function parses the provided .sdoc file and returns a Document
        object.
        """

        path_to_cached_file = PickleCache.get_cached_file_path(
            file_path, self.path_to_output_root
        )
        if os.path.isfile(path_to_cached_file):
            with open(path_to_cached_file, "rb") as cache_file:
                sdoc_pickled = cache_file.read()
            return assert_cast(pickle_load(sdoc_pickled), SDocDocument)

        path_to_cached_file_dir = os.path.dirname(path_to_cached_file)
        Path(path_to_cached_file_dir).mkdir(parents=True, exist_ok=True)

        with open(file_path, encoding="utf8") as file:
            sdoc_content = file.read()

        try:
            sdoc, parse_context = self.read_with_parse_context(
                sdoc_content, file_path=file_path
            )

            sdoc.fragments_from_files = parse_context.fragments_from_files

            # HACK:
            # ProcessPoolExecutor doesn't work because of non-picklable parts
            # of textx. The offending fields are stripped down because they
            # are not used anyway.
            drop_textx_meta(sdoc)

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
