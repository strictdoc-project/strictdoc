from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_content/tiny.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_requirement_style = resolve('requirement_style')
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_title_number = l_0_truncated_statement = missing
    try:
        t_1 = environment.filters['d']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'd' found.")
    pass
    yield '\n\n<sdoc-node-content\n  node-view="'
    yield escape(t_1((undefined(name='requirement_style') if l_0_requirement_style is missing else l_0_requirement_style), context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_requirement_style_mode'))))
    yield '"\n  data-level="'
    yield escape(environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'context'), 'title_number_string'))
    yield '"'
    if environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_status'):
        pass
        yield "\n    data-status='"
        yield escape(context.call(environment.getattr(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_status'), 'lower')))
        yield "'"
    yield '\n  data-testid="requirement-style-'
    yield escape(t_1((undefined(name='requirement_style') if l_0_requirement_style is missing else l_0_requirement_style), context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_requirement_style_mode'))))
    yield '"\n>\n  '
    l_0_title_number = True
    context.vars['title_number'] = l_0_title_number
    context.exported_vars.add('title_number')
    yield '\n  '
    l_0_truncated_statement = True
    context.vars['truncated_statement'] = l_0_truncated_statement
    context.exported_vars.add('truncated_statement')
    yield '\n  '
    template = environment.get_template('components/node_field/title/index.jinja', 'components/node_content/tiny.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'title_number': l_0_title_number, 'truncated_statement': l_0_truncated_statement}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  '
    template = environment.get_template('components/node_field/uid/index.jinja', 'components/node_content/tiny.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'title_number': l_0_title_number, 'truncated_statement': l_0_truncated_statement}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  '
    template = environment.get_template('components/node_field/statement/index.jinja', 'components/node_content/tiny.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'title_number': l_0_title_number, 'truncated_statement': l_0_truncated_statement}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n</sdoc-node-content>'

blocks = {}
debug_info = '7=21&8=23&9=25&10=28&12=31&14=33&15=37&16=41&17=48&18=55'