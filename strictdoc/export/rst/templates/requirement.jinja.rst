{% if requirement.uid is not none %}
.. _{{requirement.uid}}:
{% endif %}

{%- if requirement.title is not none %}
{{ _print_rst_header(requirement.title, requirement.ng_level) }}
{% endif %}

{%- if requirement.has_meta > 0 %}
.. list-table::
    :align: left
    :header-rows: 0
{% if true -%}{# without this workaround Jinja eats too much or not enough whitespace. #}{%- endif %}
    {%- for meta_field in requirement.enumerate_meta_fields(skip_multi_lines=True) %}
    * - **{{meta_field[0]}}:**
      - {{ meta_field[1] }}
    {%- endfor -%}
{%- endif %}
{% if true -%}{# without this workaround Jinja eats too much or not enough whitespace. #}{%- endif %}

{%- if requirement.statement is not none %}
{{requirement.statement}}
{% elif requirement.statement_multiline is not none %}
{{requirement.statement_multiline}}
{% endif %}

{%- if requirement.rationale or requirement.rationale_multiline %}
**Rationale:** {{ requirement.get_rationale_single_or_multiline() }}
{% endif %}

{%- for comment in requirement.comments %}
**Comment:** {{comment.get_comment()}}
{% endfor %}

{%- if requirement.has_meta %}
{%- for meta_field in requirement.enumerate_meta_fields(skip_single_lines=True) %}
**{{meta_field[0]}}:**
{{ meta_field[1] }}
{% endfor %}
{%- endif %}

{%- set parent_requirement_refs = requirement.get_requirement_references("Parent") %}
{%- if parent_requirement_refs|length > 0 %}
**Parents:**
{% if true -%}{# without this workaround Jinja eats too much or not enough whitespace. #}{%- endif %}
{%- for reference in parent_requirement_refs %}
- ``[{{reference.ref_uid}}]`` :ref:`{{reference.ref_uid}}`
{%- endfor %}
{% endif %}

{%- if index.has_children_requirements(requirement) %}
**Children:**
{% if true -%}{# without this workaround Jinja eats too much or not enough whitespace. #}{%- endif %}
{%- for child_requirement in index.get_children_requirements(requirement) %}
- ``[{{child_requirement.uid}}]`` :ref:`{{child_requirement.uid}}`
{%- endfor %}
{% endif %}
