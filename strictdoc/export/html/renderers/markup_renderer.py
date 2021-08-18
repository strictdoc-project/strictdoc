from strictdoc.backend.dsl.models.requirement import (
    Requirement,
    RequirementComment,
)
from strictdoc.backend.dsl.models.section import FreeText
from strictdoc.export.html.renderers.text_to_html_writer import TextToHtmlWriter
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)


class MarkupRenderer:
    @staticmethod
    def create(markup):
        if not markup or markup == "RST":
            html_fragment_writer = RstToHtmlFragmentWriter
        else:
            html_fragment_writer = TextToHtmlWriter
        return MarkupRenderer(html_fragment_writer)

    def __init__(self, fragment_writer):
        self.cache = {}
        self.rationale_cache = {}
        self.fragment_writer = fragment_writer

    def render_requirement_statement(self, requirement):
        assert isinstance(requirement, Requirement)
        if requirement in self.cache:
            return self.cache[requirement]

        output = self.fragment_writer.write(
            requirement.get_statement_single_or_multiline()
        )
        self.cache[requirement] = output

        return output

    def render_requirement_rationale(self, requirement):
        assert isinstance(requirement, Requirement)
        if requirement in self.rationale_cache:
            return self.rationale_cache[requirement]

        output = self.fragment_writer.write(
            requirement.get_rationale_single_or_multiline()
        )
        self.rationale_cache[requirement] = output

        return output

    def render_comment(self, comment):
        assert isinstance(comment, RequirementComment)
        if comment in self.cache:
            return self.cache[comment]

        output = self.fragment_writer.write(comment.get_comment())
        self.cache[comment] = output

        return output

    def render_free_text(self, free_text):
        assert isinstance(free_text, FreeText)
        if free_text in self.cache:
            return self.cache[free_text]

        output = self.fragment_writer.write(free_text.text)
        self.cache[free_text] = output

        return output
