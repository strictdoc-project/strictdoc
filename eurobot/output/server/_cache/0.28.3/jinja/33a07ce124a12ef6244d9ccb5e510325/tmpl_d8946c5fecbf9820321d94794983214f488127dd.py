from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/uid/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    pass
    if environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_uid'):
        pass
        yield '\n  <sdoc-node-uid>'
        l_1_field_content = environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_uid')
        pass
        template = environment.get_template('components/field/index.jinja', 'components/node_field/uid/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = missing
        yield '</sdoc-node-uid>'

blocks = {}
debug_info = '2=12&5=17'