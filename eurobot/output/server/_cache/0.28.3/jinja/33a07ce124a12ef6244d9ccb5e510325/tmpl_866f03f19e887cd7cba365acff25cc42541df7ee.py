from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/update_node_relations/stream_update.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_node_mid = resolve('node_mid')
    l_0_affected_related_nodes = resolve('affected_related_nodes')
    pass
    yield '<turbo-stream action="update" target="cell-'
    yield escape((undefined(name='node_mid') if l_0_node_mid is missing else l_0_node_mid))
    yield '-RELATIONS">\n  <template>'
    template = environment.get_template('screens/document/table/field_display_mode/relations.jinja', 'actions/table/update_node_relations/stream_update.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </template>\n</turbo-stream>'
    for l_1_related_node in (undefined(name='affected_related_nodes') if l_0_affected_related_nodes is missing else l_0_affected_related_nodes):
        _loop_vars = {}
        pass
        yield '\n<turbo-stream action="update" target="cell-'
        yield escape(environment.getattr(l_1_related_node, 'reserved_mid'))
        yield '-RELATIONS">\n  <template>'
        l_2_requirement = l_1_related_node
        pass
        template = environment.get_template('screens/document/table/field_display_mode/relations.jinja', 'actions/table/update_node_relations/stream_update.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'requirement': l_2_requirement, 'related_node': l_1_related_node}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_2_requirement = missing
        yield '\n  </template>\n</turbo-stream>'
    l_1_related_node = missing
    yield '\n<turbo-stream action="update" target="modal">\n  <template></template>\n</turbo-stream>'

blocks = {}
debug_info = '1=14&3=16&6=23&7=27&10=31'