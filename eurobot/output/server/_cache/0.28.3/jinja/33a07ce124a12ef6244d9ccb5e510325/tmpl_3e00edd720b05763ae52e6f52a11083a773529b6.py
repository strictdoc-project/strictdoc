from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/document_custom_meta_field_name.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form_key = resolve('form_key')
    l_0_field_label = resolve('field_label')
    pass
    yield '\n<input\n  type="hidden"\n  name="metadata['
    yield escape((undefined(name='form_key') if l_0_form_key is missing else l_0_form_key))
    yield '][name]"\n  value="'
    yield escape((undefined(name='field_label') if l_0_field_label is missing else l_0_field_label))
    yield '"\n/>\n<span>'
    yield escape((undefined(name='field_label') if l_0_field_label is missing else l_0_field_label))
    yield ':</span>'

blocks = {}
debug_info = '9=14&10=16&12=18'