from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/get_node_autocomplete_inline/stream_inline_form.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_node_mid = resolve('node_mid')
    l_0_cell_field_name = resolve('cell_field_name')
    pass
    yield '<turbo-stream action="update" target="cell-'
    yield escape((undefined(name='node_mid') if l_0_node_mid is missing else l_0_node_mid))
    yield '-'
    yield escape((undefined(name='cell_field_name') if l_0_cell_field_name is missing else l_0_cell_field_name))
    yield '">\n  <template>'
    template = environment.get_template('screens/document/table/field_edit_mode/autocompletable.jinja', 'actions/table/get_node_autocomplete_inline/stream_inline_form.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </template>\n</turbo-stream>'

blocks = {}
debug_info = '1=14&3=18'