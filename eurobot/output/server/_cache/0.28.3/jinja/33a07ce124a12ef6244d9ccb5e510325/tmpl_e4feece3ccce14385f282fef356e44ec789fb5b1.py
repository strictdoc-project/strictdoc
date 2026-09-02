from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/row/row_with_comment.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_comment_field_row_context = resolve('comment_field_row_context')
    l_0_row_context = l_0_form_object = missing
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    parent_template = environment.get_template('components/form/row/index.jinja', 'components/form/row/row_with_comment.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context)), 'row_with_comment: row_context must be defined.', caller=caller)
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'errors')), 'row_with_comment: errors must be defined.', caller=caller)
    def macro():
        t_4 = []
        pass
        return concat(t_4)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field')), 'row_with_comment: field must be defined.', caller=caller)
    l_0_row_context = (undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context)
    context.vars['row_context'] = l_0_row_context
    context.exported_vars.add('row_context')
    if not isinstance(l_0_row_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_row_context['field_actions'] = {'delete': True}
    l_0_form_object = (undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context)
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
    l_0_comment_field_row_context = resolve('comment_field_row_context')
    pass
    yield '\n  data-testid="requirement-form-comment-row"\n  mid="'
    yield escape(environment.getattr(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field'), 'field_mid'))
    yield '"\n'

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
    l_0_comment_field_row_context = resolve('comment_field_row_context')
    try:
        t_5 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    if (t_5(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors')) > 0):
        pass
        for l_1_error_ in environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors'):
            _loop_vars = {}
            pass
            yield '<sdoc-form-error>\n      '
            yield escape(l_1_error_)
            yield '\n    </sdoc-form-error>'
        l_1_error_ = missing
    l_1_field_class_name = None
    l_1_field_editable = environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field_editable')
    l_1_field_input_name = context.call(environment.getattr(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field'), 'get_input_field_name'), _block_vars=_block_vars)
    l_1_field_label = environment.getattr(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field'), 'field_name')
    l_1_field_placeholder = 'Enter comment here...'
    l_1_field_type = 'multiline'
    l_1_field_value = environment.getattr(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field'), 'field_value')
    l_1_mid = environment.getattr(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field'), 'field_mid')
    l_1_testid_postfix = 'COMMENT'
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/form/row/row_with_comment.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_mid = l_1_testid_postfix = missing
    yield '<input\n    type="hidden"\n    name="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field'), 'get_input_field_type_name'), _block_vars=_block_vars))
    yield '"\n    value="'
    yield escape(environment.getattr(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field'), 'field_name'))
    yield '"\n  />\n\n'

def block_row_right(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_namespace = resolve('namespace')
    l_0_comment_field_row_context = resolve('comment_field_row_context')
    l_0_action_button_context = missing
    pass
    l_0_action_button_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), _block_vars=_block_vars)
    _block_vars['action_button_context'] = l_0_action_button_context
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_actions'] = {'delete': True}
    yield '\n  '
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_name'] = 'requirement comment'
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['mid'] = environment.getattr(environment.getattr((undefined(name='comment_field_row_context') if l_0_comment_field_row_context is missing else l_0_comment_field_row_context), 'field'), 'field_mid')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['testid_postfix'] = 'comment'
    template = environment.get_template('components/form/field_action_button/index.jinja', 'components/form/row/row_with_comment.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()

blocks = {'row_form_attributes': block_row_form_attributes, 'row_left': block_row_left, 'row_content': block_row_content, 'row_right': block_row_right}
debug_info = '1=20&3=23&5=29&6=35&8=41&9=46&12=47&14=52&16=62&19=65&23=75&24=91&25=93&27=97&42=110&47=118&48=120&53=123&55=134&56=138&58=142&59=145&60=148&61=149'