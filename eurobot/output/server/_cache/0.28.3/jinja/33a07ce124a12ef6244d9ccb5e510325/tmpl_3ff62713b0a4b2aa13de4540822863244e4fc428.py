from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/row/row_uid_with_reset/frame.jinja'

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
    parent_template = environment.get_template('components/form/row/index.jinja', 'components/form/row/row_uid_with_reset/frame.jinja')
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
    def macro():
        t_7 = []
        pass
        return concat(t_7)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'reference_mid')), 'row_with_text: reference_mid must be defined.', caller=caller)
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
    l_0_placeholder_name = missing
    try:
        t_8 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_8(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    if (t_8(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors')) > 0):
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
    l_1_mid = environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_mid')
    l_1_field_class_name = None
    l_1_field_editable = environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field_editable')
    l_1_field_input_name = context.call(environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    l_1_field_label = environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_name')
    l_1_field_placeholder = markup_join(('Enter ', (undefined(name='placeholder_name') if l_0_placeholder_name is missing else l_0_placeholder_name), ' here...', ))
    l_1_field_type = environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field_type')
    l_1_field_value = environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_value')
    l_1_testid_postfix = environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_name')
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/form/row/row_uid_with_reset/frame.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix, 'placeholder_name': l_0_placeholder_name}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_mid = l_1_field_class_name = l_1_field_editable = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_testid_postfix = missing
    yield '<input\n    type="hidden"\n    name="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'get_input_field_type_name'), _block_vars=_block_vars))
    yield '"\n    value="'
    yield escape(environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_name'))
    yield '"\n  />\n'

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
    if (t_1(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'uid_restore_available')) and environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'uid_restore_available')):
        pass
        yield '<a\n      class="field_action"\n      href="#"\n      title="Restore UID"\n      data-action-type="restore"\n      data-js-restore-field-action\n      data-restore-value="'
        yield escape(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'existing_requirement_uid'))
        yield '"\n      data-testid="restore-uid-field-action"\n    >'
        template = environment.get_template('icons/ico16_restore.svg', 'components/form/row/row_uid_with_reset/frame.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</a>'
    yield '<a\n      class="field_action"\n      href="/reset_uid?reference_mid='
    yield escape(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'reference_mid'))
    yield '"\n      mid="'
    yield escape(environment.getattr(environment.getattr((undefined(name='text_field_row_context') if l_0_text_field_row_context is missing else l_0_text_field_row_context), 'field'), 'field_mid'))
    yield '"\n      title="Generate default UID"\n      data-action-type="reset"\n      data-turbo-action="replace"\n      data-turbo="true"\n      data-testid="reset-uid-field-action"\n    >'
    template = environment.get_template('icons/ico16_reset.svg', 'components/form/row/row_uid_with_reset/frame.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</a>\n'

blocks = {'row_form_attributes': block_row_form_attributes, 'row_left': block_row_left, 'row_content': block_row_content, 'row_right': block_row_right}
debug_info = '1=20&3=23&5=29&6=35&7=41&8=47&9=53&11=59&14=62&16=67&20=77&24=87&26=104&27=106&29=110&34=113&47=125&52=133&53=135&57=138&58=153&68=156&70=158&74=166&75=168&81=170'