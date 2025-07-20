from strictdoc.helpers.lxml import convert_xhtml_to_multiline_string


def test_convert_xhtml_to_multiline_string():
    output = convert_xhtml_to_multiline_string("""\
<div>foo</div>
""")
    assert (
        output
        == """\
foo\
"""
    )

    output = convert_xhtml_to_multiline_string("""\
<div><p>foo</p></div>
""")
    assert (
        output
        == """\
foo\
"""
    )

    output = convert_xhtml_to_multiline_string("""\
<div><p>foo1</p><p>foo2</p><p>foo3</p></div>
""")
    assert (
        output
        == """\
foo1

foo2

foo3\
"""
    )

    output = convert_xhtml_to_multiline_string("""\
<div><div>foo1</div><div>foo2</div><div>foo3</div></div>
""")
    assert (
        output
        == """\
foo1

foo2

foo3\
"""
    )

    output = convert_xhtml_to_multiline_string("""\
<div>

    <div>
        foo1
    </div>
    
    
    
    <div>foo2</div>
    
    <div>
    
    foo3
    
    
    </div>

</div>
""")  # noqa: W293

    assert (
        output
        == """\
foo1

foo2

foo3\
"""
    )
