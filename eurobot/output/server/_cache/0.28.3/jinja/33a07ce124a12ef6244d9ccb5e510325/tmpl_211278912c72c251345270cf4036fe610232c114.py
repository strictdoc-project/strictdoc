from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/statement/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_view_object = resolve('view_object')
    l_0_truncated_statement = resolve('truncated_statement')
    try:
        t_1 = environment.tests['true']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'true' found.")
    pass
    if (context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'has_reserved_statement')) and context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'current_view'), 'includes_field'), environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'node_type'), context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_content_field_name')))):
        pass
        if t_1((undefined(name='truncated_statement') if l_0_truncated_statement is missing else l_0_truncated_statement)):
            pass
            yield '\n    <sdoc-node-field data-field-label="statement">\n      <sdoc-autogen>'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_truncated_node_statement'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity)))
            yield '</sdoc-autogen>\n    </sdoc-node-field>'
        else:
            pass
            yield '\n    <sdoc-node-field-label>'
            yield escape(context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_field_human_title_for_statement')))
            yield ':</sdoc-node-field-label>\n    <sdoc-node-field\n      data-field-label="statement"\n    >'
            l_1_field_content = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_statement'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity))
            pass
            template = environment.get_template('components/field/index.jinja', 'components/node_field/statement/index.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_1_field_content = missing
            yield '</sdoc-node-field>\n    '
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_issues'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), field='STATEMENT'))

blocks = {}
debug_info = '2=20&3=22&6=25&10=30&15=34&18=42'