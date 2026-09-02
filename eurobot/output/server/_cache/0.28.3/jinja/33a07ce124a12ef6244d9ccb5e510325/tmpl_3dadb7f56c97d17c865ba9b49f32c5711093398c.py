from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_custom_meta_add.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_doc_mid = resolve('doc_mid')
    pass
    yield '\n<sdoc-meta-row\n  id="document-custom-meta-add"\n  class="table-view-custom-metadata-add-button"\n  js-table_view_edit-field="contenteditable"\n  js-table_view_edit-submit-unchanged\n  data-url="/actions/table/get_document_custom_meta_new_inline?document_mid='
    yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
    yield '"\n  data-testid="document-config-metadata-add"\n>\n  <span class="action_button">'
    template = environment.get_template('icons/ico16_add.svg', 'screens/document/table/field_display_mode/document_custom_meta_add.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield 'Add metadata\n  </span>\n</sdoc-meta-row>'

blocks = {}
debug_info = '13=13&17=15'