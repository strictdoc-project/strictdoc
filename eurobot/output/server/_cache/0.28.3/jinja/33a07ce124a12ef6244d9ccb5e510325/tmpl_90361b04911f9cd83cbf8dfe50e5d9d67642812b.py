from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/modal/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '\n<turbo-frame data-js-modal>\n  <sdoc-backdrop>\n      <sdoc-modal context="'
    yield from context.blocks['modal__context'][0](context)
    yield '">\n        <sdoc-modal-header data-testid="modal-header">'
    yield from context.blocks['modal_header'][0](context)
    yield '</sdoc-modal-header>\n        <sdoc-modal-container>'
    yield from context.blocks['modal_container'][0](context)
    yield '</sdoc-modal-container>'
    l_1_cancel_name = 'Close'
    pass
    template = environment.get_template('components/button/cancel.jinja', 'components/modal/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'cancel_name': l_1_cancel_name}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_cancel_name = missing
    yield '</sdoc-modal>\n  </sdoc-backdrop>\n</turbo-frame>'

def block_modal__context(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_modal_header(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_modal_container(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

blocks = {'modal__context': block_modal__context, 'modal_header': block_modal_header, 'modal_container': block_modal_container}
debug_info = '6=12&8=14&13=16&16=20&6=29&8=38&13=47'