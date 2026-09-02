from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/update_node_comments/stream_update.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_node_mid = resolve('node_mid')
    l_0_rendered_comments = resolve('rendered_comments')
    pass
    yield '<turbo-stream action="update" target="cell-'
    yield escape((undefined(name='node_mid') if l_0_node_mid is missing else l_0_node_mid))
    yield '-COMMENT">\n  <template>'
    for l_1_rendered_comment in (undefined(name='rendered_comments') if l_0_rendered_comments is missing else l_0_rendered_comments):
        _loop_vars = {}
        pass
        l_2_field_content = l_1_rendered_comment
        pass
        template = environment.get_template('screens/document/table/field_display_mode/comment.jinja', 'actions/table/update_node_comments/stream_update.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_2_field_content, 'rendered_comment': l_1_rendered_comment}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_2_field_content = missing
    l_1_rendered_comment = missing
    yield '</template>\n</turbo-stream>\n<turbo-stream action="update" target="modal">\n  <template></template>\n</turbo-stream>'

blocks = {}
debug_info = '1=14&3=16&5=21'