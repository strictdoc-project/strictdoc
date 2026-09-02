from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/grammar_form_element/row_with_relation/index.jinja'

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
    parent_template = environment.get_template('components/form/row/index.jinja', 'components/grammar_form_element/row_with_relation/index.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object)), 'form_object: form_object must be defined.', caller=caller)
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
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation')), 'form_object: relation must be defined.', caller=caller)
    yield from parent_template.root_render_func(context)

def block_row_form_attributes(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_form_object = resolve('form_object')
    pass
    yield '\n  mid="'
    yield escape(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_mid'))
    yield '"\n  data-testid="grammar-form-relation-row"\n'

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
    l_0_relation_type_errors = missing
    try:
        t_5 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    yield '\n\n  '
    l_0_relation_type_errors = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_type_input_name'), _block_vars=_block_vars), _block_vars=_block_vars)
    _block_vars['relation_type_errors'] = l_0_relation_type_errors
    yield '<sdoc-form-field-group\n    data-field-label="Relation"\n    '
    if t_5((undefined(name='relation_type_errors') if l_0_relation_type_errors is missing else l_0_relation_type_errors)):
        pass
        yield 'errors="true"'
    yield '>\n\n  '
    if (((environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_type') == 'Parent') or (environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_type') == 'Child')) or (environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_type') == 'File')):
        pass
        if (t_5((undefined(name='relation_type_errors') if l_0_relation_type_errors is missing else l_0_relation_type_errors)) > 0):
            pass
            for l_1_error_ in (undefined(name='relation_type_errors') if l_0_relation_type_errors is missing else l_0_relation_type_errors):
                _loop_vars = {}
                pass
                yield '<sdoc-form-error>\n        '
                yield escape(l_1_error_)
                yield '\n      </sdoc-form-error>'
            l_1_error_ = missing
        yield '<sdoc-form-field field-type="select">\n      <label for="relation_type_'
        yield escape(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_mid'))
        yield '">Relation type</label>\n        <select\n          class="sdoc-form-select"\n          name="'
        yield escape(context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_type_input_name'), _block_vars=_block_vars))
        yield '"\n          id="relation_type_'
        yield escape(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_mid'))
        yield '"\n          mid="'
        yield escape(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_mid'))
        yield '"\n          data-testid="select-relation-type"\n        >\n          <option\n            value="Parent"\n            '
        yield escape(('selected' if (environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_type') == 'Parent') else ''))
        yield '\n          >Parent</option>\n          <option\n            value="Child"\n            '
        yield escape(('selected' if (environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_type') == 'Child') else ''))
        yield '\n          >Child</option>\n          <option\n            value="File"\n            '
        yield escape(('selected' if (environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_type') == 'File') else ''))
        yield '\n          >File</option>\n        </select>\n    </sdoc-form-field>'
        l_1_field_class_name = 'monospace'
        l_1_field_editable = True
        l_1_field_required = False
        l_1_field_input_name = context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_role_input_name'), _block_vars=_block_vars)
        l_1_field_label = 'Relation role:'
        l_1_field_placeholder = 'Enter relation role here...'
        l_1_field_type = 'singleline'
        l_1_field_value = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_role')
        l_1_mid = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_mid')
        l_1_testid_postfix = 'relation-role'
        l_1_errors = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_role_input_name'), _block_vars=_block_vars), _block_vars=_block_vars)
        pass
        template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/grammar_form_element/row_with_relation/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_required': l_1_field_required, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'mid': l_1_mid, 'testid_postfix': l_1_testid_postfix, 'relation_type_errors': l_0_relation_type_errors}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_class_name = l_1_field_editable = l_1_field_required = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_mid = l_1_testid_postfix = l_1_errors = missing
    yield '\n  </sdoc-form-field-group>\n'

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
    l_0_action_button_context['field_name'] = 'relation'
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['mid'] = environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation'), 'relation_mid')
    if not isinstance(l_0_action_button_context, Namespace):
        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
    l_0_action_button_context['testid_postfix'] = 'relation'
    template = environment.get_template('components/form/field_action_button/index.jinja', 'components/grammar_form_element/row_with_relation/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()

blocks = {'row_form_attributes': block_row_form_attributes, 'row_left': block_row_left, 'row_content': block_row_content, 'row_right': block_row_right}
debug_info = '1=19&3=22&5=28&6=34&8=42&9=52&13=55&17=65&19=82&22=85&27=89&35=91&36=93&38=97&44=101&47=103&48=105&49=107&54=109&58=111&62=113&80=127&87=136&88=147&89=151&90=154&91=157&92=160&93=161'