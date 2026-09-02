from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/document/edit_document_config/stream_save_document_config.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<turbo-stream action="replace" target="article-'
    yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'reserved_mid'))
    yield '">\n  <template>\n    '
    template = environment.get_template('screens/document/document/frame_document_config.jinja.html', 'actions/document/edit_document_config/stream_save_document_config.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </template>\n</turbo-stream>\n<turbo-stream action="replace" target="header_document_title">\n  <template>\n    '
    template = environment.get_template('screens/document/_shared/frame_header_document_title.jinja', 'actions/document/edit_document_config/stream_save_document_config.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </template>\n</turbo-stream>\n<turbo-stream action="update" target="frame_aside_project_tree">\n  <template>\n    '
    template = environment.get_template('screens/document/_shared/project_tree.jinja', 'actions/document/edit_document_config/stream_save_document_config.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </template>\n</turbo-stream>'

blocks = {}
debug_info = '1=13&3=15&8=22&13=29'