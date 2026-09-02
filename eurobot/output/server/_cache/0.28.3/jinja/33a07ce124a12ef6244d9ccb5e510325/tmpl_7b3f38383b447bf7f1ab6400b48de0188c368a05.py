from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_content/card.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_requirement = resolve('requirement')
    l_0_requirement_style = l_0_sdoc_entity = missing
    pass
    yield '\n\n\n'
    l_0_requirement_style = 'simple'
    context.vars['requirement_style'] = l_0_requirement_style
    context.exported_vars.add('requirement_style')
    l_0_sdoc_entity = (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)
    context.vars['sdoc_entity'] = l_0_sdoc_entity
    context.exported_vars.add('sdoc_entity')
    template = environment.get_template('components/node_content/index.jinja', 'components/node_content/card.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'requirement_style': l_0_requirement_style, 'sdoc_entity': l_0_sdoc_entity}))
    try:
        for event in gen:
            yield event
    finally: gen.close()

blocks = {}
debug_info = '8=14&9=17&10=20'