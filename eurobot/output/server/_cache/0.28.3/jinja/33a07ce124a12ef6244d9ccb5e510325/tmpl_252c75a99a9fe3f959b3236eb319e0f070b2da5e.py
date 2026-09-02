from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/document/frame_document_config.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_view_object = resolve('view_object')
    l_0_sdoc_entity = missing
    pass
    parent_template = environment.get_template('components/node/root.jinja', 'screens/document/document/frame_document_config.jinja.html')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    l_0_sdoc_entity = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document')
    context.vars['sdoc_entity'] = l_0_sdoc_entity
    context.exported_vars.add('sdoc_entity')
    yield from parent_template.root_render_func(context)

def block_sdoc_entity(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n\n  '
    template = environment.get_template('components/node_field/document_title/index.jinja', 'screens/document/document/frame_document_config.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  '
    template = environment.get_template('components/node_field/document_meta/index.jinja', 'screens/document/document/frame_document_config.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n\n'

blocks = {'sdoc_entity': block_sdoc_entity}
debug_info = '1=14&2=17&3=22&5=31&6=38'