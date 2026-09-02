from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/update_node_field_multiline/stream_update.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_node_mid = resolve('node_mid')
    l_0_field_name = resolve('field_name')
    l_0_rendered_content = resolve('rendered_content')
    pass
    yield '<turbo-stream action="update" target="cell-'
    yield escape((undefined(name='node_mid') if l_0_node_mid is missing else l_0_node_mid))
    yield '-'
    yield escape((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name))
    yield '">\n  <template>'
    if (undefined(name='rendered_content') if l_0_rendered_content is missing else l_0_rendered_content):
        pass
        l_1_field_content = (undefined(name='rendered_content') if l_0_rendered_content is missing else l_0_rendered_content)
        pass
        template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'actions/table/update_node_field_multiline/stream_update.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = missing
    yield '</template>\n</turbo-stream>\n<turbo-stream action="update" target="modal">\n  <template></template>\n</turbo-stream>'

blocks = {}
debug_info = '1=15&3=19&5=23'