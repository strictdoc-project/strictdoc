from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'autocomplete/uid/stream_autocomplete_uid.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_nodes = resolve('nodes')
    pass
    for l_1_node in (undefined(name='nodes') if l_0_nodes is missing else l_0_nodes):
        _loop_vars = {}
        pass
        yield '\n<li class="autocompletable-result-item" role="option" data-autocompletable-value="'
        yield escape(environment.getattr(l_1_node, 'reserved_uid'))
        yield '"><span class="requirement__link-parent"><span class="requirement__parent-uid">'
        yield escape(environment.getattr(l_1_node, 'reserved_uid'))
        yield '</span> '
        yield escape(environment.getattr(l_1_node, 'reserved_title'))
        yield '</span></li>'
    l_1_node = missing

blocks = {}
debug_info = '1=12&2=16'