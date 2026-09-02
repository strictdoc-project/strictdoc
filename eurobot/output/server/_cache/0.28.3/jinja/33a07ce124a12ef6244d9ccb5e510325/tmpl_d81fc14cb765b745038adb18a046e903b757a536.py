from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/anchor_document/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_local_anchor = resolve('local_anchor')
    pass
    yield '<span style="position: absolute; left: 0;" id="'
    yield escape((undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor))
    yield '" data-uid="'
    yield escape((undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor))
    yield '" data-anchor="'
    yield escape((undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor))
    yield '"></span>'

blocks = {}
debug_info = '1=13'