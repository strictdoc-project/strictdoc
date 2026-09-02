from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_content/tiny_extends_card.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_requirement = resolve('requirement')
    l_0_sdoc_entity = l_0_requirement_style = missing
    pass
    parent_template = environment.get_template('components/node/card.jinja', 'components/node_content/tiny_extends_card.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    l_0_sdoc_entity = (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)
    context.vars['sdoc_entity'] = l_0_sdoc_entity
    context.exported_vars.add('sdoc_entity')
    l_0_requirement_style = 'simple'
    context.vars['requirement_style'] = l_0_requirement_style
    context.exported_vars.add('requirement_style')
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
    template = environment.get_template('components/node_content/tiny.jinja', 'components/node_content/tiny_extends_card.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n'

blocks = {'sdoc_entity': block_sdoc_entity}
debug_info = '1=14&2=17&3=20&4=25&5=34'