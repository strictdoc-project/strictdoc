from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_meta_readonly_field.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_field_testid = resolve('field_testid')
    l_0_field_label = resolve('field_label')
    pass
    yield '<sdoc-meta-label data-testid="document-config-'
    yield escape((undefined(name='field_testid') if l_0_field_testid is missing else l_0_field_testid))
    yield '-label">'
    yield escape((undefined(name='field_label') if l_0_field_label is missing else l_0_field_label))
    yield ':</sdoc-meta-label>\n<sdoc-meta-field data-testid="document-config-'
    yield escape((undefined(name='field_testid') if l_0_field_testid is missing else l_0_field_testid))
    yield '-field">'
    template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'screens/document/table/field_display_mode/document_meta_readonly_field.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</sdoc-meta-field>'

blocks = {}
debug_info = '1=14&2=18&3=20'