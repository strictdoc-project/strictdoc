from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/document/add_requirement_relation/stream_add_requirement_relation.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_namespace = resolve('namespace')
    l_0_field = resolve('field')
    l_0_form_object = resolve('form_object')
    l_0_relation_types = resolve('relation_types')
    l_0_requirement_mid = resolve('requirement_mid')
    l_0_relation_row_context = missing
    pass
    l_0_relation_row_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace))
    context.vars['relation_row_context'] = l_0_relation_row_context
    context.exported_vars.add('relation_row_context')
    yield '\n\n'
    if not isinstance(l_0_relation_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_relation_row_context['errors'] = []
    yield '\n'
    if not isinstance(l_0_relation_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_relation_row_context['field'] = (undefined(name='field') if l_0_field is missing else l_0_field)
    yield '\n'
    if not isinstance(l_0_relation_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_relation_row_context['form_object'] = (undefined(name='form_object') if l_0_form_object is missing else l_0_form_object)
    yield '\n'
    if not isinstance(l_0_relation_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_relation_row_context['relation_types'] = (undefined(name='relation_types') if l_0_relation_types is missing else l_0_relation_types)
    yield '\n\n<turbo-stream action="before" target="requirement_'
    yield escape((undefined(name='requirement_mid') if l_0_requirement_mid is missing else l_0_requirement_mid))
    yield '__new_relation">\n  <template>\n    '
    template = environment.get_template('components/form/row/row_with_relation.jinja', 'actions/document/add_requirement_relation/stream_add_requirement_relation.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'relation_row_context': l_0_relation_row_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </template>\n</turbo-stream>'

blocks = {}
debug_info = '1=17&3=23&4=27&5=31&6=35&8=37&10=39'