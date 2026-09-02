from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/document/move_node/frame_move_node_success.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('components/modal/index.jinja', 'actions/document/move_node/frame_move_node_success.jinja')
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
    yield 'move-node-success'

def block_modal_container(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_new_location_href = resolve('new_location_href')
    pass
    yield '\n  <sdoc-modal-message data-testid="move-node-success-message">\n    <p class="move_node_modal_message">✔</p>\n    <p class="move_node_modal_message"><b>Node moved successfully.</b></p>\n  </sdoc-modal-message>\n  <a\n    href="'
    yield escape((undefined(name='new_location_href') if l_0_new_location_href is missing else l_0_new_location_href))
    yield '"\n    data-turbo="false"\n    class="action_button"\n    data-js-move-node-tree-new-location\n    data-testid="move-node-go-to-new-location"\n  >Go to new location</a>\n'

blocks = {'modal__context': block_modal__context, 'modal_container': block_modal_container}
debug_info = '1=12&2=17&3=27&9=37'