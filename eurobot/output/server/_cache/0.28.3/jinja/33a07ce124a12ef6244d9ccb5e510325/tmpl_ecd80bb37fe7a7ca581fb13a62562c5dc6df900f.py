from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/row/row_uid_with_reset/stream.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_uid_form_field = resolve('uid_form_field')
    l_0_reference_mid = resolve('reference_mid')
    l_0_namespace = resolve('namespace')
    l_0_text_field_row_context = l_0_row_context = missing
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='uid_form_field') if l_0_uid_form_field is missing else l_0_uid_form_field)), None, caller=caller)
    yield '\n'
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='reference_mid') if l_0_reference_mid is missing else l_0_reference_mid)), None, caller=caller)
    yield '\n\n'
    l_0_text_field_row_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace))
    context.vars['text_field_row_context'] = l_0_text_field_row_context
    context.exported_vars.add('text_field_row_context')
    yield '\n'
    l_0_row_context = (undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context)
    context.vars['row_context'] = l_0_row_context
    context.exported_vars.add('row_context')
    yield '\n\n\n\n'
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['errors'] = []
    yield '\n'
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['field'] = (undefined(name='uid_form_field') if l_0_uid_form_field is missing else l_0_uid_form_field)
    yield '\n'
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['field_editable'] = True
    yield '\n'
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['field_type'] = 'singleline'
    yield '\n'
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['reference_mid'] = (undefined(name='reference_mid') if l_0_reference_mid is missing else l_0_reference_mid)
    yield '\n\n<turbo-stream action="replace" target="uid_with_reset-'
    yield escape((undefined(name='reference_mid') if l_0_reference_mid is missing else l_0_reference_mid))
    yield '">\n  \n  <template>\n    <turbo-frame id="uid_with_reset-'
    yield escape((undefined(name='reference_mid') if l_0_reference_mid is missing else l_0_reference_mid))
    yield '">\n      '
    template = environment.get_template('components/form/row/row_uid_with_reset/frame.jinja', 'components/form/row/row_uid_with_reset/stream.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'row_context': l_0_row_context, 'text_field_row_context': l_0_text_field_row_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    </turbo-frame>\n  </template>\n</turbo-stream>'

blocks = {}
debug_info = '1=21&2=28&4=35&5=39&23=45&24=49&25=53&26=57&27=61&29=63&32=65&33=67'