from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_title.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_document_title_wrap = resolve('document_title_wrap')
    l_0_view_object = resolve('view_object')
    l_0_doc_mid = resolve('doc_mid')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    if (t_1((undefined(name='document_title_wrap') if l_0_document_title_wrap is missing else l_0_document_title_wrap)) and (undefined(name='document_title_wrap') if l_0_document_title_wrap is missing else l_0_document_title_wrap)):
        pass
        yield '<div\n     data-testid="document-title-field"\n     data-field-name="TITLE"'
        if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
            pass
            yield '\n     data-field-type="contenteditable"\n     js-table_view_edit-field="contenteditable"\n     data-node-mid="'
            yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
            yield '"\n     data-url="/actions/table/get_document_config_field_inline?document_mid='
            yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
            yield '&amp;field_name=TITLE"'
        yield '\n>'
        if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
            pass
            yield '<div class="editable-cell-indicator"></div>'
        yield '\n  <div id="doc-field-'
        yield escape((undefined(name='doc_mid') if l_0_doc_mid is missing else l_0_doc_mid))
        yield '-TITLE" wrapper-field-type="contenteditable">'
        template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'screens/document/table/field_display_mode/document_title.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</div>\n</div>'
    else:
        pass
        template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'screens/document/table/field_display_mode/document_title.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()

blocks = {}
debug_info = '1=20&5=23&8=26&9=28&12=31&13=35&14=37&18=46'