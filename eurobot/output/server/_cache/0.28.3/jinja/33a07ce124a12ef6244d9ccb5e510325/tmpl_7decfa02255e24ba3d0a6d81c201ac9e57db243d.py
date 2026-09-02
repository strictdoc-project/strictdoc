from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_config_field_value.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_field_content = resolve('field_content')
    pass
    if (undefined(name='field_content') if l_0_field_content is missing else l_0_field_content):
        pass
        template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'screens/document/table/field_display_mode/document_config_field_value.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()

blocks = {}
debug_info = '1=12&2=14'