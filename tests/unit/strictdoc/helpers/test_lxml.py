from lxml import etree

from strictdoc.helpers.lxml import stringify_children


def test_01():
    node = etree.fromstring(
        """<content>
    Text outside tag <div>Text <em>inside</em> tag</div>
    </content>"""
    )
    assert (
        stringify_children(node)
        == "\n    Text outside tag <div>Text <em>inside</em> tag</div>\n    "
    )
