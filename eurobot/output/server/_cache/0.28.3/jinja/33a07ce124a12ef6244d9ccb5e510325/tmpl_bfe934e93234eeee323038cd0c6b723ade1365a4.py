from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/_shared/frame_show_full_node.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('components/modal/index.jinja', 'screens/document/_shared/frame_show_full_node.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    yield from parent_template.root_render_func(context)

def block_modal_container(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_requirement = resolve('requirement')
    l_0_sdoc_entity = l_0_node = missing
    pass
    l_0_sdoc_entity = (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)
    _block_vars['sdoc_entity'] = l_0_sdoc_entity
    l_0_node = (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)
    _block_vars['node'] = l_0_node
    template = environment.get_template('components/node_content/index_extends_readonly.jinja', 'screens/document/_shared/frame_show_full_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'node': l_0_node, 'sdoc_entity': l_0_sdoc_entity}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n'

blocks = {'modal_container': block_modal_container}
debug_info = '1=12&2=17&3=27&4=29&5=31'