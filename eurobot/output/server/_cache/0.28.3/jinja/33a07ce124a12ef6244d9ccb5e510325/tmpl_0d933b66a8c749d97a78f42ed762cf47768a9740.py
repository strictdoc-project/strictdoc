from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/section_h/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_h_level = resolve('h_level')
    l_0_field_content_ = resolve('field_content_')
    l_0_title = resolve('title')
    try:
        t_1 = environment.filters['safe']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'safe' found.")
    try:
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '\n'
    if environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_title'):
        pass
        yield '\n<sdoc-section-title\n  data-level="'
        yield escape(environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'title_number_string'))
        yield '"\n>'
        l_0_h_level = ((environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'ng_level') + 1) if (environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'ng_level') < 6) else 6)
        context.vars['h_level'] = l_0_h_level
        context.exported_vars.add('h_level')
        yield '<h'
        yield escape((undefined(name='h_level') if l_0_h_level is missing else l_0_h_level))
        if (environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'ng_level') >= 6):
            pass
            yield ' aria-level="'
            yield escape((environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'ng_level') + 1))
            yield '"'
        yield '>'
        l_0_field_content_ = ''
        context.vars['field_content_'] = l_0_field_content_
        context.exported_vars.add('field_content_')
        if environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'title_number_string'):
            pass
            l_0_field_content_ = (((undefined(name='field_content_') if l_0_field_content_ is missing else l_0_field_content_) + environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'title_number_string')) + Markup('.&nbsp;'))
            context.vars['field_content_'] = l_0_field_content_
            context.exported_vars.add('field_content_')
        l_0_title = (environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_title') if context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'is_content_node')) else environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'title'))
        context.vars['title'] = l_0_title
        context.exported_vars.add('title')
        if (not t_2((undefined(name='title') if l_0_title is missing else l_0_title))):
            pass
            l_0_field_content_ = ((undefined(name='field_content_') if l_0_field_content_ is missing else l_0_field_content_) + (undefined(name='title') if l_0_title is missing else l_0_title))
            context.vars['field_content_'] = l_0_field_content_
            context.exported_vars.add('field_content_')
        l_1_field_content = (undefined(name='field_content_') if l_0_field_content_ is missing else l_0_field_content_)
        pass
        template = environment.get_template('components/field/index.jinja', 'components/node_field/section_h/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content, 'field_content_': l_0_field_content_, 'h_level': l_0_h_level, 'title': l_0_title}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = missing
        yield '</h'
        yield escape((undefined(name='h_level') if l_0_h_level is missing else l_0_h_level))
        yield '>\n</sdoc-section-title>'

blocks = {}
debug_info = '3=28&5=31&7=33&11=37&13=44&15=47&17=49&20=52&21=55&23=57&28=62&30=70'