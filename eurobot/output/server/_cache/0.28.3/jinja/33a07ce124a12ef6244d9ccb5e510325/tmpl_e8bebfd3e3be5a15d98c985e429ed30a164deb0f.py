from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node/readonly.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_view_object = resolve('view_object')
    l_0_node_type_string = missing
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '\n\n'
    l_0_node_type_string = context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_node_type_string'))
    context.vars['node_type_string'] = l_0_node_type_string
    context.exported_vars.add('node_type_string')
    yield '\n\n  <sdoc-node\n    class="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_html2pdf_classes'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity)))
    yield '"\n    node-style="readonly"\n    node-role="'
    yield escape(context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_type_string')))
    yield '"'
    if (not t_1((undefined(name='node_type_string') if l_0_node_type_string is missing else l_0_node_type_string))):
        pass
        yield '\n      show-node-type-name="'
        yield escape((undefined(name='node_type_string') if l_0_node_type_string is missing else l_0_node_type_string))
        yield '"'
    yield '\n    \n    '
    if context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'is_content_node')):
        pass
        yield 'node-view="'
        yield escape(context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_requirement_style_mode')))
        yield '"\n    '
    yield 'data-testid="node-'
    yield escape(context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_type_string')))
    yield '"\n  >\n\n    '
    template = environment.get_template('components/anchor/index.jinja', 'components/node/readonly.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'node_type_string': l_0_node_type_string}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    \n    '
    yield from context.blocks['sdoc_entity'][0](context)
    yield '\n\n  </sdoc-node>'

def block_sdoc_entity(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n    \n    '

blocks = {'sdoc_entity': block_sdoc_entity}
debug_info = '3=21&6=25&8=27&9=29&10=32&13=35&14=38&16=41&19=43&21=50'