from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_edit_mode/document_custom_meta_name.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_key = resolve('form_key')
    l_0_field_label = resolve('field_label')
    l_0_name_errors = resolve('name_errors')
    pass
    yield '\n<input type="hidden" name="active_form_key" value="'
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '"/>\n<input type="hidden" name="active_field_name" value="name"/>'
    l_1_field_class_name = 'monospace'
    l_1_field_editable = True
    l_1_field_required = True
    l_1_field_input_name = markup_join(('metadata[', (undefined(name='form_key') if l_0_form_key is missing else l_0_form_key), '][name]', ))
    l_1_field_label = 'Name'
    l_1_field_placeholder = 'Enter name...'
    l_1_field_type = 'singleline'
    l_1_field_value = (undefined(name='field_label') if l_0_field_label is missing else l_0_field_label)
    l_1_testid_postfix = markup_join(('metadata-name-', (undefined(name='form_key') if l_0_form_key is missing else l_0_form_key), ))
    l_1_errors = (undefined(name='name_errors') if l_0_name_errors is missing else l_0_name_errors)
    l_1_field_render_errors = False
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'screens/document/table/field_edit_mode/document_custom_meta_name.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_render_errors': l_1_field_render_errors, 'field_required': l_1_field_required, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_required = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_testid_postfix = l_1_errors = l_1_field_render_errors = missing

blocks = {}
debug_info = '7=15&23=29'