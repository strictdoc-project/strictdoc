from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'autocomplete/field/stream_autocomplete_field.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_values = resolve('values')
    pass
    for (l_1_value, l_1_is_selected) in (undefined(name='values') if l_0_values is missing else l_0_values):
        _loop_vars = {}
        pass
        yield '\n<li class="autocompletable-result-item'
        if l_1_is_selected:
            pass
            yield ' autocompletable-result-item_selected'
        yield '" role="option" '
        if l_1_is_selected:
            pass
            yield 'aria-disabled="true" '
        yield 'data-autocompletable-value="'
        yield escape(l_1_value)
        yield '">'
        yield escape(l_1_value)
        yield '</li>'
    l_1_value = l_1_is_selected = missing

blocks = {}
debug_info = '1=12&2=16'