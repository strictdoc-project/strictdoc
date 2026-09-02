from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/grammar_form_element/row_with_custom_field/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_form_object = resolve('form_object')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    parent_template = environment.get_template('components/form/row/index.jinja', 'components/grammar_form_element/row_with_custom_field/index.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object)), 'form_object must be defined.', caller=caller)
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors')), 'form_object: errors must be defined.', caller=caller)
    def macro():
        t_4 = []
        pass
        return concat(t_4)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field')), 'form_object: field must be defined.', caller=caller)
    yield from parent_template.root_render_func(context)

def block_row_form_attributes(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n'

def block_row_left(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_namespace = resolve('namespace')
    l_0_form_object = resolve('form_object')
    l_0_action_button_context = missing
    pass
    l_0_action_button_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), _block_vars=_block_vars)
    _block_vars['action_button_context'] = l_0_action_button_context
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_actions'] = {'move_down': True}
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_name'] = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_name')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_input_name'] = context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['mid'] = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_mid')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['testid_postfix'] = 'custom-field'
    template = environment.get_template('components/form/field_action_button/index.jinja', 'components/grammar_form_element/row_with_custom_field/index.jinja')
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
    l_0_action_button_context['field_name'] = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_name')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_input_name'] = context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['mid'] = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_mid')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['testid_postfix'] = 'custom-field'
    template = environment.get_template('components/form/field_action_button/index.jinja', 'components/grammar_form_element/row_with_custom_field/index.jinja')
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
    l_0_form_object = resolve('form_object')
    l_0__name_errors = l_0__human_name_errors = l_0_placeholder_name = l_0_human_title_value = missing
    try:
        t_5 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    try:
        t_6 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    l_0__name_errors = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_name'), _block_vars=_block_vars), _block_vars=_block_vars)
    _block_vars['_name_errors'] = l_0__name_errors
    l_0__human_name_errors = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_human_title'), _block_vars=_block_vars), _block_vars=_block_vars)
    _block_vars['_human_name_errors'] = l_0__human_name_errors
    yield '\n<sdoc-form-field-group\n  data-field-label="Custom field"\n  '
    if (t_6((undefined(name='_name_errors') if l_0__name_errors is missing else l_0__name_errors)) or t_6((undefined(name='_human_name_errors') if l_0__human_name_errors is missing else l_0__human_name_errors))):
        pass
        yield 'errors="true"'
    yield '>\n\n  \n  <input\n    type="hidden"\n    value="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_required_value'), _block_vars=_block_vars))
    yield '"\n    name="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_required'), _block_vars=_block_vars))
    yield '"\n  />'
    l_0_placeholder_name = t_5(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_name'), 'custom field name', True)
    _block_vars['placeholder_name'] = l_0_placeholder_name
    yield '\n  '
    l_1_field_class_name = 'monospace'
    l_1_field_editable = True
    l_1_field_required = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_required')
    l_1_field_input_name = context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    l_1_field_label = 'Field name'
    l_1_field_placeholder = 'Enter field name here...'
    l_1_field_type = 'singleline'
    l_1_field_value = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_name')
    l_1_mid = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_mid')
    l_1_testid_postfix = 'reserved_field_name'
    l_1_errors = (undefined(name='_name_errors') if l_0__name_errors is missing else l_0__name_errors)
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/grammar_form_element/row_with_custom_field/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_required': l_1_field_required, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix, '_human_name_errors': l_0__human_name_errors, '_name_errors': l_0__name_errors, 'human_title_value': l_0_human_title_value, 'placeholder_name': l_0_placeholder_name}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_required = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_mid = l_1_testid_postfix = l_1_errors = missing
    l_0_human_title_value = (environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_human_title') if environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_human_title') else '')
    _block_vars['human_title_value'] = l_0_human_title_value
    l_1_field_class_name = 'monospace'
    l_1_field_editable = True
    l_1_field_required = False
    l_1_field_input_name = context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_human_title'), _block_vars=_block_vars)
    l_1_field_label = 'Field human name'
    l_1_field_placeholder = 'Enter human readable field name here...'
    l_1_field_type = 'singleline'
    l_1_field_value = (undefined(name='human_title_value') if l_0_human_title_value is missing else l_0_human_title_value)
    l_1_mid = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_mid')
    l_1_testid_postfix = 'reserved_field_human_title'
    l_1_errors = (undefined(name='_human_name_errors') if l_0__human_name_errors is missing else l_0__human_name_errors)
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/grammar_form_element/row_with_custom_field/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_required': l_1_field_required, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix, '_human_name_errors': l_0__human_name_errors, '_name_errors': l_0__name_errors, 'human_title_value': l_0_human_title_value, 'placeholder_name': l_0_placeholder_name}))
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
    l_0_form_object = resolve('form_object')
    l_0_action_button_context = missing
    pass
    l_0_action_button_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), _block_vars=_block_vars)
    _block_vars['action_button_context'] = l_0_action_button_context
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_actions'] = {'delete': True}
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_name'] = 'custom field'
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['mid'] = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'field_mid')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['testid_postfix'] = 'custom-field'
    template = environment.get_template('components/form/field_action_button/index.jinja', 'components/grammar_form_element/row_with_custom_field/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()

blocks = {'row_form_attributes': block_row_form_attributes, 'row_left': block_row_left, 'row_content': block_row_content, 'row_right': block_row_right}
debug_info = '1=19&3=22&4=28&5=34&7=42&10=52&11=63&12=67&13=70&14=73&15=76&16=79&17=80&19=86&20=90&21=93&22=96&23=99&24=102&25=103&28=110&30=132&31=134&34=137&42=141&43=143&46=145&61=160&63=167&77=181&82=190&84=201&85=205&86=208&87=211&88=214&89=215'