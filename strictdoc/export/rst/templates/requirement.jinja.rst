{% if requirement.uid is not none %}
.. _{{requirement.uid}}:
{% endif %}

{%- if requirement.title is not none %}
{{ _print_rst_header(requirement.title, requirement.ng_level) }}
{% endif %}

{%- if requirement.uid is not none %}
.. list-table::
    :align: left
    :header-rows: 0

    * - **UID:**
      - {{requirement.uid}}
{% endif %}

{%- if requirement.statement is not none %}
{{requirement.statement}}
{% elif requirement.statement_multiline is not none %}
{{requirement.statement_multiline}}
{% endif %}

{%- for comment in requirement.comments %}
**Comment:** {{comment.get_comment()}}
{% endfor %}

{%- set requirement_references = requirement.get_requirement_references() %}
{%- if requirement_references|length > 0 %}
**Parents:**
{% if true -%}{# without this workaround Jinja eats too much or not enough whitespace. #}{%- endif %}
{%- for reference in requirement_references %}
- ``[{{reference.path}}]`` :ref:`{{reference.path}}`
{%- endfor %}
{% endif %}

{%- if index.has_children_requirements(requirement) %}
**Children:**
{% if true -%}{# without this workaround Jinja eats too much or not enough whitespace. #}{%- endif %}
{%- for child_requirement in index.get_children_requirements(requirement) %}
- ``[{{child_requirement.uid}}]`` :ref:`{{child_requirement.uid}}`
{%- endfor %}
{% endif %}
