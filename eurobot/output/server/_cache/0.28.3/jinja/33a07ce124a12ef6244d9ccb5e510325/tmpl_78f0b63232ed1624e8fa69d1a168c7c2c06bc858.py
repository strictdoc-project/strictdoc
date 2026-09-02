from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_index/actions.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
        pass
        yield '\n<turbo-frame>\n  '
        template = environment.get_template('components/static_search/index.jinja', 'features/project_index/actions.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_header__actions_template = 'features/project_index/action_list.jinja'
        pass
        template = environment.get_template('components/header/actions_wrapper.jinja', 'features/project_index/actions.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'header__actions_template': l_1_header__actions_template}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_header__actions_template = missing
        yield '</turbo-frame>'
    else:
        pass
        template = environment.get_template('components/static_search/index.jinja', 'features/project_index/actions.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()

blocks = {}
debug_info = '1=12&7=15&9=23&13=33'