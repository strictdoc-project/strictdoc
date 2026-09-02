from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_edit_mode/autocompletable.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_cell_field_name = resolve('cell_field_name')
    l_0_current_value = resolve('current_value')
    l_0_node_mid = resolve('node_mid')
    l_0_document_mid = resolve('document_mid')
    l_0_element_type = resolve('element_type')
    l_0_is_multiple_choice = resolve('is_multiple_choice')
    pass
    l_1_field_class_name = None
    l_1_field_editable = True
    l_1_field_input_name = (undefined(name='cell_field_name') if l_0_cell_field_name is missing else l_0_cell_field_name)
    l_1_field_label = (undefined(name='cell_field_name') if l_0_cell_field_name is missing else l_0_cell_field_name)
    l_1_field_placeholder = (undefined(name='cell_field_name') if l_0_cell_field_name is missing else l_0_cell_field_name)
    l_1_field_value = (undefined(name='current_value') if l_0_current_value is missing else l_0_current_value)
    l_1_mid = (undefined(name='node_mid') if l_0_node_mid is missing else l_0_node_mid)
    l_1_testid_postfix = (undefined(name='cell_field_name') if l_0_cell_field_name is missing else l_0_cell_field_name)
    l_1_autocomplete_url = markup_join(('/autocomplete/field?document_mid=', (undefined(name='document_mid') if l_0_document_mid is missing else l_0_document_mid), '&element_type=', (undefined(name='element_type') if l_0_element_type is missing else l_0_element_type), '&field_name=', (undefined(name='cell_field_name') if l_0_cell_field_name is missing else l_0_cell_field_name), ))
    l_1_autocomplete_len = 0
    l_1_autocomplete_multiplechoice = (undefined(name='is_multiple_choice') if l_0_is_multiple_choice is missing else l_0_is_multiple_choice)
    l_1_result_class_name = 'cell-autocomplete-dropdown'
    pass
    template = environment.get_template('components/form/field/autocompletable/index.jinja', 'screens/document/table/field_edit_mode/autocompletable.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'autocomplete_len': l_1_autocomplete_len, 'autocomplete_multiplechoice': l_1_autocomplete_multiplechoice, 'autocomplete_url': l_1_autocomplete_url, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_value': l_1_field_value, 'mid': l_1_mid, 'result_class_name': l_1_result_class_name, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_value = l_1_mid = l_1_testid_postfix = l_1_autocomplete_url = l_1_autocomplete_len = l_1_autocomplete_multiplechoice = l_1_result_class_name = missing

blocks = {}
debug_info = '31=30'