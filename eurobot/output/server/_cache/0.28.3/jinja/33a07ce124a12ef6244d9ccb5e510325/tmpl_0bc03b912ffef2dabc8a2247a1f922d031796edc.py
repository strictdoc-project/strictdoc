from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/_shared/resizable_bar_with_toc.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_toc_position = resolve('toc_position')
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    pass
    l_1_resizable_bar_content = 'screens/document/_shared/frame_toc.jinja'
    l_1_resizable_bar_name = 'toc'
    l_1_resizable_bar_position = t_1((undefined(name='toc_position') if l_0_toc_position is missing else l_0_toc_position), 'left', True)
    pass
    template = environment.get_template('components/resizable_bar/index.jinja', 'screens/document/_shared/resizable_bar_with_toc.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'resizable_bar_content': l_1_resizable_bar_content, 'resizable_bar_name': l_1_resizable_bar_name, 'resizable_bar_position': l_1_resizable_bar_position}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_resizable_bar_content = l_1_resizable_bar_name = l_1_resizable_bar_position = missing

blocks = {}
debug_info = '7=22'