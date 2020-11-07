from strictdoc.backend.dsl.models.requirement import Requirement, RequirementComment
from strictdoc.backend.dsl.models.section import FreeText
from strictdoc.export.rst.rst_to_html_fragment_writer import RstToHtmlFragmentWriter


class MarkupRenderer:
    def __init__(self):
        self.cache = {}

    def render_requirement_statement(self, requirement):
        assert isinstance(requirement, Requirement)
        if requirement in self.cache:
            return self.cache[requirement]

        output = RstToHtmlFragmentWriter.write(
            requirement.get_statement_single_or_multiline()
        )
        self.cache[requirement] = output

        return output

    def render_comment(self, comment):
        assert isinstance(comment, RequirementComment)
        if comment in self.cache:
            return self.cache[comment]

        output = RstToHtmlFragmentWriter.write(comment.get_comment())
        self.cache[comment] = output

        return output

    def render_free_text(self, free_text):
        assert isinstance(free_text, FreeText)
        if free_text in self.cache:
            return self.cache[free_text]

        output = RstToHtmlFragmentWriter.write(free_text.text)
        self.cache[free_text] = output

        return output
