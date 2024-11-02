# mypy: disable-error-code="no-any-return,no-untyped-call,no-untyped-def"
import sys
import traceback
from typing import Tuple

from textx import metamodel_from_str

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.grammar.grammar_builder import SDocGrammarBuilder
from strictdoc.backend.sdoc.models.constants import DOCUMENT_MODELS
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.backend.sdoc.processor import ParseContext, SDocParsingProcessor
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.textx import drop_textx_meta


class SDReader:
    meta_model = metamodel_from_str(
        SDocGrammarBuilder.create_grammar(),
        classes=DOCUMENT_MODELS,
        use_regexp_group=True,
    )

    @staticmethod
    def _read(input_string, file_path=None):
        parse_context = ParseContext(path_to_sdoc_file=file_path)
        processor = SDocParsingProcessor(parse_context=parse_context)
        SDReader.meta_model.register_obj_processors(
            processor.get_default_processors()
        )

        document: SDocDocument = SDReader.meta_model.model_from_str(
            input_string, file_name=file_path
        )
        parse_context.document_reference.set_document(document)
        document.ng_has_requirements = parse_context.document_has_requirements

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
        return document, parse_context

    def read_from_file(
        self, file_path: str, project_config: ProjectConfig
    ) -> SDocDocument:
        """
        This function parses the provided .sdoc file and returns a Document
        object.
        """

        unpickled_content = PickleCache.read_from_cache(
            file_path, project_config, "sdoc"
        )
        if unpickled_content:
            return assert_cast(unpickled_content, SDocDocument)

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

            PickleCache.save_to_cache(sdoc, file_path, project_config, "sdoc")

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
