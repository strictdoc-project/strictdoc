from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/row/row_uid_with_reset/example.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_namespace = resolve('namespace')
    l_0_form_object = resolve('form_object')
    l_0_text_field_row_context = missing
    pass
    yield '  '
    l_0_text_field_row_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace))
    context.vars['text_field_row_context'] = l_0_text_field_row_context
    context.exported_vars.add('text_field_row_context')
    yield '\n\n  '
    for l_1_field_values_ in context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'enumerate_fields'), multiline=False):
        _loop_vars = {}
        pass
        for l_2_field_ in l_1_field_values_:
            _loop_vars = {}
            pass
            if not isinstance(l_0_text_field_row_context, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_text_field_row_context['errors'] = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), environment.getattr(l_2_field_, 'field_name'), _loop_vars=_loop_vars)
            yield '\n      '
            if not isinstance(l_0_text_field_row_context, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_text_field_row_context['field'] = l_2_field_
            yield '\n      '
            if not isinstance(l_0_text_field_row_context, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_text_field_row_context['field_type'] = 'singleline'
            yield '\n      '
            if not isinstance(l_0_text_field_row_context, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_text_field_row_context['reference_mid'] = environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'requirement_mid')
            if ((environment.getattr(l_2_field_, 'field_name') == 'UID') and (environment.getattr(l_2_field_, 'field_value') == '')):
                pass
                yield '<turbo-frame id="uid_with_reset-'
                yield escape(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'reference_mid'))
                yield '">\n          \n          '
                template = environment.get_template('components/form/row/row_uid_with_reset/frame.jinja', 'components/form/row/row_uid_with_reset/example.jinja.html')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_': l_2_field_, 'field_values_': l_1_field_values_, 'text_field_row_context': l_0_text_field_row_context}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n        </turbo-frame>'
            else:
                pass
                template = environment.get_template('components/form/row/row_with_text_field.jinja', 'components/form/row/row_uid_with_reset/example.jinja.html')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_': l_2_field_, 'field_values_': l_1_field_values_, 'text_field_row_context': l_0_text_field_row_context}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
        l_2_field_ = missing
    l_1_field_values_ = missing

blocks = {}
debug_info = '1=15&4=19&5=22&6=27&7=31&8=35&9=39&10=40&11=43&13=45&16=54'