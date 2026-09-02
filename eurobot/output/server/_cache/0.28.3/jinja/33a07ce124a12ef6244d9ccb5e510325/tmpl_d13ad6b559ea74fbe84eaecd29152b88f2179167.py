from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_coverage/value_bar.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_coverage_value = resolve('coverage_value')
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    if (not t_1((undefined(name='coverage_value') if l_0_coverage_value is missing else l_0_coverage_value))):
        pass
        yield '<div class="value-bar">\n  <span class="value-bar_bar" data-value='
        yield escape((undefined(name='coverage_value') if l_0_coverage_value is missing else l_0_coverage_value))
        yield '>\n    <span class="value-bar_filler" style="width:'
        yield escape((undefined(name='coverage_value') if l_0_coverage_value is missing else l_0_coverage_value))
        yield '%"></span>\n  </span>\n  <span class="value-bar_text">'
        yield escape((undefined(name='coverage_value') if l_0_coverage_value is missing else l_0_coverage_value))
        yield '%</span>\n</div>'
    else:
        pass
        yield '<div class="value-bar">\n  <span class="value-bar_bar">\n    <span class="value-bar_filler"></span>\n  </span>\n  <span class="value-bar_text"></span>\n</div>'

blocks = {}
debug_info = '1=18&3=21&4=23&6=25'