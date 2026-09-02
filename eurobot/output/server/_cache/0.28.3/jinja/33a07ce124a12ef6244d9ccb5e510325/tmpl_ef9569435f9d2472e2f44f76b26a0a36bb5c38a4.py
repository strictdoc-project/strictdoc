from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/get_document_custom_meta_new_inline/stream_inline_form.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '\n<turbo-stream action="update" target="document-custom-meta-add">\n  <template>'
    template = environment.get_template('screens/document/table/field_edit_mode/document_custom_meta_new.jinja', 'actions/table/get_document_custom_meta_new_inline/stream_inline_form.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</template>\n</turbo-stream>'

blocks = {}
debug_info = '7=12'