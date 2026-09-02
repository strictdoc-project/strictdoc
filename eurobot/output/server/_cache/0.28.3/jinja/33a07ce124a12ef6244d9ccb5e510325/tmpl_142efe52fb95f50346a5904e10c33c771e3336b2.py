from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/header/header_pagetype.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_template_type = resolve('template_type')
    pass
    yield '<div class="pagetype">'
    yield escape((undefined(name='template_type') if l_0_template_type is missing else l_0_template_type))
    yield '</div>'

blocks = {}
debug_info = '1=13'