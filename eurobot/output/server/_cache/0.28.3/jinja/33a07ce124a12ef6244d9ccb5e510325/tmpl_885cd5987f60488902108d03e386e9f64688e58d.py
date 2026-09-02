from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_custom_meta_field_value.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_key = resolve('form_key')
    l_0_field_value = resolve('field_value')
    l_0_field_content = resolve('field_content')
    pass
    yield '\n<input\n  type="hidden"\n  name="metadata['
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '][value]"\n  value="'
    yield escape((undefined(name='field_value') if l_0_field_value is missing else l_0_field_value))
    yield '"\n/>\n<sdoc-autogen>'
    yield escape((undefined(name='field_content') if l_0_field_content is missing else l_0_field_content))
    yield '</sdoc-autogen>'

blocks = {}
debug_info = '10=15&11=17&13=19'