from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/grammar_form_element/row_with_reserved_field/index.jinja'

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
    parent_template = environment.get_template('components/form/row/index.jinja', 'components/grammar_form_element/row_with_reserved_field/index.jinja')
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
    yield '\n  data-controller=""\n'

def block_row_left(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n\n'

def block_row_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_form_object = resolve('form_object')
    l_0__name_errors = l_0__human_name_errors = l_0_human_title_value = missing
    try:
        t_5 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    l_0__name_errors = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_name'), _block_vars=_block_vars), _block_vars=_block_vars)
    _block_vars['_name_errors'] = l_0__name_errors
    l_0__human_name_errors = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_human_title'), _block_vars=_block_vars), _block_vars=_block_vars)
    _block_vars['_human_name_errors'] = l_0__human_name_errors
    yield '\n<sdoc-form-field-group\n  data-field-label="Reserved field"\n  '
    if (t_5((undefined(name='_name_errors') if l_0__name_errors is missing else l_0__name_errors)) or t_5((undefined(name='_human_name_errors') if l_0__human_name_errors is missing else l_0__human_name_errors))):
        pass
        yield 'errors="true"'
    yield '>\n\n  \n  <input\n    type="hidden"\n    value="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_required_value'), _block_vars=_block_vars))
    yield '"\n    name="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'field'), 'get_input_field_required'), _block_vars=_block_vars))
    yield '"\n  />'
    l_1_field_class_name = 'monospace'
    l_1_field_editable = False
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
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/grammar_form_element/row_with_reserved_field/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_required': l_1_field_required, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix, '_human_name_errors': l_0__human_name_errors, '_name_errors': l_0__name_errors, 'human_title_value': l_0_human_title_value}))
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
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/grammar_form_element/row_with_reserved_field/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_required': l_1_field_required, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix, '_human_name_errors': l_0__human_name_errors, '_name_errors': l_0__name_errors, 'human_title_value': l_0_human_title_value}))
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
    pass
    yield '\n\n'

blocks = {'row_form_attributes': block_row_form_attributes, 'row_left': block_row_left, 'row_content': block_row_content, 'row_right': block_row_right}
debug_info = '1=19&3=22&4=28&5=34&7=42&11=52&15=62&17=78&18=80&21=83&29=87&30=89&46=103&48=110&62=124&67=133'