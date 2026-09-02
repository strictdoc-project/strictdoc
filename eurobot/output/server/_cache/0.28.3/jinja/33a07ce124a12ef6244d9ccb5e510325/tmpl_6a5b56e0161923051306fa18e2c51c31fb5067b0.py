from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = '_shared/favicon.svg.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_variant = resolve('variant')
    l_0_light_color = resolve('light_color')
    l_0_dark_color = resolve('dark_color')
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    pass
    yield '\n'
    l_0_variant = t_1((undefined(name='variant') if l_0_variant is missing else l_0_variant), 'default')
    context.vars['variant'] = l_0_variant
    context.exported_vars.add('variant')
    yield '\n\n'
    if ((undefined(name='variant') if l_0_variant is missing else l_0_variant) == 'dev'):
        pass
        yield '\n  \n  '
        l_0_light_color = 'rgb(242, 100, 42)'
        context.vars['light_color'] = l_0_light_color
        context.exported_vars.add('light_color')
        yield '\n  '
        l_0_dark_color = 'rgb(242, 100, 42)'
        context.vars['dark_color'] = l_0_dark_color
        context.exported_vars.add('dark_color')
        yield '\n'
    elif ((undefined(name='variant') if l_0_variant is missing else l_0_variant) == 'test'):
        pass
        yield '\n  \n  '
        l_0_light_color = 'rgb(42, 142, 42)'
        context.vars['light_color'] = l_0_light_color
        context.exported_vars.add('light_color')
        yield '\n  '
        l_0_dark_color = 'rgb(42, 142, 42)'
        context.vars['dark_color'] = l_0_dark_color
        context.exported_vars.add('dark_color')
        yield '\n'
    elif ((undefined(name='variant') if l_0_variant is missing else l_0_variant) == 'export'):
        pass
        yield '\n  \n  '
        l_0_light_color = '#282c42'
        context.vars['light_color'] = l_0_light_color
        context.exported_vars.add('light_color')
        yield '\n  '
        l_0_dark_color = '#F2F5F9'
        context.vars['dark_color'] = l_0_dark_color
        context.exported_vars.add('dark_color')
        yield '\n'
    else:
        pass
        yield '\n  \n  '
        l_0_light_color = '#555555'
        context.vars['light_color'] = l_0_light_color
        context.exported_vars.add('light_color')
        yield '\n  '
        l_0_dark_color = '#AAAAAA'
        context.vars['dark_color'] = l_0_dark_color
        context.exported_vars.add('dark_color')
        yield '\n'
    yield '\n\n<svg\n  data-testid="'
    yield escape((undefined(name='variant') if l_0_variant is missing else l_0_variant))
    yield '-favicon"\n  viewBox="0 0 100 100"\n  xmlns="http://www.w3.org/2000/svg">\n  <style>\n    .line {\n      fill: none;\n      stroke-width: 6;\n      stroke: #808080;\n    }\n    .node {\n      fill: #808080;\n      stroke: none;\n    }\n\n    @media (prefers-color-scheme: light) {\n      .line { stroke: '
    yield escape((undefined(name='light_color') if l_0_light_color is missing else l_0_light_color))
    yield '; }\n      .node { fill: '
    yield escape((undefined(name='light_color') if l_0_light_color is missing else l_0_light_color))
    yield '; }\n    }\n    @media (prefers-color-scheme: dark) {\n      .line { stroke: '
    yield escape((undefined(name='dark_color') if l_0_dark_color is missing else l_0_dark_color))
    yield '; }\n      .node { fill: '
    yield escape((undefined(name='dark_color') if l_0_dark_color is missing else l_0_dark_color))
    yield '; }\n    }\n  </style>\n\n  <path\n    class="line"\n    d="M 76,35 50,20 24,35 76,65 50,80 24,65"/>\n\n  <circle id="sdoc_n_7" class="node" cx="24" cy="65" r="9.0"/>\n  <circle id="sdoc_n_6" class="node" cx="50" cy="80" r="9.0"/>\n  <circle id="sdoc_n_5" class="node" cx="76" cy="65" r="9.0"/>\n  <circle id="sdoc_n_4" class="node" cx="50" cy="50" r="9.0"/>\n  <circle id="sdoc_n_3" class="node" cx="24" cy="35" r="9.0"/>\n  <circle id="sdoc_n_2" class="node" cx="50" cy="20" r="9.0"/>\n  <circle id="sdoc_n_1" class="node" cx="76" cy="35" r="9.0"/>\n\n  \n  \n</svg>'

blocks = {}
debug_info = '35=21&37=25&43=28&44=32&45=36&51=39&52=43&53=47&60=50&61=54&68=61&69=65&73=70&88=72&89=74&92=76&93=78'