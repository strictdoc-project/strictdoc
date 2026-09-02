from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/section/pdf.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    pass
    yield '\n\n<sdoc-section>\n  \n  '
    template = environment.get_template('components/node_field/section_h/pdf.jinja', 'components/section/pdf.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    if context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'is_document_node')):
        pass
        l_1_document = (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity)
        pass
        yield '\n      '
        template = environment.get_template('components/node_field/document_meta/index.jinja', 'components/section/pdf.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_1_document}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_document = missing
    else:
        pass
        yield '\n    '
        template = environment.get_template('components/node_field/uid_standalone/index.jinja', 'components/section/pdf.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    yield '\n</sdoc-section>'

blocks = {}
debug_info = '13=13&14=19&16=24&19=34'