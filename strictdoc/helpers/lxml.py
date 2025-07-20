from lxml import etree
from lxml.etree import _Element

BLOCK_TAGS = {"div", "p"}


def convert_xhtml_to_multiline_string(xhtml_value: str) -> str:
    r"""
    Convert HTML string to just plain text paragraphs.

    Replace <div>...</div> and <p>...</p> tags with \n\n newlines. Normalize
    combinations of more than two newline characters to just \n\n. Also,
    remove all training spaces before and after each paragraph.

    The method is used for converting ReqIF XHTML text blocks to plain text
    paragraphs that StrictDoc renders as RST (current default).

    The method assumes that the input HTML string has already been stripped
    from the xhtml namespace. i.e., instead of <xhtml:div>...</xhtml:div>, the
    input string will only have <div>...</div>.
    """

    root = etree.fromstring(xhtml_value.encode())

    parts = []

    def recurse(elem: _Element) -> None:
        if elem.text:
            parts.append(elem.text)

        for child in elem:
            recurse(child)
            if child.tail:
                parts.append(child.tail)

        # End of block is replaced with \n\n.
        if elem.tag in BLOCK_TAGS:
            parts.append("\n\n")

    recurse(root)
    text = "".join(parts)

    # Normalize multiple newlines to two.
    text = "\n\n".join(filter(None, map(str.strip, text.split("\n\n"))))
    return text.strip()
