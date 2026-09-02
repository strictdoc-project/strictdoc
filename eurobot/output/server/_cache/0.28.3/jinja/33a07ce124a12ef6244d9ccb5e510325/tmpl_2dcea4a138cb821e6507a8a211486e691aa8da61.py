from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/update_document_custom_meta/stream_update.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_key = resolve('form_key')
    l_0_active_field_name = resolve('active_field_name')
    pass
    yield '\n<turbo-stream\n  action="remove"\n  targets="[js-table_view_edit-custom_meta-error=\''
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '\']"\n>\n  <template></template>\n</turbo-stream>\n<turbo-stream\n  action="update"\n  target="document-custom-meta-'
    yield escape((undefined(name='active_field_name') if l_0_active_field_name is missing else l_0_active_field_name))
    yield '-'
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '"\n>\n  <template>'
    if ((undefined(name='active_field_name') if l_0_active_field_name is missing else l_0_active_field_name) == 'name'):
        pass
        template = environment.get_template('screens/document/table/field_display_mode/document_custom_meta_field_name.jinja', 'actions/table/update_document_custom_meta/stream_update.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    else:
        pass
        template = environment.get_template('screens/document/table/field_display_mode/document_custom_meta_field_value.jinja', 'actions/table/update_document_custom_meta/stream_update.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    yield '</template>\n</turbo-stream>'

blocks = {}
debug_info = '8=14&14=16&17=20&18=22&20=30'