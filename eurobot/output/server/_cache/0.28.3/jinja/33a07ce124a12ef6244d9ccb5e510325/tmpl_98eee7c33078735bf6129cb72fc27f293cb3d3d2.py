from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/document/frame_document_content.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<turbo-frame id="frame_document_content">\n      <div\n        class="content"\n      >\n        \n        \n\n        '
    template = environment.get_template('screens/document/document/frame_document_config.jinja.html', 'screens/document/document/frame_document_content.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_chunked_rendering')):
        pass
        l_1_loop = missing
        for l_1_chunk, l_1_loop in LoopContext(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_content_chunks')), undefined):
            _loop_vars = {}
            pass
            if environment.getattr(l_1_loop, 'first'):
                pass
                l_2_chunk_index = environment.getattr(l_1_chunk, 'index')
                l_2_from_node = environment.getattr(l_1_chunk, 'first_node_mid')
                l_2_count = environment.getattr(l_1_chunk, 'size')
                pass
                yield '\n                '
                template = environment.get_template('screens/document/document/document_chunk.jinja.html', 'screens/document/document/frame_document_content.jinja.html')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'chunk_index': l_2_chunk_index, 'count': l_2_count, 'from_node': l_2_from_node, 'chunk': l_1_chunk, 'loop': l_1_loop}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_chunk_index = l_2_from_node = l_2_count = missing
            else:
                pass
                if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
                    pass
                    yield '\n                '
                    template = environment.get_template('screens/document/document/document_chunk_lazy_placeholder.jinja.html', 'screens/document/document/frame_document_content.jinja.html')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'chunk': l_1_chunk, 'loop': l_1_loop}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                else:
                    pass
                    yield '\n                '
                    template = environment.get_template('screens/document/document/document_chunk_lazy_placeholder_static.jinja.html', 'screens/document/document/frame_document_content.jinja.html')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'chunk': l_1_chunk, 'loop': l_1_loop}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
        l_1_loop = l_1_chunk = missing
    else:
        pass
        for (l_1_node, l_1__) in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_content_iterator')):
            _loop_vars = {}
            pass
            template = environment.get_template('screens/document/document/_node_dispatch.jinja.html', 'screens/document/document/frame_document_content.jinja.html')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'node': l_1_node}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
        l_1_node = l_1__ = missing
    yield '\n\n      </div>\n</turbo-frame>'

blocks = {}
debug_info = '8=13&10=19&11=22&12=25&14=32&17=41&18=44&20=53&26=62&27=65'