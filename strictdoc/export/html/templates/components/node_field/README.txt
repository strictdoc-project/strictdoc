{#
  This template
  - gets the sdoc_entity parameter from the view it is included in,
  - or you must use it with the variable:
      {%- with sdoc_entity = requirement -%}
      {% include "components/***/index.jinja" %}
      {%- endwith -%}
#}
