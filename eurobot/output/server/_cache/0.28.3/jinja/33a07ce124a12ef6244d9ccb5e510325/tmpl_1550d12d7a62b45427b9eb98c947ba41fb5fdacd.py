from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_custom_meta_row.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_key = resolve('form_key')
    l_0_view_object = resolve('view_object')
    l_0_namespace = resolve('namespace')
    l_0_action_button_context = resolve('action_button_context')
    l_0_doc_mid = resolve('doc_mid')
    pass
    yield '\n<sdoc-meta-row\n  data-testid="document-config-metadata-row-'
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '"'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '\n  draggable="true"\n  js-table_view_edit-custom_meta-row\n  data-form-key="'
        yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
        yield '"'
    yield '\n>'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '\n  \n  <div\n    class="custom_meta-row-move-container"\n    js-table_view_edit-custom_meta-drag_handle\n  >'
        l_0_action_button_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace))
        context.vars['action_button_context'] = l_0_action_button_context
        context.exported_vars.add('action_button_context')
        if not isinstance(l_0_action_button_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_action_button_context['field_actions'] = {'move': True}
        if not isinstance(l_0_action_button_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_action_button_context['field_name'] = 'metadata'
        if not isinstance(l_0_action_button_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_action_button_context['mid'] = (undefined(name='form_key') if l_0_form_key is missing else l_0_form_key)
        if not isinstance(l_0_action_button_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_action_button_context['testid_postfix'] = 'form-field-metadata'
        template = environment.get_template('components/form/field_action_button/index.jinja', 'screens/document/table/field_display_mode/document_custom_meta_row.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</div>'
    yield '\n\n  <sdoc-meta-label\n    id="document-custom-meta-label-'
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '"\n    data-testid="document-config-metadata-label"'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '\n    data-field-type="contenteditable"\n    js-table_view_edit-field="contenteditable"\n    data-url="/actions/table/get_document_custom_meta_inline?document_mid='
        yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
        yield '&amp;form_key='
        yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
        yield '&amp;field_name=name"'
    yield '\n  >'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '<div class="editable-cell-indicator"></div>'
    yield '\n    <div id="document-custom-meta-name-'
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '">'
    template = environment.get_template('screens/document/table/field_display_mode/document_custom_meta_field_name.jinja', 'screens/document/table/field_display_mode/document_custom_meta_row.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</div>\n\n  </sdoc-meta-label>\n  <sdoc-meta-field\n    id="document-custom-meta-field-'
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '"\n    data-testid="document-config-metadata-field"'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '\n    data-field-type="contenteditable"\n    js-table_view_edit-field="contenteditable"\n    data-url="/actions/table/get_document_custom_meta_inline?document_mid='
        yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
        yield '&amp;form_key='
        yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
        yield '&amp;field_name=value"'
    yield '\n  >'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '<div class="editable-cell-indicator"></div>'
    yield '\n    <div id="document-custom-meta-value-'
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '">'
    template = environment.get_template('screens/document/table/field_display_mode/document_custom_meta_field_value.jinja', 'screens/document/table/field_display_mode/document_custom_meta_row.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</div>\n\n  </sdoc-meta-field>'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '\n  \n  <div\n    class="custom_meta-row-delete-container"\n    js-table_view_edit-custom_meta-delete_action\n  >'
        l_0_action_button_context = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace))
        context.vars['action_button_context'] = l_0_action_button_context
        context.exported_vars.add('action_button_context')
        if not isinstance(l_0_action_button_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_action_button_context['field_actions'] = {'delete': True}
        if not isinstance(l_0_action_button_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_action_button_context['field_name'] = 'metadata'
        if not isinstance(l_0_action_button_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_action_button_context['mid'] = (undefined(name='form_key') if l_0_form_key is missing else l_0_form_key)
        if not isinstance(l_0_action_button_context, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_action_button_context['testid_postfix'] = 'form-field-metadata'
        template = environment.get_template('components/form/field_action_button/index.jinja', 'screens/document/table/field_display_mode/document_custom_meta_row.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'action_button_context': l_0_action_button_context}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</div>'
    yield '\n\n</sdoc-meta-row>'

blocks = {}
debug_info = '13=17&14=19&17=22&21=25&27=28&28=33&29=36&30=39&31=42&32=43&37=51&39=53&42=56&45=61&46=65&47=67&52=74&54=76&57=79&60=84&61=88&62=90&67=97&73=100&74=105&75=108&76=111&77=114&78=115'