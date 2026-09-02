from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/resizable_bar/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_resizable_bar_name = resolve('resizable_bar_name')
    l_0_resizable_bar_state = resolve('resizable_bar_state')
    l_0_resizable_bar_position = resolve('resizable_bar_position')
    l_0_resizable_bar_content = resolve('resizable_bar_content')
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    pass
    yield '\n\n\n\n<div\n  js-resizable_bar="'
    yield escape((undefined(name='resizable_bar_name') if l_0_resizable_bar_name is missing else l_0_resizable_bar_name))
    yield '"\n  data-state="'
    yield escape(t_1((undefined(name='resizable_bar_state') if l_0_resizable_bar_state is missing else l_0_resizable_bar_state), 'open', True))
    yield '"\n  data-position="'
    yield escape(t_1((undefined(name='resizable_bar_position') if l_0_resizable_bar_position is missing else l_0_resizable_bar_position), 'left', True))
    yield '"\n>\n'
    template = environment.get_or_select_template((undefined(name='resizable_bar_content') if l_0_resizable_bar_content is missing else l_0_resizable_bar_content), 'components/resizable_bar/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n</div>'

blocks = {}
debug_info = '19=22&20=24&21=26&23=28'