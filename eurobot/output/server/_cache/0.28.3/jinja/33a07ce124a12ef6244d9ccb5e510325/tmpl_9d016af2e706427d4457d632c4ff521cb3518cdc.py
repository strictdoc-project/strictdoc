from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/document/create_requirement/stream_new_requirement.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_replace_action = resolve('replace_action')
    l_0_target_node_mid = resolve('target_node_mid')
    pass
    yield '\n\n<turbo-stream action="'
    yield escape((undefined(name='replace_action') if l_0_replace_action is missing else l_0_replace_action))
    yield '" target="article-'
    yield escape((undefined(name='target_node_mid') if l_0_target_node_mid is missing else l_0_target_node_mid))
    yield '">\n  <template>\n    '
    template = environment.get_template('screens/document/document/frame_requirement_form.jinja', 'actions/document/create_requirement/stream_new_requirement.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </template>\n</turbo-stream>'

blocks = {}
debug_info = '3=14&5=18'