from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/document/document_chunk.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_chunk_index = resolve('chunk_index')
    l_0_view_object = resolve('view_object')
    l_0_from_node = resolve('from_node')
    l_0_count = resolve('count')
    pass
    yield '<turbo-frame id="document-chunk-'
    yield escape((undefined(name='chunk_index') if l_0_chunk_index is missing else l_0_chunk_index))
    yield '">'
    for (l_1_node, l_1__) in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_chunk_content_iterator'), (undefined(name='from_node') if l_0_from_node is missing else l_0_from_node), (undefined(name='count') if l_0_count is missing else l_0_count)):
        _loop_vars = {}
        pass
        template = environment.get_template('screens/document/document/_node_dispatch.jinja.html', 'screens/document/document/document_chunk.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'node': l_1_node}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    l_1_node = l_1__ = missing
    yield '\n</turbo-frame>'

blocks = {}
debug_info = '1=16&2=18&3=21'