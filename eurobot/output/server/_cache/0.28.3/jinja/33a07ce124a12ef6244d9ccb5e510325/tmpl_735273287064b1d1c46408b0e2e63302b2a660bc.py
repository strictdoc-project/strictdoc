from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/confirm/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('components/modal/form.jinja', 'components/confirm/index.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    yield from parent_template.root_render_func(context)

def block_modal__context(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield 'confirm'

def block_modal_form__header(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_confirm_title = resolve('confirm_title')
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    pass
    yield '\n  '
    yield escape(t_1((undefined(name='confirm_title') if l_0_confirm_title is missing else l_0_confirm_title), 'Are you sure?'))
    yield '\n'

def block_modal_form__content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_confirm_message = resolve('confirm_message')
    l_0_errors = resolve('errors')
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    try:
        t_2 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    yield '\n<sdoc-modal-message data-testid="confirm-message">\n  '
    yield escape(t_1((undefined(name='confirm_message') if l_0_confirm_message is missing else l_0_confirm_message), 'This is an unrecoverable action.'))
    yield '\n\n  \n  '
    if (t_2((undefined(name='errors') if l_0_errors is missing else l_0_errors)) > 0):
        pass
        yield '\n    <div class="error">\n    <p>This element cannot be deleted:</p>\n    <ul>\n  '
        for l_1_error_ in (undefined(name='errors') if l_0_errors is missing else l_0_errors):
            _loop_vars = {}
            pass
            yield '\n    <li>'
            yield escape(l_1_error_)
            yield '</li>\n  '
        l_1_error_ = missing
        yield '\n    </ul>\n    </div>\n  '
    yield '\n\n</sdoc-modal-message>\n'

def block_modal_form__footer_submit(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n  \n  '
    template = environment.get_template('components/button/confirm.jinja', 'components/confirm/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n'

blocks = {'modal__context': block_modal__context, 'modal_form__header': block_modal_form__header, 'modal_form__content': block_modal_form__content, 'modal_form__footer_submit': block_modal_form__footer_submit}
debug_info = '1=12&7=17&8=27&9=43&11=46&13=69&18=71&22=74&23=78&31=84&41=93'