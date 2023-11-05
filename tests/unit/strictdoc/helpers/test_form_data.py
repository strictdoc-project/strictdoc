import pytest

from strictdoc.helpers.form_data import parse_form_data


def test_01():
    form_data = [
        ("document_mid", "b7dc9679bd77416cb8205c6b8f73d66f"),
    ]
    result = parse_form_data(form_data)

    assert result == {
        "document_mid": "b7dc9679bd77416cb8205c6b8f73d66f",
    }


def test_01_02():
    form_data = [
        ("document_mid[0][name]", "b7dc9679bd77416cb8205c6b8f73d66f"),
    ]
    result = parse_form_data(form_data)

    assert result == {
        "document_mid": [
            {
                "name": "b7dc9679bd77416cb8205c6b8f73d66f",
            }
        ]
    }


def test_02():
    form_data = [
        ("document_grammar_field[UID][UIE]", "Value"),
    ]
    result = parse_form_data(form_data)

    assert result == {
        "document_grammar_field": {"UID": {"UIE": "Value"}},
    }


def test_03():
    form_data = [
        ("document_grammar_field[0][UIE]", "Value"),
    ]
    result = parse_form_data(form_data)

    assert result == {
        "document_grammar_field": [{"UIE": "Value"}],
    }


def test_04():
    form_data = [
        ("document_grammar_field[0][relation_type]", "Parent"),
        ("document_grammar_field[1][relation_type]", "Parent"),
    ]
    result = parse_form_data(form_data)

    assert result == {
        "document_grammar_field": [
            {
                "relation_type": "Parent",
            },
            {
                "relation_type": "Parent",
            },
        ],
    }


def test_05():
    form_data = [
        ("document_grammar_field[0][relation_type]", "Parent"),
        ("document_grammar_field[0][relation_type_two]", "Child"),
    ]
    result = parse_form_data(form_data)

    assert result == {
        "document_grammar_field": [
            {
                "relation_type": "Parent",
                "relation_type_two": "Child",
            }
        ],
    }


def test_06():
    form_data = [
        ("document_grammar_relation[0][type]", "Parent"),
        ("document_grammar_relation[0][role]", "Refines"),
        ("document_grammar_relation[1][type]", "Parent"),
        ("document_grammar_relation[1][role]", "Implements"),
    ]

    result = parse_form_data(form_data)

    assert result == {
        "document_grammar_relation": [
            {
                "type": "Parent",
                "role": "Refines",
            },
            {
                "type": "Parent",
                "role": "Implements",
            },
        ],
    }


def test_07():
    form_data = [
        ("document_grammar_relation[0][type]", "Parent"),
        ("document_grammar_relation[0][role]", "Refines"),
        ("document_grammar_relation[1][type]", "Parent"),
        ("document_grammar_relation[1][role]", "Implements"),
        ("document_grammar_relation[2][type]", "Parent"),
        ("document_grammar_relation[2][role]", "Verifies"),
    ]

    result = parse_form_data(form_data)

    assert result == {
        "document_grammar_relation": [
            {
                "type": "Parent",
                "role": "Refines",
            },
            {
                "type": "Parent",
                "role": "Implements",
            },
            {
                "type": "Parent",
                "role": "Verifies",
            },
        ],
    }


def test_08():
    form_data = [
        ("document_grammar_relation[0][type]", "Parent"),
        ("document_grammar_relation[0][role]", "Refines"),
        ("document_grammar_relation[1][list][0][foo]", "foo"),
        ("document_grammar_relation[1][list][0][bar]", "bar"),
    ]

    result = parse_form_data(form_data)

    assert result == {
        "document_grammar_relation": [
            {
                "type": "Parent",
                "role": "Refines",
            },
            {
                "list": [
                    {
                        "foo": "foo",
                        "bar": "bar",
                    },
                ]
            },
        ],
    }


def test_20():
    form_data = [
        ("document_mid[1][name]", "b7dc9679bd77416cb8205c6b8f73d66f"),
    ]
    with pytest.raises(IndentationError) as exc_info:
        parse_form_data(form_data)
    assert """\
The ordering [0], [1], ... is broken in this form data: \
{'document_mid': []} ['document_mid', 1, 'name'] \
b7dc9679bd77416cb8205c6b8f73d66f.\
""" == str(exc_info.value)


def test_21():
    form_data = [
        ("document_mid[2][name]", "b7dc9679bd77416cb8205c6b8f73d66f"),
    ]
    with pytest.raises(IndentationError) as exc_info:
        parse_form_data(form_data)
    assert """\
The ordering [0], [1], ... is broken in this form data: \
{'document_mid': []} ['document_mid', 2, 'name'] \
b7dc9679bd77416cb8205c6b8f73d66f.\
""" == str(exc_info.value)


def test_22():
    form_data = [
        ("document_mid[0][name]", "ABC"),
        ("document_mid[2][name]", "XYZ"),
    ]
    with pytest.raises(IndentationError) as exc_info:
        parse_form_data(form_data)
    assert """\
The ordering [0], [1], ... is broken in this form data: \
{'document_mid': [{'name': 'ABC'}]} \
['document_mid', 2, 'name'] XYZ.\
""" == str(exc_info.value)


def test_30():
    form_data = [
        ("document_mid[0][name]", "ABC"),
        ("document_mid[new][name]", "XYZ"),
    ]
    with pytest.raises(KeyError):
        parse_form_data(form_data)


def test_100():
    form_data = [
        ("document_mid", "b7dc9679bd77416cb8205c6b8f73d66f"),
        ("document_grammar_field[UID]", "UID"),
        ("document_grammar_field[TITLE]", "TITLE"),
        ("document_grammar_field[STATEMENT]", "STATEMENT"),
        ("document_grammar_field[RATIONALE]", "RATIONALE"),
        ("document_grammar_field[COMMENT]", "COMMENT"),
        ("document_grammar_relation[0][type]", "Parent"),
        ("document_grammar_relation[0][role]", "Refines"),
        ("document_grammar_relation[1][type]", "Parent"),
        ("document_grammar_relation[1][role]", "Implements"),
    ]

    result = parse_form_data(form_data)

    assert result == {
        "document_mid": "b7dc9679bd77416cb8205c6b8f73d66f",
        "document_grammar_field": {
            "UID": "UID",
            "TITLE": "TITLE",
            "STATEMENT": "STATEMENT",
            "RATIONALE": "RATIONALE",
            "COMMENT": "COMMENT",
        },
        "document_grammar_relation": [
            {
                "type": "Parent",
                "role": "Refines",
            },
            {
                "type": "Parent",
                "role": "Implements",
            },
        ],
    }
