from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_edit_mode/relations.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_object = resolve('form_object')
    l_0_namespace = resolve('namespace')
    l_0_derived_nodes = resolve('derived_nodes')
    l_0_relation_row_context = l_0_requirement_mid = missing
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    yield '\n\n<form\n  action="/actions/table/update_node_relations"\n  method="POST"\n  data-turbo="false"\n  js-table_view_edit-form\n>\n  <input type="hidden" name="requirement_mid" value="'
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
        for l_2_field_ in l_1_field_values_:
            _loop_vars = {}
            pass
            yield '<input type="hidden" name="'
            yield escape(context.call(environment.getattr(l_2_field_, 'get_input_field_type_name'), _loop_vars=_loop_vars))
            yield '" value="'
            yield escape(l_1_field_name_)
            yield '"/>\n      <input type="hidden" name="'
            yield escape(context.call(environment.getattr(l_2_field_, 'get_input_field_name'), _loop_vars=_loop_vars))
            yield '" value="'
            yield escape(environment.getattr(l_2_field_, 'field_value'))
            yield '"/>'
        l_2_field_ = missing
    l_1_field_name_ = l_1_field_values_ = missing
    for l_1_error_list in context.call(environment.getattr(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'errors'), 'values')):
        _loop_vars = {}
        pass
        for l_2_error_ in l_1_error_list:
            _loop_vars = {}
            pass
            yield '<sdoc-form-error>'
            yield escape(l_2_error_)
            yield '</sdoc-form-error>'
        l_2_error_ = missing
    l_1_error_list = missing
    l_0_relation_row_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace))
    context.vars['relation_row_context'] = l_0_relation_row_context
    context.exported_vars.add('relation_row_context')
    l_0_requirement_mid = environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'requirement_mid')
    context.vars['requirement_mid'] = l_0_requirement_mid
    context.exported_vars.add('requirement_mid')
    for l_1_field_ in context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'enumerate_reference_fields')):
        _loop_vars = {}
        pass
        if not isinstance(l_0_relation_row_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_relation_row_context['field'] = l_1_field_
        if not isinstance(l_0_relation_row_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_relation_row_context['errors'] = environment.getattr(l_1_field_, 'validation_messages')
        if not isinstance(l_0_relation_row_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_relation_row_context['relation_types'] = environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relation_types')
        if not isinstance(l_0_relation_row_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_relation_row_context['form_object'] = (undefined(name='form_object') if l_0_form_object is missing else l_0_form_object)
        template = environment.get_template('components/form/row/row_with_relation.jinja', 'screens/document/table/field_edit_mode/relations.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_': l_1_field_, 'relation_row_context': l_0_relation_row_context, 'requirement_mid': l_0_requirement_mid}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    l_1_field_ = missing
    if (t_1((undefined(name='derived_nodes') if l_0_derived_nodes is missing else l_0_derived_nodes)) and (undefined(name='derived_nodes') if l_0_derived_nodes is missing else l_0_derived_nodes)):
        pass
        yield '\n  <div class="relations-computed">\n    <span class="relations-computed__label">Computed:</span>\n    <ul class="requirement__link">'
        for l_1_req_ in (undefined(name='derived_nodes') if l_0_derived_nodes is missing else l_0_derived_nodes):
            l_1_view_object = resolve('view_object')
            _loop_vars = {}
            pass
            yield '\n      <li>\n        <a class="requirement__link-child" href="'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_1_view_object is missing else l_1_view_object), 'render_node_link'), l_1_req_, _loop_vars=_loop_vars))
            yield '">'
            if environment.getattr(l_1_req_, 'reserved_uid'):
                pass
                yield '<span class="requirement__child-uid">'
                yield escape(environment.getattr(l_1_req_, 'reserved_uid'))
                yield '</span>'
            yield '\n          '
            yield escape((environment.getattr(l_1_req_, 'reserved_title') if environment.getattr(l_1_req_, 'reserved_title') else ''))
            yield '\n        </a>\n      </li>'
        l_1_req_ = l_1_view_object = missing
        yield '\n    </ul>\n  </div>'
    yield '\n\n  <div id="requirement_'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'requirement_mid'))
    yield '__new_relation"></div>\n  <sdoc-form-row>\n    <a\n      class="action_button"\n      href="/actions/document/new_relation?requirement_mid='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'requirement_mid'))
    yield '&document_mid='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
    yield '&context_document_mid='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'context_document_mid'))
    yield '&element_type='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'element_type'))
    yield '&revision='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'revision'))
    yield '"\n      data-action-type="add_field"\n      js-table_view_edit-add-field\n      data-testid="form-action-add-relation"\n    >'
    template = environment.get_template('icons/ico16_add.svg', 'screens/document/table/field_edit_mode/relations.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'relation_row_context': l_0_relation_row_context, 'requirement_mid': l_0_requirement_mid}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield ' Add relation</a>\n  </sdoc-form-row>\n\n</form>'

blocks = {}
debug_info = '15=22&16=24&17=26&18=28&19=30&21=32&22=35&23=39&24=43&28=49&29=52&30=56&34=60&35=63&36=66&37=71&38=74&39=77&40=80&41=81&44=88&48=91&50=96&51=98&52=104&60=109&64=111&68=121'