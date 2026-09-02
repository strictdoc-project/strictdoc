from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node/root.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_view_object = resolve('view_object')
    l_0_copy_to_clipboard = missing
    pass
    yield '\n\n<turbo-frame id="article-'
    yield escape(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_mid'))
    yield '">\n\n  <sdoc-node\n    data-editable_node="on"\n    node-role="root"\n    data-testid="node-root"\n  >\n\n    '
    l_0_copy_to_clipboard = True
    context.vars['copy_to_clipboard'] = l_0_copy_to_clipboard
    context.exported_vars.add('copy_to_clipboard')
    yield '\n    '
    yield from context.blocks['sdoc_entity'][0](context)
    if ((not environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'section_contents')) and context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_type'), 'is_document'))):
        pass
        yield '<sdoc-main-placeholder data-testid="document-root-placeholder">\n        The document is empty.\n        <br/>Start adding text, sections, and requirements.\n      </sdoc-main-placeholder>'
    yield '\n    '
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
        pass
        yield '\n    '
        template = environment.get_template('components/node/node_controls/index.jinja', 'components/node/root.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'copy_to_clipboard': l_0_copy_to_clipboard}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n    '
    yield '\n\n  </sdoc-node>\n</turbo-frame>'

def block_sdoc_entity(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n    '

blocks = {'sdoc_entity': block_sdoc_entity}
debug_info = '7=15&20=17&23=21&26=22&34=26&35=29&23=38'