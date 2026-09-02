from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_config_field.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_field_testid = resolve('field_testid')
    l_0_field_label = resolve('field_label')
    l_0_field_name = resolve('field_name')
    l_0_view_object = resolve('view_object')
    l_0_doc_mid = resolve('doc_mid')
    pass
    yield '<sdoc-meta-label\n  data-testid="document-config-'
    yield escape((undefined(name='field_testid') if l_0_field_testid is missing else l_0_field_testid))
    yield '-label">'
    yield escape((undefined(name='field_label') if l_0_field_label is missing else l_0_field_label))
    yield ':</sdoc-meta-label>\n<sdoc-meta-field\n  data-testid="document-config-'
    yield escape((undefined(name='field_testid') if l_0_field_testid is missing else l_0_field_testid))
    yield '-field"\n  data-field-name="'
    yield escape((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name))
    yield '"'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '\n  data-field-type="contenteditable"\n  js-table_view_edit-field="contenteditable"\n  data-node-mid="'
        yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
        yield '"\n  data-url="/actions/table/get_document_config_field_inline?document_mid='
        yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
        yield '&amp;field_name='
        yield escape((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name))
        yield '"'
    yield '\n>'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '<div class="editable-cell-indicator"></div>'
    yield '\n  <div\n    id="doc-field-'
    yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
    yield '-'
    yield escape((undefined(name='field_name') if l_0_field_name is missing else l_0_field_name))
    yield '"'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '\n    \n    placeholder="Enter '
        yield escape((undefined(name='field_label') if l_0_field_label is missing else l_0_field_label))
        yield ' here..."\n    wrapper-field-type="contenteditable"'
    yield '\n  >'
    template = environment.get_template('screens/document/table/field_display_mode/document_config_field_value.jinja', 'screens/document/table/field_display_mode/document_config_field.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</div>\n</sdoc-meta-field>'

blocks = {}
debug_info = '2=17&4=21&5=23&6=25&9=28&10=30&13=35&15=39&16=43&18=46&22=49'