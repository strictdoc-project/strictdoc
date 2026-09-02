from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/get_document_custom_meta_inline/stream_inline_form.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_key = resolve('form_key')
    l_0_errors = resolve('errors')
    l_0_field_name = resolve('field_name')
    pass
    yield '\n<turbo-stream\n  action="remove"\n  targets="[js-table_view_edit-custom_meta-error=\''
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '\']"\n>\n  <template></template>\n</turbo-stream>\n<turbo-stream action="after" target="document-custom-meta-field-'
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '">\n  <template>'
    for l_1_error_ in (undefined(name='errors') if l_0_errors is missing else l_0_errors):
        _loop_vars = {}
        pass
        yield '<sdoc-form-error\n        js-table_view_edit-custom_meta-error="'
        yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
        yield '"\n        data-testid="document-config-metadata-error-'
        yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
        yield '"\n      >'
        yield escape(l_1_error_)
        yield '</sdoc-form-error>'
    l_1_error_ = missing
    yield '</template>\n</turbo-stream>\n<turbo-stream\n  action="update"\n  target="document-custom-meta-'
    yield escape((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name))
    yield '-'
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '"\n>\n  <template>'
    if ((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name) == 'name'):
        pass
        template = environment.get_template('screens/document/table/field_edit_mode/document_custom_meta_name.jinja', 'actions/table/get_document_custom_meta_inline/stream_inline_form.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    else:
        pass
        template = environment.get_template('screens/document/table/field_edit_mode/document_custom_meta.jinja', 'actions/table/get_document_custom_meta_inline/stream_inline_form.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    yield '</template>\n</turbo-stream>'

blocks = {}
debug_info = '8=15&12=17&14=19&16=23&17=25&18=27&24=31&27=35&28=37&30=45'