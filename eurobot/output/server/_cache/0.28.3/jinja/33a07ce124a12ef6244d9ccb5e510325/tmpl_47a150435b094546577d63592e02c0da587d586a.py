from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/section_h/pdf.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_h_level = resolve('h_level')
    l_0_view_object = resolve('view_object')
    l_0_section = resolve('section')
    l_0_title = resolve('title')
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '\n'
    if environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_title'):
        pass
        yield '\n<sdoc-section-title\n  data-level="'
        yield escape(environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'title_number_string'))
        yield '"\n>\n  '
        l_0_h_level = ((environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'ng_level') + 1) if (environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'ng_level') < 6) else 6)
        context.vars['h_level'] = l_0_h_level
        context.exported_vars.add('h_level')
        yield '\n  <h'
        yield escape((undefined(name='h_level') if l_0_h_level is missing else l_0_h_level))
        yield '\n    id="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_local_anchor'), (undefined(name='section') if l_0_section is missing else l_0_section)))
        yield '"'
        if (environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'ng_level') >= 6):
            pass
            yield ' aria-level="'
            yield escape((environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'ng_level') + 1))
            yield '"'
        yield '\n  >'
        if environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'title_number_string'):
            pass
            yield escape(environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'title_number_string'))
            yield '.&nbsp;'
        l_0_title = (environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_title') if context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'is_content_node')) else environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'title'))
        context.vars['title'] = l_0_title
        context.exported_vars.add('title')
        if (not t_1((undefined(name='title') if l_0_title is missing else l_0_title))):
            pass
            yield escape((undefined(name='title') if l_0_title is missing else l_0_title))
        yield '</h'
        yield escape((undefined(name='h_level') if l_0_h_level is missing else l_0_h_level))
        yield '>\n</sdoc-section-title>'

blocks = {}
debug_info = '3=23&5=26&7=28&10=32&11=34&12=36&14=42&15=44&17=46&18=49&19=51&21=53'