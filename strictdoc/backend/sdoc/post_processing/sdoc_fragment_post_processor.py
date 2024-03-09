import os

from strictdoc.backend.sdoc.include_reader import SDIncludeReader
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.fragment import Fragment
from strictdoc.backend.sdoc.models.fragment_from_file import FragmentFromFile
from strictdoc.backend.sdoc.processor import ParseContext


class SDocFragmentPostProcessor:
    @staticmethod
    def process_document(_: SDocDocument, parse_context: ParseContext):
        for fragment_from_file_ in parse_context.fragments_from_files:
            assert isinstance(
                fragment_from_file_, FragmentFromFile
            ), fragment_from_file_
            fragment: Fragment = SDocFragmentPostProcessor.parse_fragment(
                fragment_from_file_, parse_context
            )

            parent_section_contents = (
                fragment_from_file_.parent.section_contents
            )
            index = parent_section_contents.index(fragment_from_file_)
            before = parent_section_contents[:index]
            index = (
                index + 1
            )  # black and flake8 fight to put a space before ':' otherwise
            after = parent_section_contents[index:]

            fragment_from_file_.parent.section_contents = []
            fragment_from_file_.parent.section_contents.extend(before)
            fragment_from_file_.parent.section_contents.extend(
                fragment.section_contents
            )
            fragment_from_file_.parent.section_contents.extend(after)

    @staticmethod
    def parse_fragment(
        fragment_from_file: FragmentFromFile, parse_context: ParseContext
    ):
        path_to_fragment = (
            os.path.join(
                parse_context.path_to_sdoc_dir, fragment_from_file.file
            )
            if parse_context.path_to_sdoc_dir is not None
            else fragment_from_file.file
        )
        reader = SDIncludeReader()
        fragment = reader.read_from_file(
            file_path=path_to_fragment, context=parse_context
        )
        assert isinstance(fragment, Fragment)
        return fragment
