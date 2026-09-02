from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_custom_meta.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_doc_mid = resolve('doc_mid')
    l_0_document_config = resolve('document_config')
    pass
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '\n<form\n  id="document-custom-meta-'
        yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
        yield '"\n  action="/actions/table/update_document_custom_meta"\n  method="POST"\n  data-turbo="false"\n  style="display: contents;"\n  js-table_view_edit-form\n>\n  <input type="hidden" name="document_mid" value="'
        yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
        yield '"/>\n  <input type="hidden" name="document[TITLE]" value="'
        yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'title'))
        yield '"/>\n  <input type="hidden" name="document[UID]" value="'
        yield escape((environment.getattr((undefined(name='document_config') if l_0_document_config is missing else l_0_document_config), 'uid') or ''))
        yield '"/>\n  <input type="hidden" name="document[VERSION]" value="'
        yield escape((environment.getattr((undefined(name='document_config') if l_0_document_config is missing else l_0_document_config), 'version') or ''))
        yield '"/>\n  <input type="hidden" name="document[CLASSIFICATION]" value="'
        yield escape((environment.getattr((undefined(name='document_config') if l_0_document_config is missing else l_0_document_config), 'classification') or ''))
        yield '"/>\n  <input type="hidden" name="document[PREFIX]" value="'
        yield escape((environment.getattr((undefined(name='document_config') if l_0_document_config is missing else l_0_document_config), 'requirement_prefix') or ''))
        yield '"/>'
        template = environment.get_template('screens/document/table/field_display_mode/document_custom_meta_value.jinja', 'screens/document/table/field_display_mode/document_custom_meta.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</form>'
    else:
        pass
        template = environment.get_template('screens/document/table/field_display_mode/document_custom_meta_value.jinja', 'screens/document/table/field_display_mode/document_custom_meta.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()

blocks = {}
debug_info = '9=14&11=17&18=19&19=21&20=23&21=25&22=27&23=29&25=31&28=40'