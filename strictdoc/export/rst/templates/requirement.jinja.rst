{%- if requirement.reserved_uid is not none -%}
.. _{{requirement.reserved_uid}}:

{% endif -%}

{%- if requirement.reserved_title is not none -%}
{{ _print_rst_header(requirement.reserved_title, requirement.ng_level) }}

{% endif -%}

{%- if requirement.has_meta > 0 -%}
.. list-table::
    :align: left
    :header-rows: 0

{% for meta_field in requirement.enumerate_meta_fields(skip_multi_lines=True) -%}
{%- if true %}    {% endif %}* - **{{meta_field[0]}}:**
      - {{ meta_field[1] }}
{% endfor %}
{% endif %}

{%- if requirement.reserved_statement is not none -%}
{{requirement.reserved_statement.strip()}}

{% endif -%}

{%- if requirement.rationale -%}
**Rationale:** {{ requirement.rationale }}

{% endif -%}

{%- for comment in requirement.comments -%}
**Comment:** {{comment}}

{% endfor -%}

{%- if requirement.has_meta -%}
{%- for meta_field in requirement.enumerate_meta_fields(skip_single_lines=True) -%}
**{{meta_field[0]}}:**
{{ meta_field[1] }}

{% endfor -%}
{%- endif %}

{%- set parent_requirement_refs = requirement.get_requirement_references("Parent") -%}
{%- if parent_requirement_refs|length > 0 -%}
**Parents:**

{% for reference in parent_requirement_refs -%}
- ``[{{reference.ref_uid}}]`` :ref:`{{reference.ref_uid}}`
{% endfor %}
{% endif %}

{%- if index.has_children_requirements(requirement) -%}
**Children:**

{% for child_requirement in index.get_children_requirements(requirement) -%}
- ``[{{child_requirement.reserved_uid}}]`` :ref:`{{child_requirement.reserved_uid}}`
{% endfor %}
{% endif -%}
