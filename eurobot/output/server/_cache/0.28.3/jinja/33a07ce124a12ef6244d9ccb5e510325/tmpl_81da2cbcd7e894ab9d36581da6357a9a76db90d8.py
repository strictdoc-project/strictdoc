from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/document_title/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_local_anchor = missing
    pass
    l_0_local_anchor = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_local_anchor'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'))
    context.vars['local_anchor'] = l_0_local_anchor
    context.exported_vars.add('local_anchor')
    yield '\n<h1 data-testid="document-title">\n  '
    yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'title'))
    yield '\n  '
    template = environment.get_template('components/anchor_document/index.jinja', 'components/node_field/document_title/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'local_anchor': l_0_local_anchor}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n</h1>'

blocks = {}
debug_info = '1=13&3=17&4=19'