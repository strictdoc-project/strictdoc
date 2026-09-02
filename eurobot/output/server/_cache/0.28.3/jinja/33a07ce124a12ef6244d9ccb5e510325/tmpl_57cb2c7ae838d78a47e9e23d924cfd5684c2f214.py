from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/header/_usage_example.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    l_1_header__items = ['screens/document/_shared/frame_header_document_title.jinja', 'screens/document/_shared/viewtype_menu.jinja']
    l_1_header__last = 'screens/document/document/actions.jinja'
    pass
    template = environment.get_template('components/header/index.jinja', 'components/header/_usage_example.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'header__items': l_1_header__items, 'header__last': l_1_header__last}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_header__items = l_1_header__last = missing

blocks = {}
debug_info = '14=14'