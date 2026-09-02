from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/document/frame_section_form.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_form_object = resolve('form_object')
    l_0_is_new_section = resolve('is_new_section')
    l_0_submit_url = resolve('submit_url')
    l_0_cancel_url = resolve('cancel_url')
    l_0_frame_id = missing
    pass
    parent_template = environment.get_template('components/form/index.jinja', 'screens/document/document/frame_section_form.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    l_0_frame_id = markup_join(('article-', environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'section_mid'), ))
    context.vars['frame_id'] = l_0_frame_id
    context.exported_vars.add('frame_id')
    if (undefined(name='is_new_section') if l_0_is_new_section is missing else l_0_is_new_section):
        pass
        l_0_submit_url = '/actions/document/create_section'
        context.vars['submit_url'] = l_0_submit_url
        context.exported_vars.add('submit_url')
        l_0_cancel_url = markup_join(('/actions/document/cancel_new_section?section_mid=', environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'section_mid'), ))
        context.vars['cancel_url'] = l_0_cancel_url
        context.exported_vars.add('cancel_url')
    else:
        pass
        l_0_submit_url = '/actions/document/update_section'
        context.vars['submit_url'] = l_0_submit_url
        context.exported_vars.add('submit_url')
        l_0_cancel_url = markup_join(('/actions/document/cancel_edit_section?section_mid=', environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'section_mid'), ))
        context.vars['cancel_url'] = l_0_cancel_url
        context.exported_vars.add('cancel_url')
    yield from parent_template.root_render_func(context)

def block_form_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_is_new_section = resolve('is_new_section')
    l_0_reference_mid = resolve('reference_mid')
    l_0_whereto = resolve('whereto')
    l_0_form_object = resolve('form_object')
    l_0_namespace = resolve('namespace')
    l_0_text_field_row_context = missing
    pass
    yield '\n\n  '
    if (undefined(name='is_new_section') if l_0_is_new_section is missing else l_0_is_new_section):
        pass
        yield '<input type="hidden" id="reference_mid" name="reference_mid" value="'
        yield escape((undefined(name='reference_mid') if l_0_reference_mid is missing else l_0_reference_mid))
        yield '" />\n    <input type="hidden" id="whereto" name="whereto" value="'
        yield escape((undefined(name='whereto') if l_0_whereto is missing else l_0_whereto))
        yield '" />'
    yield '<input type="hidden" id="section_mid" name="section_mid" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'section_mid'))
    yield '" />\n  <input type="hidden" id="context_document_mid" name="context_document_mid" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'context_document_mid'))
    yield '" />\n\n  '
    l_0_text_field_row_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), _block_vars=_block_vars)
    _block_vars['text_field_row_context'] = l_0_text_field_row_context
    yield '\n\n  \n\n  '
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['errors'] = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), 'section_title', _block_vars=_block_vars)
    yield '\n  '
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['field'] = environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'section_title_field')
    yield '\n  '
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['field_editable'] = True
    yield '\n  '
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['field_type'] = 'singleline'
    yield '\n  '
    template = environment.get_template('components/form/row/row_with_text_field.jinja', 'screens/document/document/frame_section_form.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'text_field_row_context': l_0_text_field_row_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n\n  \n\n  '
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['errors'] = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), 'section_uid', _block_vars=_block_vars)
    yield '\n  '
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['field'] = environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'section_uid_field')
    yield '\n  '
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['field_editable'] = True
    yield '\n  '
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['field_type'] = 'singleline'
    yield '\n  '
    if not isinstance(l_0_text_field_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_text_field_row_context['reference_mid'] = environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'section_mid')
    if ((not (undefined(name='is_new_section') if l_0_is_new_section is missing else l_0_is_new_section)) and (environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'section_uid_field'), 'field_value') == '')):
        pass
        yield '<turbo-frame id="uid_with_reset-'
        yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'section_mid'))
        yield '">\n      \n      '
        template = environment.get_template('components/form/row/row_uid_with_reset/frame.jinja', 'screens/document/document/frame_section_form.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'text_field_row_context': l_0_text_field_row_context}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n    </turbo-frame>\n  '
    else:
        pass
        yield '\n    '
        template = environment.get_template('components/form/row/row_with_text_field.jinja', 'screens/document/document/frame_section_form.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'text_field_row_context': l_0_text_field_row_context}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  '
    yield '\n  \n\n'

blocks = {'form_content': block_form_content}
debug_info = '1=17&3=20&4=23&5=25&6=28&8=33&9=36&12=41&16=56&17=59&18=61&20=64&21=66&23=68&27=73&28=77&29=81&30=85&31=87&35=96&36=100&37=104&38=108&39=112&40=113&41=116&43=118&46=128'