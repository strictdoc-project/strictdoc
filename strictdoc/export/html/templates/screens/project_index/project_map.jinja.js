// map of the project for the stable_uri forwarder
const projectMap = {
{%- for root_tree_ in view_object.document_tree_iterator.document_tree.file_tree %}
  {%- if root_tree_.root_folder_or_file.is_folder() %}
    {%- if root_tree_.root_folder_or_file.has_sdoc_content %}
      {%- with folder = root_tree_.root_folder_or_file %}
        {%- include "screens/project_index/project_map_folder.jinja" %}
      {%- endwith %}
    {%- endif %}
  {%- else %}
    {%- with file = root_tree_.root_folder_or_file %}
      {%- include "screens/project_index/project_map_file.jinja" %}
    {%- endwith %}
  {%- endif %}
{%- endfor %}
};

