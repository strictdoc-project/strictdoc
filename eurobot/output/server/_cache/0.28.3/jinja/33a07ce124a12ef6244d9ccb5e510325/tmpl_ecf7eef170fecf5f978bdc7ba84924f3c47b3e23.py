from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_edit_mode/comments.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_object = resolve('form_object')
    l_0_namespace = resolve('namespace')
    l_0_comment_field_row_context = missing
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    yield '\n\n<form\n  action="/actions/table/update_node_comments"\n  method="POST"\n  data-turbo="false"\n  js-table_view_edit-form\n>\n  <input type="hidden" name="requirement_mid" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'requirement_mid'))
    yield '"/>\n  <input type="hidden" name="document_mid" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
    yield '"/>\n  <input type="hidden" name="context_document_mid" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'context_document_mid'))
    yield '"/>\n  <input type="hidden" name="element_type" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'element_type'))
    yield '"/>\n  <input type="hidden" name="revision" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'revision'))
    yield '"/>'
    for (l_1_field_name_, l_1_field_values_) in context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'fields'), 'items')):
        _loop_vars = {}
        pass
        if (l_1_field_name_ != 'COMMENT'):
            pass
            for l_2_field_ in l_1_field_values_:
                _loop_vars = {}
                pass
                yield '<input type="hidden" name="'
                yield escape(context.call(environment.getattr(l_2_field_, 'get_input_field_type_name'), _loop_vars=_loop_vars))
                yield '" value="'
                yield escape(l_1_field_name_)
                yield '"/>\n        <input type="hidden" name="'
                yield escape(context.call(environment.getattr(l_2_field_, 'get_input_field_name'), _loop_vars=_loop_vars))
                yield '" value="'
                yield escape(environment.getattr(l_2_field_, 'field_value'))
                yield '"/>'
            l_2_field_ = missing
    l_1_field_name_ = l_1_field_values_ = missing
    for l_1_ref_field in environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'reference_fields'):
        _loop_vars = {}
        pass
        yield '<input type="hidden" name="'
        yield escape(context.call(environment.getattr(l_1_ref_field, 'get_type_field_name'), _loop_vars=_loop_vars))
        yield '" value="'
        yield escape(environment.getattr(environment.getattr(l_1_ref_field, 'field_type'), 'value'))
        if environment.getattr(l_1_ref_field, 'field_role'):
            pass
            yield ','
            yield escape(environment.getattr(l_1_ref_field, 'field_role'))
        yield '"/>\n    <input type="hidden" name="'
        yield escape(context.call(environment.getattr(l_1_ref_field, 'get_value_field_name'), _loop_vars=_loop_vars))
        yield '" value="'
        yield escape(environment.getattr(l_1_ref_field, 'field_value'))
        yield '"/>'
    l_1_ref_field = missing
    l_0_comment_field_row_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace))
    context.vars['comment_field_row_context'] = l_0_comment_field_row_context
    context.exported_vars.add('comment_field_row_context')
    for l_1_field_values in context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'enumerate_fields'), multiline=True):
        _loop_vars = {}
        pass
        for l_2_field_ in l_1_field_values:
            _loop_vars = {}
            pass
            if (environment.getattr(l_2_field_, 'field_name') == 'COMMENT'):
                pass
                if (t_1(environment.getattr(l_2_field_, 'field_value')) > 0):
                    pass
                    if not isinstance(l_0_comment_field_row_context, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_0_comment_field_row_context['field'] = l_2_field_
                    if not isinstance(l_0_comment_field_row_context, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_0_comment_field_row_context['field_editable'] = True
                    if not isinstance(l_0_comment_field_row_context, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_0_comment_field_row_context['errors'] = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), environment.getattr(l_2_field_, 'field_mid'), _loop_vars=_loop_vars)
                    template = environment.get_template('components/form/row/row_with_comment.jinja', 'screens/document/table/field_edit_mode/comments.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_': l_2_field_, 'field_values': l_1_field_values, 'comment_field_row_context': l_0_comment_field_row_context}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
        l_2_field_ = missing
    l_1_field_values = missing
    yield '<div id="requirement_'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'requirement_mid'))
    yield '__new_comment"></div>\n  <sdoc-form-row>\n    <a\n      class="action_button"\n      href="/actions/document/new_comment?requirement_mid='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'requirement_mid'))
    yield '&document_mid='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
    yield '&context_document_mid='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'context_document_mid'))
    yield '&element_type='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'element_type'))
    yield '&revision='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'revision'))
    yield '"\n      data-action-type="add_field"\n      js-table_view_edit-add-field\n      data-testid="form-action-add-comment"\n    >'
    template = environment.get_template('icons/ico16_add.svg', 'screens/document/table/field_edit_mode/comments.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'comment_field_row_context': l_0_comment_field_row_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield ' Add comment</a>\n  </sdoc-form-row>\n\n</form>'

blocks = {}
debug_info = '14=21&15=23&16=25&17=27&18=29&20=31&21=34&22=36&23=40&24=44&29=50&30=54&31=62&34=67&35=70&36=73&37=76&38=78&39=82&40=85&41=88&42=89&48=98&52=100&56=110'