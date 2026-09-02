from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/document/edit_section/stream_updated_section.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_node = resolve('node')
    pass
    yield '<turbo-stream action="replace" target="article-'
    yield escape(environment.getattr((undefined(name='node') if l_0_node is missing else l_0_node), 'reserved_mid'))
    yield '">\n  <template>\n    '
    template = environment.get_template('components/section/index_extends_node.jinja', 'actions/document/edit_section/stream_updated_section.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </template>\n</turbo-stream>'

blocks = {}
debug_info = '1=13&3=15'