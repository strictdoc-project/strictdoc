from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/comments/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_sdoc_entity = resolve('sdoc_entity')
    pass
    yield '\n\n\n'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'current_view'), 'includes_field'), environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'node_type'), 'COMMENT'):
        pass
        for l_1_comment_field_ in context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_comment_fields')):
            _loop_vars = {}
            pass
            yield '\n    <sdoc-node-field-label>'
            yield escape(context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_field_human_title'), 'COMMENT', _loop_vars=_loop_vars))
            yield ':</sdoc-node-field-label>\n    <sdoc-node-field\n      data-field-label="comment"\n    >'
            l_2_field_content = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_field'), l_1_comment_field_, _loop_vars=_loop_vars)
            pass
            template = environment.get_template('components/field/index.jinja', 'components/node_field/comments/index.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_2_field_content, 'comment_field_': l_1_comment_field_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_field_content = missing
            yield '</sdoc-node-field>'
        l_1_comment_field_ = missing
        yield '\n  '
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_issues'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), field='COMMENT'))

blocks = {}
debug_info = '4=14&5=16&6=20&11=24&15=34'