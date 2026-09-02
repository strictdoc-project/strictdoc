from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_custom_meta_value.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_document_config = resolve('document_config')
    l_0_view_object = resolve('view_object')
    pass
    if context.call(environment.getattr((undefined(name='document_config') if l_0_document_config is missing else l_0_document_config), 'has_custom_metadata')):
        pass
        l_1_loop = missing
        for (l_1_key, l_1_value), l_1_loop in LoopContext(context.call(environment.getattr((undefined(name='document_config') if l_0_document_config is missing else l_0_document_config), 'get_custom_metadata')), undefined):
            l_1_form_key = l_1_metadata_value = missing
            _loop_vars = {}
            pass
            l_1_form_key = markup_join(('custom_meta_', environment.getattr(l_1_loop, 'index0'), ))
            _loop_vars['form_key'] = l_1_form_key
            l_1_metadata_value = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_metadata_value'), l_1_value, _loop_vars=_loop_vars)
            _loop_vars['metadata_value'] = l_1_metadata_value
            l_2_field_content = (undefined(name='metadata_value') if l_1_metadata_value is missing else l_1_metadata_value)
            l_2_field_label = l_1_key
            l_2_field_value = l_1_value
            l_2_form_key = (undefined(name='form_key') if l_1_form_key is missing else l_1_form_key)
            pass
            template = environment.get_template('screens/document/table/field_display_mode/document_custom_meta_row.jinja', 'screens/document/table/field_display_mode/document_custom_meta_value.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_2_field_content, 'field_label': l_2_field_label, 'field_value': l_2_field_value, 'form_key': l_2_form_key, 'key': l_1_key, 'loop': l_1_loop, 'metadata_value': l_1_metadata_value, 'value': l_1_value}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_field_content = l_2_field_label = l_2_field_value = l_2_form_key = missing
        l_1_loop = l_1_key = l_1_value = l_1_form_key = l_1_metadata_value = missing
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        template = environment.get_template('screens/document/table/field_display_mode/document_custom_meta_add.jinja', 'screens/document/table/field_display_mode/document_custom_meta_value.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()

blocks = {}
debug_info = '5=13&6=16&13=20&14=22&21=29&26=37&27=39'