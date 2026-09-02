from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/text/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_view_object = resolve('view_object')
    pass
    if context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'has_reserved_statement')):
        pass
        yield '<sdoc-section-text>'
        l_1_field_content = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_statement'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity))
        pass
        template = environment.get_template('components/field/index.jinja', 'components/node_field/text/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = missing
        yield '</sdoc-section-text>'

blocks = {}
debug_info = '2=13&5=18'