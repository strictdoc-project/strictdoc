from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/row/row_with_metadata.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_custom_metadata_row_context = resolve('custom_metadata_row_context')
    l_0_row_context = l_0_form_object = missing
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
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context)), 'row_with_metadata: metadata_row_context must be defined.', caller=caller)
    if parent_template is None:
        yield '\n'
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'field')), 'row_with_metadata: field must be defined.', caller=caller)
    if parent_template is None:
        yield '\n'
    def macro():
        t_4 = []
        pass
        return concat(t_4)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'errors')), 'row_with_metadata: errors must be defined.', caller=caller)
    if parent_template is None:
        yield '\n'
    def macro():
        t_5 = []
        pass
        return concat(t_5)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'form_object')), 'row_with_metadata: form_object must be defined.', caller=caller)
    if parent_template is None:
        yield '\n\n'
    l_0_row_context = (undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context)
    context.vars['row_context'] = l_0_row_context
    context.exported_vars.add('row_context')
    l_0_form_object = (undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context)
    context.vars['form_object'] = l_0_form_object
    context.exported_vars.add('form_object')
    parent_template = environment.get_template('components/form/row/index.jinja', 'components/form/row/row_with_metadata.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    yield from parent_template.root_render_func(context)

def block_row_form_attributes(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_custom_metadata_row_context = resolve('custom_metadata_row_context')
    pass
    yield '\n  data-testid="document-config-form-metadata-row"\n  mid="'
    yield escape(environment.getattr(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'field'), 'field_mid'))
    yield '"\n'

def block_row_left(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_namespace = resolve('namespace')
    l_0_custom_metadata_row_context = resolve('custom_metadata_row_context')
    l_0_action_button_context = missing
    pass
    l_0_action_button_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), _block_vars=_block_vars)
    _block_vars['action_button_context'] = l_0_action_button_context
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_actions'] = {'move_down': True}
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_name'] = environment.getattr(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'field'), 'field_name')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_input_name'] = context.call(environment.getattr(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['mid'] = environment.getattr(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'field'), 'field_mid')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['testid_postfix'] = 'custom-field'
    template = environment.get_template('components/form/field_action_button/index.jinja', 'components/form/row/row_with_metadata.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_0_action_button_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), _block_vars=_block_vars)
    _block_vars['action_button_context'] = l_0_action_button_context
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_actions'] = {'move_up': True}
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_name'] = environment.getattr(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'field'), 'field_name')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_input_name'] = context.call(environment.getattr(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['mid'] = environment.getattr(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'field'), 'field_mid')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['testid_postfix'] = 'custom-field'
    template = environment.get_template('components/form/field_action_button/index.jinja', 'components/form/row/row_with_metadata.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()

def block_row_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_custom_metadata_row_context = resolve('custom_metadata_row_context')
    l_0_form_object = resolve('form_object')
    try:
        t_6 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    yield '\n\n<sdoc-form-field-group\n  data-field-label="Metadata"\n  '
    if t_6(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'errors')):
        pass
        yield 'errors="true"'
    yield '>'
    l_1_field_class_name = 'monospace'
    l_1_field_editable = True
    l_1_field_required = True
    l_1_field_input_name = context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    l_1_field_label = 'Name'
    l_1_field_placeholder = 'Enter name...'
    l_1_field_type = 'singleline'
    l_1_field_value = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_name')
    l_1_mid = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_mid')
    l_1_testid_postfix = context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    l_1_errors = environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'errors')
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/form/row/row_with_metadata.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_required': l_1_field_required, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_required = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_mid = l_1_testid_postfix = l_1_errors = missing
    l_1_field_class_name = 'monospace'
    l_1_field_editable = True
    l_1_field_required = False
    l_1_field_input_name = context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_value'), _block_vars=_block_vars)
    l_1_field_label = 'Value'
    l_1_field_placeholder = 'Enter value...'
    l_1_field_type = 'singleline'
    l_1_field_value = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_value')
    l_1_mid = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_mid')
    l_1_testid_postfix = context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_value'), _block_vars=_block_vars)
    l_1_errors = []
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/form/row/row_with_metadata.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_required': l_1_field_required, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_required = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_mid = l_1_testid_postfix = l_1_errors = missing
    yield '</sdoc-form-field-group>\n'

def block_row_right(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_namespace = resolve('namespace')
    l_0_custom_metadata_row_context = resolve('custom_metadata_row_context')
    l_0_action_button_context = missing
    pass
    l_0_action_button_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), _block_vars=_block_vars)
    _block_vars['action_button_context'] = l_0_action_button_context
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_actions'] = {'delete': True}
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_name'] = 'metadata'
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['mid'] = environment.getattr(environment.getattr((undefined(name='custom_metadata_row_context') if l_0_custom_metadata_row_context is missing else l_0_custom_metadata_row_context), 'field'), 'field_mid')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['testid_postfix'] = 'form-field-metadata'
    template = environment.get_template('components/form/field_action_button/index.jinja', 'components/form/row/row_with_metadata.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()

blocks = {'row_form_attributes': block_row_form_attributes, 'row_left': block_row_left, 'row_content': block_row_content, 'row_right': block_row_right}
debug_info = '1=20&2=28&3=36&4=44&7=52&9=55&11=58&13=63&15=73&18=76&19=87&20=91&21=94&22=97&23=100&24=103&25=104&27=110&28=114&29=117&30=120&31=123&32=126&33=127&36=134&40=151&57=167&73=186&79=195&81=206&82=210&83=213&84=216&85=219&86=220'