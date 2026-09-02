from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/update_document_config_field/stream_update.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_document = resolve('document')
    l_0_field_name = resolve('field_name')
    l_0_display_value = resolve('display_value')
    pass
    yield '<turbo-stream action="update" target="doc-field-'
    yield escape(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'reserved_mid'))
    yield '-'
    yield escape((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name))
    yield '">\n  <template>'
    if ((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name) == 'TITLE'):
        pass
        l_1_field_content = (undefined(name='display_value') if l_0_display_value is missing else l_0_display_value)
        pass
        template = environment.get_template('screens/document/table/field_display_mode/document_title.jinja', 'actions/table/update_document_config_field/stream_update.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = missing
    elif (undefined(name='display_value') if l_0_display_value is missing else l_0_display_value):
        pass
        l_1_field_content = (undefined(name='display_value') if l_0_display_value is missing else l_0_display_value)
        pass
        template = environment.get_template('screens/document/table/field_display_mode/document_config_field_value.jinja', 'actions/table/update_document_config_field/stream_update.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = missing
    yield '</template>\n</turbo-stream>\n\n'
    if ((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name) == 'TITLE'):
        pass
        yield '<turbo-stream action="replace" target="header_document_title">\n  <template>\n    '
        template = environment.get_template('screens/document/_shared/frame_header_document_title.jinja', 'actions/table/update_document_config_field/stream_update.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  </template>\n</turbo-stream>'

blocks = {}
debug_info = '1=15&3=19&5=23&7=30&9=34&16=42&19=45'