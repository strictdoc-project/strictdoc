from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/included_document_form/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_object = resolve('form_object')
    pass
    yield '<turbo-frame id="article-'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
    yield '">\n<sdoc-form>\n\n  <form\n    method="POST"\n    data-turbo="true"\n    action="/actions/document/save_included_document"\n  >\n    <input type="hidden" id="document_mid" name="document_mid" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
    yield '"/>\n    <input type="hidden" id="context_document_mid" name="context_document_mid" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'context_document_mid'))
    yield '"/>\n\n    <sdoc-form-grid>\n      <sdoc-form-row>\n        <sdoc-form-row-aside></sdoc-form-row-aside>\n        <sdoc-form-row-main>'
    l_1_field_class_name = None
    l_1_field_editable = True
    l_1_field_input_name = 'document[TITLE]'
    l_1_field_label = 'TITLE'
    l_1_field_placeholder = 'Enter TITLE here...'
    l_1_field_type = 'singleline'
    l_1_field_value = environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_title')
    l_1_testid_postfix = 'document[TITLE]'
    l_1_errors = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), 'TITLE')
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'components/included_document_form/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_testid_postfix = l_1_errors = missing
    yield '</sdoc-form-row-main>\n        <sdoc-form-row-aside></sdoc-form-row-aside>\n      </sdoc-form-row>\n    </sdoc-form-grid>\n\n    <sdoc-form-footer>\n      '
    template = environment.get_template('components/button/submit.jinja', 'components/included_document_form/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_cancel_href = markup_join(('/actions/document/cancel_edit_included_document?document_mid=', environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'), ))
    pass
    template = environment.get_template('components/button/cancel.jinja', 'components/included_document_form/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'cancel_href': l_1_cancel_href}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_cancel_href = missing
    yield '</sdoc-form-footer>\n\n  </form>\n\n</sdoc-form>\n</turbo-frame>'

blocks = {}
debug_info = '1=13&9=15&10=17&27=29&35=37&37=45'