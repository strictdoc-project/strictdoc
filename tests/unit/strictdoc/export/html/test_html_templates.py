import pytest
from jinja2 import DictLoader, Environment, TemplateRuntimeError

from strictdoc.export.html.jinja.assert_extension import AssertExtension


def test_assert():
    template_string = """\
{% assert 0, "TEST ASSERT" %}
    """

    env = Environment(
        loader=DictLoader(
            {
                "my_template": template_string,
            }
        ),
        extensions=[AssertExtension],
    )

    template = env.get_template("my_template")

    with pytest.raises(Exception) as exc_info:
        template.render(name="World")

    assert exc_info.type is TemplateRuntimeError
    assert (
        exc_info.value.args[0]
        == """\
Assertion error in the Jinja template: None:1. Message: TEST ASSERT\
"""
    )
