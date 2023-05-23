import re

# Possible tags with arguments and without:
# .. image:: _assets/picture.svg
# .. csv-table:: (has no argument)
RST_DIRECTIVE_PATTERN = re.compile(r"^\.\. [a-z-]+:: ?.*$", re.MULTILINE)


def string_contains_rst_directive(input_string: str) -> bool:
    return RST_DIRECTIVE_PATTERN.match(input_string) is not None


def truncated_statement_with_no_rst(input_string: str) -> str:
    statement_to_render = input_string
    if len(statement_to_render) >= 255:
        first_line_break_index = statement_to_render.find("\n\n")
        if first_line_break_index != -1:
            statement_to_render = statement_to_render[0:first_line_break_index]
        else:
            statement_to_render = statement_to_render[0:255]

        # We do not want to have anything that contains RST directives
        # truncated because that can result in RST validation errors later on.
        if string_contains_rst_directive(statement_to_render):
            statement_to_render = "<...>"
        else:
            statement_to_render += " <...>"
    return statement_to_render
