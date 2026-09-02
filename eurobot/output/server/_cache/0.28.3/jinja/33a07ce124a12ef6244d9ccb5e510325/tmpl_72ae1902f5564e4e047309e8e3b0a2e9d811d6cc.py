from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/document/move_node/frame_move_node_error.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('components/modal/index.jinja', 'actions/document/move_node/frame_move_node_error.jinja')
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
    yield 'move-node-error'

def block_modal_container(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_error_message = resolve('error_message')
    pass
    yield '\n  <sdoc-modal-message data-testid="move-node-error-message">\n    '
    yield escape((undefined(name='error_message') if l_0_error_message is missing else l_0_error_message))
    yield '\n  </sdoc-modal-message>\n'

blocks = {'modal__context': block_modal__context, 'modal_container': block_modal_container}
debug_info = '1=12&2=17&3=27&5=37'