from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/row/row_with_text_field.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_text_field_row_context = resolve('text_field_row_context')
    l_0_row_context = l_0_form_object = missing
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    parent_template = environment.get_template('components/form/row/index.jinja', 'components/form/row/row_with_text_field.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context)), 'row_with_text: row_context must be defined.', caller=caller)
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'errors')), 'row_with_text: errors must be defined.', caller=caller)
    def macro():
        t_4 = []
        pass
        return concat(t_4)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field')), 'row_with_text: field must be defined.', caller=caller)
    def macro():
        t_5 = []
        pass
        return concat(t_5)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field_type')), 'row_with_text: field_type must be defined.', caller=caller)
    def macro():
        t_6 = []
        pass
        return concat(t_6)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, (environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field_type') in ('singleline', 'multiline')), 'row_with_text: field_type must be singleline or multiline.', caller=caller)
    l_0_row_context = (undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context)
    context.vars['row_context'] = l_0_row_context
    context.exported_vars.add('row_context')
    l_0_form_object = (undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context)
    context.vars['form_object'] = l_0_form_object
    context.exported_vars.add('form_object')
    yield from parent_template.root_render_func(context)

def block_row_form_attributes(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n\n'

def block_row_left(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n  \n'

def block_row_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_form_object = resolve('form_object')
    l_0_text_field_row_context = resolve('text_field_row_context')
    l_0_placeholder_name = l_0_field_name = missing
    try:
        t_7 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    if (t_7(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors')) > 0):
        pass
        for l_1_error_ in environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors'):
            _loop_vars = {}
            pass
            yield '<sdoc-form-error>\n      '
            yield escape(l_1_error_)
            yield '\n    </sdoc-form-error>'
        l_1_error_ = missing
    l_0_placeholder_name = environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_name')
    _block_vars['placeholder_name'] = l_0_placeholder_name
    l_0_field_name = environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_name')
    _block_vars['field_name'] = l_0_field_name
    if (not environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field_editable')):
        pass
        l_0_field_name = markup_join(((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name), ' (READ-ONLY)', ))
        _block_vars['field_name'] = l_0_field_name
    l_1_document_mid = resolve('document_mid')
    l_1_element_type = resolve('element_type')
    l_1_mid = environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_mid')
    l_1_field_class_name = None
    l_1_field_editable = environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field_editable')
    l_1_field_input_name = context.call(environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    l_1_field_label = (undefined(name='field_name') if l_0_field_name is missing else l_0_field_name)
    l_1_field_placeholder = markup_join(('Enter ', (undefined(name='placeholder_name') if l_0_placeholder_name is missing else l_0_placeholder_name), ' here...', ))
    l_1_field_type = environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field_type')
    l_1_field_value = environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_value')
    l_1_testid_postfix = environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_name')
    pass
    if context.call(environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'is_autocompletable')):
        pass
        l_2_autocomplete_url = markup_join(('/autocomplete/field?document_mid=', (undefined(name='document_mid') if l_1_document_mid is missing else l_1_document_mid), '&element_type=', (undefined(name='element_type') if l_1_element_type is missing else l_1_element_type), '&field_name=', l_1_field_label, ))
        l_2_result_class_name = 'requirement__link'
        l_2_autocomplete_len = '0'
        l_2_autocomplete_multiplechoice = context.call(environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'is_multiplechoice'))
        pass
        template = environment.get_template('components/form/field/autocompletable/index.jinja', 'components/form/row/row_with_text_field.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'autocomplete_len': l_2_autocomplete_len, 'autocomplete_multiplechoice': l_2_autocomplete_multiplechoice, 'autocomplete_url': l_2_autocomplete_url, 'result_class_name': l_2_result_class_name, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix, 'field_name': l_0_field_name, 'placeholder_name': l_0_placeholder_name}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_2_autocomplete_url = l_2_result_class_name = l_2_autocomplete_len = l_2_autocomplete_multiplechoice = missing
    else:
        pass
        template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/form/row/row_with_text_field.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix, 'field_name': l_0_field_name, 'placeholder_name': l_0_placeholder_name}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    l_1_mid = l_1_field_class_name = l_1_field_editable = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_testid_postfix = l_1_document_mid = l_1_element_type = missing
    yield '<input\n    type="hidden"\n    name="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'get_input_field_type_name'), _block_vars=_block_vars))
    yield '"\n    value="'
    yield escape(environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_name'))
    yield '"\n  />\n\n'

def block_row_right(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_text_field_row_context = resolve('text_field_row_context')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    if (((environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_name') == 'UID') and t_1(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'uid_restore_available'))) and environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'uid_restore_available')):
        pass
        yield '<a\n      class="field_action"\n      href="#"\n      title="Restore UID"\n      data-action-type="restore"\n      data-js-restore-field-action\n      data-restore-value="'
        yield escape(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'existing_requirement_uid'))
        yield '"\n      data-testid="restore-uid-field-action"\n    >'
        template = environment.get_template('icons/ico16_restore.svg', 'components/form/row/row_with_text_field.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</a>'

blocks = {'row_form_attributes': block_row_form_attributes, 'row_left': block_row_left, 'row_content': block_row_content, 'row_right': block_row_right}
debug_info = '1=20&3=23&4=29&5=35&6=41&7=47&9=53&11=56&13=61&17=71&21=81&23=98&24=100&26=104&31=107&33=109&34=111&35=113&49=127&58=134&61=143&67=151&68=153&73=156&74=171&85=174&87=176'