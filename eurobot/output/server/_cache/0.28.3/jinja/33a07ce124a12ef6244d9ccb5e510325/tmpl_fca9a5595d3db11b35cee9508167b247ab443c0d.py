from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/document/_node_dispatch.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_node = resolve('node')
    pass
    if context.call(environment.getattr((undefined(name='node') if l_0_node is missing else l_0_node), 'is_document_node')):
        pass
        yield '\n  '
        template = environment.get_template('components/section/index_extends_node.jinja', 'screens/document/document/_node_dispatch.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    elif context.call(environment.getattr((undefined(name='node') if l_0_node is missing else l_0_node), 'is_content_node')):
        pass
        yield '\n  \n  \n    '
        template = environment.get_template('components/node_content/index_extends_node.jinja', 'screens/document/document/_node_dispatch.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  '
    else:
        pass
        yield '\n  '
        def macro():
            t_1 = []
            pass
            return concat(t_1)
        caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
        yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, False, 'Must not reach here.', caller=caller)

blocks = {}
debug_info = '1=12&2=15&3=21&8=24&11=34'