from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_file_view/range_button.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_begin = resolve('begin')
    l_0_end = resolve('end')
    l_0_href = resolve('href')
    l_0_scope = resolve('scope')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    yield '\n\n<a\n  class="source__range-pointer action_button"\n  data-begin="'
    yield escape((undefined(name='begin') if l_0_begin is missing else l_0_begin))
    yield '"\n  data-end="'
    yield escape((undefined(name='end') if l_0_end is missing else l_0_end))
    yield '"\n  href="'
    yield escape((undefined(name='href') if l_0_href is missing else l_0_href))
    yield '"\n  title="Click to toggle range (Ctrl/Cmd + Click with focus)"\n><span class="source__range-definition">'
    yield escape((undefined(name='begin') if l_0_begin is missing else l_0_begin))
    yield ' - '
    yield escape((undefined(name='end') if l_0_end is missing else l_0_end))
    if t_1((undefined(name='scope') if l_0_scope is missing else l_0_scope)):
        pass
        yield ' | '
        yield escape((undefined(name='scope') if l_0_scope is missing else l_0_scope))
    yield '</span></a>'

blocks = {}
debug_info = '14=22&15=24&16=26&18=28'