from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/document/move_node/frame_move_node.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('components/modal/index.jinja', 'actions/document/move_node/frame_move_node.jinja')
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
    yield 'move-node'

def block_modal_header(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_moved_node = resolve('moved_node')
    pass
    yield 'Move &quot;'
    yield escape(context.call(environment.getattr((undefined(name='moved_node') if l_0_moved_node is missing else l_0_moved_node), 'get_display_title'), include_toc_number=False, _block_vars=_block_vars))
    yield '&quot;\n'

def block_modal_container(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n  <sdoc-modal-content>\n    '
    template = environment.get_template('actions/document/move_node/_project_move_tree.jinja', 'actions/document/move_node/frame_move_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </sdoc-modal-content>\n'

blocks = {'modal__context': block_modal__context, 'modal_header': block_modal_header, 'modal_container': block_modal_container}
debug_info = '1=12&2=17&3=27&4=37&6=40&8=49'