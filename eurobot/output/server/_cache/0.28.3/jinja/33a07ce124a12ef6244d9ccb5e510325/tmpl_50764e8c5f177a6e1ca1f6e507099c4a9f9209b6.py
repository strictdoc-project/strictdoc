from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_edit_mode/contenteditable.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_action = resolve('form_action')
    l_0_node_mid = resolve('node_mid')
    l_0_field_name = resolve('field_name')
    l_0_field_type = resolve('field_type')
    l_0_current_value = resolve('current_value')
    pass
    yield '\n<form\n  action="'
    yield escape((undefined(name='form_action') if l_0_form_action is missing else l_0_form_action))
    yield '"\n  method="POST"\n  data-turbo="false"\n  js-table_view_edit-form\n>\n  <input type="hidden" name="node_mid" value="'
    yield escape((undefined(name='node_mid') if l_0_node_mid is missing else l_0_node_mid))
    yield '"/>\n  <input type="hidden" name="field_name" value="'
    yield escape((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name))
    yield '"/>'
    l_1_field_class_name = None
    l_1_field_editable = True
    l_1_field_input_name = 'field_value'
    l_1_field_label = (undefined(name='field_name') if l_0_field_name is missing else l_0_field_name)
    l_1_field_placeholder = markup_join(('Enter ', (undefined(name='field_name') if l_0_field_name is missing else l_0_field_name), ' here...', ))
    l_1_field_type = (undefined(name='field_type') if l_0_field_type is missing else l_0_field_type)
    l_1_field_value = (undefined(name='current_value') if l_0_current_value is missing else l_0_current_value)
    l_1_testid_postfix = (undefined(name='field_name') if l_0_field_name is missing else l_0_field_name)
    l_1_errors = []
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'screens/document/table/field_edit_mode/contenteditable.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_testid_postfix = l_1_errors = missing
    yield '</form>'

blocks = {}
debug_info = '6=17&11=19&12=21&25=33'