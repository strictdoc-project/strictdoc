import re

# Possible tags with arguments and without:
# .. image:: _assets/picture.svg
# .. csv-table:: (has no argument)
RST_DIRECTIVE_PATTERN = re.compile(r"^\.\. [a-z-]+:: ?.*$", re.MULTILINE)


def string_contains_rst_directive(input_string: str) -> bool:
    return RST_DIRECTIVE_PATTERN.match(input_string) is not None
