from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/update_node_field/stream_update_node_field.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_node = resolve('node')
    l_0_field_name = resolve('field_name')
    l_0_field_value = resolve('field_value')
    pass
    yield '<turbo-stream action="update" target="cell-'
    yield escape(environment.getattr((undefined(name='node') if l_0_node is missing else l_0_node), 'reserved_mid'))
    yield '-'
    yield escape((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name))
    yield '">\n  <template>'
    if (((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name) == 'TITLE') and (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value)):
        pass
        l_1_sdoc_entity = (undefined(name='node') if l_0_node is missing else l_0_node)
        pass
        template = environment.get_template('components/anchor/index.jinja', 'actions/table/update_node_field/stream_update_node_field.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'sdoc_entity': l_1_sdoc_entity}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_sdoc_entity = missing
        l_1_field_content = (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value)
        pass
        template = environment.get_template('screens/document/table/field_display_mode/title.jinja', 'actions/table/update_node_field/stream_update_node_field.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = missing
    elif (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value):
        pass
        l_1_field_content = (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value)
        pass
        template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'actions/table/update_node_field/stream_update_node_field.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = missing
    yield '</template>\n</turbo-stream>'

blocks = {}
debug_info = '1=15&3=19&5=23&8=32&10=39&12=43'