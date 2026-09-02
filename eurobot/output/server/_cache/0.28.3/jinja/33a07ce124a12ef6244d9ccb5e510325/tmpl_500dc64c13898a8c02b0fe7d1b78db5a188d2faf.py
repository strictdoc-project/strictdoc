from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/row/row_with_relation.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_relation_row_context = resolve('relation_row_context')
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
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context)), 'row_with_relation: relation_row_context must be defined.', caller=caller)
    if parent_template is None:
        yield '\n'
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'errors')), 'row_with_relation: errors must be defined.', caller=caller)
    if parent_template is None:
        yield '\n'
    def macro():
        t_4 = []
        pass
        return concat(t_4)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field')), 'row_with_relation: field must be defined.', caller=caller)
    if parent_template is None:
        yield '\n'
    def macro():
        t_5 = []
        pass
        return concat(t_5)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'relation_types')), 'row_with_relation: relation_types must be defined.', caller=caller)
    if parent_template is None:
        yield '\n'
    def macro():
        t_6 = []
        pass
        return concat(t_6)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'form_object')), 'row_with_relation: form_object must be defined.', caller=caller)
    if parent_template is None:
        yield '\n\n'
    l_0_row_context = (undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context)
    context.vars['row_context'] = l_0_row_context
    context.exported_vars.add('row_context')
    l_0_form_object = (undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context)
    context.vars['form_object'] = l_0_form_object
    context.exported_vars.add('form_object')
    parent_template = environment.get_template('components/form/row/index.jinja', 'components/form/row/row_with_relation.jinja')
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
    l_0_relation_row_context = resolve('relation_row_context')
    pass
    yield '\n  data-testid="requirement-form-relation-row"\n  mid="'
    yield escape(environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_mid'))
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
    l_0_relation_row_context = resolve('relation_row_context')
    l_0_form_object = resolve('form_object')
    l_0_requirement_mid = resolve('requirement_mid')
    try:
        t_7 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_8 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_8(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '\n\n\n<input type="hidden"\n  name="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'get_is_new_field_name'), _block_vars=_block_vars))
    yield '"\n  value="'
    yield escape(('true' if environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'is_new') else 'false'))
    yield '"\n/>\n\n<sdoc-form-field-group\n  data-field-label="Node relation"\n  '
    if t_7(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors')):
        pass
        yield 'errors="true"'
    yield '>'
    if (t_7(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors')) > 0):
        pass
        for l_1_error_ in environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors'):
            _loop_vars = {}
            pass
            yield '<sdoc-form-error>\n      '
            yield escape(l_1_error_)
            yield '\n    </sdoc-form-error>'
        l_1_error_ = missing
    if (environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_type') == 'File'):
        pass
        yield '\n    <sdoc-form-error>\n      Warning: Editing file relations is not supported yet.\n    </sdoc-form-error>\n  '
    l_1_field_class_name = None
    l_1_result_class_name = 'requirement__link'
    l_1_field_editable = (True if (environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_type') != 'File') else False)
    l_1_field_label = ('Relation UID' if (environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_type') != 'File') else 'Path to file')
    l_1_field_input_name = context.call(environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'get_value_field_name'), _block_vars=_block_vars)
    l_1_field_placeholder = 'Enter relation UID...'
    l_1_field_type = 'singleline'
    l_1_field_value = environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_value')
    l_1_mid = environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_mid')
    l_1_autocomplete_url = markup_join(('/autocomplete/uid?exclude_requirement_mid=', (undefined(name='requirement_mid') if l_0_requirement_mid is missing else l_0_requirement_mid), ))
    l_1_autocomplete_len = '2'
    l_1_autocomplete_multiplechoice = False
    l_1_testid_postfix = 'relation-uid'
    pass
    template = environment.get_template('components/form/field/autocompletable/index.jinja', 'components/form/row/row_with_relation.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'autocomplete_len': l_1_autocomplete_len, 'autocomplete_multiplechoice': l_1_autocomplete_multiplechoice, 'autocomplete_url': l_1_autocomplete_url, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'result_class_name': l_1_result_class_name, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_result_class_name = l_1_field_editable = l_1_field_label = l_1_field_input_name = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_mid = l_1_autocomplete_url = l_1_autocomplete_len = l_1_autocomplete_multiplechoice = l_1_testid_postfix = missing
    yield '<sdoc-form-field field-type="select">\n    <label for="relation_typerole_'
    yield escape(environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_mid'))
    yield '">Relation type</label>\n    <select\n      data-testid="select-relation-typerole"\n      name="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'get_type_field_name'), _block_vars=_block_vars))
    yield '"\n      id="relation_typerole_'
    yield escape(environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_mid'))
    yield '"\n      mid="'
    yield escape(environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_mid'))
    yield '"\n      '
    if (environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_type') == 'File'):
        pass
        yield '\n        disabled\n      '
    yield '\n    >\n      '
    for (l_1_relation_type_, l_1_relation_role_, l_1_is_current_relation_) in context.call(environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'form_object'), 'enumerate_relation_roles'), environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), _block_vars=_block_vars):
        _loop_vars = {}
        pass
        if ((environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_type') != 'File') and (l_1_relation_type_ == 'File')):
            pass
        elif (not t_8(l_1_relation_role_)):
            pass
            yield '\n          <option\n            value="'
            yield escape(l_1_relation_type_)
            yield ','
            yield escape(l_1_relation_role_)
            yield '"\n            '
            if l_1_is_current_relation_:
                pass
                yield '\n              selected\n            '
            yield '\n          >'
            yield escape(l_1_relation_type_)
            yield ' ('
            yield escape(l_1_relation_role_)
            yield ')\n          </option>'
        else:
            pass
            yield '<option\n            value="'
            yield escape(l_1_relation_type_)
            yield '"\n            '
            if l_1_is_current_relation_:
                pass
                yield '\n              selected\n            '
            yield '\n          >'
            yield escape(l_1_relation_type_)
            yield '\n          </option>'
    l_1_relation_type_ = l_1_relation_role_ = l_1_is_current_relation_ = missing
    yield '\n    </select>\n  </sdoc-form-field>\n</sdoc-form-field-group>\n'

def block_row_right(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_namespace = resolve('namespace')
    l_0_relation_row_context = resolve('relation_row_context')
    l_0_action_button_context = missing
    pass
    l_0_action_button_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), _block_vars=_block_vars)
    _block_vars['action_button_context'] = l_0_action_button_context
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_actions'] = {'delete': True}
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['field_name'] = 'requirement relation'
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['mid'] = environment.getattr(environment.getattr((undefined(name='relation_row_context') if l_0_relation_row_context is missing else l_0_relation_row_context), 'field'), 'field_mid')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['testid_postfix'] = 'form-field-relation'
    template = environment.get_template('components/form/field_action_button/index.jinja', 'components/form/row/row_with_relation.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()

blocks = {'row_form_attributes': block_row_form_attributes, 'row_left': block_row_left, 'row_content': block_row_content, 'row_right': block_row_right}
debug_info = '1=20&2=28&3=36&4=44&5=52&8=60&10=63&12=66&14=71&16=81&19=84&23=94&30=118&31=120&36=122&41=126&42=128&44=132&49=135&70=152&74=160&77=162&78=164&79=166&80=168&84=172&85=175&87=177&89=180&90=184&93=188&97=195&98=197&101=201&110=206&112=217&113=221&114=224&115=227&116=230&117=231'