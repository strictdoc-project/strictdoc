from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/text_node/index_extends_node.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_node = resolve('node')
    l_0_sdoc_entity = l_0_text_node = missing
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='node') if l_0_node is missing else l_0_node)), None, caller=caller)
    if parent_template is None:
        yield '\n\n'
    parent_template = environment.get_template('components/node/index.jinja', 'components/text_node/index_extends_node.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    l_0_sdoc_entity = (undefined(name='node') if l_0_node is missing else l_0_node)
    context.vars['sdoc_entity'] = l_0_sdoc_entity
    context.exported_vars.add('sdoc_entity')
    l_0_text_node = (undefined(name='node') if l_0_node is missing else l_0_node)
    context.vars['text_node'] = l_0_text_node
    context.exported_vars.add('text_node')
    yield from parent_template.root_render_func(context)

def block_sdoc_entity(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n'
    template = environment.get_template('components/text_node/index.jinja', 'components/text_node/index_extends_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n'

blocks = {'sdoc_entity': block_sdoc_entity}
debug_info = '1=20&3=28&4=31&5=34&6=39&7=48'