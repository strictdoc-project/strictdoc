from itertools import chain

from lxml.etree import tostring


# https://stackoverflow.com/a/4624146/598057
def stringify_children(node):
    return "".join(
        chunk
        for chunk in chain(
            (node.text,),
            chain(
                *(
                    (tostring(child, encoding=str, with_tail=False), child.tail)
                    for child in node.getchildren()
                )
            ),
            (node.tail,),
        )
        if chunk
    )
