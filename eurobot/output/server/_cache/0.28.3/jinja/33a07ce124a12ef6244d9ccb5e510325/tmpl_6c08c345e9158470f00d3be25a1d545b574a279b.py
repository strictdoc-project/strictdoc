from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/multiline/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    pass
    yield '\n\n\n'
    if environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'has_meta'):
        pass
        yield '\n  '
        def t_1(fiter):
            l_1_view_object = resolve('view_object')
            for l_1_meta_field in fiter:
                if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_1_view_object is missing else l_1_view_object), 'current_view'), 'includes_field'), environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'node_type'), environment.getitem(l_1_meta_field, 0)):
                    yield l_1_meta_field
        for l_1_meta_field in t_1(context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'enumerate_meta_fields'), skip_single_lines=True)):
            l_1_view_object = resolve('view_object')
            _loop_vars = {}
            pass
            yield '\n    <sdoc-node-field-label>'
            yield escape(environment.getitem(l_1_meta_field, 0))
            yield ':</sdoc-node-field-label>\n    <sdoc-node-field\n      data-field-label="'
            yield escape(environment.getitem(l_1_meta_field, 0))
            yield '"\n    >'
            l_2_field_content = context.call(environment.getattr((undefined(name='view_object') if l_1_view_object is missing else l_1_view_object), 'render_node_field'), environment.getitem(l_1_meta_field, 1), _loop_vars=_loop_vars)
            pass
            template = environment.get_template('components/field/index.jinja', 'components/node_field/multiline/index.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_2_field_content, 'meta_field': l_1_meta_field}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_field_content = missing
            yield '</sdoc-node-field>\n    '
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_1_view_object is missing else l_1_view_object), 'render_issues'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), field=environment.getitem(l_1_meta_field, 0), _loop_vars=_loop_vars))
        l_1_meta_field = l_1_view_object = missing

blocks = {}
debug_info = '5=13&6=16&7=26&9=28&12=32&15=40'