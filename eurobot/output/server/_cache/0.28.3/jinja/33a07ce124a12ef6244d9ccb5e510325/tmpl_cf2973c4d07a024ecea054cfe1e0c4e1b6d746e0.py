from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/modal/form.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '\n<turbo-frame data-js-modal>\n  <sdoc-backdrop>\n      <sdoc-modal context="'
    yield from context.blocks['modal__context'][0](context)
    yield '">\n        <sdoc-modal-header>'
    yield from context.blocks['modal_form__header'][0](context)
    yield '</sdoc-modal-header>\n        <sdoc-modal-content>'
    yield from context.blocks['modal_form__content'][0](context)
    yield '</sdoc-modal-content>\n        <sdoc-modal-footer>'
    yield from context.blocks['modal_form__footer_extra'][0](context)
    yield from context.blocks['modal_form__footer_submit'][0](context)
    yield from context.blocks['modal_form__footer_cancel'][0](context)
    yield '</sdoc-modal-footer>\n      </sdoc-modal>\n  </sdoc-backdrop>\n</turbo-frame>'

def block_modal__context(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_modal_form__header(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_modal_form__content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_modal_form__footer_extra(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_modal_form__footer_submit(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n            '
    template = environment.get_template('components/button/submit.jinja', 'components/modal/form.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n          '

def block_modal_form__footer_cancel(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n            '
    template = environment.get_template('components/button/cancel.jinja', 'components/modal/form.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n          '

blocks = {'modal__context': block_modal__context, 'modal_form__header': block_modal_form__header, 'modal_form__content': block_modal_form__content, 'modal_form__footer_extra': block_modal_form__footer_extra, 'modal_form__footer_submit': block_modal_form__footer_submit, 'modal_form__footer_cancel': block_modal_form__footer_cancel}
debug_info = '8=12&10=14&13=16&16=18&17=19&20=20&8=23&10=32&13=41&16=50&17=59&18=68&20=76&21=85'