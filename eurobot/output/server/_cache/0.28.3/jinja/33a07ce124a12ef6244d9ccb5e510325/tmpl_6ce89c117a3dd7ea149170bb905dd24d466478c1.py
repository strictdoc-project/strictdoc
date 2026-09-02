from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/header/actions_wrapper.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_header__actions_template = resolve('header__actions_template')
    pass
    yield '\n\n<div\n  id="header-actions"\n  class="header-actions"\n>\n  <div\n    id="header-actions-handler"\n    class="header-actions__kebab action_button"\n    role="button"\n    data-dropdown-handler\n    aria-expanded="false"\n    aria-controls="header-actions-menu"\n    aria-haspopup="true"\n    title="Actions"\n    data-testid="header-action-menu-handler"\n  >'
    template = environment.get_template('icons/ico16_3dots.svg', 'components/header/actions_wrapper.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</div>\n  <menu\n    id="header-actions-menu"\n    class="dropdown_menu"\n    aria-hidden="true"\n    aria-label="Header actions"\n    aria-labelledby="header-actions-handler"\n    role="menu"\n  >\n    '
    template = environment.get_or_select_template((undefined(name='header__actions_template') if l_0_header__actions_template is missing else l_0_header__actions_template), 'components/header/actions_wrapper.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </menu>\n</div>'

blocks = {}
debug_info = '17=13&26=20'